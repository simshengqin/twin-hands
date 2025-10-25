"""
Test Joker System - Comprehensive tests for joker mechanics.

These tests focus on game logic, NOT specific joker values.
Tests remain valid even if joker CSV values change.
"""

import pytest
from src.managers.joker_manager import JokerManager
from src.managers.score_manager import ScoreManager
from src.resources.joker_resource import JokerResource
from src.resources.game_state_resource import GameStateResource
from src.resources.game_config_resource import GameConfigResource
from src.resources.card_resource import CardResource
from src.utils.poker_evaluator import PokerEvaluator


class TestJokerManager:
    """Test JokerManager core functionality."""

    def test_joker_manager_initializes_empty(self):
        """Joker manager should start with no jokers."""
        manager = JokerManager(max_slots=5)
        assert manager.get_joker_count() == 0
        assert manager.has_empty_slot() is True

    def test_add_joker_increases_count(self):
        """Adding a joker should increase count."""
        manager = JokerManager(max_slots=5)
        joker = JokerResource(
            id="test_001",
            name="Test Joker",
            rarity="Common",
            cost=5,
            effect_type="instant",
            trigger="always",
            condition_type="",
            condition_value="",
            bonus_type="+m",
            bonus_value=10,
            per_card=False
        )

        success = manager.add_joker(joker)
        assert success is True
        assert manager.get_joker_count() == 1

    def test_cannot_exceed_max_slots(self):
        """Cannot add more jokers than max slots."""
        manager = JokerManager(max_slots=2)

        joker1 = JokerResource(
            id="test_001", name="Joker 1", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=5, per_card=False
        )
        joker2 = JokerResource(
            id="test_002", name="Joker 2", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=5, per_card=False
        )
        joker3 = JokerResource(
            id="test_003", name="Joker 3", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=5, per_card=False
        )

        assert manager.add_joker(joker1) is True
        assert manager.add_joker(joker2) is True
        assert manager.add_joker(joker3) is False  # Should fail
        assert manager.get_joker_count() == 2

    def test_remove_joker_decreases_count(self):
        """Removing a joker should decrease count."""
        manager = JokerManager(max_slots=5)
        joker = JokerResource(
            id="test_001", name="Test Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=10, per_card=False
        )

        manager.add_joker(joker)
        assert manager.get_joker_count() == 1

        removed = manager.remove_joker(0)
        assert removed is not None
        assert manager.get_joker_count() == 0

    def test_has_empty_slot_accuracy(self):
        """has_empty_slot should accurately reflect available space."""
        manager = JokerManager(max_slots=2)
        joker = JokerResource(
            id="test_001", name="Test Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=10, per_card=False
        )

        assert manager.has_empty_slot() is True
        manager.add_joker(joker)
        assert manager.has_empty_slot() is True
        manager.add_joker(joker.duplicate())
        assert manager.has_empty_slot() is False


