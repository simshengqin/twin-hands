"""
Reroll Manager - Column reroll system (GDD v1.1)
Manages the shared token pool and column rerolls.
In Godot: extends Node
"""

from typing import List, Tuple


class RerollManager:
    """
    Manages column reroll logic (GDD v1.1).
    In Godot, this would extend Node.

    GDScript equivalent:
    class_name RerollManager
    extends Node

    var state: GameStateResource
    var config: GameConfigResource
    var grid_manager: GridManager
    """

    def __init__(self, state: 'GameStateResource', config: 'GameConfigResource', grid_manager: 'GridManager'):
        """
        Initialize the reroll manager.

        Args:
            state: Game state resource
            config: Game configuration
            grid_manager: Grid manager for dealing cards
        """
        self.state = state
        self.config = config
        self.grid_manager = grid_manager

    def can_reroll_columns(self, column_indices: List[int]) -> Tuple[bool, str]:
        """
        Check if player can reroll the specified columns.

        Args:
            column_indices: List of column indices to reroll

        Returns:
            (success, message) tuple
        """
        if not column_indices:
            return False, "No columns specified"

        # Check if all indices are valid
        for col in column_indices:
            if not (0 <= col < self.config.grid_cols):
                return False, f"Invalid column index: {col}"

        # Calculate cost
        cost = len(column_indices) * self.config.cost_per_column_reroll

        # Check if player has enough tokens
        if self.state.reroll_tokens_left < cost:
            return False, f"Not enough tokens (need {cost}, have {self.state.reroll_tokens_left})"

        return True, "OK"

    def reroll_columns(self, column_indices: List[int]) -> Tuple[bool, str]:
        """
        Reroll the specified columns by redrawing cards in those columns.

        Args:
            column_indices: List of column indices to reroll (0-indexed)

        Returns:
            (success, message) tuple
        """
        from src.autoload.events import Events

        # Validate
        can_reroll, message = self.can_reroll_columns(column_indices)
        if not can_reroll:
            return False, message

        # Calculate cost
        cost = len(column_indices) * self.config.cost_per_column_reroll

        # Spend tokens
        if not self.state.spend_reroll_tokens(cost):
            return False, "Failed to spend tokens"

        # Reroll each column (only unfrozen cells)
        for col in column_indices:
            self._reroll_column(col)

        # Emit event
        Events.emit_columns_rerolled(column_indices, cost)

        return True, f"Rerolled {len(column_indices)} column(s) for {cost} token(s)"

    def _reroll_column(self, col: int) -> None:
        """
        Reroll a single column by redrawing unfrozen cells.

        Args:
            col: Column index to reroll
        """
        # Redraw each cell in the column (respecting freeze state)
        for row in range(self.config.grid_rows):
            cell = self.state.grid[row][col]

            # Only redraw if not frozen
            if not cell.is_frozen:
                # Draw a new card from the shared deck
                new_card = self.state.deck.draw_random()
                cell.set_card(new_card)

    def get_reroll_cost(self, num_columns: int) -> int:
        """
        Calculate the cost to reroll N columns.

        Args:
            num_columns: Number of columns to reroll

        Returns:
            Token cost
        """
        return num_columns * self.config.cost_per_column_reroll

    def has_tokens_left(self) -> bool:
        """Check if player has any reroll tokens left."""
        return self.state.reroll_tokens_left > 0

    def can_take_more_spins(self) -> bool:
        """Check if player can take more spins this quota."""
        return self.state.spins_taken < self.config.spins_per_quota

    def complete_spin(self) -> None:
        """Mark a spin as completed."""
        from src.autoload.events import Events

        self.state.spins_taken += 1
        Events.emit_spin_completed(self.state.spins_taken, self.config.spins_per_quota)

    def is_quota_complete(self) -> bool:
        """Check if all spins for this quota are used."""
        return self.state.spins_taken >= self.config.spins_per_quota
