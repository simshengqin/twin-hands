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

    # === TOKEN SYSTEM (GDD 4-3) ===
    hand_tokens_per_round: int = 4  # Number of hands you can play
    trade_tokens_per_round: int = 3  # Number of trades you can make
    max_hands_per_deck: int = 2     # Max hands per deck per round

    # === CARD VISIBILITY (GDD 4-4) ===
    max_visible_per_deck: int = 8   # 4 base + 4 from trades

    # === PROGRESSION (GDD 5-2, 5-3) ===
    max_rounds: int = 8             # Maximum number of rounds
    quota_scaling: float = 1.3      # Round quota multiplier (1.3×)

    # === UI/UX ===
    skip_welcome_screen: bool = True  # Skip welcome screen for testing

    # === HAND SCORES (GDD 4-7) ===
    # Class constant - UPPERCASE
    HAND_SCORES = {
        "Royal Flush": 60,
        "Straight Flush": 50,
        "Four of a Kind": 30,
        "Flush": 20,
        "Straight": 18,
        "Three of a Kind": 15,
        "Two Pair": 10,
        "Pair": 6,
        "High Card": 3,
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
