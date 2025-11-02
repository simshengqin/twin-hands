"""
Unit tests for TokenManager.

Tests token spending, validation logic for GDD v6.1 token system.
GDD v6.1: Unlimited hand tokens (max 2 per deck), discard tokens (3), trade tokens (2).
"""

import pytest
from src.managers.token_manager import TokenManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TestTokenManager:
    """Test TokenManager in isolation (GDD v6.1: discard + trade tokens)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig(
            num_decks=2,
            discard_tokens_per_round=3,
            trade_tokens_per_round=2,
            max_hands_per_deck=2
        )
        state = TwinHandsState(config)
        manager = TokenManager(config, state)
        return config, state, manager

    # === HAND PLAYING (GDD v6.1: Unlimited, max 2 per deck) ===

    def test_can_play_hand_initially(self, setup):
        """GDD v6.1: Can play hands initially (unlimited tokens)."""
        config, state, manager = setup
        assert manager.can_play_hand(deck_index=0) == True
        assert manager.can_play_hand(deck_index=1) == True

    def test_can_play_hand_respects_max_per_deck(self, setup):
        """GDD v6.1 4-3: Cannot play more than max hands per deck."""
        config, state, manager = setup

        # Play max hands from deck 0
        for _ in range(config.max_hands_per_deck):
            manager.record_hand_played(deck_index=0)

        # Should not be able to play another from deck 0
        assert manager.can_play_hand(deck_index=0) == False

        # But should still be able to play from deck 1
        assert manager.can_play_hand(deck_index=1) == True

    def test_record_hand_played_increments_counter(self, setup):
        """Recording hand played should track hands per deck."""
        config, state, manager = setup

        manager.record_hand_played(deck_index=0)
        assert state.hands_played_per_deck[0] == 1
        assert state.hands_played_per_deck[1] == 0

        manager.record_hand_played(deck_index=1)
        assert state.hands_played_per_deck[0] == 1
        assert state.hands_played_per_deck[1] == 1

    def test_record_hand_played_fails_if_max_reached(self, setup):
        """GDD v6.1: Cannot record if max hands per deck reached."""
        config, state, manager = setup

        # Play max hands from deck 0
        for _ in range(config.max_hands_per_deck):
            manager.record_hand_played(deck_index=0)

        # Next attempt should fail
        result = manager.record_hand_played(deck_index=0)
        assert result == False
        assert state.hands_played_per_deck[0] == config.max_hands_per_deck  # Unchanged

    # === DISCARD TOKENS (GDD v6.1: 3 per round) ===

    def test_initial_discard_tokens(self, setup):
        """GDD v6.1: Start with discard tokens from config."""
        config, state, manager = setup
        assert state.discard_tokens == config.discard_tokens_per_round

    def test_can_discard_when_tokens_available(self, setup):
        """Should be able to discard if tokens available."""
        config, state, manager = setup
        assert manager.can_discard() == True

    def test_cannot_discard_when_no_tokens(self, setup):
        """Cannot discard if no tokens left."""
        config, state, manager = setup

        # Spend all discard tokens
        for _ in range(config.discard_tokens_per_round):
            manager.spend_discard_token()

        assert manager.can_discard() == False

    def test_spend_discard_token_decrements(self, setup):
        """Spending discard token should decrement count."""
        config, state, manager = setup
        initial = state.discard_tokens

        assert manager.spend_discard_token() == True
        assert state.discard_tokens == initial - 1

    def test_spend_discard_token_fails_when_none_left(self, setup):
        """Cannot spend discard token if none left."""
        config, state, manager = setup

        # Spend all tokens
        for _ in range(config.discard_tokens_per_round):
            manager.spend_discard_token()

        # Next attempt should fail
        result = manager.spend_discard_token()
        assert result == False
        assert state.discard_tokens == 0  # Unchanged

    # === TRADE TOKENS (GDD v6.1: 2 per round) ===

    def test_initial_trade_tokens(self, setup):
        """GDD v6.1: Start with trade tokens from config."""
        config, state, manager = setup
        assert state.trade_tokens == config.trade_tokens_per_round

    def test_can_trade_when_tokens_available(self, setup):
        """Should be able to trade if tokens available."""
        config, state, manager = setup
        assert manager.can_trade() == True

    def test_cannot_trade_when_no_tokens(self, setup):
        """Cannot trade if no tokens left."""
        config, state, manager = setup

        # Spend all trade tokens
        for _ in range(config.trade_tokens_per_round):
            manager.spend_trade_token()

        assert manager.can_trade() == False

    def test_spend_trade_token_decrements(self, setup):
        """Spending trade token should decrement count."""
        config, state, manager = setup
        initial = state.trade_tokens

        assert manager.spend_trade_token() == True
        assert state.trade_tokens == initial - 1

    def test_spend_trade_token_fails_when_none_left(self, setup):
        """Cannot spend trade token if none left."""
        config, state, manager = setup

        # Spend all tokens
        for _ in range(config.trade_tokens_per_round):
            manager.spend_trade_token()

        # Next attempt should fail
        result = manager.spend_trade_token()
        assert result == False
        assert state.trade_tokens == 0  # Unchanged

    # === ROUND RESET ===

    def test_reset_for_new_round_restores_tokens(self, setup):
        """Reset should restore tokens from config."""
        config, state, manager = setup

        # Spend some tokens
        manager.spend_discard_token()
        manager.spend_trade_token()
        manager.record_hand_played(0)

        # Reset for new round
        manager.reset_for_new_round()

        # Tokens restored
        assert state.discard_tokens == config.discard_tokens_per_round
        assert state.trade_tokens == config.trade_tokens_per_round
        assert state.hands_played_per_deck == [0, 0]

    # === GODOT-READY ===

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        # Data is in state, not manager
        assert not hasattr(manager, 'discard_tokens')
        assert not hasattr(manager, 'trade_tokens')
