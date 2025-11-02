"""
Terminal UI for Twin Hands (Balatro-inspired layout).
Clean, information-dense display optimized for 2-deck gameplay.
"""

import sys
from typing import List, Optional
from src.managers.game_manager import GameManager
from src.resources.card_resource import CardResource
from src.resources.hand_resource import HandResource
from src.utils.hand_highlight_detector import HandHighlightDetector

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class TerminalUI:
    """
    Balatro-inspired terminal UI for Twin Hands.
    Optimized for 2-deck gameplay with clear visual hierarchy.
    """

    # Color codes (ANSI)
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Text Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Background Colors (for highlighting)
    BG_GREEN = "\033[42m"    # Green background (0 cards missing)
    BG_YELLOW = "\033[43m"   # Yellow background (1 card missing)
    BG_ORANGE = "\033[41m"   # Red/Orange background (2 cards missing)

    # Suit symbols (emoji)
    SUITS = {
        "hearts": "♥",
        "diamonds": "♦",
        "clubs": "♣",
        "spades": "♠"
    }

    # Suit order for sorting
    SUIT_ORDER = ["clubs", "diamonds", "hearts", "spades"]  # ♣ ♦ ♥ ♠

    # Suit colors for better visibility
    # Red vs Blue makes suits much easier to distinguish
    SUIT_COLORS = {
        "hearts": RED,        # ♥ Red
        "diamonds": YELLOW,   # ♦ Yellow (orange-ish)
        "clubs": CYAN,        # ♣ Cyan (light blue)
        "spades": BLUE        # ♠ Blue
    }

    def __init__(self, game: GameManager):
        """Initialize UI with game manager."""
        self.game = game
        # GDD v6.1: Hand highlighting filters (per-deck toggleable)
        # Default to Flush and Straight (most visual impact)
        self.enabled_filters = {
            0: ["Flush", "Straight"],  # Deck 0
            1: ["Flush", "Straight"]   # Deck 1
        }

        # Available hand types for filtering
        self.available_hand_types = [
            "Flush", "Straight", "Four of a Kind",
            "Three of a Kind", "Two Pair", "Pair"
        ]

    def clear_screen(self):
        """Clear terminal (cross-platform)."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    def format_card(self, card: CardResource, index: int = None, bg_color: str = None) -> str:
        """
        Format a card with suit symbol and color (Balatro style).

        Args:
            card: CardResource to format
            index: Optional index to show [0], [1], etc.
            bg_color: Optional background color for highlighting

        Returns:
            Formatted string like "[0] K♥" (red) or "[1] 3♠" (white)
        """
        suit_symbol = self.SUITS.get(card.suit, card.suit[0].upper())
        suit_color = self.SUIT_COLORS.get(card.suit, self.WHITE)

        # Pad rank to 2 chars for alignment (10 is special)
        rank_str = f"{card.rank:>2}"

        # Apply background color if provided (for highlighting)
        if bg_color:
            card_str = f"{bg_color}{suit_color}{rank_str}{suit_symbol}{self.RESET}"
        else:
            card_str = f"{suit_color}{rank_str}{suit_symbol}{self.RESET}"

        if index is not None:
            return f"{self.GRAY}[{index}]{self.RESET} {card_str}"
        return card_str

    def format_hand_type(self, hand: HandResource) -> str:
        """Format hand type with score (Balatro style)."""
        score_color = self.CYAN if hand.base_score >= 15 else self.WHITE
        return f"{self.BOLD}{hand.hand_type}{self.RESET} {score_color}({hand.base_score} pts){self.RESET}"

    def display_header(self):
        """Display game header with round and quota info."""
        state = self.game.get_game_state_summary()
        quota = self.game.config.round_quotas[state["round"] - 1]
        current_score = state["current_score"]

        # Progress bar (Windows-safe characters)
        progress = min(100, int((current_score / quota) * 100))
        bar_filled = "#" * (progress // 5)
        bar_empty = "-" * (20 - (progress // 5))

        print(f"\n{self.BOLD}{'='*70}{self.RESET}")
        print(f"{self.YELLOW}{self.BOLD}  TWIN HANDS{self.RESET} {self.GRAY}|{self.RESET} "
              f"{self.CYAN}Round {state['round']}{self.RESET}")
        print(f"{self.BOLD}{'='*70}{self.RESET}\n")

        # Score display (big numbers like Balatro)
        score_color = self.GREEN if current_score >= quota else self.RED
        print(f"  {self.BOLD}Round Score:{self.RESET} {score_color}{self.BOLD}{current_score:,}{self.RESET} "
              f"{self.GRAY}/{self.RESET} {self.CYAN}{quota:,}{self.RESET}")
        print(f"  {self.GRAY}[{bar_filled}{bar_empty}] {progress}%{self.RESET}\n")

    def display_tokens(self):
        """Display token status (GDD v6.1: discard + trade tokens)."""
        state = self.game.get_game_state_summary()

        # Discard tokens (GDD v6.1: 3 per round) - not yet implemented
        discard_color = self.YELLOW if state["discard_tokens"] > 0 else self.GRAY
        discard_icons = "[D]" * state["discard_tokens"] + self.GRAY + "[_]" * (3 - state["discard_tokens"]) + self.RESET

        # Trade tokens (GDD v6.1: 2 per round)
        trade_color = self.CYAN if state["trade_tokens"] > 0 else self.GRAY
        trade_icons = "[T]" * state["trade_tokens"] + self.GRAY + "[_]" * (2 - state["trade_tokens"]) + self.RESET

        print(f"  {self.BOLD}Discard Tokens:{self.RESET} {discard_color}{state['discard_tokens']}/3{self.RESET} {discard_icons}")
        print(f"  {self.BOLD}Trade Tokens:{self.RESET} {trade_color}{state['trade_tokens']}/2{self.RESET} {trade_icons}\n")

    def display_deck_status(self):
        """Display per-deck hand counts (unique to Twin Hands)."""
        state = self.game.get_game_state_summary()

        print(f"  {self.BOLD}Deck Status:{self.RESET}")
        for i, count in enumerate(state["hands_played_per_deck"]):
            deck_num = i + 1
            max_hands = self.game.config.max_hands_per_deck

            # Color: green if can play, gray if maxed out
            if count < max_hands:
                status_color = self.GREEN
                status = f"{count}/{max_hands}"
            else:
                status_color = self.GRAY
                status = f"{count}/{max_hands} {self.RED}(MAX){self.RESET}"

            print(f"    {self.CYAN}Deck {deck_num}:{self.RESET} {status_color}{status}{self.RESET} hands played")
        print()

    def _sort_cards(self, cards: List[CardResource]) -> List[CardResource]:
        """Sort cards by rank first, then suit."""
        rank_order = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

        def sort_key(card):
            rank_idx = rank_order.index(card.rank) if card.rank in rank_order else 99
            suit_idx = self.SUIT_ORDER.index(card.suit) if card.suit in self.SUIT_ORDER else 99
            return (rank_idx, suit_idx)  # Rank first, suit second

        return sorted(cards, key=sort_key)

    def display_decks(self):
        """Display both decks with hand highlighting (GDD v6.1)."""
        print(f"{self.BOLD}{'-'*70}{self.RESET}")

        for deck_idx in range(self.game.config.num_decks):
            # Sort the actual visible_cards list (modifies state)
            # This ensures displayed order matches actual indices
            deck = self.game.state.decks[deck_idx]
            deck.visible_cards = self._sort_cards(deck.visible_cards)
            cards = deck.visible_cards
            deck_num = deck_idx + 1

            # Deck header
            hands_played = self.game.state.hands_played_per_deck[deck_idx]
            max_hands = self.game.config.max_hands_per_deck

            if hands_played < max_hands:
                deck_color = self.CYAN
                status = f"{self.GREEN}*{self.RESET}"  # Green star = available
            else:
                deck_color = self.GRAY
                status = f"{self.RED}X{self.RESET}"  # Red X = maxed out

            print(f"\n  {status} {deck_color}{self.BOLD}DECK {deck_num}{self.RESET} "
                  f"{self.GRAY}({hands_played}/{max_hands} played){self.RESET}")

            # GDD v6.1: Detect highlights for this deck
            filters = self.enabled_filters.get(deck_idx, [])
            highlight_match = HandHighlightDetector.detect_best_highlight(cards, filters)

            # Build highlight map (index -> background color)
            highlight_map = {}
            if highlight_match:
                # Map cards_needed to background color
                bg_color = {
                    0: self.BG_GREEN,   # Complete hand (0 missing)
                    1: self.BG_YELLOW,  # Need 1 more card
                    2: self.BG_ORANGE   # Need 2 more cards
                }.get(highlight_match.cards_needed, None)

                if bg_color:
                    for idx in highlight_match.matching_indices:
                        highlight_map[idx] = bg_color

            # Cards in a row with unified indexing and highlighting
            card_str = "    "
            for i, card in enumerate(cards):
                # Unified index: Deck 0 = 1-7, Deck 1 = 8-14 (v6.1: 7 cards)
                unified_idx = (deck_idx * 7) + i + 1  # 1-indexed
                bg_color = highlight_map.get(i, None)
                card_str += self.format_card(card, unified_idx, bg_color) + "  "
            print(card_str)

        print(f"\n{self.BOLD}{'-'*70}{self.RESET}\n")

    def display_hands_played(self):
        """Display hands played this round (like Balatro's hand history)."""
        if not self.game._hands_played:
            return

        print(f"  {self.BOLD}Hands Played This Round:{self.RESET}")
        for i, hand in enumerate(self.game._hands_played, 1):
            print(f"    {self.GRAY}{i}.{self.RESET} {self.format_hand_type(hand)}")
        print()

    def display_commands(self):
        """Display available commands (Balatro-style: compact, clear)."""
        print(f"{self.BOLD}{'-'*70}{self.RESET}")
        print(f"  {self.BOLD}Commands:{self.RESET}")
        print(f"    {self.YELLOW}<card numbers>{self.RESET}  {self.GRAY}->{self.RESET}  "
              f"Play 1-5 cards (e.g., {self.CYAN}123{self.RESET} or {self.CYAN}10 11{self.RESET})")
        print(f"    {self.YELLOW}d<cards>{self.RESET}         {self.GRAY}->{self.RESET}  "
              f"Discard 1-5 cards (e.g., {self.CYAN}d123{self.RESET} or {self.CYAN}d 10 11{self.RESET})")
        print(f"    {self.YELLOW}t<card>{self.RESET}          {self.GRAY}->{self.RESET}  "
              f"Trade 1 card (e.g., {self.CYAN}t1{self.RESET} or {self.CYAN}t 10{self.RESET})")
        print(f"    {self.YELLOW}f<deck> <type>{self.RESET}   {self.GRAY}->{self.RESET}  "
              f"Toggle filter (e.g., {self.CYAN}f1 Flush{self.RESET}, {self.CYAN}f2 Pair{self.RESET})")
        print(f"    {self.YELLOW}filters{self.RESET}          {self.GRAY}->{self.RESET}  "
              f"Show current filter settings")
        print(f"    {self.YELLOW}end{self.RESET}              {self.GRAY}->{self.RESET}  "
              f"End round and calculate score")
        print(f"{self.BOLD}{'-'*70}{self.RESET}\n")

    def display_full_state(self):
        """Display complete game state (all-in-one screen like Balatro)."""
        self.clear_screen()
        self.display_header()
        self.display_tokens()
        self.display_deck_status()
        self.display_hands_played()
        self.display_decks()
        self.display_commands()

    def display_hand_result(self, hand: HandResource):
        """Display hand result (Balatro-style: big, satisfying)."""
        print(f"\n  {self.GREEN}{self.BOLD}[SUCCESS!]{self.RESET}")
        print(f"  {self.format_hand_type(hand)}")

        # Show cards played
        cards_str = " ".join(self.format_card(card) for card in hand.cards)
        print(f"  {self.GRAY}Cards:{self.RESET} {cards_str}\n")

    def display_trade_result(self, num_cards: int, source_deck: int):
        """Display trade result (PHASE B)."""
        receiving_deck = 1 - source_deck
        print(f"\n  {self.CYAN}{self.BOLD}[TRADE SUCCESSFUL!]{self.RESET}")
        print(f"  {self.GRAY}Traded {num_cards} card{'s' if num_cards > 1 else ''} from Deck {source_deck + 1} → Deck {receiving_deck + 1}{self.RESET}\n")

    def display_error(self, message: str):
        """Display error message."""
        print(f"\n  {self.RED}{self.BOLD}[ERROR]{self.RESET} {message}\n")

    def display_round_end(self, final_score: int, quota: int, success: bool):
        """Display round end summary (Balatro-style: big reveal)."""
        self.clear_screen()

        print(f"\n{self.BOLD}{'='*70}{self.RESET}")
        if success:
            print(f"{self.GREEN}{self.BOLD}  [ROUND COMPLETE - SUCCESS!]{self.RESET}")
        else:
            print(f"{self.RED}{self.BOLD}  [ROUND FAILED]{self.RESET}")
        print(f"{self.BOLD}{'='*70}{self.RESET}\n")

        # Big score display
        score_color = self.GREEN if success else self.RED
        print(f"  {self.BOLD}Final Score:{self.RESET} {score_color}{self.BOLD}{final_score:,}{self.RESET}")
        print(f"  {self.BOLD}Quota:{self.RESET}       {self.CYAN}{quota:,}{self.RESET}")

        if success:
            diff = final_score - quota
            print(f"  {self.GREEN}+{diff:,} over quota!{self.RESET}")
        else:
            diff = quota - final_score
            print(f"  {self.RED}-{diff:,} short of quota{self.RESET}")

        print(f"\n{self.BOLD}{'='*70}{self.RESET}\n")

    def toggle_filter(self, deck_index: int, hand_type: str) -> bool:
        """
        Toggle a hand type filter for a specific deck.

        Args:
            deck_index: Which deck (0-indexed)
            hand_type: Hand type to toggle (e.g., "Flush", "Pair")

        Returns:
            True if filter is now enabled, False if now disabled
        """
        if deck_index not in self.enabled_filters:
            self.enabled_filters[deck_index] = []

        filters = self.enabled_filters[deck_index]

        if hand_type in filters:
            filters.remove(hand_type)
            return False
        else:
            filters.append(hand_type)
            return True

    def display_filter_status(self):
        """Display current filter settings for all decks."""
        print(f"  {self.BOLD}Hand Highlighting Filters:{self.RESET}")
        for deck_idx in range(self.game.config.num_decks):
            deck_num = deck_idx + 1
            filters = self.enabled_filters.get(deck_idx, [])

            if filters:
                filter_str = ", ".join(filters)
                print(f"    {self.CYAN}Deck {deck_num}:{self.RESET} {self.GREEN}{filter_str}{self.RESET}")
            else:
                print(f"    {self.CYAN}Deck {deck_num}:{self.RESET} {self.GRAY}None{self.RESET}")
        print()

    def prompt_input(self) -> str:
        """Get user input with styled prompt."""
        return input(f"  {self.YELLOW}>{self.RESET} ").strip()
