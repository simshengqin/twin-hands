#!/usr/bin/env python3
# Test auto-freeze priority system

import sys
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from game_state import GameStateManager
from ui import TerminalUI
from config import Config
from models import Card

def test_aligned_pair():
    """Test Priority 1: Highest pair in same row/column"""
    print("=" * 60)
    print("TEST 1: Aligned Pair (Priority 1)")
    print("=" * 60)

    config = Config()
    game = GameStateManager(config)

    # Manually set up grid with pair of Aces in same row
    game.state.current_round = 1
    game.state.grid[0][0].set_card(Card("A", "H"))
    game.state.grid[0][2].set_card(Card("A", "D"))  # Same row
    game.state.grid[1][1].set_card(Card("K", "S"))
    game.state.grid[1][2].set_card(Card("K", "C"))  # Kings same row (lower rank)

    # Fill rest with random cards
    game.state.grid[2][0].set_card(Card("7", "H"))
    game.state.grid[3][0].set_card(Card("3", "D"))
    game.state.grid[4][0].set_card(Card("2", "C"))

    game._auto_freeze_highest_pair()

    ui = TerminalUI(game)
    ui.print_grid()
    ui.print_auto_freeze_message()

    print("Expected: Pair of Aces (same row)")
    print()

def test_suited_cards():
    """Test Priority 2: Two highest cards of same suit"""
    print("=" * 60)
    print("TEST 2: Suited Cards (Priority 2)")
    print("=" * 60)

    config = Config()
    game = GameStateManager(config)

    # Manually set up grid with no aligned pairs, but suited cards
    game.state.current_round = 1
    game.state.grid[0][0].set_card(Card("A", "H"))
    game.state.grid[2][3].set_card(Card("K", "H"))  # Same suit, different row/col
    game.state.grid[1][1].set_card(Card("Q", "D"))
    game.state.grid[3][2].set_card(Card("J", "D"))  # Same suit, lower value

    # Fill rest with random cards
    game.state.grid[2][0].set_card(Card("7", "C"))
    game.state.grid[3][0].set_card(Card("3", "S"))
    game.state.grid[4][0].set_card(Card("2", "C"))

    game._auto_freeze_highest_pair()

    ui = TerminalUI(game)
    ui.print_grid()
    ui.print_auto_freeze_message()

    print("Expected: A♥ K♥ (same suit)")
    print()

def test_no_freeze():
    """Test Priority 3: Don't freeze anything"""
    print("=" * 60)
    print("TEST 3: No Freeze (Priority 3)")
    print("=" * 60)

    config = Config()
    game = GameStateManager(config)

    # Manually set up grid with only 4 cards, all different suits (no pairs, no suit matches)
    game.state.current_round = 1
    game.state.grid[0][0].set_card(Card("A", "H"))
    game.state.grid[1][1].set_card(Card("K", "D"))
    game.state.grid[2][2].set_card(Card("Q", "C"))
    game.state.grid[3][3].set_card(Card("J", "S"))
    # Only 4 cards, all different suits - should not freeze anything

    game._auto_freeze_highest_pair()

    ui = TerminalUI(game)
    ui.print_grid()
    ui.print_auto_freeze_message()

    print("Expected: No freeze")
    print()

# Run tests
test_aligned_pair()
test_suited_cards()
test_no_freeze()

print("=" * 60)
print("All tests complete!")
print("=" * 60)
