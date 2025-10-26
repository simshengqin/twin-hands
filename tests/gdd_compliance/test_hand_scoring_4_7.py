"""
GDD Compliance Tests for Section 4-7: Poker Hand Scoring.

Verifies game behavior matches GDD specification for hand evaluation and scoring.
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.card_resource import CardResource


class TestGDD_4_7_HandScoring:
    """Test GDD 4-7: Poker Hand Scoring compliance."""

    @pytest.fixture
    def setup(self):
        """Create game manager for testing."""
        config = TwinHandsConfig()
        game = GameManager(config)
        game.start_game()
        return game

    def test_can_play_1_card(self, setup):
        """GDD 4-7: Can play 1 card (minimum)."""
        game = setup

        result = game.play_hand(deck_index=0, card_indices=[0])

        assert result["success"] == True
        assert len(result["hand"].cards) == 1

    def test_can_play_2_cards(self, setup):
        """GDD 4-7: Can play 2 cards."""
        game = setup

        result = game.play_hand(deck_index=0, card_indices=[0, 1])

        assert result["success"] == True
        assert len(result["hand"].cards) == 2

    def test_can_play_3_cards(self, setup):
        """GDD 4-7: Can play 3 cards."""
        game = setup

        result = game.play_hand(deck_index=0, card_indices=[0, 1, 2])

        assert result["success"] == True
        assert len(result["hand"].cards) == 3

    def test_can_play_4_cards(self, setup):
        """GDD 4-7: Can play 4 cards (maximum)."""
        game = setup

        result = game.play_hand(deck_index=0, card_indices=[0, 1, 2, 3])

        assert result["success"] == True
        assert len(result["hand"].cards) == 4

    def test_invalid_hand_returns_0_score(self, setup):
        """GDD 4-7: Invalid hands (5+ cards) should return 0 score."""
        game = setup

        # Manually create an invalid hand with 5 cards
        cards = [CardResource(rank="2", suit="hearts") for _ in range(5)]
        hand = game.scoring_manager.evaluate_hand(cards)

        assert hand.hand_type == "Invalid"
        assert hand.base_score == 0

    # Future tests (from GDD 4-7):
    # - test_royal_flush_scores_60
    # - test_straight_flush_scores_50
    # - test_four_of_a_kind_scores_30
    # - test_flush_scores_20
    # - test_straight_scores_18
    # - test_three_of_a_kind_scores_15
    # - test_two_pair_scores_10
    # - test_pair_scores_6
    # - test_high_card_scores_3
