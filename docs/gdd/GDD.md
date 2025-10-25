# 🃏 TWIN HANDS (v6.0 – Design Goals Edition)

---

## 🌟 DESIGN GOALS (NORTH STAR)

**These goals guide EVERY design decision. When in doubt, revisit these.**

**Inspired by Balatro's design philosophy:** Exponential power scaling, satisfying number growth, and emergent strategic depth.

---

### **TIER 1: Identity-Defining (Non-Negotiable)**

When these conflict with other goals, **Tier 1 always wins.**

#### **#1: Satisfying Progression (Exponential Power Fantasy)**
- **Players feel godlike by Round 8:** Scores scale from hundreds → thousands
- **Exponential scaling:** Jokers multiply power, not just add
- **Visible growth:** Every Joker purchase makes you noticeably stronger
- **"Number go up" dopamine:** Big numbers, satisfying calculations
- **Success Metric:** Round 8 feels EPIC, not impossible. Players say "I'm so OP!"

#### **#2: Meaningful Decisions Over Busywork**
- **Every action matters:** No repetitive grinding or "going through motions"
- **Visible impact:** Show exactly how each Joker/hand affects score
- **Quality > Quantity:** 4 impactful hands better than 10 tedious ones
- **No hidden math:** Formula is clear: (Left + Right) × Mult
- **Success Metric:** Players think "this choice matters" not "whatever, next"

#### **#3: Casual Friendly Entry (Easy to Start)**
- **Poker familiarity:** Everyone knows poker hands already
- **No tutorial needed:** Start playing Round 1 immediately
- **Clear goals:** "Beat the quota" is instantly understandable
- **Simple base rules:** Complexity emerges from Joker combos, not core mechanics
- **Success Metric:** New players understand Round 1 in < 2 minutes

---

### **TIER 2: Important (Support Tier 1)**

When these conflict with Tier 1, **Tier 1 wins.** Otherwise, preserve these.

#### **#4: Strategic Depth (Emergent, Not Taught)**
- **No obvious optimal play:** Multiple viable strategies each round
- **Depth from interactions:** Joker combos create complexity, not rules
- **Learnable patterns:** High-level strategies emerge through play
- **Hard to master:** Beginners can win, veterans optimize micro-decisions
- **Success Metric:** Community discusses strategies. "I'm running X build" pride.

#### **#5: Highly Replayable (One More Run Loop)**
- **Short sessions:** 20-40 min runs (8 rounds)
- **Variety:** Random Joker shops make every run unique
- **Discovery:** Players find new synergies across runs
- **"One more run" feeling:** Losing makes you want to retry immediately
- **Success Metric:** Players play 5+ runs in one sitting

**Sub-goal 5a: Session Length & Flow**
- Target: 25-35 min per complete run
- 3-5 min per round average
- Can pause/resume between rounds

#### **#6: No RNG Bloat (Player Agency)**
- **Tools to fight bad luck:** Shop refresh, trades, dual decks
- **Skill > Luck:** Good play beats bad RNG consistently
- **Never feel helpless:** Always have options to adapt
- **Fair failures:** "I could have played better" not "bad RNG"
- **Success Metric:** Win rate increases with skill, not just luck

**Sub-goal 6a: Comeback Mechanics**
- Bad rounds don't doom entire run
- Shop flexibility allows pivots
- Can recover with smart Joker repositioning

---

### **TIER 3: Sub-Goals (Nice to Have)**

#### **Player Expression / Build Identity**
- Players CAN pursue archetypes (Flush specialist, Pair engine)
- BUT adaptation to RNG is equally valid
- "This is MY strategy" feeling emerges naturally
- Not forced — expression is possible, not required

#### **Risk vs Reward Tension**
- Optional high-risk plays available
- Unspent tokens = money (conservative play rewarded)
- Future: Hard mode rounds for bonus rewards

---

## 🎯 ELEVATOR PITCH

Build two poker engines from one deck. Trade cards freely, trigger shared Jokers, and break escalating quotas.

