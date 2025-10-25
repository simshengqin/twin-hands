# Project Structure

Clean, organized structure with Godot-ready architecture.

## Directory Tree

```
poker-grid/
│
├── src/                        # Main source code (Godot-ready)
│   │
│   ├── resources/              # Data classes (extends Resource in Godot)
│   │   ├── __init__.py
│   │   ├── card_resource.py
│   │   ├── hand_resource.py
│   │   ├── game_config_resource.py
│   │   ├── grid_cell_resource.py
│   │   ├── reel_resource.py
│   │   └── game_state_resource.py
│   │
│   ├── managers/               # Game controllers (extends Node in Godot)
│   │   ├── __init__.py
│   │   ├── game_manager.py
│   │   ├── grid_manager.py
│   │   └── score_manager.py
│   │
│   ├── utils/                  # Static helper functions
│   │   ├── __init__.py
│   │   ├── poker_evaluator.py
│   │   └── card_factory.py
│   │
│   ├── autoload/               # Global singletons (autoload in Godot)
│   │   ├── __init__.py
│   │   └── events.py
│   │
│   ├── ui/                     # User interface (UI scenes in Godot)
│   │   ├── __init__.py
│   │   └── terminal_ui.py
│   │
│   ├── docs/                   # Architecture documentation
│   │   ├── README.md
│   │   ├── GODOT_ARCHITECTURE.md
│   │   ├── PORTING_GUIDE.md
│   │   ├── README_REFACTOR.md
│   │   ├── REFACTOR_SUMMARY.md
│   │   └── ARCHITECTURE_DIAGRAM.txt
│   │
│   ├── tests_manual/           # Manual visual test scripts
│   │   ├── README.md
│   │   ├── test_hand.py  (tests one hand)
│   │   ├── test_run.py
│   │   └── test_autofreeze.py
│   │
│   ├── ui_adapter.py           # Bridge between managers and UI
│   └── __init__.py
│
├── tests/                      # Automated test suite (pytest)
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_deck_system.py
│   ├── test_game_flow.py
│   ├── test_grid_manager.py
│   └── test_scoring.py
│
├── run.py                      # Main entry point
├── README.md                   # Main documentation
├── CLAUDE.md                   # Instructions for Claude AI
├── AGENTS.md                   # Agent workflows
├── CONTRIBUTING.md             # Contribution guide
└── STRUCTURE.md                # This file
```

## What Lives Where

### `src/` - Godot-Ready Code

**Purpose:** Production code ready to port to Godot Engine

**Structure follows Godot conventions:**
- `resources/` → `res://resources/` in Godot
- `managers/` → `res://managers/` in Godot
- `utils/` → `res://utils/` in Godot
- `autoload/` → `res://autoload/` in Godot
- `ui/` → `res://ui/` in Godot

### `src/resources/` - Data Only

**What:** Pure data structures (no complex logic)

**Godot equivalent:** `extends Resource`

Files:
- `card_resource.py` - Playing card (rank, suit)
- `hand_resource.py` - Poker hand with chips × mult scoring
- `game_config_resource.py` - Game configuration and hand scores
- `grid_cell_resource.py` - Single grid cell
- `reel_resource.py` - Column deck
- `game_state_resource.py` - Main game state

### `src/managers/` - Game Logic

**What:** Controllers that coordinate game systems

**Godot equivalent:** `extends Node`

Files:
- `game_manager.py` - Main coordinator (starts rounds, handles game flow)
- `grid_manager.py` - Grid operations (dealing, freezing)
- `score_manager.py` - Scoring logic (chips × mult, local scoring)

### `src/utils/` - Static Helpers

**What:** Utility functions with no state

**Godot equivalent:** Static classes

Files:
- `poker_evaluator.py` - Hand evaluation logic (returns chips & mult)
- `card_factory.py` - Deck creation and shuffling

### `src/autoload/` - Global Systems

**What:** Game-wide singletons

**Godot equivalent:** `extends Node` + added to AutoLoad

Files:
- `events.py` - Global event bus (signal system)

### `src/ui/` - User Interface

**What:** UI components for player interaction

**Godot equivalent:** UI scenes and scripts

Files:
- `terminal_ui.py` - Terminal-based UI (displays chips × mult breakdown)

### `src/docs/` - Documentation

**What:** Architecture and porting guides

Files:
- `GODOT_ARCHITECTURE.md` - Deep dive into architecture
- `PORTING_GUIDE.md` - Step-by-step Godot porting
- `README_REFACTOR.md` - Quick overview
- `REFACTOR_SUMMARY.md` - Transformation details
- `ARCHITECTURE_DIAGRAM.txt` - Visual diagrams

### `src/tests_manual/` - Manual Tests

**What:** Quick visual test scripts

**Purpose:** Development validation (not automated tests)

Files:
- `test_hand.py` - Test hand mechanics
- `test_run.py` - Test poker evaluation
- `test_autofreeze.py` - Test auto-freeze logic

### `tests/` - Automated Tests

**What:** pytest test suite (119 tests)

**Purpose:** Regression testing and validation

Files:
- `test_config.py` - Configuration tests
- `test_deck_system.py` - Deck and drawing tests
- `test_game_flow.py` - Game flow integration tests
- `test_grid_manager.py` - Grid operations tests
- `test_scoring.py` - Poker evaluation and scoring tests

## Entry Point

### Main Entry Point
```bash
python run.py
```
Uses the Godot-ready architecture in `src/`

## Import Patterns

### In `run.py`
```python
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource
from src.ui_adapter import UIAdapter
from src.ui.terminal_ui import TerminalUI
```

### In `src/` files
```python
# Resources import other resources
from src.resources.card_resource import CardResource

# Managers import resources, utils, autoload
from src.resources.game_state_resource import GameStateResource
from src.utils.poker_evaluator import PokerEvaluator
from src.autoload.events import Events

# Utils import resources
from src.resources.hand_resource import HandResource

# UI imports managers and resources
from src.ui_adapter import UIAdapter
```

## Scoring System

The game uses **Balatro-style chips × mult scoring**:

```python
# Each hand has base chips and multiplier
GameConfigResource.HAND_SCORES = {
    "Royal Flush": {"chips": 100, "mult": 8},    # 100 × 8 = 800
    "Flush": {"chips": 35, "mult": 4},           # 35 × 4 = 140
    "One Pair": {"chips": 10, "mult": 2},        # 10 × 2 = 20
    # ...
}

# Local scoring formula
total_score = Σ(row_chips × row_mult) + Σ(col_chips × col_mult)
```

## File Counts

- **src/**: 20+ Python files + 7 docs
- **tests/**: 6 test files (119 tests)
- **Total code**: ~3500 lines (well-organized)
- **Total docs**: ~5000 lines

## Key Principles

### 1. Single Responsibility
Each file has one clear purpose

### 2. Godot Alignment
Structure maps directly to Godot concepts

### 3. Separation of Concerns
Data, logic, utilities, UI, and globals are separate

### 4. Documentation First
Every folder has a README explaining its purpose

### 5. Clean Imports
No circular dependencies, clear import hierarchy

### 6. Test Coverage
119 automated tests covering all major systems

## Next Steps

1. **Now:** Use the new structure (`python run.py`)
2. **Soon:** Read `src/docs/GODOT_ARCHITECTURE.md`
3. **Later:** Port to Godot using `src/docs/PORTING_GUIDE.md`

The structure is ready for professional game development!
