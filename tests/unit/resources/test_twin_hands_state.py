"""
Unit tests for TwinHandsState.

Tests game state representation and validation.
"""

import pytest
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.twin_hands_config_resource import TwinHandsConfig


class TestTwinHandsState:
    """Test TwinHandsState resource (PHASE A: minimal, no trading/jokers)."""

    def test_initialization_with_config(self):
        """State should initialize with correct deck count from config."""
        config = TwinHandsConfig(num_decks=2)
        state = TwinHandsState(config)

        # RULE 6: Generic N decks
        assert len(state.decks) == 2
        assert len(state.scores) == 2
        assert len(state.hands_played_per_deck) == 2

        # Initial values
        assert all(score == 0 for score in state.scores)
        assert all(count == 0 for count in state.hands_played_per_deck)

    def test_initialization_with_3_decks(self):
        """State should support N decks (RULE 6: multiplayer-ready)."""
        config = TwinHandsConfig(num_decks=3)
        state = TwinHandsState(config)

        assert len(state.decks) == 3
        assert len(state.scores) == 3
        assert len(state.hands_played_per_deck) == 3

    def test_token_initialization(self):
        """Tokens should initialize from config (GDD v6.1: discard + trade tokens)."""
        config = TwinHandsConfig(
            discard_tokens_per_round=3,
            trade_tokens_per_round=2
        )
        state = TwinHandsState(config)

        # Config-driven: verify state matches config, not hardcoded values
        assert state.discard_tokens == config.discard_tokens_per_round
        assert state.trade_tokens == config.trade_tokens_per_round
        # GDD v6.1: Hand tokens unlimited (no tracking)

    def test_round_starts_at_1(self):
        """GDD 5-3: Rounds start at 1, not 0."""
        config = TwinHandsConfig()
        state = TwinHandsState(config)

        assert state.current_round == 1

    def test_decks_are_none_initially(self):
        """Decks should be None until populated by DeckManager."""
        config = TwinHandsConfig()
        state = TwinHandsState(config)

        # List exists with correct length, but contains None
        assert state.decks is not None
        assert len(state.decks) == 2  # Default config
        assert all(deck is None for deck in state.decks)

    def test_state_is_data_only(self):
        """RULE 3: State is data only, no logic."""
        config = TwinHandsConfig()
        state = TwinHandsState(config)

        # State should only have data attributes, no methods (except __init__)
        # This is verified by code review, not a runtime test
        assert hasattr(state, 'decks')
        assert hasattr(state, 'scores')
        assert hasattr(state, 'discard_tokens')  # GDD v6.1
        assert hasattr(state, 'trade_tokens')    # GDD v6.1
        assert hasattr(state, 'current_round')
