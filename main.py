"""Entry point for launching the websocket game server."""

import asyncio
import logging

from utils.websocket_server import WebSocketServer


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info("Starting the WebSocket server...")
    server = WebSocketServer()
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
