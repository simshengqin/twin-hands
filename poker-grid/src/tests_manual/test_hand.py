#!/usr/bin/env python3
# Quick test to simulate a single hand using the new architecture

import sys
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.resources.game_config_resource import GameConfigResource
from src.managers.game_manager import GameManager
from src.ui_adapter import UIAdapter
from src.ui.terminal_ui import TerminalUI

# Initialize new architecture
config = GameConfigResource()
game_manager = GameManager(config)
adapter = UIAdapter(game_manager)
ui = TerminalUI(adapter)

# Start the round
adapter.start_new_round()

print("Initial grid:")
ui.print_grid()
ui.print_auto_freeze_message()

# Play one hand
print("\n--- Playing hand ---")
adapter.play_hand()

# Score and update
current_score, row_hands, col_hands, top_lines = adapter.score_and_update()

print(f"\nHand {adapter.state.hands_taken} complete!")
ui.print_line_scores(row_hands, col_hands, current_score, top_lines)
print(f"Cumulative Score: {adapter.state.cumulative_score} chips")
print(f"Hands Remaining: {adapter.state.hands_left}")

print("\nGrid after hand:")
ui.print_grid(top_lines)
