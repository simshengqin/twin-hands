"""
Smart AI Manager
EV-driven AI for freeze and shop decisions under the top-K-lines rule.
Fair: uses only public grid, config, active jokers, and shop display.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING

from ai_simulation.utils.ai_evaluator import AIEvaluator

if TYPE_CHECKING:
    from src.resources.game_state_resource import GameStateResource
    from src.resources.game_config_resource import GameConfigResource
    from src.managers.joker_manager import JokerManager
    from src.resources.card_resource import CardResource


class SmartAIManager:
    """
    Smart AI that:
    - Picks freezes by evaluating candidate sets via Monte Carlo EV, summing only top-K lines.
    - Chooses shop actions (buy/sell/reroll/none) based on value heuristics and budget/slots.

    Fairness: Uses only public state (grid, config, active jokers, shop_display, can_afford).
    """

    # Tuning knobs (can be exposed to a separate ai_config later)
    DEFAULT_SAMPLES = 200
    CANDIDATE_CAP = 24
    BUY_THRESHOLD = 0.02      # minimal value score to justify buy
    SELL_THRESHOLD = 0.05     # minimal net gain to justify selling weakest to buy
    REROLL_MIN_VALUE = 0.015  # reroll when best shop value below this and affordable

    def __init__(self, state: 'GameStateResource', config: 'GameConfigResource', joker_manager: Optional['JokerManager'] = None):
        self.state = state
        self.config = config
        self.joker_manager = joker_manager
        self._last_explanation: str = ""

    def recommend_freezes(self, max_to_freeze: int = 2, samples: Optional[int] = None) -> List[Tuple[int, int]]:
        """
        Recommend a set of cells to freeze using EV across candidate sets.
        Returns list of (row, col).
        """
        if max_to_freeze <= 0:
            return []

        candidates = self._generate_candidates(max_to_freeze)
        candidates = candidates[: self.CANDIDATE_CAP]

        grid_cards = [[cell.card for cell in row] for row in self.state.grid]
        active_jokers = list(self.joker_manager.active_jokers) if self.joker_manager else []

        best_ev = -1.0
        best = []
        used_samples = samples if samples is not None else self.DEFAULT_SAMPLES

        for cand in candidates:
            ev = AIEvaluator.estimate_expected_score(
                grid_cards=grid_cards,
                frozen_cells=cand,
                config=self.config,
                active_jokers=active_jokers,
                samples=used_samples,
            )
            if ev > best_ev:
                best_ev = ev
                best = cand

        self._last_explanation = f"Freeze EV picked {best} with EV={best_ev:.1f} over {len(candidates)} candidates"
        return best

    def _generate_candidates(self, max_to_freeze: int) -> List[List[Tuple[int, int]]]:
        """
        Generate freeze candidates seeded by strong human heuristics, then expanded.
        Includes [] (no-freeze) always.
        """
        cards = []  # (card, r, c)
        for r in range(self.config.grid_rows):
            for c in range(self.config.grid_cols):
                cell = self.state.grid[r][c]
                if cell.card:
                    cards.append((cell.card, r, c))

        seeds: List[List[Tuple[int, int]]] = [[]]

        # Aligned pair
        aligned = self._find_best_aligned_pair(cards)
        if aligned:
            seeds.append(aligned[:max_to_freeze])

        # Best suited pair
        suited = self._find_best_suited(cards)
        if suited:
            seeds.append(suited[:max_to_freeze])

        # Highest single ranks as singles
        ranked = sorted(cards, key=lambda t: self.config.RANK_VALUES[t[0].rank], reverse=True)
        if ranked:
            seeds.append([(ranked[0][1], ranked[0][2])])
        if len(ranked) > 1 and max_to_freeze >= 2:
            seeds.append([(ranked[0][1], ranked[0][2]), (ranked[1][1], ranked[1][2])])

        # Deduplicate while preserving order
        seen = set()
        uniq: List[List[Tuple[int, int]]] = []
        for s in seeds:
            key = tuple(sorted(s))
            if key not in seen:
                seen.add(key)
                uniq.append(s)

        return uniq

    def _find_best_aligned_pair(self, all_cards: List[Tuple['CardResource', int, int]]) -> Optional[List[Tuple[int, int]]]:
        by_rank = {}
        for card, r, c in all_cards:
            by_rank.setdefault(card.rank, []).append((r, c))
        best = None
        best_val = -1
        for rank, pos in by_rank.items():
            if len(pos) < 2:
                continue
            for i in range(len(pos)):
                for j in range(i + 1, len(pos)):
                    (r1, c1), (r2, c2) = pos[i], pos[j]
                    if r1 == r2 or c1 == c2:
                        v = self.config.RANK_VALUES[rank]
                        if v > best_val:
                            best_val = v
                            best = [(r1, c1), (r2, c2)]
        return best

    def _find_best_suited(self, all_cards: List[Tuple['CardResource', int, int]]) -> Optional[List[Tuple[int, int]]]:
        by_suit = {}
        for card, r, c in all_cards:
            by_suit.setdefault(card.suit, []).append((card, r, c))
        best = None
        best_sum = -1
        for suit, items in by_suit.items():
            if len(items) < 2:
                continue
            items.sort(key=lambda t: self.config.RANK_VALUES[t[0].rank], reverse=True)
            top2 = items[:2]
            val = sum(self.config.RANK_VALUES[t[0].rank] for t in top2)
            if val > best_sum:
                best_sum = val
                best = [(top2[0][1], top2[0][2]), (top2[1][1], top2[1][2])]
        return best

    def recommend_shop_action(self, shop_display: List[dict], reroll_cost: int) -> Tuple[str, int]:
        """
        Decide one shop action: ('buy'| 'sell' | 'reroll' | 'none', index or -1)
        For 'sell', index refers to the joker index to sell in joker_manager.active_jokers.
        """
        if not self.joker_manager:
            return ("none", -1)

        active = list(self.joker_manager.active_jokers)
        shop_items = [it for it in shop_display if it.get('joker')]

        # Evaluate shop jokers
        best_shop = None
        best_value = float('-inf')
        for it in shop_items:
            j = it['joker']
            val = AIEvaluator.evaluate_joker_value(j, active)
            if val > best_value:
                best_value = val
                best_shop = it

        # Compute weakest currently owned joker value
        weakest_idx = -1
        weakest_value = float('inf')
        for idx, j in enumerate(active):
            val = AIEvaluator.evaluate_joker_value(j, [jj for k, jj in enumerate(active) if k != idx])
            if val < weakest_value:
                weakest_value = val
                weakest_idx = idx

        # Decide action
        if best_shop and best_value >= self.BUY_THRESHOLD:
            cost = best_shop['cost']
            # Buy if slot available and affordable
            if self.joker_manager.has_empty_slot() and self.state.can_afford(cost):
                self._last_explanation = f"Buy {best_shop['name']} (value={best_value:.2f})"
                return ("buy", best_shop['index'])

            # Else, consider selling weakest to buy if net gain is sufficient
            if weakest_idx >= 0:
                # Money after selling weakest
                projected_money = self.state.money + active[weakest_idx].sell_value
                if projected_money >= cost and (best_value - weakest_value) >= self.SELL_THRESHOLD:
                    self._last_explanation = (
                        f"Sell idx {weakest_idx} (value={weakest_value:.2f}) to buy {best_shop['name']} (value={best_value:.2f})"
                    )
                    return ("sell", weakest_idx)

        # Consider reroll if affordable and best shop value is too low
        if self.state.can_afford(reroll_cost) and (best_value < self.REROLL_MIN_VALUE or not best_shop):
            self._last_explanation = f"Reroll (best_value={best_value:.2f})"
            return ("reroll", -1)

        self._last_explanation = "No beneficial action"
        return ("none", -1)

    def explain_last_decision(self) -> str:
        return self._last_explanation
