"""
AI Evaluator Utilities
Static helpers to estimate expected value and suggest actions.
"""

import random
from typing import List, Tuple, Optional


class AIEvaluator:
    """
    Static helper functions for AI evaluation.
    - Monte Carlo estimate of grid score given freeze plan
    - Lightweight scoring using PokerEvaluator + JokerManager
    """

    @staticmethod
    def estimate_expected_score(
        grid_cards: List[List[Optional['CardResource']]],
        frozen_cells: List[Tuple[int, int]],
        config: 'GameConfigResource',
        active_jokers: Optional[List['JokerResource']] = None,
        samples: int = 200,
        rng: Optional[random.Random] = None,
    ) -> float:
        """
        Estimate expected score after redeal, with given frozen cells.
        Sums only the top-K line scores per config.lines_scored_per_hand.
        """
        from src.utils.card_factory import CardFactory
        from src.utils.poker_evaluator import PokerEvaluator

        # Prepare a deck sampler (with replacement behavior)
        deck = CardFactory.create_deck_resource()

        def draw_random_card():
            return deck.draw_random()

        chips_sum = 0.0

        rows = config.grid_rows
        cols = config.grid_cols

        for _ in range(samples):
            # Build a fresh JokerManager per sample so growing effects
            # do not accumulate across samples (only within this hand simulation).
            joker_manager = None
            if active_jokers:
                from src.managers.joker_manager import JokerManager
                joker_manager = JokerManager(max_slots=len(active_jokers))
                for j in active_jokers:
                    joker_manager.add_joker(j.duplicate())

            # Build a temp 2D grid of cards for this simulation
            temp_cards: List[List[Optional['CardResource']]] = [[None for _ in range(cols)] for _ in range(rows)]

            # Copy frozen cells; redeal others
            frozen_set = set(frozen_cells)
            for r in range(rows):
                for c in range(cols):
                    if (r, c) in frozen_set and grid_cards[r][c] is not None:
                        temp_cards[r][c] = grid_cards[r][c]
                    else:
                        temp_cards[r][c] = draw_random_card()

            # Score all complete rows and columns
            line_scores: List[int] = []

            # Rows
            for r in range(rows):
                line = [temp_cards[r][c] for c in range(cols)]
                if all(line):
                    hand = PokerEvaluator.evaluate_hand(line)
                    chips, mult = AIEvaluator._apply_jokers_to_hand(joker_manager, hand, line)
                    line_scores.append(chips * mult)

            # Cols
            for c in range(cols):
                line = [temp_cards[r][c] for r in range(rows)]
                if all(line):
                    hand = PokerEvaluator.evaluate_hand(line)
                    chips, mult = AIEvaluator._apply_jokers_to_hand(joker_manager, hand, line)
                    line_scores.append(chips * mult)

            # Only count top-K lines as per config
            k = getattr(config, 'lines_scored_per_hand', 3)
            if line_scores:
                line_scores.sort(reverse=True)
                chips_sum += sum(line_scores[:k])

        return chips_sum / float(samples)

    @staticmethod
    def _apply_jokers_to_hand(
        joker_manager: Optional['JokerManager'],
        hand: 'HandResource',
        cards: List['CardResource']
    ) -> Tuple[int, int]:
        base_chips = hand.chips
        base_mult = hand.mult
        if joker_manager is None:
            return base_chips, base_mult
        return joker_manager.apply_joker_effects(hand, cards, base_chips, base_mult)

    @staticmethod
    def evaluate_joker_value(
        joker: 'JokerResource',
        current_active: List['JokerResource']
    ) -> float:
        """
        Heuristic value score for a joker given current synergies.
        Higher is better.
        """
        rarity_weight = {
            'Common': 1.0,
            'Uncommon': 1.3,
            'Rare': 1.7,
            'Legendary': 2.5,
        }.get(joker.rarity, 1.0)

        bonus_weight = {
            '+m': 1.2,   # per-line mult is strong for top-K
            '+c': 0.9,
            'Xm': 1.8,   # multiplicative effects favored
            '++': 1.3,
        }.get(joker.bonus_type, 0.8)

        cond_bonus = 0.0
        frequent_conditions = {'hand_type': {'Pair', 'Two Pair', 'Three of a Kind'},
                               'card_type': {'face'},
                               'rank_parity': {'even', 'odd'}}
        if not joker.condition_type or joker.trigger == 'always':
            cond_bonus += 0.6
        elif joker.condition_type in frequent_conditions:
            # Slightly favor common hand types (Pairs, etc.)
            cond_bonus += 0.5
        else:
            cond_bonus += 0.15

        has_mult = any(j.bonus_type in ('+m', 'Xm') for j in current_active)
        has_chips = any(j.bonus_type in ('+c', '++') for j in current_active)
        synergy = 0.0
        if joker.bonus_type in ('+m', 'Xm') and has_chips:
            synergy += 0.6
        if joker.bonus_type in ('+c', '++') and has_mult:
            synergy += 0.5

        cost_penalty = max(1, joker.cost)
        score = (rarity_weight * bonus_weight * (1.0 + cond_bonus + synergy)) * 10.0 / cost_penalty
        if joker.effect_type == 'growing':
            score *= 1.4  # growing value over many hands/rounds
        return score
