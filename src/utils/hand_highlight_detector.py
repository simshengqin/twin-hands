"""
HandHighlightDetector - Detects partial poker hands for UI highlighting.

GDD v6.1 Hand Highlighting System:
- Progressive detection: Check 5-card → 4-card → 3-card, highlight highest match only
- Colors = cards missing: Green (0), Yellow (1), Orange (2)
- Per-deck filters: Players toggle which hand types to highlight
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.resources.card_resource import CardResource


@dataclass
class HighlightMatch:
    """Represents a potential hand match for highlighting."""
    hand_type: str           # "Flush", "Straight", "Pair", etc.
    cards_needed: int        # 0 (green), 1 (yellow), 2 (orange)
    current_cards: int       # How many cards are part of this hand
    total_required: int      # Total cards needed for complete hand
    matching_indices: List[int]  # Indices of cards that match


class HandHighlightDetector:
    """
    Detects partial poker hands for UI highlighting.

    GDD v6.1: Progressive detection (5→4→3), highest match only.
    """

    # Rank values for straight detection
    RANK_VALUES = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "Q": 12, "K": 13, "A": 14
    }

    # Hand types in priority order (check these first)
    HAND_PRIORITIES = [
        "Royal Flush",
        "Straight Flush",
        "Four of a Kind",
        "Flush",
        "Straight",
        "Three of a Kind",
        "Two Pair",
        "Pair"
    ]

    @staticmethod
    def detect_best_highlight(cards: List[CardResource], enabled_filters: List[str]) -> Optional[HighlightMatch]:
        """
        Detect the best partial hand for highlighting.

        GDD v6.1: Check 5-card → 4-card → 3-card, return highest match only.

        Args:
            cards: List of cards to check
            enabled_filters: List of hand types to check (e.g., ["Flush", "Straight"])

        Returns:
            HighlightMatch if found, None otherwise
        """
        if not cards or not enabled_filters:
            return None

        # Progressive detection: 5 → 4 → 3 → 2 cards
        for check_size in [5, 4, 3, 2]:
            # Try each enabled filter in priority order
            for hand_type in HandHighlightDetector.HAND_PRIORITIES:
                if hand_type not in enabled_filters:
                    continue

                match = HandHighlightDetector._check_hand_type(cards, hand_type, check_size)
                if match:
                    return match

        return None

    @staticmethod
    def _check_hand_type(cards: List[CardResource], hand_type: str, check_size: int) -> Optional[HighlightMatch]:
        """
        Check if cards contain a partial hand of given type.

        Args:
            cards: Cards to check
            hand_type: Hand type to check for
            check_size: How many cards to check (3, 4, or 5)

        Returns:
            HighlightMatch if found, None otherwise
        """
        if hand_type == "Flush":
            return HandHighlightDetector._check_flush(cards, check_size)
        elif hand_type == "Straight":
            return HandHighlightDetector._check_straight(cards, check_size)
        elif hand_type == "Four of a Kind":
            return HandHighlightDetector._check_four_of_kind(cards, check_size)
        elif hand_type == "Three of a Kind":
            return HandHighlightDetector._check_three_of_kind(cards, check_size)
        elif hand_type == "Two Pair":
            return HandHighlightDetector._check_two_pair(cards, check_size)
        elif hand_type == "Pair":
            return HandHighlightDetector._check_pair(cards, check_size)

        return None

    @staticmethod
    def _check_flush(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """
        Check for flush (5 same suit).
        GDD v6.1: Flushes require exactly 5 cards.
        """
        if check_size < 3:
            return None

        # Count cards by suit
        suits = {}
        for i, card in enumerate(cards):
            suit = card.suit
            if suit not in suits:
                suits[suit] = []
            suits[suit].append(i)

        # Find best suit
        for suit, indices in suits.items():
            count = len(indices)

            if count >= check_size:
                # Have check_size cards of same suit
                cards_needed = 5 - check_size  # How many more needed for complete flush

                return HighlightMatch(
                    hand_type="Flush",
                    cards_needed=cards_needed,
                    current_cards=check_size,
                    total_required=5,
                    matching_indices=indices[:check_size]  # Take first check_size cards
                )

        return None

    @staticmethod
    def _check_straight(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """
        Check for straight (5 sequential ranks).
        GDD v6.1: Straights require exactly 5 cards.
        """
        if check_size < 3:
            return None

        # Get unique ranks sorted
        rank_values = sorted(set(HandHighlightDetector.RANK_VALUES[card.rank] for card in cards))

        if len(rank_values) < check_size:
            return None

        # Check for sequential runs
        for i in range(len(rank_values) - check_size + 1):
            window = rank_values[i:i + check_size]

            # Check if sequential
            is_sequential = all(window[j+1] == window[j] + 1 for j in range(len(window) - 1))

            if is_sequential:
                # Find card indices that match these ranks
                matching_indices = []
                for idx, card in enumerate(cards):
                    if HandHighlightDetector.RANK_VALUES[card.rank] in window:
                        matching_indices.append(idx)
                        if len(matching_indices) >= check_size:
                            break

                cards_needed = 5 - check_size

                return HighlightMatch(
                    hand_type="Straight",
                    cards_needed=cards_needed,
                    current_cards=check_size,
                    total_required=5,
                    matching_indices=matching_indices[:check_size]
                )

        return None

    @staticmethod
    def _check_four_of_kind(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """Check for four of a kind (4 same rank)."""
        if check_size < 3:
            return None

        # Count by rank
        ranks = {}
        for i, card in enumerate(cards):
            rank = card.rank
            if rank not in ranks:
                ranks[rank] = []
            ranks[rank].append(i)

        for rank, indices in ranks.items():
            count = len(indices)

            if count >= check_size and check_size >= 3:
                cards_needed = 4 - check_size

                return HighlightMatch(
                    hand_type="Four of a Kind",
                    cards_needed=cards_needed,
                    current_cards=check_size,
                    total_required=4,
                    matching_indices=indices[:check_size]
                )

        return None

    @staticmethod
    def _check_three_of_kind(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """Check for three of a kind (3 same rank)."""
        # Three of a Kind requires 3 cards - skip if checking for larger hands
        if check_size > 3:
            return None

        # Count by rank
        ranks = {}
        for i, card in enumerate(cards):
            rank = card.rank
            if rank not in ranks:
                ranks[rank] = []
            ranks[rank].append(i)

        for rank, indices in ranks.items():
            count = len(indices)

            if count >= 3:
                cards_needed = 0  # Already complete

                return HighlightMatch(
                    hand_type="Three of a Kind",
                    cards_needed=cards_needed,
                    current_cards=3,
                    total_required=3,
                    matching_indices=indices[:3]
                )

        return None

    @staticmethod
    def _check_two_pair(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """Check for two pair (2 pairs)."""
        # Two Pair requires 4 cards - skip if checking for larger hands
        if check_size > 4:
            return None

        # Find all pairs
        ranks = {}
        for i, card in enumerate(cards):
            rank = card.rank
            if rank not in ranks:
                ranks[rank] = []
            ranks[rank].append(i)

        pairs = [(rank, indices) for rank, indices in ranks.items() if len(indices) >= 2]

        if len(pairs) >= 2:
            # Have two pair
            matching_indices = []
            matching_indices.extend(pairs[0][1][:2])  # First pair
            matching_indices.extend(pairs[1][1][:2])  # Second pair

            return HighlightMatch(
                hand_type="Two Pair",
                cards_needed=0,  # Already complete
                current_cards=4,
                total_required=4,
                matching_indices=matching_indices
            )

        return None

    @staticmethod
    def _check_pair(cards: List[CardResource], check_size: int) -> Optional[HighlightMatch]:
        """Check for pair (2 same rank)."""
        # Pair requires 2 cards - skip if we're checking for larger hands
        if check_size > 2:
            return None

        # Count by rank
        ranks = {}
        for i, card in enumerate(cards):
            rank = card.rank
            if rank not in ranks:
                ranks[rank] = []
            ranks[rank].append(i)

        for rank, indices in ranks.items():
            count = len(indices)

            if count >= 2:
                return HighlightMatch(
                    hand_type="Pair",
                    cards_needed=0,  # Already complete
                    current_cards=2,
                    total_required=2,
                    matching_indices=indices[:2]
                )

        return None