A roguelike poker builder where one 52-card deck splits into two specialized hands (Red ♥♦ vs Black ♣♠) that grow, diverge, and synergize.

Manage resources across both decks in a fluid round where every decision matters.

## 🧩 CORE CONCEPT

- **Deck Splitting:** One 52-card deck splits into Left (Red ♥♦) and Right (Black ♣♠) decks of 26 cards each.
- **Free-Form Rounds:** Play, discard, and trade cards in any order using shared tokens.
- **Joker Systems:** Each deck has 3 dedicated Joker slots, plus 2 shared Bridge Joker slots that affect both decks.
- **Escalating Quotas:** Combined score from both decks must meet or exceed quota to advance. Fail = game over.
- **Natural Imbalance:** Decks don't need to score equally — synergy and adaptation matter more than balance.
- **Solo Focus (Co-op = TODO):** Current design is solo play. Co-op mechanics deferred to future updates.

## ♠️ CORE MECHANICS

### 1️⃣ Deck Splitting

- **Starting Split:** Perfect 26/26 — Left Deck (Red ♥♦) vs Right Deck (Black ♣♠).
- **Future TODO:** Randomized or asymmetric splits for unique deck identities.

### 2️⃣ Card Drawing System

- Each deck maintains **4 visible cards** at a time.
- When you play cards, you immediately draw replacements from that deck.
- **Example:** Play 3 cards from left deck → draw 3 new cards from left deck → back to 4 visible.
- Each deck's 26 cards cycle independently throughout the round.

### 3️⃣ Token System (Shared Between Decks)

All tokens are shared resources between both decks:

| Token Type | Amount | Usage | Max Per Deck |
|------------|--------|-------|--------------|
| **Hand Tokens** | 4 per round | Play 1-4 cards to form a poker hand | **Max 2 hands per deck** |
| **Trade Tokens** | 3 per round | Give 1-4 cards one direction (temporary) | 8 card visible limit per deck |

**Key Rules:**
- You can use tokens in any order throughout the round.
- A hand can only be formed from one deck's cards (no mixing).
- **Maximum 2 hands per deck** prevents degenerate "stack-one-side" strategies.
- Each deck has a **hard cap of 8 visible cards** (4 base + 4 from trades max).
- Trade tokens reset each round; traded cards return to their original decks.

**Why Max 2 Hands Per Deck?**
- Prevents optimal strategy from being "stack all 6 Jokers on one side, play 3-0 every round"
- Forces both decks to remain relevant throughout the game
- Encourages 3-3 Joker split or strategic 4-2 splits
- Aligns with Design Goal #4 (Strategic Depth) — no single dominant strategy

### 4️⃣ Trading System

**Temporary Trades (During Round):**
- **One-directional only:** Choose a source deck and give 1-4 cards to the other deck.
- **Giving deck:** Immediately draws replacement cards equal to cards given (stays at 4 visible).
- **Receiving deck:** Accumulates cards up to the 8 card hard cap.
- **Cannot trade if:** Receiving deck would exceed 8 cards.
- **Strategic use:**
  - "Trade away bad cards" = Refresh your hand by giving cards away
  - "Feed the engine" = Stack cards into the deck with better Jokers
  - **Example:** Left has 3 hearts. Right has Flush Joker. Trade 3 hearts from left → right. Left draws 3 new cards. Right now has 7 cards (4 + 3).

**Temporary Trades Reset:**
- At round end, all traded cards return to their original decks.
- Both decks reset to 4 visible cards each for the next round.

**Permanent Trades (Shop Phase):**
- Purchase permanent card transfers in the shop (cost TBD).
- Moves a specific card permanently from one deck to the other.
- One-way transfer: receiving deck cannot give cards back in the same transaction.
- **Example:** Buy "Move A♠ from Right to Left" = A♠ permanently joins left deck for the entire run.

### 5️⃣ Joker System

#### Slot Structure (Fixed)

