"""
TwinHandsState resource.
Stores current game state (data only, no logic).

In Godot: extends Resource
"""
from dataclasses import dataclass, field
from typing import List, Optional
from src.resources.deck_resource import DeckResource
from src.resources.twin_hands_config_resource import TwinHandsConfig


@dataclass
class TwinHandsState:
    """
    Game state resource (PHASE A: minimal version).
    Stores all mutable game state. Data only, no logic.

    In Godot: extends Resource with @export variables
    """

    # Reference to config (immutable)
    config: TwinHandsConfig

    # === DECK STATE (GDD 4-1) ===
    # RULE 6: Generic N decks (not left/right)
    decks: List[Optional[DeckResource]] = field(default_factory=list)

    # === SCORING STATE (GDD 4-7) ===
    scores: List[int] = field(default_factory=list)  # Per-deck scores

    # === TOKEN STATE (GDD v6.1 4-3) ===
    # GDD v6.1: Hand tokens unlimited (no tracking), discard + trade tokens limited
    discard_tokens: int = 0  # NEW in v6.1
    trade_tokens: int = 0

    # === ROUND STATE (GDD 5-3) ===
    current_round: int = 1  # Rounds start at 1, not 0

    # === PLAY TRACKING (GDD 4-3: max 2 hands per deck) ===
    hands_played_per_deck: List[int] = field(default_factory=list)

    def __post_init__(self):
        """
        Initialize state based on config.
        Called automatically after __init__.
        """
        num_decks = self.config.num_decks

        # Initialize deck list (None until DeckManager populates)
        self.decks = [None] * num_decks

        # Initialize per-deck tracking
        self.scores = [0] * num_decks
        self.hands_played_per_deck = [0] * num_decks

        # Initialize tokens from config (GDD v6.1)
        self.discard_tokens = self.config.discard_tokens_per_round
        self.trade_tokens = self.config.trade_tokens_per_round
