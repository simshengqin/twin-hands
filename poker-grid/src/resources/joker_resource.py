"""
Joker Resource - Godot-ready joker card representation
Represents a joker with its effects and state.
In Godot: extends Resource
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union


@dataclass
class JokerResource:
    """
    Represents a joker card with its effects.
    In Godot, this would extend Resource.

    GDScript equivalent:
    class_name JokerResource
    extends Resource

    @export var id: String
    @export var name: String
    @export var effect_type: String
    @export var rarity: String
    ...
    """

    # Identity
    id: str  # e.g., "j_001"
    name: str  # e.g., "Joker"
    rarity: str  # Common, Uncommon, Rare, Legendary
    cost: int  # Shop price

    # Effect definition
    effect_type: str  # "instant" or "growing"
    trigger: str  # "always", "on_scored", "on_held", "on_discard"
    condition_type: str  # "", "suit", "rank", "hand_type", "card_type", etc.
    condition_value: str  # e.g., "Diamond", "Pair", "face"
    bonus_type: str  # "+m", "+c", "Xm", "++"
    bonus_value: Union[float, str]  # Numeric value or special format (e.g., "20c4m" for ++)
    per_card: bool  # Apply per card (True) or per line (False)

    # Growing jokers
    grow_per: Optional[str] = None  # "line", "hand", "round"
    current_bonus: float = 0.0  # Accumulated bonus for growing jokers

    # Metadata
    notes: str = ""
    sell_value: Optional[int] = None

    def __post_init__(self):
        """Initialize computed values."""
        if self.sell_value is None:
            # Default sell value is half of cost
            self.sell_value = max(1, self.cost // 2)

    def get_display_name(self) -> str:
        """Get display name with rarity indicator."""
        rarity_symbols = {
            "Common": "",
            "Uncommon": "◆",
            "Rare": "★",
            "Legendary": "♛"
        }
        symbol = rarity_symbols.get(self.rarity, "")
        return f"{symbol} {self.name}".strip()

    def get_description(self) -> str:
        """
        Generate description from joker data.
        Auto-generates based on effect type and conditions.
        """
        # Growing jokers show current value
        if self.effect_type == "growing":
            return self._generate_growing_description()
        else:
            return self._generate_instant_description()

    def _generate_instant_description(self) -> str:
        """Generate description for instant effects."""
        # Always active
        if self.trigger == "always":
            if self.bonus_type == "+m":
                return f"+{int(self.bonus_value)} Mult"
            elif self.bonus_type == "+c":
                return f"+{int(self.bonus_value)} Chips"
            elif self.bonus_type == "Xm":
                return f"×{self.bonus_value} Mult"

        # Conditional effects
        desc_parts = []

        # Bonus description
        if self.bonus_type == "+m":
            # Handle numeric and special formats
            if isinstance(self.bonus_value, str) and 'x' in self.bonus_value.lower():
                desc_parts.append(f"{self.bonus_value} Mult")
            else:
                desc_parts.append(f"+{int(self.bonus_value)} Mult")
        elif self.bonus_type == "+c":
            desc_parts.append(f"+{int(self.bonus_value)} Chips")
        elif self.bonus_type == "Xm":
            desc_parts.append(f"×{self.bonus_value} Mult")
        elif self.bonus_type == "++":
            # Special case: both chips and mult (Scholar, Walkie Talkie)
            values = str(self.bonus_value).split("c")
            chips = values[0]
            mult = values[1].replace("m", "")
            desc_parts.append(f"+{chips} Chips and +{mult} Mult")

        # Per card modifier
        if self.per_card:
            desc_parts.append("per")
        else:
            desc_parts.append("if")

        # Condition description
        if self.condition_type == "suit":
            desc_parts.append(f"{self.condition_value} card")
            if self.per_card:
                desc_parts.append("scored")
        elif self.condition_type == "hand_type":
            desc_parts.append(f"hand is a {self.condition_value}")
        elif self.condition_type == "card_type":
            if self.condition_value == "face":
                desc_parts.append("face card")
                if self.per_card:
                    desc_parts.append("scored")
            elif self.condition_value == "lowest_rank":
                return f"Adds 2× lowest held card rank to Mult"
        elif self.condition_type == "rank":
            ranks = self.condition_value.split("|")
            if len(ranks) > 1:
                desc_parts.append(f"{' or '.join(ranks)}")
            else:
                desc_parts.append(f"{self.condition_value}")
            if self.per_card:
                desc_parts.append("scored")
        elif self.condition_type == "rank_parity":
            desc_parts.append(f"{self.condition_value} rank card")
            if self.per_card:
                desc_parts.append("scored")
        elif self.condition_type == "card_position":
            if self.condition_value == "first_face":
                return "First face card in each line gets ×2 Mult"

        return " ".join(desc_parts)

    def _generate_growing_description(self) -> str:
        """Generate description for growing effects."""
        bonus_str = f"+{int(self.bonus_value)}"
        type_str = "Mult" if self.bonus_type == "+m" else "Chips"
        current_str = int(self.current_bonus)

        if self.condition_type == "hand_type":
            return f"Gains {bonus_str} {type_str} per {self.condition_value} scored (currently +{current_str})"
        else:
            return f"Gains {bonus_str} {type_str} (currently +{current_str})"

    def grow(self, amount: Optional[float] = None) -> None:
        """
        Increase current bonus for growing jokers.
        If amount not specified, uses bonus_value.
        """
        if self.effect_type == "growing":
            growth = amount if amount is not None else self.bonus_value
            self.current_bonus += growth

    def get_effective_bonus(self) -> float:
        """Get the current effective bonus value."""
        if self.effect_type == "growing":
            return self.current_bonus
        else:
            return self.bonus_value

    def duplicate(self) -> 'JokerResource':
        """Create a copy of this joker (Resource pattern)."""
        return JokerResource(
            id=self.id,
            name=self.name,
            rarity=self.rarity,
            cost=self.cost,
            effect_type=self.effect_type,
            trigger=self.trigger,
            condition_type=self.condition_type,
            condition_value=self.condition_value,
            bonus_type=self.bonus_type,
            bonus_value=self.bonus_value,
            per_card=self.per_card,
            grow_per=self.grow_per,
            current_bonus=self.current_bonus,
            notes=self.notes,
            sell_value=self.sell_value
        )

    def __str__(self) -> str:
        return f"{self.get_display_name()}: {self.get_description()}"
