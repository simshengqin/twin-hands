"""
Unit tests for TradeManager.

Tests temporary trading between decks (GDD 4-4).
"""

import pytest
from src.managers.trade_manager import TradeManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource


class TestTradeManager:
    """Test TradeManager in isolation (GDD 4-4)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig()
        state = TwinHandsState(config)

        # Initialize decks with cards
        from src.managers.deck_manager import DeckManager
        deck_mgr = DeckManager(config, state)
        deck_mgr.split_deck()

        manager = TradeManager(config, state)
        return config, state, manager

    def test_initial_trade_tokens(self, setup):
        """GDD 4-4: Start with 3 trade tokens."""
        config, state, manager = setup

        # After split_deck, trade tokens should be initialized
        # (Assuming GameManager.start_round() sets them)
        state.trade_tokens = config.trade_tokens_per_round

        assert state.trade_tokens == 3  # GDD 4-4

    def test_can_trade_when_tokens_available(self, setup):
        """Can trade when trade tokens > 0 and receiving deck < 8 cards."""
        config, state, manager = setup
        state.trade_tokens = 3

        # Both decks start with 4 cards
        assert manager.can_trade(source_deck=0, num_cards=1) == True

    def test_cannot_trade_when_no_tokens(self, setup):
        """Cannot trade when no trade tokens left."""
        config, state, manager = setup
        state.trade_tokens = 0

        assert manager.can_trade(source_deck=0, num_cards=1) == False

    def test_cannot_trade_if_receiving_exceeds_8(self, setup):
        """GDD 4-4: Cannot trade if receiving deck would exceed 8 cards."""
        config, state, manager = setup
        state.trade_tokens = 3

        # Give Deck 2 7 cards (4 visible + 3 traded)
        deck_2 = state.decks[1]
        for i in range(3):
            deck_2.visible_cards.append(CardResource(rank="A", suit="hearts"))

        # Now Deck 2 has 7 cards. Trading 2 more would exceed 8.
        assert manager.can_trade(source_deck=0, num_cards=2) == False

    def test_trade_cards_basic(self, setup):
        """GDD 4-4: Trade 2 cards from Deck 0 to Deck 1."""
        config, state, manager = setup
        state.trade_tokens = 3

        deck_0 = state.decks[0]
        deck_1 = state.decks[1]

        # Snapshot cards before trade
        cards_to_trade = deck_0.visible_cards[:2].copy()
        deck_0_count_before = len(deck_0.visible_cards)
        deck_1_count_before = len(deck_1.visible_cards)

        # Trade 2 cards: Deck 0 → Deck 1
        manager.trade_cards(source_deck=0, card_indices=[0, 1])

        # Deck 0: Still has 4 cards (drew replacements)
        assert len(deck_0.visible_cards) == deck_0_count_before

        # Deck 1: Now has 6 cards (4 + 2 traded)
        assert len(deck_1.visible_cards) == deck_1_count_before + 2

        # Trade token spent
        assert state.trade_tokens == 2

    def test_trade_cards_draws_replacements(self, setup):
        """GDD 4-4: Giving deck draws replacement cards."""
        config, state, manager = setup
        state.trade_tokens = 3

        deck_0 = state.decks[0]
        undrawn_before = len(deck_0.undrawn_cards)

        # Trade 3 cards
        manager.trade_cards(source_deck=0, card_indices=[0, 1, 2])

        # Deck 0 drew 3 replacements from undrawn pile
        undrawn_after = len(deck_0.undrawn_cards)
        assert undrawn_before - undrawn_after == 3

        # Deck 0 still has 4 visible cards
        assert len(deck_0.visible_cards) == 4

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        assert not hasattr(manager, 'trade_tokens')  # This is in state
