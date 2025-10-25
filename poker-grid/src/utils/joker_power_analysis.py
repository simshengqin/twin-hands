"""
Joker Power Analysis - estimate expected strength and suggest token costs.

This script reads `data/jokers_structured.csv`, uses simplified probability
assumptions to estimate each joker's average score impact per scored line,
and maps that to a suggested token cost.

Assumptions:
- 5-card lines, random like 5-card poker (independence approximations).
- Base hand-type probabilities are from standard 5-card poker.
- Face cards are J/Q/K (3/13).
- Even ranks: 2,4,6,8,10; Odd ranks: 3,5,7,9,A (each 5/13).
- Suit distribution uniform (1/4 each).
- "Photograph" effect (first face x2) triggers if any face card present.
- Growing effects are treated conservatively (initially 0, slow growth).

Outputs a table: id, name, rarity, current cost, estimated factor, suggested cost.

Note: This is a heuristic to guide balancing, not a simulator.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, Tuple


# Baseline hand probabilities (standard 5-card poker)
# Keys match GameConfigResource.HAND_SCORES with mapping for "Pair" -> "One Pair".
POKER_HAND_PROBS: Dict[str, float] = {
    "High Card": 0.501177,
    "One Pair": 0.422569,
    "Two Pair": 0.047539,
    "Three of a Kind": 0.021128,
    "Straight": 0.003925,
    "Flush": 0.001981,
    "Full House": 0.001441,
    "Four of a Kind": 0.000240,
    "Straight Flush": 0.000015,  # Royal included in Straight Flush bucket here
}

# Base chips/mult from config (duplicated here to avoid importing runtime)
HAND_SCORES: Dict[str, Dict[str, int]] = {
    "Royal Flush": {"chips": 100, "mult": 8},
    "Straight Flush": {"chips": 80, "mult": 6},
    "Four of a Kind": {"chips": 60, "mult": 7},
    "Full House": {"chips": 40, "mult": 4},
    "Flush": {"chips": 35, "mult": 4},
    "Straight": {"chips": 30, "mult": 4},
    "Three of a Kind": {"chips": 30, "mult": 3},
    "Two Pair": {"chips": 20, "mult": 2},
    "One Pair": {"chips": 10, "mult": 2},
    "High Card": {"chips": 5, "mult": 1},
}


def baseline_expectations() -> Tuple[float, float, float]:
    """Compute E[chips], E[mult], E[chips*mult] under the baseline distribution."""
    e_chips = 0.0
    e_mult = 0.0
    e_product = 0.0
    for hand, p in POKER_HAND_PROBS.items():
        # Merge royal into straight flush for scoring (approx)
        if hand == "Straight Flush":
            chips = HAND_SCORES["Straight Flush"]["chips"]
            mult = HAND_SCORES["Straight Flush"]["mult"]
        else:
            chips = HAND_SCORES[hand]["chips"]
            mult = HAND_SCORES[hand]["mult"]
        e_chips += p * chips
        e_mult += p * mult
        e_product += p * chips * mult
    return e_chips, e_mult, e_product


# Precompute some simple expected counts in 5 cards
E_COUNT_SUIT = 5 * (1 / 4)  # 1.25
E_COUNT_FACE = 5 * (3 / 13)  # ~1.1538 (J/Q/K)
E_COUNT_PARITY = 5 * (5 / 13)  # ~1.9231 even or odd
E_COUNT_RANK_A = 5 * (1 / 13)  # ~0.3846
E_COUNT_RANK_10_4 = 5 * (2 / 13)  # ~0.7692 (10 or 4)

P_ANY_FACE = 1 - ((10 / 13) ** 5)  # ~0.727


def expected_min_rank_value_in_5() -> float:
    """Approximate expected minimum rank value (2..14) in 5 random cards.

    Uses a simple continuous-order-statistic approximation for speed.
    """
    # Continuous approx: E[min] ~ a + (b-a)/(n+1)
    a, b, n = 2, 14, 5
    return a + (b - a) / (n + 1)


def estimate_factor(row: Dict[str, str], e_chips: float, e_mult: float, e_prod: float) -> float:
    """Estimate expected per-line score factor for a joker.

    Returns a multiplicative factor relative to baseline E[chips*mult].
    """
    effect_type = row["effect_type"].strip()
    trigger = row["trigger"].strip()
    cond_type = row["condition_type"].strip()
    cond_val = row["condition_value"].strip()
    bonus_type = row["bonus_type"].strip()
    bonus_value_raw = row["bonus_value"].strip()
    per_card = row["per_card"].strip().lower() == "yes"

    # Growing effects are under-valued here (start at 0). We'll treat as very low.
    if effect_type == "growing":
        return 1.02  # placeholder minor long-term value

    # Compute delta contributions
    add_prod = 0.0  # Added to numerator sum p*chips*mult

    def add_mult(dm: float, weight: float = 1.0):
        # Sum over all hands: p*chips*dm*weight
        nonlocal add_prod
        add_prod += dm * weight * e_chips

    def add_chips(dc: float, weight: float = 1.0):
        nonlocal add_prod
        add_prod += dc * weight * e_mult

    # Multiplicative mult effects like x2 (Photograph)
    mult_factor = 1.0

    if bonus_type == "Xm":
        # Only seen value 2 for x2; weight by trigger probability
        if cond_type == "card_position" and cond_val == "first_face":
            p = P_ANY_FACE
            mult_factor *= (1 + p * (float(bonus_value_raw) - 1))
        else:
            # Generic Xm, assume triggers always (rare in our data)
            mult_factor *= float(bonus_value_raw)

    elif bonus_type == "++":
        chips_s, mult_s = bonus_value_raw.split("c")
        chips_add = float(chips_s)
        mult_add = float(mult_s.replace("m", ""))
        # Expected count by condition
        if cond_type == "rank" and cond_val == "A":
            count = E_COUNT_RANK_A
        elif cond_type == "rank" and cond_val == "10|4":
            count = E_COUNT_RANK_10_4
        else:
            count = 0.0
        add_chips(chips_add * count)
        add_mult(mult_add * count)

    elif bonus_type in ("+m", "+c"):
        # Parse numeric value or formats like '2x' -> treat as 2 * E[min] for Raised Fist
        if bonus_value_raw.endswith("x") and cond_type == "card_type" and cond_val == "lowest_rank":
            # 2x lowest rank value
            lowest = expected_min_rank_value_in_5()
            num = float(bonus_value_raw[:-1]) * lowest
        else:
            try:
                num = float(bonus_value_raw)
            except ValueError:
                num = 0.0

        # Determine weighting and counts
        if cond_type == "hand_type":
            # Map CSV values to baseline key names
            hand_map = {"Pair": "One Pair"}
            key = hand_map.get(cond_val, cond_val)
            p = POKER_HAND_PROBS.get(key, 0.0)
            weight = 0.0
            # weight is sum p*chips for +m or p*mult for +c; handled via add_* using e_chips/e_mult
            weight = p
            if bonus_type == "+m":
                add_mult(num, weight)
            else:
                add_chips(num, weight)

        elif cond_type == "suit":
            count = E_COUNT_SUIT if per_card else 1.0
            if bonus_type == "+m":
                add_mult(num * count)
            else:
                add_chips(num * count)

        elif cond_type == "card_type" and cond_val == "face":
            count = E_COUNT_FACE if per_card else 1.0
            if bonus_type == "+m":
                add_mult(num * count)
            else:
                add_chips(num * count)

        elif cond_type == "rank_parity":
            count = E_COUNT_PARITY if per_card else 1.0
            if bonus_type == "+m":
                add_mult(num * count)
            else:
                add_chips(num * count)

        elif cond_type == "rank":
            if cond_val == "A":
                count = E_COUNT_RANK_A if per_card else 1.0
            elif cond_val == "10|4":
                count = E_COUNT_RANK_10_4 if per_card else 1.0
            else:
                # Single rank
                count = 5 * (len(cond_val.split("|")) / 13) if per_card else 1.0
            if bonus_type == "+m":
                add_mult(num * count)
            else:
                add_chips(num * count)

        else:
            # No/unknown condition -> treat as always
            if bonus_type == "+m":
                add_mult(num)
            else:
                add_chips(num)

    # Final factor
    factor = (e_prod + add_prod) / e_prod
    factor *= mult_factor
    return factor


def suggested_cost(factor: float, rarity: str) -> int:
    """Map factor to token cost with a rarity adjustment.

    Baseline:
    - Factor ~1.00-1.05 -> 2 tokens
    - 1.06-1.15 -> 3 tokens
    - 1.16-1.30 -> 4 tokens
    - 1.31-1.55 -> 5 tokens
    - 1.56-1.85 -> 6 tokens
    - 1.86-2.20 -> 7 tokens
    - >2.20 -> 8 tokens
    Rarity bumps cost by +0 (Common), +1 (Uncommon), +2 (Rare).
    """
    base = 2
    if factor <= 1.05:
        base = 2
    elif factor <= 1.15:
        base = 3
    elif factor <= 1.30:
        base = 4
    elif factor <= 1.55:
        base = 5
    elif factor <= 1.85:
        base = 6
    elif factor <= 2.20:
        base = 7
    else:
        base = 8

    rarity_bump = {"Common": 0, "Uncommon": 1, "Rare": 2, "Legendary": 3}.get(rarity, 0)
    return max(1, base + rarity_bump)


def main():
    csv_path = Path(__file__).parent.parent.parent / "data" / "jokers_structured.csv"
    e_chips, e_mult, e_prod = baseline_expectations()

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print("id,name,rarity,current_cost,factor,suggested_cost")
    for row in rows:
        try:
            fac = estimate_factor(row, e_chips, e_mult, e_prod)
        except Exception:
            fac = 1.0
        sugg = suggested_cost(fac, row["rarity"].strip())
        print(f"{row['id']},{row['name']},{row['rarity']},{row['cost']},{fac:.3f},{sugg}")


if __name__ == "__main__":
    main()

