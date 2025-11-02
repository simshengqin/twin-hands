"""
TradeManager - Logic for trading cards between decks (GDD v6.1).
In Godot: extends Node
"""

from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource


class TradeManager:
    """
    Manages temporary trading between decks (GDD v6.1 4-4).
    Logic only - all data stored in state.

    GDD v6.1 Trade System:
    - One-directional: Give 1 card from deck X to deck Y
    - Giving deck: Redraws 1 card (stays at 7 visible baseline)
    - Receiving deck: Accumulates cards (can grow to 8, 9+ visible)
    - 2 trade tokens per round
    - All trades reset at round end (cards return to original decks)

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

    def can_trade(self, source_deck: int, target_deck: int) -> bool:
        """
        Check if trade is valid (GDD v6.1 4-4).

        Args:
            source_deck: Index of deck giving card (0, 1, ...)
            target_deck: Index of deck receiving card (0, 1, ...)

        Returns:
            True if trade is allowed, False otherwise

        Checks:
            - Must have trade tokens (GDD v6.1: 2 per round)
            - Source deck must have visible cards to give
            - Cannot trade to same deck
        """
        # Must have trade tokens
        if self.state.trade_tokens <= 0:
            return False

        # Cannot trade to self
        if source_deck == target_deck:
            return False

        # Source deck must have visible cards
        source = self.state.decks[source_deck]
        if len(source.visible_cards) == 0:
            return False

        return True

    def trade_card(self, source_deck: int, target_deck: int, card_index: int) -> bool:
        """
        Trade ONE card from source deck to target deck (GDD v6.1 4-4).

        GDD v6.1 4-4 Behavior:
        - Giving deck: Removes 1 card, redraws 1 card (stays at 7 baseline)
        - Receiving deck: Adds 1 card (can grow to 8, 9+ visible)
        - Spends 1 trade token

        Args:
            source_deck: Index of deck giving card
            target_deck: Index of deck receiving card
            card_index: Index of card to trade from source deck's visible cards

        Returns:
            True if trade successful, False if invalid

        Side effects:
            - Moves card from source.visible_cards to target.visible_cards
            - Source deck redraws 1 card from draw pile
            - Decrements state.trade_tokens
        """
        # Validate trade
        if not self.can_trade(source_deck, target_deck):
            return False

        source = self.state.decks[source_deck]
        target = self.state.decks[target_deck]

        # Validate card index
        if card_index < 0 or card_index >= len(source.visible_cards):
            return False

        # Remove card from source
        traded_card = source.visible_cards.pop(card_index)

        # Add to target deck (GDD v6.1: can stack to 8, 9+ cards)
        target.visible_cards.append(traded_card)

        # Source deck redraws 1 card (GDD v6.1: stays at 7 baseline)
        from src.managers.deck_manager import DeckManager
        deck_mgr = DeckManager(self.config, self.state)
        deck_mgr.draw_cards(source_deck, 1)

        # Spend trade token
        self.state.trade_tokens -= 1

        return True
