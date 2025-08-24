from __future__ import annotations

import logging

log = logging.getLogger(__name__)

class Player:
    """Represents an individual participant in the match."""

    def __init__(self, id: str, name: str):
        self.id: str = id
        self.name: str = name
        self.score: int = 0
        # Cards currently held in the player's hand
        self.hand: list[Card] = []
        # Cards that have been played down as sets or runs
        self.melds: list[list[Card]] = []
        # Players must issue a ``ready`` command before each game starts
        self.ready: bool = False

    def __str__(self):
        return self.name

    def add_card(self, card):
        """Add a card to the player's hand."""
        if not isinstance(card, Card):
            logging.error(f"Invalid card type: {type(card)}")
            raise TypeError("Expected a Card instance.")
        logging.debug(f"Adding card {card} to player {self.name}'s hand.")
        self.hand.append(card)

    def discard(self, card):
        """Discard a card from the player's hand."""
        if card not in self.hand:
            logging.error(f"Card {card} not found in player's hand.")
            raise ValueError("Card not found in player's hand.")
        logging.debug(f"Discarding card {card} from player {self.name}'s hand.")
        self.hand.remove(card)
        return card

    def to_dict(self, reveal_hand: bool = False) -> dict:
        """Serialise the player for transmission to clients.

        Parameters
        ----------
        reveal_hand:
            If ``True`` the returned dictionary includes the full hand.  When
            ``False`` only the number of cards is exposed which is safer when
            broadcasting the state to all participants.
        """

        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "hand": [c.to_dict() for c in self.hand]
            if reveal_hand
            else len(self.hand),
            "melds": [[c.to_dict() for c in meld] for meld in self.melds],
            "ready": self.ready,
        }


class Card:
    """Representation of a single playing card."""

    def __init__(self, suit: str, rank: str):
        if suit not in ["Hearts", "Diamonds", "Clubs", "Spades", "Joker"]:
            logging.error(f"Invalid suit: {suit}")
            raise ValueError(
                "Invalid suit. Must be one of Hearts, Diamonds, Clubs, Spades, or Joker."
            )

        if rank not in [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
            "Ace",
            "Joker",
        ]:
            logging.error(f"Invalid rank: {rank}")
            raise ValueError(
                "Invalid rank. Must be one of 2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King, Ace, or Joker."
            )

        self.suit: str = suit
        self.rank: str = rank

        if rank == "2":
            self.is_wild: bool = True
        elif rank == "Joker":
            self.is_wild: bool = True
        else:
            self.is_wild: bool = False

    def __str__(self):
        return f"{self.rank}{self.suit[0].upper()}"

    def to_dict(self) -> dict:
        """Serialise the card."""
        return {"suit": self.suit, "rank": self.rank}

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Create a card instance from a dictionary."""
        return cls(data["suit"], data["rank"])

    @property
    def value(self) -> int:
        """Return the numeric value of the rank for comparison and runs."""
        order = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "Jack": 11,
            "Queen": 12,
            "King": 13,
            "Ace": 14,
            "Joker": 15,
        }
        return order[self.rank]


class Deck:
    """Representation of a playing deck with a discard pile."""

    def __init__(self):
        self.cards: list[Card] = []
        self.discard_pile: list[Card] = []
        self._build()

    def _build(self):
        """Initialise the deck (including two jokers) and shuffle it."""
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "Jack",
            "Queen",
            "King",
            "Ace",
        ]

        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

        # Add two jokers
        self.cards.append(Card("Joker", "Joker"))
        self.cards.append(Card("Joker", "Joker"))

        self.shuffle()

    def shuffle(self):
        import random

        random.shuffle(self.cards)

    def draw(self) -> Card:
        """Draw a card from the deck."""
        if not self.cards:
            raise ValueError("The deck is empty.")
        return self.cards.pop()

    def draw_discard(self) -> Card:
        """Draw a card from the discard pile."""
        if not self.discard_pile:
            raise ValueError("The discard pile is empty.")
        return self.discard_pile.pop()

    def discard(self, card: Card):
        """Place a card on the discard pile."""
        self.discard_pile.append(card)

    def top_discard(self) -> Card | None:
        """Peek at the top of the discard pile without removing it."""
        return self.discard_pile[-1] if self.discard_pile else None
