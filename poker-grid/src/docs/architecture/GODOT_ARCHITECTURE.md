# Poker Grid - Godot-Ready Architecture

## Overview

This document describes the Godot-ready architecture for the Poker Grid game. The codebase has been refactored to follow Godot 4.5 best practices, making it straightforward to port to Godot Engine.

## Key Learnings from Godot Deck Builder Tutorial

### 1. **Resource-Based Data**
- Custom Resources (extends `Resource`) for all data structures
- Serializable as `.tres` files for easy editing
- No logic in resources, just data + signals

### 2. **Node-Based Logic**
- Managers and handlers extend `Node`
- Scene composition over inheritance
- Signals for communication between nodes

### 3. **Global Event Bus**
- Autoload singleton for game-wide events
- Decouples systems cleanly
- Easy to debug signal flow

### 4. **State Machine Pattern**
- Used for card states, game states, etc.
- Clean state transitions
- Modular and extensible

### 5. **Separation of Concerns**
- `custom_resources/` - Pure data (Resource)
- `scenes/` - Visual components + logic (Node)
- `global/` - Autoload singletons (Node)
- `effects/` - Reusable game effects

## Architecture Structure

```
godot_src/
├── resources/              # Custom Resources (extends Resource in Godot)
│   ├── card_resource.py           # Playing card data
│   ├── hand_resource.py           # Poker hand data
│   ├── game_config_resource.py   # Game configuration
│   ├── grid_cell_resource.py     # Single grid cell
│   ├── reel_resource.py          # Column reel (deck)
│   └── game_state_resource.py    # Main game state
│
├── managers/               # Game Controllers (extends Node in Godot)
│   ├── game_manager.py            # Main game logic coordinator
│   ├── grid_manager.py            # Grid operations (dealing, freezing)
│   └── score_manager.py           # Scoring logic
│
├── utils/                  # Static Utilities (no extends)
│   ├── poker_evaluator.py         # Hand evaluation logic
│   └── card_factory.py            # Deck creation/shuffling
│
└── autoload/               # Global Singletons (extends Node, autoload)
    └── events.py                   # Global event bus
```

## Component Details

### Resources (extends Resource)

**Purpose**: Pure data containers with signals for change notification.

#### CardResource
```gdscript
class_name CardResource
extends Resource

@export var rank: String  # "2"-"9", "T", "J", "Q", "K", "A"
@export var suit: String  # "H", "D", "C", "S"

func get_rank_value() -> int:
    return GameConfig.RANK_VALUES[rank]
```

#### GameConfigResource
```gdscript
class_name GameConfig
extends Resource

@export_group("Grid Settings")
@export var grid_rows: int = 5
@export var grid_cols: int = 5

@export_group("Hand System")
@export var max_hands: int = 7
@export var max_freezes: int = 2

@export_group("Scoring")
const HAND_SCORES = {
    "Royal Flush": 800,
    "Straight Flush": 400,
    # ...
}
```

#### GameStateResource
```gdscript
class_name GameStateResource
extends Resource

signal state_changed
signal hand_completed
signal score_updated(new_score: int)

var grid: Array[Array]  # 2D array of GridCellResource
var reels: Array[ReelResource]
var hands_left: int
var cumulative_score: int
var config: GameConfig
```

### Managers (extends Node)

**Purpose**: Coordinate game systems and contain logic.

#### GameManager
```gdscript
class_name GameManager
extends Node

@export var config: GameConfig
var state: GameStateResource
var grid_manager: GridManager
var score_manager: ScoreManager

func _ready():
    grid_manager = GridManager.new(state, config)
    score_manager = ScoreManager.new(state, config)
    add_child(grid_manager)
    add_child(score_manager)

func start_new_round():
    state.current_round += 1
    grid_manager.deal_grid()
    Events.emit_round_started(state.current_round)
```

#### GridManager
```gdscript
class_name GridManager
extends Node

var state: GameStateResource
var config: GameConfig

func deal_grid():
    for row in range(config.grid_rows):
        for col in range(config.grid_cols):
            var cell = state.grid[row][col]
            if not cell.is_frozen:
                var card = state.reels[col].draw()
                cell.set_card(card)
    Events.emit_cards_dealt()
```

### Utilities (Static Classes)

**Purpose**: Stateless helper functions.

#### PokerEvaluator
```gdscript
class_name PokerEvaluator

static func evaluate_hand(cards: Array[CardResource]) -> HandResource:
    var sorted_cards = cards.duplicate()
    sorted_cards.sort_custom(func(a, b): return a.get_rank_value() > b.get_rank_value())

    if _is_royal_flush(sorted_cards):
        return HandResource.new(sorted_cards, "Royal Flush", 800)
    # ...
```

### Autoload (Global Singleton)

**Purpose**: Game-wide communication hub.

