#!/usr/bin/env python3
"""
Test shop system manually.
Verifies shop inventory generation, buying, selling, and rerolls.
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.managers.shop_manager import ShopManager
from src.managers.joker_manager import JokerManager
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource
from src.utils.joker_loader import JokerLoader


def test_shop_system():
    """Test shop system with game."""
    print("=" * 70)
    print("SHOP SYSTEM TEST")
    print("=" * 70)

    # Load P0 jokers
    print("\n📁 Loading P0 jokers from CSV...")
    available_jokers = JokerLoader.load_p0_jokers()
    print(f"✓ Loaded {len(available_jokers)} jokers")

    # Create game
    config = GameConfigResource()
    game = GameManager(config)
    game.start_new_round()

    # Create joker manager
    joker_manager = JokerManager(max_slots=5)

    # Create shop manager
    shop_manager = ShopManager(game.state, joker_manager, available_jokers)

    # Simulate earning money (normally from unutilized hands)
    print(f"\n💰 Starting money: ${game.state.money}")
    game.state.add_money(20)  # Give player some money to test with
    print(f"💰 After bonus: ${game.state.money}")

    # Open shop
    print("\n🏪 Opening shop...")
    shop_manager.open_shop()

    # Display inventory
    print("\n" + "=" * 70)
    print("SHOP INVENTORY")
    print("=" * 70)

    inventory = shop_manager.get_shop_display()
    for item in inventory:
        if item['joker']:
            print(f"\n{item['index'] + 1}. {item['name']} - ${item['cost']} [{item['rarity']}]")
            print(f"   {item['description']}")
        else:
            print(f"\n{item['index'] + 1}. {item['name']}")

    # Test buying
    print("\n" + "=" * 70)
    print("BUYING TEST")
    print("=" * 70)

    if inventory[0]['joker']:
        print(f"\n💵 Attempting to buy slot 1...")
        success, msg = shop_manager.buy_joker(0)
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money remaining: ${game.state.money}")
        print(f"   Active jokers: {joker_manager.get_joker_count()}")

    # Test reroll
    print("\n" + "=" * 70)
    print("REROLL TEST")
    print("=" * 70)

    print(f"\n🔄 Reroll cost: ${shop_manager.get_reroll_cost()}")
    success, msg = shop_manager.reroll_shop()
    print(f"   {'✓' if success else '✗'} {msg}")
    print(f"   Money remaining: ${game.state.money}")

    # Show new inventory
    print("\n📦 New inventory after reroll:")
    inventory = shop_manager.get_shop_display()
    for item in inventory:
        if item['joker']:
            print(f"   {item['index'] + 1}. {item['name']} - ${item['cost']}")
        else:
            print(f"   {item['index'] + 1}. {item['name']}")

    # Test selling
    if joker_manager.get_joker_count() > 0:
        print("\n" + "=" * 70)
        print("SELLING TEST")
        print("=" * 70)

        joker_to_sell = joker_manager.active_jokers[0]
        print(f"\n💸 Selling {joker_to_sell.name}...")
        success, msg = shop_manager.sell_joker(0)
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money after sell: ${game.state.money}")
        print(f"   Active jokers: {joker_manager.get_joker_count()}")

    # Test rarity distribution
    print("\n" + "=" * 70)
    print("RARITY DISTRIBUTION TEST (100 iterations)")
    print("=" * 70)

    rarity_counts = {'Common': 0, 'Uncommon': 0, 'Rare': 0}

    for _ in range(100):
        shop_manager.generate_inventory()
        for item in shop_manager.shop_inventory:
            if item:
                rarity_counts[item.rarity] = rarity_counts.get(item.rarity, 0) + 1

    total = sum(rarity_counts.values())
    print(f"\n📊 Results from {total} jokers generated:")
    for rarity, count in rarity_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"   {rarity}: {count} ({percentage:.1f}%)")

    print("\n" + "=" * 70)
    print("Test complete! ✓")
    print("=" * 70)


if __name__ == "__main__":
    test_shop_system()
