# AGENTS.md — Agent Instructions for Poker Grid

These are repository-wide instructions for AI agents and contributors. Follow them for any changes within this repo.

- Scope: Entire repository (file lives at repo root)
- Goal: Maintain the Godot-aligned architecture while working in Python

## Project Overview

This is a poker-themed grid game with a Godot-ready architecture. The codebase follows Godot 4.5 patterns: Resources (data-only), Managers (logic), Utils (pure helpers), and Autoload singletons (global communication via Events).

Key fact: The game runs in Python but mirrors a Godot project for easy porting.

## Directory Structure

```
poker-grid/
├─ src/                    # Production code (Godot-ready)
│  ├─ resources/          # Data classes (extends Resource in Godot)
│  ├─ managers/           # Game logic (extends Node in Godot)
│  ├─ utils/              # Static helpers
│  ├─ autoload/           # Global singletons (autoload in Godot)
│  ├─ docs/               # Architecture documentation
│  └─ tests_manual/       # Manual visual tests
│
├─ legacy_code/           # Original implementation (REFERENCE ONLY)
│  └─ ui.py               # Terminal UI (used via adapter)
│
├─ party-house/           # Reference project (DO NOT MODIFY)
├─ run.py                 # Main entry point
└─ STRUCTURE.md           # Detailed directory guide
```

## Critical Rules

1) Do NOT modify `legacy_code/` or `party-house/`
- `legacy_code/` is for reference only
- `party-house/` is a separate reference project
- Exception: `legacy_code/ui.py` is used via adapter (`src/ui_adapter.py`)

2) All new code goes in `src/`
- Resources → `src/resources/`
- Game logic → `src/managers/`
- Utilities → `src/utils/`
- Global systems → `src/autoload/`

3) Follow the architecture patterns (see “Implementation Patterns”)

4) Import conventions
```python
# In src/ files, import from src
from src.resources.card_resource import CardResource
from src.managers.game_manager import GameManager
from src.utils.poker_evaluator import PokerEvaluator
from src.autoload.events import Events

# In run.py (root level)
from src.managers.game_manager import GameManager
from legacy_code.ui import TerminalUI  # UI still in legacy
```

5) Configuration attributes are lowercase instance attributes
```python
# Correct
config.max_hands
config.grid_rows
config.quota_target
config.auto_freeze_highest_pair

# Wrong (old style)
config.MAX_HANDS  # No
config.GRID_ROWS  # No
```

Constants are UPPERCASE class variables
```python
GameConfigResource.HAND_SCORES
GameConfigResource.RANK_VALUES
```

6) Use Events singleton for cross-system communication
```python
from src.autoload.events import Events

Events.emit_hand_started()
Events.emit_cell_frozen(row, col)
Events.emit_score_updated(current, cumulative)

# Connect (if needed)
Events.connect("hand_started", callback_function)
```

## Implementation Patterns

Resources (data only)
```python
# src/resources/example_resource.py
class ExampleResource:
    """Pure data container. In Godot: extends Resource
    Rules: data properties only; simple data methods OK; no complex logic"""
    property: type

    def update_property(self, value):
        self.property = value
        self._emit_changed()
```

Managers (game logic)
```python
# src/managers/example_manager.py
class ExampleManager:
    """Game logic controller. In Godot: extends Node
    Coordinates systems, emits events, references Resources for data"""

    def __init__(self, state, config):
        self.state = state  # Resource
        self.config = config  # Resource

    def do_game_action(self):
        Events.emit_something_happened()
```

Utils (static helpers)
```python
# src/utils/example_util.py
class ExampleUtil:
    """Static, pure helper functions. No state."""

    @staticmethod
    def calculate_something(input):
        return result
```

Autoload (global singletons)
```python
# src/autoload/example_system.py
class ExampleSystem:
    """Global singleton. In Godot: AutoLoad Node"""

    @classmethod
    def emit_event(cls, data):
        cls._emit("event_name", data)
```

## Common Tasks

Add a new Resource
1) Create file in `src/resources/`
2) Use dataclass pattern where appropriate
3) Only data + simple management methods
4) Add export to `src/resources/__init__.py`
```python
from dataclasses import dataclass

@dataclass
class NewResource:
    property1: str
    property2: int

    def update_something(self, value):
        self.property1 = value
```

Add a new Manager
1) Create file in `src/managers/`
2) Receive state and config in `__init__`
3) Emit events via Events singleton
4) Add export to `src/managers/__init__.py`
```python
from src.autoload.events import Events

class NewManager:
    def __init__(self, state, config):
        self.state = state
        self.config = config

    def do_something(self):
        Events.emit_something_happened()
```

Add a new Utility
1) Create file in `src/utils/`
2) Use static methods; no state
3) Add export to `src/utils/__init__.py`
```python
class NewUtil:
    @staticmethod
    def helper_function(input):
        return result
```

Add a new Event (in `src/autoload/events.py`)
```python
@classmethod
def emit_new_event(cls, data) -> None:
    """Emit new_event signal."""
    cls._emit("new_event", data)
```

## Testing

