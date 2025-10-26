"""
Integration tests for trading + playing workflow.

Tests the interaction between TradeManager and GameManager,
especially with dynamic card indexing after deck sizes change.
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.ui.terminal_ui import TerminalUI


def test_trade_then_play_from_enlarged_deck():
    """
    CRITICAL: Test dynamic card indexing after trading.

    This test catches the bug where card indices weren't updated
    after trading enlarged a deck from 4 to 8 cards.

    Scenario:
    1. Trade 4 cards from Deck 1 → Deck 2
    2. Deck 2 now has 8 cards (was 4, now 8)
    3. Play cards from Deck 2 using indices for the new cards
    4. Verify correct cards are played (not "mixed deck" error)
    """
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Snapshot Deck 2 before trading
    deck_2_before = game.state.decks[1].visible_cards.copy()
    assert len(deck_2_before) == 4, "Deck 2 should start with 4 cards"

    # Trade 4 cards from Deck 1 → Deck 2
    result = game.trade_cards(source_deck=0, card_indices=[0, 1, 2, 3])
    assert result["success"] == True, "Trade should succeed"

    # Deck 2 should now have 8 cards (4 original + 4 traded)
    deck_2_after_trade = game.state.decks[1].visible_cards
    assert len(deck_2_after_trade) == 8, "Deck 2 should have 8 cards after trade"

    # Now play 4 cards from Deck 2
    # If indexing is broken, this will fail with "mixed deck" error
    # Because it would think indices 5-8 are valid but 9+ are not

    # Sort cards for display (simulating UI)
    ui.display_decks()

    # Try to play the last 4 cards from Deck 2 (indices 4-7 in deck, displayed as positions 9-12)
    # In the UI, these would be shown as [9][10][11][12]
    # In the deck, they're at indices [4][5][6][7]
    result = game.play_hand(deck_index=1, card_indices=[4, 5, 6, 7])

    assert result["success"] == True, "Should be able to play from enlarged deck"
    assert len(result["hand"].cards) == 4, "Should play 4 cards"

    # Deck 2 should now have 8 cards again (4 remaining + 4 drawn)
    assert len(game.state.decks[1].visible_cards) == 8, "Deck should refill to 8 (max was 8)"


def test_trade_multiple_times_then_play():
    """
    Test trading multiple times, then playing from the receiving deck.
    """
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Trade 2 cards from Deck 1 → Deck 2
    game.trade_cards(source_deck=0, card_indices=[0, 1])
    assert len(game.state.decks[1].visible_cards) == 6  # 4 + 2

    # Trade 2 more cards from Deck 1 → Deck 2
    game.trade_cards(source_deck=0, card_indices=[0, 1])
    assert len(game.state.decks[1].visible_cards) == 8  # 4 + 2 + 2

    # Display to sort
    ui.display_decks()

    # Play from Deck 2 (should work with all 8 cards)
    result = game.play_hand(deck_index=1, card_indices=[0, 1, 2, 3])
    assert result["success"] == True

    # Deck 2 should still have 8 cards (4 played, 4 drawn)
    assert len(game.state.decks[1].visible_cards) == 8


def test_trade_both_directions():
    """
    Test trading in both directions, then playing from both decks.
    """
    config = TwinHandsConfig()
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Trade 2 cards: Deck 1 → Deck 2
    game.trade_cards(source_deck=0, card_indices=[0, 1])

    # Trade 2 cards: Deck 2 → Deck 1
    game.trade_cards(source_deck=1, card_indices=[0, 1])

    # Both decks should have 6 cards (4 - 2 + 4 drawn, then + 2 from trade)
    # Actually: giving deck draws immediately, so both stay at 4
    # Then receiving deck gets +2
    # So: Deck 1: 4 - 2 (gave) + 2 (drew) + 2 (received) = 6
    #     Deck 2: 4 + 2 (received) - 2 (gave) + 2 (drew) = 6
    assert len(game.state.decks[0].visible_cards) == 6
    assert len(game.state.decks[1].visible_cards) == 6

    # Display to sort
    ui.display_decks()

    # Play from both decks
    result1 = game.play_hand(deck_index=0, card_indices=[0, 1])
    assert result1["success"] == True

    result2 = game.play_hand(deck_index=1, card_indices=[0, 1])
    assert result2["success"] == True
