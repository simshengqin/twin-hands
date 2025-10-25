"""
Poker Evaluator Utility - Godot-ready poker hand evaluation
Static utility class for evaluating poker hands.
In Godot: class with static functions (no extends)
"""

from typing import List
from collections import Counter


class PokerEvaluator:
    """
    Evaluates 5-card poker hands and assigns scores.
    In Godot, this would be a static class or namespace with static funcs.

    GDScript equivalent:
    class_name PokerEvaluator

    static func evaluate_hand(cards: Array[CardResource]) -> HandResource:
        # ...
    """

    @staticmethod
    def evaluate_hand(cards: List['CardResource']) -> 'HandResource':
        """
        Evaluate a 5-card hand and return HandResource with type and chips.
        Uses new flat chip scoring (no per-hand mult).
        """
        from src.resources.hand_resource import HandResource
        from src.resources.game_config_resource import GameConfigResource

        if len(cards) != 5:
            # Invalid hand
            return HandResource(cards=cards, hand_type="Invalid", chips=0, mult=1)

        # Sort cards by value for easier evaluation
        sorted_cards = sorted(cards, key=lambda c: c.get_rank_value(), reverse=True)

        # Check all hand types from best to worst
        if PokerEvaluator._is_five_of_a_kind(sorted_cards):
            hand_type = "Five of a Kind"
        elif PokerEvaluator._is_royal_flush(sorted_cards):
            hand_type = "Royal Flush"
        elif PokerEvaluator._is_straight_flush(sorted_cards):
            hand_type = "Straight Flush"
        elif PokerEvaluator._is_four_of_a_kind(sorted_cards):
            hand_type = "Four of a Kind"
        elif PokerEvaluator._is_full_house(sorted_cards):
            hand_type = "Full House"
        elif PokerEvaluator._is_flush(sorted_cards):
            hand_type = "Flush"
        elif PokerEvaluator._is_straight(sorted_cards):
            hand_type = "Straight"
        elif PokerEvaluator._is_three_of_a_kind(sorted_cards):
            hand_type = "Three of a Kind"
        elif PokerEvaluator._is_two_pair(sorted_cards):
            hand_type = "Two Pair"
        elif PokerEvaluator._is_one_pair(sorted_cards):
            hand_type = "One Pair"
        else:
            hand_type = "High Card"

        # Get flat chips from config (new scoring system)
        chips = GameConfigResource.HAND_SCORES[hand_type]
        # Base mult is always 1 (jokers provide global mult bonuses)
        mult = 1

        return HandResource(cards=sorted_cards, hand_type=hand_type, chips=chips, mult=mult)

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
    def _is_five_of_a_kind(cards: List['CardResource']) -> bool:
        """Check if all five cards have the same rank (possible with replacement)."""
        rank_counts = PokerEvaluator._get_rank_counts(cards)
        return 5 in rank_counts.values()

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

        if hand_type in ["Five of a Kind", "Royal Flush", "Straight Flush",
                         "Full House", "Flush", "Straight"]:
            # All 5 cards contribute
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

        elif hand_type == "One Pair":
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
