"""
Joker Manager - Godot-ready joker system controller
Manages active jokers and applies their effects to scoring.
In Godot: extends Node
"""

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from src.resources.joker_resource import JokerResource
    from src.resources.hand_resource import HandResource
    from src.resources.card_resource import CardResource


class JokerManager:
    """
    Manages jokers and applies their effects.
    In Godot, this would extend Node and handle joker logic.

    GDScript equivalent:
    class_name JokerManager
    extends Node

    var active_jokers: Array[JokerResource] = []
    var max_joker_slots: int = 5
    """

    def __init__(self, max_slots: int = 5):
        """
        Initialize the joker manager.
        In Godot, this would be _ready() function.
        """
        self.active_jokers: List['JokerResource'] = []
        self.max_slots = max_slots

    def add_joker(self, joker: 'JokerResource') -> bool:
        """
        Add a joker to active slots.
        Returns True if added successfully, False if slots full.
        """
        if len(self.active_jokers) >= self.max_slots:
            return False

        self.active_jokers.append(joker)
        return True

    def remove_joker(self, index: int) -> 'JokerResource':
        """Remove and return joker at index."""
        if 0 <= index < len(self.active_jokers):
            return self.active_jokers.pop(index)
        return None

    def has_empty_slot(self) -> bool:
        """Check if there's room for another joker."""
        return len(self.active_jokers) < self.max_slots

    def get_joker_count(self) -> int:
        """Get number of active jokers."""
        return len(self.active_jokers)

    def apply_joker_effects(
        self,
        hand: 'HandResource',
        cards: List['CardResource'],
        base_chips: int,
        base_mult: int
    ) -> Tuple[int, int]:
        """
        Apply all active joker effects to a scored hand.
        Returns (modified_chips, modified_mult).

        This is called PER LINE (10 times per scoring round).

        Args:
            hand: The evaluated poker hand (HandResource)
            cards: The 5 cards in this line
            base_chips: Base chips from hand type
            base_mult: Base mult from hand type

        Returns:
            (final_chips, final_mult) after all joker effects
        """
        chips = base_chips
        mult = base_mult

        for joker in self.active_jokers:
            # Skip if joker doesn't trigger on scoring
            if joker.trigger != "always" and joker.trigger != "on_scored":
                continue

            # Check if joker condition is met
            if self._check_condition(joker, hand, cards):
                # Apply the effect
                chips, mult = self._apply_effect(joker, hand, cards, chips, mult)

                # Update growing jokers
                if joker.effect_type == "growing" and joker.grow_per == "line":
                    joker.grow()

        return chips, mult

    def _check_condition(
        self,
        joker: 'JokerResource',
        hand: 'HandResource',
        cards: List['CardResource']
    ) -> bool:
        """
        Check if joker's condition is met for this hand.

        Returns True if the joker should trigger.
        """
        # Always active
        if joker.trigger == "always":
            return True

        # Condition-based
        condition_type = joker.condition_type
        condition_value = joker.condition_value

        # No condition specified
        if not condition_type:
            return True

        # Hand type conditions (Pair, Flush, etc.)
        if condition_type == "hand_type":
            return hand.hand_type == condition_value

        # Suit conditions (at least one card of suit)
        if condition_type == "suit":
            return any(card.suit == condition_value for card in cards)

        # Rank conditions
        if condition_type == "rank":
            ranks = condition_value.split("|")
            return any(card.rank in ranks for card in cards)

        # Card type conditions (face cards, etc.)
        if condition_type == "card_type":
            if condition_value == "face":
                return any(card.rank in ['J', 'Q', 'K'] for card in cards)

        # Rank parity (even/odd)
        if condition_type == "rank_parity":
            if condition_value == "even":
                return any(card.rank in ['2', '4', '6', '8', 'T'] for card in cards)
            elif condition_value == "odd":
                return any(card.rank in ['3', '5', '7', '9', 'A'] for card in cards)

        # Card position (first card, etc.)
        if condition_type == "card_position":
            if condition_value == "first_face":
                return any(card.rank in ['J', 'Q', 'K'] for card in cards)

        return False

    def _apply_effect(
        self,
        joker: 'JokerResource',
        hand: 'HandResource',
        cards: List['CardResource'],
        chips: int,
        mult: int
    ) -> Tuple[int, int]:
        """
        Apply joker's effect to chips and mult.

        Returns (modified_chips, modified_mult).
        """
        bonus_value = joker.get_effective_bonus()
        bonus_type = joker.bonus_type

        # Per-card effects
        if joker.per_card:
            count = self._count_matching_cards(joker, cards)

            if bonus_type == "+m":
                mult += int(bonus_value * count)
            elif bonus_type == "+c":
                chips += int(bonus_value * count)

        # Per-line effects (first_only special case)
        elif joker.per_card == "first_only" or not joker.per_card:
            if bonus_type == "+m":
                mult += int(bonus_value)
            elif bonus_type == "+c":
                chips += int(bonus_value)
            elif bonus_type == "Xm":
                mult = int(mult * bonus_value)
            elif bonus_type == "++":
                # Special: both chips and mult (Scholar, Walkie Talkie)
                count = self._count_matching_cards(joker, cards)
                values = str(joker.bonus_value).split("c")
                add_chips = int(values[0]) * count
                add_mult = int(values[1].replace("m", "")) * count
                chips += add_chips
                mult += add_mult

        # Special cases
        if joker.condition_type == "card_position" and joker.condition_value == "first_face":
            # Photograph: First face card gets ×2 mult
            # Find first face card
            for card in cards:
                if card.rank in ['J', 'Q', 'K']:
                    mult = int(mult * bonus_value)
                    break  # Only first face card

        return chips, mult

    def _count_matching_cards(
        self,
        joker: 'JokerResource',
        cards: List['CardResource']
    ) -> int:
        """
        Count how many cards match the joker's condition.
        Used for per-card effects.
        """
        condition_type = joker.condition_type
        condition_value = joker.condition_value

        if condition_type == "suit":
            return sum(1 for card in cards if card.suit == condition_value)

        if condition_type == "rank":
            ranks = condition_value.split("|")
            return sum(1 for card in cards if card.rank in ranks)

        if condition_type == "card_type":
            if condition_value == "face":
                return sum(1 for card in cards if card.rank in ['J', 'Q', 'K'])

        if condition_type == "rank_parity":
            if condition_value == "even":
                return sum(1 for card in cards if card.rank in ['2', '4', '6', '8', 'T'])
            elif condition_value == "odd":
                return sum(1 for card in cards if card.rank in ['3', '5', '7', '9', 'A'])

        return 0

    def reset_round(self) -> None:
        """Reset jokers at the start of a new round (for round-based effects)."""
        # Future: handle round-specific joker effects
        pass

    def get_jokers_display(self) -> List[str]:
        """Get display strings for all active jokers."""
        return [str(joker) for joker in self.active_jokers]

    def __str__(self) -> str:
        return f"JokerManager: {len(self.active_jokers)}/{self.max_slots} jokers"
