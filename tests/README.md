# Poker Grid Test Suite

Comprehensive test suite for Poker Grid game logic. All tests designed to port easily to **Godot GUT**.

## Running Tests

### Python (pytest)

```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_deck_system.py

# Run specific test class
pytest tests/test_deck_system.py::TestDeckCreation

# Run specific test
pytest tests/test_deck_system.py::TestDeckCreation::test_standard_deck_has_52_cards

# Run with coverage
pip install pytest-cov
pytest --cov=src tests/
```

### Godot (after porting to GUT)

1. Install **GUT** (Godot Unit Test) from Asset Library
2. Port tests to GDScript (see porting guide below)
3. Place tests in `res://tests/`
4. Run from GUT panel in Godot Editor

## Test Organization

### test_deck_system.py (24 tests)
Tests the Balatro-style single deck with replacement:
- Deck creation and validation
- Draw with replacement (duplicates allowed)
- Deck mutation (add/remove cards for future shop)
- Deck persistence across hands/rounds
- CardFactory deck creation

**Key features tested:**
- ✅ Deck always has 52 cards after drawing
- ✅ Duplicates possible and expected
- ✅ Deck persists (never shuffled or reset)
- ✅ Future-proof for deck building mechanics

### test_grid_manager.py (26 tests)
Tests grid operations and freeze logic:
- Grid dealing from deck
- Cell freezing (up to 2 cells)
- Auto-freeze highest pair logic
- Auto-freeze prefers aligned pairs
- Frozen cells persist across hands

**Key features tested:**
- ✅ deal_grid() draws from single deck
- ✅ Frozen cells never change
- ✅ Auto-freeze finds and prioritizes pairs
- ✅ Grid can have duplicate cards

### test_scoring.py (33 tests)
Tests poker hand evaluation and scoring:
- All 10 poker hands detected correctly
- Poker hands with duplicate cards (replacement)
- Edge cases (Ace-low straights)
- ScoreManager integration
- Score accumulation

**Key features tested:**
- ✅ Royal Flush through High Card
- ✅ Duplicates don't break evaluation
- ✅ Scores accumulate correctly
- ✅ Hand scores match config

### test_game_flow.py (29 tests)
Tests game progression and state management:
- Game initialization
- Playing hands (7 per round)
- Freeze system during gameplay
- Round completion
- Win/lose conditions
- Deck and score persistence

**Key features tested:**
- ✅ Can play 7 hands per round
- ✅ Frozen cells persist across all hands
- ✅ Deck stays 52 cards throughout
- ✅ Score accumulates across rounds
- ✅ Win when quota reached

### test_config.py (22 tests)
Tests configuration validation:
- Default values
- Card constants (ranks, suits, values)
- Hand score constants
- Config modification and duplication

**Key features tested:**
- ✅ All defaults correct
- ✅ Hand scores in correct order
- ✅ Config is modifiable
- ✅ Values are sensible

## Total: 134 Tests

## Test Coverage

### Critical Paths Tested ✅
- ✅ Deck system (with replacement)
- ✅ Grid dealing and freezing
- ✅ All poker hands
- ✅ Game flow (start → play → score → win/lose)
- ✅ Frozen cells persistence
- ✅ Score accumulation
- ✅ Duplicate cards in grid

### What's NOT Tested ❌
- ❌ UI/Display (terminal UI, legacy code)
- ❌ Input handling (CLI-specific)
- ❌ Events system (signals, callbacks)
- ❌ RNG specifics (too random to test reliably)

## Porting to Godot GUT

All tests follow these rules for easy porting:

### 1. **Godot-Compatible Structure**
- Only test game logic (no Python-specific features)
- Use game systems (GameManager, Resources, Managers)
- Clear AAA pattern (Arrange → Act → Assert)
- No external dependencies

### 2. **Syntax Changes**

**Python → GDScript:**

```python
# Python (pytest)
def test_something(self):
    assert value == expected
    assert len(list) == 5
    assert card is not None
```

```gdscript
# GDScript (GUT)
func test_something():
    assert_eq(value, expected)
    assert_eq(list.size(), 5)
    assert_ne(card, null)
```

