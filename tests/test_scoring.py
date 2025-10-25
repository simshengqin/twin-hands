"""
Test poker hand evaluation and scoring
Tests PokerEvaluator and ScoreManager
"""
import pytest
from src.utils.poker_evaluator import PokerEvaluator
from src.resources.card_resource import CardResource
from src.resources.game_config_resource import GameConfigResource


class TestPokerHandDetection:
    """Test poker hand recognition"""

    def test_royal_flush_detection(self, get_card):
        """Royal Flush: A-K-Q-J-T same suit"""
        cards = [
            get_card('A', 'H'),
            get_card('K', 'H'),
            get_card('Q', 'H'),
            get_card('J', 'H'),
            get_card('T', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Royal Flush"
        assert hand.chips == GameConfigResource.HAND_SCORES["Royal Flush"]
        assert hand.mult == 1

    def test_straight_flush_detection(self, get_card):
        """Straight Flush: 5 consecutive cards same suit"""
        cards = [
            get_card('9', 'D'),
            get_card('8', 'D'),
            get_card('7', 'D'),
            get_card('6', 'D'),
            get_card('5', 'D'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Straight Flush"
        assert hand.chips == GameConfigResource.HAND_SCORES["Straight Flush"]
        assert hand.mult == 1

    def test_four_of_a_kind_detection(self, get_card):
        """Four of a Kind: 4 cards same rank"""
        cards = [
            get_card('K', 'H'),
            get_card('K', 'D'),
            get_card('K', 'C'),
            get_card('K', 'S'),
            get_card('2', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Four of a Kind"
        assert hand.chips == GameConfigResource.HAND_SCORES["Four of a Kind"]
        assert hand.mult == 1

    def test_full_house_detection(self, get_card):
        """Full House: 3 of a kind + pair"""
        cards = [
            get_card('Q', 'H'),
            get_card('Q', 'D'),
            get_card('Q', 'C'),
            get_card('3', 'H'),
            get_card('3', 'S'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Full House"
        assert hand.chips == GameConfigResource.HAND_SCORES["Full House"]
        assert hand.mult == 1

    def test_flush_detection(self, get_card):
        """Flush: 5 cards same suit, not consecutive"""
        cards = [
            get_card('A', 'C'),
            get_card('K', 'C'),
            get_card('9', 'C'),
            get_card('5', 'C'),
            get_card('2', 'C'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Flush"
        assert hand.chips == GameConfigResource.HAND_SCORES["Flush"]
        assert hand.mult == 1

    def test_straight_detection(self, get_card):
        """Straight: 5 consecutive cards, mixed suits"""
        cards = [
            get_card('9', 'H'),
            get_card('8', 'D'),
            get_card('7', 'C'),
            get_card('6', 'S'),
            get_card('5', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Straight"
        assert hand.chips == GameConfigResource.HAND_SCORES["Straight"]
        assert hand.mult == 1

    def test_three_of_a_kind_detection(self, get_card):
        """Three of a Kind: 3 cards same rank"""
        cards = [
            get_card('J', 'H'),
            get_card('J', 'D'),
            get_card('J', 'C'),
            get_card('5', 'H'),
            get_card('2', 'S'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Three of a Kind"
        assert hand.chips == GameConfigResource.HAND_SCORES["Three of a Kind"]
        assert hand.mult == 1

    def test_two_pair_detection(self, get_card):
        """Two Pair: 2 different pairs"""
        cards = [
            get_card('T', 'H'),
            get_card('T', 'D'),
            get_card('4', 'C'),
            get_card('4', 'S'),
            get_card('2', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Two Pair"
        assert hand.chips == GameConfigResource.HAND_SCORES["Two Pair"]
        assert hand.mult == 1

    def test_one_pair_detection(self, get_card):
        """One Pair: 2 cards same rank"""
        cards = [
            get_card('A', 'H'),
            get_card('A', 'D'),
            get_card('K', 'C'),
            get_card('9', 'S'),
            get_card('2', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "One Pair"
        assert hand.chips == GameConfigResource.HAND_SCORES["One Pair"]
        assert hand.mult == 1

    def test_high_card_detection(self, get_card):
        """High Card: No poker hand"""
        cards = [
            get_card('A', 'H'),
            get_card('K', 'D'),
            get_card('9', 'C'),
            get_card('5', 'S'),
            get_card('2', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "High Card"
        assert hand.chips == GameConfigResource.HAND_SCORES["High Card"]
        assert hand.mult == 1


class TestPokerHandWithDuplicates:
    """Test poker evaluation with duplicate cards (draw with replacement)"""

    def test_four_of_a_kind_with_duplicate_cards(self, get_card):
        """Four of a kind can have duplicate actual cards"""
        # Same card instance duplicated 4 times
        ace_hearts = get_card('A', 'H')
        cards = [
            ace_hearts,
            ace_hearts.duplicate(),
            ace_hearts.duplicate(),
            ace_hearts.duplicate(),
            get_card('2', 'C'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        # Should still be four of a kind
        assert hand.hand_type == "Four of a Kind"

    def test_pair_from_same_card_duplicated(self, get_card):
        """Pair can be the exact same card drawn twice"""
        king_spades = get_card('K', 'S')
        cards = [
            king_spades,
            king_spades.duplicate(),  # Same card
            get_card('9', 'H'),
            get_card('5', 'D'),
            get_card('2', 'C'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "One Pair"

    def test_flush_impossible_with_same_card(self, get_card):
        """Can't have flush with 5 copies of same card"""
        card = get_card('A', 'H')
        cards = [
            card,
            card.duplicate(),
            card.duplicate(),
            card.duplicate(),
            card.duplicate(),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        # 5 of the same card = Five of a Kind (with replacement)
        assert hand.hand_type == "Five of a Kind"


class TestEdgeCases:
    """Test edge cases in poker evaluation"""

    def test_ace_low_straight(self, get_card):
        """Ace can be low in straight (A-2-3-4-5)"""
        cards = [
            get_card('A', 'H'),
            get_card('2', 'D'),
            get_card('3', 'C'),
            get_card('4', 'S'),
            get_card('5', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Straight"

    def test_ace_low_straight_flush(self, get_card):
        """Ace-low straight flush"""
        cards = [
            get_card('A', 'H'),
            get_card('2', 'H'),
            get_card('3', 'H'),
            get_card('4', 'H'),
            get_card('5', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        assert hand.hand_type == "Straight Flush"

    def test_cards_sorted_in_hand(self, get_card):
        """Returned hand has cards sorted by rank"""
        cards = [
            get_card('2', 'H'),
            get_card('A', 'D'),
            get_card('5', 'C'),
            get_card('K', 'S'),
            get_card('9', 'H'),
        ]

        hand = PokerEvaluator.evaluate_hand(cards)

        # Should be sorted by rank value (descending)
        assert hand.cards[0].rank == 'A'
        assert hand.cards[1].rank == 'K'
        assert hand.cards[2].rank == '9'
        assert hand.cards[3].rank == '5'
        assert hand.cards[4].rank == '2'


class TestScoreManager:
    """Test ScoreManager functionality"""

    def test_score_empty_grid_returns_zero(self, started_game):
        """Scoring empty grid returns 0"""
        game = started_game

        # Clear all cards
        for row in range(5):
            for col in range(5):
                game.state.grid[row][col].card = None

        current_score, row_hands, col_hands, _ = game.score_manager.score_current_grid()

        assert current_score == 0
        assert len(row_hands) == 0
        assert len(col_hands) == 0

    def test_score_full_grid_evaluates_all_lines(self, started_game):
        """Scoring full grid evaluates 5 rows + 5 columns"""
        game = started_game

        current_score, row_hands, col_hands, _ = game.score_manager.score_current_grid()

        assert len(row_hands) == 5
        assert len(col_hands) == 5
        assert current_score >= 0  # Could be 0 if all high cards

    def test_score_and_update_adds_to_cumulative(self, started_game):
        """score_and_update() adds to cumulative score"""
        game = started_game
        initial_cumulative = game.state.cumulative_score

        current_score, row_hands, col_hands, _ = game.score_manager.score_and_update()

        assert game.state.cumulative_score == initial_cumulative + current_score
        assert current_score in game.state.spin_scores

    def test_multiple_scores_accumulate(self, started_game):
        """Multiple scorings accumulate"""
        game = started_game

        score1, _, _, _ = game.score_manager.score_and_update()
        score2, _, _, _ = game.score_manager.score_and_update()

        assert game.state.cumulative_score == score1 + score2
        assert len(game.state.spin_scores) == 2


class TestScoringIntegration:
    """Test scoring integration with game flow"""

    def test_play_spin_then_score(self, started_game):
        """Can play spin and score"""
        game = started_game

        # Play a spin
        success = game.play_spin()
        assert success == True

        # Score it
        current_score, row_hands, col_hands, _ = game.score_manager.score_and_update()

        assert current_score >= 0
        assert game.state.cumulative_score == current_score

    def test_frozen_cards_affect_scoring(self, started_game):
        """Frozen cards persist and affect score"""
        game = started_game

        # Freeze a good card
        game.state.freeze_cell(0, 0)
        frozen_card = game.state.grid[0][0].card

        # Play another spin
        game.play_spin()

        # Frozen card still there
        assert game.state.grid[0][0].card is frozen_card

        # Can still score
        current_score, row_hands, col_hands, _ = game.score_manager.score_and_update()
        assert current_score >= 0


class TestHandScoring:
    """Test individual hand scoring values"""

    def test_hand_scores_are_flat_chips(self):
        """Hand scores are flat chip values (integers)"""
        config = GameConfigResource()

        for hand_type, chips in config.HAND_SCORES.items():
            assert isinstance(chips, int), f"{hand_type} chips not int"
            assert chips > 0, f"{hand_type} must have positive chips"

    def test_five_of_a_kind_highest_score(self):
        """Five of a Kind has highest chip value (rarest hand)"""
        config = GameConfigResource()
        scores = config.HAND_SCORES

        five_kind_score = scores["Five of a Kind"]

        for hand_type, chips in scores.items():
            if hand_type != "Five of a Kind":
                assert five_kind_score > chips, f"Five of a Kind ({five_kind_score}) should score higher than {hand_type} ({chips})"

    def test_high_card_lowest_score(self):
        """High Card has lowest chip value"""
        config = GameConfigResource()
        scores = config.HAND_SCORES

        high_card_score = scores["High Card"]

        for hand_type, chips in scores.items():
            if hand_type != "High Card":
                assert high_card_score <= chips, f"High Card ({high_card_score}) should score lower than or equal to {hand_type} ({chips})"
