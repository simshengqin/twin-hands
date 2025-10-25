# Claude Instructions for Poker Grid

## ⚠️ CRITICAL: ALWAYS TEST BEFORE COMPLETING

**BEFORE telling the user a task is complete, you MUST:**

1. **Run ALL automated tests:**
   ```bash
   pytest tests/ -v
   ```
   ✅ ALL tests must pass (0 failures)

2. **Run the game to verify it works:**
   ```bash
   python run.py
   ```
   ✅ Game must start without errors

3. **Update or add tests for your changes:**
   - Changed game logic? Update affected tests in `tests/`
   - Added new feature? Write new tests
   - Fixed a bug? Add regression test
   - **IMPORTANT:** Tests must read values from `config`, never hardcode (e.g., `game.config.max_spins` not `5`)
   - See `tests/README.md` for guidelines

**If tests fail or game crashes, DO NOT say the task is complete. Fix the issues first.**

---

## Project Overview

This is a **poker-themed grid game** with a **Godot-ready architecture**. The codebase has been professionally refactored to follow Godot 4.5 best practices.

**Key fact:** The game is fully functional in Python but structured exactly like a Godot project for easy porting.

## Directory Structure

```
poker-grid/
├── src/                    # Production code (Godot-ready)
│   ├── resources/          # Data classes (extends Resource in Godot)
│   ├── managers/           # Game logic (extends Node in Godot)
│   ├── utils/              # Static helpers
│   ├── autoload/           # Global singletons (autoload in Godot)
│   ├── ui/                 # User interface (UI scenes in Godot)
│   ├── docs/               # Architecture documentation
│   └── tests_manual/       # Manual visual tests
│
├── tests/                  # Automated test suite
├── run.py                  # Main entry point
└── STRUCTURE.md            # Detailed directory guide
```

## Critical Rules

### 1. All Code Goes in `src/`
- Resources → `src/resources/`
- Game logic → `src/managers/`
- Utilities → `src/utils/`
- Global systems → `src/autoload/`
- User interface → `src/ui/`

### 2. Follow the Architecture Patterns

#### Resources (Data Only)
```python
# src/resources/example_resource.py
class ExampleResource:
    """
    Pure data container.
    In Godot: extends Resource

    Rules:
    - Data properties only
    - No complex game logic
    - Can have simple data management methods
    - Can emit signals (via callbacks in Python)
    """
    property: type

    def update_property(self, value):
        # Simple data management OK
        self.property = value
        self._emit_changed()
```

#### Managers (Game Logic)
```python
# src/managers/example_manager.py
class ExampleManager:
    """
    Game logic controller.
    In Godot: extends Node

    Rules:
    - Coordinates game systems
    - Contains game logic
    - Emits events via Events singleton
    - References Resources for data
    """

    def __init__(self, state, config):
        self.state = state  # Resource
        self.config = config  # Resource

    def do_game_action(self):
        # Game logic here
        Events.emit_something_happened()
```

#### Utils (Static Helpers)
```python
# src/utils/example_util.py
class ExampleUtil:
    """
    Static utility functions.
    In Godot: static functions

    Rules:
    - No state
    - Pure functions
    - Reusable across systems
    """

    @staticmethod
    def calculate_something(input):
        return result
```

#### Autoload (Global Singletons)
```python
# src/autoload/example_system.py
class ExampleSystem:
    """
    Global singleton system.
    In Godot: extends Node, added to AutoLoad

    Rules:
    - Single instance
    - Global access
    - Usually for cross-system communication
    """

    @classmethod
    def emit_event(cls, data):
        cls._emit("event_name", data)
```

### 3. Import Conventions

```python
# In src/ files, import from src
from src.resources.card_resource import CardResource
from src.managers.game_manager import GameManager
from src.utils.poker_evaluator import PokerEvaluator
from src.autoload.events import Events
from src.ui.terminal_ui import TerminalUI

# In run.py (root level)
from src.managers.game_manager import GameManager
from src.ui.terminal_ui import TerminalUI
```

### 4. Configuration Attributes

**IMPORTANT:** Configuration uses lowercase attributes!

```python
# CORRECT
config.max_hands
config.grid_rows
config.quota_target
config.auto_freeze_highest_pair

# WRONG (old style)
config.MAX_HANDS  # ❌ No
config.GRID_ROWS  # ❌ No
```

**Constants** are UPPERCASE (class variables):
```python
GameConfigResource.HAND_SCORES  # ✅ Yes - class constant
GameConfigResource.RANK_VALUES  # ✅ Yes - class constant
```

