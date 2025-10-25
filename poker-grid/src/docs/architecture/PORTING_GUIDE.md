# Godot Porting Guide - Poker Grid

## Quick Start Checklist

- [ ] Install Godot 4.5
- [ ] Create new Godot project
- [ ] Set up folder structure
- [ ] Port Resource classes
- [ ] Port Manager classes
- [ ] Set up Events autoload
- [ ] Create basic UI scenes
- [ ] Test and iterate

## Detailed Steps

### 1. Project Setup

1. Create new Godot 4.5 project
2. Create folder structure:
```
res://
├── resources/
├── managers/
├── scenes/
│   ├── main/
│   ├── ui/
│   └── cells/
├── autoload/
├── utils/
└── assets/
    ├── sprites/
    ├── fonts/
    └── audio/
```

### 2. Port Resources

For each file in `godot_src/resources/`, create a `.gd` file:

#### Example: CardResource

**Python (`card_resource.py`):**
```python
@dataclass
class CardResource:
    rank: str
    suit: str

    def get_rank_value(self) -> int:
        return GameConfigResource.RANK_VALUES[self.rank]
```

**GDScript (`card_resource.gd`):**
```gdscript
class_name CardResource
extends Resource

@export var rank: String  ## "2"-"9", "T", "J", "Q", "K", "A"
@export var suit: String  ## "H", "D", "C", "S"

func get_rank_value() -> int:
    return GameConfig.RANK_VALUES[rank]

func get_display_string() -> String:
    const SUIT_SYMBOLS = {
        "H": "♥",
        "D": "♦",
        "C": "♣",
        "S": "♠"
    }
    return rank + SUIT_SYMBOLS.get(suit, suit)
```

#### Translation Tips

| Python | GDScript | Notes |
|--------|----------|-------|
| `@dataclass` | `class_name ... extends Resource` | Use Resource for data |
| `def __init__` | Constructor not needed | Use `@export` vars |
| `from typing import` | Built-in types | `int`, `String`, `Array[Type]` |
| `Optional[Type]` | `Type` with null default | Can be null by default |
| `self._callback` | `signal signal_name` | Use signals instead |

### 3. Port Managers

For each manager in `godot_src/managers/`:

#### Example: GameManager

**Python (`game_manager.py`):**
```python
class GameManager:
    def __init__(self, config):
        self.config = config
        self.state = self._create_initial_state()
        self.grid_manager = GridManager(self.state, self.config)
```

**GDScript (`game_manager.gd`):**
```gdscript
class_name GameManager
extends Node

@export var config: GameConfig

var state: GameStateResource
var grid_manager: GridManager
var score_manager: ScoreManager

func _ready():
    if not config:
        config = GameConfig.new()

    state = _create_initial_state()

    grid_manager = GridManager.new()
    grid_manager.state = state
    grid_manager.config = config
    add_child(grid_manager)

    score_manager = ScoreManager.new()
    score_manager.state = state
    score_manager.config = config
    add_child(score_manager)

func _create_initial_state() -> GameStateResource:
    var new_state = GameStateResource.new()
    new_state.config = config

    # Create grid
    for row in range(config.grid_rows):
        var grid_row = []
        for col in range(config.grid_cols):
            var cell = GridCellResource.new()
            cell.row = row
            cell.col = col
            grid_row.append(cell)
        new_state.grid.append(grid_row)

    # Create reels
    new_state.reels = CardFactory.create_reels(config.grid_cols)

    return new_state
```

### 4. Set Up Autoload

**Python (`events.py`):**
```python
class Events:
    @classmethod
    def emit_hand_started(cls) -> None:
        cls._emit("hand_started")
```

**GDScript (`events.gd`):**
```gdscript
extends Node

signal hand_started
signal hand_completed
signal cell_frozen(row: int, col: int)
# ... etc

func emit_hand_started() -> void:
    hand_started.emit()

func emit_cell_frozen(row: int, col: int) -> void:
    cell_frozen.emit(row, col)
```