class TestJokerEffectApplication:
    """Test joker effect logic (without hardcoding specific values)."""

    def test_always_active_joker_applies_to_all_hands(self):
        """Always-active jokers should apply to every hand."""
        manager = JokerManager(max_slots=5)

        # Create an always-active +mult joker
        joker = JokerResource(
            id="test_001", name="Always Active", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=50, per_card=False
        )
        manager.add_joker(joker)

        # Test with any hand
        cards = [
            CardResource("A", "Spade"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade"),
            CardResource("T", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards)

        base_chips = hand.chips
        base_mult = hand.mult

        final_chips, final_mult = manager.apply_joker_effects(hand, cards, base_chips, base_mult)

        # Mult should have increased by joker's bonus
        assert final_mult == base_mult + 50
        assert final_chips == base_chips  # Chips unchanged

    def test_conditional_joker_only_applies_when_condition_met(self):
        """Conditional jokers should only apply when their condition is met."""
        manager = JokerManager(max_slots=5)

        # Create a joker that only triggers on Pairs
        joker = JokerResource(
            id="test_002", name="Pair Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="on_scored", condition_type="hand_type",
            condition_value="One Pair", bonus_type="+m", bonus_value=20, per_card=False
        )
        manager.add_joker(joker)

        # Test with a Pair - should apply
        pair_cards = [
            CardResource("A", "Spade"),
            CardResource("A", "Heart"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade")
        ]
        pair_hand = PokerEvaluator.evaluate_hand(pair_cards)
        assert pair_hand.hand_type == "One Pair"

        chips, mult = manager.apply_joker_effects(pair_hand, pair_cards, pair_hand.chips, pair_hand.mult)
        assert mult == pair_hand.mult + 20  # Joker applied

        # Test with High Card - should NOT apply
        high_card_cards = [
            CardResource("A", "Spade"),
            CardResource("K", "Heart"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade"),
            CardResource("9", "Spade")
        ]
        high_hand = PokerEvaluator.evaluate_hand(high_card_cards)
        assert high_hand.hand_type == "High Card"

        chips, mult = manager.apply_joker_effects(high_hand, high_card_cards, high_hand.chips, high_hand.mult)
        assert mult == high_hand.mult  # Joker did NOT apply

    def test_per_card_joker_scales_with_matching_cards(self):
        """Per-card jokers should multiply effect by number of matching cards."""
        manager = JokerManager(max_slots=5)

        # Create a per-card suit joker (e.g., +5 mult per Diamond)
        joker = JokerResource(
            id="test_003", name="Diamond Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="on_scored", condition_type="suit",
            condition_value="Diamond", bonus_type="+m", bonus_value=5, per_card=True
        )
        manager.add_joker(joker)

        # Test with 3 Diamonds
        cards_3_diamonds = [
            CardResource("A", "Diamond"),
            CardResource("K", "Diamond"),
            CardResource("Q", "Diamond"),
            CardResource("J", "Spade"),
            CardResource("T", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards_3_diamonds)

        chips, mult = manager.apply_joker_effects(hand, cards_3_diamonds, hand.chips, hand.mult)
        assert mult == hand.mult + (5 * 3)  # +5 per Diamond, 3 Diamonds = +15

        # Test with 5 Diamonds
        cards_5_diamonds = [
            CardResource("A", "Diamond"),
            CardResource("K", "Diamond"),
            CardResource("Q", "Diamond"),
            CardResource("J", "Diamond"),
            CardResource("T", "Diamond")
        ]
        hand2 = PokerEvaluator.evaluate_hand(cards_5_diamonds)

        chips2, mult2 = manager.apply_joker_effects(hand2, cards_5_diamonds, hand2.chips, hand2.mult)
        assert mult2 == hand2.mult + (5 * 5)  # +5 per Diamond, 5 Diamonds = +25

    def test_growing_joker_accumulates_value(self):
        """Growing jokers should accumulate bonus over time."""
        manager = JokerManager(max_slots=5)

        # Create a growing joker that gains +10 mult per Straight
        joker = JokerResource(
            id="test_004", name="Growing Joker", rarity="Common", cost=5,
            effect_type="growing", trigger="on_scored", condition_type="hand_type",
            condition_value="Straight", bonus_type="+m", bonus_value=10,
            per_card=False, grow_per="line"
        )
        manager.add_joker(joker)

        # Initial state: joker has 0 accumulated bonus
        assert joker.current_bonus == 0

        # Score a Straight
        straight_cards = [
            CardResource("5", "Spade"),
            CardResource("4", "Heart"),
            CardResource("3", "Diamond"),
            CardResource("2", "Club"),
            CardResource("A", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(straight_cards)
        assert hand.hand_type == "Straight"

        # Apply joker effects
        chips, mult = manager.apply_joker_effects(hand, straight_cards, hand.chips, hand.mult)

        # Joker should have grown
        assert joker.current_bonus == 10

        # Score another Straight
        chips2, mult2 = manager.apply_joker_effects(hand, straight_cards, hand.chips, hand.mult)

        # Joker should have grown again
        assert joker.current_bonus == 20

    def test_multiply_joker_multiplies_mult(self):
        """Xm jokers should multiply the mult value, not add."""
        manager = JokerManager(max_slots=5)

        # Create a ×2 mult joker
        joker = JokerResource(
            id="test_005", name="Multiply Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="Xm", bonus_value=2, per_card=False
        )
        manager.add_joker(joker)

        # Test with any hand that has base mult > 1
        cards = [
            CardResource("A", "Spade"),
            CardResource("A", "Heart"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards)
        base_mult = hand.mult

        chips, mult = manager.apply_joker_effects(hand, cards, hand.chips, base_mult)

        # Mult should be multiplied, not added
        assert mult == base_mult * 2


class TestMultipleJokersStacking:
    """Test multiple jokers working together."""

    def test_multiple_always_active_jokers_stack(self):
        """Multiple always-active jokers should stack additively."""
        manager = JokerManager(max_slots=5)

        # Add 3 always-active +mult jokers
        for i in range(3):
            joker = JokerResource(
                id=f"test_00{i}", name=f"Joker {i}", rarity="Common", cost=5,
                effect_type="instant", trigger="always", condition_type="",
                condition_value="", bonus_type="+m", bonus_value=10, per_card=False
            )
            manager.add_joker(joker)

        # Test with any hand
        cards = [
            CardResource("A", "Spade"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade"),
            CardResource("T", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards)

        chips, mult = manager.apply_joker_effects(hand, cards, hand.chips, hand.mult)

        # All 3 jokers should apply: +10 + +10 + +10 = +30
        assert mult == hand.mult + 30

    def test_chip_and_mult_jokers_work_together(self):
        """Chip jokers and mult jokers should both apply."""
        manager = JokerManager(max_slots=5)

        # Add a chip joker
        chip_joker = JokerResource(
            id="test_001", name="Chip Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+c", bonus_value=100, per_card=False
        )
        manager.add_joker(chip_joker)

        # Add a mult joker
        mult_joker = JokerResource(
            id="test_002", name="Mult Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=5, per_card=False
        )
        manager.add_joker(mult_joker)

        # Test with any hand
        cards = [
            CardResource("A", "Spade"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade"),
            CardResource("T", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards)

        chips, mult = manager.apply_joker_effects(hand, cards, hand.chips, hand.mult)

        # Both should apply
        assert chips == hand.chips + 100
        assert mult == hand.mult + 5

    def test_conditional_jokers_stack_when_both_triggered(self):
        """Multiple conditional jokers should stack when all conditions met."""
        manager = JokerManager(max_slots=5)

        # Add two Pair-triggered jokers
        joker1 = JokerResource(
            id="test_001", name="Pair Joker 1", rarity="Common", cost=5,
            effect_type="instant", trigger="on_scored", condition_type="hand_type",
            condition_value="One Pair", bonus_type="+m", bonus_value=10, per_card=False
        )
        joker2 = JokerResource(
            id="test_002", name="Pair Joker 2", rarity="Common", cost=5,
            effect_type="instant", trigger="on_scored", condition_type="hand_type",
            condition_value="One Pair", bonus_type="+m", bonus_value=15, per_card=False
        )
        manager.add_joker(joker1)
        manager.add_joker(joker2)

        # Test with a Pair
        cards = [
            CardResource("A", "Spade"),
            CardResource("A", "Heart"),
            CardResource("K", "Spade"),
            CardResource("Q", "Spade"),
            CardResource("J", "Spade")
        ]
        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "One Pair"

        chips, mult = manager.apply_joker_effects(hand, cards, hand.chips, hand.mult)

        # Both jokers should apply: +10 + +15 = +25
        assert mult == hand.mult + 25


class TestJokerScoringIntegration:
    """Test jokers integrated with full scoring system."""

    def test_score_manager_applies_jokers_to_each_line(self):
        """ScoreManager should apply jokers to each of 10 lines independently."""
        from src.managers.game_manager import GameManager

        config = GameConfigResource()
        game = GameManager(config)
        game.start_new_round()

        # Add joker manager with always-active joker
        joker_manager = JokerManager(max_slots=5)
        joker = JokerResource(
            id="test_001", name="Test Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=5, per_card=False
        )
        joker_manager.add_joker(joker)

        # Connect joker manager to score manager
        game.score_manager.joker_manager = joker_manager

        # Score the grid
        total_score, row_hands, col_hands, _ = game.score_manager.score_current_grid()

        # All hands should have joker-modified values
        # (We can't predict exact scores, but we can verify structure)
        assert len(row_hands) == 5
        assert len(col_hands) == 5
        assert total_score > 0

        # Each hand should have chips and mult values
        for hand in row_hands + col_hands:
            assert hand.chips > 0
            assert hand.mult > 0

    def test_scoring_without_jokers_vs_with_jokers(self):
        """Verify jokers increase scores compared to no jokers."""
        from src.managers.game_manager import GameManager

        config = GameConfigResource()

        # Create game and start round
        game = GameManager(config)
        game.start_new_round()

        # Score WITHOUT jokers
        score_no_jokers, _, _, _ = game.score_manager.score_current_grid()

        # Add joker and score WITH jokers
        joker_manager = JokerManager(max_slots=5)
        joker = JokerResource(
            id="test_001", name="Test Joker", rarity="Common", cost=5,
            effect_type="instant", trigger="always", condition_type="",
            condition_value="", bonus_type="+m", bonus_value=10, per_card=False
        )
        joker_manager.add_joker(joker)

        game.score_manager.joker_manager = joker_manager
        score_with_jokers, _, _, _ = game.score_manager.score_current_grid()

        # Score with jokers should be higher
        assert score_with_jokers > score_no_jokers
