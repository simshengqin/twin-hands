"""
Unit tests for ScoringManager.

Tests hand evaluation and scoring calculation (PHASE A: no Jokers).
"""

import pytest
from src.managers.scoring_manager import ScoringManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource
from src.resources.hand_resource import HandResource


class TestScoringManager:
    """Test ScoringManager in isolation (PHASE A: basic scoring only)."""

    @pytest.fixture
    def setup(self):
        """Create config, state, and manager for testing."""
        config = TwinHandsConfig()
        state = TwinHandsState(config)
        manager = ScoringManager(config, state)
        return config, state, manager

    def test_evaluate_pair(self, setup):
        """GDD 4-7: Pair should score 6 points."""
        config, state, manager = setup

        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="A", suit="diamonds")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "Pair"
        assert hand.base_score == 6  # GDD 4-7

    def test_evaluate_three_of_a_kind(self, setup):
        """GDD 4-7: Three of a Kind should score 15 points."""
        config, state, manager = setup

        cards = [
            CardResource(rank="K", suit="hearts"),
            CardResource(rank="K", suit="diamonds"),
            CardResource(rank="K", suit="clubs")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "Three of a Kind"
        assert hand.base_score == 15

    def test_evaluate_flush_4_cards(self, setup):
        """GDD 4-7: Flush (4 cards same suit) should score 20 points."""
        config, state, manager = setup

        cards = [
            CardResource(rank="2", suit="hearts"),
            CardResource(rank="5", suit="hearts"),
            CardResource(rank="9", suit="hearts"),
            CardResource(rank="K", suit="hearts")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "Flush"
        assert hand.base_score == 20

    def test_2_cards_same_suit_not_flush(self, setup):
        """GDD 4-7: 2 cards same suit should NOT be Flush (requires 4 cards)."""
        config, state, manager = setup

        cards = [
            CardResource(rank="2", suit="hearts"),
            CardResource(rank="5", suit="hearts")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "High Card"  # Not Flush
        assert hand.base_score == 3

    def test_3_cards_same_suit_not_flush(self, setup):
        """GDD 4-7: 3 cards same suit should NOT be Flush (requires 4 cards)."""
        config, state, manager = setup

        cards = [
            CardResource(rank="2", suit="hearts"),
            CardResource(rank="5", suit="hearts"),
            CardResource(rank="9", suit="hearts")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "High Card"  # Not Flush
        assert hand.base_score == 3

    def test_evaluate_high_card(self, setup):
        """GDD 4-7: High Card should score 3 points."""
        config, state, manager = setup

        cards = [
            CardResource(rank="K", suit="hearts")
        ]

        hand = manager.evaluate_hand(cards)
        assert hand.hand_type == "High Card"
        assert hand.base_score == 3

    def test_calculate_total_score_basic(self, setup):
        """PHASE A: Total score is sum of base scores (no Jokers)."""
        config, state, manager = setup

        # Simulate 2 hands played
        hands = [
            HandResource(cards=[], hand_type="Pair", base_score=6),
            HandResource(cards=[], hand_type="Flush", base_score=20)
        ]

        total = manager.calculate_total_score(hands)
        assert total == 26  # 6 + 20

    def test_manager_is_logic_only(self, setup):
        """RULE 3: Manager is logic only, no data storage."""
        config, state, manager = setup

        assert hasattr(manager, 'config')
        assert hasattr(manager, 'state')
        assert not hasattr(manager, 'score')  # This is in state