**Add to Autoload:**
1. Project Settings → Autoload
2. Add `res://autoload/events.gd`
3. Name it "Events"
4. Enable

### 5. Create UI Scenes

#### CellUI Scene

**Scene Structure:**
```
CellUI (Control)
├── Background (ColorRect)
├── CardDisplay (VBoxContainer)
│   ├── RankLabel (Label)
│   └── SuitLabel (Label)
└── FreezeIndicator (TextureRect)
```

**Script (`cell_ui.gd`):**
```gdscript
class_name CellUI
extends Control

signal cell_clicked(row: int, col: int)

var cell: GridCellResource
@onready var rank_label = $CardDisplay/RankLabel
@onready var suit_label = $CardDisplay/SuitLabel
@onready var freeze_indicator = $FreezeIndicator

func _ready():
    if cell:
        update_display()

func set_cell(new_cell: GridCellResource):
    cell = new_cell
    if cell:
        # Connect to cell signals
        cell.cell_changed.connect(update_display)
        cell.freeze_changed.connect(update_freeze_indicator)
        update_display()

func update_display():
    if not cell or not cell.card:
        rank_label.text = ""
        suit_label.text = ""
        return

    rank_label.text = cell.card.rank
    suit_label.text = _get_suit_symbol(cell.card.suit)

    # Color by suit
    var color = Color.RED if cell.card.suit in ["H", "D"] else Color.BLACK
    rank_label.add_theme_color_override("font_color", color)
    suit_label.add_theme_color_override("font_color", color)

func update_freeze_indicator():
    freeze_indicator.visible = cell.is_frozen

func _get_suit_symbol(suit: String) -> String:
    const SUIT_SYMBOLS = {
        "H": "♥", "D": "♦", "C": "♣", "S": "♠"
    }
    return SUIT_SYMBOLS.get(suit, suit)

func _gui_input(event: InputEvent):
    if event is InputEventMouseButton and event.pressed:
        cell_clicked.emit(cell.row, cell.col)
```

#### GridUI Scene

**Scene Structure:**
```
GridUI (Control)
└── GridContainer (GridContainer)
    └── CellUI x25 (instantiated)
```

**Script (`grid_ui.gd`):**
```gdscript
class_name GridUI
extends Control

@export var cell_scene: PackedScene
@onready var grid_container = $GridContainer

var game_manager: GameManager

func _ready():
    grid_container.columns = 5
    _create_cells()

func set_game_manager(manager: GameManager):
    game_manager = manager
    _update_all_cells()

func _create_cells():
    for i in range(25):  # 5x5 grid
        var cell_ui = cell_scene.instantiate()
        grid_container.add_child(cell_ui)
        cell_ui.cell_clicked.connect(_on_cell_clicked)

func _update_all_cells():
    if not game_manager:
        return

    var idx = 0
    for row in range(5):
        for col in range(5):
            var cell_ui = grid_container.get_child(idx)
            var cell = game_manager.state.grid[row][col]
            cell_ui.set_cell(cell)
            idx += 1

func _on_cell_clicked(row: int, col: int):
    if game_manager:
        game_manager.toggle_freeze(row, col)
```

### 6. Create Main Scene

**Scene Structure:**
```
Main (Node)
├── GameManager (Node, script attached)
├── UI (CanvasLayer)
│   ├── GridUI (Control)
│   ├── ScorePanel (PanelContainer)
│   │   ├── VBoxContainer
│   │   │   ├── CurrentScoreLabel (Label)
│   │   │   ├── CumulativeScoreLabel (Label)
│   │   │   └── HandsLeftLabel (Label)
│   └── Controls (HBoxContainer)
│       ├── PlayHandButton (Button)
│       └── UnfreezeAllButton (Button)
└── Camera2D
```

