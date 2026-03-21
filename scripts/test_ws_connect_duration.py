#!/usr/bin/env python3
"""
Measure WebSocket connection persistence (time until server/proxy closes).

- Performs the same Agent auth handshake as production (challenge + HMAC).
- Optionally sends in-game ``agent_connect <api_key>`` and/or periodic Evennia ``idle`` frames.
- Disables the websockets library's own ping/pong so results reflect app traffic only.

Dependency: pip install websockets

Examples:
  export CLAW_API_KEY='claw_live_...'
  # Silent after auth + agent_connect (stress proxy idle)
  python scripts/test_ws_connect_duration.py

  # With Evennia idle every 25s (expected to last longer behind strict proxies)
  python scripts/test_ws_connect_duration.py --idle-every 25

  # Auth only, no game login
  python scripts/test_ws_connect_duration.py --no-agent-connect --max-wait 300

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


async def _auth(ws, api_key: str, verbose: bool) -> None:
    raw = await ws.recv()
    challenge = json.loads(raw)
    if challenge.get("type") != "auth_challenge":
        raise RuntimeError(f"Expected auth_challenge, got: {challenge!r}")
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
    result = json.loads(await ws.recv())
    if result.get("type") != "auth_result" or result.get("status") != "success":
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
        await _auth(ws, api_key, args.verbose)

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
        description="Test WebSocket persistence after Agent auth (optional agent_connect + idle)."
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
