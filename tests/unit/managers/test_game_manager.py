"""
Unit tests for GameManager.

Tests game orchestration, round flow, and manager coordination (PHASE A).
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig


class TestGameManager:
    """Test GameManager orchestration (PHASE A: basic game flow)."""

    @pytest.fixture
    def game(self):
        """Create a GameManager for testing."""
        config = TwinHandsConfig()
        return GameManager(config)

    def test_initialization(self, game):
        """GameManager should initialize with all managers."""
        assert game.config is not None
        assert game.state is not None
        assert game.deck_manager is not None
        assert game.token_manager is not None
        assert game.scoring_manager is not None

    def test_start_game_splits_deck(self, game):
        """start_game should split deck into N decks."""
        game.start_game()

        # Decks should be created
        assert game.state.decks[0] is not None
        assert game.state.decks[1] is not None

        # Each deck should have N visible cards (config-driven)
        assert len(game.state.decks[0].visible_cards) == game.config.visible_cards_per_deck
        assert len(game.state.decks[1].visible_cards) == game.config.visible_cards_per_deck

    def test_play_hand_basic_flow(self, game):
        """play_hand should evaluate hand, record play, draw cards."""
        game.start_game()

        # Get initial visible cards from deck 0
        initial_cards = game.state.decks[0].visible_cards[:2]  # Use first 2 cards
        card_indices = [0, 1]  # Indices in visible_cards

        # Play hand
        result = game.play_hand(deck_index=0, card_indices=card_indices)

        # Should succeed
        assert result["success"] == True
        assert "hand" in result

        # GDD v6.1: Hand tokens unlimited, but hands played tracked
        assert game.state.hands_played_per_deck[0] == 1

        # Visible cards should be refilled (config-driven)
        assert len(game.state.decks[0].visible_cards) == game.config.visible_cards_per_deck

    def test_play_hand_respects_max_hands_per_deck(self, game):
        """GDD 4-3: Cannot play more than 2 hands per deck."""
        game.start_game()

        # Play 2 hands from deck 0
        game.play_hand(deck_index=0, card_indices=[0, 1])
        game.play_hand(deck_index=0, card_indices=[0, 1])

        # 3rd attempt should fail
        result = game.play_hand(deck_index=0, card_indices=[0, 1])
        assert result["success"] == False
        assert "error" in result

    def test_play_hand_unlimited_within_max_per_deck(self, game):
        """GDD v6.1 4-3: Hand tokens unlimited, only max per deck enforced."""
        game.start_game()

        # Play 2 hands from each deck (max 2 per deck)
        result1 = game.play_hand(deck_index=0, card_indices=[0, 1])
        result2 = game.play_hand(deck_index=0, card_indices=[0, 1])
        result3 = game.play_hand(deck_index=1, card_indices=[0, 1])
        result4 = game.play_hand(deck_index=1, card_indices=[0, 1])

        # All 4 should succeed (hand tokens unlimited)
        assert result1["success"] == True
        assert result2["success"] == True
        assert result3["success"] == True
        assert result4["success"] == True

        # Both decks should be at max
        assert game.state.hands_played_per_deck[0] == game.config.max_hands_per_deck
        assert game.state.hands_played_per_deck[1] == game.config.max_hands_per_deck

    def test_calculate_round_score(self, game):
        """calculate_round_score should sum all hands played."""
        game.start_game()

        # Play 2 hands
        game.play_hand(deck_index=0, card_indices=[0, 1])  # Some hand
        game.play_hand(deck_index=1, card_indices=[0, 1])  # Some hand

        # Calculate total score
        total_score = game.calculate_round_score()

        # Should be sum of the 2 hands
        assert total_score > 0  # At least High Card (3) per hand = 6+

    def test_get_visible_cards(self, game):
        """Should be able to get visible cards for each deck."""
        game.start_game()

        cards_deck_0 = game.get_visible_cards(deck_index=0)
        cards_deck_1 = game.get_visible_cards(deck_index=1)

        # Config-driven: verify visible cards match config
        assert len(cards_deck_0) == game.config.visible_cards_per_deck
        assert len(cards_deck_1) == game.config.visible_cards_per_deck

    def test_manager_is_logic_only(self, game):
        """RULE 3: Manager is logic only, stores manager refs."""
        assert hasattr(game, 'config')
        assert hasattr(game, 'state')
        assert hasattr(game, 'deck_manager')
        assert hasattr(game, 'token_manager')
        assert hasattr(game, 'scoring_manager')
