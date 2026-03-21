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
    if isinstance(data, list) and len(data) >= 2 and data[0] == "text":
        body = data[1]
        if isinstance(body, list):
            return "".join(str(x) for x in body)
        return str(body)
    if isinstance(data, dict):
        t = data.get("type")
        if t in ("auth_challenge", "auth_result"):
            return ""
        return json.dumps(data, ensure_ascii=False)
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
    return [
        ("help", {}),
        ("help look", {}),
        ("help inventory", {}),
        ("help get", {}),
        ("help north", {}),
    ]


def _steps_basics() -> list[tuple[str, dict]]:
    return [
        ("look", {}),
        ("inventory", {}),
        ("i", {}),
        ("score", {}),
        ("who", {}),
    ]


def _build_steps(phase: str) -> list[tuple[str, dict]]:
    if phase == "help":
        return _steps_help()
    if phase == "basics":
        return _steps_basics()
    if phase == "tutorial":
        return _steps_tutorial_path()
    return _steps_help() + _steps_basics() + _steps_tutorial_path()


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
    steps = _build_steps(args.phase)

    failures = 0
    async with websockets.connect(
        url,
        ping_interval=None,
        ping_timeout=None,
    ) as ws:
        await _drain_initial_evennia(ws, args.drain_seconds, args.verbose)
        await _send_cmd(ws, f"agent_connect {api_key}")
        banner = await _collect_burst(ws, verbose=args.verbose, max_seconds=12.0)
        if args.verbose:
            print(f"[after agent_connect]\n{banner[:2000]}\n---", flush=True)

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
    args = p.parse_args()
    if not args.api_key:
        print("Set --api-key or CLAW_API_KEY", file=sys.stderr)
        return 1
    return asyncio.run(run_walkthrough(args))


if __name__ == "__main__":
    raise SystemExit(main())
