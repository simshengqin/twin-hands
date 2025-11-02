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
        GDD v6.1 4-1: Split 52-card deck into N decks.
        Default: 2 decks of 26 cards each (random split).
        Each deck starts with 7 visible cards (GDD v6.1 4-2).

        Deckbuilder Model:
        - Draw pile: 26 cards → deal 7 → 19 remaining
        - Discard pile: 0 cards (empty at start)
        - Visible cards: 7 cards
        """
        # Create full 52-card deck (already shuffled)
        full_deck = CardFactory.create_shuffled_deck()

        # Split into N decks
        num_decks = self.config.num_decks
        cards_per_deck = 52 // num_decks  # 26 for 2 decks
        visible_count = self.config.visible_cards_per_deck  # 7 in v6.1

        for i in range(num_decks):
            # Get this deck's cards
            start_idx = i * cards_per_deck
            end_idx = start_idx + cards_per_deck
            deck_cards = full_deck[start_idx:end_idx]

            # Deal initial visible cards (GDD v6.1: 7 cards)
            visible_cards = deck_cards[:visible_count]
            draw_pile = deck_cards[visible_count:]

            # Create DeckResource (GDD v6.1 deckbuilder model)
            deck = DeckResource(
                draw_pile=list(draw_pile),
                discard_pile=[],  # Empty at start
                visible_cards=list(visible_cards)
            )

            # Store in state
            self.state.decks[i] = deck

    def draw_cards(self, deck_index: int, count: int) -> None:
        """
        GDD v6.1 4-2: Draw cards from draw pile to visible cards.
        Used after playing/discarding cards to maintain 7 visible baseline.

        Deckbuilder Model:
        - If draw pile empty: Shuffle discard pile → New draw pile → Continue
        - Draw from draw pile → Add to visible cards

        Args:
            deck_index: Which deck to draw from (0-indexed)
            count: Number of cards to draw
        """
        deck = self.state.decks[deck_index]

        for _ in range(count):
            # If draw pile empty, shuffle discard pile (GDD v6.1 4-2)
            if not deck.draw_pile:
                deck.shuffle_discard_into_draw()

            # Draw from draw pile (if available)
            if deck.draw_pile:
                card = deck.draw_pile.pop(0)  # Draw from top
                deck.visible_cards.append(card)

    def discard_to_pile(self, deck_index: int, cards: List[CardResource]) -> None:
        """
        GDD v6.1 4-2: Move cards to discard pile.
        Used when playing or discarding cards.

        Args:
            deck_index: Which deck these cards came from
            cards: Cards to add to discard pile
        """
        deck = self.state.decks[deck_index]
        deck.discard_pile.extend(cards)
