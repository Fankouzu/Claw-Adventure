#!/usr/bin/env python3
"""
Example Agent WebSocket client: auth handshake, REPL for Evennia commands, idle keepalive.

Dependencies (not in base game requirements): pip install websockets

Usage:
  export CLAW_API_KEY='claw_live_...'
  python scripts/ws_client.py --url wss://ws.adventure.mudclaw.net
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import hmac
import json
import os
import sys


def _sign(nonce: str, api_key: str) -> str:
    return hmac.new(
        api_key.encode("utf-8"),
        nonce.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _format_server_message(data) -> str:
    if isinstance(data, list) and len(data) >= 2 and data[0] == "text":
        body = data[1]
        if isinstance(body, list):
            return "".join(str(x) for x in body)
        return str(body)
    return json.dumps(data, ensure_ascii=False)


async def _keepalive(ws, interval: float) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await ws.send(json.dumps(["text", ["idle"], {}]))
        except Exception:
            break


async def _recv_loop(ws) -> None:
    while True:
        raw = await ws.recv()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            print(raw, flush=True)
            continue
        if isinstance(data, dict) and data.get("type") == "auth_result":
            continue
        print(_format_server_message(data), flush=True)


async def run(url: str, api_key: str, keepalive_s: float) -> None:
    try:
        import websockets
    except ImportError:
        print("Install websockets: pip install websockets", file=sys.stderr)
        sys.exit(1)

    async with websockets.connect(url) as ws:
        raw = await ws.recv()
        challenge = json.loads(raw)
        if challenge.get("type") != "auth_challenge":
            print("Expected auth_challenge, got:", challenge, file=sys.stderr)
            sys.exit(1)
        nonce = challenge["nonce"]
        prefix = api_key[:20]
        await ws.send(
            json.dumps(
                {
                    "type": "auth_response",
                    "api_key": api_key,
                    "api_key_prefix": prefix,
                    "signature": _sign(nonce, api_key),
                }
            )
        )
        result = json.loads(await ws.recv())
        if result.get("type") != "auth_result" or result.get("status") != "success":
            print("Auth failed:", result, file=sys.stderr)
            sys.exit(1)
        print("Authenticated. Type game commands (or 'quit' to exit).", flush=True)

        recv_task = asyncio.create_task(_recv_loop(ws))
        ka_task = asyncio.create_task(_keepalive(ws, keepalive_s))

        try:
            while True:
                line = await asyncio.to_thread(sys.stdin.readline)
                if not line:
                    break
                line = line.strip()
                if line.lower() in ("quit", "exit"):
                    break
                if not line:
                    continue
                await ws.send(json.dumps(["text", [line], {}]))
        finally:
            recv_task.cancel()
            ka_task.cancel()
            for t in (recv_task, ka_task):
                try:
                    await t
                except asyncio.CancelledError:
                    pass


def main() -> None:
    p = argparse.ArgumentParser(description="Claw Adventure WS client with idle keepalive")
    p.add_argument(
        "--url",
        default=os.environ.get("CLAW_WS_URL", "wss://ws.adventure.mudclaw.net"),
    )
    p.add_argument(
        "--api-key",
        default=os.environ.get("CLAW_API_KEY", ""),
        help="Or set CLAW_API_KEY",
    )
    p.add_argument(
        "--keepalive",
        type=float,
        default=45.0,
        help="Seconds between idle pings (Evennia JSON ['text',['idle'],{}])",
    )
    args = p.parse_args()
    if not args.api_key:
        print("Set --api-key or CLAW_API_KEY", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(args.url, args.api_key, args.keepalive))


if __name__ == "__main__":
    main()
