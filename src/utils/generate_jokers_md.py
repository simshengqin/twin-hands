#!/usr/bin/env python3
"""
Generate JOKERS.md documentation from CSV data.
Auto-generates comprehensive joker documentation.
"""

import sys
import os
import io
from pathlib import Path

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.joker_loader import JokerLoader


def generate_jokers_md(output_path: str):
    """Generate JOKERS.md from CSV data."""

    # Load all P0 jokers
    jokers = JokerLoader.load_p0_jokers()

    # Group by effect type
    instant_jokers = [j for j in jokers if j.effect_type == "instant"]
    growing_jokers = [j for j in jokers if j.effect_type == "growing"]

    # Further group instant jokers by trigger/condition
    always_active = [j for j in instant_jokers if j.trigger == "always"]
    hand_type_jokers = [j for j in instant_jokers if j.condition_type == "hand_type"]
    suit_jokers = [j for j in instant_jokers if j.condition_type == "suit"]
    rank_jokers = [j for j in instant_jokers if j.condition_type == "rank"]
    card_type_jokers = [j for j in instant_jokers if j.condition_type == "card_type"]
    rank_parity_jokers = [j for j in instant_jokers if j.condition_type == "rank_parity"]
    special_jokers = [j for j in instant_jokers if j.condition_type == "card_position"]

    # Build markdown content
    md = []
    md.append("# Joker Reference - P0 Priority")
    md.append("")
    md.append("**Complete reference for all P0 priority jokers**")
    md.append("")
    md.append("This document is auto-generated from `data/jokers_structured.csv`.")
    md.append("")
    md.append("---")
    md.append("")

    # Table of Contents
    md.append("## 📚 Table of Contents")
    md.append("")
    md.append("- [Always Active Jokers](#always-active-jokers) - Simple flat bonuses")
    md.append("- [Hand Type Jokers](#hand-type-jokers) - Trigger on specific poker hands")
    md.append("- [Suit Jokers](#suit-jokers) - Trigger on suit matches")
    md.append("- [Rank Jokers](#rank-jokers) - Trigger on specific ranks")
    md.append("- [Card Type Jokers](#card-type-jokers) - Trigger on face cards, etc.")
    md.append("- [Rank Parity Jokers](#rank-parity-jokers) - Trigger on even/odd ranks")
    md.append("- [Special Position Jokers](#special-position-jokers) - Position-based effects")
    md.append("- [Growing Jokers](#growing-jokers) - Accumulate value over time")
    md.append("- [Quick Reference Table](#quick-reference-table)")
    md.append("")
    md.append("---")
    md.append("")

    # Always Active Jokers
    md.append("## Always Active Jokers")
    md.append("")
    md.append("These jokers apply their effect to **every line** scored, with no conditions.")
    md.append("")
    for joker in always_active:
        md.append(f"### {joker.get_display_name()}")
        md.append("")
        md.append(f"- **Description:** {joker.get_description()}")
        md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
        md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value}")
        if joker.notes:
            md.append(f"- **Notes:** {joker.notes}")
        md.append("")

    # Hand Type Jokers
    md.append("---")
    md.append("")
    md.append("## Hand Type Jokers")
    md.append("")
    md.append("These jokers trigger when a line scores a specific poker hand.")
    md.append("")
    for joker in hand_type_jokers:
        md.append(f"### {joker.get_display_name()}")
        md.append("")
        md.append(f"- **Description:** {joker.get_description()}")
        md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
        md.append(f"- **Condition:** Line is a **{joker.condition_value}**")
        md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value}")
        if joker.notes:
            md.append(f"- **Notes:** {joker.notes}")
        md.append("")

    # Suit Jokers
    md.append("---")
    md.append("")
    md.append("## Suit Jokers")
    md.append("")
    md.append("These jokers trigger per matching suit card in each line.")
    md.append("")
    for joker in suit_jokers:
        md.append(f"### {joker.get_display_name()}")
        md.append("")
        md.append(f"- **Description:** {joker.get_description()}")
        md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
        md.append(f"- **Condition:** {joker.condition_value} card scored")
        md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value} **per card**")
        if joker.notes:
            md.append(f"- **Notes:** {joker.notes}")
        md.append("")

    # Rank Jokers
    if rank_jokers:
        md.append("---")
        md.append("")
        md.append("## Rank Jokers")
        md.append("")
        md.append("These jokers trigger on specific card ranks.")
        md.append("")
        for joker in rank_jokers:
            md.append(f"### {joker.get_display_name()}")
            md.append("")
            md.append(f"- **Description:** {joker.get_description()}")
            md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
            md.append(f"- **Condition:** {joker.condition_value} card scored")
            md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value} **per card**")
            if joker.notes:
                md.append(f"- **Notes:** {joker.notes}")
            md.append("")

    # Card Type Jokers
    if card_type_jokers:
        md.append("---")
        md.append("")
        md.append("## Card Type Jokers")
        md.append("")
        md.append("These jokers trigger on card types (face cards, etc.).")
        md.append("")
        for joker in card_type_jokers:
            md.append(f"### {joker.get_display_name()}")
            md.append("")
            md.append(f"- **Description:** {joker.get_description()}")
            md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
            if joker.per_card:
                md.append(f"- **Condition:** {joker.condition_value} card scored")
                md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value} **per card**")
            else:
                md.append(f"- **Condition:** {joker.condition_value}")
                md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value}")
            if joker.notes:
                md.append(f"- **Notes:** {joker.notes}")
            md.append("")

    # Rank Parity Jokers
    if rank_parity_jokers:
        md.append("---")
        md.append("")
        md.append("## Rank Parity Jokers")
        md.append("")
        md.append("These jokers trigger on even or odd card ranks.")
        md.append("")
        for joker in rank_parity_jokers:
            md.append(f"### {joker.get_display_name()}")
            md.append("")
            md.append(f"- **Description:** {joker.get_description()}")
            md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
            md.append(f"- **Condition:** {joker.condition_value.capitalize()} rank card scored")
            md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value} **per card**")
            if joker.notes:
                md.append(f"- **Notes:** {joker.notes}")
            md.append("")

    # Special Position Jokers
    if special_jokers:
        md.append("---")
        md.append("")
        md.append("## Special Position Jokers")
        md.append("")
        md.append("These jokers have position-based effects (first card, etc.).")
        md.append("")
        for joker in special_jokers:
            md.append(f"### {joker.get_display_name()}")
            md.append("")
            md.append(f"- **Description:** {joker.get_description()}")
            md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
            md.append(f"- **Effect:** {joker.bonus_type} {joker.bonus_value}")
            if joker.notes:
                md.append(f"- **Notes:** {joker.notes}")
            md.append("")

    # Growing Jokers
    if growing_jokers:
        md.append("---")
        md.append("")
        md.append("## Growing Jokers")
        md.append("")
        md.append("These jokers accumulate bonus value over time as conditions are met.")
        md.append("")
        for joker in growing_jokers:
            md.append(f"### {joker.get_display_name()}")
            md.append("")
            md.append(f"- **Description:** {joker.get_description()}")
            md.append(f"- **Cost:** ${joker.cost} | **Rarity:** {joker.rarity}")
            if joker.condition_type == "hand_type":
                md.append(f"- **Condition:** Line is a **{joker.condition_value}**")
            md.append(f"- **Growth:** {joker.bonus_type} {joker.bonus_value} per {joker.grow_per}")
            if joker.notes:
                md.append(f"- **Notes:** {joker.notes}")
            md.append("")

    # Quick Reference Table
    md.append("---")
    md.append("")
    md.append("## Quick Reference Table")
    md.append("")
    md.append("| Joker | Cost | Effect | Description |")
    md.append("|-------|------|--------|-------------|")
    for joker in jokers:
        effect = f"{joker.bonus_type} {joker.bonus_value}"
        md.append(f"| {joker.get_display_name()} | ${joker.cost} | {effect} | {joker.get_description()} |")
    md.append("")

    md.append("---")
    md.append("")
    md.append("## 🔧 Implementation Notes")
    md.append("")
    md.append("### Joker Activation")
    md.append("- Jokers trigger **per line** (up to 10 times per scoring round)")
    md.append("- Each of 5 rows and 5 columns evaluated separately")
    md.append("- Effects apply to each line independently, then summed")
    md.append("")
    md.append("### Per-Card vs Per-Line")
    md.append("- **Per-card:** Effect multiplies by number of matching cards (e.g., Greedy Joker)")
    md.append("- **Per-line:** Effect applies once per line if condition met (e.g., Jolly Joker)")
    md.append("")
    md.append("### Growing Jokers")
    md.append("- Start at 0 bonus")
    md.append("- Accumulate value when conditions met")
    md.append("- Growth persists across all hands in round")
    md.append("")
    md.append("### Joker Slots")
    md.append("- Maximum 5 active jokers")
    md.append("- Left-to-right order matters for some effects")
    md.append("- Jokers persist across all 7 hands in round")
    md.append("")

    # Write to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print(f"✓ Generated {output_file}")
    print(f"  - {len(jokers)} total jokers documented")
    print(f"  - {len(always_active)} always active")
    print(f"  - {len(hand_type_jokers)} hand type")
    print(f"  - {len(suit_jokers)} suit")
    print(f"  - {len(growing_jokers)} growing")


if __name__ == "__main__":
    output_path = Path(__file__).parent.parent.parent / "docs" / "gdd" / "JOKERS.md"
    generate_jokers_md(str(output_path))
