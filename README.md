# Poker Grid

A 5×5 grid-based poker game with strategic hand play and freezing mechanics.

**Now with Godot-ready architecture!** ✨

## Quick Start

### For Players

```bash
python run.py
```

### For Developers / Claude

**Read this first:** [`claude.md`](claude.md) - Complete instructions for working with this codebase

Uses the new Godot-ready architecture!

## Game Overview

- **Grid**: 5×5 grid of playing cards
- **Deck**: Single shared 52-card deck (Balatro-style deck building)
- **Hands**: 7 hands per round (configurable)
- **Drawing**: Cards drawn WITH replacement - duplicates allowed!
- **Freezes**: Up to 2 cells can be frozen - **persist across all hands** in the round
- **Auto-Freeze**: Automatically freezes the highest pair after initial deal (default: ON)
- **Scoring**: All 10 lines (5 rows + 5 columns) scored as 5-card poker hands
- **Goal**: Reach quota target (default: 5000 chips)

### Commands

During the round, you can:

- `f <row> <col>` - Toggle freeze on cell (e.g., `f 2 3`)
- `u` - Unfreeze all cells
- `s` - Play hand (redeal unfrozen cells)
- `q` - Quit session

### Gameplay Loop

1. **Initial Deal**: 5×5 grid is dealt from single shared deck
2. **Auto-Freeze** (if enabled): Highest pair is automatically frozen
3. **Hand Phase**:
   - Adjust frozen cells (up to 2 total, persist across all hands)
   - Play up to 7 hands - unfrozen cells redraw randomly from the full deck
   - Cards are drawn WITH replacement (duplicates allowed!)
   - Frozen cells stay locked for the entire round
4. **Scoring**: All rows and columns are scored as poker hands
5. **Results**: Win if you meet the quota target

## Key Mechanics

### Freezes Persist
Unlike traditional slot games, **freezes last the entire round** (all 7 hands). Once you freeze 2 cells, you can only unfreeze and re-freeze them - you cannot freeze additional cells without unfreezing first.

### Auto-Freeze Highest Pair
By default, the game automatically freezes the highest-ranked pair after the initial deal. This gives you a strategic starting point.

### Single Shared Deck (Balatro-Style)
The game uses a single 52-card deck that persists across hands and rounds. Cards are drawn randomly WITH replacement, meaning:
- The same card can appear multiple times in the grid
- Deck always has all 52 cards available for drawing
- This enables deck-building mechanics (future feature: modify deck with card packs, tarot cards)
- Allows for high-frequency combos (e.g., multiple pairs of the same rank)

## Scoring System

**Balatro-style chips × mult scoring!**

Each hand has base chips and a multiplier. Final score = chips × mult.

| Hand | Chips | Mult | Score (chips × mult) |
|------|-------|------|---------------------|
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

**Scoring Formula**: Each of the 10 lines (5 rows + 5 columns) is scored separately, then summed:
```
total_score = Σ(row_chips × row_mult) + Σ(col_chips × col_mult)
```

Future: Grid bonuses will add multipliers based on special patterns!

## Configuration

Edit `src/resources/game_config_resource.py` to customize:

- **Grid size**: `grid_rows`, `grid_cols` (default: 5x5)
- **Hands**: `max_hands` (default: 7 hands per round)
- **Freezes**: `max_freezes` (default: 2)
- **Auto-freeze**: `auto_freeze_highest_pair` (default: True)
- **Session**: `rounds_per_session`, `quota_target` (default: 1 round, 5000 chips)
- **Scoring**: `HAND_SCORES` class constant

## 🎮 Godot-Ready Architecture

This project has been **completely refactored** to follow Godot 4.5 best practices!

```
poker-grid/
├── src/                    # Godot-ready architecture
│   ├── resources/          # Data (extends Resource)
│   ├── managers/           # Logic (extends Node)
│   ├── utils/              # Static helpers
│   ├── autoload/           # Global systems
│   ├── ui/                 # User interface
│   ├── docs/               # Architecture documentation
│   └── tests_manual/       # Visual test scripts
│
├── tests/                  # Automated test suite (pytest)
└── run.py                  # Main entry point
```

### Key Benefits

- ✅ **Resource Pattern**: Data in custom Resources
- ✅ **Node Pattern**: Logic in Manager Nodes
- ✅ **Signal-Driven**: Decoupled event system
- ✅ **Separation of Concerns**: Clean architecture
- ✅ **Ready to Port**: Direct mapping to Godot

### 📖 Documentation

**Start here:** [`src/docs/README_REFACTOR.md`](src/docs/README_REFACTOR.md)

Full docs:
- **Architecture**: [`src/docs/GODOT_ARCHITECTURE.md`](src/docs/GODOT_ARCHITECTURE.md)
- **Porting Guide**: [`src/docs/PORTING_GUIDE.md`](src/docs/PORTING_GUIDE.md)
- **Summary**: [`src/docs/REFACTOR_SUMMARY.md`](src/docs/REFACTOR_SUMMARY.md)
- **Diagrams**: [`src/docs/ARCHITECTURE_DIAGRAM.txt`](src/docs/ARCHITECTURE_DIAGRAM.txt)

## Porting to Godot

When ready to port:

1. Read [`src/docs/GODOT_ARCHITECTURE.md`](src/docs/GODOT_ARCHITECTURE.md)
2. Follow [`src/docs/PORTING_GUIDE.md`](src/docs/PORTING_GUIDE.md)
3. Convert Python → GDScript (mostly syntax)
4. Create UI scenes
5. Connect signals

The architecture is already perfect for Godot!

## Display

Cards are displayed with Unicode suit symbols:
- ♥ Hearts
- ♦ Diamonds
- ♣ Clubs
- ♠ Spades

Ranks: 2-9, T (10), J (Jack), Q (Queen), K (King), A (Ace)

Frozen cells are marked with an asterisk (*).

## Testing

Run manual test scripts:

```bash
python src/tests_manual/test_run.py         # Test poker evaluation
python src/tests_manual/test_autofreeze.py  # Test auto-freeze logic
Optional manual script:
```bash
python src/tests_manual/test_hand.py        # Tests a single hand
```
```

See [`src/tests_manual/README.md`](src/tests_manual/README.md) for details.

## Strategy Tips

- The auto-freeze targets the highest pair, which is often a good starting point
- Consider unfreezing and re-freezing to chase better hands (flush draws, straight draws)
- Remember: freezes persist across all 7 hands, so choose wisely
- Watch for opportunities to build hands across multiple rows/columns
- **New**: Duplicates are possible! You might see the same card multiple times in the grid

## Future Enhancements

- **Deck Building**: Modify deck with card packs, tarot cards, spectral cards (shop system)
- **Jokers**: Conditional modifiers that affect chips and mult
- **Grid Bonuses**: Special multipliers for full grids, patterns, etc.
- **Multiple Rounds**: Survive 8 rounds (Balatro-style Antes)
- **Save/Load**: Session persistence

