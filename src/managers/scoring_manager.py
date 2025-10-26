"""
ScoringManager - Logic for hand evaluation and scoring.
In Godot: extends Node
"""

from typing import List
from collections import Counter
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource
from src.resources.hand_resource import HandResource


class ScoringManager:
    """
    Manages hand evaluation and scoring (PHASE A: basic scoring, no Jokers).
    Logic only - all data stored in state.

    In Godot: extends Node
    """

    def __init__(self, config: TwinHandsConfig, state: TwinHandsState):
        """
        Initialize manager with config and state.

        Args:
            config: Game configuration (immutable)
            state: Game state (mutable)
        """
        self.config = config
        self.state = state

    def evaluate_hand(self, cards: List[CardResource]) -> HandResource:
        """
        Evaluate a 1-4 card poker hand (GDD 4-7).

        Args:
            cards: List of 1-4 CardResource objects

        Returns:
            HandResource with hand_type and base_score
        """
        num_cards = len(cards)

        if num_cards < 1 or num_cards > 4:
            # Invalid hand
            return HandResource(cards=cards, hand_type="Invalid", base_score=0)

        # Get hand type and base score
        hand_type = self._determine_hand_type(cards)
        base_score = self.config.HAND_SCORES.get(hand_type, 0)

        return HandResource(cards=cards, hand_type=hand_type, base_score=base_score)

    def _determine_hand_type(self, cards: List[CardResource]) -> str:
        """
        Determine poker hand type for 1-4 cards (GDD 4-7).

        Args:
            cards: List of 1-4 cards

        Returns:
            Hand type string (e.g., "Pair", "Flush", etc.)
        """
        num_cards = len(cards)

        # Count ranks and suits
        ranks = [card.rank for card in cards]
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)
        suit_counts = Counter(suits)

        # Check for same suit (Flush potential)
        is_flush = len(suit_counts) == 1

        # Check for sequential ranks (Straight potential)
        is_straight = self._is_sequential(cards)

        # 4-card hands
        if num_cards == 4:
            # Four of a Kind
            if max(rank_counts.values()) == 4:
                return "Four of a Kind"

            # Royal Flush (A-K-Q-J same suit)
            if is_flush and is_straight and self._is_royal(cards):
                return "Royal Flush"

            # Straight Flush
            if is_flush and is_straight:
                return "Straight Flush"

            # Flush
            if is_flush:
                return "Flush"

            # Straight
            if is_straight:
                return "Straight"

            # Two Pair
            if list(rank_counts.values()).count(2) == 2:
                return "Two Pair"

            # Pair
            if max(rank_counts.values()) == 2:
                return "Pair"

            # High Card
            return "High Card"

        # 3-card hands
        if num_cards == 3:
            # Three of a Kind
            if max(rank_counts.values()) == 3:
                return "Three of a Kind"

            # Straight Flush
            if is_flush and is_straight:
                return "Straight Flush"

            # Flush
            if is_flush:
                return "Flush"

            # Straight
            if is_straight:
                return "Straight"

            # Pair
            if max(rank_counts.values()) == 2:
                return "Pair"

            # High Card
            return "High Card"

        # 2-card hands
        if num_cards == 2:
            # Pair
            if max(rank_counts.values()) == 2:
                return "Pair"

            # Flush (2 cards same suit)
            if is_flush:
                return "Flush"

            # Straight (2 sequential cards)
            if is_straight:
                return "Straight"

            # High Card
            return "High Card"

        # 1-card hand
        return "High Card"

    def _is_sequential(self, cards: List[CardResource]) -> bool:
        """Check if cards form a sequential straight."""
        if len(cards) < 2:
            return False

        # Define rank order (A can be high or low)
        rank_order = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

        # Get rank indices
        indices = []
        for card in cards:
            # Get all possible indices for this rank (A appears twice)
            card_indices = [i for i, r in enumerate(rank_order) if r == card.rank]
            indices.append(card_indices)

        # Try to find a sequential pattern
        # For now, simple check: sort by first occurrence
        first_indices = [idx_list[0] for idx_list in indices]
        sorted_indices = sorted(first_indices)

        # Check if consecutive
        for i in range(len(sorted_indices) - 1):
            if sorted_indices[i + 1] - sorted_indices[i] != 1:
                return False

        return True

    def _is_royal(self, cards: List[CardResource]) -> bool:
        """Check if cards are A-K-Q-J (Royal Flush)."""
        if len(cards) != 4:
            return False

        ranks = set(card.rank for card in cards)
        return ranks == {"A", "K", "Q", "J"}

    def calculate_total_score(self, hands: List[HandResource]) -> int:
        """
        Calculate total score from all hands (PHASE A: simple sum).

        Args:
            hands: List of HandResource objects

        Returns:
            Total score (sum of base_scores)
        """
        return sum(hand.base_score for hand in hands)
