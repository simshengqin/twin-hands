"""
Deck Resource - Godot-ready deck representation
Represents ONE of the N split decks in Twin Hands.
In Godot: extends Resource
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random


@dataclass
class DeckResource:
    """
    Represents ONE split deck in Twin Hands (GDD 4-1, 4-2).
    Each deck has visible cards (4) and undrawn cards (22 initially).
    Cards are drawn WITHOUT replacement during a round.

    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name DeckResource
    extends Resource

    signal deck_changed
    signal card_drawn

    @export var visible_cards: Array[CardResource]
    @export var undrawn_cards: Array[CardResource]
    """

    # GDD 4-2: 4 visible cards at a time
    visible_cards: List['CardResource'] = field(default_factory=list)

    # Remaining cards in this deck (drawn from this pile)
    undrawn_cards: List['CardResource'] = field(default_factory=list)

    def total_cards(self) -> int:
        """Return total cards in this deck (visible + undrawn)."""
        return len(self.visible_cards) + len(self.undrawn_cards)
