# main.py
# !/usr/bin/env python3
import sys
import signal
from screen_handler import BedrockScreenHandler
from rcon_server import RCONServer


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <bedrock_screen_session>")
        sys.exit(1)

    session_name = sys.argv[1]

    screen_handler = BedrockScreenHandler(session_name)
    rcon_server = RCONServer(screen_handler)

    def shutdown(sig, frame):
        print("\nShutting down...")
        rcon_server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)

    print(f"Starting RCONify for bedrock session: {session_name}")
    rcon_server.start()


if __name__ == "__main__":
    main()