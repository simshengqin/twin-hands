"""
Quota Analysis Simulator for New Scoring System

Simulates realistic gameplay to determine appropriate quota targets:
- 7 spins per round
- 12 reroll tokens (shared across all spins)
- Top 3 out of 10 hands count
- New flat chip scoring system
- Strategic reroll usage (reroll columns that improve top 3)

Goal: Find balanced quotas for rounds 1-3 without jokers
"""

import sys
import time
from collections import Counter
from statistics import mean, median, stdev
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, 'C:\\Users\\User\\Documents\\GitHub\\poker-grid')

from src.resources.card_resource import CardResource
from src.resources.deck_resource import DeckResource
from src.resources.game_config_resource import GameConfigResource
from src.resources.game_state_resource import GameStateResource
from src.resources.grid_cell_resource import GridCellResource
from src.managers.grid_manager import GridManager
from src.utils.poker_evaluator import PokerEvaluator


# New scoring table (flat chips per hand)
NEW_HAND_SCORES = {
    "Royal Flush": 150,
    "Five of a Kind": 130,
    "Straight Flush": 110,
    "Four of a Kind": 90,
    "Full House": 70,
    "Flush": 55,
    "Straight": 45,
    "Three of a Kind": 30,
    "Two Pair": 20,
    "One Pair": 10,
    "High Card": 3,
}