**Script (`main.gd`):**
```gdscript
extends Node

@onready var game_manager = $GameManager
@onready var grid_ui = $UI/GridUI
@onready var score_label = $UI/ScorePanel/VBoxContainer/CumulativeScoreLabel
@onready var hands_label = $UI/ScorePanel/VBoxContainer/HandsLeftLabel

func _ready():
    # Set up UI
    grid_ui.set_game_manager(game_manager)

    # Connect signals
    Events.hand_completed.connect(_on_hand_completed)
    Events.score_updated.connect(_on_score_updated)
    Events.game_won.connect(_on_game_won)
    Events.game_lost.connect(_on_game_lost)

    # Start game
    game_manager.start_new_round()
    _update_ui()

func _on_play_hand_button_pressed():
    if game_manager.play_hand():
        game_manager.auto_refreeze_if_better()
        game_manager.score_and_update()

func _on_unfreeze_all_button_pressed():
    game_manager.unfreeze_all()

func _on_hand_completed():
    _update_ui()

func _on_score_updated(current: int, cumulative: int):
    score_label.text = "Score: %d" % cumulative

func _update_ui():
    hands_label.text = "Hands: %d/%d" % [
        game_manager.state.hands_taken,
        game_manager.config.max_hands
    ]

func _on_game_won(score: int):
    _show_end_screen("YOU WIN!", score)

func _on_game_lost(score: int):
    _show_end_screen("Game Over", score)

func _show_end_screen(title: String, score: int):
    # Create end screen popup
    var dialog = AcceptDialog.new()
    dialog.title = title
    dialog.dialog_text = "Final Score: %d" % score
    add_child(dialog)
    dialog.popup_centered()
```

## Key Differences to Remember

### 1. Signals vs Callbacks

**Python:**
```python
cell._on_changed_callback = some_function
```

**GDScript:**
```gdscript
cell.cell_changed.connect(some_function)
```

### 2. Array Typing

**Python:**
```python
cards: List[CardResource]
```

**GDScript:**
```gdscript
var cards: Array[CardResource]
```

### 3. Dictionary Typing

**Python:**
```python
rank_values: Dict[str, int]
```

**GDScript:**
```gdscript
var rank_values: Dictionary  # No generic typing for Dictionary
```

### 4. Class Methods

**Python:**
```python
@staticmethod
def evaluate_hand(cards):
    pass
```

**GDScript:**
```gdscript
static func evaluate_hand(cards: Array[CardResource]) -> HandResource:
    pass
```

### 5. Enums

**Python:**
```python
class HandType(Enum):
    ROYAL_FLUSH = "Royal Flush"
```

**GDScript:**
```gdscript
enum HandType {
    ROYAL_FLUSH,
    STRAIGHT_FLUSH,
    # ...
}

const HAND_TYPE_NAMES = {
    HandType.ROYAL_FLUSH: "Royal Flush",
    # ...
}
```

## Testing Checklist

- [ ] Cards display correctly
- [ ] Freezing/unfreezing works
- [ ] Playing a hand deals new cards
- [ ] Scoring calculates correctly
- [ ] Signals fire as expected
- [ ] Game win/lose conditions work
- [ ] UI updates reactively
- [ ] No error messages in console

## Common Issues

### Issue: Resource not updating in Inspector
**Solution:** Call `property_list_changed_notify()` or `notify_property_list_changed()`

### Issue: Signals not firing
**Solution:** Check signal is defined and connected in `_ready()`

### Issue: Null reference errors
**Solution:** Check initialization order, use `is_instance_valid()`

### Issue: Type errors with Arrays
**Solution:** Use untyped Arrays for complex types if needed

## Performance Tips

1. Use object pooling for cells instead of recreating
2. Batch UI updates instead of updating every frame
3. Use `call_deferred()` for non-urgent updates
4. Profile with Godot's built-in profiler

## Next Steps

1. Add animations (tweens for card dealing, scoring)
2. Add sound effects (using AudioStreamPlayer)
3. Add particle effects (for wins, freezes)
4. Create a proper menu system
5. Add save/load using Resources
6. Polish UI with themes

## Resources

- Python codebase: `godot_src/`
- Architecture doc: `GODOT_ARCHITECTURE.md`
- Godot docs: https://docs.godotengine.org/
