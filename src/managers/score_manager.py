"""
Score Manager - Godot-ready scoring controller
Manages scoring operations: evaluate hands, update scores.
In Godot: extends Node
"""

from typing import Tuple, List, Optional


class ScoreManager:
    """
    Manages scoring operations.
    In Godot, this would extend Node and handle scoring logic.

    GDScript equivalent:
    class_name ScoreManager
    extends Node

    var state: GameStateResource
    var config: GameConfig
    var joker_manager: JokerManager
    """

    def __init__(
        self,
        state: 'GameStateResource',
        config: 'GameConfigResource',
        joker_manager: Optional['JokerManager'] = None
    ):
        """
        Initialize the score manager.
        In Godot, this would be _ready() function.
        """
        self.state = state
        self.config = config
        self.joker_manager = joker_manager

    def score_current_grid(self) -> Tuple[int, List['HandResource'], List['HandResource'], List[dict]]:
        """
        Score all rows and columns using flat chip scoring.
        Returns (total_score, row_hands, col_hands, top_lines).

        NEW: Only top 3 scoring lines count towards total_score (including ties).
        top_lines is a list of dicts with: {'type': 'row'/'col', 'index': int, 'score': int, 'rank': int}

        Emits Events.poker_hand_scored for each poker hand evaluated.

        Scoring Formula (new system):
        - Each hand has flat chips (no per-hand mult)
        - Base mult = 1 for all hands
        - Jokers can add global +chips, +mult, or ×mult (applied when implemented)
        - Current: score = chips × 1 = chips (joker system pending)
        - Only top 3 lines are summed for total score
        """
        from src.utils.poker_evaluator import PokerEvaluator
        from src.autoload.events import Events

        row_hands = []
        col_hands = []
        all_lines = []  # Track all scored lines for ranking

        # Score all rows (local chip × mult + jokers)
        for row_idx in range(self.config.grid_rows):
            cards = self.state.get_row(row_idx)
            if len(cards) == 5:
                hand = PokerEvaluator.evaluate_hand(cards)

                # Apply joker effects
                final_chips, final_mult = self._apply_jokers_to_hand(hand, cards)

                # Calculate line score with jokers
                line_score = final_chips * final_mult

                # Update hand with joker-modified values (for display)
                hand.chips = final_chips
                hand.mult = final_mult

                row_hands.append(hand)
                all_lines.append({
                    'type': 'row',
                    'index': row_idx,
                    'score': line_score,
                    'hand': hand
                })
                Events.emit_poker_hand_scored(hand, is_row=True, index=row_idx)

        # Score all columns (local chip × mult + jokers)
        for col_idx in range(self.config.grid_cols):
            cards = self.state.get_col(col_idx)
            if len(cards) == 5:
                hand = PokerEvaluator.evaluate_hand(cards)

                # Apply joker effects
                final_chips, final_mult = self._apply_jokers_to_hand(hand, cards)

                # Calculate line score with jokers
                line_score = final_chips * final_mult

                # Update hand with joker-modified values (for display)
                hand.chips = final_chips
                hand.mult = final_mult

                col_hands.append(hand)
                all_lines.append({
                    'type': 'col',
                    'index': col_idx,
                    'score': line_score,
                    'hand': hand
                })
                Events.emit_poker_hand_scored(hand, is_row=False, index=col_idx)

        # Identify top-K scoring lines (including ties)
        top_lines, total_score = self._get_top_lines(all_lines)

        return total_score, row_hands, col_hands, top_lines

    def _get_top_lines(self, all_lines: List[dict]) -> Tuple[List[dict], int]:
        """
        Get top 3 scoring lines with deterministic priority (rows before cols).
        Returns (top_lines, total_score).

        Priority: Row 0 > Row 1 > ... > Row 4 > Col 0 > Col 1 > ... > Col 4

        Labeling: Lines with same score get same rank label (e.g., "2nd tied")

        Example: Scores [40, 20, 20, 20, 5] for [Row0, Col0, Col1, Row1, Row2]
        After priority sort: [Row0(40), Row1(20), Col0(20), Col1(20), Row2(5)]
        Pick top 3 positions: Row0, Row1, Col0
        Labels: Row0="1st", Row1="2nd tied", Col0="2nd tied"
        """
        if not all_lines:
            return [], 0

        # Define priority: rows first (0-4), then cols (0-4)
        def get_priority(line):
            if line['type'] == 'row':
                return (0, line['index'])  # rows come first
            else:  # 'col'
                return (1, line['index'])  # cols come second

        # Sort by: 1) score descending, 2) priority (rows before cols, then by index)
        sorted_lines = sorted(all_lines, key=lambda x: (-x['score'], get_priority(x)))

        # Take top-K positions
        k = max(0, min(self.config.lines_scored_per_spin, len(sorted_lines)))
        top_k_positions = sorted_lines[:k]

        if not top_k_positions:
            return [], 0

        # Assign ranks based on score comparison
        # If score matches position 0 → rank 1
        # If score matches position 1 (but not 0) → rank 2
        # If score matches position 2 (but not 1) → rank 3
        scores = [line['score'] for line in top_k_positions]

        for i, line in enumerate(top_k_positions):
            if line['score'] == scores[0]:
                line['rank'] = 1
            elif len(scores) > 1 and line['score'] == scores[1]:
                line['rank'] = 2
            else:
                line['rank'] = 3

        total_score = sum(line['score'] for line in top_k_positions)

        return top_k_positions, total_score

    def _apply_jokers_to_hand(self, hand: 'HandResource', cards: List['CardResource']) -> Tuple[int, int]:
        """
        Apply joker effects to a single hand/line.
        Returns (final_chips, final_mult) after joker modifications.
        """
        base_chips = hand.chips
        base_mult = hand.mult

        if self.joker_manager:
            return self.joker_manager.apply_joker_effects(hand, cards, base_chips, base_mult)
        else:
            return base_chips, base_mult

    def score_and_update(self) -> Tuple[int, List['HandResource'], List['HandResource'], List[dict]]:
        """
        Score the current grid and update cumulative score.
        Returns (current_score, row_hands, col_hands, top_lines).
        Emits Events.score_updated signal.
        """
        from src.autoload.events import Events

        current_score, row_hands, col_hands, top_lines = self.score_current_grid()
        self.state.update_score(current_score)

        Events.emit_score_updated(current_score, self.state.cumulative_score)

        return current_score, row_hands, col_hands, top_lines
