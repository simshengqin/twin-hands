# Manual Test Scripts

## What Are These?

These are **manual test scripts** - quick programs you run to visually test specific features during development.

## Type of Tests

### Manual Tests (This Folder) ⚡
**Purpose:** Quick visual verification during development

**Characteristics:**
- Run with `python test_hand.py`
- Print output to terminal
- Visual inspection required
- No assertions (no pass/fail)
- Interactive/exploratory
- Quick to write

**Example:**
```python
# test_hand.py
game.play_hand()
ui.print_grid()  # Look at it yourself!
print(f"Score: {score}")  # Does it look right?
```

**When to use:**
- Testing game flow visually
- Debugging specific scenarios
- Quick prototyping
- Demonstrating features

### Automated Tests (like party-house/tests/) ✅
**Purpose:** Automated validation of correctness

**Characteristics:**
- Run with `pytest`
- No human needed
- Assertions validate results
- Pass/fail automated
- Can run in CI/CD
- Takes time to write properly

**Example:**
```python
# test_game_state.py
def test_score_adds_to_totals():
    state.active_party = [card1, card2]
    popularity, cash = state.score_hand()

    assert popularity == 1  # Automated check
    assert cash == 1        # Pass or fail
    assert state.popularity == 6
```

**When to use:**
- Regression testing
- CI/CD pipelines
- Complex logic validation
- Before releases

## Files in This Folder

### test_run.py
**What it tests:** Poker hand evaluation
**How to run:** `python tests_manual/test_run.py`

Prints all poker hands (Royal Flush, Straight, etc.) to verify scoring works.

```
Testing Poker Evaluator:
========================================
Royal Flush Test: Royal Flush - 800 chips
Straight Flush Test: Straight Flush - 400 chips
...
```

### test_hand.py
**What it tests:** Single hand mechanics
**How to run:** `python tests_manual/test_hand.py`

Shows grid before and after one hand to verify dealing works.

```
Initial grid:
[A♥] [K♦] [Q♣] [J♠] [T♥]
...

--- Playing hand ---
Hand 1 complete!
...
```

### test_autofreeze.py
**What it tests:** Auto-freeze priority system
**How to run:** `python tests_manual/test_autofreeze.py`

Tests 3 scenarios:
1. Aligned pair (Priority 1)
2. Suited cards (Priority 2)
3. No freeze (Priority 3)

```
TEST 1: Aligned Pair (Priority 1)
========================================
[A♥*] [K♦] [A♦*] [J♠] [T♥]
Expected: Pair of Aces (same row)
```

## Comparison Table

| Feature | Manual Tests | Automated Tests |
|---------|--------------|-----------------|
| **Run with** | `python test_*.py` | `pytest` |
| **Output** | Terminal prints | Pass/fail report |
| **Validation** | Human eyes | Assertions |
| **Speed** | Fast to write | Slow to write |
| **Coverage** | Spotty | Comprehensive |
| **CI/CD** | ❌ Can't use | ✅ Can use |
| **Debugging** | ✅ Great | ❌ Harder |
| **Regression** | ❌ Manual check | ✅ Automated |

## Party-House Tests (for comparison)

The `party-house/tests/` folder has **professional automated tests**:

### Structure
```
party-house/tests/
├── conftest.py              # Pytest fixtures (shared setup)
├── test_game_state.py       # Core game logic tests
├── test_abilities.py        # Card ability tests
├── test_economy.py          # Cash/popularity tests
├── test_progression.py      # Blind progression tests
└── ...
```

### Key Differences

**1. Uses pytest framework:**
```python
# conftest.py - shared fixtures
@pytest.fixture
def fresh_state():
    return GameState()

# test_game_state.py - test classes
class TestGameInitialization:
    def test_fresh_game_state_defaults(self, fresh_state):
        state = fresh_state
        assert state.current_blind == 1  # Automated
        assert state.cash == 0           # Automated
```

**2. Has assertions everywhere:**
```python
def test_score_adds_to_totals(fresh_state, sample_cards):
    state = fresh_state
    state.active_party = [card1, card2]

    popularity, cash = state.score_hand()

    assert popularity == 1        # ✅ Pass or ❌ Fail
    assert cash == 1
    assert state.popularity == 6
```

**3. Organized by feature:**
- `test_game_state.py` - Game loop
- `test_abilities.py` - Ability system
- `test_economy.py` - Cash/popularity
- `test_progression.py` - Blind advancement

**4. Comprehensive coverage:**
```python
class TestDrawMechanics:
    def test_draw_guest_removes_from_pile()
    def test_draw_empty_pile_returns_none()
    def test_drawn_cards_are_independent_instances()

class TestShutdownMechanics:
    def test_shutdown_with_too_much_trouble()
    def test_no_shutdown_below_threshold()
    def test_flags_cancel_trouble()
```

Every edge case is tested!

## When to Use Each Type

### Use Manual Tests When:
- ✅ Prototyping new features
- ✅ Visual debugging
- ✅ Quick validation
- ✅ Demonstrating to others
- ✅ Testing UI/display

### Use Automated Tests When:
- ✅ Complex game logic
- ✅ Before releases
- ✅ Regression prevention
- ✅ CI/CD pipelines
- ✅ Critical systems

## Example Workflow

### Development Phase (Use Manual Tests)
```bash
# Implementing new feature
python tests_manual/test_hand.py
# Does it look right? Yes!

# Quick iteration
# Edit code...
python tests_manual/test_hand.py
# Better? Yes!
```

### Release Phase (Use Automated Tests)
```bash
# Before release
pytest party-house/tests/
# 87 passed in 2.3s ✅

# All edge cases covered
# Ready to deploy!
```

## Creating New Tests

### Quick Manual Test
```python
# tests_manual/test_my_feature.py
from game_state import GameStateManager
from ui import TerminalUI

game = GameStateManager()
game.start_new_round()

# Test something
game.my_new_feature()

# Print and look
ui = TerminalUI(game)
ui.print_grid()
print("Does this look right?")
```

### Proper Automated Test
```python
# tests/test_my_feature.py
import pytest
from game_state import GameStateManager

def test_my_feature_works_correctly():
    game = GameStateManager()
    game.start_new_round()

    result = game.my_new_feature()

    assert result == expected_value
    assert game.state.something == correct_value
```

## Recommendation for Poker Grid

### Now (Development)
Keep using **manual tests** for:
- Quick visual checks
- Debugging game flow
- Testing UI display

### Future (Production)
Add **automated tests** for:
- Poker hand evaluation
- Freeze/unfreeze logic
- Scoring calculations
- Win/lose conditions

Example structure:
```
poker-grid/
├── tests_manual/        # Quick visual tests
│   ├── test_hand.py
│   └── test_autofreeze.py
│
└── tests/               # Automated tests (future)
    ├── conftest.py
    ├── test_poker_evaluator.py
    ├── test_game_manager.py
    └── test_scoring.py
```

## Summary

**Manual Tests (tests_manual/):**
- Quick and dirty
- For development
- Visual inspection
- No automation

**Automated Tests (like party-house/tests/):**
- Professional
- For production
- Assertions validate
- Can automate

Both have their place! Manual tests are great for development speed, automated tests are essential for production quality.
