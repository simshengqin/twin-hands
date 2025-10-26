"""
Card Factory Utility - Godot-ready card/deck creation
Static utility class for creating and shuffling decks.
In Godot: class with static functions (no extends)
"""

import random
from typing import List


class CardFactory:
    """
    Factory for creating and shuffling decks.
    In Godot, this would be a static class or namespace with static funcs.

    GDScript equivalent:
    class_name CardFactory

    static func create_deck() -> Array[CardResource]:
        # ...

    static func shuffle_deck(deck: Array[CardResource]) -> void:
        # ...
    """

    @staticmethod
    def create_deck() -> List['CardResource']:
        """Create a standard 52-card deck."""
        from src.resources.card_resource import CardResource

        # Standard poker deck constants
        SUITS = ["hearts", "diamonds", "clubs", "spades"]
        RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        deck = []
        for suit in SUITS:
            for rank in RANKS:
                deck.append(CardResource(rank=rank, suit=suit))
        return deck

    @staticmethod
    def shuffle_deck(deck: List['CardResource']) -> None:
        """
        Shuffle a deck in place.
        In Godot, you'd use: deck.shuffle() or use RandomNumberGenerator
        """
        random.shuffle(deck)

    @staticmethod
    def create_shuffled_deck() -> List['CardResource']:
        """Create and shuffle a new deck."""
        deck = CardFactory.create_deck()
        CardFactory.shuffle_deck(deck)
        return deck
