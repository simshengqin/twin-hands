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
    Represents a 1-5 card poker hand in Twin Hands (GDD v6.1 4-7).
    Ready for Phase B Joker system (GDD 4-5-3).

    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name HandResource
    extends Resource

    @export var cards: Array[CardResource]
    @export var hand_type: String
    @export var base_score: int
    @export var mult: float
    """

    cards: List['CardResource']  # List of CardResource objects (1-5 cards)
    hand_type: str  # "Pair", "Flush", "High Card", etc. (GDD 4-7)
    base_score: int  # Base score from GDD 4-7 table (chips/points)
    mult: float = 1.0  # Multiplier (starts at 1.0, Jokers modify this - GDD 4-5-3)

    def get_display_string(self) -> str:
        """Get display string for the hand."""
        cards_str = " ".join(str(card) for card in self.cards)
        return f"{self.hand_type} ({self.base_score} pts): {cards_str}"

    def __str__(self) -> str:
        return self.get_display_string()
