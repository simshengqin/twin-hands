"""
TokenManager - Logic for token spending and validation.
In Godot: extends Node
"""

from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TokenManager:
    """
    Manages token spending and validation (PHASE A: hand tokens only).
    Logic only - all data stored in state.

    In Godot: extends Node
    """

    def __init__(self, config: TwinHandsConfig, state: TwinHandsState):
        """
        Initialize manager with config and state.

        Args:
            config: Game configuration (immutable)
            state: Game state (mutable)
        """
        self.config = config
        self.state = state

    def can_spend_hand_token(self, deck_index: int) -> bool:
        """
        Check if can spend a hand token for this deck.

        Args:
            deck_index: Which deck wants to play (0-indexed)

        Returns:
            True if can spend, False otherwise

        Checks:
            - Have hand tokens remaining (GDD 4-3: 4 per round)
            - Deck hasn't exceeded max hands (GDD 4-3: max 2 per deck)
        """
        # Check if hand tokens available
        if self.state.hand_tokens <= 0:
            return False

        # Check if deck hasn't hit max hands per deck (GDD 4-3)
        if self.state.hands_played_per_deck[deck_index] >= self.config.max_hands_per_deck:
            return False

        return True

    def spend_hand_token(self, deck_index: int) -> bool:
        """
        Spend a hand token for this deck.

        Args:
            deck_index: Which deck is playing (0-indexed)

        Returns:
            True if spent successfully, False if cannot spend

        Side effects:
            - Decrements state.hand_tokens
            - Increments state.hands_played_per_deck[deck_index]
        """
        # Validate can spend
        if not self.can_spend_hand_token(deck_index):
            return False

        # Spend token
        self.state.hand_tokens -= 1
        self.state.hands_played_per_deck[deck_index] += 1

        return True