**Common Conversions:**
- `assert x == y` → `assert_eq(x, y)`
- `assert x != y` → `assert_ne(x, y)`
- `assert x` → `assert_true(x)`
- `assert not x` → `assert_false(x)`
- `assert x > y` → `assert_gt(x, y)`
- `len(list)` → `list.size()`
- `is None` → `== null`
- `isinstance(obj, Type)` → `obj is Type`

### 3. **Fixture → Setup Methods**

**Python:**
```python
@pytest.fixture
def fresh_game():
    return GameManager()
```

**GDScript:**
```gdscript
var fresh_game: GameManager

func before_each():
    fresh_game = GameManager.new()
```

### 4. **Import Changes**

**Python:**
```python
from src.managers.game_manager import GameManager
```

**GDScript:**
```gdscript
const GameManager = preload("res://managers/game_manager.gd")
```

### Estimated Port Time
- **Per test file**: 20-30 minutes
- **Total suite**: ~2-3 hours
- **Mostly syntax changes** (no logic changes needed)

## Continuous Testing

Run tests before:
- ✅ Committing changes
- ✅ Adding new features
- ✅ Tweaking game balance
- ✅ Porting to Godot

Tests catch regressions early!

## Adding New Tests

When adding features:

1. **Write test first (TDD)**
2. **Follow existing patterns**
3. **Keep tests Godot-portable**
4. **Test one concept per test**
5. **Use descriptive names**

**Example:**
```python
def test_new_feature_does_expected_thing(self, fresh_game):
    """Clear description of what's being tested"""
    # ARRANGE
    game = fresh_game
    game.state.some_value = 10

    # ACT
    result = game.do_something()

    # ASSERT
    assert result == 20
    assert game.state.some_value == 10  # Unchanged
```

## Balance Testing

Use tests to validate balance changes:

```bash
# Before changing hand scores
pytest tests/test_scoring.py -v

# After changing hand scores
pytest tests/test_scoring.py -v

# Check what broke (if anything)
```

## Performance

All 134 tests run in **~1 second** on modern hardware.

For CI/CD:
```bash
pytest tests/ --tb=short --maxfail=1
```

## Test-Driven Development

The tests are designed for TDD:

1. **Red**: Write a failing test
2. **Green**: Make it pass
3. **Refactor**: Clean up code

Example workflow:
```bash
# Write new test
pytest tests/test_deck_system.py::test_new_feature -v
# (Test fails)

# Implement feature
# (Edit code)

# Re-run test
pytest tests/test_deck_system.py::test_new_feature -v
# (Test passes!)
```

## Why These Tests Matter

### 1. **Deck System Validation**
The deck refactor (5 reels → 1 deck with replacement) is a major change. Tests ensure:
- Deck always has 52 cards
- Duplicates work correctly
- Frozen cards persist
- No cards "leak" from deck

### 2. **Poker Hand Correctness**
With duplicates now possible, tests verify:
- Four of a Kind with 4 identical cards works
- Pairs from same card work
- All edge cases handled

### 3. **Game Balance**
Tests validate:
- 7 hands per round is playable
- Quota targets are achievable
- Scoring accumulates correctly

### 4. **Future-Proofing**
Tests enable safe refactoring for:
- Balatro scoring (chips × mult)
- Joker system
- Shop mechanics
- Deck mutations

## Bugs Caught During Development

These tests caught bugs during the deck refactor:

- ✅ Deck size not preserved after draw
- ✅ Frozen cells being redrawn
- ✅ Auto-freeze breaking with duplicates
- ✅ Score not accumulating correctly
- ✅ Hands counter not decrementing

## Godot GUT Resources

- **Documentation**: https://gut.readthedocs.io/
- **GitHub**: https://github.com/bitwes/Gut
- **Asset Library**: Search "GUT - Godot Unit Testing"
- **Version**: GUT 9.x for Godot 4.x

## Questions?

- Check existing tests for patterns
- Read `src/docs/GODOT_ARCHITECTURE.md` for architecture
- See `party-house/tests/` for reference (similar structure)

## Contributing

When adding tests:
1. Follow the existing structure
2. Keep tests simple and focused
3. Use descriptive names
4. Add comments for complex setup
5. Ensure tests are Godot-portable

**Don't test:**
- UI rendering (terminal output)
- Random number generation specifics
- Event system internals
- Performance benchmarks

**Do test:**
- Game logic and rules
- State management
- Scoring calculations
- Win/lose conditions
- Feature interactions
