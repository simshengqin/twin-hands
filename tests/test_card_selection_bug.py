"""
Test for card selection bug where sorted display doesn't match actual indices.

Bug: UI sorts cards for display, but GameManager operates on unsorted list.
Result: Player selects cards by sorted position, but wrong cards get removed.
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.resources.card_resource import CardResource
from src.ui.terminal_ui import TerminalUI


def test_card_selection_matches_display():
    """
    CRITICAL BUG TEST: Cards displayed should match cards selected.

    Scenario:
    1. Deck has cards: [K♥, 3♠, 9♣, A♦] (unsorted)
    2. UI sorts them: [9♣, A♦, K♥, 3♠] (displayed as [1][2][3][4])
    3. Player types '12' intending to play 9♣ and A♦
    4. Should remove 9♣ and A♦, NOT K♥ and 3♠!
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
    first_card_before = sorted_cards[0]
    second_card_before = sorted_cards[1]

    print(f"\nPlayer intends to select: {first_card_before.rank}{first_card_before.suit[0].upper()}, "
          f"{second_card_before.rank}{second_card_before.suit[0].upper()}")

    # Play hand with indices 0, 1 (first two cards in sorted display)
    result = game.play_hand(deck_index=0, card_indices=[0, 1])

    assert result["success"] == True

    # Check that the CORRECT cards were played
    played_cards = result["hand"].cards
    print(f"Actually played: {[f'{c.rank}{c.suit[0].upper()}' for c in played_cards]}")

    # These should match what the player intended
    assert first_card_before.rank == played_cards[0].rank
    assert first_card_before.suit == played_cards[0].suit
    assert second_card_before.rank == played_cards[1].rank
    assert second_card_before.suit == played_cards[1].suit

    print("\n✅ BUG FIXED: Selected cards match displayed cards!")


def test_card_sorting_is_stable():
    """
    Ensure sorting is consistent across multiple displays.
    Cards should stay in the same order.
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
    test_card_selection_matches_display()
    test_card_sorting_is_stable()
