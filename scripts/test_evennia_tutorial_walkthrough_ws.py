#!/usr/bin/env python3
"""
In-game walkthrough smoke test over WebSocket (see docs/EVENNIA_TUTORIAL_WALKTHROUGH.md).

- Same connect path as scripts/test_ws_connect_duration.py: drain MotD, then agent_connect.
- Runs help + appendix commands and a linear tutorial path (look, move, climb, bridge, dark).
- Flags likely command failures in captured text (Evennia-style phrases).

Requires: pip install websockets
Env: CLAW_API_KEY, optional CLAW_WS_URL

Examples:
  export CLAW_API_KEY='claw_live_...'
  python scripts/test_evennia_tutorial_walkthrough_ws.py
  python scripts/test_evennia_tutorial_walkthrough_ws.py --verbose
  python scripts/test_evennia_tutorial_walkthrough_ws.py --phase help
  python scripts/test_evennia_tutorial_walkthrough_ws.py --idle-every 25
  # Prefer a single WS client; --strict-single-session exits 3 if banner shows shared puppet
  # --quiet-multisession hides the sharing warning (script still runs)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time


def _format_server_message(data) -> str:
    if isinstance(data, list) and data:
        if data[0] == "logged_in":
            return ""
        if len(data) >= 2 and data[0] == "text":
            body = data[1]
            if isinstance(body, list):
                return "".join(str(x) for x in body)
            return str(body)
    if isinstance(data, dict):
        t = data.get("type")
        if t in ("auth_challenge", "auth_result"):
            return ""
        return json.dumps(data, ensure_ascii=False)
    if isinstance(data, list):
        return ""
    return json.dumps(data, ensure_ascii=False)


_FAILURE_PATTERNS = [
    re.compile(r"command\s+['\"]?[^\s'\"]+['\"]?\s+is\s+not\s+available", re.I),
    re.compile(r"command\s+not\s+available", re.I),
    re.compile(r"unknown\s+command", re.I),
    re.compile(r"i\s+don'?t\s+know\s+that\s+command", re.I),
    re.compile(r"could\s+not\s+find\s+.*command", re.I),
    re.compile(r"no\s+such\s+command", re.I),
]


def _looks_like_cmd_failure(text: str) -> bool:
    if not text or not text.strip():
        return False
    for pat in _FAILURE_PATTERNS:
        if pat.search(text):
            return True
    return False


_CHAR_KEY_RE = re.compile(
    r"connected to the Adventure as\s*(?:<[^>]+>)*\s*([\w\-_]+)",
    re.I,
)


def _parse_character_key(banner: str) -> str | None:
    m = _CHAR_KEY_RE.search(banner.replace("\n", " "))
    return m.group(1) if m else None


def _banner_shows_shared_puppet(banner: str) -> bool:
    bl = banner.lower()
    return "session" in bl and (
        "sharing" in bl
        or "shared from another" in bl
        or "now shared from" in bl
    )


_NOPE_CMD_FAIL_RE = re.compile(r"command\s+['\"]nope['\"]", re.I)


async def _recover_if_needed(
    ws,
    text: str,
    char_key: str | None,
    *,
    quiet_after: float,
    step_timeout: float,
    verbose: bool,
) -> tuple[str, str | None]:
    """
    Cancel chardelete get_input prompt; re-puppet after OOC.

    Evennia stores the prompt on the Account with InputCmdSet. While puppeting a
    Character, a bare line like "no" is parsed by the *character* cmdset first
    (nomatch -> "Command 'no' is not available"), so it never reaches get_input.
    We unpuppet (ooc) then send any non-yes line (e.g. nope) to abort deletion.

    With **multisession**, get_input may be bound to another client: ooc/nope may
    not cancel the prompt and the character may already be deleted. Returns
    (text, character_key_or_None) with key cleared if the character is gone.
    """
    low = text.lower()
    out = text
    alive_key = char_key
    delete_cancelled = False

    if "permanently destroy" in low and "continue yes" in low:
        if "has been destroyed" in low:
            if verbose:
                print(
                    "[recover] chardelete text present but character already destroyed "
                    "(other session likely confirmed) — skip ooc/nope",
                    flush=True,
                )
            return out, None

        if verbose:
            print(
                "[recover] chardelete prompt: sending ooc then nope (abort get_input)",
                flush=True,
            )
        await _send_cmd(ws, "ooc")
        out += await _collect_burst(
            ws,
            quiet_after_last=quiet_after,
            max_seconds=min(12.0, step_timeout),
            verbose=verbose,
        )
        # Any answer except "yes" aborts (see CmdCharDelete in evennia.commands.default.account)
        await _send_cmd(ws, "nope")
        out += await _collect_burst(
            ws,
            quiet_after_last=quiet_after,
            max_seconds=min(20.0, step_timeout),
            verbose=verbose,
        )
        low = out.lower()
        if "has been destroyed" in low or "not a valid character choice" in low:
            if verbose:
                print("[recover] character gone after chardelete race — stop ic", flush=True)
            return out, None
        nope_failed = bool(_NOPE_CMD_FAIL_RE.search(out))
        aborted = "deletion was aborted" in low
        if nope_failed and not aborted:
            if verbose:
                print(
                    "[recover] nope did not reach get_input (multisession or stale prompt) "
                    "— skip auto ic from chardelete path",
                    flush=True,
                )
        else:
            delete_cancelled = aborted or not nope_failed

    if alive_key and (
        "has been destroyed" in low or "not a valid character choice" in low
    ):
        alive_key = None

    need_ic = bool(
        alive_key
        and (
            delete_cancelled
            or "out-of-character (ooc)" in low
            or "you go ooc" in low
        )
    )
    if need_ic:
        if verbose:
            print(f"[recover] sending ic {alive_key}", flush=True)
        await _send_cmd(ws, f"ic {alive_key}")
        out += await _collect_burst(
            ws,
            quiet_after_last=quiet_after,
            max_seconds=min(20.0, step_timeout),
            verbose=verbose,
        )
        low = out.lower()
        if "not a valid character choice" in low:
            if verbose:
                print("[recover] ic failed — character no longer available", flush=True)
            alive_key = None
    return out, alive_key


async def _drain_initial_evennia(ws, max_seconds: float, verbose: bool) -> None:
    deadline = time.monotonic() + max_seconds
    while time.monotonic() < deadline:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=0.35)
        except asyncio.TimeoutError:
            break
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        if verbose:
            print(f"[drain] {raw[:200]!r}...", flush=True)


async def _collect_burst(
    ws,
    *,
    quiet_after_last: float = 1.4,
    poll: float = 0.22,
    max_seconds: float = 35.0,
    max_msgs: int = 80,
    verbose: bool,
) -> str:
    """Collect text lines until no JSON text frames for quiet_after_last seconds."""
    parts: list[str] = []
    last_rx = time.monotonic()
    deadline = time.monotonic() + max_seconds
    msgs = 0
    while time.monotonic() < deadline and msgs < max_msgs:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=poll)
        except asyncio.TimeoutError:
            if parts and (time.monotonic() - last_rx) >= quiet_after_last:
                break
            if not parts and (time.monotonic() - deadline + max_seconds) > 18.0:
                break
            continue
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            parts.append(raw)
            last_rx = time.monotonic()
            msgs += 1
            continue
        chunk = _format_server_message(data)
        if chunk and not chunk.strip().lower() in ("idle", "."):
            parts.append(chunk)
        last_rx = time.monotonic()
        msgs += 1
        if verbose:
            print(f"  [<- {msgs}] {chunk[:240]!r}...", flush=True)
    return "".join(parts)


async def _send_cmd(ws, cmd: str) -> None:
    await ws.send(json.dumps(["text", [cmd], {}]))


async def _idle_loop(ws, interval: float) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await ws.send(json.dumps(["text", ["idle"], {}]))
        except Exception:
            break


def _steps_help() -> list[tuple[str, dict]]:
    # Topics that exist on default Account + Character cmdsets (avoid "No help found"
    # for tutorial-only verbs like get/north on some merges).
    return [
        ("help", {}),
        ("help look", {}),
        ("help inventory", {}),
        ("help ic", {}),
        ("help ooc", {}),
    ]


def _steps_basics(include_score: bool) -> list[tuple[str, dict]]:
    steps: list[tuple[str, dict]] = [
        ("look", {}),
        ("inventory", {}),
        ("i", {}),
    ]
    if include_score:
        steps.append(("score", {}))
    steps.append(("who", {}))
    return steps


def _build_steps(phase: str, *, include_score: bool) -> list[tuple[str, dict]]:
    if phase == "help":
        return _steps_help()
    if phase == "basics":
        return _steps_basics(include_score)
    if phase == "tutorial":
        return _steps_tutorial_path()
    return _steps_help() + _steps_basics(include_score) + _steps_tutorial_path()


def _steps_tutorial_path() -> list[tuple[str, dict]]:
    """
    Linear path from EVENNIA_TUTORIAL_WALKTHROUGH.md (best-effort).
    Fails softly if the character is not at tutorial start.
    """
    return [
        ("look", {}),
        ("n", {"note": "Intro -> Cliff"}),
        ("look", {}),
        ("climb tree", {}),
        ("look", {}),
        ("n", {"note": "Cliff -> Bridge — send quickly"}),
        ("n", {"note": "Bridge crossing (second n if room is wide)"}),
        ("look", {}),
        ("search", {"quiet_after_last": 2.0}),
        ("feel", {}),
        ("feel around", {}),
    ]


async def run_walkthrough(args: argparse.Namespace) -> int:
    try:
        import websockets
    except ImportError:
        print("Install websockets: pip install websockets", file=sys.stderr)
        return 1

    url = args.url
    api_key = args.api_key
    steps = _build_steps(args.phase, include_score=args.with_score)
    char_key = None

    failures = 0
    async with websockets.connect(
        url,
        ping_interval=None,
        ping_timeout=None,
    ) as ws:
        await _drain_initial_evennia(ws, args.drain_seconds, args.verbose)
        await _send_cmd(ws, f"agent_connect {api_key}")
        banner = await _collect_burst(ws, verbose=args.verbose, max_seconds=12.0)
        char_key = _parse_character_key(banner)
        if args.verbose:
            print(f"[after agent_connect]\n{banner[:2000]}\n---", flush=True)
        if char_key and args.verbose:
            print(f"[parsed character key: {char_key!r}]", flush=True)
        if _banner_shows_shared_puppet(banner):
            if args.strict_single_session:
                print(
                    "ERROR: shared puppet / multisession detected in banner. "
                    "Close all other WebSocket or browser sessions for this Agent, then retry. "
                    "(Without --strict-single-session the script continues but results are unreliable.)",
                    file=sys.stderr,
                )
                return 3
            if not args.quiet_multisession:
                print(
                    "WARNING: multisession (shared puppet) detected — close other clients "
                    "to avoid chardelete races and duplicated output. "
                    "Use --strict-single-session to fail fast, or --quiet-multisession to hide this.",
                    file=sys.stderr,
                )

        idle_task = None
        if args.idle_every and args.idle_every > 0:
            idle_task = asyncio.create_task(_idle_loop(ws, args.idle_every))

        try:
            for cmd, meta in steps:
                note = meta.get("note", "")
                qa = float(meta.get("quiet_after_last", args.quiet_after))
                if args.verbose:
                    print(f"\n>> {cmd}" + (f"  # {note}" if note else ""), flush=True)
                await _send_cmd(ws, cmd)
                text = await _collect_burst(
                    ws,
                    quiet_after_last=qa,
                    max_seconds=args.step_timeout,
                    verbose=args.verbose,
                )
                text, char_key = await _recover_if_needed(
                    ws,
                    text,
                    char_key,
                    quiet_after=args.quiet_after,
                    step_timeout=args.step_timeout,
                    verbose=args.verbose,
                )
                if not text.strip():
                    print(f"WARN: no text response for: {cmd!r}", flush=True)
                bad = _looks_like_cmd_failure(text)
                if bad:
                    failures += 1
                    snippet = text.strip().replace("\n", " ")[:300]
                    print(f"FAIL pattern in output for {cmd!r}: {snippet!r}", flush=True)
                elif args.print_ok:
                    print(f"OK {cmd!r}", flush=True)
        finally:
            if idle_task:
                idle_task.cancel()
                try:
                    await idle_task
                except asyncio.CancelledError:
                    pass

    print(f"Done steps={len(steps)} cmd_failures={failures}", flush=True)
    return 1 if failures else 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="WebSocket walkthrough: help + tutorial path (EVENNIA_TUTORIAL_WALKTHROUGH.md)."
    )
    p.add_argument("--url", default=os.environ.get("CLAW_WS_URL", "wss://ws.adventure.mudclaw.net"))
    p.add_argument("--api-key", default=os.environ.get("CLAW_API_KEY", ""))
    p.add_argument(
        "--phase",
        choices=("all", "help", "basics", "tutorial"),
        default="all",
        help="Which step groups to run (default: all)",
    )
    p.add_argument("--drain-seconds", type=float, default=3.0)
    p.add_argument("--step-timeout", type=float, default=40.0, help="Max seconds to wait per command")
    p.add_argument(
        "--quiet-after",
        type=float,
        default=1.4,
        help="End burst after this many seconds without a message",
    )
    p.add_argument(
        "--idle-every",
        type=float,
        default=0.0,
        help="Send idle every N seconds during test (0 = off)",
    )
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--print-ok", action="store_true", help="Print one line per successful command")
    p.add_argument(
        "--with-score",
        action="store_true",
        help="Include 'score' in basics (omitted by default; not in default CharacterCmdSet on this game)",
    )
    p.add_argument(
        "--quiet-multisession",
        action="store_true",
        help="Do not print stderr warning when banner shows shared-puppet / multisession",
    )
    p.add_argument(
        "--strict-single-session",
        action="store_true",
        help="Exit with code 3 if agent_connect banner shows shared puppet (multisession)",
    )
    args = p.parse_args()
    if not args.api_key:
        print("Set --api-key or CLAW_API_KEY", file=sys.stderr)
        return 1
    return asyncio.run(run_walkthrough(args))


if __name__ == "__main__":
    raise SystemExit(main())
