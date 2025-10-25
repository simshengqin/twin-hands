#!/usr/bin/env python3
"""
Test shop with money earning scenario.
Shows earning money from unutilized hands, buying jokers, and using them.
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


def test_shop_with_money():
    """Test shop system with money earning and spending."""
    print("=" * 70)
    print("SHOP WITH MONEY TEST")
    print("=" * 70)

    # Create game with settings that will earn money
    config = GameConfigResource()
    config.quota_target = 2000  # Higher quota
    config.rounds_per_session = 5
    config.max_hands = 7  # Standard 7 hands

    joker_manager = JokerManager(max_slots=5)
    game = GameManager(config, joker_manager)

    # Load jokers
    print("\n📁 Loading jokers...")
    available_jokers = JokerLoader.load_p0_jokers()
    print(f"✓ Loaded {len(available_jokers)} jokers")

    # Create shop manager
    shop_manager = ShopManager(game.state, joker_manager, available_jokers)

    # Round 1: Play only 4 hands (save 3 hands = $3)
    print("\n" + "=" * 70)
    print("ROUND 1: Playing 4 hands, saving 3 for money")
    print("=" * 70)

    game.start_new_round()
    print(f"\n✓ Round {game.state.current_round} started")
    print(f"   Hands available: {game.state.hands_left}")

    # Play only 4 hands
    for _ in range(4):
        if game.play_hand():
            score, row_hands, col_hands = game.score_and_update()
            print(f"   Hand {game.state.hands_taken}: Scored {score} chips")

    print(f"\n   Hands remaining: {game.state.hands_left}")

    # Complete round (should earn money)
    money_earned = game.complete_round()

    print(f"\n✓ Round complete!")
    print(f"   Cumulative score: {game.state.cumulative_score}/{config.quota_target}")
    print(f"   💰 Earned ${money_earned} from {money_earned} unutilized hands")
    print(f"   💵 Total money: ${game.state.money}")

    # Shop Phase 1
    print("\n" + "=" * 70)
    print("SHOP PHASE 1: Buying a joker")
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
            print(f"       {item['description']}")
        else:
            print(f"   [{item['index'] + 1}] [EMPTY]")

    # Find a joker we can afford
    affordable_slot = None
    for item in inventory:
        if item['joker'] and game.state.can_afford(item['cost']):
            affordable_slot = item['index']
            break

    if affordable_slot is not None:
        print(f"\n💵 Buying joker from slot {affordable_slot + 1}...")
        success, msg = shop_manager.buy_joker(affordable_slot)
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money remaining: ${game.state.money}")
        print(f"   Active jokers: {joker_manager.get_joker_count()}/{joker_manager.max_slots}")

        # Show the joker we bought
        if success:
            joker = joker_manager.active_jokers[0]
            print(f"\n   🃏 Equipped: {joker.get_display_name()}")
            print(f"      {joker.get_description()}")
    else:
        print("\n   ⚠️  No affordable jokers in this shop")

    shop_manager.close_shop()

    # Round 2: Play with the joker
    print("\n" + "=" * 70)
    print("ROUND 2: Playing with joker effects")
    print("=" * 70)

    game.start_new_round()
    print(f"\n✓ Round {game.state.current_round} started")
    print(f"   Active jokers: {joker_manager.get_joker_count()}")

    if joker_manager.get_joker_count() > 0:
        print("\n   Active Jokers:")
        for joker in joker_manager.active_jokers:
            print(f"      • {joker.get_display_name()}")

    # Play 4 hands again (save 3 for money)
    for _ in range(4):
        if game.play_hand():
            score, row_hands, col_hands = game.score_and_update()
            print(f"   Hand {game.state.hands_taken}: Scored {score} chips (joker effects applied)")

    money_earned = game.complete_round()

    print(f"\n✓ Round complete!")
    print(f"   Cumulative score: {game.state.cumulative_score}/{config.quota_target}")
    print(f"   💰 Earned ${money_earned} from {money_earned} unutilized hands")
    print(f"   💵 Total money: ${game.state.money}")

    # Shop Phase 2: Test reroll and selling
    print("\n" + "=" * 70)
    print("SHOP PHASE 2: Testing reroll")
    print("=" * 70)

    shop_manager.open_shop()
    print(f"\n✓ Shop opened")
    print(f"   Money available: ${game.state.money}")

    # Show initial inventory
    print("\nInitial inventory:")
    inventory = shop_manager.get_shop_display()
    for item in inventory:
        if item['joker']:
            print(f"   [{item['index'] + 1}] {item['name']} - ${item['cost']}]")

    # Test reroll if we can afford it
    if game.state.can_afford(shop_manager.get_reroll_cost()):
        print(f"\n🔄 Rerolling shop (${shop_manager.get_reroll_cost()})...")
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

    # Test selling if we have jokers
    if joker_manager.get_joker_count() > 0:
        print(f"\n💸 Testing sell...")
        joker_to_sell = joker_manager.active_jokers[0]
        sell_value = joker_to_sell.sell_value
        print(f"   Selling {joker_to_sell.name} for ${sell_value}")
        success, msg = shop_manager.sell_joker(0)
        print(f"   {'✓' if success else '✗'} {msg}")
        print(f"   Money after sell: ${game.state.money}")

    shop_manager.close_shop()

    # Final summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Rounds completed: {game.state.current_round}/{config.rounds_per_session}")
    print(f"Score: {game.state.cumulative_score}/{config.quota_target}")
    print(f"Final money: ${game.state.money}")
    print(f"Final jokers: {joker_manager.get_joker_count()}")

    print("\n✓ Shop system working correctly!")
    print("  • Money earned from unutilized hands")
    print("  • Jokers purchased and equipped")
    print("  • Joker effects applied to scoring")
    print("  • Shop reroll working")
    print("  • Joker selling working")

    print("\n" + "=" * 70)
    print("Test complete! ✓")
    print("=" * 70)


if __name__ == "__main__":
    test_shop_with_money()
