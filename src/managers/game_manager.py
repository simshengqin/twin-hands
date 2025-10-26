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
        # Validate can spend token
        if not self.token_manager.can_spend_hand_token(deck_index):
            return {
                "success": False,
                "error": "Cannot play hand: No tokens or max hands per deck reached"
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

        # Spend token
        self.token_manager.spend_hand_token(deck_index)

        # Remove played cards from visible_cards
        # Sort indices in reverse to avoid index shifting
        for i in sorted(card_indices, reverse=True):
            deck.visible_cards.pop(i)

        # Draw replacement cards
        num_to_draw = len(card_indices)
        self.deck_manager.draw_cards(deck_index, num_to_draw)

        # Track hand for scoring
        self._hands_played.append(hand)

        return {
            "success": True,
            "hand": hand
        }

    def trade_cards(self, source_deck: int, card_indices: List[int]) -> Dict[str, Any]:
        """
        Trade cards from source deck to receiving deck (PHASE B: GDD 4-4).

        Args:
            source_deck: Index of deck giving cards (0-indexed)
            card_indices: Indices of cards in visible_cards to trade

        Returns:
            Dict with:
                - success: bool (True if trade successful)
                - error: str (if failure)
        """
        # Validate trade
        if not self.trade_manager.can_trade(source_deck, len(card_indices)):
            # Determine error reason
            if self.state.trade_tokens <= 0:
                error = "No trade tokens remaining"
            else:
                error = "Receiving deck would exceed 8 cards"

            return {
                "success": False,
                "error": error
            }

        # Execute trade
        success = self.trade_manager.trade_cards(source_deck, card_indices)

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
            "hand_tokens": self.state.hand_tokens,
            "trade_tokens": self.state.trade_tokens,  # PHASE B
            "hands_played_per_deck": self.state.hands_played_per_deck,
            "hands_this_round": len(self._hands_played),
            "current_score": self.calculate_round_score()
        }
