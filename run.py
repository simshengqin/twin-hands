"""
Twin Hands - Terminal UI (PHASE A: Minimal Playable)
Balatro-inspired UI with clean, information-dense layout.
Run this to play the game!
"""

from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.ui.terminal_ui import TerminalUI


def play_round(game: GameManager, ui: TerminalUI):
    """Play one round with Balatro-style UI."""
    game.start_game()

    while game.state.hand_tokens > 0:
        # Display full state (all-in-one screen like Balatro)
        ui.display_full_state()

        # Get player input
        user_input = ui.prompt_input()

        if user_input == "end":
            break

        # Parse play command
        if user_input.startswith("play"):
            parts = user_input.split()
            if len(parts) < 3:
                ui.display_error("Invalid command. Use 'play <deck> <card_indices>'")
                input("\nPress Enter to continue...")
                continue

            try:
                deck_num = int(parts[1])  # User enters 1 or 2
                deck_index = deck_num - 1  # Convert to 0-indexed
                card_indices = [int(x) for x in parts[2:]]

                result = game.play_hand(deck_index, card_indices)

                if result["success"]:
                    hand = result["hand"]
                    ui.display_hand_result(hand)
                    input("\nPress Enter to continue...")
                else:
                    ui.display_error(result["error"])
                    input("\nPress Enter to continue...")

            except (ValueError, IndexError) as e:
                ui.display_error(f"Invalid input - {e}")
                input("\nPress Enter to continue...")
        else:
            ui.display_error("Unknown command. Use 'play' or 'end'.")
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
    print(f"{ui.YELLOW}{ui.BOLD}  TWIN HANDS{ui.RESET} {ui.GRAY}│{ui.RESET} {ui.CYAN}Phase A: Minimal Playable{ui.RESET}")
    print(f"{ui.BOLD}{'='*70}{ui.RESET}\n")
    print(f"  {ui.BOLD}Goal:{ui.RESET} Play poker hands from 2 decks to beat the quota!\n")
    print(f"  {ui.BOLD}Rules:{ui.RESET}")
    print(f"    • 4 hand tokens per round")
    print(f"    • Max 2 hands per deck")
    print(f"    • Play 1-4 cards to form poker hands")
    print(f"    • Beat Round 1 quota: {ui.CYAN}300 points{ui.RESET}\n")
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