Manual visual tests
```python
# src/tests_manual/test_something.py
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource

config = GameConfigResource()
game = GameManager(config)

print("Testing...")
game.do_something()
print("Does this look right?")
```
Run: `python src/tests_manual/test_something.py`

Automated tests (future)
- Create `tests/` (separate from `src/`)
- Use `pytest`
- Add assertions and fixtures

## Running

```
# Main
python run.py

# Manual tests
python src/tests_manual/test_run.py
python src/tests_manual/test_run.py
python src/tests_manual/test_autofreeze.py
```

## Documentation

Read these first:
1) `src/docs/README_REFACTOR.md` — Quick overview
2) `src/docs/GODOT_ARCHITECTURE.md` — Deep dive
3) `src/docs/PORTING_GUIDE.md` — Porting to Godot
4) `STRUCTURE.md` — Directory guide

## Key Concepts

Resource pattern
- Data stored in Resource classes
- Serializable feel (maps to Godot Resource)
- No complex game logic; may signal changes

Manager pattern
- Controllers that coordinate systems
- Each manager has a single responsibility
- GameManager coordinates flow; GridManager grid ops; ScoreManager scoring

Signal-driven architecture
- Systems communicate via Events singleton
- Decoupled; easy to extend; natural for UI updates

Separation of concerns
```
Resources  → What is the data?
Managers   → What actions can happen?
Utils      → How do we calculate things?
Autoload   → How do systems communicate?
```

## Common Pitfalls

Don’t do this
```python
# Don’t modify legacy_code (except ui.py via adapter)
# legacy_code/game_state.py
def new_feature():  # NO
    ...

# Don’t put game logic in Resources
# src/resources/card_resource.py
def evaluate_poker_hand(self, other_cards):  # NO
    ...

# Don’t use old uppercase config names
config.MAX_HANDS  # NO
config.GRID_ROWS  # NO

# Don’t create circular imports
# src/managers/a.py ↔ src/managers/b.py  # NO
```

Do this instead
```python
# Add features in src/
def new_feature(self):  # YES (in manager)
    ...

# Put game logic in managers/utils
@staticmethod
def evaluate_poker_hand(cards):  # YES (in util)
    ...

# Use lowercase config attributes
config.max_hands  # YES
config.grid_rows  # YES

# Use Events to avoid circular dependencies
from src.autoload.events import Events
Events.emit_something()  # YES
```

## Architecture Principles

1) Single responsibility
- CardResource: store card data
- GameManager: coordinate game flow
- PokerEvaluator: evaluate poker hands
- Events: facilitate communication

2) Godot alignment
- `src/resources/` → `res://resources/` (Resource)
- `src/managers/`  → `res://managers/` (Node)
- `src/utils/`     → `res://utils/` (static)
- `src/autoload/`  → `res://autoload/` (AutoLoad)

3) Open/Closed principle
- Open to extension (add new managers/resources)
- Closed to modification (don’t break patterns)

4) Dependency direction
```
run.py
  ↓
Managers (coordinate)
  ↓
Resources (data) + Utils (helpers) + Events (communication)
```
Never reverse this flow.

## Debugging Tips

Import errors
1) Use `from src.` (not other roots)
2) Is the file in the right folder?
3) Did you add to `__init__.py`?

Attribute errors
```python
# If config.MAX_HANDS fails → use lowercase: config.max_hands
# For constants → use class vars: GameConfigResource.RANK_VALUES
```

Circular import errors
```python
# Don’t import managers from each other; use Events instead
from src.autoload.events import Events
Events.emit_something()
```

## Quick Reference

File locations
```
New resource   → src/resources/new_resource.py
New manager    → src/managers/new_manager.py
New utility    → src/utils/new_util.py
New event      → Add to src/autoload/events.py
Manual test    → src/tests_manual/test_something.py
Docs           → src/docs/
```

Import patterns
```python
from src.resources.card_resource import CardResource
from src.managers.game_manager import GameManager
from src.utils.poker_evaluator import PokerEvaluator
from src.autoload.events import Events
```

Config access
```python
config.max_hands           # Instance attribute
config.grid_rows           # Instance attribute
config.auto_freeze         # Instance attribute

GameConfigResource.RANKS   # Class constant
GameConfigResource.SUITS   # Class constant
```

## Questions to Ask Before Coding

1) Is this data or logic?
- Data → Resource
- Logic → Manager/Util

2) Is it game-specific or generic?
- Game-specific → Manager
- Generic helper → Util

3) Does everyone need access?
- Yes → Autoload (Events)
- No → Regular class

4) Should it be in Godot’s scene tree?
- Yes → Manager (Node)
- No → Resource/Util

## Success Criteria

- All new code is in `src/`
- Resources contain only data
- Managers contain game logic
- Events used for communication
- No circular imports
- Lowercase config attributes
- Code maps cleanly to Godot concepts

## Final Notes

This codebase is production-ready and follows professional game development patterns. When porting to Godot, the structure remains the same—only the language shifts from Python to GDScript.

The architecture is the product. Maintain it carefully.


