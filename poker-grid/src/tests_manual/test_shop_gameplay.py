#!/usr/bin/env python3
"""
Test shop integration in actual gameplay (automated).
Simulates playing through a round to reach the shop.
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.managers.game_manager import GameManager
from src.managers.joker_manager import JokerManager
from src.managers.shop_manager import ShopManager
from src.resources.game_config_resource import GameConfigResource
from src.utils.joker_loader import JokerLoader


def test_shop_gameplay():
    """Test complete round-to-shop flow."""
    print("=" * 70)
    print("SHOP GAMEPLAY TEST")
    print("=" * 70)

    # Create game with easy win config (low quota)
    config = GameConfigResource()
    config.quota_target = 100  # Easy win
    config.rounds_per_session = 3
    config.max_hands = 3  # Fewer hands = more money from unutilized

    joker_manager = JokerManager(max_slots=5)
    game = GameManager(config, joker_manager)

    # Load jokers
    print("\n📁 Loading jokers...")
    available_jokers = JokerLoader.load_p0_jokers()
    print(f"✓ Loaded {len(available_jokers)} jokers")

    # Create shop manager
    shop_manager = ShopManager(game.state, joker_manager, available_jokers)

    # Simulate Round 1
    print("\n" + "=" * 70)
    print("ROUND 1: Playing through hands")
    print("=" * 70)

    game.start_new_round()
    print(f"\n✓ Round {game.state.current_round} started")
    print(f"   Money: ${game.state.money}")
    print(f"   Hands left: {game.state.hands_left}")

    # Play all hands (simulate)
    while game.state.hands_left > 0:
        if game.play_hand():
            score, row_hands, col_hands = game.score_and_update()
            print(f"   Hand {game.state.hands_taken}: Scored {score} chips")

    # Complete round (earns money from unutilized hands)
    money_earned = game.complete_round()

    print(f"\n✓ Round complete!")
    print(f"   Cumulative score: {game.state.cumulative_score}")
    print(f"   Money earned from unutilized hands: ${money_earned}")
    print(f"   Total money: ${game.state.money}")

    # Open shop
    print("\n" + "=" * 70)
    print("SHOP PHASE")
    print("=" * 70)

    shop_manager.open_shop()
    print(f"\n✓ Shop opened")
    print(f"   Money available: ${game.state.money}")
    print(f"   Reroll cost: ${shop_manager.get_reroll_cost()}")

    # Display inventory
    print("\nShop Inventory:")
    inventory = shop_manager.get_shop_display()
    for item in inventory:
        if item['joker']:
            print(f"   [{item['index'] + 1}] {item['name']} - ${item['cost']} [{item['rarity']}]")
        else:
            print(f"   [{item['index'] + 1}] [EMPTY]")

    # Display active jokers
    print(f"\nActive Jokers: {joker_manager.get_joker_count()}/{joker_manager.max_slots}")

    # Test buying if we have money
    if game.state.money > 0 and inventory[0]['joker']:
        print(f"\n💵 Testing buy...")
        joker_to_buy = inventory[0]['joker']
        cost = inventory[0]['cost']

        if game.state.can_afford(cost):
            success, msg = shop_manager.buy_joker(0)
            print(f"   {'✓' if success else '✗'} {msg}")
            print(f"   Money remaining: ${game.state.money}")
            print(f"   Active jokers: {joker_manager.get_joker_count()}")
        else:
            print(f"   ✗ Not enough money (need ${cost}, have ${game.state.money})")

    # Test reroll if we have money
    if game.state.money >= shop_manager.get_reroll_cost():
        print(f"\n🔄 Testing reroll...")
        success, msg = shop_manager.reroll_shop()
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money remaining: ${game.state.money}")
        print(f"   New reroll cost: ${shop_manager.get_reroll_cost()}")

        # Show new inventory
        inventory = shop_manager.get_shop_display()
        print("\nNew inventory:")
        for item in inventory:
            if item['joker']:
                print(f"   [{item['index'] + 1}] {item['name']} - ${item['cost']}]")
            else:
                print(f"   [{item['index'] + 1}] [EMPTY]")

    # Test selling if we have a joker
    if joker_manager.get_joker_count() > 0:
        print(f"\n💸 Testing sell...")
        joker_to_sell = joker_manager.active_jokers[0]
        success, msg = shop_manager.sell_joker(0)
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money after sell: ${game.state.money}")
        print(f"   Active jokers: {joker_manager.get_joker_count()}")

    # Close shop
    shop_manager.close_shop()
    print(f"\n✓ Shop closed")

    # Simulate Round 2 with jokers
    print("\n" + "=" * 70)
    print("ROUND 2: Testing joker effects in gameplay")
    print("=" * 70)

    game.start_new_round()
    print(f"\n✓ Round {game.state.current_round} started")
    print(f"   Active jokers: {joker_manager.get_joker_count()}")

    # Play hands with joker effects
    while game.state.hands_left > 0:
        if game.play_hand():
            # Score and update (joker effects applied automatically by ScoreManager)
            score, row_hands, col_hands = game.score_and_update()
            print(f"   Hand {game.state.hands_taken}: Scored {score} chips (with joker effects)")

    money_earned = game.complete_round()

    print(f"\n✓ Round complete!")
    print(f"   Cumulative score: {game.state.cumulative_score}")
    print(f"   Money earned: ${money_earned}")
    print(f"   Total money: ${game.state.money}")

    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Rounds completed: {game.state.current_round}/{config.rounds_per_session}")
    print(f"Final score: {game.state.cumulative_score}/{config.quota_target}")
    print(f"Final money: ${game.state.money}")
    print(f"Final jokers: {joker_manager.get_joker_count()}")

    if game.is_quota_met():
        print("\n🎉 QUOTA MET!")
    else:
        print(f"\nNot yet at quota (need {config.quota_target - game.state.cumulative_score} more)")

    print("\n" + "=" * 70)
    print("Test complete! ✓")
    print("=" * 70)


if __name__ == "__main__":
    test_shop_gameplay()
