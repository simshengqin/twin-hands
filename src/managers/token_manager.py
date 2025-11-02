"""
TokenManager - Logic for token spending and validation (GDD v6.1).
In Godot: extends Node
"""

from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState


class TokenManager:
    """
    Manages token spending and validation (GDD v6.1).
    Logic only - all data stored in state.

    GDD v6.1 Token System:
    - Hand tokens: UNLIMITED (no tracking, but max 2 hands per deck enforced)
    - Discard tokens: 3 per round
    - Trade tokens: 2 per round

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

    # === HAND PLAYING (GDD v6.1: Unlimited, but max 2 per deck) ===

    def can_play_hand(self, deck_index: int) -> bool:
        """
        Check if can play a hand from this deck.
        GDD v6.1: Hand tokens unlimited, but max 2 hands per deck enforced.

        Args:
            deck_index: Which deck wants to play (0-indexed)

        Returns:
            True if can play, False otherwise

        Checks:
            - Deck hasn't exceeded max hands per deck (GDD v6.1: max 2)
        """
        # Check if deck hasn't hit max hands per deck (GDD v6.1 4-3)
        if self.state.hands_played_per_deck[deck_index] >= self.config.max_hands_per_deck:
            return False

        return True

    def record_hand_played(self, deck_index: int) -> bool:
        """
        Record that a hand was played from this deck.
        GDD v6.1: No token spending, just tracking for max 2 per deck.

        Args:
            deck_index: Which deck played (0-indexed)

        Returns:
            True if recorded successfully, False if cannot play

        Side effects:
            - Increments state.hands_played_per_deck[deck_index]
        """
        # Validate can play
        if not self.can_play_hand(deck_index):
            return False

        # Record hand played
        self.state.hands_played_per_deck[deck_index] += 1

        return True

    # === DISCARD TOKENS (GDD v6.1: 3 per round) ===

    def can_discard(self) -> bool:
        """
        Check if can discard cards.
        GDD v6.1: 3 discard tokens per round.

        Returns:
            True if discard tokens available, False otherwise
        """
        return self.state.discard_tokens > 0

    def spend_discard_token(self) -> bool:
        """
        Spend a discard token.
        GDD v6.1 4-3: 3 discard tokens per round.

        Returns:
            True if spent successfully, False if no tokens available

        Side effects:
            - Decrements state.discard_tokens
        """
        if not self.can_discard():
            return False

        self.state.discard_tokens -= 1
        return True

    # === TRADE TOKENS (GDD v6.1: 2 per round) ===

    def can_trade(self) -> bool:
        """
        Check if can trade cards.
        GDD v6.1: 2 trade tokens per round.

        Returns:
            True if trade tokens available, False otherwise
        """
        return self.state.trade_tokens > 0

    def spend_trade_token(self) -> bool:
        """
        Spend a trade token.
        GDD v6.1 4-3: 2 trade tokens per round.

        Returns:
            True if spent successfully, False if no tokens available

        Side effects:
            - Decrements state.trade_tokens
        """
        if not self.can_trade():
            return False

        self.state.trade_tokens -= 1
        return True

    # === ROUND MANAGEMENT ===

    def reset_for_new_round(self) -> None:
        """
        Reset tokens and tracking for a new round.
        GDD v6.1: Reset discard/trade tokens, reset hands played tracking.

        Side effects:
            - Resets state.discard_tokens to config value
            - Resets state.trade_tokens to config value
            - Resets state.hands_played_per_deck to [0, 0, ...]
        """
        self.state.discard_tokens = self.config.discard_tokens_per_round
        self.state.trade_tokens = self.config.trade_tokens_per_round
        self.state.hands_played_per_deck = [0] * self.config.num_decks