```
╔════════════════════════════════════════════════════════════╗
║ JOKERS                                                     ║
║ LEFT:   [J1] [J2] [J3]  ┐                                 ║
║ RIGHT:  [J4] [J5] [J6]   ├─→ BRIDGE: [B1] [B2]            ║
║                          ┘                                 ║
╚════════════════════════════════════════════════════════════╝
```

**Slot Configuration:**
- Left Deck: 3 Joker slots
- Right Deck: 3 Joker slots
- Bridge (Shared): 2 Joker slots
- Total: 8 Joker slots (configurable for future expansion)

#### Universal Jokers

**ANY Joker can be placed in ANY slot** — there are no "deck-specific" or "bridge-specific" Joker types.

**Slot determines trigger behavior:**
- **Left Slot:** Joker triggers once during left deck scoring
- **Right Slot:** Joker triggers once during right deck scoring
- **Bridge Slot:** Joker triggers TWICE — once during left deck scoring, once during right deck scoring

**Strategic Choice:** Bridge slots are premium because Joker effects stack (trigger twice per round).

**Example:**
- Joker: "+0.2 mult"
- Placed in Left slot → Triggers once → Global mult becomes 1.2
- Placed in Bridge slot → Triggers twice → Global mult becomes 1.4 (1.0 + 0.2 + 0.2)

**Rarity Tiers:**
- Common, Uncommon, Rare, Legendary
- Higher rarity = stronger effects (pricing TBD)

#### Joker Effects & Terminology

Jokers can modify two components of scoring:

**Points (Additive):**
- Add to deck's total score
- Example: "+50 points when Flush is played"

**Mult (Additive to Global Multiplier):**
- Add to the global multiplier
- Example: "+0.3 mult when Pair is played"
- Global mult starts at 1.0 each round

**Final Score Formula:**
```
Final Score = (Left Deck Points + Right Deck Points) × Global Mult
```

#### Joker Placement Rules

- **When:** Jokers can be freely moved and reordered **during Shop Phase only**.
- **Once Round Starts:** Jokers are locked in position for the entire round.
- **Placement:** When purchasing a Joker, you immediately choose which slot (Left/Right/Bridge) to place it in.
- **Movement:** During Shop Phase, you can move any Joker between any slots freely.

**Why Lock During Rounds?**
- Prevents tedious micromanagement (moving Jokers before every hand)
- Enforces strategic planning rather than tactical optimization
- Aligns with Design Goal #1 (Casual Friendly) — less cognitive load mid-round

#### Trigger Order

**Left Deck Scoring:**
1. Calculate base points from all hands played
2. Trigger Left slot Jokers (J1 → J2 → J3)
3. Trigger Bridge slot Jokers (B1 → B2)

**Right Deck Scoring:**
1. Calculate base points from all hands played
2. Trigger Right slot Jokers (J4 → J5 → J6)
3. Trigger Bridge slot Jokers (B1 → B2) — **triggers again**

**Final Calculation:**
- Combine both deck points
- Apply accumulated global mult

#### Example Round with Joker Triggers

**Setup:**
- Left J1: "+50 points per Flush played"
- Left J2: "+0.1 mult per hand played"
- Bridge B1: "+0.2 mult per Pair played"
- Right J4: "+30 points per Two Pair played"

**Round Play:**
- Left deck plays 2 hands: Flush (20 base) + Pair (6 base) = 26 base points
- Right deck plays 2 hands: Two Pair (10 base) + Pair (6 base) = 16 base points

**Scoring:**

**Left Deck Scoring:**
1. Base: 26 points
2. Left J1 triggers: +50 (Flush) → 76 points
3. Left J2 triggers: +0.1 mult (per hand) × 2 hands → Global mult = 1.0 + 0.2 = 1.2
4. Bridge B1 triggers: +0.2 mult (Pair played) → Global mult = 1.2 + 0.2 = 1.4
5. **Left Result: 76 points, Global mult = 1.4**

