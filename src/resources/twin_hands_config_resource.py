"""
TwinHandsConfig resource.
Stores all game configuration values from GDD.

In Godot: extends Resource with @export variables
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class TwinHandsConfig:
    """
    Game configuration resource.
    All values match GDD specifications.

    In Godot: extends Resource
    """

    # === DECK CONFIGURATION ===
    # RULE 6: Multiplayer-ready - configurable deck count
    num_decks: int = 2  # GDD specifies 2, but configurable for future modes

    # === TOKEN SYSTEM (GDD v6.1 4-3) ===
    # GDD v6.1: Hand tokens unlimited, discard and trade tokens limited
    discard_tokens_per_round: int = 3  # Number of discards (NEW in v6.1)
    trade_tokens_per_round: int = 2    # Number of trades (was 3 in v6.0)
    max_hands_per_deck: int = 2        # Max hands per deck per round
    # Note: No min_hands_per_deck - if quota hit early, round ends immediately

    # === CARD VISIBILITY (GDD v6.1 4-2) ===
    visible_cards_per_deck: int = 7    # Base visible cards (up from 4 in v6.0)

    # === PROGRESSION (GDD 5-2, 5-3) ===
    max_rounds: int = 8             # Maximum number of rounds
    quota_scaling: float = 1.3      # Round quota multiplier (1.3×)

    # === UI/UX ===
    skip_welcome_screen: bool = True  # Skip welcome screen for testing

    # === RANK VALUES (for comparison/sorting) ===
    # Class constant - UPPERCASE
    RANK_VALUES = {
        "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
        "J": 11, "Q": 12, "K": 13, "A": 14
    }

    # === HAND SCORES (GDD v6.1 4-7) ===
    # Class constant - UPPERCASE
    # GDD v6.1: Flushes and straights now require 5 cards (was 4 in v6.0)
    HAND_SCORES = {
        "Royal Flush": 60,        # A-K-Q-J-10 same suit (5 cards)
        "Straight Flush": 50,     # 5 sequential same suit
        "Four of a Kind": 30,     # 4 same rank + optional kicker
        "Flush": 20,              # 5 same suit
        "Straight": 18,           # 5 sequential
        "Three of a Kind": 15,    # 3 same rank + optional kickers
        "Two Pair": 10,           # 2 pairs + optional kicker
        "Pair": 6,                # 2 same rank + optional kickers
        "High Card": 3,           # No pattern (1-5 cards)
    }

    @property
    def round_quotas(self) -> List[int]:
        """
        Calculate round quotas based on quota_scaling.
        GDD 5-3: Starts at 300, multiplies by 1.3× each round.

        Returns:
            List of quota targets for each round (length = max_rounds)
        """
        quotas = []
        current_quota = 300  # GDD 5-3: Starting quota

        for _ in range(self.max_rounds):
            quotas.append(round(current_quota))
            current_quota *= self.quota_scaling

        return quotas
