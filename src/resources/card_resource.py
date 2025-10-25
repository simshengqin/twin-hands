"""
Card Resource - Godot-ready data structure
Represents a playing card as a custom Resource.
In Godot: extends Resource
"""

from dataclasses import dataclass
from typing import ClassVar, Dict


@dataclass
class CardResource:
    """
    Represents a single playing card.
    In Godot, this would extend Resource with @export vars.

    GDScript equivalent:
    class_name CardResource
    extends Resource

    @export var rank: String
    @export var suit: String
    """

    # Class constants (would be const in Godot)
    SUIT_SYMBOLS: ClassVar[Dict[str, str]] = {
        "H": "♥",
        "D": "♦",
        "C": "♣",
        "S": "♠"
    }

    # ANSI color codes for suits (red for hearts/diamonds, bright white for clubs/spades)
    SUIT_COLORS: ClassVar[Dict[str, str]] = {
        "H": "\033[91m",  # Bright red
        "D": "\033[91m",  # Bright red
        "C": "\033[97m",  # Bright white
        "S": "\033[97m",  # Bright white
    }
    COLOR_RESET: ClassVar[str] = "\033[0m"

    rank: str  # "2"-"9", "T", "J", "Q", "K", "A"
    suit: str  # "H", "D", "C", "S"

    def get_display_string(self, colored: bool = False) -> str:
        """
        Get display string for the card.

        Args:
            colored: If True, apply ANSI color codes to suits

        Returns:
            Formatted card string (e.g., "A♥" or colored version)
        """
        suit_symbol = self.SUIT_SYMBOLS.get(self.suit, self.suit)

        if colored:
            suit_color = self.SUIT_COLORS.get(self.suit, "")
            return f"{self.rank}{suit_color}{suit_symbol}{self.COLOR_RESET}"
        else:
            return f"{self.rank}{suit_symbol}"

    def get_rank_value(self) -> int:
        """Returns numeric value for comparison (from config)."""
        from src.resources.game_config_resource import GameConfigResource
        return GameConfigResource.RANK_VALUES[self.rank]

    def duplicate(self) -> 'CardResource':
        """Create a copy of this card (Resource pattern)."""
        return CardResource(rank=self.rank, suit=self.suit)

    def __str__(self) -> str:
        return self.get_display_string(colored=True)
