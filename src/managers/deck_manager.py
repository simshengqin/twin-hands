"""
DeckManager - Logic for deck splitting and card drawing.
In Godot: extends Node
"""

import random
from typing import List
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.deck_resource import DeckResource
from src.resources.card_resource import CardResource
from src.utils.card_factory import CardFactory


class DeckManager:
    """
    Manages deck splitting and card drawing (PHASE A).
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

    def split_deck(self) -> None:
        """
        GDD 4-1: Split 52-card deck into N decks.
        Default: 2 decks of 26 cards each (random split).
        Each deck starts with 4 visible cards (GDD 4-2).
        """
        # Create full 52-card deck (already shuffled)
        full_deck = CardFactory.create_shuffled_deck()

        # Split into N decks
        num_decks = self.config.num_decks
        cards_per_deck = 52 // num_decks  # 26 for 2 decks

        for i in range(num_decks):
            # Get this deck's cards
            start_idx = i * cards_per_deck
            end_idx = start_idx + cards_per_deck
            deck_cards = full_deck[start_idx:end_idx]

            # Draw initial 4 visible cards (GDD 4-2)
            visible_cards = deck_cards[:4]
            undrawn_cards = deck_cards[4:]

            # Create DeckResource
            deck = DeckResource(
                visible_cards=list(visible_cards),
                undrawn_cards=list(undrawn_cards)
            )

            # Store in state
            self.state.decks[i] = deck

    def draw_cards(self, deck_index: int, count: int) -> None:
        """
        GDD 4-2: Draw cards from undrawn pile to visible cards.
        Used after playing cards to refill to 4 visible.

        Args:
            deck_index: Which deck to draw from (0-indexed)
            count: Number of cards to draw
        """
        deck = self.state.decks[deck_index]

        # Draw from undrawn pile
        for _ in range(count):
            if deck.undrawn_cards:
                card = deck.undrawn_cards.pop(0)  # Draw from top
                deck.visible_cards.append(card)
