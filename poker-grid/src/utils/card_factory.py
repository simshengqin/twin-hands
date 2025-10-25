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
        from src.resources.game_config_resource import GameConfigResource

        deck = []
        for suit in GameConfigResource.SUITS:
            for rank in GameConfigResource.RANKS:
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

    @staticmethod
    def create_deck_resource() -> 'DeckResource':
        """
        Create a single DeckResource with standard 52 cards.
        Cards are NOT shuffled - draw_random() handles randomness.
        """
        from src.resources.deck_resource import DeckResource

        deck = CardFactory.create_deck()
        return DeckResource(cards=deck)
