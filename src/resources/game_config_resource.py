"""
Game Config Resource - Godot-ready configuration
All game parameters stored as a Resource.
In Godot: extends Resource with @export properties
"""

from dataclasses import dataclass
from typing import ClassVar, Dict, List


@dataclass
class GameConfigResource:
    """
    Configuration resource for the game.
    In Godot, this would extend Resource with all parameters as @export vars.

    GDScript equivalent:
    class_name GameConfig
    extends Resource

    @export_group("Grid Settings")
    @export var grid_rows: int = 5
    @export var grid_cols: int = 5

    @export_group("Hand System")
    @export var max_hands: int = 7
    @export var max_freezes: int = 2
    ...
    """

    # Class constants (const in Godot)
    SUITS: ClassVar[List[str]] = ["H", "D", "C", "S"]
    # Full 52-card deck (standard poker ranks)
    RANKS: ClassVar[List[str]] = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
    RANK_VALUES: ClassVar[Dict[str, int]] = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
    }
    # Flat chip scoring system (simplified from Balatro)
    # Each hand type has a flat chip value (no mult per hand)
    # Multipliers come from jokers globally
    HAND_SCORES: ClassVar[Dict[str, int]] = {
        "Five of a Kind": 160,    # Rarest (1 in 7.3M with replacement)
        "Royal Flush": 150,        # T-J-Q-K-A of same suit
        "Straight Flush": 110,     # Any straight + flush
        "Four of a Kind": 90,      # 4 of same rank
        "Full House": 70,          # 3 of a kind + pair
        "Flush": 55,               # All same suit
        "Straight": 45,            # Sequential ranks (wrap-around allowed)
        "Three of a Kind": 30,     # 3 of same rank
        "Two Pair": 20,            # 2 different pairs
        "One Pair": 10,            # 2 of same rank
        "High Card": 3             # No matching cards
    }

    # Grid settings
    grid_rows: int = 5
    grid_cols: int = 5

    # Spin system (5 spins per quota)
    max_spins: int = 5  # Number of spins per quota
    max_freezes: int = 2
    # Number of lines scored per spin (top-k out of rows+cols)
    lines_scored_per_spin: int = 3

    # Freeze system toggle
    enable_freeze: bool = False  # Set to False to disable freeze mechanic entirely

    # Auto-freeze settings (only applies if enable_freeze is True)
    auto_freeze_highest_pair: bool = True

    # Deck configuration
    cards_per_deck: int = 52

    # Session configuration
    rounds_per_session: int = 8
    quota_target: int = 2400  # Total quota (for backwards compatibility)

    # Token economy (Cloverpit's Charm style)
    use_token_system: bool = True  # True = tokens, False = money ($1 per unused hand)
    tokens_per_round: int = 3  # Fixed tokens awarded for meeting round quota
    tokens_for_early_completion: int = 2  # Bonus tokens if quota met before using all hands

    # Reroll system (GDD v1.1)
    reroll_tokens_per_quota: int = 8  # Shared token pool per quota (adjusted for 5 spins)
    cost_per_column_reroll: int = 1  # Cost to reroll one column
    spins_per_quota: int = 5  # Number of spins per quota

    # Per-round quotas (cumulative) - based on simulation data
    # Balanced for flat chip scoring without jokers (baseline)
    # With jokers, these become easier (expected progression)
    round_quotas: List[int] = None

    def __post_init__(self):
        """Initialize mutable defaults after dataclass init."""
        if self.round_quotas is None:
            # Adjusted for 5 spins (approximately 5/7 of original 7-spin quotas)
            self.round_quotas = [
                300,   # Round 1: ~286 scaled to 300
                600,   # Round 2: ~593
                920,   # Round 3: ~918
                1260,  # Round 4: ~1254
                1605,  # Round 5: ~1600
                1960,  # Round 6: ~1957
                2330,  # Round 7: ~2325
                2710   # Round 8: ~2703 (final challenge)
            ]

    # Future toggles
    use_global_replacement: bool = False

    def duplicate(self) -> 'GameConfigResource':
        """Create a copy of this config (Resource pattern)."""
        return GameConfigResource(
            grid_rows=self.grid_rows,
            grid_cols=self.grid_cols,
            max_spins=self.max_spins,
            max_freezes=self.max_freezes,
            lines_scored_per_spin=self.lines_scored_per_spin,
            enable_freeze=self.enable_freeze,
            auto_freeze_highest_pair=self.auto_freeze_highest_pair,
            cards_per_deck=self.cards_per_deck,
            rounds_per_session=self.rounds_per_session,
            quota_target=self.quota_target,
            round_quotas=self.round_quotas.copy(),
            use_global_replacement=self.use_global_replacement,
            use_token_system=self.use_token_system,
            tokens_per_round=self.tokens_per_round,
            tokens_for_early_completion=self.tokens_for_early_completion,
            reroll_tokens_per_quota=self.reroll_tokens_per_quota,
            cost_per_column_reroll=self.cost_per_column_reroll,
            spins_per_quota=self.spins_per_quota
        )
