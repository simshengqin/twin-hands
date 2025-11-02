"""
Poker Evaluator Utility - Godot-ready poker hand evaluation (Twin Hands v6.1)
Static utility class for evaluating poker hands (1-5 cards).
In Godot: class with static functions (no extends)
"""

from typing import List
from collections import Counter


class PokerEvaluator:
    """
    Evaluates 1-5 card poker hands and assigns scores (GDD v6.1 4-7).

    GDD v6.1 Rules:
    - Flushes/Straights: Require exactly 5 cards
    - Kickers allowed: Four of a Kind (4-5), Three of a Kind (3-5), Two Pair (4-5), Pair (2-5)
    - High Card: 1-5 cards (any cards that don't match a pattern)

    In Godot, this would be a static class or namespace with static funcs.

    GDScript equivalent:
    class_name PokerEvaluator

    static func evaluate_hand(cards: Array[CardResource]) -> HandResource:
        # ...
    """

    @staticmethod
    def evaluate_hand(cards: List['CardResource']) -> 'HandResource':
        """
        Evaluate a 1-5 card hand and return HandResource with type and base score.
        GDD v6.1 4-7: Supports variable-length hands with kickers.

        Args:
            cards: 1-5 cards to evaluate

        Returns:
            HandResource with hand_type and base score from TwinHandsConfig
        """
        from src.resources.hand_resource import HandResource
        from src.resources.twin_hands_config_resource import TwinHandsConfig

        if len(cards) < 1 or len(cards) > 5:
            # Invalid hand
            return HandResource(cards=cards, hand_type="Invalid", base_score=0, mult=1.0)

        # Sort cards by value for easier evaluation
        sorted_cards = sorted(cards, key=lambda c: c.get_rank_value(), reverse=True)
        num_cards = len(sorted_cards)

        # GDD v6.1 4-7: Check hands based on card count and rules
        # Note: Flushes/Straights REQUIRE 5 cards

        if num_cards == 5:
            # 5-card hands: Check all types
            if PokerEvaluator._is_royal_flush(sorted_cards):
                hand_type = "Royal Flush"
            elif PokerEvaluator._is_straight_flush(sorted_cards):
                hand_type = "Straight Flush"
            elif PokerEvaluator._is_four_of_a_kind(sorted_cards):
                hand_type = "Four of a Kind"
            elif PokerEvaluator._is_flush(sorted_cards):
                hand_type = "Flush"
            elif PokerEvaluator._is_straight(sorted_cards):
                hand_type = "Straight"
            elif PokerEvaluator._is_full_house(sorted_cards):
                hand_type = "Full House"  # GDD: 3-of-a-kind + pair
            elif PokerEvaluator._is_three_of_a_kind(sorted_cards):
                hand_type = "Three of a Kind"
            elif PokerEvaluator._is_two_pair(sorted_cards):
                hand_type = "Two Pair"
            elif PokerEvaluator._is_one_pair(sorted_cards):
                hand_type = "Pair"
            else:
                hand_type = "High Card"

        elif num_cards == 4:
            # 4-card hands: No flush/straight (require 5), check pairs/sets
            if PokerEvaluator._is_four_of_a_kind(sorted_cards):
                hand_type = "Four of a Kind"
            elif PokerEvaluator._is_three_of_a_kind(sorted_cards):
                hand_type = "Three of a Kind"
            elif PokerEvaluator._is_two_pair(sorted_cards):
                hand_type = "Two Pair"
            elif PokerEvaluator._is_one_pair(sorted_cards):
                hand_type = "Pair"
            else:
                hand_type = "High Card"

        elif num_cards == 3:
            # 3-card hands: Only three-of-a-kind or pair
            if PokerEvaluator._is_three_of_a_kind(sorted_cards):
                hand_type = "Three of a Kind"
            elif PokerEvaluator._is_one_pair(sorted_cards):
                hand_type = "Pair"
            else:
                hand_type = "High Card"

        elif num_cards == 2:
            # 2-card hands: Only pair
            if PokerEvaluator._is_one_pair(sorted_cards):
                hand_type = "Pair"
            else:
                hand_type = "High Card"

        else:  # num_cards == 1
            # 1-card hand: Always High Card
            hand_type = "High Card"

        # Get base score from TwinHandsConfig (GDD v6.1 4-7)
        base_score = TwinHandsConfig.HAND_SCORES[hand_type]
        # Base mult is always 1.0 (Jokers will modify this in Phase B - GDD 4-5-3)
        mult = 1.0

        return HandResource(cards=sorted_cards, hand_type=hand_type, base_score=base_score, mult=mult)

    # Helper methods for hand detection

    @staticmethod
    def _get_rank_counts(cards: List['CardResource']) -> Counter:
        """Get count of each rank in the hand."""
        return Counter(card.rank for card in cards)

    @staticmethod
    def _is_flush(cards: List['CardResource']) -> bool:
        """Check if all cards are the same suit."""
        suits = set(card.suit for card in cards)
        return len(suits) == 1

    @staticmethod
    def _is_straight(cards: List['CardResource']) -> bool:
        """Check if cards form a straight."""
        values = sorted([card.get_rank_value() for card in cards])

        # Check normal straight
        if values == list(range(values[0], values[0] + 5)):
            return True

        # Check wheel straight (A-2-3-4-5)
        if values == [2, 3, 4, 5, 14]:
            return True

        return False

    @staticmethod
    def _is_royal_flush(cards: List['CardResource']) -> bool:
        """Check if hand is a royal flush (10-J-Q-K-A of same suit)."""
        if not PokerEvaluator._is_flush(cards):
            return False

        ranks = set(card.rank for card in cards)
        return ranks == {"T", "J", "Q", "K", "A"}

    @staticmethod
    def _is_straight_flush(cards: List['CardResource']) -> bool:
        """Check if hand is a straight flush (not royal)."""
        if PokerEvaluator._is_royal_flush(cards):
            return False
        return PokerEvaluator._is_flush(cards) and PokerEvaluator._is_straight(cards)


    @staticmethod
    def _is_four_of_a_kind(cards: List['CardResource']) -> bool:
        """Check if hand has four of a kind."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        return 4 in rank_counts.values()

    @staticmethod
    def _is_full_house(cards: List['CardResource']) -> bool:
        """Check if hand is a full house (3 of a kind + pair)."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        counts = sorted(rank_counts.values())
        return counts == [2, 3]

    @staticmethod
    def _is_three_of_a_kind(cards: List['CardResource']) -> bool:
        """Check if hand has three of a kind (but not full house)."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        return 3 in rank_counts.values() and not PokerEvaluator._is_full_house(cards)

    @staticmethod
    def _is_two_pair(cards: List['CardResource']) -> bool:
        """Check if hand has two pairs."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        pairs = [count for count in rank_counts.values() if count == 2]
        return len(pairs) == 2

    @staticmethod
    def _is_one_pair(cards: List['CardResource']) -> bool:
        """Check if hand has exactly one pair."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        return 2 in rank_counts.values() and not PokerEvaluator._is_two_pair(cards)

    @staticmethod
    def get_contributing_cards(hand_resource: 'HandResource') -> List['CardResource']:
        """
        Get the list of cards that contribute to the hand's scoring.
        Like Balatro, only returns the cards that matter for the hand type.

        Examples:
        - Three of a Kind: Returns the 3 matching cards
        - Two Pair: Returns the 4 cards (2 pairs)
        - Full House: Returns all 5 cards
        - Straight/Flush: Returns all 5 cards
        - High Card: Returns only the highest card

        Args:
            hand_resource: The evaluated hand

        Returns:
            List of cards that contribute to scoring
        """
        cards = hand_resource.cards
        hand_type = hand_resource.hand_type

        if hand_type in ["Royal Flush", "Straight Flush", "Full House", "Flush", "Straight"]:
            # All cards contribute (5-card hands only)
            return cards

        elif hand_type == "Four of a Kind":
            # Return the 4 matching cards
            rank_counts = PokerEvaluator._get_rank_counts(cards)
            target_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
            return [c for c in cards if c.rank == target_rank]

        elif hand_type == "Three of a Kind":
            # Return the 3 matching cards
            rank_counts = PokerEvaluator._get_rank_counts(cards)
            target_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            return [c for c in cards if c.rank == target_rank]

        elif hand_type == "Two Pair":
            # Return the 4 cards (both pairs)
            rank_counts = PokerEvaluator._get_rank_counts(cards)
            pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]
            return [c for c in cards if c.rank in pair_ranks]

        elif hand_type == "Pair":
            # Return the 2 matching cards
            rank_counts = PokerEvaluator._get_rank_counts(cards)
            target_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            return [c for c in cards if c.rank == target_rank]

        elif hand_type == "High Card":
            # Return only the highest card
            return [cards[0]] if cards else []

        else:
            # Invalid or unknown hand type
            return []
