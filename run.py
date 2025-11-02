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
    """Play one round with Balatro-style UI (GDD v6.1: with Trading)."""
    game.start_game()

    # GDD v6.1: Check if can still play hands (max 2 per deck) OR have trade/discard tokens
    def can_continue():
        # Can play if any deck hasn't hit max hands
        can_play = any(game.token_manager.can_play_hand(i) for i in range(game.config.num_decks))
        # Can trade if have trade tokens
        can_trade = game.state.trade_tokens > 0
        # Can discard if have discard tokens
        can_discard = game.state.discard_tokens > 0
        return can_play or can_trade or can_discard

    while can_continue():
        # Display full state (all-in-one screen like Balatro)
        ui.display_full_state()

        # Get player input
        user_input = ui.prompt_input().strip().lower()

        if user_input == "end":
            break

        # Handle filters command - show current filter settings
        if user_input == "filters":
            ui.clear_screen()
            ui.display_header()
            ui.display_filter_status()
            print(f"  {ui.BOLD}Available Hand Types:{ui.RESET}")
            for hand_type in ui.available_hand_types:
                print(f"    {ui.GRAY}•{ui.RESET} {hand_type}")
            print()
            input("Press Enter to continue...")
            continue

        # Handle filter toggle command - "f1 Flush", "f2 Pair", etc.
        if user_input.startswith("f") and len(user_input) > 1 and user_input[1].isdigit():
            try:
                # Parse "f1 Flush" -> deck_num=1, hand_type="Flush"
                parts = user_input[1:].split(maxsplit=1)
                if len(parts) != 2:
                    ui.display_error("Invalid filter command. Use format: f<deck> <type> (e.g., 'f1 Flush')")
                    input("\nPress Enter to continue...")
                    continue

                deck_num = int(parts[0])
                hand_type_input = parts[1].strip()

                # Validate deck number
                if deck_num < 1 or deck_num > game.config.num_decks:
                    ui.display_error(f"Invalid deck number. Use 1-{game.config.num_decks}")
                    input("\nPress Enter to continue...")
                    continue

                # Find matching hand type (case-insensitive, partial match)
                hand_type = None
                hand_type_lower = hand_type_input.lower()
                for available_type in ui.available_hand_types:
                    if available_type.lower().startswith(hand_type_lower):
                        hand_type = available_type
                        break

                if hand_type is None:
                    ui.display_error(f"Unknown hand type: '{hand_type_input}'. Use 'filters' to see available types.")
                    input("\nPress Enter to continue...")
                    continue

                # Toggle the filter
                deck_idx = deck_num - 1
                enabled = ui.toggle_filter(deck_idx, hand_type)

                # Show result
                status = f"{ui.GREEN}enabled{ui.RESET}" if enabled else f"{ui.GRAY}disabled{ui.RESET}"
                print(f"\n  {ui.CYAN}{ui.BOLD}[FILTER TOGGLED]{ui.RESET}")
                print(f"  {ui.GRAY}Deck {deck_num} - {hand_type}: {status}{ui.RESET}\n")
                input("Press Enter to continue...")
                continue

            except (ValueError, IndexError) as e:
                ui.display_error(f"Error toggling filter - {e}")
                input("\nPress Enter to continue...")
                continue

        # Handle discard command - accepts "d123", "d 123", "discard 123"
        if user_input.startswith("discard") or (user_input.startswith("d") and not user_input.startswith("d ")):
            # Avoid conflicting with "deck" or other "d" commands - only trigger if d followed by number
            if user_input.startswith("d") and len(user_input) > 1 and not user_input[1].isdigit() and user_input[1] != ' ':
                # Not a discard command, fall through
                pass
            else:
                # Extract card numbers after "discard" or "d"
                if user_input.startswith("discard"):
                    if len(user_input) > 7 and user_input[7] == ' ':
                        discard_input = user_input[8:].strip()  # "discard 123"
                    else:
                        discard_input = user_input[7:].strip()  # "discard123"
                elif user_input.startswith("d"):
                    if len(user_input) > 1 and user_input[1] == ' ':
                        discard_input = user_input[2:].strip()  # "d 123"
                    else:
                        discard_input = user_input[1:].strip()  # "d123"

                # Skip if it's just "d" or "discard" with no cards
                if not discard_input:
                    ui.display_error("Invalid discard. Enter card numbers (e.g., 'd123' or 'd 10 11')")
                    input("\nPress Enter to continue...")
                    continue

                parsed = parse_card_selection(discard_input, game)

                if parsed is None:
                    ui.display_error("Invalid discard. Enter 1-5 cards from ONE deck (e.g., 'd123' or 'd 10 11')")
                    input("\nPress Enter to continue...")
                    continue

                deck_index, card_indices, num_cards = parsed

                # Validate 1-5 cards
                if num_cards < 1 or num_cards > 5:
                    ui.display_error(f"Can only discard 1-5 cards (you selected {num_cards})")
                    input("\nPress Enter to continue...")
                    continue

                try:
                    result = game.discard_cards(deck_index, card_indices)

                    if result["success"]:
                        print(f"\n  {ui.YELLOW}{ui.BOLD}[DISCARDED!]{ui.RESET}")
                        print(f"  {ui.GRAY}Discarded {result['num_cards']} card{'s' if result['num_cards'] > 1 else ''} from Deck {deck_index + 1}{ui.RESET}\n")
                        input("Press Enter to continue...")
                    else:
                        ui.display_error(result["error"])
                        input("\nPress Enter to continue...")

                except (ValueError, IndexError) as e:
                    ui.display_error(f"Error discarding cards - {e}")
                    input("\nPress Enter to continue...")

                continue

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
                ui.display_error("Invalid trade. Enter 1 card number (e.g., 't1' or 't 10')")
                input("\nPress Enter to continue...")
                continue

            source_deck, card_indices, num_cards = parsed

            # GDD v6.1: Only 1 card per trade
            if num_cards != 1:
                ui.display_error(f"Can only trade 1 card at a time (GDD v6.1). You selected {num_cards} cards.")
                input("\nPress Enter to continue...")
                continue

            # Determine target deck (simple: trade to opposite deck)
            target_deck = 1 if source_deck == 0 else 0

            try:
                result = game.trade_card(source_deck, target_deck, card_indices[0])

                if result["success"]:
                    ui.display_trade_result(1, source_deck)
                    input("\nPress Enter to continue...")
                else:
                    ui.display_error(result["error"])
                    input("\nPress Enter to continue...")

            except (ValueError, IndexError) as e:
                ui.display_error(f"Error trading card - {e}")
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

        # Validate 1-5 cards (GDD v6.1 4-7)
        if num_cards < 1 or num_cards > 5:
            ui.display_error(f"Can only play 1-5 cards per hand (you selected {num_cards})")
            input("\nPress Enter to continue...")
            continue

        try:
            result = game.play_hand(deck_index, card_indices)

            if result["success"]:
                hand = result["hand"]
                ui.display_hand_result(hand)

                # GDD 4-6: Check if quota reached (round ends immediately)
                current_score = game.calculate_round_score()
                quota = game.config.round_quotas[game.state.current_round - 1]

                if current_score >= quota:
                    print(f"  {ui.GREEN}{ui.BOLD}[QUOTA REACHED!]{ui.RESET}")
                    print(f"  {ui.GRAY}Score: {current_score:,} / {quota:,}{ui.RESET}")
                    print(f"  {ui.GRAY}Round ending automatically (GDD 4-6)...{ui.RESET}\n")
                    input("Press Enter to continue...")
                    break  # End round immediately

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
        print(f"{ui.YELLOW}{ui.BOLD}  TWIN HANDS{ui.RESET} {ui.GRAY}|{ui.RESET} {ui.CYAN}GDD v6.1 (Trading + Deckbuilder){ui.RESET}")
        print(f"{ui.BOLD}{'='*70}{ui.RESET}\n")
        print(f"  {ui.BOLD}Goal:{ui.RESET} Play poker hands from 2 decks to beat the quota!\n")
        print(f"  {ui.BOLD}Rules (GDD v6.1):{ui.RESET}")
        print(f"    • Hand tokens: {ui.CYAN}UNLIMITED{ui.RESET} (max 2 hands per deck)")
        print(f"    • 2 trade tokens per round")
        print(f"    • 3 discard tokens per round (not yet implemented)")
        print(f"    • Play 1-5 cards to form poker hands")
        print(f"    • Trade 1 card at a time between decks")
        print(f"    • Beat Round 1 quota: {ui.CYAN}300 points{ui.RESET}\n")
        print(f"  {ui.BOLD}How to Play:{ui.RESET}")
        print(f"    • Cards numbered {ui.CYAN}1-7{ui.RESET} (Deck 1), {ui.CYAN}8-14{ui.RESET} (Deck 2)")
        print(f"    • After trading: decks can grow to 8, 9+ cards")
        print(f"    • Play 1-5 cards: {ui.CYAN}12345{ui.RESET} or {ui.CYAN}10 11 12{ui.RESET} (spaces for 10+)")
        print(f"    • Trade 1 card: {ui.CYAN}t1{ui.RESET} or {ui.CYAN}t 10{ui.RESET} (goes to opposite deck)")
        print(f"    • End round: {ui.CYAN}end{ui.RESET}\n")
        print(f"{ui.BOLD}{'='*70}{ui.RESET}\n")

        input("Press Enter to start...")

    # Play round
    play_round(game, ui)

    # Goodbye
    print(f"\n{ui.BOLD}Thanks for playing Twin Hands!{ui.RESET}")
    print(f"{ui.GRAY}GDD v6.1 prototype: Trading + Deckbuilder model implemented{ui.RESET}")
    print(f"{ui.GRAY}Coming soon: Discard system, Hand highlighting, Jokers, Shop, 8-round progression!{ui.RESET}\n")


if __name__ == "__main__":
    main()
