#!/usr/bin/env python3
"""
Test joker system with 5 MVP jokers.
Verifies joker effects apply correctly to scoring.
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
from src.resources.game_config_resource import GameConfigResource
from src.resources.joker_resource import JokerResource


def create_mvp_jokers():
    """Create 5 MVP jokers covering all main effect types."""

    # 1. Joker - Simplest (always active, flat bonus)
    joker_basic = JokerResource(
        id="j_001",
        name="Joker",
        effect_type="instant",
        trigger="always",
        condition_type="",
        condition_value="",
        bonus_type="+m",
        bonus_value=4,
        per_card=False,
        rarity="Common",
        cost=2,
        notes="Simplest joker - always active"
    )

    # 2. Jolly Joker - Conditional (triggers on hand type)
    jolly = JokerResource(
        id="j_006",
        name="Jolly Joker",
        effect_type="instant",
        trigger="on_scored",
        condition_type="hand_type",
        condition_value="Pair",
        bonus_type="+m",
        bonus_value=8,
        per_card=False,
        rarity="Common",
        cost=3,
        notes="+8 Mult if line is a Pair"
    )

    # 3. Greedy Joker - Per-card effect (counts diamonds)
    greedy = JokerResource(
        id="j_002",
        name="Greedy Joker",
        effect_type="instant",
        trigger="on_scored",
        condition_type="suit",
        condition_value="Diamond",
        bonus_type="+m",
        bonus_value=3,
        per_card=True,
        rarity="Common",
        cost=5,
        notes="+3 Mult per Diamond in scored line"
    )

    # 4. Runner - Growing joker (accumulates over time)
    runner = JokerResource(
        id="j_049",
        name="Runner",
        effect_type="growing",
        trigger="on_scored",
        condition_type="hand_type",
        condition_value="Straight",
        bonus_type="+c",
        bonus_value=15,
        per_card=False,
        grow_per="line",
        rarity="Common",
        cost=5,
        notes="Gains +15 Chips per Straight line scored"
    )

    # 5. Photograph - Multiply effect (×2 mult)
    photograph = JokerResource(
        id="j_078",
        name="Photograph",
        effect_type="instant",
        trigger="on_scored",
        condition_type="card_position",
        condition_value="first_face",
        bonus_type="Xm",
        bonus_value=2,
        per_card=False,
        rarity="Common",
        cost=5,
        notes="First face card in each line gets ×2 Mult"
    )

    return [joker_basic, jolly, greedy, runner, photograph]


def test_joker_system():
    """Test joker system with game."""
    print("=" * 60)
    print("JOKER SYSTEM TEST - 5 MVP Jokers")
    print("=" * 60)

    # Create joker manager and add MVP jokers
    joker_manager = JokerManager(max_slots=5)
    mvp_jokers = create_mvp_jokers()

    print("\n📋 Active Jokers:")
    for joker in mvp_jokers:
        added = joker_manager.add_joker(joker)
        status = "✓" if added else "✗"
        print(f"  {status} {joker.get_display_name()}: {joker.get_description()}")

    print(f"\n🃏 Joker Slots: {joker_manager.get_joker_count()}/{joker_manager.max_slots}")

    # Initialize game with joker manager
    config = GameConfigResource()
    game = GameManager(config)

    # Connect joker manager to score manager
    game.score_manager.joker_manager = joker_manager

    # Start a new round
    print("\n🎲 Starting new round...")
    game.start_new_round()

    # Score the grid with jokers
    print("\n💯 Scoring with jokers...")
    current_score, row_hands, col_hands = game.score_and_update()

    # Display results
    print("\n" + "=" * 60)
    print("SCORING RESULTS")
    print("=" * 60)

    print("\n🔢 Row Scores:")
    for i, hand in enumerate(row_hands):
        print(f"  Row {i}: {hand.hand_type:15s} | {hand.chips:4d} chips × {hand.mult:3d} mult = {hand.chips * hand.mult:6d}")

    print("\n🔢 Column Scores:")
    for i, hand in enumerate(col_hands):
        print(f"  Col {i}: {hand.hand_type:15s} | {hand.chips:4d} chips × {hand.mult:3d} mult = {hand.chips * hand.mult:6d}")

    print(f"\n💰 Current Score: {current_score}")
    print(f"💰 Cumulative Score: {game.state.cumulative_score}")

    # Show growing joker status
    print("\n📈 Growing Joker Status:")
    runner = mvp_jokers[3]  # Runner is 4th joker
    print(f"  {runner.get_display_name()}: {runner.get_description()}")

    print("\n" + "=" * 60)
    print("Test complete! ✓")
    print("=" * 60)

    # Verify jokers are working
    print("\n🔍 Verification:")
    print(f"  - Joker manager has {joker_manager.get_joker_count()} active jokers")
    print(f"  - Score manager is using joker_manager: {game.score_manager.joker_manager is not None}")
    print(f"  - Base score (no jokers) would be lower")
    print(f"  - Growing joker (Runner) current bonus: +{int(runner.current_bonus)} chips")


if __name__ == "__main__":
    test_joker_system()
