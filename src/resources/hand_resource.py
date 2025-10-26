"""
Hand Resource - Godot-ready poker hand representation
Represents a 1-4 card poker hand in Twin Hands.
In Godot: extends Resource
"""

from dataclasses import dataclass
from typing import List


@dataclass
class HandResource:
    """
    Represents a 1-4 card poker hand in Twin Hands (GDD 4-7).
    PHASE A: Only base_score (no Joker mult yet)

    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name HandResource
    extends Resource

    @export var cards: Array[CardResource]
    @export var hand_type: String
    @export var base_score: int
    """

    cards: List['CardResource']  # List of CardResource objects (1-4 cards)
    hand_type: str  # "Pair", "Flush", "High Card", etc. (GDD 4-7)
    base_score: int  # Base score from GDD 4-7 table

    def get_display_string(self) -> str:
        """Get display string for the hand."""
        cards_str = " ".join(str(card) for card in self.cards)
        return f"{self.hand_type} ({self.base_score} pts): {cards_str}"

    def __str__(self) -> str:
        return self.get_display_string()
