"""
GameManager - Main game orchestration logic.
In Godot: extends Node
"""

from typing import List, Dict, Any
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.twin_hands_state_resource import TwinHandsState
from src.resources.card_resource import CardResource
from src.resources.hand_resource import HandResource
from src.managers.deck_manager import DeckManager
from src.managers.token_manager import TokenManager
from src.managers.scoring_manager import ScoringManager
from src.managers.trade_manager import TradeManager


class GameManager:
    """
    Main game orchestrator (PHASE A: basic game flow).
    Coordinates all managers and game flow.

    In Godot: extends Node
    """

    def __init__(self, config: TwinHandsConfig):
        """
        Initialize GameManager with config.
        Creates state and all sub-managers.

        Args:
            config: Game configuration
        """
        self.config = config
        self.state = TwinHandsState(config)

        # Initialize managers (RULE 3: separation of concerns)
        self.deck_manager = DeckManager(config, self.state)
        self.token_manager = TokenManager(config, self.state)
        self.scoring_manager = ScoringManager(config, self.state)
        self.trade_manager = TradeManager(config, self.state)  # PHASE B

        # Track hands played this round
        self._hands_played: List[HandResource] = []

    def start_game(self) -> None:
        """
        Start a new game.
        GDD 4-1: Split deck into N decks (default 2).
        GDD 4-2: Each deck starts with 4 visible cards.
        """
        # Split deck and draw initial cards
        self.deck_manager.split_deck()

    def play_hand(self, deck_index: int, card_indices: List[int]) -> Dict[str, Any]:
        """
        Play a hand from the specified deck.

        Args:
            deck_index: Which deck to play from (0-indexed)
            card_indices: Indices of cards in visible_cards to play

        Returns:
            Dict with:
                - success: bool (True if hand played successfully)
                - hand: HandResource (if success)
                - error: str (if failure)
        """
        # Validate can play hand (GDD v6.1: unlimited hands, but max 2 per deck)
        if not self.token_manager.can_play_hand(deck_index):
            return {
                "success": False,
                "error": "Cannot play hand: Max hands per deck reached (GDD v6.1: max 2)"
            }

        # Get cards from visible_cards
        deck = self.state.decks[deck_index]
        try:
            cards = [deck.visible_cards[i] for i in card_indices]
        except IndexError:
            return {
                "success": False,
                "error": "Invalid card indices"
            }

        # Evaluate hand
        hand = self.scoring_manager.evaluate_hand(cards)

        # Record hand played (GDD v6.1: no token spending, just tracking)
        self.token_manager.record_hand_played(deck_index)

        # Remove played cards from visible_cards
        # Sort indices in reverse to avoid index shifting
        played_cards = []
        for i in sorted(card_indices, reverse=True):
            played_cards.append(deck.visible_cards.pop(i))

        # Move played cards to discard pile (GDD v6.1 deckbuilder model)
        self.deck_manager.discard_to_pile(deck_index, played_cards)

        # Draw replacement cards (GDD v6.1: redraw from draw pile, auto-reshuffle if empty)
        num_to_draw = len(card_indices)
        self.deck_manager.draw_cards(deck_index, num_to_draw)

        # Track hand for scoring
        self._hands_played.append(hand)

        return {
            "success": True,
            "hand": hand
        }

    def discard_cards(self, deck_index: int, card_indices: List[int]) -> Dict[str, Any]:
        """
        Discard 1-5 cards from the specified deck (GDD v6.1 4-3).

        GDD v6.1: Discard → discard pile → redraw from draw pile.
        Costs 1 discard token per use (regardless of card count).

        Args:
            deck_index: Which deck to discard from (0-indexed)
            card_indices: Indices of cards in visible_cards to discard

        Returns:
            Dict with:
                - success: bool (True if discard successful)
                - error: str (if failure)
        """
        # Validate can discard
        if not self.token_manager.can_discard():
            return {
                "success": False,
                "error": "No discard tokens remaining (GDD v6.1: 3 per round)"
            }

        # Validate 1-5 cards
        if len(card_indices) < 1 or len(card_indices) > 5:
            return {
                "success": False,
                "error": f"Can only discard 1-5 cards (you selected {len(card_indices)})"
            }

        # Get cards from visible_cards
        deck = self.state.decks[deck_index]
        try:
            cards = [deck.visible_cards[i] for i in card_indices]
        except IndexError:
            return {
                "success": False,
                "error": "Invalid card indices"
            }

        # Remove discarded cards from visible_cards
        # Sort indices in reverse to avoid index shifting
        discarded_cards = []
        for i in sorted(card_indices, reverse=True):
            discarded_cards.append(deck.visible_cards.pop(i))

        # Move discarded cards to discard pile (GDD v6.1 deckbuilder model)
        self.deck_manager.discard_to_pile(deck_index, discarded_cards)

        # Draw replacement cards (GDD v6.1: redraw from draw pile, auto-reshuffle if empty)
        num_to_draw = len(card_indices)
        self.deck_manager.draw_cards(deck_index, num_to_draw)

        # Spend discard token
        self.token_manager.spend_discard_token()

        return {
            "success": True,
            "num_cards": len(card_indices)
        }

    def trade_card(self, source_deck: int, target_deck: int, card_index: int) -> Dict[str, Any]:
        """
        Trade ONE card from source deck to target deck (GDD v6.1 4-4).

        GDD v6.1: One-directional, 1 card at a time, can stack to 8-9+ cards.

        Args:
            source_deck: Index of deck giving card (0-indexed)
            target_deck: Index of deck receiving card (0-indexed)
            card_index: Index of card in source deck's visible_cards to trade

        Returns:
            Dict with:
                - success: bool (True if trade successful)
                - error: str (if failure)
        """
        # Validate trade
        if not self.trade_manager.can_trade(source_deck, target_deck):
            # Determine error reason
            if self.state.trade_tokens <= 0:
                error = "No trade tokens remaining (GDD v6.1: 2 per round)"
            elif source_deck == target_deck:
                error = "Cannot trade to same deck"
            else:
                error = "Source deck has no visible cards"

            return {
                "success": False,
                "error": error
            }

        # Execute trade (GDD v6.1: 1 card only)
        success = self.trade_manager.trade_card(source_deck, target_deck, card_index)

        return {
            "success": success
        }

    def calculate_round_score(self) -> int:
        """
        Calculate total score for the round.
        PHASE A: Simple sum of all hand scores (no Jokers).

        Returns:
            Total score
        """
        return self.scoring_manager.calculate_total_score(self._hands_played)

    def get_visible_cards(self, deck_index: int) -> List[CardResource]:
        """
        Get visible cards for a deck.

        Args:
            deck_index: Which deck (0-indexed)

        Returns:
            List of visible CardResource objects
        """
        return self.state.decks[deck_index].visible_cards

    def get_game_state_summary(self) -> Dict[str, Any]:
        """
        Get current game state summary for UI.

        Returns:
            Dict with game state info
        """
        return {
            "round": self.state.current_round,
            "discard_tokens": self.state.discard_tokens,  # GDD v6.1
            "trade_tokens": self.state.trade_tokens,      # GDD v6.1
            "hands_played_per_deck": self.state.hands_played_per_deck,
            "hands_this_round": len(self._hands_played),
            "current_score": self.calculate_round_score()
        }
