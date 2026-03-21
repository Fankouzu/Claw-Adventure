#!/usr/bin/env python3
"""
Measure WebSocket connection persistence (time until server/proxy closes).

- Performs the same Agent auth handshake as production (challenge + HMAC).
- Optionally sends in-game ``agent_connect <api_key>`` and/or periodic Evennia ``idle`` frames.
- Disables the websockets library's own ping/pong so results reflect app traffic only.

Dependency: pip install websockets

Examples:
  export CLAW_API_KEY='claw_live_...'
  # Production wss (MotD first, no JSON challenge): silent + agent_connect
  python scripts/test_ws_connect_duration.py

  # MCP-style JSON auth challenge first
  python scripts/test_ws_connect_duration.py --json-auth

  # With Evennia idle every 25s (longer behind strict proxies)
  python scripts/test_ws_connect_duration.py --idle-every 25

  # Three runs, average
  python scripts/test_ws_connect_duration.py --runs 3
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import json
import os
import sys
import time


def _sign(nonce: str, api_key: str) -> str:
    return hmac.new(
        api_key.encode("utf-8"),
        nonce.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


async def _recv_json(ws, timeout: float = 15.0):
    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    return json.loads(raw)


async def _auth(ws, api_key: str, verbose: bool) -> None:
    challenge = None
    for _ in range(20):
        data = await _recv_json(ws)
        if isinstance(data, dict) and data.get("type") == "auth_challenge":
            challenge = data
            break
        if verbose:
            print(f"[{time.monotonic():.3f}] pre-auth frame: {data!r}", flush=True)
    if not challenge:
        raise RuntimeError("Never received auth_challenge")

    nonce = challenge["nonce"]
    prefix = api_key[:20]
    await ws.send(
        json.dumps(
            {
                "type": "auth_response",
                "api_key_prefix": prefix,
                "signature": _sign(nonce, api_key),
            }
        )
    )

    result = None
    for _ in range(20):
        data = await _recv_json(ws)
        if isinstance(data, dict) and data.get("type") == "auth_result":
            result = data
            break
        if verbose:
            print(f"[{time.monotonic():.3f}] post-response frame: {data!r}", flush=True)

    if not result:
        raise RuntimeError("Never received auth_result")
    if result.get("status") != "success":
        raise RuntimeError(f"Auth failed: {result!r}")
    if verbose:
        print(f"[{time.monotonic():.3f}] auth ok agent={result.get('agent_name')!r}", flush=True)


async def _idle_sender(ws, interval: float, verbose: bool) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await ws.send(json.dumps(["text", ["idle"], {}]))
            if verbose:
                print(f"[{time.monotonic():.3f}] sent idle", flush=True)
        except Exception:
            break


async def _recv_loop(ws, verbose: bool, log_json: bool, close_info: dict) -> None:
    import websockets

    try:
        while True:
            raw = await ws.recv()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="replace")
            if not verbose and not log_json:
                continue
            try:
                data = json.loads(raw)
                if log_json:
                    print(f"[{time.monotonic():.3f}] <- {data!r}", flush=True)
                elif verbose:
                    print(f"[{time.monotonic():.3f}] <- {raw[:200]!r}", flush=True)
            except json.JSONDecodeError:
                if verbose or log_json:
                    print(f"[{time.monotonic():.3f}] <- {raw!r}", flush=True)
    except websockets.exceptions.ConnectionClosed as e:
        close_info["code"] = e.code
        close_info["reason"] = e.reason or ""


async def _drain_initial_evennia(ws, max_seconds: float, verbose: bool) -> None:
    """Consume MotD / banner frames (production WS often has no JSON auth_challenge)."""
    deadline = time.monotonic() + max_seconds
    while time.monotonic() < deadline:
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=0.35)
        except asyncio.TimeoutError:
            break
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        if verbose:
            print(f"[{time.monotonic():.3f}] drain <- {raw[:160]!r}...", flush=True)


async def run_once(args: argparse.Namespace) -> float:
    import websockets

    url = args.url
    api_key = args.api_key
    t0 = time.monotonic()
    close_info: dict = {"code": None, "reason": None}

    async with websockets.connect(
        url,
        ping_interval=None,
        ping_timeout=None,
    ) as ws:
        t_after_connect = time.monotonic()
        if args.json_auth:
            await _auth(ws, api_key, args.verbose)
        else:
            await _drain_initial_evennia(ws, args.drain_seconds, args.verbose)

        if args.agent_connect:
            cmd = f"agent_connect {api_key}"
            await ws.send(json.dumps(["text", [cmd], {}]))
            if args.verbose:
                print(f"[{time.monotonic():.3f}] sent agent_connect ...", flush=True)

        recv_task = asyncio.create_task(
            _recv_loop(ws, args.verbose, args.log_json, close_info)
        )
        idle_task = None
        if args.idle_every and args.idle_every > 0:
            idle_task = asyncio.create_task(_idle_sender(ws, args.idle_every, args.verbose))

        watchdog = asyncio.create_task(asyncio.sleep(args.max_wait))

        done, pending = await asyncio.wait(
            {recv_task, watchdog},
            return_when=asyncio.FIRST_COMPLETED,
        )

        elapsed = time.monotonic() - t0
        setup = t_after_connect - t0

        if watchdog in done and recv_task not in done:
            for t in pending:
                t.cancel()
            if idle_task:
                idle_task.cancel()
            try:
                await ws.close()
            except Exception:
                pass
            _wait = [recv_task]
            if idle_task:
                _wait.append(idle_task)
            await asyncio.gather(*_wait, return_exceptions=True)
            print(
                f"SURVIVED max_wait={args.max_wait:.1f}s (client closed) "
                f"elapsed={elapsed:.2f}s ws_connect_setup={setup:.3f}s",
                flush=True,
            )
            return elapsed

        # recv finished first -> remote closed (or error)
        watchdog.cancel()
        if idle_task:
            idle_task.cancel()
        _done_wait = [watchdog]
        if idle_task:
            _done_wait.append(idle_task)
        await asyncio.gather(*_done_wait, return_exceptions=True)
        await recv_task

        code = close_info.get("code")
        reason = close_info.get("reason") or ""
        print(
            f"DISCONNECTED elapsed={elapsed:.2f}s ws_connect_setup={setup:.3f}s "
            f"close_code={code!r} reason={reason!r}",
            flush=True,
        )
        return elapsed


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Test WebSocket persistence: default = Evennia banner drain + agent_connect; "
            "use --json-auth for challenge+HMAC flow."
        )
    )
    p.add_argument("--url", default=os.environ.get("CLAW_WS_URL", "wss://ws.adventure.mudclaw.net"))
    p.add_argument("--api-key", default=os.environ.get("CLAW_API_KEY", ""))
    p.add_argument(
        "--max-wait",
        type=float,
        default=300.0,
        help="If still connected, close client after this many seconds (report as SURVIVED)",
    )
    p.add_argument(
        "--idle-every",
        type=float,
        default=0.0,
        help="Send Evennia ['text',['idle'],{}] every N seconds; 0 disables",
    )
    p.add_argument(
        "--agent-connect",
        dest="agent_connect",
        action="store_true",
        default=True,
        help="Send agent_connect <api_key> after auth (default: on)",
    )
    p.add_argument(
        "--no-agent-connect",
        dest="agent_connect",
        action="store_false",
        help="Skip in-game agent_connect",
    )
    p.add_argument("--runs", type=int, default=1, help="Repeat test N times and print summary")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--log-json", action="store_true", help="Print each incoming JSON message")
    p.add_argument(
        "--json-auth",
        action="store_true",
        help="Use challenge+HMAC JSON auth (MCP-style). Default: Evennia MotD then agent_connect.",
    )
    p.add_argument(
        "--drain-seconds",
        type=float,
        default=3.0,
        help="When not using --json-auth, max time to drain banner frames before agent_connect",
    )
    args = p.parse_args()

    if not args.api_key:
        print("Set --api-key or CLAW_API_KEY", file=sys.stderr)
        sys.exit(1)

    try:
        import websockets  # noqa: F401
    except ImportError:
        print("Install websockets: pip install websockets", file=sys.stderr)
        sys.exit(1)

    durations: list[float] = []
    for i in range(args.runs):
        if args.runs > 1:
            print(f"--- run {i + 1}/{args.runs} ---", flush=True)
        try:
            d = asyncio.run(run_once(args))
            durations.append(d)
        except KeyboardInterrupt:
            print("Interrupted", flush=True)
            sys.exit(130)
        except Exception as e:
            print(f"ERROR: {e!r}", file=sys.stderr)
            sys.exit(1)

    if len(durations) > 1:
        avg = sum(durations) / len(durations)
        print(
            f"SUMMARY runs={len(durations)} min={min(durations):.2f}s "
            f"max={max(durations):.2f}s avg={avg:.2f}s",
            flush=True,
        )


if __name__ == "__main__":
    main()