### 5. Scoring System

The game uses **Balatro-style chips × mult scoring**:

```python
# Each poker hand has base chips and multiplier
GameConfigResource.HAND_SCORES = {
    "Royal Flush": {"chips": 100, "mult": 8},    # 100 × 8 = 800
    "Flush": {"chips": 35, "mult": 4},           # 35 × 4 = 140
    "One Pair": {"chips": 10, "mult": 2},        # 10 × 2 = 20
    # ...
}

# Local scoring: Each line scored separately, then summed
total_score = Σ(row_chips × row_mult) + Σ(col_chips × col_mult)

# Future: Grid bonuses will multiply total_score
# (see TODO in score_manager.py)
```

### 6. Signal/Event Pattern

Use the Events singleton for cross-system communication:

```python
from src.autoload.events import Events

# Emit events
Events.emit_hand_started()
Events.emit_cell_frozen(row, col)
Events.emit_score_updated(current, cumulative)

# Connect to events (if needed)
Events.connect("hand_started", callback_function)
```

## Common Tasks

### Adding a New Resource

1. Create file in `src/resources/`
2. Use dataclass pattern
3. Only data + simple management methods
4. Add to `src/resources/__init__.py`

```python
# src/resources/new_resource.py
from dataclasses import dataclass

@dataclass
class NewResource:
    """
    Description of what data this holds.
    In Godot: extends Resource
    """
    property1: str
    property2: int

    def update_something(self, value):
        self.property1 = value
```

### Adding a New Manager

1. Create file in `src/managers/`
2. Receive state and config in `__init__`
3. Emit events via Events singleton
4. Add to `src/managers/__init__.py`

```python
# src/managers/new_manager.py
from src.autoload.events import Events

class NewManager:
    """
    Description of what this manages.
    In Godot: extends Node
    """

    def __init__(self, state, config):
        self.state = state
        self.config = config

    def do_something(self):
        # Game logic
        Events.emit_something_happened()
```

### Adding a New Utility

1. Create file in `src/utils/`
2. Use static methods
3. No state
4. Add to `src/utils/__init__.py`

```python
# src/utils/new_util.py
class NewUtil:
    """
    Description of what this helps with.
    In Godot: static functions
    """

    @staticmethod
    def helper_function(input):
        return result
```

### Adding New Events

Add to `src/autoload/events.py`:

```python
# In Events class
@classmethod
def emit_new_event(cls, data) -> None:
    """Emit new_event signal."""
    cls._emit("new_event", data)
```

## Testing

### Manual Tests (Visual)
For quick development validation:

```python
# src/tests_manual/test_something.py
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource

config = GameConfigResource()
game = GameManager(config)

# Test something and print results
print("Testing...")
game.do_something()
print("Does this look right?")
```

Run with:
```bash
python src/tests_manual/test_something.py
```

### Automated Tests (Future)
If adding pytest tests:
- Create `tests/` folder (separate from `src/`)
- Use `pytest` framework
- Add assertions and fixtures

## Running the Game

```bash
# Main entry point
python run.py

# Manual tests
python src/tests_manual/test_run.py
python src/tests_manual/test_run.py
python src/tests_manual/test_autofreeze.py
```

## Documentation

Always read these first when working on the project:

1. **Start here:** `src/docs/README_REFACTOR.md` - Quick overview
2. **Architecture:** `src/docs/GODOT_ARCHITECTURE.md` - Deep dive
3. **Porting:** `src/docs/PORTING_GUIDE.md` - How to port to Godot
4. **Structure:** `STRUCTURE.md` - Directory guide

## Key Concepts

### Resource Pattern
- Data is stored in Resource classes
- Serializable (can be saved as `.tres` in Godot)
- No complex game logic
- Can have signals for change notification

### Manager Pattern
- Controllers that coordinate systems
- Each manager has single responsibility
- GameManager coordinates overall flow
- GridManager handles grid operations
- ScoreManager handles scoring

### Signal-Driven Architecture
- Systems communicate via Events singleton
- Decoupled - systems don't directly call each other
- Easy to add new features
- Natural for UI updates

### Separation of Concerns
```
Resources  → What is the data?
Managers   → What actions can happen?
Utils      → How do we calculate things?
Autoload   → How do systems communicate?
```

## Common Pitfalls

### ❌ DON'T Do This

