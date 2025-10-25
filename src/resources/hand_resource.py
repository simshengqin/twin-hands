"""
Hand Resource - Godot-ready poker hand representation
Represents a 5-card poker hand with its evaluation.
In Godot: extends Resource
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class HandResource:
    """
    Represents a 5-card poker hand with its evaluation.
    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name HandResource
    extends Resource

    @export var cards: Array[CardResource]
    @export var hand_type: String
    @export var chips: int
    @export var mult: int
    """

    cards: List['CardResource']  # List of CardResource objects
    hand_type: str  # "Royal Flush", "Straight Flush", etc.
    chips: int
    mult: int  # Base multiplier for this hand
    # Whether this line was counted toward the hand total (set by ScoreManager)
    counted: bool = field(default=False, repr=False)

    def get_score(self) -> int:
        """Calculate score: chips × mult"""
        return self.chips * self.mult

    def get_display_string(self) -> str:
        """Get display string for the hand."""
        cards_str = " ".join(str(card) for card in self.cards)
        score = self.get_score()
        return f"{self.hand_type} ({self.chips} × {self.mult} = {score}): {cards_str}"

    def duplicate(self) -> 'HandResource':
        """Create a copy of this hand (Resource pattern)."""
        from src.resources.card_resource import CardResource
        return HandResource(
            cards=[card.duplicate() for card in self.cards],
            hand_type=self.hand_type,
            chips=self.chips,
            mult=self.mult
        )

    def __str__(self) -> str:
        return self.get_display_string()
