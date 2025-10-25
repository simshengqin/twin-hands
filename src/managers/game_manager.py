"""
Game Manager - Godot-ready game controller
Main game logic controller (like a main scene Node in Godot).
In Godot: extends Node
"""

from typing import Tuple, List, Optional


class GameManager:
    """
    Manages the game state and core logic.
    In Godot, this would extend Node and coordinate other systems.

    GDScript equivalent:
    class_name GameManager
    extends Node

    @export var config: GameConfig
    var state: GameStateResource
    var grid_manager: GridManager
    var score_manager: ScoreManager
    """

    def __init__(self, config: 'GameConfigResource' = None, joker_manager: 'JokerManager' = None):
        """
        Initialize the game manager.
        In Godot, this would be _ready() function.

        Args:
            config: Game configuration
            joker_manager: Optional joker manager for applying joker effects
        """
        from src.resources.game_config_resource import GameConfigResource
        from src.resources.game_state_resource import GameStateResource
        from src.resources.grid_cell_resource import GridCellResource
        from src.utils.card_factory import CardFactory
        from src.autoload.events import Events

        self.config = config if config else GameConfigResource()

        # Create initial state
        self.state = self._create_initial_state()

        # Initialize sub-managers
        from src.managers.grid_manager import GridManager
        from src.managers.score_manager import ScoreManager
        from src.managers.reroll_manager import RerollManager

        self.grid_manager = GridManager(self.state, self.config)
        self.score_manager = ScoreManager(self.state, self.config, joker_manager)
        self.reroll_manager = RerollManager(self.state, self.config, self.grid_manager)

    def _create_initial_state(self) -> 'GameStateResource':
        """Create the initial game state."""
        from src.resources.game_state_resource import GameStateResource
        from src.resources.grid_cell_resource import GridCellResource
        from src.utils.card_factory import CardFactory

        # Create empty grid
        grid = []
        for row in range(self.config.grid_rows):
            grid_row = []
            for col in range(self.config.grid_cols):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Create single shared deck (Balatro-style)
        deck = CardFactory.create_deck_resource()

        # Create state
        state = GameStateResource(
            grid=grid,
            deck=deck,
            spins_left=self.config.max_spins,
            spins_taken=0,
            frozen_cells=[],
            current_round=0,
            cumulative_score=0,
            spin_scores=[],
            config=self.config
        )

        return state

    def start_new_round(self) -> None:
        """
        Start a new round: deal initial grid, auto-freeze if enabled.
        Deck persists between rounds (Balatro-style).
        Emits Events.round_started signal.
        """
        from src.autoload.events import Events

        self.state.current_round += 1
        self.state.reset_round()

        # Deal initial 5x5 grid from shared deck
        self.grid_manager.deal_grid()

        # Auto-freeze highest pair if freeze system is enabled
        if self.config.enable_freeze and self.config.auto_freeze_highest_pair:
            self.grid_manager.auto_freeze_highest_pair()

        # Emit event
        Events.emit_round_started(self.state.current_round)

    def play_spin(self) -> bool:
        """
        Play a spin: deal new grid (redeal all cells).
        Returns True if successful, False if no spins left.
        Emits Events.hand_started and Events.hand_completed signals.
        """
        from src.autoload.events import Events

        if self.state.spins_left <= 0:
            Events.emit_hand_limit_reached()
            return False

        Events.emit_hand_started()

        # Deal new grid (all 25 cells)
        self.grid_manager.deal_grid()

        Events.emit_hand_completed()

        return True

    def toggle_freeze(self, row: int, col: int) -> Tuple[bool, str]:
        """
        Toggle freeze on a cell. Returns (success, message).
        Emits Events.cell_frozen or Events.cell_unfrozen signals.
        Only works if freeze system is enabled.
        """
        from src.autoload.events import Events

        # Check if freeze system is enabled
        if not self.config.enable_freeze:
            return False, "Freeze system is disabled"

        # Validate coordinates
        if not (0 <= row < self.config.grid_rows and 0 <= col < self.config.grid_cols):
            return False, "Invalid coordinates"

        cell = self.state.grid[row][col]

        # If already frozen, unfreeze it
        if cell.is_frozen:
            self.state.unfreeze_cell(row, col)
            Events.emit_cell_unfrozen(row, col)
            return True, f"Unfroze cell ({row}, {col})"

        # Try to freeze it
        if self.state.freeze_cell(row, col):
            Events.emit_cell_frozen(row, col)
            return True, f"Froze cell ({row}, {col})"
        else:
            Events.emit_freeze_limit_reached()
            return False, f"Max freezes reached ({self.config.max_freezes})"

    def unfreeze_all(self) -> None:
        """
        Unfreeze all cells.
        Only works if freeze system is enabled.
        Emits Events.grid_updated signal.
        """
        from src.autoload.events import Events

        if not self.config.enable_freeze:
            return

        self.state.unfreeze_all()
        Events.emit_grid_updated()

    def auto_refreeze_if_better(self) -> None:
        """
        Check if there's a better freeze combination and refreeze if so.
        Only runs if freeze system is enabled.
        """
        if not self.config.enable_freeze or not self.config.auto_freeze_highest_pair:
            return

        # Unfreeze current
        self.state.unfreeze_all()

        # Try to freeze best combination
        self.grid_manager.auto_freeze_highest_pair()

    def score_and_update(self) -> Tuple[int, List['HandResource'], List['HandResource'], List[dict]]:
        """
        Score the current grid and update cumulative score.
        Returns (current_score, row_hands, col_hands, top_lines).
        Emits Events.score_updated and Events.hand_scored signals.
        """
        return self.score_manager.score_and_update()

    def is_round_complete(self) -> bool:
        """Check if all spins in the round are complete."""
        return self.state.spins_left <= 0

    def is_session_complete(self) -> bool:
        """Check if all rounds are complete."""
        return self.state.current_round >= self.config.rounds_per_session

    def is_quota_met(self) -> bool:
        """Check if quota target has been reached."""
        return self.state.cumulative_score >= self.config.quota_target

    def get_session_result(self) -> str:
        """
        Get the final session result (WIN/LOSE).
        Emits Events.game_won or Events.game_lost signals.
        """
        from src.autoload.events import Events

        if self.is_quota_met():
            Events.emit_game_won(self.state.cumulative_score)
            return "WIN"
        else:
            Events.emit_game_lost(self.state.cumulative_score)
            return "LOSE"

    def reroll_columns(self, column_indices: List[int]) -> Tuple[bool, str]:
        """
        Reroll specific columns (GDD v1.1 reroll system).

        Args:
            column_indices: List of column indices to reroll (0-4)

        Returns:
            (success, message) tuple
        """
        return self.reroll_manager.reroll_columns(column_indices)

    def complete_spin(self) -> None:
        """
        Complete a spin (GDD v1.1).
        Marks the current spin as complete.
        """
        self.state.complete_spin()  # Update spin counters
        # Note: RerollManager tracks separately via spins_taken

    def is_spins_complete(self) -> bool:
        """Check if all spins for this quota are used (GDD v1.1)."""
        return self.reroll_manager.is_quota_complete()

    def complete_round(self) -> dict:
        """
        Mark the round as complete.
        Awards currency based on config.use_token_system:
        - Token system: Fixed tokens per round + bonus for early completion
        - Money system: $1 per unused spin
        Returns dict with 'currency_type', 'amount', 'bonus', 'early_completion'.
        Emits Events.round_completed signal.
        """
        from src.autoload.events import Events

        # Determine if player completed early (with spins remaining)
        early_completion = self.state.spins_left > 0

        if self.config.use_token_system:
            # Token system: Fixed rewards
            base_tokens = self.config.tokens_per_round
            bonus_tokens = self.config.tokens_for_early_completion if early_completion else 0
            total_tokens = base_tokens + bonus_tokens

            self.state.add_tokens(total_tokens)

            result = {
                'currency_type': 'tokens',
                'amount': base_tokens,
                'bonus': bonus_tokens,
                'total': total_tokens,
                'early_completion': early_completion
            }
        else:
            # Money system: $1 per unused spin
            money_earned = self.state.spins_left
            if money_earned > 0:
                self.state.add_money(money_earned)

            result = {
                'currency_type': 'money',
                'amount': money_earned,
                'bonus': 0,
                'total': money_earned,
                'early_completion': early_completion
            }

        Events.emit_round_completed(self.state.current_round, self.state.cumulative_score)
        self.state.complete_round()

        return result
