# Claude Instructions for Twin Hands

## � CRITICAL: THREE NON-NEGOTIABLE RULES

### RULE 1: ALWAYS REFER TO GDD - NEVER ASSUME

**When implementing ANY feature:**

1. **Read `docs/gdd/GDD.md` section relevant to the feature**
2. **If GDD is unclear or contradictory, ASK CLARIFICATION QUESTIONS**
3. **Never assume game mechanics - always verify against GDD**

**Example of doing it RIGHT:**
```
S Question: "In GDD section 4-3, it says 'max 2 hands per deck'.
   Does this mean max 2 per round total, or max 2 per deck per round?"

 Wait for answer, then implement
```

**Example of doing it WRONG:**
```
L "I'll assume max 2 hands per deck means total for the round..."
L Implements based on assumption
L Wrong implementation, wasted time
```

**GDD Sections Quick Reference:**
- Design Goals: Section 1
- Core Mechanics: Section 4
  - 4-1: Deck Splitting
  - 4-2: Card Drawing
  - 4-3: Token System
  - 4-4: Trading
  - 4-5: Jokers
  - 4-6: Round Flow
  - 4-7: Hand Scoring
- Progression: Section 5

### RULE 2: TEST-FIRST ARCHITECTURE (RED � GREEN � REFACTOR)

**EVERY new component follows this cycle:**

1. **=4 RED:** Write test first (it fails)
2. **=� GREEN:** Write minimal code to pass test
3. **=5 REFACTOR:** Make it Godot-ready, add signals, clean up

### RULE 3: GODOT-READY ARCHITECTURE

**Follow poker-grid's proven patterns:**
- Resources = Data only (extends Resource)
- Managers = Logic only (extends Node)
- Utils = Static helpers
- Events = Global singleton (AutoLoad)

**See poker-grid/src/docs/GODOT_ARCHITECTURE.md for full details**

### RULE 4: EVERYTHING CONFIGURABLE

**Make ALL game parameters configurable:**
- Token counts (hand tokens, trade tokens)
- Slot limits (joker slots, max hands per deck)
- Scoring values (hand scores, multipliers)
- Progression values (round quotas, scaling)

**Config Pattern:**
```python
# ✅ GOOD - configurable
class TwinHandsConfig:
    hand_tokens_per_round: int = 4  # Lowercase instance attr
    trade_tokens_per_round: int = 3
    max_hands_per_deck: int = 2

    HAND_SCORES = {...}  # UPPERCASE class constants

# ✅ GOOD - use config values
def play_hand(self):
    if hands_played >= self.config.max_hands_per_deck:  # From config
        return False

# ❌ BAD - hardcoded magic numbers
def play_hand(self):
    if hands_played >= 2:  # Magic number!
        return False
```

**Benefits:**
- Easy balancing and testing
- Fast iteration on game feel
- No hunting through code to change values

### RULE 5: i18n-READY (Not implemented, but architected for)

**We focus on English/solo now, but design so i18n is painless later:**

**Pattern: Separate data from text**
```python
# ❌ BAD - NOT i18n-ready
class GameManager:
    def start_round(self):
        print("Round 5 started!")  # Hardcoded English in logic

# ✅ GOOD - i18n-ready
class GameManager:
    def start_round(self):
        Events.emit_round_started(self.state.current_round)  # Just data

# UI layer formats the text
class TerminalUI:
    def on_round_started(self, round_num):
        print(f"Round {round_num} started!")  # Text only in UI
```

**Rules:**
- All UI strings ONLY in UI layer (never in managers/resources)
- Emit data via events, let UI format it
- Use dict keys for hand names: `hand.name = "Royal Flush"` (key for lookup)
- Future: UI swaps out text dict based on language

**We won't implement i18n now, but this pattern costs nothing and saves massive refactoring later.**

### RULE 6: MULTIPLAYER-READY (Not implemented, but architected for)

**We focus on solo now, but design so co-op/competitive is painless later:**

**Pattern: State as truth, deterministic logic, event communication**
```python
# ✅ GOOD - multiplayer-ready (GDD Section 6 co-op compatible)
class GameManager:
    def play_hand(self, deck_side: str, card_indices: List[int]):
        """
        Solo: Player controls both "left" and "right"
        Co-op: Player 1 = "left", Player 2 = "right" (GDD 6)
        """
        # Validate action
        if not self._can_play_hand(deck_side):
            return False

        # Execute deterministically (same input = same output)
        hand = self._evaluate_hand(deck_side, card_indices)
        self.state.update_score(deck_side, hand.score)

        # Communicate via events (can be networked)
        Events.emit_hand_played(deck_side, hand)
        return True
```

