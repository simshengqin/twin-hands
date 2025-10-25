# Game Mechanics - Detailed Rules

**Complete mechanics reference for Poker Grid**

---

## 🎴 The Grid

### Grid Structure
- **5 rows × 5 columns** = 25 cells
- Each cell holds one playing card
- Cards are dealt from a single 52-card deck (with replacement)

### Scoring Lines
- **5 rows** (left to right)
- **5 columns** (top to bottom)
- **Total: 10 lines** scored as 5-card poker hands

---

## 🎲 Round Flow

### 1. Initial Deal
- All 25 cells filled randomly from deck
- Cards drawn **with replacement** (duplicates possible!)
- Auto-freeze activates (if enabled)

### 2. Auto-Freeze (Default: ON)
- Finds highest-ranked pair in grid
- Prefers pairs in same row/column
- Freezes both cards automatically
- Uses 2 freeze slots

### 3. Hand Phase (7 hands per round)
Player can:
- **Freeze cells** (`f <row> <col>`) - Toggle freeze (max 2 total)
- **Unfreeze all** (`u`) - Clear all freezes
- **Play hand** (`s`) - Redraw unfrozen cells, then score

**Key Rule:** Freezes **persist across all 7 hands**!

### 4. Scoring
After each hand:
- All 10 lines evaluated as poker hands
- Each line scored using chips × mult
- Jokers apply their effects
- Cumulative score updated

### 5. Round End
- Win: Cumulative score ≥ 5000
- Lose: 7 hands used, score < 5000

---

## ❄️ Freeze System

### Freeze Rules
- **Max 2 cells** frozen at once
- Frozen cells marked with `*`
- Frozen cells **never redraw**
- Freezes persist across all 7 hands in round

### Strategy
- Freeze high-value cards (Aces, face cards)
- Freeze pairs (build to trips/quads)
- Freeze flush draws
- Freeze straight draws
- **Think 10 lines ahead!** A frozen card affects both its row AND column

