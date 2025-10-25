"""
AI Demo: Show NormalAI and SmartAI decisions on a fresh grid and shop.
Run: python ai_simulation/scripts/demo.py
"""

import os
import sys
import io

# Ensure project root is on sys.path when running as a script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from ai_simulation import NormalAIManager, SmartAIManager
from src.resources.game_config_resource import GameConfigResource
from src.managers.game_manager import GameManager
from src.managers.joker_manager import JokerManager
from src.managers.shop_manager import ShopManager
from src.utils.joker_loader import JokerLoader


def print_grid(state):
    rows = state.config.grid_rows
    cols = state.config.grid_cols
    for r in range(rows):
        row_str = []
        for c in range(cols):
            card = state.grid[r][c].card
            row_str.append(card.get_display_string())
        print(" ".join(row_str))


def main():
    config = GameConfigResource()
    joker_manager = JokerManager(max_slots=5)
    game_manager = GameManager(config, joker_manager)

    # Start a new round to deal a grid
    game_manager.start_new_round()

    print("Initial Grid:")
    print_grid(game_manager.state)
    print()

    # Load jokers and open a shop
    print("Loading jokers and opening shop...")
    available = JokerLoader.load_p0_jokers()
    shop = ShopManager(game_manager.state, joker_manager, available)
    shop.open_shop()
    display = shop.get_shop_display()
    reroll_cost = shop.get_reroll_cost()

    print("Shop Inventory:")
    for item in display:
        if item['joker']:
            print(f"  [{item['index']}] {item['name']} - ${item['cost']} :: {item['description']}")
        else:
            print(f"  [{item['index']}] [EMPTY]")
    print()

    # Normal AI
    norm_ai = NormalAIManager(game_manager.state, config, joker_manager)
    n_freezes = norm_ai.recommend_freezes(max_to_freeze=config.max_freezes)
    n_shop = norm_ai.recommend_shop_action(display, reroll_cost)

    print("NormalAI recommendations:")
    print(f"  Freezes: {n_freezes}")
    print(f"  Shop: {n_shop}")
    print()

    # Smart AI (use fewer samples for demo speed)
    smart_ai = SmartAIManager(game_manager.state, config, joker_manager)
    s_freezes = smart_ai.recommend_freezes(max_to_freeze=config.max_freezes, samples=60)
    s_shop = smart_ai.recommend_shop_action(display, reroll_cost)

    print("SmartAI recommendations:")
    print(f"  Freezes: {s_freezes}")
    print(f"  Shop: {s_shop}")
    print(f"  Why: {smart_ai.explain_last_decision()}")


if __name__ == "__main__":
    main()
