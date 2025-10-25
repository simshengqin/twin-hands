"""
Events Autoload - Godot-ready global event bus
Central event system using signal pattern.
In Godot: extends Node (autoload singleton)
"""

from typing import Dict, List, Callable


class Events:
    """
    Global event bus for game-wide signals.
    In Godot, this would be an autoload Node with signals.

    GDScript equivalent:
    extends Node

    # Grid-related events
    signal cell_frozen(row: int, col: int)
    signal cell_unfrozen(row: int, col: int)
    signal grid_updated

    # Hand-related events
    signal hand_started
    signal hand_completed
    signal cards_dealt

    # Score-related events
    signal score_updated(current_score: int, cumulative_score: int)
    signal poker_hand_scored(hand: HandResource, is_row: bool, index: int)

    # Round-related events
    signal round_started(round_number: int)
    signal round_completed(round_number: int, final_score: int)

    # Game-related events
    signal game_started
    signal game_won(final_score: int)
    signal game_lost(final_score: int)

    # UI-related events
    signal freeze_limit_reached
    signal hand_limit_reached

    # Reroll-related events (GDD v1.1)
    signal columns_rerolled(column_indices: List[int], cost: int)
    signal spin_completed(spins_taken: int, total_spins: int)
    signal reroll_tokens_updated(tokens_left: int)
    """

    # Event callbacks storage
    _callbacks: Dict[str, List[Callable]] = {}

    # Grid-related events
    @classmethod
    def emit_cell_frozen(cls, row: int, col: int) -> None:
        """Emit cell_frozen signal."""
        cls._emit("cell_frozen", row, col)

    @classmethod
    def emit_cell_unfrozen(cls, row: int, col: int) -> None:
        """Emit cell_unfrozen signal."""
        cls._emit("cell_unfrozen", row, col)

    @classmethod
    def emit_grid_updated(cls) -> None:
        """Emit grid_updated signal."""
        cls._emit("grid_updated")

    # Hand-related events
    @classmethod
    def emit_hand_started(cls) -> None:
        """Emit hand_started signal."""
        cls._emit("hand_started")

    @classmethod
    def emit_hand_completed(cls) -> None:
        """Emit hand_completed signal."""
        cls._emit("hand_completed")

    @classmethod
    def emit_cards_dealt(cls) -> None:
        """Emit cards_dealt signal."""
        cls._emit("cards_dealt")

    # Score-related events
    @classmethod
    def emit_score_updated(cls, current_score: int, cumulative_score: int) -> None:
        """Emit score_updated signal."""
        cls._emit("score_updated", current_score, cumulative_score)

    @classmethod
    def emit_poker_hand_scored(cls, hand: 'HandResource', is_row: bool, index: int) -> None:
        """Emit poker_hand_scored signal."""
        cls._emit("poker_hand_scored", hand, is_row, index)

    # Round-related events
    @classmethod
    def emit_round_started(cls, round_number: int) -> None:
        """Emit round_started signal."""
        cls._emit("round_started", round_number)

    @classmethod
    def emit_round_completed(cls, round_number: int, final_score: int) -> None:
        """Emit round_completed signal."""
        cls._emit("round_completed", round_number, final_score)

    # Game-related events
    @classmethod
    def emit_game_started(cls) -> None:
        """Emit game_started signal."""
        cls._emit("game_started")

    @classmethod
    def emit_game_won(cls, final_score: int) -> None:
        """Emit game_won signal."""
        cls._emit("game_won", final_score)

    @classmethod
    def emit_game_lost(cls, final_score: int) -> None:
        """Emit game_lost signal."""
        cls._emit("game_lost", final_score)

    # UI-related events
    @classmethod
    def emit_freeze_limit_reached(cls) -> None:
        """Emit freeze_limit_reached signal."""
        cls._emit("freeze_limit_reached")

    @classmethod
    def emit_hand_limit_reached(cls) -> None:
        """Emit hand_limit_reached signal."""
        cls._emit("hand_limit_reached")

    # Reroll-related events (GDD v1.1)
    @classmethod
    def emit_columns_rerolled(cls, column_indices: List[int], cost: int) -> None:
        """Emit columns_rerolled signal."""
        cls._emit("columns_rerolled", column_indices, cost)

    @classmethod
    def emit_spin_completed(cls, spins_taken: int, total_spins: int) -> None:
        """Emit spin_completed signal."""
        cls._emit("spin_completed", spins_taken, total_spins)

    @classmethod
    def emit_reroll_tokens_updated(cls, tokens_left: int) -> None:
        """Emit reroll_tokens_updated signal."""
        cls._emit("reroll_tokens_updated", tokens_left)

    # Core signal system
    @classmethod
    def connect(cls, signal_name: str, callback: Callable) -> None:
        """
        Connect a callback to a signal.
        In Godot: Events.signal_name.connect(callback)
        """
        if signal_name not in cls._callbacks:
            cls._callbacks[signal_name] = []
        cls._callbacks[signal_name].append(callback)

    @classmethod
    def disconnect(cls, signal_name: str, callback: Callable) -> None:
        """
        Disconnect a callback from a signal.
        In Godot: Events.signal_name.disconnect(callback)
        """
        if signal_name in cls._callbacks:
            cls._callbacks[signal_name].remove(callback)

    @classmethod
    def _emit(cls, signal_name: str, *args) -> None:
        """
        Emit a signal with arguments.
        In Godot: Events.signal_name.emit(args...)
        """
        if signal_name in cls._callbacks:
            for callback in cls._callbacks[signal_name]:
                callback(*args)

    @classmethod
    def clear_all_connections(cls) -> None:
        """Clear all signal connections (useful for cleanup/testing)."""
        cls._callbacks.clear()
