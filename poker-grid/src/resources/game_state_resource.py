"""
Game State Resource - Godot-ready state management
Main game state container with signals for state changes.
In Godot: extends Resource with multiple signals
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class GameStateResource:
    """
    Main game state container (like a Godot Resource with state).
    In Godot, this would extend Resource with signals.

    GDScript equivalent:
    class_name GameStateResource
    extends Resource

    signal state_changed
    signal hand_completed
    signal round_completed
    signal score_updated(new_score: int)

    var grid: Array[Array]  # 2D array of GridCellResource
    var deck: DeckResource  # Single shared deck (Balatro-style)
    var hands_left: int
    var hands_taken: int
    var frozen_cells: Array[Vector2i]
    var current_round: int
    var cumulative_score: int
    var hand_scores: Array[int]
    var config: GameConfig
    """

    # Grid state
    grid: List[List['GridCellResource']] = field(default_factory=list)
    deck: 'DeckResource' = None

    # Round state
    spins_left: int = 7
    spins_taken: int = 0
    frozen_cells: List[Tuple[int, int]] = field(default_factory=list)

    # Reroll state (new system per GDD v1.1)
    reroll_tokens_left: int = 12  # Shared tokens per quota

    # Session state
    current_round: int = 0
    cumulative_score: int = 0
    spin_scores: List[int] = field(default_factory=list)  # Score for each spin

    # Economy state (supports both money and tokens)
    money: int = 0  # Money system: $1 per unused hand
    tokens: int = 0  # Token system: Fixed rewards per round

    # Config reference
    config: 'GameConfigResource' = None

    # Callbacks for signals (in Godot, these would be signals)
    _on_state_changed_callback: Optional[callable] = field(default=None, repr=False)
    _on_hand_completed_callback: Optional[callable] = field(default=None, repr=False)
    _on_round_completed_callback: Optional[callable] = field(default=None, repr=False)
    _on_score_updated_callback: Optional[callable] = field(default=None, repr=False)

    def reset_round(self) -> None:
        """Reset state for a new round."""
        self.spins_left = self.config.max_spins
        self.spins_taken = 0
        self.frozen_cells = []
        self.spin_scores = []

        # Reset reroll tokens (no carryover per GDD v1.1)
        self.reroll_tokens_left = self.config.reroll_tokens_per_quota

        # Unfreeze all cells
        for row in self.grid:
            for cell in row:
                cell.unfreeze()

        self._emit_state_changed()

    def can_freeze_more(self) -> bool:
        """Check if player can freeze more cells."""
        return len(self.frozen_cells) < self.config.max_freezes

    def freeze_cell(self, row: int, col: int) -> bool:
        """Attempt to freeze a cell. Returns success."""
        if (row, col) in self.frozen_cells:
            return False  # Already frozen

        if not self.can_freeze_more():
            return False  # At max freezes

        self.grid[row][col].freeze()
        self.frozen_cells.append((row, col))
        self._emit_state_changed()
        return True

    def unfreeze_cell(self, row: int, col: int) -> bool:
        """Attempt to unfreeze a cell. Returns success."""
        if (row, col) not in self.frozen_cells:
            return False  # Not frozen

        self.grid[row][col].unfreeze()
        self.frozen_cells.remove((row, col))
        self._emit_state_changed()
        return True

    def unfreeze_all(self) -> None:
        """Unfreeze all cells."""
        for row, col in list(self.frozen_cells):
            self.grid[row][col].unfreeze()
        self.frozen_cells = []
        self._emit_state_changed()

    def get_row(self, row_index: int) -> List['CardResource']:
        """Get all cards in a row."""
        return [cell.card for cell in self.grid[row_index] if cell.card]

    def get_col(self, col_index: int) -> List['CardResource']:
        """Get all cards in a column."""
        return [self.grid[row][col_index].card
                for row in range(self.config.grid_rows)
                if self.grid[row][col_index].card]

    def update_score(self, new_score: int) -> None:
        """Update cumulative score and emit signal."""
        self.cumulative_score += new_score
        self.spin_scores.append(new_score)
        self._emit_score_updated(self.cumulative_score)

    def complete_spin(self) -> None:
        """Mark a spin as completed and emit signal."""
        self.spins_taken += 1
        self.spins_left -= 1
        self._emit_hand_completed()  # Keep event name for compatibility

    def complete_round(self) -> None:
        """Mark a round as completed and emit signal."""
        self._emit_round_completed()

    def add_money(self, amount: int) -> None:
        """Add money to player's balance (old system)."""
        self.money += amount
        self._emit_state_changed()

    def spend_money(self, amount: int) -> bool:
        """
        Attempt to spend money (old system).
        Returns True if successful, False if insufficient funds.
        """
        if self.money >= amount:
            self.money -= amount
            self._emit_state_changed()
            return True
        return False

    def can_afford(self, amount: int) -> bool:
        """Check if player can afford an amount (old system)."""
        return self.money >= amount

    def add_tokens(self, amount: int) -> None:
        """Add tokens to player's balance (new system)."""
        self.tokens += amount
        self._emit_state_changed()

    def spend_tokens(self, amount: int) -> bool:
        """
        Attempt to spend tokens (new system).
        Returns True if successful, False if insufficient funds.
        """
        if self.tokens >= amount:
            self.tokens -= amount
            self._emit_state_changed()
            return True
        return False

    def can_afford_tokens(self, amount: int) -> bool:
        """Check if player can afford tokens (new system)."""
        return self.tokens >= amount

    def spend_reroll_tokens(self, amount: int) -> bool:
        """
        Spend reroll tokens (GDD v1.1 column reroll system).
        Returns True if successful, False if insufficient tokens.
        """
        if self.reroll_tokens_left >= amount:
            self.reroll_tokens_left -= amount
            self._emit_state_changed()
            return True
        return False

    def can_reroll(self, num_columns: int) -> bool:
        """Check if player has enough reroll tokens for N columns."""
        cost = num_columns * self.config.cost_per_column_reroll
        return self.reroll_tokens_left >= cost

    # Signal emission methods
    def _emit_state_changed(self) -> None:
        """Emit state_changed signal."""
        if self._on_state_changed_callback:
            self._on_state_changed_callback()

    def _emit_hand_completed(self) -> None:
        """Emit hand_completed signal."""
        if self._on_hand_completed_callback:
            self._on_hand_completed_callback()

    def _emit_round_completed(self) -> None:
        """Emit round_completed signal."""
        if self._on_round_completed_callback:
            self._on_round_completed_callback()

    def _emit_score_updated(self, score: int) -> None:
        """Emit score_updated signal."""
        if self._on_score_updated_callback:
            self._on_score_updated_callback(score)

    # Signal connection methods
    def connect_state_changed(self, callback: callable) -> None:
        """Connect to the state_changed signal."""
        self._on_state_changed_callback = callback

    def connect_hand_completed(self, callback: callable) -> None:
        """Connect to the hand_completed signal."""
        self._on_hand_completed_callback = callback

    def connect_round_completed(self, callback: callable) -> None:
        """Connect to the round_completed signal."""
        self._on_round_completed_callback = callback

    def connect_score_updated(self, callback: callable) -> None:
        """Connect to the score_updated signal."""
        self._on_score_updated_callback = callback
