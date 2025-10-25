# Joker Reference - P0 Priority

**Complete reference for all P0 priority jokers**

This document is auto-generated from `data/jokers_structured.csv`.

---

## 📚 Table of Contents

- [Always Active Jokers](#always-active-jokers) - Simple flat bonuses
- [Hand Type Jokers](#hand-type-jokers) - Trigger on specific poker hands
- [Suit Jokers](#suit-jokers) - Trigger on suit matches
- [Rank Jokers](#rank-jokers) - Trigger on specific ranks
- [Card Type Jokers](#card-type-jokers) - Trigger on face cards, etc.
- [Rank Parity Jokers](#rank-parity-jokers) - Trigger on even/odd ranks
- [Special Position Jokers](#special-position-jokers) - Position-based effects
- [Growing Jokers](#growing-jokers) - Accumulate value over time
- [Quick Reference Table](#quick-reference-table)

---

## Always Active Jokers

These jokers apply their effect to **every line** scored, with no conditions.

### Joker

- **Description:** +4 Mult
- **Cost:** $2 | **Rarity:** Common
- **Effect:** +m 4.0
- **Notes:** Simplest joker - always active

### Gros Michel

- **Description:** +15 Mult
- **Cost:** $5 | **Rarity:** Common
- **Effect:** +m 15.0
- **Notes:** +15 Mult (1/6 chance destroyed each round)

---

## Hand Type Jokers

These jokers trigger when a line scores a specific poker hand.

### Jolly Joker

- **Description:** +8 Mult if hand is a Pair
- **Cost:** $3 | **Rarity:** Common
- **Condition:** Line is a **Pair**
- **Effect:** +m 8.0
- **Notes:** +8 Mult if line is a Pair

### Zany Joker

- **Description:** +12 Mult if hand is a Three of a Kind
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Three of a Kind**
- **Effect:** +m 12.0
- **Notes:** +12 Mult if line is Three of a Kind

### Mad Joker

- **Description:** +10 Mult if hand is a Two Pair
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Two Pair**
- **Effect:** +m 10.0
- **Notes:** +10 Mult if line is Two Pair

### Crazy Joker

- **Description:** +12 Mult if hand is a Straight
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Straight**
- **Effect:** +m 12.0
- **Notes:** +12 Mult if line is a Straight

### Droll Joker

- **Description:** +10 Mult if hand is a Flush
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Flush**
- **Effect:** +m 10.0
- **Notes:** +10 Mult if line is a Flush

### Sly Joker

- **Description:** +50 Chips if hand is a Pair
- **Cost:** $3 | **Rarity:** Common
- **Condition:** Line is a **Pair**
- **Effect:** +c 50.0
- **Notes:** +50 Chips if line is a Pair

### Wily Joker

- **Description:** +100 Chips if hand is a Three of a Kind
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Three of a Kind**
- **Effect:** +c 100.0
- **Notes:** +100 Chips if line is Three of a Kind

### Clever Joker

- **Description:** +80 Chips if hand is a Two Pair
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Two Pair**
- **Effect:** +c 80.0
- **Notes:** +80 Chips if line is Two Pair

### Devious Joker

- **Description:** +100 Chips if hand is a Straight
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Straight**
- **Effect:** +c 100.0
- **Notes:** +100 Chips if line is a Straight

### Crafty Joker

- **Description:** +80 Chips if hand is a Flush
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Line is a **Flush**
- **Effect:** +c 80.0
- **Notes:** +80 Chips if line is a Flush

---

## Suit Jokers

These jokers trigger per matching suit card in each line.

### Greedy Joker

- **Description:** +3 Mult per Diamond card scored
- **Cost:** $5 | **Rarity:** Common
- **Condition:** Diamond card scored
- **Effect:** +m 3.0 **per card**
- **Notes:** +3 Mult per Diamond in scored line

### Lusty Joker

- **Description:** +3 Mult per Heart card scored
- **Cost:** $5 | **Rarity:** Common
- **Condition:** Heart card scored
- **Effect:** +m 3.0 **per card**
- **Notes:** +3 Mult per Heart in scored line

### Wrathful Joker

- **Description:** +3 Mult per Spade card scored
- **Cost:** $5 | **Rarity:** Common
- **Condition:** Spade card scored
- **Effect:** +m 3.0 **per card**
- **Notes:** +3 Mult per Spade in scored line

### Gluttonous Joker

- **Description:** +3 Mult per Club card scored
- **Cost:** $5 | **Rarity:** Common
- **Condition:** Club card scored
- **Effect:** +m 3.0 **per card**
- **Notes:** +3 Mult per Club in scored line

---

## Rank Jokers

These jokers trigger on specific card ranks.

### Scholar

- **Description:** +20 Chips and +4 Mult per A scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** A card scored
- **Effect:** ++ 20c4m **per card**
- **Notes:** Aces give +20 Chips AND +4 Mult

### Walkie Talkie

- **Description:** +10 Chips and +4 Mult per 10 or 4 scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** 10|4 card scored
- **Effect:** ++ 10c4m **per card**
- **Notes:** 10s and 4s give +10 Chips AND +4 Mult

---

## Card Type Jokers

These jokers trigger on card types (face cards, etc.).

### Raised Fist

- **Description:** Adds 2× lowest held card rank to Mult
- **Cost:** $5 | **Rarity:** Common
- **Condition:** lowest_rank
- **Effect:** +m 2x
- **Notes:** Adds 2× lowest held card rank to Mult

### Scary Face

- **Description:** +30 Chips per face card scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** face card scored
- **Effect:** +c 30.0 **per card**
- **Notes:** +30 Chips per face card in scored line

### Smiley Face

- **Description:** +5 Mult per face card scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** face card scored
- **Effect:** +m 5.0 **per card**
- **Notes:** +5 Mult per face card in scored line

---

## Rank Parity Jokers

These jokers trigger on even or odd card ranks.

### Even Steven

- **Description:** +4 Mult per even rank card scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Even rank card scored
- **Effect:** +m 4.0 **per card**
- **Notes:** +4 Mult per even rank card (10-8-6-4-2)

### Odd Todd

- **Description:** +31 Chips per odd rank card scored
- **Cost:** $4 | **Rarity:** Common
- **Condition:** Odd rank card scored
- **Effect:** +c 31.0 **per card**
- **Notes:** +31 Chips per odd rank card (A-9-7-5-3)

---

## Special Position Jokers

These jokers have position-based effects (first card, etc.).

### Photograph

- **Description:** First face card in each line gets ×2 Mult
- **Cost:** $5 | **Rarity:** Common
- **Effect:** Xm 2.0
- **Notes:** First face card in each line gets ×2 Mult

---

## Growing Jokers

These jokers accumulate bonus value over time as conditions are met.

### Runner

- **Description:** Gains +15 Chips per Straight scored (currently +0)
- **Cost:** $5 | **Rarity:** Common
- **Condition:** Line is a **Straight**
- **Growth:** +c 15.0 per line
- **Notes:** Gains +15 Chips per Straight line scored

### ◆ Spare Trousers

- **Description:** Gains +2 Mult per Two Pair scored (currently +0)
- **Cost:** $6 | **Rarity:** Uncommon
- **Condition:** Line is a **Two Pair**
- **Growth:** +m 2.0 per line
- **Notes:** Gains +2 Mult per Two Pair line scored

---

## Quick Reference Table

| Joker | Cost | Effect | Description |
|-------|------|--------|-------------|
| Joker | $2 | +m 4.0 | +4 Mult |
| Greedy Joker | $5 | +m 3.0 | +3 Mult per Diamond card scored |
| Lusty Joker | $5 | +m 3.0 | +3 Mult per Heart card scored |
| Wrathful Joker | $5 | +m 3.0 | +3 Mult per Spade card scored |
| Gluttonous Joker | $5 | +m 3.0 | +3 Mult per Club card scored |
| Jolly Joker | $3 | +m 8.0 | +8 Mult if hand is a Pair |
| Zany Joker | $4 | +m 12.0 | +12 Mult if hand is a Three of a Kind |
| Mad Joker | $4 | +m 10.0 | +10 Mult if hand is a Two Pair |
| Crazy Joker | $4 | +m 12.0 | +12 Mult if hand is a Straight |
| Droll Joker | $4 | +m 10.0 | +10 Mult if hand is a Flush |
| Sly Joker | $3 | +c 50.0 | +50 Chips if hand is a Pair |
| Wily Joker | $4 | +c 100.0 | +100 Chips if hand is a Three of a Kind |
| Clever Joker | $4 | +c 80.0 | +80 Chips if hand is a Two Pair |
| Devious Joker | $4 | +c 100.0 | +100 Chips if hand is a Straight |
| Crafty Joker | $4 | +c 80.0 | +80 Chips if hand is a Flush |
| Raised Fist | $5 | +m 2x | Adds 2× lowest held card rank to Mult |
| Scary Face | $4 | +c 30.0 | +30 Chips per face card scored |
| Gros Michel | $5 | +m 15.0 | +15 Mult |
| Even Steven | $4 | +m 4.0 | +4 Mult per even rank card scored |
| Odd Todd | $4 | +c 31.0 | +31 Chips per odd rank card scored |
| Scholar | $4 | ++ 20c4m | +20 Chips and +4 Mult per A scored |
| Runner | $5 | +c 15.0 | Gains +15 Chips per Straight scored (currently +0) |
| Photograph | $5 | Xm 2.0 | First face card in each line gets ×2 Mult |
| ◆ Spare Trousers | $6 | +m 2.0 | Gains +2 Mult per Two Pair scored (currently +0) |
| Walkie Talkie | $4 | ++ 10c4m | +10 Chips and +4 Mult per 10 or 4 scored |
| Smiley Face | $4 | +m 5.0 | +5 Mult per face card scored |

---

## 🔧 Implementation Notes

### Joker Activation
- Jokers trigger **per line** (up to 10 times per scoring round)
- Each of 5 rows and 5 columns evaluated separately
- Effects apply to each line independently, then summed

### Per-Card vs Per-Line
- **Per-card:** Effect multiplies by number of matching cards (e.g., Greedy Joker)
- **Per-line:** Effect applies once per line if condition met (e.g., Jolly Joker)

### Growing Jokers
- Start at 0 bonus
- Accumulate value when conditions met
- Growth persists across all hands in round

### Joker Slots
- Maximum 5 active jokers
- Left-to-right order matters for some effects
- Jokers persist across all 7 hands in round
