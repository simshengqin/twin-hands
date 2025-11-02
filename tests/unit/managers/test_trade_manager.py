"""
Unit tests for TradeManager.

Tests one-directional trading between decks (GDD v6.1 4-4).
GDD v6.1: Trade 1 card at a time, giving deck redraws, receiving deck accumulates.
"""

import pytest
from src.managers.trade_manager import TradeManager
from src.managers.deck_manager import DeckManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource


class TestTradeManager:
    """Test TradeManager in isolation (GDD v6.1 4-4)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig(
            trade_tokens_per_round=2,
            visible_cards_per_deck=7
        )
        state = TwinHandsState(config)

        # Initialize decks with deckbuilder model
        deck_mgr = DeckManager(config, state)
        deck_mgr.split_deck()

        manager = TradeManager(config, state)
        return config, state, manager

    # === VALIDATION ===

    def test_can_trade_initially(self, setup):
        """Can trade when tokens available and source has cards."""
        config, state, manager = setup

        # Both decks have 7 visible cards
        assert manager.can_trade(source_deck=0, target_deck=1) == True
        assert manager.can_trade(source_deck=1, target_deck=0) == True

    def test_cannot_trade_when_no_tokens(self, setup):
        """Cannot trade when no trade tokens left."""
        config, state, manager = setup

        # Spend all trade tokens
        state.trade_tokens = 0

        assert manager.can_trade(source_deck=0, target_deck=1) == False

    def test_cannot_trade_to_same_deck(self, setup):
        """Cannot trade from deck to itself."""
        config, state, manager = setup

        assert manager.can_trade(source_deck=0, target_deck=0) == False
        assert manager.can_trade(source_deck=1, target_deck=1) == False

    def test_cannot_trade_if_source_empty(self, setup):
        """Cannot trade if source deck has no visible cards."""
        config, state, manager = setup

        # Remove all visible cards from deck 0
        state.decks[0].visible_cards = []

        assert manager.can_trade(source_deck=0, target_deck=1) == False

    # === TRADING MECHANICS ===

    def test_trade_card_basic(self, setup):
        """GDD v6.1 4-4: Trade 1 card from source to target."""
        config, state, manager = setup

        deck_0 = state.decks[0]
        deck_1 = state.decks[1]

        # Snapshot state before trade
        card_to_trade = deck_0.visible_cards[2]  # Trade 3rd card
        deck_0_initial_count = len(deck_0.visible_cards)
        deck_1_initial_count = len(deck_1.visible_cards)
        tokens_before = state.trade_tokens

        # Trade card from deck 0 → deck 1
        result = manager.trade_card(source_deck=0, target_deck=1, card_index=2)

        assert result == True
        # Source deck: Stayed at same count (redrew 1 card)
        assert len(deck_0.visible_cards) == deck_0_initial_count
        # Target deck: Gained 1 card
        assert len(deck_1.visible_cards) == deck_1_initial_count + 1
        # Traded card is in target deck
        assert card_to_trade in deck_1.visible_cards
        # Traded card is NOT in source deck
        assert card_to_trade not in deck_0.visible_cards
        # Trade token spent
        assert state.trade_tokens == tokens_before - 1

    def test_trade_card_giving_deck_redraws(self, setup):
        """GDD v6.1 4-4: Giving deck redraws 1 card from draw pile."""
        config, state, manager = setup

        deck_0 = state.decks[0]
        draw_pile_before = len(deck_0.draw_pile)

        # Trade 1 card
        manager.trade_card(source_deck=0, target_deck=1, card_index=0)

        # Deck 0 drew 1 card from draw pile
        draw_pile_after = len(deck_0.draw_pile)
        assert draw_pile_before - draw_pile_after == 1

        # Deck 0 still has same number of visible cards
        assert len(deck_0.visible_cards) == config.visible_cards_per_deck

    def test_trade_card_receiving_deck_accumulates(self, setup):
        """GDD v6.1 4-4: Receiving deck can accumulate to 8, 9+ cards."""
        config, state, manager = setup

        deck_1 = state.decks[1]
        initial_count = len(deck_1.visible_cards)  # Should be 7

        # Trade 1 card → deck 1
        manager.trade_card(source_deck=0, target_deck=1, card_index=0)

        # Deck 1 now has 8 cards
        assert len(deck_1.visible_cards) == initial_count + 1

        # Trade another card → deck 1
        manager.trade_card(source_deck=0, target_deck=1, card_index=0)

        # Deck 1 now has 9 cards (can stack beyond 8)
        assert len(deck_1.visible_cards) == initial_count + 2

    def test_trade_card_spends_token(self, setup):
        """Trading should spend 1 trade token."""
        config, state, manager = setup

        initial_tokens = state.trade_tokens

        manager.trade_card(source_deck=0, target_deck=1, card_index=0)

        assert state.trade_tokens == initial_tokens - 1

    def test_trade_card_fails_if_no_tokens(self, setup):
        """Cannot trade if no tokens left."""
        config, state, manager = setup

        # Spend all tokens
        state.trade_tokens = 0

        result = manager.trade_card(source_deck=0, target_deck=1, card_index=0)
        assert result == False

    def test_trade_card_fails_if_invalid_index(self, setup):
        """Cannot trade with invalid card index."""
        config, state, manager = setup

        deck_0 = state.decks[0]
        num_cards = len(deck_0.visible_cards)

        # Try to trade card at invalid index
        result = manager.trade_card(source_deck=0, target_deck=1, card_index=num_cards + 10)
        assert result == False

    def test_trade_bidirectional_possible(self, setup):
        """Can trade in both directions (not forced swap)."""
        config, state, manager = setup

        # Trade deck 0 → deck 1
        manager.trade_card(source_deck=0, target_deck=1, card_index=0)

        # Can also trade deck 1 → deck 0
        result = manager.trade_card(source_deck=1, target_deck=0, card_index=0)
        assert result == True

    # === GODOT-READY ===

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        assert not hasattr(manager, 'trade_tokens')  # This is in state
