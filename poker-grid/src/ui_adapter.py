"""
UI Adapter - Bridge between terminal UI and game manager
In Godot, this would be replaced by actual UI scenes.
This adapter allows the existing terminal UI to work with the new architecture.
"""

from typing import Tuple, List
from src.managers.game_manager import GameManager
from src.resources.hand_resource import HandResource


class UIAdapter:
    """
    Adapter to make the new GameManager work with the old terminal UI.
    In Godot, this wouldn't exist - UI would connect directly to signals.
    """

    def __init__(self, game_manager: GameManager):
        self.game = game_manager

    # Delegate all methods to the game manager
    @property
    def state(self):
        """Access game state."""
        return self.game.state

    @property
    def config(self):
        """Access game config."""
        return self.game.config

    def start_new_round(self) -> None:
        """Start a new round."""
        self.game.start_new_round()

    def play_spin(self) -> bool:
        """Play a spin (deal new grid)."""
        return self.game.play_spin()

    def toggle_freeze(self, row: int, col: int) -> Tuple[bool, str]:
        """Toggle freeze on a cell."""
        return self.game.toggle_freeze(row, col)

    def unfreeze_all(self) -> None:
        """Unfreeze all cells."""
        self.game.unfreeze_all()

    def auto_refreeze_if_better(self) -> None:
        """Auto-refreeze if better combination available."""
        self.game.auto_refreeze_if_better()

    def reroll_columns(self, column_indices: List[int]) -> Tuple[bool, str]:
        """Reroll specific columns (GDD v1.1). Returns (success, message)."""
        return self.game.reroll_columns(column_indices)

    def complete_spin(self) -> None:
        """Complete a spin (GDD v1.1)."""
        self.game.complete_spin()

    def is_spins_complete(self) -> bool:
        """Check if all spins are used (GDD v1.1)."""
        return self.game.is_spins_complete()

    def score_and_update(self) -> Tuple[int, List[HandResource], List[HandResource], List[dict]]:
        """Score the grid and update state. Returns (score, row_hands, col_hands, top_lines)."""
        return self.game.score_and_update()

    def is_quota_met(self) -> bool:
        """Check if quota is met."""
        return self.game.is_quota_met()

    def is_session_complete(self) -> bool:
        """Check if all rounds are complete."""
        return self.game.is_session_complete()

    def get_session_result(self) -> str:
        """Get session result (WIN/LOSE)."""
        return self.game.get_session_result()
