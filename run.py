"""
Twin Hands - Terminal UI (PHASE A: Minimal Playable)
Run this to play the game!
"""

from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig


def display_deck(game: GameManager, deck_index: int):
    """Display visible cards for a deck."""
    cards = game.get_visible_cards(deck_index)
    print(f"\n  Deck {deck_index + 1} visible cards:")
    for i, card in enumerate(cards):
        print(f"    [{i}] {card}")


def display_game_state(game: GameManager):
    """Display current game state."""
    state_summary = game.get_game_state_summary()
    print("\n" + "="*60)
    print(f"ROUND {state_summary['round']}")
    print(f"Hand Tokens: {state_summary['hand_tokens']}")
    print(f"Hands played: Deck 1: {state_summary['hands_played_per_deck'][0]}/2, "
          f"Deck 2: {state_summary['hands_played_per_deck'][1]}/2")
    print(f"Current Score: {state_summary['current_score']}")
    print("="*60)


def play_round(game: GameManager):
    """Play one round."""
    print("\n\nSTARTING NEW ROUND!")
    game.start_game()

    while game.state.hand_tokens > 0:
        display_game_state(game)

        # Show both decks
        display_deck(game, 0)
        display_deck(game, 1)

        # Get player input
        print("\n  Enter command:")
        print("    - 'play <deck> <card_indices>' (e.g., 'play 1 0 1 2' to play cards 0,1,2 from deck 1)")
        print("    - 'end' to end round")

        user_input = input("\n  > ").strip()

        if user_input == "end":
            break

        # Parse play command
        if user_input.startswith("play"):
            parts = user_input.split()
            if len(parts) < 3:
                print("  ERROR: Invalid command. Use 'play <deck> <card_indices>'")
                continue

            try:
                deck_num = int(parts[1])  # User enters 1 or 2
                deck_index = deck_num - 1  # Convert to 0-indexed
                card_indices = [int(x) for x in parts[2:]]

                result = game.play_hand(deck_index, card_indices)

                if result["success"]:
                    hand = result["hand"]
                    print(f"\n  SUCCESS! You played: {hand.hand_type} ({hand.base_score} points)")
                else:
                    print(f"\n  ERROR: {result['error']}")

            except (ValueError, IndexError) as e:
                print(f"  ERROR: Invalid input - {e}")
        else:
            print("  ERROR: Unknown command. Use 'play' or 'end'.")

    # Round over
    display_game_state(game)
    final_score = game.calculate_round_score()
    print(f"\n\nROUND COMPLETE!")
    print(f"Final Score: {final_score}")

    # Check if beat quota (GDD 5-3)
    quota = game.config.round_quotas[0]  # Round 1 quota
    if final_score >= quota:
        print(f"SUCCESS! You beat the quota of {quota}!")
    else:
        print(f"FAILED! You needed {quota} but scored {final_score}.")


def main():
    """Main entry point."""
    print("="*60)
    print(" TWIN HANDS - PHASE A (Minimal Playable)")
    print("="*60)
    print("\nGoal: Play poker hands from 2 decks to beat the quota!")
    print("Rules:")
    print("  - 4 hand tokens per round")
    print("  - Max 2 hands per deck")
    print("  - Play 1-4 cards to form poker hands")
    print("  - Beat Round 1 quota: 300 points")
    print("\n")

    config = TwinHandsConfig()
    game = GameManager(config)

    play_round(game)

    print("\n\nThanks for playing Twin Hands PHASE A!")
    print("This is a minimal playable prototype.")
    print("Future: Trading, Jokers, Shop, 8-round progression!")


if __name__ == "__main__":
    main()
