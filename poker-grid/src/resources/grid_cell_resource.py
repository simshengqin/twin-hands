"""
Grid Cell Resource - Godot-ready cell representation
Represents a single cell in the 5x5 grid.
In Godot: extends Resource with signals
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GridCellResource:
    """
    Represents a single cell in the grid.
    In Godot, this would extend Resource with signals.

    GDScript equivalent:
    class_name GridCellResource
    extends Resource

    signal cell_changed
    signal freeze_changed

    @export var row: int
    @export var col: int
    var card: CardResource
    var is_frozen: bool = false
    """

    row: int
    col: int
    card: Optional['CardResource'] = None
    is_frozen: bool = False

    # Callbacks for signals (in Godot, these would be signals)
    _on_changed_callback: Optional[callable] = field(default=None, repr=False)
    _on_freeze_changed_callback: Optional[callable] = field(default=None, repr=False)

    def set_card(self, card: 'CardResource') -> None:
        """Set the card for this cell and emit signal."""
        self.card = card
        self._emit_changed()

    def freeze(self) -> None:
        """Mark this cell as frozen and emit signal."""
        if not self.is_frozen:
            self.is_frozen = True
            self._emit_freeze_changed()
            self._emit_changed()

    def unfreeze(self) -> None:
        """Unmark this cell as frozen and emit signal."""
        if self.is_frozen:
            self.is_frozen = False
            self._emit_freeze_changed()
            self._emit_changed()

    def _emit_changed(self) -> None:
        """Emit cell_changed signal (callback in Python)."""
        if self._on_changed_callback:
            self._on_changed_callback(self)

    def _emit_freeze_changed(self) -> None:
        """Emit freeze_changed signal (callback in Python)."""
        if self._on_freeze_changed_callback:
            self._on_freeze_changed_callback(self)

    def connect_changed(self, callback: callable) -> None:
        """Connect to the changed signal."""
        self._on_changed_callback = callback

    def connect_freeze_changed(self, callback: callable) -> None:
        """Connect to the freeze_changed signal."""
        self._on_freeze_changed_callback = callback

    def duplicate(self) -> 'GridCellResource':
        """Create a copy of this cell (Resource pattern)."""
        return GridCellResource(
            row=self.row,
            col=self.col,
            card=self.card.duplicate() if self.card else None,
            is_frozen=self.is_frozen
        )
