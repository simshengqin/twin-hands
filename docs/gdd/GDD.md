# 🃏 TWIN HANDS (v4.0 – Natural Imbalance Edition)

## 🎯 ELEVATOR PITCH

Play alone or with friends. Build two poker engines that trade cards, trigger shared Jokers, and break escalating quotas.

A roguelike poker builder where one 52-card deck splits into two specialized hands that grow, diverge, and synergize.

Trade cards across decks, manage distinct Joker builds, and chase impossible quotas — solo or co-op.

## 🧩 CORE CONCEPT

- **Deck Splitting:** A single 52-card deck divided into two unique "hands."
- **Trade Economy:** Swap cards temporarily each round or buy permanent transfers in the shop.
- **Joker Systems:** Each deck has its own Jokers plus shared bridge Jokers that link both engines.
- **Escalating Quotas:** The combined score of both decks must meet the target to survive.
- **Supports Solo & Co-op:** One player can run both decks, or multiple players each control one.
- **Natural Imbalance Philosophy:** Both decks can scale unevenly — success comes from leveraging synergy, not forcing equality.

## ♠️ CORE MECHANICS

### 1️⃣ Deck Splitting

- **First Run Split:** Perfect 26/26 — Red Specialist (♥♦) vs. Black Specialist (♣♠).
- **Later Runs:** Unlocks randomized or asymmetric splits for unique deck identities.

### 2️⃣ 4-Card System

- Each deck draws 6 visible cards per round.
- You get 5 total hands (each 4 cards) and 4 discards per round.
- A hand can only be formed from one deck's cards.
- Both decks reset and redraw each round.

### 3️⃣ Hand Distribution Rule

- 5 total hands per round.
- Maximum of 3 hands may come from either deck per round.
- Prevents full 5–0 dumps while keeping both decks relevant.

### 4️⃣ Trading System

| Type | Uses | Duration | Cost | Source |
|------|------|----------|------|--------|
| Temporary Trades | Up to 4 per round (via trade tokens). | Reset each round. | Free. | Tactical swaps. |
| Permanent Trades | Purchased in shop. | Persist across run. | Costs gold. | Strategic upgrades. |

**Trade Pool Limitation:**
- Each deck exposes 6–8 random cards from its 26-card pool for trading each round.
- This prevents consistent "funneling" and keeps decisions unpredictable.

### 5️⃣ Joker System

#### Slot Structure (2-Deck Default)

```
Left Deck Jokers    Shared Bridge Jokers     Right Deck Jokers
[J1][J2][J3]    |    [B1][B2]    |    [J4][J5][J6]
```

#### Categories

**Left/Right Jokers:**
- Affect only their own deck's scoring.
- Each deck can hold 3–4 Jokers.

**Shared Bridge Jokers:**
- Trigger off both decks' events or global conditions (e.g. both played a Flush, or sum of scores).
- Designed to scale global multipliers or cross-deck bonuses.

#### Joker Placement Rules

- Jokers may be rearranged only during Shop Phase or between Antes.
- Once a round begins, Jokers are locked in their current slots for the whole round.
- Jokers are bound to their deck side (Left, Right, or Shared) once purchased.
- Jokers cannot be reassigned between sides normally.
- Rare shop service: "Reassign Joker Slot" allows moving one Joker (Left↔Right↔Shared) for a high cost.
- Jokers within a deck may be freely reordered.

#### Trigger Logic

- Each deck triggers its own Jokers sequentially.
- Shared Bridge Jokers trigger once per deck per round (when both sides complete scoring).
- Jokers reference "your deck" and "other deck," never Left/Right by name.

**Locking Justification:**
This prevents mid-round micromanagement exploits (e.g., moving a Mult Joker to whichever hand you're about to play) and reinforces round-based planning rather than hand-by-hand optimization.

### 6️⃣ Round Flow

1. **Draw Phase:** Both decks reveal 6 cards.
2. **Trade Phase:** Up to 4 temporary trades using visible trade pools.
3. **Play Phase:** Play 5 hands total (max 3 per deck).
4. **Score Phase:**
   - Each deck's hands are scored using their Joker effects.
   - Shared Jokers trigger off both decks' results.
   - Total = LeftScore + RightScore (no enforced equality).
5. **Shop Phase:** Purchase Jokers, upgrades, or permanent trades. Rearrange Jokers (within allowed rules).

### 7️⃣ 4-Card Hand Hierarchy

| Rank | Hand | Points |
|------|------|--------|
| 1 | Royal Flush | 60 |
| 2 | Straight Flush | 50 |
| 3 | Four of a Kind | 30 |
| 4 | Flush | 20 |
| 5 | Straight | 18 |
| 6 | Three of a Kind | 15 |
| 7 | Two Pair | 10 |
| 8 | Pair | 6 |
| 9 | High Card | 3 |

*(Values tuned for smaller hand sizes and two-deck scoring balance.)*

## 👥 CO-OP INTEGRATION

| Element | Solo | Co-op |
|---------|------|-------|
| **Decks** | One player manages both. | Each player controls one deck (up to 4 total). |
| **Jokers** | Two personal sets + shared bridge jokers. | Each player manages their own Jokers; shared bridge jokers affect all. |
| **Shop & Money** | Single wallet. | Shared team wallet and shop inventory. |
| **Quota** | Combined total of all decks. | Scales with player count (BaseQuota × N × 1.3). |
| **Trades** | Internal swaps. | Cross-player trades require mutual confirmation. |

**Co-op Hook:**
"Two decks, one fate."
Every trade, discard, and Joker choice shapes the shared outcome.

## ⚙️ WHY IT WORKS

| Aspect | Strength |
|--------|----------|
| **Natural Imbalance** | Each deck can shine or lag; players adapt dynamically. |
| **Bound Jokers** | Solidifies deck identity and long-term strategy. |
| **Round-Locked Planning** | Each round feels like a tactical puzzle, not a micro loop. |
| **Trade Friction** | Ensures evolving interdependence without funnels. |
| **Co-op Scaling** | Fits 1–4 players without redesign. |

## 💎 UNIQUE SELL POINTS

- Dual-deck poker engine with evolving asymmetry.
- Locked Joker systems that build long-term identity.
- 4-trade token tactical economy per round.
- 5-hand rounds (max 3 per deck) for constant dual engagement.
- Shared bridge Jokers connecting both scoring systems.
- Works identically in solo or co-op modes.

## 🎯 TARGET AUDIENCE

| Group | Appeal |
|-------|--------|
| **Balatro Fans** | Familiar feel, deeper two-deck strategy. |
| **Roguelike Players** | High replayability and emergent engine builds. |
| **Co-op / Party Gamers** | Real teamwork tension through trades and shared quotas. |
| **Streamers / Content Creators** | Decision-rich moments: trades, Joker purchases, clutch dual scoring. |

## 💬 MARKETING HOOKS

- "Two decks. One fate."
- "Build twin poker engines — trade, sync, and survive together."
- "A co-op Balatro-style roguelike where synergy beats symmetry."

## ✅ FINAL SUMMARY

Twin Hands transforms poker scoring into a dynamic two-engine roguelike where strategy lives in trade-offs, not symmetry.

Each round demands foresight — what you lock in before play defines your fate.

Natural imbalance, locked Jokers, and strict per-deck hand limits keep every decision meaningful, every synergy earned.

Designed for deep solo mastery or chaotic co-op harmony.
