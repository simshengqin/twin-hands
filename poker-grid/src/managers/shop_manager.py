"""
Shop Manager - Godot-ready shop system controller
Manages shop inventory, buying/selling jokers, and rerolls.
In Godot: extends Node
"""

import random
from typing import List, Optional, Tuple

from src.resources.joker_resource import JokerResource
from src.managers.joker_manager import JokerManager


class ShopManager:
    """
    Manages the shop system: inventory generation, buying, selling, rerolls.
    In Godot, this would extend Node.

    GDScript equivalent:
    class_name ShopManager
    extends Node

    var state: GameStateResource
    var joker_manager: JokerManager
    var available_jokers: Array[JokerResource]
    var shop_inventory: Array[JokerResource]
    var reroll_count: int
    """

    # Rarity weights for random selection
    RARITY_WEIGHTS = {
        'Common': 70,
        'Uncommon': 25,
        'Rare': 5,
        'Legendary': 0  # Not available in shop (for now)
    }

    BASE_REROLL_COST = 5
    SHOP_SLOTS = 3

    def __init__(
        self,
        state: 'GameStateResource',
        joker_manager: JokerManager,
        available_jokers: List[JokerResource],
        config: 'GameConfigResource' = None
    ):
        """
        Initialize the shop manager.
        In Godot, this would be _ready() function.

        Args:
            state: Game state (for money/token tracking)
            joker_manager: Manager for player's active jokers
            available_jokers: Pool of all available jokers (from CSV)
            config: Game configuration (for token system toggle)
        """
        self.state = state
        self.joker_manager = joker_manager
        self.available_jokers = available_jokers
        self.config = config

        # Shop state
        self.shop_inventory: List[Optional[JokerResource]] = []
        self.reroll_count: int = 0

    def open_shop(self) -> None:
        """
        Open the shop: generate initial inventory, reset reroll count.
        Call this when entering the shop between rounds.
        """
        self.reroll_count = 0
        self.generate_inventory()

    def generate_inventory(self) -> None:
        """
        Generate shop inventory: 3 random jokers weighted by rarity.
        Excludes jokers player already owns.
        Excludes duplicate jokers within the shop.
        Can have empty slots if pool exhausted.
        """
        self.shop_inventory = []

        # Get jokers player already owns
        owned_joker_ids = {joker.id for joker in self.joker_manager.active_jokers}

        # Filter available jokers (not owned, available in shop)
        available_pool = [
            joker for joker in self.available_jokers
            if joker.id not in owned_joker_ids
            and self.RARITY_WEIGHTS.get(joker.rarity, 0) > 0
        ]

        # Generate up to SHOP_SLOTS jokers
        selected_ids = set()  # Track selected to avoid duplicates

        for _ in range(self.SHOP_SLOTS):
            # Filter out already selected jokers
            remaining_pool = [
                joker for joker in available_pool
                if joker.id not in selected_ids
            ]

            if not remaining_pool:
                # No more jokers available, add empty slot
                self.shop_inventory.append(None)
                continue

            # Select random joker weighted by rarity
            selected_joker = self._select_random_by_rarity(remaining_pool)

            if selected_joker:
                self.shop_inventory.append(selected_joker)
                selected_ids.add(selected_joker.id)
            else:
                self.shop_inventory.append(None)

    def _select_random_by_rarity(self, joker_pool: List[JokerResource]) -> Optional[JokerResource]:
        """
        Select a random joker from pool, weighted by rarity.

        Returns:
            Selected joker or None if pool is empty
        """
        if not joker_pool:
            return None

        # Build weighted list
        weighted_jokers = []
        for joker in joker_pool:
            weight = self.RARITY_WEIGHTS.get(joker.rarity, 0)
            weighted_jokers.extend([joker] * weight)

        if not weighted_jokers:
            return None

        return random.choice(weighted_jokers)

    def buy_joker(self, shop_index: int) -> Tuple[bool, str]:
        """
        Attempt to buy a joker from shop inventory.
        Uses tokens if config.use_token_system is True, otherwise uses money.

        Args:
            shop_index: Index in shop_inventory (0-2)

        Returns:
            (success, message)
        """
        # Validate index
        if not (0 <= shop_index < len(self.shop_inventory)):
            return False, "Invalid shop slot"

        joker = self.shop_inventory[shop_index]

        if joker is None:
            return False, "Empty slot"

        # Check if player has joker slots
        if not self.joker_manager.has_empty_slot():
            return False, "No joker slots available (sell a joker first)"

        # Check currency and complete purchase
        use_tokens = self.config.use_token_system if self.config else False

        if use_tokens:
            # Token system
            if not self.state.can_afford_tokens(joker.cost):
                return False, f"Not enough tokens (need {joker.cost} tokens)"

            self.state.spend_tokens(joker.cost)
            self.joker_manager.add_joker(joker.duplicate())
            self.shop_inventory[shop_index] = None

            return True, f"Bought {joker.name} for {joker.cost} tokens"
        else:
            # Money system
            if not self.state.can_afford(joker.cost):
                return False, f"Not enough money (need ${joker.cost})"

            self.state.spend_money(joker.cost)
            self.joker_manager.add_joker(joker.duplicate())
            self.shop_inventory[shop_index] = None

            return True, f"Bought {joker.name} for ${joker.cost}"

    def sell_joker(self, joker_index: int) -> Tuple[bool, str]:
        """
        Sell one of player's active jokers for 50% of cost.
        Returns tokens if config.use_token_system is True, otherwise returns money.

        Args:
            joker_index: Index in joker_manager.active_jokers

        Returns:
            (success, message)
        """
        if not (0 <= joker_index < self.joker_manager.get_joker_count()):
            return False, "Invalid joker index"

        joker = self.joker_manager.active_jokers[joker_index]
        sell_value = joker.sell_value

        # Remove joker and add currency
        self.joker_manager.remove_joker(joker_index)

        use_tokens = self.config.use_token_system if self.config else False

        if use_tokens:
            self.state.add_tokens(sell_value)
            return True, f"Sold {joker.name} for {sell_value} tokens"
        else:
            self.state.add_money(sell_value)
            return True, f"Sold {joker.name} for ${sell_value}"

    def reroll_shop(self) -> Tuple[bool, str]:
        """
        Reroll shop inventory for a cost.
        Cost increases by 1 currency per reroll in same shop visit.
        Uses tokens if config.use_token_system is True, otherwise uses money.

        Returns:
            (success, message)
        """
        reroll_cost = self.BASE_REROLL_COST + self.reroll_count

        use_tokens = self.config.use_token_system if self.config else False

        if use_tokens:
            # Token system
            if not self.state.can_afford_tokens(reroll_cost):
                return False, f"Not enough tokens (need {reroll_cost} tokens)"

            self.state.spend_tokens(reroll_cost)
            self.reroll_count += 1
            self.generate_inventory()

            return True, f"Rerolled for {reroll_cost} tokens"
        else:
            # Money system
            if not self.state.can_afford(reroll_cost):
                return False, f"Not enough money (need ${reroll_cost})"

            self.state.spend_money(reroll_cost)
            self.reroll_count += 1
            self.generate_inventory()

            return True, f"Rerolled for ${reroll_cost}"

    def get_reroll_cost(self) -> int:
        """Get current reroll cost."""
        return self.BASE_REROLL_COST + self.reroll_count

    def get_shop_display(self) -> List[dict]:
        """
        Get shop inventory in display format.

        Returns:
            List of dicts with joker info or None for empty slots
        """
        display = []
        for i, joker in enumerate(self.shop_inventory):
            if joker:
                display.append({
                    'index': i,
                    'joker': joker,
                    'name': joker.get_display_name(),
                    'description': joker.get_description(),
                    'cost': joker.cost,
                    'rarity': joker.rarity
                })
            else:
                display.append({
                    'index': i,
                    'joker': None,
                    'name': '[EMPTY]',
                    'description': 'No joker available',
                    'cost': 0,
                    'rarity': ''
                })
        return display

    def close_shop(self) -> None:
        """
        Close the shop: clear inventory.
        Call this when exiting the shop.
        """
        self.shop_inventory = []
        self.reroll_count = 0