### Cannot Freeze
- Empty cells (shouldn't happen in this game)
- Already frozen cells (toggle unfreezes them)

---

## 🃏 Deck System

### Single Deck
- One 52-card deck (4 suits × 13 ranks)
- Deck persists across all hands and rounds
- **Draw with replacement** - same card can appear multiple times

### Why With Replacement?
- Enables high-frequency combos (multiple Aces, etc.)
- Allows future deck building (add/remove cards)
- Creates interesting probability space
- Balatro does this!

### Future: Deck Building
- Add cards to deck (make certain cards more likely)
- Remove cards (slim deck for consistency)
- Enhance cards (foil, holographic, polychrome)

---

## 🎯 Scoring System

### Chips × Mult Formula
Each line scored separately:
```
line_score = (base_chips + chip_bonuses) × (base_mult + mult_bonuses)
```

Then summed:
```
total_score = Σ(all row scores) + Σ(all column scores)
```

### Base Hand Values

| Hand | Base Chips | Base Mult | Score (chips × mult) |
|------|------------|-----------|---------------------|
| Royal Flush | 100 | 8 | 800 |
| Straight Flush | 80 | 6 | 480 |
| Four of a Kind | 60 | 7 | 420 |
| Full House | 40 | 4 | 160 |
| Flush | 35 | 4 | 140 |
| Straight | 30 | 4 | 120 |
| Three of a Kind | 30 | 3 | 90 |
| Two Pair | 20 | 2 | 40 |
| One Pair | 10 | 2 | 20 |
| High Card | 5 | 1 | 5 |

### Joker Effects
Jokers modify chips and mult **per line**:

**Example:**
```
Row 0: Pair of 5s (10 chips × 2 mult)
Joker: "+8 mult if Pair"
Final: 10 × 10 = 100 points

Row 1: Flush (35 chips × 4 mult)
Joker: no effect (not a pair)
Final: 35 × 4 = 140 points
```

### Local Scoring
Each line scored **independently**, then summed. NOT global multiplication.

**Why?**
- Balanced for 10 lines
- Each line can have different joker synergies
- Grid bonuses can multiply total later

---

## 🃏 Joker System

### Joker Slots
- **Max 5 jokers** active at once
- Left-to-right order matters for some jokers
- Jokers persist across all hands in round

### Joker Activation
Jokers trigger **per line** (up to 10 times per scoring round):

```python
for each line in [5 rows + 5 columns]:
    base_chips, base_mult = evaluate_hand(line)

    for joker in active_jokers:
        if joker.condition_met(line):
            # Apply effect
            chips, mult = joker.apply(line, chips, mult)

    line_score = chips × mult
    total_score += line_score
```

### Joker Effect Types

#### 1. Static Effects (+m, +c)
Add flat bonus if condition met:
- **Joker**: +4 Mult (always)
- **Jolly Joker**: +8 Mult if line is a Pair

#### 2. Per-Card Effects
Triggered by individual cards in line:
- **Greedy Joker**: +3 Mult per Diamond scored
- **Scary Face**: +30 Chips per face card scored

#### 3. Multiply Effects (Xm)
Multiply the mult value:
- **Photograph**: First face card in line gets ×2 Mult

#### 4. Growing Effects
Accumulate value over time:
- **Runner**: Gains +15 Chips per Straight scored (cumulative)

### Joker Stacking
- Multiple copies of same joker allowed
- Effects stack additively
- Example: 2× Joker = +8 Mult total

---

## 💰 Economy (Future)

### Money System
- Earn money from joker effects
- Earn interest on saved money
- Spend in shop between rounds

### Shop
- Buy jokers ($2-$10)
- Buy consumables (tarot, planet cards)
- Reroll shop offerings ($5)

### Sell Value
- Jokers sell for ~50% of cost
- Some jokers gain sell value over time

---

## 🎲 RNG & Probability

### Card Drawing
- Uniform random from 52 cards
- With replacement (same card can appear multiple times)
- No "deck memory" - each draw independent

### Joker Probabilities
Some jokers have chance-based effects:
- "1 in 4 chance" = 25%
- "1 in 2 chance" = 50%
- Future: "Oops! All 6s" doubles all probabilities

---

## 🏆 Win/Lose Conditions

### Win
- Cumulative score ≥ 5000 chips
- Achieved within 7 hands

### Lose
- 7 hands used
- Cumulative score < 5000 chips

### Future: Ante System
- Win 8 Antes in a row
- Each Ante has higher quota
- Boss blinds have special abilities

---

## 🎮 Strategy Tips

### Early Game
- Use auto-freeze (it's usually good!)
- Focus on high-frequency hands (Pairs, Two Pairs)
- Don't chase rare hands (Royal Flush) too early

### Mid Game
- Identify which lines score best
- Freeze cards that benefit multiple lines
- Balance chip jokers vs mult jokers

### Late Game
- All-in on your best synergy
- Consider unfreezing to pivot if needed
- Calculate whether you can reach 5000

### Grid Thinking
- **Intersections matter most** - A frozen Ace affects 2 lines!
- **Diagonal thinking** - Cards in corners affect 2 lines
- **Row vs Column** - Sometimes better to optimize 1 row than 2 weak columns

---

## 📊 Advanced Mechanics

### Card Evaluation Order
1. Cards evaluated left-to-right, top-to-bottom
2. "First card" = leftmost card in a line
3. Matters for jokers like "Photograph"

### Hand Type Priority
Standard poker hierarchy:
1. Royal Flush
2. Straight Flush
3. Four of a Kind
4. Full House
5. Flush
6. Straight
7. Three of a Kind
8. Two Pair
9. One Pair
10. High Card

### Special Rules
- Ace can be low in straights (A-2-3-4-5)
- Flush requires all 5 cards same suit
- Straight requires exactly 5 consecutive ranks
- Future: "Four Fingers" joker makes 4-card hands valid

---

## 🔮 Future Mechanics

### Consumables
- **Tarot Cards**: Modify cards in deck
- **Planet Cards**: Upgrade hand levels
- **Spectral Cards**: High-risk, high-reward effects

### Card Enhancements
- **Foil**: +50 chips
- **Holographic**: +10 mult
- **Polychrome**: ×1.5 mult

### Seals
- **Gold Seal**: Earn $3 when scored
- **Red Seal**: Retrigger card
- **Blue Seal**: Create Planet card
- **Purple Seal**: Create Tarot card

### Grid Bonuses (Not Yet Implemented)
- All 10 lines scored: ×1.5 mult
- Symmetrical grid: +bonus
- Monochrome grid (all same suit): +bonus

---

## 📚 See Also

- **[SCORING.md](SCORING.md)** - Detailed scoring math
- **[JOKERS.md](JOKERS.md)** - All joker effects
- **[BALANCE.md](BALANCE.md)** - Balance formulas