class QuotaAnalysisSimulator:
    """Simulate realistic rounds to analyze quota balance."""

    def __init__(self, num_rounds: int = 10_000):
        self.num_rounds = num_rounds
        self.config = GameConfigResource()

        # Override config values for simulation
        self.spins_per_round = 7
        self.reroll_tokens = 12

        # Results tracking
        self.round_scores = []
        self.spin_scores = []
        self.tokens_used_per_round = []
        self.rerolls_per_spin = []

    def run_simulation(self):
        """Run the full simulation."""
        print("=" * 80)
        print("QUOTA ANALYSIS SIMULATOR (New Scoring System)")
        print("=" * 80)
        print(f"Simulations: {self.num_rounds:,} rounds")
        print(f"Spins per round: {self.spins_per_round}")
        print(f"Reroll tokens per round: {self.reroll_tokens}")
        print(f"Scoring: Top 3 out of 10 hands (flat chips)")
        print(f"Reroll strategy: Greedy (improve top 3)")
        print("=" * 80)
        print()

        start_time = time.time()

        for i in range(self.num_rounds):
            round_score = self._simulate_one_round()
            self.round_scores.append(round_score)

            if (i + 1) % 1_000 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                eta = (self.num_rounds - (i + 1)) / rate
                print(f"[{i+1:,} / {self.num_rounds:,}] "
                      f"{(i+1)/self.num_rounds*100:.1f}% | "
                      f"Rate: {rate:.0f} rounds/sec | "
                      f"ETA: {eta:.0f}s")

        elapsed = time.time() - start_time
        self._print_results(elapsed)

    def _simulate_one_round(self) -> int:
        """
        Simulate one complete round with strategic reroll usage.
        Returns cumulative score for the round.
        """
        tokens_left = self.reroll_tokens
        cumulative_score = 0
        round_token_usage = 0

        for spin_idx in range(self.spins_per_round):
            # Deal initial grid
            grid, deck = self._create_fresh_grid()

            # Score initial grid
            initial_score, initial_top3 = self._score_grid(grid)

            # Decide if we should reroll (simple greedy strategy)
            # Early spins: more aggressive rerolls
            # Late spins: conservative (save tokens for bad situations)
            reroll_threshold = 80 if spin_idx < 4 else 100

            best_score = initial_score
            rerolls_used = 0

            # Try rerolling if score is below threshold and we have tokens
            if initial_score < reroll_threshold and tokens_left > 0:
                # Simple strategy: reroll 1-2 worst columns if affordable
                num_to_reroll = min(2, tokens_left)

                # Identify worst columns (columns not in top 3)
                top3_indices = set((hand['type'], hand['index']) for hand in initial_top3)
                worst_cols = [col for col in range(5) if ('col', col) not in top3_indices]

                if worst_cols and num_to_reroll > 0:
                    # Reroll random worst columns
                    cols_to_reroll = worst_cols[:num_to_reroll]
                    self._reroll_columns(grid, deck, cols_to_reroll)

                    rerolled_score, _ = self._score_grid(grid)
                    best_score = rerolled_score
                    tokens_left -= num_to_reroll
                    rerolls_used = num_to_reroll
                    round_token_usage += num_to_reroll

            cumulative_score += best_score
            self.spin_scores.append(best_score)
            self.rerolls_per_spin.append(rerolls_used)

        self.tokens_used_per_round.append(round_token_usage)
        return cumulative_score

    def _create_fresh_grid(self) -> Tuple[List[List], DeckResource]:
        """Create a fresh random 5x5 grid."""
        deck = DeckResource()
        for rank in GameConfigResource.RANKS:
            for suit in GameConfigResource.SUITS:
                deck.add_card(CardResource(rank=rank, suit=suit))

        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                cell = GridCellResource(row=row, col=col)
                cell.set_card(deck.draw_random())
                grid_row.append(cell)
            grid.append(grid_row)

        return grid, deck

    def _reroll_columns(self, grid: List[List], deck: DeckResource, col_indices: List[int]):
        """Reroll specified columns."""
        for col in col_indices:
            for row in range(5):
                grid[row][col].set_card(deck.draw_random())

    def _score_grid(self, grid: List[List]) -> Tuple[int, List[dict]]:
        """
        Score a grid using new scoring system.
        Returns (total_score, top_3_hands).
        """
        all_hands = []

        # Score rows
        for row_idx in range(5):
            cards = [grid[row_idx][col].card for col in range(5)]
            if all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                chips = NEW_HAND_SCORES.get(hand.hand_type, 0)
                all_hands.append({
                    'type': 'row',
                    'index': row_idx,
                    'score': chips,
                    'hand_type': hand.hand_type
                })

        # Score columns
        for col_idx in range(5):
            cards = [grid[row][col_idx].card for row in range(5)]
            if all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                chips = NEW_HAND_SCORES.get(hand.hand_type, 0)
                all_hands.append({
                    'type': 'col',
                    'index': col_idx,
                    'score': chips,
                    'hand_type': hand.hand_type
                })

        # Get top 3 (rows-first priority for ties)
        def get_priority(line):
            if line['type'] == 'row':
                return (0, line['index'])
            else:
                return (1, line['index'])

        sorted_hands = sorted(all_hands, key=lambda x: (-x['score'], get_priority(x)))
        top_3 = sorted_hands[:3]
        total_score = sum(hand['score'] for hand in top_3)

        return total_score, top_3

    def _print_results(self, elapsed: float):
        """Print comprehensive results."""
        print()
        print("=" * 80)
        print("SIMULATION COMPLETE")
        print("=" * 80)
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Rounds simulated: {self.num_rounds:,}")
        print(f"Rate: {self.num_rounds/elapsed:.0f} rounds/sec")
        print()

        # Round score statistics
        print("=" * 80)
        print("ROUND SCORE DISTRIBUTION (7 spins, with strategic rerolls)")
        print("=" * 80)
        print(f"{'Statistic':<20} {'Value':>12}")
        print("-" * 80)
        print(f"{'Minimum':<20} {min(self.round_scores):>12}")
        print(f"{'Maximum':<20} {max(self.round_scores):>12}")
        print(f"{'Mean':<20} {mean(self.round_scores):>12.1f}")
        print(f"{'Median':<20} {median(self.round_scores):>12.1f}")
        print(f"{'Std Dev':<20} {stdev(self.round_scores):>12.1f}")
        print()

        # Percentile analysis
        sorted_scores = sorted(self.round_scores)
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        print("SCORE PERCENTILES:")
        print("-" * 80)
        for p in percentiles:
            idx = int(len(sorted_scores) * p / 100)
            score = sorted_scores[idx]
            print(f"  {p}th percentile: {score:>6} chips")
        print()

        # Token usage
        print("=" * 80)
        print("REROLL TOKEN USAGE")
        print("=" * 80)
        print(f"Mean tokens used per round: {mean(self.tokens_used_per_round):.2f} / {self.reroll_tokens}")
        print(f"Median tokens used: {median(self.tokens_used_per_round):.1f}")
        print(f"Token usage rate: {mean(self.tokens_used_per_round) / self.reroll_tokens * 100:.1f}%")
        print()

        # Recommended quotas
        print("=" * 80)
        print("RECOMMENDED QUOTAS (based on percentiles)")
        print("=" * 80)

        # Round 1: ~50th percentile (half of players pass)
        round1_quota = sorted_scores[int(len(sorted_scores) * 0.50)]

        # Round 2: ~65th percentile (bit harder)
        round2_quota = sorted_scores[int(len(sorted_scores) * 0.65)]

        # Round 3: ~75th percentile (challenging)
        round3_quota = sorted_scores[int(len(sorted_scores) * 0.75)]

        print(f"Round 1 (50th percentile): {round1_quota:>6} chips")
        print(f"Round 2 (65th percentile): {round2_quota:>6} chips")
        print(f"Round 3 (75th percentile): {round3_quota:>6} chips")
        print()
        print("Note: These are WITHOUT jokers. Jokers will significantly boost scores.")
        print()

        # Per-spin statistics
        print("=" * 80)
        print("PER-SPIN STATISTICS")
        print("=" * 80)
        print(f"Mean score per spin: {mean(self.spin_scores):.1f} chips")
        print(f"Median score per spin: {median(self.spin_scores):.1f} chips")
        print(f"Mean rerolls per spin: {mean(self.rerolls_per_spin):.2f}")
        print()


def main():
    """Main entry point."""
    num_rounds = 10_000
    if len(sys.argv) > 1:
        try:
            num_rounds = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default 10,000")

    simulator = QuotaAnalysisSimulator(num_rounds=num_rounds)
    simulator.run_simulation()


if __name__ == "__main__":
    main()
