#!/usr/bin/env python3
"""
WebSocket client for Claw Adventure.

Interactive client - connect and type commands manually.

Usage:
    python scripts/ws_client.py                    # Connect to production
    python scripts/ws_client.py --local            # Connect to localhost
    python scripts/ws_client.py --url ws://...     # Custom URL
"""
import asyncio
import websockets
import json
import sys
import re
import os
import termios
import tty

# WebSocket URLs
WEBSOCKET_URL = "wss://ws.adventure.mudclaw.net"
LOCAL_URL = "ws://localhost:4002"


def strip_html(text):
    """Remove HTML tags and convert Evennia color codes to terminal colors."""
    if not text:
        return ""

    # Remove HTML tags but keep content
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<span[^>]*>', '', text)
    text = re.sub(r'</span>', '', text)
    text = re.sub(r'<[^>]+>', '', text)

    # Convert Evennia color codes to terminal colors
    color_map = {
        '|w': '\033[1;37m',  # White (bold)
        '|n': '\033[0m',     # Reset
        '|g': '\033[32m',    # Green
        '|r': '\033[31m',    # Red
        '|y': '\033[33m',    # Yellow
        '|c': '\033[36m',    # Cyan
        '|b': '\033[34m',    # Blue
        '|m': '\033[35m',    # Magenta
    }

    for code, term_color in color_map.items():
        text = text.replace(code, term_color)

    # Reset color at the end if needed
    if '\033[' in text:
        text = text + '\033[0m'

    return text


def format_message(msg):
    """Format a WebSocket message for display."""
    try:
        data = json.loads(msg)

        if isinstance(data, list) and len(data) >= 1:
            msg_type = data[0]

            if msg_type == "logged_in":
                return "\n✅ 已登录成功！\n"

            elif msg_type == "text":
                content = data[1] if len(data) >= 2 else ""
                return strip_html(str(content))

            elif msg_type == "prompt":
                return f"[状态] {data[1] if len(data) >= 2 else ''}"

            else:
                return f"[{msg_type}] {data[1:]}"

        elif isinstance(data, dict):
            return json.dumps(data, indent=2)

        return str(data)

    except json.JSONDecodeError:
        return msg


def read_line(prompt="> "):
    """Read a line of input, handling different terminal modes."""
    print(prompt, end='', flush=True)

    # Try standard input first
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        # Handle both \r\n and \n line endings
        return line.rstrip('\r\n')
    except:
        return None


async def receive_messages(ws, stop_event):
    """Background task to receive and print messages."""
    while not stop_event.is_set():
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
            formatted = format_message(msg)
            if formatted.strip():
                print(formatted)
        except asyncio.TimeoutError:
            continue
        except websockets.exceptions.ConnectionClosed:
            print("\n❌ 连接已关闭")
            stop_event.set()
            break


async def interactive_client(url):
    """Interactive WebSocket client."""
    print(f"正在连接到 {url}...")

    try:
        async with websockets.connect(
            url,
            ping_interval=30,
            ping_timeout=60,
            compression=None
        ) as ws:
            print("✅ 已连接！\n")
            print("=" * 60)

            # Receive welcome message
            msg = await ws.recv()
            print(format_message(msg))
            print("=" * 60)
            print("\n输入命令（输入 'quit' 退出）:\n")

            # Start background receiver
            stop_event = asyncio.Event()
            receive_task = asyncio.create_task(receive_messages(ws, stop_event))

            loop = asyncio.get_event_loop()

            try:
                while not stop_event.is_set():
                    # Get user input in thread pool (non-blocking)
                    try:
                        cmd = await loop.run_in_executor(None, read_line, "> ")
                    except:
                        break

                    if cmd is None:
                        break

                    if not cmd:
                        continue

                    if cmd.lower() == 'quit':
                        print("正在退出...")
                        break

                    # Send command
                    msg = json.dumps(["text", [cmd], {}])
                    await ws.send(msg)

                    # Small delay to let response arrive
                    await asyncio.sleep(0.1)

            except KeyboardInterrupt:
                print("\n正在退出...")

            finally:
                stop_event.set()
                receive_task.cancel()
                try:
                    await receive_task
                except asyncio.CancelledError:
                    pass

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"\n❌ 连接关闭: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Claw Adventure WebSocket 客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/ws_client.py                # 连接生产服务器
  python scripts/ws_client.py --local        # 连接本地服务器

登录命令:
  connect <用户名> <密码>        # 普通用户登录
  agent_connect <api_key>       # Agent 登录
  create <用户名> <密码>         # 创建新账户

输入 'quit' 退出
        """
    )
    parser.add_argument("--url", help="WebSocket URL")
    parser.add_argument("--local", action="store_true", help="连接本地服务器")

    args = parser.parse_args()

    # Determine URL
    if args.url:
        url = args.url
    elif args.local:
        url = LOCAL_URL
    else:
        url = WEBSOCKET_URL

    print("\n" + "=" * 60)
    print("  Claw Adventure WebSocket 客户端")
    print("=" * 60 + "\n")

    asyncio.run(interactive_client(url))


if __name__ == "__main__":
    main()