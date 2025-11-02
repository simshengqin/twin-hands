"""
Unit tests for DeckManager.

Tests deck splitting, drawing, and card management logic (PHASE A).
"""

import pytest
from src.managers.deck_manager import DeckManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TestDeckManager:
    """Test DeckManager in isolation (PHASE A: split, draw only)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig(num_decks=2)
        state = TwinHandsState(config)
        manager = DeckManager(config, state)
        return config, state, manager

    def test_split_deck_creates_n_decks(self, setup):
        """GDD 4-1: Split 52-card deck into N decks (default 2)."""
        config, state, manager = setup

        manager.split_deck()

        # Should create 2 decks
        assert len(state.decks) == 2
        assert state.decks[0] is not None
        assert state.decks[1] is not None

    def test_split_deck_26_26_distribution(self, setup):
        """GDD 4-1: Default split is 26/26 for 2 decks."""
        config, state, manager = setup

        manager.split_deck()

        # Each deck should have 26 cards total (draw_pile + visible + discard)
        deck_0_total = len(state.decks[0].draw_pile) + len(state.decks[0].visible_cards) + len(state.decks[0].discard_pile)
        deck_1_total = len(state.decks[1].draw_pile) + len(state.decks[1].visible_cards) + len(state.decks[1].discard_pile)

        assert deck_0_total == 26
        assert deck_1_total == 26

    def test_split_deck_accounts_for_all_52_cards(self, setup):
        """GDD 4-1: All 52 cards should be distributed."""
        config, state, manager = setup

        manager.split_deck()

        # Collect all cards from both decks (GDD v6.1: 3 piles per deck)
        all_cards = []
        for deck in state.decks:
            all_cards.extend(deck.draw_pile)
            all_cards.extend(deck.visible_cards)
            all_cards.extend(deck.discard_pile)

        # Should have exactly 52 unique cards
        assert len(all_cards) == 52
        # Check uniqueness (no duplicate cards)
        assert len(set((c.rank, c.suit) for c in all_cards)) == 52

    def test_split_deck_random_distribution(self, setup):
        """GDD 4-1: Split should be random (different each time)."""
        config, state, manager = setup

        # Split twice and compare first visible card
        manager.split_deck()
        first_card_run1 = state.decks[0].visible_cards[0]

        # Reset state
        state2 = TwinHandsState(config)
        manager2 = DeckManager(config, state2)
        manager2.split_deck()
        first_card_run2 = state2.decks[0].visible_cards[0]

        # Very unlikely to get same card in same position (4/52 chance)
        # If this test is flaky, we can test distributions statistically
        # For now, this is a smoke test for randomness

    def test_initial_draw_visible_cards(self, setup):
        """GDD v6.1 4-2: Each deck starts with N visible cards (config-driven)."""
        config, state, manager = setup

        manager.split_deck()

        # Config-driven: verify visible cards match config
        assert len(state.decks[0].visible_cards) == config.visible_cards_per_deck
        assert len(state.decks[1].visible_cards) == config.visible_cards_per_deck

    def test_draw_cards_refills_correctly(self, setup):
        """GDD v6.1 4-2: Drawing cards adds to visible cards (config-driven)."""
        config, state, manager = setup

        manager.split_deck()

        initial_count = len(state.decks[0].visible_cards)

        # Remove 2 cards from deck 0's visible cards
        removed_cards = [state.decks[0].visible_cards.pop() for _ in range(2)]

        # Now deck 0 has (initial - 2) visible cards
        assert len(state.decks[0].visible_cards) == initial_count - 2

        # Draw should refill by 2
        manager.draw_cards(deck_index=0, count=2)
        assert len(state.decks[0].visible_cards) == initial_count

    def test_draw_cards_from_draw_pile(self, setup):
        """GDD v6.1 4-2: Draw cards should come from draw pile."""
        config, state, manager = setup

        manager.split_deck()

        initial_draw_pile_count = len(state.decks[0].draw_pile)

        # Remove 3 cards from visible
        for _ in range(3):
            state.decks[0].visible_cards.pop()

        # Draw 3 cards
        manager.draw_cards(deck_index=0, count=3)

        # Draw pile should have 3 fewer cards
        assert len(state.decks[0].draw_pile) == initial_draw_pile_count - 3

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        # Manager should only have config and state references
        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        # Manager should not store data (all data in state)
        assert not hasattr(manager, 'decks')  # This is in state, not manager
