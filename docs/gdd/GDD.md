# Poker Grid - Game Design Document

**Version:** 1.1 (Locked)
**Last Updated:** 2025-10-21
**Designer:** User

---

## 🎯 Core Fantasy

**"Build a living poker machine that rewires itself every run."**

Players construct a 5×5 poker slot grid, forming hands across rows and columns while manipulating a 3×3 Joker grid whose powers mutate each run via dynamic spatial tags.

Every round is a tense push-pull between skillful probability control and gambler's risk management.

---

## 🕹️ Core Gameplay Loop

1. **Spin columns** → draw cards from your deck (with replacement)
2. **Choose columns to reroll**, paying tokens from a shared pool
3. **Score all 10 hands** (5 rows + 5 columns), counting only the **top 3**
4. **Apply Joker effects** (chips, mult, x-mult, economy)
5. **Shop phase** → buy/sell Jokers, reroll their tags, or lock them in
6. **Meet quota** → progress to next ante (round)
7. **Repeat** — new decks, new tags, new synergies

---

## ♠️ Core Structure & Rules

### Deck & Draw
- **Ranks:** Full deck (2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K, A)
- **Suits:** 4 (♠ ♥ ♦ ♣)
- **Total cards:** 52 (standard poker deck)
- **Draw type:** With replacement — every cell is independent
- **Purpose:** Familiar poker odds with strategic reroll depth

### Grid Mechanics
- **Grid Size:** 5×5 = 25 cards
- **Total Hands:** 10 (5 rows + 5 columns)
- **Scoring:** Only the **top 3 highest hands** contribute to your quota each round
- **Valid Hands:** Standard poker hierarchy (Pair → Quads → Straight Flush)
- **Wrap-around straights allowed** (e.g., 9-T-2-3-4)

### 🎰 Reroll System

| Parameter | Value |
|-----------|-------|
| Spins per quota | 7 |
| Shared reroll tokens per quota | 12 total |
| Cost per column rerolled | 1 token |
| Carry-over | ❌ None (tokens reset each new quota) |
| Draw rule | With replacement |
| Per-spin cap | None — players choose how many to spend |
| Quota scoring | Cumulative across all 7 spins |

**Player Flow per Round:**
1. Observe grid → judge its potential
2. Spend 0–N tokens to reroll specific columns
3. Updated results ripple through multiple hands
4. End spin → new 5×5 board state saved
5. After 7 spins, quota total is scored

**Player Agency:**
- Judge when to go all-in vs save tokens
- Evaluate if current board is worth improving or too risky to chase
- Manage tempo across 7 spins for optimal EV

**This shared-token economy creates real tension — gambling fantasy with skill-based decision depth.**

### 🧊 Freeze System (Special Ability)
- **Freeze cells** as a special ability (not part of core loop)
- Certain Jokers or consumables grant freeze powers
- Example: "Freeze 2 cells for the next 3 spins"
- **Purpose:** Strategic tool, not baseline mechanic

---

## 🌟 Core Pillars

### 1. **Risk–Reward Agency**
Shared token pool creates strategic tempo tension. Decide when to all-in vs conserve.

### 2. **Cross-Hand Strategy**
Column rerolls ripple through 5 hands at once. A single card contributes to both its row AND column.
- High-value cards in intersections matter most
- Think multi-dimensionally

### 3. **Spatial Joker Synergy**
3×3 grid + tags = emergent power network. Placement matters — adjacency drives synergy.

### 4. **Readable Randomness**
Every probability visible and fair. No hidden RNG.

### 5. **Emotional Payoff**
Each spin is a thrill — skillful luck manipulation.

---

## 💰 Quota & Progression

- Each quota (round) requires reaching a chip target
- Higher antes increase quota requirements and shop prices
- Tokens reset every new quota
- Jokers and deck persist across rounds (roguelite carryover)

---

## 🃏 Joker System

### Overview
- Up to **9 Jokers**, arranged on a **3×3 grid**
- Each Joker has:
  - One **base effect** (chips / mult / x-mult / economy / reroll bonus)
  - One **dynamic Tag** (behavior modifier)
- Jokers interact spatially — **adjacency drives synergy**
- Players can **lock Joker positions** per round (7 spins) to reduce cognitive load

