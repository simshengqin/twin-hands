"""
Unit tests for TokenManager.

Tests token spending, refunding, and validation logic (PHASE A).
"""

import pytest
from src.managers.token_manager import TokenManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TestTokenManager:
    """Test TokenManager in isolation (PHASE A: hand tokens only)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig(
            num_decks=2,
            hand_tokens_per_round=4,
            max_hands_per_deck=2
        )
        state = TwinHandsState(config)
        manager = TokenManager(config, state)
        return config, state, manager

    def test_initial_hand_tokens(self, setup):
        """GDD 4-3: Start with 4 hand tokens."""
        config, state, manager = setup
        assert state.hand_tokens == 4

    def test_can_spend_hand_token_when_available(self, setup):
        """Should be able to spend hand token if available."""
        config, state, manager = setup
        assert manager.can_spend_hand_token(deck_index=0) == True

    def test_can_spend_hand_token_when_none_left(self, setup):
        """Cannot spend hand token if none left."""
        config, state, manager = setup

        # Spend all 4 tokens
        for _ in range(4):
            manager.spend_hand_token(deck_index=0)

        assert manager.can_spend_hand_token(deck_index=0) == False

    def test_can_spend_hand_token_respects_max_hands_per_deck(self, setup):
        """GDD 4-3: Cannot play more than 2 hands per deck."""
        config, state, manager = setup

        # Play 2 hands from deck 0
        manager.spend_hand_token(deck_index=0)
        manager.spend_hand_token(deck_index=0)

        # Should not be able to play 3rd hand from deck 0
        assert manager.can_spend_hand_token(deck_index=0) == False

        # But should still be able to play from deck 1
        assert manager.can_spend_hand_token(deck_index=1) == True

    def test_spend_hand_token_decrements_tokens(self, setup):
        """Spending hand token should decrement count."""
        config, state, manager = setup

        assert manager.spend_hand_token(deck_index=0) == True
        assert state.hand_tokens == 3

    def test_spend_hand_token_increments_deck_counter(self, setup):
        """Spending hand token should track hands per deck."""
        config, state, manager = setup

        manager.spend_hand_token(deck_index=0)
        assert state.hands_played_per_deck[0] == 1
        assert state.hands_played_per_deck[1] == 0

        manager.spend_hand_token(deck_index=1)
        assert state.hands_played_per_deck[0] == 1
        assert state.hands_played_per_deck[1] == 1

    def test_spend_hand_token_fails_if_max_hands_reached(self, setup):
        """GDD 4-3: Cannot spend if max hands per deck reached."""
        config, state, manager = setup

        # Play 2 hands from deck 0
        manager.spend_hand_token(deck_index=0)
        manager.spend_hand_token(deck_index=0)

        # 3rd attempt should fail
        result = manager.spend_hand_token(deck_index=0)
        assert result == False
        assert state.hand_tokens == 2  # Tokens not spent
        assert state.hands_played_per_deck[0] == 2  # Counter unchanged

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        assert not hasattr(manager, 'hand_tokens')  # This is in state
