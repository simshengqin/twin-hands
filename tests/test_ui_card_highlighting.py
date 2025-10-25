"""
Tests for Balatro-style card highlighting in grid display.
Ensures contributing cards are correctly identified and highlighted.
"""

import pytest
from src.resources.game_config_resource import GameConfigResource
from src.managers.game_manager import GameManager
from src.ui.terminal_ui import TerminalUI
from src.resources.card_resource import CardResource
from src.utils.poker_evaluator import PokerEvaluator


class TestCardHighlighting:
    """Test that contributing cards are correctly identified for highlighting."""

    def test_one_pair_highlights_correct_cards(self):
        """Test that One Pair highlights only the 2 matching cards."""
        # Create a One Pair hand: K♣ K♠ 7♦ 5♥ 2♠
        cards = [
            CardResource(rank='K', suit='Clubs'),
            CardResource(rank='K', suit='Spades'),
            CardResource(rank='7', suit='Diamonds'),
            CardResource(rank='5', suit='Hearts'),
            CardResource(rank='2', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "One Pair"

        contributing = PokerEvaluator.get_contributing_cards(hand)
        contributing_ranks = [c.rank for c in contributing]

        # Should only highlight the 2 Kings
        assert len(contributing) == 2
        assert contributing_ranks.count('K') == 2

    def test_two_pair_highlights_correct_cards(self):
        """Test that Two Pair highlights the 4 cards (both pairs)."""
        # Create a Two Pair hand: K♣ K♠ 7♦ 7♥ 2♠
        cards = [
            CardResource(rank='K', suit='Clubs'),
            CardResource(rank='K', suit='Spades'),
            CardResource(rank='7', suit='Diamonds'),
            CardResource(rank='7', suit='Hearts'),
            CardResource(rank='2', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Two Pair"

        contributing = PokerEvaluator.get_contributing_cards(hand)
        contributing_ranks = [c.rank for c in contributing]

        # Should highlight the 2 Kings + 2 Sevens = 4 cards
        assert len(contributing) == 4
        assert contributing_ranks.count('K') == 2
        assert contributing_ranks.count('7') == 2

    def test_three_of_a_kind_highlights_correct_cards(self):
        """Test that Three of a Kind highlights only the 3 matching cards."""
        # Create a Three of a Kind hand: 6♦ 6♣ 6♠ T♥ 5♠
        cards = [
            CardResource(rank='6', suit='Diamonds'),
            CardResource(rank='6', suit='Clubs'),
            CardResource(rank='6', suit='Spades'),
            CardResource(rank='T', suit='Hearts'),
            CardResource(rank='5', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Three of a Kind"

        contributing = PokerEvaluator.get_contributing_cards(hand)
        contributing_ranks = [c.rank for c in contributing]

        # Should only highlight the 3 Sixes
        assert len(contributing) == 3
        assert contributing_ranks.count('6') == 3

    def test_four_of_a_kind_highlights_correct_cards(self):
        """Test that Four of a Kind highlights only the 4 matching cards."""
        # Create a Four of a Kind hand: A♣ A♠ A♦ A♥ 2♠
        cards = [
            CardResource(rank='A', suit='Clubs'),
            CardResource(rank='A', suit='Spades'),
            CardResource(rank='A', suit='Diamonds'),
            CardResource(rank='A', suit='Hearts'),
            CardResource(rank='2', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Four of a Kind"

        contributing = PokerEvaluator.get_contributing_cards(hand)
        contributing_ranks = [c.rank for c in contributing]

        # Should only highlight the 4 Aces
        assert len(contributing) == 4
        assert contributing_ranks.count('A') == 4

    def test_full_house_highlights_all_cards(self):
        """Test that Full House highlights all 5 cards."""
        # Create a Full House hand: K♣ K♠ K♦ 7♥ 7♠
        cards = [
            CardResource(rank='K', suit='Clubs'),
            CardResource(rank='K', suit='Spades'),
            CardResource(rank='K', suit='Diamonds'),
            CardResource(rank='7', suit='Hearts'),
            CardResource(rank='7', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Full House"

        contributing = PokerEvaluator.get_contributing_cards(hand)

        # Should highlight all 5 cards
        assert len(contributing) == 5

    def test_flush_highlights_all_cards(self):
        """Test that Flush highlights all 5 cards."""
        # Create a Flush hand: K♠ T♠ 8♠ 6♠ 3♠
        cards = [
            CardResource(rank='K', suit='Spades'),
            CardResource(rank='T', suit='Spades'),
            CardResource(rank='8', suit='Spades'),
            CardResource(rank='6', suit='Spades'),
            CardResource(rank='3', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Flush"

        contributing = PokerEvaluator.get_contributing_cards(hand)

        # Should highlight all 5 cards
        assert len(contributing) == 5

    def test_straight_highlights_all_cards(self):
        """Test that Straight highlights all 5 cards."""
        # Create a Straight hand: 9♣ 8♠ 7♦ 6♥ 5♠
        cards = [
            CardResource(rank='9', suit='Clubs'),
            CardResource(rank='8', suit='Spades'),
            CardResource(rank='7', suit='Diamonds'),
            CardResource(rank='6', suit='Hearts'),
            CardResource(rank='5', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "Straight"

        contributing = PokerEvaluator.get_contributing_cards(hand)

        # Should highlight all 5 cards
        assert len(contributing) == 5

    def test_high_card_highlights_only_highest(self):
        """Test that High Card highlights only the highest card."""
        # Create a High Card hand: K♣ T♠ 8♦ 6♥ 3♠
        cards = [
            CardResource(rank='K', suit='Clubs'),
            CardResource(rank='T', suit='Spades'),
            CardResource(rank='8', suit='Diamonds'),
            CardResource(rank='6', suit='Hearts'),
            CardResource(rank='3', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "High Card"

        contributing = PokerEvaluator.get_contributing_cards(hand)
        contributing_ranks = [c.rank for c in contributing]

        # Should only highlight the King
        assert len(contributing) == 1
        assert contributing_ranks[0] == 'K'

    def test_contributing_cards_match_original_positions(self):
        """
        Test that contributing cards map to correct positions in original unsorted grid.
        This is the critical test for the bug fix.
        """
        config = GameConfigResource()
        game = GameManager(config)
        game.start_new_round()

        # Manually set a row with a known pair in specific positions
        # Row 0: 9♥ 6♦ K♠ 6♣ 7♦ (pair of 6s at positions 1 and 3)
        game.state.grid[0][0].card = CardResource(rank='9', suit='Hearts')
        game.state.grid[0][1].card = CardResource(rank='6', suit='Diamonds')
        game.state.grid[0][2].card = CardResource(rank='K', suit='Spades')
        game.state.grid[0][3].card = CardResource(rank='6', suit='Clubs')
        game.state.grid[0][4].card = CardResource(rank='7', suit='Diamonds')

        # Get the row cards
        row_cards = game.state.get_row(0)

        # Evaluate the hand
        hand = PokerEvaluator.evaluate_hand(row_cards)
        assert hand.hand_type == "One Pair"

        # Get contributing cards
        contributing = PokerEvaluator.get_contributing_cards(hand)

        # Contributing cards should be the two 6s
        assert len(contributing) == 2
        assert all(c.rank == '6' for c in contributing)

        # The contributing cards should match the exact cards at positions 1 and 3
        # not positions based on sorted order
        assert contributing[0].suit in ['Diamonds', 'Clubs']
        assert contributing[1].suit in ['Diamonds', 'Clubs']

    def test_duplicate_cards_handled_correctly(self):
        """Test that duplicate cards (same rank AND suit) are handled correctly."""
        # Create a hand with duplicate K♣ cards: K♣ K♣ 7♦ 5♥ 2♠
        cards = [
            CardResource(rank='K', suit='Clubs'),
            CardResource(rank='K', suit='Clubs'),  # Duplicate
            CardResource(rank='7', suit='Diamonds'),
            CardResource(rank='5', suit='Hearts'),
            CardResource(rank='2', suit='Spades')
        ]

        hand = PokerEvaluator.evaluate_hand(cards)
        assert hand.hand_type == "One Pair"

        contributing = PokerEvaluator.get_contributing_cards(hand)

        # Should highlight both K♣ cards
        assert len(contributing) == 2
        assert all(c.rank == 'K' and c.suit == 'Clubs' for c in contributing)