**Right Deck Scoring:**
1. Base: 16 points
2. Right J4 triggers: +30 (Two Pair) → 46 points
3. Bridge B1 triggers again: +0.2 mult (Pair played) → Global mult = 1.4 + 0.2 = 1.6
4. **Right Result: 46 points, Global mult = 1.6**

**Final:**
- Total Points: 76 + 46 = 122
- Global Mult: 1.6
- **Final Score: 122 × 1.6 = 195**

#### Example Joker Library (Scaling Tiers)

**Design Philosophy:** Jokers scale from flat bonuses (early game) → multiplicative (mid game) → exponential conditionals (late game).

##### **COMMON JOKERS** (Cost: $5)
Flat bonuses, always useful, never gamebreaking.

1. **"Chip Stack"**
   - Effect: +30 points per hand played
   - Scaling: Additive only
   - Best in: Early game (Rounds 1-3)

2. **"Lucky Seven"**
   - Effect: +15 points if hand contains a 7
   - Scaling: Conditional flat bonus
   - Best in: Early-mid game

3. **"Pair Producer"**
   - Effect: +0.1 mult per Pair played
   - Scaling: Additive mult (stacks in Bridge slot)
   - Best in: Pair-focused builds

##### **UNCOMMON JOKERS** (Cost: $8)
Conditional bonuses or small multipliers.

4. **"Flush Fund"**
   - Effect: +60 points per Flush played
   - Scaling: Higher flat bonus with condition
   - Best in: Flush specialist builds

5. **"Twin Boost"**
   - Effect: +0.2 mult if both decks played at least 1 hand this round
   - Scaling: Conditional mult (great in Bridge slot)
   - Best in: Balanced 2-2 hand splits

6. **"Card Counter"**
   - Effect: +5 points per card played this round (cumulative)
   - Scaling: Grows throughout round
   - Best in: High-volume play (playing all 4 hands)

##### **RARE JOKERS** (Cost: $12)
Multiplicative scaling or strong conditionals.

7. **"Suit Synergy"**
   - Effect: ×1.3 mult if all hands played this round were same suit type
   - Scaling: Multiplicative
   - Best in: Specialist builds (all Flushes or mono-suit focus)

8. **"High Roller"**
   - Effect: ×1.5 mult if round score > 500 before this Joker triggers
   - Scaling: Exponential (triggers after other Jokers)
   - Best in: Late game (Rounds 6-8)

9. **"Bridge Troll"**
   - Effect: +0.4 mult per Joker in Bridge slots (including self)
   - Scaling: Self-synergizing (MUST go in Bridge to trigger twice)
   - Best in: Bridge-focused builds

##### **LEGENDARY JOKERS** (Cost: $18)
Game-warping effects, build-defining.

10. **"Twin Flames"**
    - Effect: ×2.0 mult if both decks scored exactly the same this round
    - Scaling: Massive multiplier with strict condition
    - Best in: Coordinated 2-2 balanced builds
    - High risk, high reward

---

**Joker Synergy Example (Late Game):**

**Setup:**
- Bridge B1: "Twin Boost" (+0.2 mult if both decks played)
- Bridge B2: "Bridge Troll" (+0.4 mult per Bridge Joker)
- Left J1: "Flush Fund" (+60 per Flush)
- Right J4: "High Roller" (×1.5 if score > 500)

**Round 7 Play:**
- Left plays 2 Flushes = 40 base + 120 (Flush Fund) = 160 points
- Right plays 2 Pairs = 12 base = 12 points
- Bridge triggers:
  - Twin Boost: +0.2 mult (both played) → 1.2
  - Bridge Troll: +0.4 mult (2 Bridge Jokers) → 1.6
  - Triggers again for right deck: +0.6 mult → 2.2
- High Roller checks: 172 points < 500 → doesn't trigger
- **Final: 172 × 2.2 = 378 points**