#### Events
```gdscript
extends Node

# Grid events
signal cell_frozen(row: int, col: int)
signal cell_unfrozen(row: int, col: int)
signal grid_updated

# Hand events
signal hand_started
signal hand_completed

# Score events
signal score_updated(current_score: int, cumulative_score: int)

# Game events
signal game_won(final_score: int)
signal game_lost(final_score: int)
```

## Signal Flow Example

```
Player clicks play-hand button
    ↓
GameManager.play_hand() called
    ↓
Events.emit_hand_started()
    ↓
GridManager.deal_grid()
    ↓
Events.emit_cards_dealt()
    ↓
ScoreManager.score_and_update()
    ↓
Events.emit_score_updated(score)
    ↓
UI updates automatically via signal connections
    ↓
Events.emit_hand_completed()
```

## Scene Tree Structure (Godot)

```
Main (Node)
├── GameManager (Node)
│   ├── GridManager (Node)
│   └── ScoreManager (Node)
│
├── UI (CanvasLayer)
│   ├── GridUI (Control)
│   │   └── CellUI x25 (Control)
│   ├── ScoreUI (Control)
│   └── ControlsUI (Control)
│
└── Camera2D
```

## Porting to Godot - Step by Step

### 1. Create Resource Files

Create `.gd` files in `res://resources/`:
- `card_resource.gd`
- `game_config_resource.gd`
- `game_state_resource.gd`
- etc.

Copy the structure from Python files, using GDScript syntax.

### 2. Create Manager Scenes

Create scenes with attached scripts in `res://managers/`:
- `game_manager.tscn` + `game_manager.gd`
- `grid_manager.tscn` + `grid_manager.gd`
- `score_manager.tscn` + `score_manager.gd`

### 3. Create Autoload Singleton

1. Create `res://autoload/events.gd`
2. Add to Project Settings → Autoload
3. Name it "Events"

### 4. Create Utility Classes

Create static classes in `res://utils/`:
- `poker_evaluator.gd`
- `card_factory.gd`

### 5. Create UI Scenes

Create UI scenes in `res://scenes/ui/`:
- `grid_ui.tscn` - Visual grid representation
- `cell_ui.tscn` - Individual cell display
- `score_ui.tscn` - Score display
- etc.

Connect UI signals to Events and GameManager.

### 6. Create Main Scene

Create `main.tscn`:
```
Main
├── GameManager (instantiate game_manager.tscn)
└── UI (instantiate ui scenes)
```

Connect everything through signals in `_ready()`.

## Best Practices Applied

### 1. **Resource Pattern**
- All data is in Resources
- Can be saved as `.tres` files
- Easy to edit in Godot Inspector

### 2. **Signal-Driven Architecture**
- Decoupled systems
- Easy to add new features
- Natural for UI updates

### 3. **Manager Pattern**
- Single Responsibility Principle
- Each manager handles one domain
- Easy to test and maintain

### 4. **No God Objects**
- GameManager coordinates but doesn't do everything
- Logic distributed appropriately
- Easier to understand and modify

### 5. **Type Safety**
- Class names and type hints throughout
- Catches errors early
- Better IDE support

## Differences from Original Code

| Original | Godot-Ready | Reason |
|----------|-------------|--------|
| Single `GameStateManager` class | Multiple managers | Separation of concerns |
| Dataclasses | Resources | Godot serialization |
| Direct method calls | Signal-based | Decoupling |
| `Config` class | `GameConfig` Resource | Inspector editing |
| No event system | Global Events singleton | Cross-system communication |
| Monolithic logic | Distributed logic | Maintainability |

## Testing the New Architecture

Run the Python version:
```bash
python run_godot_ready.py
```

This uses the new architecture with the existing terminal UI via an adapter.

## Migration Path

1. **Phase 1**: Test new architecture with terminal UI ✓
2. **Phase 2**: Port to Godot, create basic UI
3. **Phase 3**: Add visual effects and polish
4. **Phase 4**: Add save/load system using Resources
5. **Phase 5**: Add sound and music using AudioStream

## Key Files

- `run_godot_ready.py` - New architecture entry point
- `godot_src/managers/game_manager.py` - Main game controller
- `godot_src/autoload/events.py` - Event system
- `godot_src/resources/game_state_resource.py` - Central state

## Signal Reference

See `godot_src/autoload/events.py` for complete signal list.

Key signals:
- `cell_frozen(row, col)` - Cell was frozen
- `hand_completed()` - Hand finished
- `score_updated(current, cumulative)` - Score changed
- `game_won(score)` / `game_lost(score)` - Game ended

## Resources for Further Study

- [Godot Best Practices](https://docs.godotengine.org/en/stable/tutorials/best_practices/index.html)
- [Scene Organization](https://docs.godotengine.org/en/stable/tutorials/best_practices/scene_organization.html)
- [Signals Documentation](https://docs.godotengine.org/en/stable/getting_started/step_by_step/signals.html)
- Deck Builder Tutorial (reference implementation)
