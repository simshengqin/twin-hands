"""
Twin Hands - Terminal UI (PHASE A: Minimal Playable)
Balatro-inspired UI with clean, information-dense layout.
Run this to play the game!
"""

from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.ui.terminal_ui import TerminalUI


def parse_card_selection(input_str: str, game: GameManager):
    """
    Parse unified card selection with dynamic deck sizes (handles trading).

    Supports:
    - Single digits: "123" → [1,2,3]
    - With spaces: "10 11 12" → [10,11,12]
    - With commas: "10,11,12" → [10,11,12]

    Args:
        input_str: User input (e.g., "123" or "10 11 12")
        game: GameManager to check actual deck sizes

    Returns:
        tuple: (deck_index, card_indices, num_cards_selected) or None if invalid
    """
    try:
        # Check if input contains spaces or commas (for multi-digit numbers)
        if ' ' in input_str or ',' in input_str:
            # Split by spaces and/or commas
            parts = input_str.replace(',', ' ').split()
            card_nums = [int(p) for p in parts]
        else:
            # Parse as individual digits (for convenience: "123" = [1,2,3])
            card_nums = [int(c) for c in input_str if c.isdigit()]

        if not card_nums:
            return None

        # Build mapping: unified_index → (deck_idx, card_idx)
        index_to_deck_card = {}
        unified_idx = 1  # Start at 1 (user-facing)

        for deck_idx in range(game.config.num_decks):
            num_cards = len(game.state.decks[deck_idx].visible_cards)
            for card_idx in range(num_cards):
                index_to_deck_card[unified_idx] = (deck_idx, card_idx)
                unified_idx += 1

        # Map user input to (deck, card) pairs
        selections = []
        for card_num in card_nums:
            if card_num not in index_to_deck_card:
                return None  # Invalid card number
            selections.append(index_to_deck_card[card_num])

        if not selections:
            return None

        # All cards must be from same deck
        first_deck = selections[0][0]
        if not all(deck == first_deck for deck, _ in selections):
            return None  # Mixed decks

        # Extract card indices for that deck
        card_indices = [card_idx for _, card_idx in selections]
        return (first_deck, card_indices, len(card_nums))

    except (ValueError, IndexError, KeyError):
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

        # Handle trade command (PHASE B) - accepts "t123", "t 123", "trade 123"
        if user_input.startswith("trade") or user_input.startswith("t"):
            # Extract card numbers after "trade" or "t"
            if user_input.startswith("trade"):
                if len(user_input) > 5 and user_input[5] == ' ':
                    trade_input = user_input[6:].strip()  # "trade 123"
                else:
                    trade_input = user_input[5:].strip()  # "trade123"
            elif user_input.startswith("t"):
                if len(user_input) > 1 and user_input[1] == ' ':
                    trade_input = user_input[2:].strip()  # "t 123"
                else:
                    trade_input = user_input[1:].strip()  # "t123"

            # Skip if it's just "t" or "trade" with no cards
            if not trade_input:
                ui.display_error("Invalid trade. Enter card numbers (e.g., 't123' or 't 10 11')")
                input("\nPress Enter to continue...")
                continue

            parsed = parse_card_selection(trade_input, game)

            if parsed is None:
                ui.display_error("Invalid trade. Enter 1-4 card numbers from ONE deck (e.g., 't123' or 't 10 11')")
                input("\nPress Enter to continue...")
                continue

            deck_index, card_indices, num_cards = parsed

            # Validate 1-4 cards (GDD 4-4)
            if num_cards < 1 or num_cards > 4:
                ui.display_error(f"Can only trade 1-4 cards per trade (you selected {num_cards})")
                input("\nPress Enter to continue...")
                continue

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

        # Parse play command (numbers, spaces, commas only)
        # Allow: "123", "10 11 12", "10,11,12"
        if not all(c.isdigit() or c in ' ,' for c in user_input):
            ui.display_error("Invalid input. Enter only card numbers (e.g., '123' or '10 11 12')")
            input("\nPress Enter to continue...")
            continue

        parsed = parse_card_selection(user_input, game)

        if parsed is None:
            ui.display_error("Invalid selection. Enter 1-4 cards from ONE deck (e.g., '123' or '10 11')")
            input("\nPress Enter to continue...")
            continue

        deck_index, card_indices, num_cards = parsed

        # Validate 1-4 cards (GDD 4-7)
        if num_cards < 1 or num_cards > 4:
            ui.display_error(f"Can only play 1-4 cards per hand (you selected {num_cards})")
            input("\nPress Enter to continue...")
            continue

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

    # Welcome screen (can be skipped for testing)
    if not config.skip_welcome_screen:
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
        print(f"    • Cards numbered {ui.CYAN}1-4{ui.RESET} (Deck 1), {ui.CYAN}5-8{ui.RESET} (Deck 2)")
        print(f"    • After trading: decks can have up to 8 cards each")
        print(f"    • Play 1-4 cards: {ui.CYAN}123{ui.RESET} or {ui.CYAN}10 11 12{ui.RESET} (use spaces for 10+)")
        print(f"    • Trade 1-4 cards: {ui.CYAN}t123{ui.RESET} or {ui.CYAN}t 10 11{ui.RESET}")
        print(f"    • End round: {ui.CYAN}end{ui.RESET}\n")
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