### 🔖 Example Tags

| Tag | Effect | Category |
|-----|--------|----------|
| 🔺 Amplifier | Adjacent Jokers gain +25% mult | Buff |
| 🔻 Downlink | Pass 50% of effect downward | Relay |
| 🔁 Mirror | Copies adjacent Joker's base effect | Copy |
| 🔥 Reactor | Retriggers a neighbor once per round | Retrigger |
| 🌀 Propagator | Spreads +1 mult to nearby Jokers | Growth |
| 💰 Link | Shares economy gains with adjacent Jokers | Economy |
| 🌱 Grower | Gains +1 mult per adjacent Grower | Scaling |

### Spatial Synergy
- **Placement matters** — adjacency, directionality, and tag spread change power flow
- Same Joker behaves **differently each run** due to randomized tag assignments
- Creates **procedural replayability** without complex text or rule overhead

---

## 🧮 Scoring System

### Simplified Scoring Formula
**Total Score = (Sum of top 3 hand chips + Joker chip bonuses) × (Base mult + Joker +mult bonuses) × Joker ×mult bonuses**

- Each hand type has a **flat chip value** (no per-card math)
- Jokers can add:
  - **Global +chips** (added to chip sum)
  - **Global +mult** (stacks additively, e.g., +2 mult + +3 mult = +5 mult)
  - **Global ×mult** (stacks multiplicatively, e.g., ×2 × ×1.5 = ×3 total)
- **Base multiplier = 1** (so chips × 1 × x-mults)
- Clear, fast, dopamine-driven — no number bloat or cognitive friction

### Hand Scoring Table

| Hand Type | Chips | Notes |
|-----------|-------|-------|
| **Five of a Kind** | 160 | All 5 cards same rank (rarest - 1 in 7.3M) |
| **Royal Flush** | 150 | T-J-Q-K-A of same suit |
| **Straight Flush** | 110 | Any straight + flush combo |
| **Four of a Kind** | 90 | 4 cards of same rank |
| **Full House** | 70 | 3 of a kind + pair |
| **Flush** | 55 | All 5 cards same suit |
| **Straight** | 45 | Sequential ranks (wrap-around allowed) |
| **Three of a Kind** | 30 | 3 cards of same rank |
| **Two Pair** | 20 | 2 different pairs |
| **One Pair** | 10 | 2 cards of same rank |
| **High Card** | 3 | No matching cards |

**Wrap-around straights:** A-2-3-4-5, K-A-2-3-4, Q-K-A-2-3, etc.

### Example Calculation

**Grid results:**
- Row 0: Full House (70 chips)
- Col 2: Flush (55 chips)
- Row 3: Two Pair (20 chips)
- Other hands: lower scores (not counted)

**Jokers active:**
- Joker A: +30 chips (global)
- Joker B: +4 mult (global)
- Joker C: +3 mult (global)
- Joker D: ×2 mult (global)
- Joker E: ×1.5 mult (global)

**Calculation:**
1. Sum top 3 hand chips: 70 + 55 + 20 = **145 chips**
2. Add global chip bonuses: 145 + 30 = **175 chips**
3. Calculate total +mult: 1 (base) + 4 + 3 = **8 mult**
4. Apply additive mult: 175 × 8 = **1,400**
5. Apply multiplicative x-mults: 1,400 × 2 × 1.5 = **4,200 final score**

**Key principles:**
- +mult bonuses stack additively (4 + 3 = 7, plus base 1 = 8 total)
- ×mult bonuses stack multiplicatively (×2 × ×1.5 = ×3 total)

---

## 🌟 Unique Selling Points

| # | USP | Why It Matters |
|---|-----|----------------|
| 1 | 5×5 Poker Grid | Strategy across 10 simultaneous hands |
| 2 | Column Rerolls | Pure risk/reward control per spin |
| 3 | Shared Token Pool | Skillful tempo management — when to all-in |
| 4 | 3×3 Joker Grid | Spatial meta-layer of emergent synergy |
| 5 | Dynamic Tags | Every Joker behaves uniquely each run |
| 6 | Procedural Engine-Building | Constant discovery and experimentation |
| 7 | Readable Scoring | Balatro-like depth, simpler clarity |

---

## 🧠 Design Philosophy

