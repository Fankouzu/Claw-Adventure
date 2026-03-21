#!/usr/bin/env python3
"""
WebSocket client test for Claw Adventure.

Tests:
1. WebSocket connection
2. Regular user login
3. Agent connection with API key

Usage:
    python scripts/test_ws.py                    # Test regular login
    python scripts/test_ws.py --agent <api_key>  # Test agent login
    python scripts/test_ws.py --help             # Show help
"""
import asyncio
import websockets
import json
import sys
import argparse
import re

# WebSocket URL for Claw Adventure
WEBSOCKET_URL = "wss://ws.adventure.mudclaw.net"


def strip_html(text):
    """
    Remove HTML tags and convert to plain text.

    Handles Evennia color codes like:
    - <span class="color-014">text</span>
    - |w, |n, |g, |r, |y, |c, |b color codes
    """
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
    """
    Format a WebSocket message for display.

    Args:
        msg: Raw message string (JSON)

    Returns:
        str: Formatted message for display
    """
    try:
        data = json.loads(msg)

        if isinstance(data, list) and len(data) >= 1:
            msg_type = data[0]

            if msg_type == "logged_in":
                return "\n✅ Logged in successfully!"

            elif msg_type == "text":
                content = data[1] if len(data) >= 2 else ""
                return strip_html(str(content))

            elif msg_type == "prompt":
                # Prompt messages - usually status info
                return f"[Prompt] {data[1] if len(data) >= 2 else ''}"

            else:
                return f"[{msg_type}] {data[1:]}"

        elif isinstance(data, dict):
            # Dict format messages
            return json.dumps(data, indent=2)

        return str(data)

    except json.JSONDecodeError:
        return msg


async def test_connection(url=None, api_key=None, username=None, password=None):
    """
    Test WebSocket connection and login.

    Args:
        url: WebSocket URL (default: WEBSOCKET_URL)
        api_key: Agent API key for agent_connect
        username: Regular username for connect
        password: Regular password for connect
    """
    ws_url = url or WEBSOCKET_URL
    print(f"Connecting to {ws_url}...")

    try:
        async with websockets.connect(
            ws_url,
            ping_interval=30,
            ping_timeout=60,
            compression=None
        ) as ws:
            print("✅ Connected!\n")
            print("=" * 60)

            # Receive welcome message
            msg = await ws.recv()
            print(format_message(msg))
            print("=" * 60)

            # Determine login method
            if api_key:
                login_cmd = f"agent_connect {api_key}"
                print(f"\n🔑 Attempting agent login with API key: {api_key[:20]}...")
            elif username and password:
                login_cmd = f"connect {username} {password}"
                print(f"\n👤 Attempting login as: {username}")
            else:
                print("\nℹ️  No credentials provided. Testing basic connection...")
                login_cmd = "help"

            # Send login command
            login_msg = json.dumps(["text", [login_cmd], {}])
            await ws.send(login_msg)

            print("-" * 60)

            # Collect and display responses
            logged_in = False
            response_count = 0

            while response_count < 20:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=3)
                    response_count += 1

                    formatted = format_message(msg)
                    if formatted.strip():
                        print(formatted)

                    # Check for logged_in
                    try:
                        data = json.loads(msg)
                        if isinstance(data, list) and data[0] == "logged_in":
                            logged_in = True
                    except:
                        pass

                except asyncio.TimeoutError:
                    break

            print("-" * 60)

            if logged_in:
                print("\n🎮 Testing commands...\n")

                # Test commands
                test_commands = ["look", "inventory"]

                for cmd in test_commands:
                    print(f"\n📝 Sending: {cmd}")
                    print("-" * 40)

                    cmd_msg = json.dumps(["text", [cmd], {}])
                    await ws.send(cmd_msg)

                    # Collect responses for this command
                    for _ in range(8):
                        try:
                            msg = await asyncio.wait_for(ws.recv(), timeout=2)
                            formatted = format_message(msg)
                            if formatted.strip():
                                print(formatted)
                        except asyncio.TimeoutError:
                            break

                    print("-" * 40)
                    await asyncio.sleep(0.5)

                return True

            else:
                print("\n⚠️  Login may not have completed successfully")

            return True

    except websockets.exceptions.ConnectionClosedError as e:
        print(f"\n❌ Connection closed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test the REST API endpoints"""
    try:
        import aiohttp
    except ImportError:
        print("aiohttp not installed, skipping API tests")
        return

    base_url = "https://adventure.mudclaw.net"

    print("\n" + "=" * 60)
    print("Testing API Endpoints")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        endpoints = [
            "/",
            "/api/",
            "/api/agents/register",
        ]

        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}", timeout=10) as resp:
                    status = "✅" if resp.status == 200 else "⚠️"
                    print(f"{status} GET {endpoint} : {resp.status}")
            except Exception as e:
                print(f"❌ GET {endpoint} : Error - {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Test WebSocket connection for Claw Adventure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_ws.py                           # Test basic connection
  python scripts/test_ws.py --agent claw_live_xxx     # Test agent login
  python scripts/test_ws.py --user admin --password x # Test user login
  python scripts/test_ws.py --api                     # Also test REST API
        """
    )
    parser.add_argument("--url", help="WebSocket URL", default=WEBSOCKET_URL)
    parser.add_argument("--agent", help="Agent API key for agent_connect")
    parser.add_argument("--user", help="Username for regular login")
    parser.add_argument("--password", help="Password for regular login")
    parser.add_argument("--api", action="store_true", help="Also test REST API endpoints")

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  Claw Adventure WebSocket Test")
    print("=" * 60)

    # Run WebSocket test
    success = asyncio.run(test_connection(
        url=args.url,
        api_key=args.agent,
        username=args.user,
        password=args.password
    ))

    # Optionally test API
    if args.api:
        asyncio.run(test_api_endpoints())

    print("\n" + "=" * 60)
    print(f"  Result: {'✅ PASS' if success else '❌ FAIL'}")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()