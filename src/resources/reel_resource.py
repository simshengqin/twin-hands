"""
Reel Resource - Godot-ready reel representation
Represents a single column reel (52-card deck with no replacement).
In Godot: extends Resource
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ReelResource:
    """
    Represents a single column reel (52-card deck with no replacement).
    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name ReelResource
    extends Resource

    signal cards_changed
    signal card_drawn

    @export var col_index: int
    var deck: Array[CardResource]
    var drawn_indices: Array[int]
    """

    col_index: int
    deck: List['CardResource'] = field(default_factory=list)
    drawn_indices: List[int] = field(default_factory=list)

    # Callbacks for signals (in Godot, these would be signals)
    _on_card_drawn_callback: Optional[callable] = field(default=None, repr=False)

    def reset(self, new_deck: List['CardResource']) -> None:
        """Reset the reel with a fresh shuffled deck."""
        self.deck = new_deck
        self.drawn_indices = []

    def draw(self) -> Optional['CardResource']:
        """Draw the next card from this reel and emit signal."""
        if len(self.drawn_indices) >= len(self.deck):
            return None  # Deck exhausted

        next_index = len(self.drawn_indices)
        card = self.deck[next_index]
        self.drawn_indices.append(next_index)

        self._emit_card_drawn(card)
        return card

    def cards_remaining(self) -> int:
        """Return number of cards left in this reel."""
        return len(self.deck) - len(self.drawn_indices)

    def _emit_card_drawn(self, card: 'CardResource') -> None:
        """Emit card_drawn signal (callback in Python)."""
        if self._on_card_drawn_callback:
            self._on_card_drawn_callback(card)

    def connect_card_drawn(self, callback: callable) -> None:
        """Connect to the card_drawn signal."""
        self._on_card_drawn_callback = callback

    def duplicate(self) -> 'ReelResource':
        """Create a copy of this reel (Resource pattern)."""
        from src.resources.card_resource import CardResource
        return ReelResource(
            col_index=self.col_index,
            deck=[card.duplicate() for card in self.deck],
            drawn_indices=self.drawn_indices.copy()
        )