- **Readable Depth** → Players understand effects instantly but master interactions over time
- **Controlled RNG** → Player choice mitigates randomness; odds always clear
- **Discovery-First** → Fun comes from uncovering new Joker-tag synergies each run
- **Spatial Elegance** → Depth arises from placement, not text density
- **Gambling Tension** → Shared tokens + cumulative spins = self-driven risk curve

---

## 🎨 Presentation & Feel

### Theme
Neo-casino — sleek, futuristic, confident

### Palette
Dark base with neon and gold highlights

### FX
- Column clacks
- Pulsing rows
- Jackpot bursts

### Audio
- Rising tension as tokens dwindle
- Distinct sound cues for pairs/trips/full house/quads
- "All-in" SFX when spending >50% tokens in one spin

### UI Essentials
- **Tokens:** 8 / 12
- **Spins:** 3 / 7
- **Quota progress bar**
- Highlight improved (green) vs worsened (red) hands

---

## 🎯 Target Audience

**Primary:** Balatro fans who want spatial strategy depth
**Secondary:** Poker roguelike fans (Luck Be a Landlord, Roundguard)
**Tertiary:** Puzzle game fans who enjoy procedural synergy discovery

**Skill Floor:** Understand basic poker hands
**Skill Ceiling:** Master spatial grid optimization + dynamic Joker tag synergies

---

## 🚀 Development Roadmap

### ✅ Phase 0: Core Game (DONE)
- 5×5 grid with card drawing (full 52-card deck)
- Poker hand evaluation (with wrap-around straights)
- Flat chip scoring per hand type
- 7 spins per quota

### 🔄 Phase 1: Reroll System (CURRENT)
- Shared token pool (12 tokens per quota)
- Column reroll mechanics
- Top 3 hand scoring
- Token economy UI

### 📋 Phase 2: Joker System
- 3×3 Joker grid
- Dynamic tag system
- Spatial synergy mechanics
- Joker locking per quota

### 📋 Phase 3: Economy & Shop
- Money system
- Shop between rounds
- Buy/sell Jokers
- Reroll Joker tags
- Ante progression (8 rounds)

### 📋 Phase 4: Deck Building
- Consumable cards (tarot, planet, spectral)
- Card enhancements (foil, holographic, polychrome)
- Freeze abilities (as special powers)
- Deck manipulation

### 📋 Phase 5: Content & Polish
- 150 Jokers with tag variations
- Multiple deck types
- Challenges and unlocks
- Balance tuning

### 📋 Phase 6: Godot Port
- Convert to Godot Engine
- UI/UX polish
- Animations and juice
- Sound and music

---

## 🎯 Success Metrics

**MVP Success:**
- Reroll economy feels tense and rewarding
- Joker tag system creates emergent builds
- Grid mechanics feel unique (not just "Balatro clone")

**Launch Success:**
- "Balatro meets spatial strategy" is instantly understood
- Streamers discover wild Joker tag synergies
- Community creates tier lists and optimal token spending guides

---

## 🧩 Why It's Innovative

| Dimension | Innovation |
|-----------|------------|
| **Systemic Depth** | 10-hand grid with cross-impact rerolls |
| **Agency Curve** | Shared-token pool creates strategic tempo tension |
| **Procedural Replayability** | Dynamic Joker tags make every run unpredictable |
| **Elegant Complexity** | Deep systems, minimal text, visual clarity |
| **Fantasy Cohesion** | "Living poker machine" theme fuses perfectly with mechanics |

---

## ✅ Final Locked Pillars

| Pillar | Description |
|--------|-------------|
| **Risk–Reward Agency** | Decide when to all-in vs conserve |
| **Cross-Hand Strategy** | Column rerolls ripple through 5 hands at once |
| **Spatial Joker Synergy** | 3×3 grid + tags = emergent power network |
| **Readable Randomness** | Every probability visible and fair |
| **Emotional Payoff** | Each spin is a thrill — skillful luck manipulation |

---

## 📚 See Also

- **[MECHANICS.md](MECHANICS.md)** - Detailed rules
- **[JOKERS.md](JOKERS.md)** - Joker system design
- **[SCORING.md](SCORING.md)** - Scoring formulas
- **[BALANCE.md](BALANCE.md)** - Balance notes
