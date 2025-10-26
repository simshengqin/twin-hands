# Twin Hands Terminal UI Design

## Balatro-Inspired Layout

### Design Principles (from Balatro)
1. **All info visible at once** - No scrolling, everything on one screen
2. **Clear visual hierarchy** - Important info (score, quota) is BIG
3. **Color coding** - Different colors for different info types
4. **Minimal chrome** - No unnecessary borders/decorations
5. **Context-aware** - Show what matters NOW (available decks, tokens left)

---

## Layout Mockup

```
======================================================================
  TWIN HANDS │ Round 1
======================================================================

  Round Score: 156 / 300
  [████████████░░░░░░░░] 52%

  Hand Tokens: 2/4 🃏🃏🃏🃏

  Deck Status:
    Deck 1: 1/2 hands played
    Deck 2: 2/2 hands played (MAX)

  Hands Played This Round:
    1. Pair (6 pts)
    2. Flush (20 pts)
    3. Three of a Kind (15 pts)

──────────────────────────────────────────────────────────────────────

  ● DECK 1 (1/2 played)
    [0] K♥  [1]  3♠  [2]  9♣  [3]  A♦

  ● DECK 2 (2/2 played)
    [0]  5♦  [1]  J♠  [2]  7♥  [3]  2♣

──────────────────────────────────────────────────────────────────────
  Commands:
    play <deck> <cards>  →  Play cards from a deck (e.g., play 1 0 1 2)
    end                  →  End round and calculate score
──────────────────────────────────────────────────────────────────────

  >
```

---

## Key Improvements vs Basic UI

### 1. **Visual Hierarchy** (Balatro-style)
- **BIG** - Round score, quota (most important)
- **Medium** - Token count, deck status
- **Small** - Commands, helper text

### 2. **Color Coding**
| Element | Color | Meaning |
|---------|-------|---------|
| Score (above quota) | Green | Success! |
| Score (below quota) | Red | Danger! |
| Quota target | Cyan | Goal |
| Available deck | Cyan + Green dot | Can play |
| Maxed deck | Gray + Red dot | Cannot play |
| Hand tokens | Yellow | Resource |
| Card suits (♥♦) | Red | Red suits |
| Card suits (♣♠) | White | Black suits |

### 3. **Progress Bar**
```
[████████████░░░░░░░░] 52%
```
- Instant visual feedback on quota progress
- Inspired by Balatro's clear progress indicators

### 4. **Deck Status Indicators**
```
● DECK 1 (1/2 played)  ← Green dot = available
● DECK 2 (2/2 played)  ← Red dot = maxed out
```
- At-a-glance shows which decks can still play
- Unique to Twin Hands (Balatro has 1 hand, we have 2 decks)

### 5. **Card Formatting**
```
[0] K♥  [1]  3♠  [2]  9♣
```
- Suit symbols (♥♦♣♠) instead of text
- Color-coded (red/white)
- Index numbers for easy selection
- Aligned for clean visual scan

### 6. **Hand History**
```
Hands Played This Round:
  1. Pair (6 pts)
  2. Flush (20 pts)
  3. Three of a Kind (15 pts)
```
- Shows what you've played (like Balatro's history)
- Running total visible at top

---

## Responsive Behaviors

### When Hand Token is Spent
```
✓ SUCCESS!
Flush (20 pts)
Cards: [2♥] [5♥] [9♥] [K♥]

[Press Enter to continue...]
```
- Big success indicator
- Hand type and score clearly shown
- Satisfying feedback (like Balatro's animations)

### When Action Fails
```
✗ ERROR: Cannot play hand: Max hands per deck reached

[Press Enter to continue...]
```
- Clear error message
- Red color for errors

### Round End Screen
```
======================================================================
  ✓ ROUND COMPLETE - SUCCESS!
======================================================================

  Final Score: 324
  Quota:       300
  +24 over quota!

======================================================================
```
- BIG reveal (Balatro-style)
- Clear success/failure
- Shows margin of success

---

## Differences from Balatro

### Balatro Has:
- 1 hand with 8 cards
- Discards (red button)
- Joker display at top
- Mult calculation (chips × mult)

### Twin Hands Has:
- 2 decks with 4 cards each
- No discards (Phase A)
- Deck status (hands played per deck)
- Simple scoring (Phase A: sum of base scores)

### Future (Phase B/C):
- Trading system display
- Joker slots (deck-specific + bridge)
- Per-deck mult calculation
- Shop interface

---

## Implementation Notes

### ANSI Colors
```python
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
GRAY = "\033[90m"
BOLD = "\033[1m"
RESET = "\033[0m"
```

### Suit Symbols
```python
SUITS = {
    "hearts": "♥",
    "diamonds": "♦",
    "clubs": "♣",
    "spades": "♠"
}
```

### Screen Clearing
- Clear before each redraw for "single-screen" experience
- Like Balatro: all info visible, no scrolling

---

## Future Enhancements (Phase B+)

### Trading Display
```
  Trade Tokens: 3/3 🔄🔄🔄

  [trade <from_deck> <to_deck> <cards>]
```

### Joker Display
```
  ┌─────────────── JOKERS ───────────────┐
  │ DECK 1: [+50 pts] [×1.5 mult] [___]  │
  │ DECK 2: [+30 pts] [___] [___]        │
  │ BRIDGE: [×2.0 mult] [___]            │
  └───────────────────────────────────────┘
```

### Per-Deck Scoring
```
  Deck 1: 85 × 1.5 = 127
  Deck 2: 60 × 2.0 = 120
  ────────────────────────
  Total:           247
```

---

## Accessibility

- **High contrast** - Bold colors on dark terminal
- **Clear symbols** - Dots (●), checkmarks (✓), crosses (✗)
- **Keyboard-only** - No mouse required
- **Readable at a glance** - Important info is BIG

---

## Inspiration Credit

**Balatro** by LocalThunk
- Visual hierarchy (big numbers!)
- Color coding system
- Single-screen design
- Satisfying feedback

Adapted for Twin Hands' unique 2-deck gameplay.
