"""
Twin Hands - Terminal UI (PHASE A: Minimal Playable)
Balatro-inspired UI with clean, information-dense layout.
Run this to play the game!
"""

from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.ui.terminal_ui import TerminalUI


def parse_card_selection(input_str: str, num_decks: int = 2):
    """
    Parse unified card selection (1-8 for 2 decks).

    Args:
        input_str: User input (e.g., "123" or "1456")
        num_decks: Number of decks (default 2)

    Returns:
        tuple: (deck_index, card_indices) or None if invalid
            - deck_index: which deck (0-indexed)
            - card_indices: list of card indices within that deck (0-indexed)
    """
    try:
        # Parse individual digits
        card_nums = [int(c) for c in input_str if c.isdigit()]

        if not card_nums:
            return None

        # Map unified indices to (deck, card_in_deck)
        cards_per_deck = 4
        selections = []

        for unified_idx in card_nums:
            # Convert 1-indexed to 0-indexed
            zero_idx = unified_idx - 1

            # Which deck? (0-7 maps to deck 0 or 1)
            deck_idx = zero_idx // cards_per_deck
            card_idx = zero_idx % cards_per_deck

            if deck_idx >= num_decks or card_idx >= cards_per_deck:
                return None  # Out of range

            selections.append((deck_idx, card_idx))

        # All cards must be from same deck (can't mix decks in one hand)
        if not selections:
            return None

        first_deck = selections[0][0]
        if not all(deck == first_deck for deck, _ in selections):
            return None  # Mixed decks

        # Extract card indices for that deck
        card_indices = [card_idx for _, card_idx in selections]
        return (first_deck, card_indices)

    except (ValueError, IndexError):
        return None


def play_round(game: GameManager, ui: TerminalUI):
    """Play one round with Balatro-style UI (PHASE B: with Trading)."""
    game.start_game()

    while game.state.hand_tokens > 0 or game.state.trade_tokens > 0:
        # Display full state (all-in-one screen like Balatro)
        ui.display_full_state()

        # Get player input
        user_input = ui.prompt_input().strip().lower()

        if user_input == "end":
            break

        # Handle trade command (PHASE B)
        if user_input.startswith("trade "):
            trade_input = user_input.replace("trade ", "").strip()
            parsed = parse_card_selection(trade_input, game.config.num_decks)

            if parsed is None:
                ui.display_error("Invalid trade. Enter card numbers from ONE deck (e.g., 'trade 12' or 'trade 567')")
                input("\nPress Enter to continue...")
                continue

            deck_index, card_indices = parsed

            try:
                result = game.trade_cards(deck_index, card_indices)

                if result["success"]:
                    ui.display_trade_result(len(card_indices), deck_index)
                    input("\nPress Enter to continue...")
                else:
                    ui.display_error(result["error"])
                    input("\nPress Enter to continue...")

            except (ValueError, IndexError) as e:
                ui.display_error(f"Error trading cards - {e}")
                input("\nPress Enter to continue...")

            continue

        # Parse play command (just card numbers)
        parsed = parse_card_selection(user_input, game.config.num_decks)

        if parsed is None:
            ui.display_error("Invalid input. Enter card numbers from ONE deck (e.g., '123' or '5678')")
            input("\nPress Enter to continue...")
            continue

        deck_index, card_indices = parsed

        try:
            result = game.play_hand(deck_index, card_indices)

            if result["success"]:
                hand = result["hand"]
                ui.display_hand_result(hand)
                input("\nPress Enter to continue...")
            else:
                ui.display_error(result["error"])
                input("\nPress Enter to continue...")

        except (ValueError, IndexError) as e:
            ui.display_error(f"Error playing hand - {e}")
            input("\nPress Enter to continue...")

    # Round over - display results
    final_score = game.calculate_round_score()
    quota = game.config.round_quotas[0]  # Round 1 quota
    success = final_score >= quota

    ui.display_round_end(final_score, quota, success)


def main():
    """Main entry point."""
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)

    # Welcome screen
    ui.clear_screen()
    print(f"\n{ui.BOLD}{'='*70}{ui.RESET}")
    print(f"{ui.YELLOW}{ui.BOLD}  TWIN HANDS{ui.RESET} {ui.GRAY}|{ui.RESET} {ui.CYAN}Phase B: Core Loop (Trading){ui.RESET}")
    print(f"{ui.BOLD}{'='*70}{ui.RESET}\n")
    print(f"  {ui.BOLD}Goal:{ui.RESET} Play poker hands from 2 decks to beat the quota!\n")
    print(f"  {ui.BOLD}Rules:{ui.RESET}")
    print(f"    • 4 hand tokens per round (max 2 per deck)")
    print(f"    • 3 trade tokens per round")
    print(f"    • Play 1-4 cards to form poker hands")
    print(f"    • Trade cards between decks to set up combos")
    print(f"    • Beat Round 1 quota: {ui.CYAN}300 points{ui.RESET}\n")
    print(f"  {ui.BOLD}How to Play:{ui.RESET}")
    print(f"    • Cards numbered {ui.CYAN}1-4{ui.RESET} (Deck 1) and {ui.CYAN}5-8{ui.RESET} (Deck 2)")
    print(f"    • Play hand: Type {ui.CYAN}123{ui.RESET} or {ui.CYAN}5678{ui.RESET}")
    print(f"    • Trade cards: Type {ui.CYAN}trade 12{ui.RESET} (gives 2 cards to other deck)")
    print(f"    • End round: Type {ui.CYAN}end{ui.RESET}\n")
    print(f"{ui.BOLD}{'='*70}{ui.RESET}\n")

    input("Press Enter to start...")

    # Play round
    play_round(game, ui)

    # Goodbye
    print(f"\n{ui.BOLD}Thanks for playing Twin Hands!{ui.RESET}")
    print(f"{ui.GRAY}This is a Phase A prototype.{ui.RESET}")
    print(f"{ui.GRAY}Coming soon: Trading, Jokers, Shop, 8-round progression!{ui.RESET}\n")


if __name__ == "__main__":
    main()
