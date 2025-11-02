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
    Represents ONE split deck in Twin Hands (GDD v6.1 4-1, 4-2).

    Deckbuilder Model (GDD v6.1 4-2):
    - draw_pile: Cards not yet drawn (26 at start → decreases)
    - discard_pile: Played/discarded cards (0 at start → increases)
    - visible_cards: Cards in hand (7 at start → can grow to 8-9 via trades)

    When draw_pile is empty during redraw:
    - Shuffle discard_pile → Becomes new draw_pile
    - Continue drawing

    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name DeckResource
    extends Resource

    signal deck_changed
    signal card_drawn
    signal discard_pile_shuffled

    @export var draw_pile: Array[CardResource]
    @export var discard_pile: Array[CardResource]
    @export var visible_cards: Array[CardResource]
    """

    # GDD v6.1 4-2: Deckbuilder model with 3 piles
    draw_pile: List['CardResource'] = field(default_factory=list)      # Cards to be drawn
    discard_pile: List['CardResource'] = field(default_factory=list)   # Played/discarded cards
    visible_cards: List['CardResource'] = field(default_factory=list)  # 7 baseline (can grow to 8-9)

    def total_cards(self) -> int:
        """Return total cards in this deck (all 3 piles)."""
        return len(self.draw_pile) + len(self.discard_pile) + len(self.visible_cards)

    def shuffle_discard_into_draw(self) -> None:
        """
        Shuffle discard pile and move to draw pile.
        GDD v6.1 4-2: Called when draw pile is empty during redraw.

        In Godot: Emits discard_pile_shuffled signal.
        """
        if not self.discard_pile:
            return  # Nothing to shuffle

        random.shuffle(self.discard_pile)
        self.draw_pile = self.discard_pile
        self.discard_pile = []