**Rules:**
- State is single source of truth (can be synced)
- All actions are pure data (serializable/networkable)
- Logic is deterministic (same state + action = same result)
- Communication via events (can be network messages)
- `deck_side` parameter already maps to players in co-op (GDD 6)

**We won't implement multiplayer now, but this pattern is already natural for our game design.**

---

## <� BUILD STRATEGY: PLAYABLE FIRST

### Phase A: MINIMAL PLAYABLE (2-3 days)
**Priority:** Get playable ASAP to test feel

**Include:**
- Split deck (GDD 4-1)
- 4 visible cards per deck (GDD 4-2)
- Play hands, basic scoring (GDD 4-7)
- 4 hand tokens, max 2 per deck (GDD 4-3)
- Terminal UI

**Exclude:**
- Trading (Phase B)
- Jokers (Phase B)
- Shop (Phase C)

### Phase B: CORE LOOP (+2 days)
- Add trading (GDD 4-4)
- Add basic Jokers (GDD 4-5, no Bridge yet)
- Per-Deck Mult scoring

### Phase C: FEEL-TESTABLE (+2-3 days)
- Bridge Jokers (trigger twice)
- Shop system
- Full 8-round progression

---

## =� IMPLEMENTATION ORDER (Phase A)

### Day 1: Foundation
1. Copy reusable files from poker-grid
2. Create TwinHandsConfig (TEST-FIRST, verify against GDD)
3. Create TwinHandsState (TEST-FIRST, verify against GDD)

### Day 2: Core Managers
1. **ASK CLARIFICATION QUESTIONS FIRST**
2. Create DeckManager (TEST-FIRST)
3. Create TokenManager (TEST-FIRST)
4. Create ScoringManager (TEST-FIRST, basic version)

### Day 3: Playable!
1. Create GameManager (TEST-FIRST)
2. Create Terminal UI
3. **PLAY IT!**

---

## =� WHEN TO ASK QUESTIONS

**Always ask if:**
- GDD wording is ambiguous
- Multiple interpretations possible
- Feature not described in GDD
- Contradiction between sections
- Unclear edge case

**Example good questions:**
-  "GDD 4-4: Can I trade 0 cards (skip trade)?"
-  "GDD 4-5: Do Bridge Jokers trigger during each deck's scoring, or once at end?"
-  "GDD 5-3: Should Round 8 quota be exactly 1,882 or rounded?"

---

## =� QUICK REFERENCE

**GDD Location:** `docs/gdd/GDD.md`

**poker-grid Reusables:** (copy AS-IS)
- `poker-grid/src/utils/poker_evaluator.py`
- `poker-grid/src/resources/card_resource.py`
- `poker-grid/src/resources/deck_resource.py`
- `poker-grid/src/utils/card_factory.py`
- `poker-grid/src/autoload/events.py`

**poker-grid Patterns:** (adapt for Twin Hands)
- `poker-grid/src/managers/game_manager.py` - How to structure managers
- `poker-grid/tests/test_game_manager.py` - How to test
- `poker-grid/src/docs/GODOT_ARCHITECTURE.md` - Full architecture guide

---

##  SUCCESS CHECKLIST

**Before calling Phase A complete:**
- [ ] Read GDD Section 4 (Core Mechanics)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Game runs (`python run.py`)
- [ ] Can play 1-2 rounds
- [ ] Features match GDD specs
- [ ] Code is Godot-ready
- [ ] Asked questions when unsure

**You're doing it RIGHT if:**
-  Reading GDD before every feature
-  Writing tests before code
-  Following poker-grid patterns
-  Asking clarification questions

**You're doing it WRONG if:**
- L Implementing without reading GDD
- L Skipping tests
- L Assuming mechanics
- L Ignoring poker-grid patterns

---

## <� THE THREE COMMANDMENTS

1. **READ GDD FIRST** - Every feature, every time
2. **TEST FIRST** - RED � GREEN � REFACTOR
3. **GODOT-READY** - Follow poker-grid patterns

**When in doubt:**
1. Read GDD section
2. If unclear, ASK
3. Look at poker-grid example
4. Write test first
5. Implement
6. Make Godot-ready

**LET'S BUILD! =�**
