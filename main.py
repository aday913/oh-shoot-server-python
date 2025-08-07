import logging

from utils.classes import Player, Card
from utils.websocket_server import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting the WebSocket server...")
    # main()  # Start the WebSocket server
