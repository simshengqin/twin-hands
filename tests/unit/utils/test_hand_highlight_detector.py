"""
Unit tests for HandHighlightDetector.

Tests progressive detection and color logic (GDD v6.1).
"""

import pytest
from src.utils.hand_highlight_detector import HandHighlightDetector, HighlightMatch
from src.resources.card_resource import CardResource


class TestHandHighlightDetector:
    """Test hand highlighting detection."""

    def test_detect_flush_3_of_5(self):
        """Detect 3 cards of same suit (need 2 more for flush)."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="K", suit="hearts"),
            CardResource(rank="Q", suit="hearts"),
            CardResource(rank="5", suit="spades"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush"])

        assert match is not None
        assert match.hand_type == "Flush"
        assert match.cards_needed == 2  # Orange (need 2 more)
        assert match.current_cards == 3
        assert match.total_required == 5

    def test_detect_flush_4_of_5(self):
        """Detect 4 cards of same suit (need 1 more for flush)."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="K", suit="hearts"),
            CardResource(rank="Q", suit="hearts"),
            CardResource(rank="J", suit="hearts"),
            CardResource(rank="5", suit="spades"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush"])

        assert match is not None
        assert match.hand_type == "Flush"
        assert match.cards_needed == 1  # Yellow (need 1 more)
        assert match.current_cards == 4

    def test_detect_flush_complete(self):
        """Detect complete flush (5 cards same suit)."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="K", suit="hearts"),
            CardResource(rank="Q", suit="hearts"),
            CardResource(rank="J", suit="hearts"),
            CardResource(rank="10", suit="hearts"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush"])

        assert match is not None
        assert match.hand_type == "Flush"
        assert match.cards_needed == 0  # Green (complete!)
        assert match.current_cards == 5

    def test_detect_straight_3_of_5(self):
        """Detect 3 sequential cards (need 2 more for straight)."""
        cards = [
            CardResource(rank="5", suit="hearts"),
            CardResource(rank="6", suit="spades"),
            CardResource(rank="7", suit="clubs"),
            CardResource(rank="A", suit="diamonds"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Straight"])

        assert match is not None
        assert match.hand_type == "Straight"
        assert match.cards_needed == 2  # Orange

    def test_detect_pair(self):
        """Detect complete pair."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="A", suit="spades"),
            CardResource(rank="K", suit="clubs"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Pair"])

        assert match is not None
        assert match.hand_type == "Pair"
        assert match.cards_needed == 0  # Green (complete)
        assert len(match.matching_indices) == 2

    def test_progressive_detection_prioritizes_higher_hands(self):
        """Progressive detection: Should find flush before pair."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="A", suit="spades"),
            CardResource(rank="K", suit="hearts"),
            CardResource(rank="Q", suit="hearts"),
            CardResource(rank="J", suit="hearts"),
        ]

        # Both Flush and Pair enabled, should prioritize Flush
        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush", "Pair"])

        assert match is not None
        assert match.hand_type == "Flush"  # Prioritized over Pair
        assert match.cards_needed == 1  # Need 1 more for flush

    def test_no_match_when_filter_disabled(self):
        """Should return None if hand type not in enabled filters."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="A", suit="spades"),
        ]

        # Pair exists but filter not enabled
        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush"])

        assert match is None

    def test_no_match_when_insufficient_cards(self):
        """Should return None if not enough cards for any hand."""
        cards = [
            CardResource(rank="A", suit="hearts"),
            CardResource(rank="K", suit="spades"),
        ]

        match = HandHighlightDetector.detect_best_highlight(cards, ["Flush", "Straight"])

        assert match is None
