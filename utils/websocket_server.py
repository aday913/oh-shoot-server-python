from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict

import websockets
from websockets.server import WebSocketServerProtocol

from .classes import Card, Player
from .game import Game


class WebSocketServer:
    """Class based websocket server that mediates between clients and game logic."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.game = Game()
        self.clients: Dict[str, WebSocketServerProtocol] = {}
        self.log = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    async def handler(self, websocket: WebSocketServerProtocol):
        """Handle an individual client connection."""
        player_id: str | None = None
        try:
            async for message in websocket:
                data = json.loads(message)
                action = data.get("action")
                if action == "join":
                    player_id = data["player_id"]
                    name = data.get("name", player_id)
                    player = Player(player_id, name)
                    self.game.add_player(player)
                    self.clients[player_id] = websocket
                    await self.send_state()
                elif action == "ready":
                    self.game.ready_player(player_id)
                    if self.game.all_ready():
                        self.game.start_game()
                    await self.send_state()
                elif action == "draw":
                    source = data.get("source", "deck")
                    self.game.draw_card(player_id, source)
                    await self.send_state()
                elif action == "discard":
                    card = Card.from_dict(data["card"])
                    self.game.discard_card(player_id, card)
                    await self.send_state()
                elif action == "go_down":
                    sets = [
                        [Card.from_dict(c) for c in group] for group in data.get("sets", [])
                    ]
                    runs = [
                        [Card.from_dict(c) for c in group] for group in data.get("runs", [])
                    ]
                    self.game.go_down(player_id, sets, runs)
                    await self.send_state()
                elif action == "play":
                    target = data["target"]
                    meld_index = data["meld_index"]
                    card = Card.from_dict(data["card"])
                    self.game.play_card(player_id, target, meld_index, card)
                    await self.send_state()
                elif action == "win":
                    if self.game.check_winner(player_id):
                        await self.send_state()
                elif action == "state":
                    await self.send_state()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if player_id:
                self.clients.pop(player_id, None)
                self.game.remove_player(player_id)

    # ------------------------------------------------------------------
    async def send_state(self):
        """Send the current game state to all connected clients."""
        state = self.game.get_state()
        message = json.dumps({"type": "state", "state": state})
        await asyncio.gather(
            *[client.send(message) for client in self.clients.values()],
            return_exceptions=True,
        )

    # ------------------------------------------------------------------
    async def start(self):
        """Start the websocket server and run forever."""
        async with websockets.serve(self.handler, self.host, self.port):
            self.log.info(
                "WebSocket server running on ws://%s:%s", self.host, self.port
            )
            await asyncio.Future()  # Run forever