```python
# Don't put game logic in Resources
# src/resources/card_resource.py
def evaluate_poker_hand(self, other_cards):  # ❌ NO!
    # This is game logic, goes in managers/utils
    ...

# Don't use old uppercase config names
config.MAX_HANDS  # ❌ NO!
config.GRID_ROWS  # ❌ NO!

# Don't create circular imports
# src/managers/a.py imports src/managers/b.py
# src/managers/b.py imports src/managers/a.py  # ❌ NO!
```

### ✅ DO This Instead

```python
# Add features in src/
# src/managers/game_manager.py
def new_feature(self):  # ✅ YES!
    ...

# Put game logic in managers/utils
# src/utils/poker_evaluator.py
@staticmethod
def evaluate_poker_hand(cards):  # ✅ YES!
    ...

# Use lowercase config attributes
config.max_hands  # ✅ YES!
config.grid_rows  # ✅ YES!

# Use Events to avoid circular dependencies
from src.autoload.events import Events
Events.emit_something()  # ✅ YES!
```

## Architecture Principles

### 1. Single Responsibility
Each class has ONE job:
- CardResource: Store card data
- GameManager: Coordinate game flow
- PokerEvaluator: Evaluate poker hands
- Events: Facilitate communication

### 2. Godot Alignment
Structure maps directly to Godot:
- `src/resources/` → `res://resources/` (extends Resource)
- `src/managers/` → `res://managers/` (extends Node)
- `src/utils/` → `res://utils/` (static classes)
- `src/autoload/` → `res://autoload/` (AutoLoad singletons)

### 3. Open/Closed Principle
- Open for extension (add new managers, resources)
- Closed for modification (don't change existing patterns)

### 4. Dependency Direction
```
run.py
  ↓
Managers (coordinate)
  ↓
Resources (data) + Utils (helpers) + Events (communication)
```

Never reverse this flow!

## Debugging Tips

### Import Errors
```bash
# If you get import errors, check:
1. Are you using "from src." not "from godot_src."?
2. Is the file in the right folder?
3. Did you add to __init__.py?
```

### Attribute Errors
```python
# If config.MAX_HANDS fails:
# Use lowercase: config.max_hands

# If you need the constant:
# Use class variable: GameConfigResource.RANK_VALUES
```

### Circular Import Errors
```python
# Don't import managers from each other
# Use Events to communicate instead
from src.autoload.events import Events
Events.emit_something()
```

## Quick Reference

### File Locations
```
New resource     → src/resources/new_resource.py
New manager      → src/managers/new_manager.py
New utility      → src/utils/new_util.py
New UI component → src/ui/new_ui.py
New event        → Add to src/autoload/events.py
Manual test      → src/tests_manual/test_something.py
Automated test   → tests/test_feature.py
Documentation    → src/docs/
```

### Import Patterns
```python
# Resources
from src.resources.card_resource import CardResource

# Managers
from src.managers.game_manager import GameManager

# Utils
from src.utils.poker_evaluator import PokerEvaluator

# UI
from src.ui.terminal_ui import TerminalUI

# Events
from src.autoload.events import Events
```

### Config Access
```python
config.max_hands           # Instance attribute
config.grid_rows           # Instance attribute
config.auto_freeze         # Instance attribute

GameConfigResource.RANKS   # Class constant
GameConfigResource.SUITS   # Class constant
```

## Questions to Ask Before Coding

1. **Is this data or logic?**
   - Data → Resource
   - Logic → Manager/Util

2. **Is it game-specific or generic?**
   - Game-specific → Manager
   - Generic helper → Util

3. **Does everyone need access?**
   - Yes → Autoload (Events)
   - No → Regular class

4. **Should it be in Godot's scene tree?**
   - Yes → Manager (Node)
   - No → Resource/Util

## When in Doubt

1. Read `src/docs/GODOT_ARCHITECTURE.md`
2. Look at existing code for patterns
3. Follow the existing structure
4. Ask yourself: "How would this work in Godot?"

## Success Criteria

You're doing it right if:
- ✅ All new code is in `src/`
- ✅ Resources contain only data
- ✅ Managers contain game logic
- ✅ Events used for communication
- ✅ No circular imports
- ✅ Lowercase config attributes
- ✅ Code maps cleanly to Godot concepts

## Git Commits

**IMPORTANT:** Do NOT include `Co-Authored-By: Claude` or any Claude attribution in commit messages.

## Final Notes

This codebase is **production-ready** and follows professional game development patterns. When porting to Godot, the structure will remain exactly the same - only the syntax changes from Python to GDScript.

**The architecture is the product.** Maintain it carefully!
