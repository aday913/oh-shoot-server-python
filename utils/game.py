from __future__ import annotations

import logging
from typing import Dict, List

from .classes import Card, Player, Deck

log = logging.getLogger(__name__)


class Game:
    """Manage a full match consisting of several individual games.

    The class is intentionally verbose and heavily commented so it can serve as
    a starting point for future rule extensions.
    """

    # Mapping of game number to the rules for that game
    GAME_RULES: Dict[int, Dict[str, int]] = {
        1: {"cards": 7, "sets": 2, "runs": 0},
        2: {"cards": 8, "sets": 1, "runs": 1},
        3: {"cards": 9, "sets": 0, "runs": 2},
        4: {"cards": 10, "sets": 3, "runs": 0},
        5: {"cards": 11, "sets": 2, "runs": 1},
        6: {"cards": 12, "sets": 1, "runs": 2},
    }

    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.current_game: int = 1
        self.deck: Deck | None = None

    # ------------------------------------------------------------------
    # Player management
    # ------------------------------------------------------------------
    def add_player(self, player: Player):
        log.debug("Adding player %s", player.name)
        self.players[player.id] = player

    def remove_player(self, player_id: str):
        self.players.pop(player_id, None)

    def ready_player(self, player_id: str):
        self.players[player_id].ready = True

    def all_ready(self) -> bool:
        return bool(self.players) and all(p.ready for p in self.players.values())

    # ------------------------------------------------------------------
    # Game lifecycle
    # ------------------------------------------------------------------
    def start_game(self):
        """Start a new game within the match."""
        rules = self.GAME_RULES[self.current_game]
        self.deck = Deck()

        # Deal cards to each player
        for player in self.players.values():
            player.hand = [self.deck.draw() for _ in range(rules["cards"])]
            player.melds = []
            player.ready = False

        # Flip the first card to the discard pile
        self.deck.discard(self.deck.draw())
        log.info("Game %s started with %s players", self.current_game, len(self.players))

    def end_game(self, winner_id: str):
        """End the current game and tally scores."""
        log.info("Game %s finished, winner: %s", self.current_game, winner_id)
        for player in self.players.values():
            if player.id != winner_id:
                player.score += self.calculate_hand_score(player.hand)
            player.hand = []
            player.melds = []
            player.ready = False

        # Prepare for next game
        self.current_game += 1
        if self.current_game not in self.GAME_RULES:
            self.current_game = 1  # Reset for a new match

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------
    def draw_card(self, player_id: str, source: str) -> Card:
        player = self.players[player_id]
        if source == "deck":
            card = self.deck.draw()
        else:
            card = self.deck.draw_discard()
        player.hand.append(card)
        return card

    def discard_card(self, player_id: str, card: Card):
        player = self.players[player_id]
        actual = self._remove_from_hand(player, card)
        self.deck.discard(actual)

    def go_down(self, player_id: str, sets: List[List[Card]], runs: List[List[Card]]):
        rules = self.GAME_RULES[self.current_game]
        if len(sets) != rules["sets"] or len(runs) != rules["runs"]:
            raise ValueError("Incorrect number of sets or runs supplied")

        player = self.players[player_id]

        for group in sets:
            if not self.is_set(group):
                raise ValueError("Invalid set")
        for group in runs:
            if not self.is_run(group):
                raise ValueError("Invalid run")

        # Remove used cards from the player's hand
        for group in sets + runs:
            for card in group:
                self._remove_from_hand(player, card)

        player.melds = sets + runs

    def play_card(self, player_id: str, target_id: str, meld_index: int, card: Card):
        player = self.players[player_id]
        target = self.players[target_id]
        actual = self._remove_from_hand(player, card)

        meld = target.melds[meld_index]
        meld.append(actual)
        if self.is_set(meld) or self.is_run(meld):
            return

        # Revert if not valid
        meld.pop()
        player.hand.append(actual)
        raise ValueError("Card cannot be played on that meld")

    def check_winner(self, player_id: str) -> bool:
        if not self.players[player_id].hand:
            self.end_game(player_id)
            return True
        return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _remove_from_hand(self, player: Player, card: Card) -> Card:
        for i, c in enumerate(player.hand):
            if c.suit == card.suit and c.rank == card.rank:
                return player.hand.pop(i)
        raise ValueError("Card not found in hand")

    def is_set(self, cards: List[Card]) -> bool:
        """Return True if the cards form a valid set."""
        if len(cards) < 3:
            return False
        ranks = {c.rank for c in cards if not c.is_wild}
        return len(ranks) <= 1

    def is_run(self, cards: List[Card]) -> bool:
        """Return True if the cards form a valid run."""
        if len(cards) < 4:
            return False
        non_wild = [c for c in cards if not c.is_wild]
        wilds = len(cards) - len(non_wild)
        suits = {c.suit for c in non_wild}
        if len(suits) > 1:
            return False
        values = sorted(c.value for c in non_wild)
        if any(values[i] == values[i + 1] for i in range(len(values) - 1)):
            return False
        needed = 0
        for i in range(len(values) - 1):
            gap = values[i + 1] - values[i] - 1
            needed += gap
        return needed <= wilds

    def calculate_hand_score(self, hand: List[Card]) -> int:
        score = 0
        for card in hand:
            if card.is_wild:
                score += 20
            elif card.rank == "Ace":
                score += 15
            elif card.rank in ["10", "Jack", "Queen", "King"]:
                score += 10
            elif card.rank in ["3", "4", "5", "6", "7", "8", "9"]:
                score += 5
        return score

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def get_state(self) -> dict:
        """Return a JSON‑serialisable representation of the entire game state."""
        return {
            "current_game": self.current_game,
            "players": [p.to_dict(reveal_hand=True) for p in self.players.values()],
            "deck_count": len(self.deck.cards) if self.deck else 0,
            "discard_top": self.deck.top_discard().to_dict() if self.deck and self.deck.top_discard() else None,
        }
