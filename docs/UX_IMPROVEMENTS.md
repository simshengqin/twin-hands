# UX Improvements Summary

## Overview
Major user experience improvements implemented based on feedback and Balatro UI analysis.

---

## ✨ The 4 Big Improvements

### 1. **Emoji Suit Symbols** ♥♦♣♠

**Before:** `KH`, `3S`, `9C`, `AD`
**After:** `K♥`, `3♠`, `9♣`, `A♦`

**Why Better:**
- ✅ Instantly recognizable (proper card symbols)
- ✅ Red/black color distinction clear
- ✅ Professional look (matches real cards)
- ✅ Less cognitive load (no mental translation from H→♥)

**Technical:**
```python
# UTF-8 encoding fix for Windows
sys.stdout.reconfigure(encoding='utf-8')

SUITS = {
    "hearts": "♥",
    "diamonds": "♦",
    "clubs": "♣",
    "spades": "♠"
}
```

---

### 2. **Card Sorting (Suit → Rank)**

**Before:** Random card order (as drawn)
**After:** Sorted by suit (♣ ♦ ♥ ♠), then rank (A-K)

**Why Better:**
- ✅ Easier to scan (suits grouped together)
- ✅ Find specific cards faster
- ✅ Consistent with poker conventions
- ✅ Flushes/straights more obvious

**Example:**
```
Before:  [1] K♥  [2] 3♠  [3] 9♣  [4] A♦
After:   [1] 9♣  [2] A♦  [3] K♥  [4] 3♠
         ↑ clubs  ↑ diamonds ↑ hearts ↑ spades
```

---

### 3. **Unified 1-8 Indexing (1-indexed, not 0)**

**Before:** 0-indexed per deck
- Deck 1: [0] [1] [2] [3]
- Deck 2: [0] [1] [2] [3]

**After:** Unified 1-8 (1-indexed)
- Deck 1: [1] [2] [3] [4]
- Deck 2: [5] [6] [7] [8]

**Why Better:**
- ✅ **More intuitive** - People count from 1, not 0
- ✅ **Natural left-to-right** - Card 5 is "first card on right"
- ✅ **No context switching** - Don't need to think "which deck?"
- ✅ **Balatro-style** - Cards numbered left-to-right across screen

**Mental Model:**
```
[1] [2] [3] [4] | [5] [6] [7] [8]
   Deck 1       |     Deck 2
```

---

### 4. **Simplified Input (No 'play' Keyword)**

**Before:**
```
> play 1 0 1 2    # Play cards 0,1,2 from deck 1
> play 2 0 1 2 3  # Play cards 0,1,2,3 from deck 2
```

**After:**
```
> 123    # Play cards 1,2,3 (from Deck 1)
> 5678   # Play cards 5,6,7,8 (from Deck 2)
```

**Why Better:**
- ✅ **50% less typing** - No 'play' keyword, no spaces
- ✅ **Faster** - Type `123` vs `play 1 0 1 2` (11 chars saved!)
- ✅ **Natural** - Feels like selecting cards directly
- ✅ **Validation built-in** - Can't mix decks (e.g., `15` rejected)

**How It Works:**
1. Parse each digit as a card number (1-8)
2. Map to deck: 1-4 → Deck 0, 5-8 → Deck 1
3. Validate all cards from same deck
4. Auto-detect which deck to play from

**Examples:**
```
123   → Deck 0, cards [0,1,2] ✅
5678  → Deck 1, cards [0,1,2,3] ✅
14    → Deck 0, cards [0,3] ✅
56    → Deck 1, cards [0,1] ✅
15    → REJECTED (mixed decks) ❌
999   → REJECTED (out of range) ❌
```

---

## Complete Example Session

### Before (Old UI):
```
  Deck 1 visible cards:
    [0] KH
    [1] 3S
    [2] 9C
    [3] AD

  Deck 2 visible cards:
    [0] 5D
    [1] JS
    [2] 7H
    [3] 2C

> play 1 0 1 2    # Type 14 characters
```

### After (New UI):
```
  * DECK 1 (0/2 played)
    [1]  9♣  [2]  A♦  [3]  K♥  [4]  3♠

  * DECK 2 (0/2 played)
    [5]  5♦  [6]  7♥  [7]  J♠  [8]  2♣

  > 123             # Type 3 characters
```

