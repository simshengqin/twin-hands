"""
TradeManager - Logic for trading cards between decks.
In Godot: extends Node
"""

from typing import List
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TradeManager:
    """
    Manages temporary trading between decks (GDD 4-4).
    Logic only - all data stored in state.

    In Godot: extends Node
    """

    def __init__(self, config: TwinHandsConfig, state: TwinHandsState):
        """
        Initialize manager with config and state.

        Args:
            config: Game configuration (immutable)
            state: Game state (mutable)
        """
        self.config = config
        self.state = state

    def can_trade(self, source_deck: int, num_cards: int) -> bool:
        """
        Check if trade is valid (GDD 4-4).

        Args:
            source_deck: Index of deck giving cards (0, 1, ...)
            num_cards: Number of cards to trade

        Returns:
            True if trade is allowed, False otherwise
        """
        # Must have trade tokens
        if self.state.trade_tokens <= 0:
            return False

        # Calculate receiving deck (for 2 decks: 0→1, 1→0)
        receiving_deck = 1 - source_deck

        # Receiving deck cannot exceed 8 cards
        receiving_deck_cards = len(self.state.decks[receiving_deck].visible_cards)
        if receiving_deck_cards + num_cards > 8:
            return False

        return True

    def trade_cards(self, source_deck: int, card_indices: List[int]):
        """
        Trade cards from source deck to receiving deck (GDD 4-4).

        - Giving deck: Removes cards, draws replacements (stays at 4)
        - Receiving deck: Adds cards (up to 8 max)
        - Spends 1 trade token

        Args:
            source_deck: Index of deck giving cards
            card_indices: Indices of cards to trade from source deck
        """
        num_cards = len(card_indices)

        # Validate trade
        if not self.can_trade(source_deck, num_cards):
            return False

        # Calculate receiving deck
        receiving_deck = 1 - source_deck

        source = self.state.decks[source_deck]
        receiver = self.state.decks[receiving_deck]

        # Remove cards from source (in reverse to preserve indices)
        traded_cards = []
        for i in sorted(card_indices, reverse=True):
            card = source.visible_cards.pop(i)
            traded_cards.append(card)

        # Add to receiving deck
        receiver.visible_cards.extend(reversed(traded_cards))

        # Source deck draws replacements
        from src.managers.deck_manager import DeckManager
        deck_mgr = DeckManager(self.config, self.state)
        deck_mgr.draw_cards(source_deck, num_cards)

        # Spend trade token
        self.state.trade_tokens -= 1

        return True
