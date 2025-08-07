import logging

log = logging.getLogger(__name__)

class Player:
    def __init__(self, id: str, name: str):
        self.id: str = id
        self.name: str = name
        self.score: int = 0
        self.hand: list[Card] = []
        self.area: list = []  # This is the area where played cards are stored

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


class Card:
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
