**AI Simulation Overview**
- Location: `ai_simulation/`
- Purpose: Non-production AIs, utilities, and scripts for experiments. Cleanly separated from `src/` runtime.

**Layout**
- `agents/`
  - `normal_ai_manager.py` — Simple “average player” AI. Heuristic freezes; basic shop action.
  - `smart_ai_manager.py` — EV-based AI. Monte Carlo freeze selection; value-driven shop.
- `utils/`
  - `ai_evaluator.py` — Monte Carlo EV for grids (top‑K lines) and joker value heuristics.
- `scripts/`
  - `demo.py` — Prints NormalAI/SmartAI freeze + shop picks on a fresh grid.
  - `auto_play.py` — Runs full sessions; CLI for AI choice, samples, seeds, and K lines.
- `tests/` — Pytest suite for fairness and behaviors.
- `__init__.py` — Re-exports `AIEvaluator`, `NormalAIManager`, and `SmartAIManager`.

**Normal AI — Behavior**
- Freeze decisions
  - Collects visible grid cards from `state.grid`.
  - Picks up to `max_to_freeze` cells using a simple priority:
    - Highest aligned pair (same row or column).
    - Else two highest cards of the same suit.
    - Else no freezes.
- Shop decisions
  - If there is an empty joker slot and enough money, buys the first affordable `+m` or `+c` joker in the shop list provided.
  - Does not sell or reroll by itself (kept intentionally simple).
- Fairness
  - Reads only public information (grid, `config.RANK_VALUES`, `state.can_afford`, and `joker_manager.has_empty_slot`).
  - Does not simulate future draws or peek at the deck.

**Normal AI — Tuning Knobs**
- `max_to_freeze` (method parameter) — how many cells to freeze.
- Heuristic tweaks (code-local):
  - Change rank comparison to favor different ranks.
  - Add or remove suit-based tie-breakers.
  - Allow non-aligned pairs by extending the search.

**Smart AI — Design**
- Goal
  - Select freezes and shop actions that maximize expected value (EV) while remaining fair (no hidden info).
- Freeze selection
  - Candidate generation
    - Seed candidates with human-strong patterns: aligned pairs, top same-suit pairs, and top single high ranks.
    - Build combinations up to `config.max_freezes` and include a `no-freeze` candidate.
    - Prune to top-K via quick heuristics (rank sum, suit counts) before EV.
  - EV evaluation
    - For each candidate, estimate next-hand score with `AIEvaluator.estimate_expected_score(...)` using:
      - Public `grid_cards` from `state.grid`.
      - Candidate `frozen_cells`.
      - `config` and `joker_manager.active_jokers`.
    - Pick the candidate with the highest EV; tie-break toward stability (keep previous freezes) or highest-pair preference.
  - Optional horizon
    - Short-horizon (2–3 hands) with discount `gamma` (e.g., 0.85) to value persistence.
- Shop decisions
  - Value function per joker combines:
    - Immediate impact (trigger frequency × additive/multiplier effect).
    - Synergy with current jokers (chips vs mult stacking).
    - Growth potential over remaining hands/rounds.
    - Cost efficiency and quota pressure (more aggressive when behind).
  - Actions
    - Buy best positive-value joker when affordable and slot available.
    - If no slot, sell weakest joker only if net gain exceeds a threshold.
    - Reroll when expected reroll value exceeds the best available option and affordable.
- Fairness
  - Samples future deals from the same distribution as the game (with replacement), without peeking at the real next draw.
  - Uses only public inputs: `state.grid`, `config`, `joker_manager.active_jokers`, `state.can_afford`, and the provided `shop_display`.

**Smart AI — Tuning Knobs (Target)**
- `samples` — number of Monte Carlo samples per candidate (e.g., 100–600).
- `candidate_cap` — max freeze sets to evaluate (e.g., 20–40).
- `gamma` — discount for short-horizon planning (0–1).
- `buy_threshold` — minimum EV lift to justify a purchase.
- `sell_threshold` — minimum net gain to justify selling for a better joker.
- `reroll_policy` — when to reroll based on reroll cost and expected shop EV.

**Performance Considerations**
- Candidate pruning keeps evaluation fast.
- Adaptive samples: increase only when candidates are close in EV.
- Memoization per decision step to avoid duplicate EV work.
- Optional seeded RNG to make behavior reproducible for tests.

**Public APIs**
- Normal AI
  - `NormalAIManager(state, config, joker_manager=None)`
  - `recommend_freezes(max_to_freeze: int = 2) -> List[(row, col)]`
  - `recommend_shop_action(shop_display: List[dict], reroll_cost: int) -> (action: str, index: int)`
- Smart AI
  - `SmartAIManager(state, config, joker_manager=None)`
  - `recommend_freezes(max_to_freeze: int = 2, samples: Optional[int] = None) -> List[(row, col)]`
  - `recommend_shop_action(shop_display: List[dict], reroll_cost: int) -> (action: str, index: int)`
- EV Helper
  - `AIEvaluator.estimate_expected_score(grid_cards, frozen_cells, config, active_jokers=None, samples=200, rng=None) -> float`
  - `AIEvaluator.evaluate_joker_value(joker, current_active) -> float`

**Scripts**
- Demo: `python ai_simulation/scripts/demo.py`
- Auto-play:
  - `python ai_simulation/scripts/auto_play.py --ai both`
  - Options: `--ai normal|smart|both`, `--samples N`, `--seed S`, `--lines K`

**Testing**
- `ai_simulation/tests/test_normal_ai_public_api.py`
  - Guards against hidden state access and validates freeze/shop suggestions.
- `ai_simulation/tests/test_ai_evaluator_smoke.py`
  - Smoke test for EV estimation.

**Extension Points**
- Add `SmartAIManager` in `ai_simulation/smart_ai_manager.py` implementing the design above.
- Introduce a lightweight config module (e.g., `ai_simulation/ai_config.py`) to centralize tuning knobs.
- Add explainability: `explain_last_decision()` to log rationale for choices.

**Usage Examples**
- Normal AI
  - `from ai_simulation import NormalAIManager`
  - `ai = NormalAIManager(state, config, joker_manager)`
  - `freezes = ai.recommend_freezes()`
  - `actions = ai.recommend_shop_actions(shop_display)`
- EV Helper
  - `from ai_simulation import AIEvaluator`
  - `ev = AIEvaluator.estimate_expected_score(grid_cards, frozen_cells, config, active_jokers, samples=200)`
