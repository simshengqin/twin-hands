"""
Integration tests for UI and game state synchronization.

Ensures that what the player sees in the UI matches what actually happens
in the game state (WYSIWYG principle).
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.card_resource import CardResource
from src.ui.terminal_ui import TerminalUI


def test_displayed_cards_match_selected_cards():
    """
    Test that cards shown to player are the cards actually played.

    Scenario:
    1. UI sorts cards for better UX: [9♣, A♦, K♥, 3♠]
    2. Player selects first 2 cards (positions [1][2])
    3. Should play 9♣ and A♦ (what player sees)
    4. Should keep K♥ and 3♠ (what player didn't select)
    """
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)

    game.start_game()

    # Get initial deck state
    deck = game.state.decks[0]
    original_cards = deck.visible_cards.copy()

    print(f"\nOriginal cards (unsorted): {[f'{c.rank}{c.suit[0].upper()}' for c in original_cards]}")

    # Sort cards (what UI does)
    ui.display_decks()  # This now sorts visible_cards in-place

    sorted_cards = deck.visible_cards.copy()
    print(f"Sorted cards (displayed): {[f'{c.rank}{c.suit[0].upper()}' for c in sorted_cards]}")

    # Player selects first 2 cards from sorted display
    card_1 = sorted_cards[0]  # Will play
    card_2 = sorted_cards[1]  # Will play
    card_3 = sorted_cards[2]  # Should stay
    card_4 = sorted_cards[3]  # Should stay

    print(f"\nPlayer intends to play: {card_1.rank}{card_1.suit[0].upper()}, "
          f"{card_2.rank}{card_2.suit[0].upper()}")
    print(f"Should keep: {card_3.rank}{card_3.suit[0].upper()}, "
          f"{card_4.rank}{card_4.suit[0].upper()}")

    # Play hand with indices 0, 1 (first two cards in sorted display)
    result = game.play_hand(deck_index=0, card_indices=[0, 1])

    assert result["success"] == True

    # Check that the CORRECT cards were played
    played_cards = result["hand"].cards
    print(f"Actually played: {[f'{c.rank}{c.suit[0].upper()}' for c in played_cards]}")

    # These should match what the player intended to play
    assert card_1.rank == played_cards[0].rank
    assert card_1.suit == played_cards[0].suit
    assert card_2.rank == played_cards[1].rank
    assert card_2.suit == played_cards[1].suit

    # Check that cards 3 and 4 are still in the deck (not removed by mistake)
    remaining = deck.visible_cards
    assert card_3 in remaining, f"Card 3 ({card_3.rank}{card_3.suit}) should still be there!"
    assert card_4 in remaining, f"Card 4 ({card_4.rank}{card_4.suit}) should still be there!"

    # And cards 1 and 2 should be gone
    assert card_1 not in remaining, f"Card 1 ({card_1.rank}{card_1.suit}) should be removed!"
    assert card_2 not in remaining, f"Card 2 ({card_2.rank}{card_2.suit}) should be removed!"

    print("\n✅ Correct cards played AND correct cards kept!")


def test_display_sorting_is_stable():
    """
    Test that UI sorting is deterministic and stable.

    Multiple displays should produce the same card order.
    """
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)

    game.start_game()

    # Display multiple times
    ui.display_decks()
    first_order = [f"{c.rank}{c.suit}" for c in game.state.decks[0].visible_cards]

    ui.display_decks()
    second_order = [f"{c.rank}{c.suit}" for c in game.state.decks[0].visible_cards]

    # Should be identical
    assert first_order == second_order

    print(f"\n✅ Sorting is stable: {first_order}")


if __name__ == "__main__":
    test_displayed_cards_match_selected_cards()
    test_display_sorting_is_stable()
