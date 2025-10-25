"""
Deck Resource - Godot-ready deck representation
Represents the player's single persistent deck (Balatro-style).
In Godot: extends Resource
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random


@dataclass
class DeckResource:
    """
    Represents the player's single persistent deck (Balatro-style).
    Cards are drawn WITH replacement - deck always has all cards available.
    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name DeckResource
    extends Resource

    signal deck_changed
    signal card_drawn

    @export var cards: Array[CardResource]
    """

    cards: List['CardResource'] = field(default_factory=list)

    # Callbacks for signals (in Godot, these would be signals)
    _on_deck_changed_callback: Optional[callable] = field(default=None, repr=False)
    _on_card_drawn_callback: Optional[callable] = field(default=None, repr=False)

    def draw_random(self) -> 'CardResource':
        """
        Draw a random card from the deck WITH replacement.
        Returns a duplicate of the card so the deck remains unchanged.
        This allows multiple instances of the same card in the grid.
        """
        if not self.cards:
            raise ValueError("Cannot draw from empty deck")

        card = random.choice(self.cards)
        drawn_card = card.duplicate()

        self._emit_card_drawn(drawn_card)
        return drawn_card

    def add_card(self, card: 'CardResource') -> None:
        """
        Add a card to the deck (for future deck mutation mechanics).
        Emits deck_changed signal.
        """
        self.cards.append(card)
        self._emit_deck_changed()

    def remove_card(self, card: 'CardResource') -> bool:
        """
        Remove a card from the deck (for future deck mutation mechanics).
        Returns True if card was found and removed.
        Emits deck_changed signal.
        """
        try:
            self.cards.remove(card)
            self._emit_deck_changed()
            return True
        except ValueError:
            return False

    def size(self) -> int:
        """Return the number of cards in the deck."""
        return len(self.cards)

    def _emit_deck_changed(self) -> None:
        """Emit deck_changed signal (callback in Python)."""
        if self._on_deck_changed_callback:
            self._on_deck_changed_callback()

    def _emit_card_drawn(self, card: 'CardResource') -> None:
        """Emit card_drawn signal (callback in Python)."""
        if self._on_card_drawn_callback:
            self._on_card_drawn_callback(card)

    def connect_deck_changed(self, callback: callable) -> None:
        """Connect to the deck_changed signal."""
        self._on_deck_changed_callback = callback

    def connect_card_drawn(self, callback: callable) -> None:
        """Connect to the card_drawn signal."""
        self._on_card_drawn_callback = callback

    def duplicate(self) -> 'DeckResource':
        """Create a copy of this deck (Resource pattern)."""
        return DeckResource(
            cards=[card.duplicate() for card in self.cards]
        )
