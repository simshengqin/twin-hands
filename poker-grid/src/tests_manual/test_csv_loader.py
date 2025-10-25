#!/usr/bin/env python3
"""
Test CSV loader for jokers.
Verifies jokers can be loaded from CSV and descriptions are generated correctly.
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.joker_loader import JokerLoader


def test_csv_loader():
    """Test loading jokers from CSV."""
    print("=" * 70)
    print("CSV JOKER LOADER TEST")
    print("=" * 70)

    # Load all P0 jokers
    print("\n📁 Loading P0 priority jokers from CSV...")
    p0_jokers = JokerLoader.load_p0_jokers()

    print(f"\n✓ Loaded {len(p0_jokers)} P0 jokers\n")

    # Display each joker with generated description
    print("=" * 70)
    print("JOKER CATALOG - P0 Priority")
    print("=" * 70)

    for i, joker in enumerate(p0_jokers, 1):
        print(f"\n{i}. {joker.get_display_name()} [{joker.rarity}] - ${joker.cost}")
        print(f"   ID: {joker.id}")
        print(f"   Description: {joker.get_description()}")
        print(f"   Effect: {joker.effect_type} | Trigger: {joker.trigger}")
        print(f"   Bonus: {joker.bonus_type} {joker.bonus_value}")
        if joker.per_card:
            print(f"   Per-card: Yes")
        if joker.grow_per:
            print(f"   Grows per: {joker.grow_per}")
        if joker.notes:
            print(f"   Notes: {joker.notes}")

    print("\n" + "=" * 70)
    print("CSV LOADER TEST COMPLETE ✓")
    print("=" * 70)

    # Verify specific jokers loaded correctly
    print("\n🔍 Verification:")
    print(f"  - Total P0 jokers: {len(p0_jokers)}")

    # Check for specific jokers
    joker_names = [j.name for j in p0_jokers]
    expected_jokers = ["Joker", "Jolly Joker", "Greedy Joker", "Runner", "Photograph"]

    print(f"  - Expected MVP jokers found:")
    for name in expected_jokers:
        found = name in joker_names
        status = "✓" if found else "✗"
        print(f"    {status} {name}")

    # Test specific joker descriptions
    print("\n📝 Description Tests:")
    for joker in p0_jokers:
        if joker.name == "Joker":
            print(f"  • Joker: '{joker.get_description()}'")
            assert "4 Mult" in joker.get_description(), "Joker description incorrect"
        elif joker.name == "Greedy Joker":
            print(f"  • Greedy Joker: '{joker.get_description()}'")
            assert "Diamond" in joker.get_description(), "Greedy description incorrect"
        elif joker.name == "Runner":
            print(f"  • Runner: '{joker.get_description()}'")
            assert "Straight" in joker.get_description(), "Runner description incorrect"
        elif joker.name == "Scholar":
            print(f"  • Scholar: '{joker.get_description()}'")
            assert "Chips" in joker.get_description() and "Mult" in joker.get_description(), "Scholar description incorrect"

    print("\n✓ All descriptions generated correctly!")


if __name__ == "__main__":
    test_csv_loader()
