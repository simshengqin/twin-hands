"""
Integration tests for trading + playing workflow (GDD v6.1).

Tests the interaction between TradeManager and GameManager,
especially with dynamic card indexing after deck sizes change.

GDD v6.1: One-directional trading, 1 card at a time, receiving deck accumulates.
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig
from src.ui.terminal_ui import TerminalUI


def test_trade_then_play_from_enlarged_deck():
    """
    CRITICAL: Test dynamic card indexing after trading.

    GDD v6.1 Scenario:
    1. Trade 1 card from Deck 0 → Deck 1
    2. Deck 1 now has 8 cards (was 7, now 8)
    3. Play cards from Deck 1 using indices for the new cards
    4. Verify correct cards are played
    """
    config = TwinHandsConfig(
        trade_tokens_per_round=2,
        visible_cards_per_deck=7
    )
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Snapshot Deck 1 before trading
    deck_1_before = game.state.decks[1].visible_cards.copy()
    assert len(deck_1_before) == config.visible_cards_per_deck, "Deck 1 should start with 7 cards"

    # Trade 1 card from Deck 0 → Deck 1
    result = game.trade_card(source_deck=0, target_deck=1, card_index=0)
    assert result["success"] == True, "Trade should succeed"

    # Deck 1 should now have 8 cards (7 original + 1 traded)
    deck_1_after_trade = game.state.decks[1].visible_cards
    assert len(deck_1_after_trade) == 8, "Deck 1 should have 8 cards after trade"

    # Now play cards from Deck 1
    # If indexing is broken, this will fail

    # Sort cards for display (simulating UI)
    ui.display_decks()

    # Try to play the last 4 cards from Deck 1 (indices 4-7)
    result = game.play_hand(deck_index=1, card_indices=[4, 5, 6, 7])

    assert result["success"] == True, "Should be able to play from enlarged deck"
    assert len(result["hand"].cards) == 4, "Should play 4 cards"

    # Deck 1 should refill to 8 cards (4 remaining + 4 drawn)
    assert len(game.state.decks[1].visible_cards) == 8, "Deck should refill to 8"


def test_trade_multiple_times_then_play():
    """
    GDD v6.1: Test trading multiple times (1 card each), then playing from receiving deck.
    """
    config = TwinHandsConfig(
        trade_tokens_per_round=2,
        visible_cards_per_deck=7
    )
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Trade 1 card from Deck 0 → Deck 1
    game.trade_card(source_deck=0, target_deck=1, card_index=0)
    assert len(game.state.decks[1].visible_cards) == 8  # 7 + 1

    # Trade 1 more card from Deck 0 → Deck 1
    game.trade_card(source_deck=0, target_deck=1, card_index=0)
    assert len(game.state.decks[1].visible_cards) == 9  # 7 + 1 + 1

    # Display to sort
    ui.display_decks()

    # Play from Deck 1 (should work with all 9 cards)
    result = game.play_hand(deck_index=1, card_indices=[0, 1, 2, 3])
    assert result["success"] == True

    # Deck 1 should refill to 9 cards (5 remaining + 4 drawn)
    assert len(game.state.decks[1].visible_cards) == 9


def test_trade_both_directions():
    """
    GDD v6.1: Test trading in both directions, then playing from both decks.
    """
    config = TwinHandsConfig(
        trade_tokens_per_round=2,
        visible_cards_per_deck=7
    )
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Trade 1 card: Deck 0 → Deck 1
    game.trade_card(source_deck=0, target_deck=1, card_index=0)

    # Trade 1 card: Deck 1 → Deck 0
    game.trade_card(source_deck=1, target_deck=0, card_index=0)

    # Deck 0: Gave 1 (redrew 1, stayed at 7), then received 1 = 8 cards
    # Deck 1: Received 1 (8 cards), then gave 1 (redrew 1, stayed at 8)
    assert len(game.state.decks[0].visible_cards) == 8
    assert len(game.state.decks[1].visible_cards) == 8

    # Display to sort
    ui.display_decks()

    # Play from both decks
    result1 = game.play_hand(deck_index=0, card_indices=[0, 1])
    assert result1["success"] == True

    result2 = game.play_hand(deck_index=1, card_indices=[0, 1])
    assert result2["success"] == True
