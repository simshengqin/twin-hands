# Testing Guide for Twin Hands

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── unit/                          # Unit tests (mirrors src/ structure)
│   ├── managers/                  # Tests for src/managers/
│   ├── resources/                 # Tests for src/resources/
│   └── utils/                     # Tests for src/utils/
├── integration/                   # Integration tests
│   └── test_game_manager_flow.py  # Full game loop tests
└── gdd_compliance/                # GDD specification tests
    ├── test_deck_splitting_4_1.py
    ├── test_card_drawing_4_2.py
    ├── test_token_system_4_3.py
    ├── test_trading_system_4_4.py
    ├── test_joker_system_4_5.py
    ├── test_round_flow_4_6.py
    └── test_hand_scoring_4_7.py
```

## Test Categories

### 1. Unit Tests (70%)
**Purpose:** Test individual managers and resources in isolation.

**Location:** `tests/unit/`

**Example:**
```python
# tests/unit/managers/test_token_manager.py
def test_spend_hand_token():
    token_mgr = TokenManager(config, state)
    assert token_mgr.spend_hand_token(deck_index=0) == True
    assert state.hand_tokens == 3
```

**What to test:**
- Manager logic (TokenManager, DeckManager, ScoringManager)
- Resource validation (TwinHandsConfig, TwinHandsState)
- Utility functions (poker_evaluator, card_factory)

### 2. Integration Tests (20%)
**Purpose:** Test how managers work together through GameManager.

**Location:** `tests/integration/`

**Example:**
```python
# tests/integration/test_game_manager_flow.py
def test_play_hand_full_flow():
    game = GameManager(config)
    game.start_round()
    result = game.play_hand(deck_index=0, card_indices=[0, 1, 2, 3, 4])

    assert result.success == True
    assert game.state.hand_tokens == 3  # Token spent
    assert game.state.scores[0] > 0     # Score updated
```

**What to test:**
- Full round lifecycle (start → play → score → end)
- Manager interactions
- Game state consistency

### 3. GDD Compliance Tests (10%)
**Purpose:** Verify game rules match GDD specifications.

**Location:** `tests/gdd_compliance/`

**Example:**
```python
# tests/gdd_compliance/test_token_system_4_3.py
def test_max_2_hands_per_deck_per_round():
    """GDD 4-3: Max 2 hands per deck."""
    game.play_hand(deck_index=0, ...)  # 1st hand
    game.play_hand(deck_index=0, ...)  # 2nd hand
    result = game.play_hand(deck_index=0, ...)  # 3rd hand
    assert result.success == False
```

**What to test:**
- GDD Section 4-1: Deck splits into 2x 26 cards
- GDD Section 4-3: 4 hand tokens, 3 trade tokens, max 2 hands/deck
- GDD Section 4-7: Hand scoring values match GDD table

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run specific category
```bash
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v             # Integration tests only
pytest tests/gdd_compliance/ -v          # GDD compliance tests only
```

### Run specific file
```bash
pytest tests/unit/managers/test_token_manager.py -v
```

### Run specific test
```bash
pytest tests/gdd_compliance/test_token_system_4_3.py::TestGDD_4_3_TokenSystem::test_max_2_hands_per_deck -v
```

## Writing Tests

### Naming Conventions
- **Test files:** `test_<module_name>.py`
- **Test classes:** `Test<ClassName>` or `TestGDD_<section>_<topic>`
- **Test functions:** `test_<what_it_tests>`

### Example Test Structure
```python
"""
Module docstring explaining what this file tests.
"""

import pytest


