# Game Design Document

**Poker Grid** - A strategic grid-based poker game with Balatro-inspired mechanics

## 📚 Documentation Structure

- **[GDD.md](GDD.md)** - High-level vision and core design pillars
- **[MECHANICS.md](MECHANICS.md)** - Detailed game mechanics and rules
- **[SCORING.md](SCORING.md)** - Scoring system (chips × mult)
- **[JOKERS.md](JOKERS.md)** - Joker system design (auto-generated from CSV)
- **[BALANCE.md](BALANCE.md)** - Balance formulas and tuning notes

## 🎮 Quick Overview

**Genre:** Strategic Card Game / Roguelike
**Platform:** Python (Terminal) → Godot
**Core Loop:** Build poker hands in a 5×5 grid using freezes and redraws

**USP (Unique Selling Point):**
- Grid-based poker scoring (10 lines simultaneously)
- Persistent freezes across all hands in a round
- Balatro-style chips × mult scoring with jokers
- Single deck with replacement (enables deck building)

## 🔗 See Also

- **Technical Docs:** `src/docs/architecture/`
- **Game Data:** `data/jokers.csv`
- **Tests:** `tests/`