---

## Impact Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Typing per hand** | ~14 chars | ~3 chars | **78% less** |
| **Card scanning** | Random | Sorted | **Faster** |
| **Suit recognition** | ASCII | Emoji | **Instant** |
| **Indexing** | 0-indexed | 1-indexed | **More natural** |
| **Cognitive load** | High (deck + index) | Low (unified index) | **Simpler** |

---

## User Feedback Points Addressed

### ✅ "Should use emoji for suit symbols"
Implemented with UTF-8 encoding fix for Windows.

### ✅ "Should sort by suit then rank"
Cards now sorted ♣ ♦ ♥ ♠, then A-K within each suit.

### ✅ "Shouldn't need 'play' keyword"
Just type card numbers directly (e.g., `123`).

### ✅ "Shouldn't be zero-indexed"
Changed to 1-indexed (1-8 for 2 decks).

### ✅ "Should be unified indexing (not separate 1-3 per deck)"
Unified 1-4 (Deck 1) and 5-8 (Deck 2) - natural left-to-right.

---

## Design Philosophy

Following **Balatro's UX Principles:**
1. **Minimal friction** - Fewer keystrokes, faster gameplay
2. **Visual clarity** - Emoji symbols, sorted cards
3. **Natural mental models** - 1-indexed, left-to-right
4. **Immediate feedback** - Clear error messages

Adapted for **Twin Hands' unique 2-deck system:**
- Unified card numbering (not separate per deck)
- Auto-detect deck from card range
- Validate same-deck selection
- Visual deck status indicators

---

## Technical Implementation

### Card Selection Parser
```python
def parse_card_selection(input_str: str, num_decks: int = 2):
    """
    Parse unified card selection (1-8 for 2 decks).

    Examples:
        "123"  → (deck=0, cards=[0,1,2])
        "5678" → (deck=1, cards=[0,1,2,3])
        "15"   → None (mixed decks)
    """
    # Parse digits
    card_nums = [int(c) for c in input_str if c.isdigit()]

    # Map to (deck, card_in_deck)
    selections = []
    for unified_idx in card_nums:
        deck_idx = (unified_idx - 1) // 4
        card_idx = (unified_idx - 1) % 4
        selections.append((deck_idx, card_idx))

    # Validate same deck
    first_deck = selections[0][0]
    if not all(deck == first_deck for deck, _ in selections):
        return None  # Mixed decks not allowed

    return (first_deck, [c for _, c in selections])
```

### Card Sorting
```python
def _sort_cards(cards):
    """Sort by suit (♣ ♦ ♥ ♠) then rank (A-K)."""
    SUIT_ORDER = ["clubs", "diamonds", "hearts", "spades"]
    RANK_ORDER = ["A", "2", "3", ..., "K"]

    return sorted(cards, key=lambda c: (
        SUIT_ORDER.index(c.suit),
        RANK_ORDER.index(c.rank)
    ))
```

---

## Future Enhancements

### Phase B (Trading):
- Could add `t` prefix for trading: `t13` = trade cards 1,3 to other deck
- Visual arrows showing trade direction

### Phase C (Shop):
- Quick-buy with numbers: `1` = buy first Joker
- Arrow keys for navigation?

### Godot Port:
- Click/drag cards directly
- Keyboard shortcuts (1-8) still work
- Visual highlighting on hover

---

## Comparison to Balatro

| Feature | Balatro | Twin Hands |
|---------|---------|------------|
| **Card symbols** | Emoji suits | ✅ Matching |
| **Indexing** | Not shown | ✅ 1-8 unified |
| **Input** | Click/select | ✅ Type numbers |
| **Sorting** | Auto-sorted | ✅ Matching |
| **Visual clarity** | High | ✅ High |

Twin Hands adapts Balatro's excellent UX while adding innovations for 2-deck gameplay!

---

## Credits

**Inspiration:** Balatro by LocalThunk
**Design Goal:** Match Balatro's polish while innovating for 2-deck mechanics

🃏 The result: A fast, intuitive, satisfying card selection experience!