class TestMyClass:
    """Test MyClass functionality."""

    def test_simple_case(self):
        """Test description."""
        # Arrange
        obj = MyClass()

        # Act
        result = obj.do_something()

        # Assert
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case description."""
        # ...
```

## Test Coverage Goals

**Phase A (Minimal Playable):**
- ✅ Unit tests for all managers (TokenManager, DeckManager, ScoringManager)
- ✅ GDD compliance for core mechanics (4-1, 4-2, 4-3, 4-7)
- ✅ Integration tests for basic game flow

**Phase B (Core Loop):**
- ✅ GDD compliance for trading (4-4) and jokers (4-5)
- ✅ Integration tests for full round flow

**Phase C (Complete):**
- ✅ All GDD compliance tests passing
- ✅ Full integration test coverage

## Tips

1. **Write tests BEFORE code** (RED → GREEN → REFACTOR)
2. **Use GDD as test specification** - each GDD rule should have a test
3. **Keep tests simple** - one assertion per concept
4. **Use descriptive names** - test names should explain what they verify
5. **Check GDD when unsure** - tests verify against GDD specs
6. **CRITICAL: Tests MUST be config-driven** - NEVER hardcode values that exist in TwinHandsConfig

### Config-Driven Testing (CRITICAL RULE)

**❌ BAD - Hardcoded values:**
```python
def test_token_initialization():
    state = TwinHandsState(config)
    assert state.discard_tokens == 3  # WRONG! Hardcoded value
    assert state.trade_tokens == 2    # WRONG! Hardcoded value
```

**✅ GOOD - Config-driven:**
```python
def test_token_initialization():
    config = TwinHandsConfig(
        discard_tokens_per_round=3,
        trade_tokens_per_round=2
    )
    state = TwinHandsState(config)
    assert state.discard_tokens == config.discard_tokens_per_round  # ✅ From config
    assert state.trade_tokens == config.trade_tokens_per_round      # ✅ From config
```

**Why this matters:**
- If we change config defaults, tests still pass (they test the behavior, not the values)
- Tests verify "does state match config" not "does state have magic number 3"
- Makes tests resilient to balance changes

**Exception:** GDD compliance tests can use hardcoded values to verify GDD specs:
```python
def test_gdd_defaults_match_spec():
    """GDD v6.1 4-3: Default discard tokens = 3"""
    config = TwinHandsConfig()  # Default values
    assert config.discard_tokens_per_round == 3  # ✅ OK - testing GDD spec
```

## Key Lesson: Test Behavior, Not Just Mechanisms

**What we tested:** "Does the mechanism work?" ✅
**What we missed:** "Does the RIGHT thing happen?" ❌

### Example (Card Selection Bug):

**Mechanism test (what we had):**
```python
def test_play_hand_refills_cards():
    game.play_hand(deck_index=0, card_indices=[0, 1])
    assert len(deck.visible_cards) == 4  # ✅ Cards refilled
```
✅ Mechanism works (cards refill)
❌ Didn't check if CORRECT cards were removed

**Behavior test (what we missed):**
```python
def test_correct_cards_removed_and_kept():
    ui.display_decks()  # Player sees sorted: [9♣, A♦, K♥, 3♠]
    card_1 = deck.visible_cards[0]  # 9♣ (will play)
    card_2 = deck.visible_cards[1]  # A♦ (will play)
    card_3 = deck.visible_cards[2]  # K♥ (should stay)
    card_4 = deck.visible_cards[3]  # 3♠ (should stay)

    game.play_hand(deck_index=0, card_indices=[0, 1])  # Play [1][2]

    remaining = deck.visible_cards
    assert card_1 not in remaining  # ✅ Played card gone
    assert card_2 not in remaining  # ✅ Played card gone
    assert card_3 in remaining      # ✅ Other card stayed
    assert card_4 in remaining      # ✅ Other card stayed
```
✅ Tests correctness (right cards removed AND right cards kept)

**Rule:** Don't just test "does it do something" - test "does it do the RIGHT thing".

## Porting to Godot

These tests will translate to Godot's GUT (Godot Unit Test) framework:

**Python → GDScript:**
```python
# Python
def test_spend_token():
    assert token_mgr.spend_hand_token(0) == True
    assert state.hand_tokens == 3
```

```gdscript
# GDScript (GUT)
func test_spend_token():
    assert_true(token_mgr.spend_hand_token(0))
    assert_eq(state.hand_tokens, 3)
```

Almost 1:1 translation!
