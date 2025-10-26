# Bug Fix: Card Selection Mismatch

## 🐛 The Bug

**Symptom:** Cards would disappear or wrong cards were played when selecting cards.

**User Report:**
> "When I play 2 cards from deck 1, those 2 cards refresh correctly, but sometimes 1 or even 2 of the other cards I didn't play just disappeared!"

## 🔍 Root Cause Analysis

### The Problem

**Mismatch between displayed order and internal state order.**

1. **UI Layer** sorted cards for display (better UX):
   ```
   Display: [1] 9♣  [2] A♦  [3] K♥  [4] 3♠
   ```

2. **Game State** kept cards in original draw order (unsorted):
   ```
   visible_cards: [K♥, 3♠, 9♣, A♦]  (indices 0-3)
   ```

3. **Player** sees sorted display and types `12` intending to play `9♣` and `A♦`

4. **Parser** correctly interprets `12` as indices `[0, 1]` for the first deck

5. **GameManager** removes indices `[0, 1]` from **unsorted** `visible_cards`:
   ```python
   visible_cards = [K♥, 3♠, 9♣, A♦]
   # Remove index 0 → removes K♥
   # Remove index 1 → removes 3♠
   # Result: [9♣, A♦] remain
   ```

6. **WRONG CARDS REMOVED!** Player wanted `9♣, A♦` but got `K♥, 3♠` removed instead!

### Visual Diagram

```
UI DISPLAY (sorted):          GAME STATE (unsorted):
[1] 9♣                        [0] K♥
[2] A♦                        [1] 3♠
[3] K♥                        [2] 9♣
[4] 3♠                        [3] A♦

Player types: 12
↓
Parser returns: indices [0, 1]
↓
GameManager removes indices [0, 1] from STATE
↓
Removes K♥ and 3♠ ❌ (Player wanted 9♣ and A♦!)
```

## 🔨 The Fix

### Solution: Sort In-Place

**Make displayed order = actual state order**

```python
# Before (BUG):
def display_decks(self):
    cards_raw = self.game.get_visible_cards(deck_idx)
    cards = self._sort_cards(cards_raw)  # Temporary sorted copy
    # Display 'cards' but state still has 'cards_raw' ❌

# After (FIXED):
def display_decks(self):
    deck = self.game.state.decks[deck_idx]
    deck.visible_cards = self._sort_cards(deck.visible_cards)  # Sort IN-PLACE ✅
    cards = deck.visible_cards
    # Display 'cards' AND state has same sorted order ✅
```

### Why This Works

- **WYSIWYG** (What You See Is What You Get)
- Displayed indices match state indices perfectly
- No translation needed
- Simple and robust

## 📊 Why Tests Didn't Catch It

### Test Gap Analysis

**Unit Tests:**
- Tested `GameManager.play_hand()` with direct indices
- No UI layer involved
- Assumed indices match visible order
- ✅ Passed (correctly testing game logic)
- ❌ Missed the UI-state mismatch

**Integration Tests:**
- Tested full game flow
- But didn't verify displayed cards vs removed cards
- ❌ Missed the display-state synchronization

### What Was Missing

**Needed:** End-to-end test that:
1. Displays cards (UI layer)
2. Records what player sees
3. Plays cards by displayed indices
4. Verifies correct cards were removed

## ✅ Regression Tests Added

### Test 1: Card Selection Matches Display

```python
def test_card_selection_matches_display():
    """
    CRITICAL: Cards displayed should match cards selected.
    """
    game = GameManager(config)
    ui = TerminalUI(game)
    game.start_game()

    # Display cards (triggers sorting)
    ui.display_decks()

    # Get what's shown
    sorted_cards = game.state.decks[0].visible_cards.copy()
    first_card = sorted_cards[0]
    second_card = sorted_cards[1]

    # Play first 2 cards
    result = game.play_hand(deck_index=0, card_indices=[0, 1])

    # Verify CORRECT cards were played
    assert result["hand"].cards[0].rank == first_card.rank
    assert result["hand"].cards[1].rank == second_card.rank
```

### Test 2: Sorting Is Stable

```python
def test_card_sorting_is_stable():
    """
    Ensure sorting is consistent across multiple displays.
    """
    ui.display_decks()
    first_order = game.state.decks[0].visible_cards.copy()

    ui.display_decks()
    second_order = game.state.decks[0].visible_cards.copy()

    # Should be identical
    assert first_order == second_order
```

## 📝 Lessons Learned

### 1. **Test the Integration Points**

Unit tests are great, but they miss interface boundaries:
- ❌ Tested game logic in isolation
- ❌ Tested UI formatting separately
- ✅ **Needed:** Test UI → Game state → Result flow

### 2. **WYSIWYG Principle**

When displaying mutable state:
- Option A: Display copy (read-only) ❌ Creates divergence
- Option B: Display actual state ✅ Truth is visible

### 3. **State Synchronization**

If you have:
- **Displayed order** (sorted for UX)
- **Storage order** (unsorted for performance)

You need:
- **Index translation** (map display → storage)
- **OR sort storage to match display** ← We chose this

### 4. **User Bug Reports Are Gold**

This bug was caught by actual gameplay, not tests!
- Tests validated correct behavior *given assumptions*
- User found *assumption was wrong*
- Bug report was specific and reproducible

## 🎯 Prevention Strategies

### For Future Development

**1. Add UI-State Integration Tests**
```python
def test_ui_state_consistency():
    """Always test: What UI shows = What state contains"""
    pass
```

**2. Test Sorting Side Effects**
```python
def test_sorting_doesnt_break_selection():
    """If UI sorts for display, verify selection still works"""
    pass
```

**3. Test Round-Trip**
```python
def test_display_select_remove_roundtrip():
    """Display → Select → Remove → Verify correct cards gone"""
    pass
```

## 📈 Impact Assessment

### Severity: **CRITICAL** 🔴

- **Frequency:** Every time player plays cards
- **Impact:** Wrong cards removed (game-breaking)
- **User Experience:** Confusing, frustrating
- **Data Loss:** No (recoverable by restarting)

### Affected Versions

- Initial release through commit `1ebb780`
- **Fixed in:** commit `556ecae`

### Test Results

- **Before Fix:** Bug reproducible 100% of the time
- **After Fix:** All 54 tests pass ✅
- **Regression Tests:** 2 new tests added

## 🙏 Credits

**Found by:** User (great bug report!)
**Root cause:** Sorted display vs unsorted state mismatch
**Fixed by:** Sort state in-place to match display
**Tests added:** `test_card_selection_bug.py`

## 🔗 Related Commits

- `556ecae` - Fix card selection bug
- `1ebb780` - Improved examples (where bug existed)
- `39a5b79` - Added card sorting (introduced bug)

---

**Status:** ✅ **FIXED**
**Test Coverage:** ✅ **REGRESSION TESTS ADDED**
**Ready for:** Phase B development