(Not enough! Need better Joker synergies or higher base hands for Round 7's 3,418 quota)

### 6️⃣ Round Flow

Rounds are **free-form** — you can play or trade in any order until tokens are exhausted.

**1. Round Start:**
- Both decks draw 4 cards each (8 cards visible total).
- Tokens available: 4 hands, 3 trades.

**2. Free Play Phase:**
- **Play:** Choose left or right deck, select 1-4 cards, form a poker hand (uses 1 hand token).
  - Played cards are removed and replaced from that deck immediately.
  - **Max 2 hands per deck per round.**
- **Trade:** Choose source deck, give 1-4 cards to the other deck (uses 1 trade token).
  - Giving deck draws replacements immediately (stays at 4).
  - Receiving deck accumulates cards (max 8).
- Repeat in any order until you've used all tokens or choose to end the round.

**3. Scoring:**
- **Left Deck Scoring:**
  - Sum base points from all hands played
  - Trigger Left slot Jokers (J1 → J2 → J3) — modify points or global mult
  - Trigger Bridge slot Jokers (B1 → B2) — modify points or global mult
  - Result: Left Deck Points + updated Global Mult
- **Right Deck Scoring:**
  - Sum base points from all hands played
  - Trigger Right slot Jokers (J4 → J5 → J6) — modify points or global mult
  - Trigger Bridge slot Jokers (B1 → B2) **again** — modify points or global mult
  - Result: Right Deck Points + updated Global Mult
- **Final Calculation:**
  - Final Score = (Left Deck Points + Right Deck Points) × Global Mult
  - Compare to quota: Pass = advance to shop, Fail = game over.

**4. Shop Phase:**
- 4 random Jokers offered (Common/Uncommon/Rare/Legendary mix).
- Purchase Jokers (cost TBD based on rarity) — immediately choose which slot to place them in.
- **Freely move and reorder ALL Jokers** between any slots (Left/Right/Bridge).
- Shop refresh costs $4.
- Purchase permanent card trades (cost TBD).
- Proceed to next round.

**5. End of Round Rewards:**
- Earn money for unspent tokens:
  - $2 per unspent hand token
  - $1 per unspent trade token
- Earn interest: $1 per $5 held (max $4 interest on $20+)

### 7️⃣ Poker Hand Scoring (1-4 Cards)

Players can form hands using 1-4 cards from a single deck. Hand rankings and base scores:

| Rank | Hand | Base Score | Notes |
|------|------|------------|-------|
| 1 | Royal Flush | 60 | A-K-Q-J of same suit (requires 4 cards) |
| 2 | Straight Flush | 50 | Sequential ranks, same suit |
| 3 | Four of a Kind | 30 | All 4 cards same rank |
| 4 | Flush | 20 | All cards same suit |
| 5 | Straight | 18 | Sequential ranks (A-2-3-4, 2-3-4-5, etc.) |
| 6 | Three of a Kind | 15 | Three cards same rank |
| 7 | Two Pair | 10 | Two different pairs |
| 8 | Pair | 6 | Two cards same rank |
| 9 | High Card | 3 | No matching pattern |

**Scoring Notes:**
- Jokers modify these base scores (add chips, multiply, etc.).
- Hands with fewer cards are valid (e.g., play 1 card = High Card for 3 points).
- Values tuned for dual-deck economy where 4 hands per round are played.

## 📈 PROGRESSION & ECONOMY

### Starting Conditions
- **Money:** $0
- **Jokers:** None (all slots empty)
- **First Round:** Play Round 1 with no Jokers, earn money from unspent tokens and beating quota, then enter first shop

### Win Condition
- Beat **Round 8** to win the run.
- **Future TODO:** Endless mode after Round 8.

### Quota Scaling (Exponential - 1.5× Per Round)
- **Round 1:** 300 points (beatable with base poker hands)
- **Round 2:** 450 points (1.5×)
- **Round 3:** 675 points (1.5×)
- **Round 4:** 1,013 points (1.5×)
- **Round 5:** 1,519 points (1.5×)
- **Round 6:** 2,279 points (1.5×)
- **Round 7:** 3,418 points (1.5×)
- **Round 8:** 5,127 points (1.5×)

**Scaling Philosophy (Balatro-Inspired):**
- Early game (R1-3): Linear-ish feel, building your engine
- Mid game (R4-6): Exponential curve kicks in, Jokers become critical
- Late game (R7-8): God mode, massive scores, exponential scaling pays off

**Why Exponential:**
- Matches Balatro's "power fantasy" progression
- Forces Joker synergies (can't brute-force with base hands)
- Round 8 feels epic (17× harder than Round 1)
- Aligns with Design Goal #1 (Satisfying Progression)

### Failure Condition
- If final score < quota: **Game Over** (no retry, no lives).

### Money System

**Earning Money:**
- Unspent hand tokens: $2 each
- Unspent trade tokens: $1 each
- Interest: $1 per $5 held (max $4 interest on $20+)
- Example: Use 2 hands, 1 trade, hold $12 → Earn $4 (hands) + $2 (trades) + $2 (interest) = $8

**Spending Money:**

**Joker Prices (by rarity):**
- Common: $5
- Uncommon: $8
- Rare: $12
- Legendary: $18

**Other Shop Options:**
- Shop refresh: $4 (reroll all 4 Jokers)
- Sell Joker: Receive 50% of purchase price (mitigates bad purchases)
- Skip purchase: Free (save money for better shops)
- Permanent card trades: $8 (move one specific card permanently between decks)

**Shop Strategy:**
- Early game: Buy cheap Commons to start scaling
- Mid game: Save for Rares ($12+) with exponential effects
- Late game: Hunt for Legendary synergies or perfect Bridge Jokers
- Always: Can sell bad Jokers to pivot builds (comeback mechanic)

### Unlocks (Future TODO)
- Asymmetric deck splits
- New starting Jokers
- Special card modifications

## 👥 CO-OP INTEGRATION (TODO - Future Feature)

Co-op is planned but not part of the current solo prototype. Future design considerations:

| Element | Solo (Current) | Co-op (Future) |
|---------|----------------|----------------|
| **Decks** | One player manages both. | Each player controls one deck. |
| **Jokers** | Two personal sets + shared bridge jokers. | Each player manages their own Jokers; shared bridge jokers affect all. |
| **Shop & Money** | Single wallet. | Shared team wallet and shop inventory. |
| **Quota** | Combined total of all decks. | Scales with player count (BaseQuota × N × 1.3). |
| **Trades** | Internal swaps. | Cross-player trades require mutual confirmation. |

## 💎 UNIQUE SELL POINTS

- **Dual-deck poker engine** where both sides matter every round.
- **Free-form action economy** — play, discard, trade in any order.
- **Bridge Jokers** create cross-deck synergies and global scaling.
- **1-4 card hands** enable flexible tactical plays.
- **Solo-focused design** with future co-op expansion.

## ✅ IMPLEMENTATION ROADMAP

### Phase 1: Python Terminal Prototype (Current)
- Core mechanics: dual decks, one-directional trading, poker evaluation
- Token system: 4 hands (max 2 per deck) + 3 trades
- 4 visible cards per deck (max 8 with trades)
- Basic Joker system (simple effects)
- Terminal UI with clear info display
- 8-round progression with linear quota scaling (240 → 1920)

### Phase 2: Godot Port
- Godot 4.5 architecture (Resources, Managers, Signals)
- Visual card UI with drag-and-drop
- Animated scoring and Joker effects
- Polished shop interface

### Phase 3: Content Expansion
- 50+ unique Jokers across all rarities
- Unlockable deck splits and modifiers
- Endless mode post-Round 8
- Balanced economy tuning

### Phase 4: Co-op (Future)
- Multiplayer infrastructure
- Scaled quotas and shared resources
- Cross-player trade confirmation UI

## 🎯 TARGET AUDIENCE

- **Balatro Fans:** Familiar poker-roguelike feel with deeper strategic layers.
- **Roguelike Players:** High replayability through emergent Joker combinations.
- **Strategy Gamers:** Resource management meets tactical card play.
- **Streamers:** Decision-rich moments create engaging content.
