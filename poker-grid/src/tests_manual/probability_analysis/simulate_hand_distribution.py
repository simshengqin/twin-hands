"""
Probability Distribution Simulator for Poker Grid

Simulates 1,000,000 random grids to analyze:
- Frequency of each poker hand type
- Statistical distribution (min/max/median/avg per grid)
- Comparison with theoretical 5-card poker probabilities
- Detailed analysis of hand occurrence patterns

No freezing, no quota, no filtering - pure random grid analysis.
"""

import sys
import json
import time
from collections import defaultdict, Counter
from typing import Dict, List
from statistics import mean, median, stdev

# Add project root to path
sys.path.insert(0, 'C:\\Users\\User\\Documents\\GitHub\\poker-grid')

from src.resources.card_resource import CardResource
from src.resources.deck_resource import DeckResource
from src.resources.game_config_resource import GameConfigResource
from src.resources.game_state_resource import GameStateResource
from src.managers.grid_manager import GridManager
from src.utils.poker_evaluator import PokerEvaluator


class HandDistributionSimulator:
    """Simulates millions of grids to analyze hand probability distribution."""

    # Theoretical probabilities for 5-card poker (with replacement, infinite deck)
    # These are approximate - actual values depend on sampling method
    THEORETICAL_PROBABILITIES = {
        "Royal Flush": 0.00015,      # ~0.015%
        "Straight Flush": 0.00139,   # ~0.139%
        "Four of a Kind": 0.024,     # ~2.4%
        "Full House": 0.144,         # ~14.4%
        "Flush": 0.197,              # ~19.7%
        "Straight": 0.392,           # ~39.2%
        "Three of a Kind": 2.11,     # ~21.1%
        "Two Pair": 4.75,            # ~47.5%
        "One Pair": 42.26,           # ~42.26%
        "High Card": 50.12,          # ~50.12%
    }

    def __init__(self, num_simulations: int = 1_000_000):
        self.num_simulations = num_simulations
        self.config = GameConfigResource()

        # Statistics tracking
        self.hand_counts = Counter()  # Total counts across all hands
        self.per_grid_counts = defaultdict(list)  # Per-grid occurrence of each hand type
        self.total_hands_evaluated = 0

        # Progress tracking
        self.start_time = None
        self.last_report_time = None

    def run_simulation(self):
        """Run the full simulation."""
        print("=" * 80)
        print(f"POKER GRID HAND DISTRIBUTION SIMULATOR")
        print("=" * 80)
        print(f"Simulations: {self.num_simulations:,} grids")
        print(f"Grid size: {self.config.grid_rows}x{self.config.grid_cols}")
        print(f"Hands per grid: {self.config.grid_rows + self.config.grid_cols}")
        print(f"Total hands to evaluate: {self.num_simulations * (self.config.grid_rows + self.config.grid_cols):,}")
        print(f"Sampling method: WITH REPLACEMENT (infinite deck)")
        print("=" * 80)
        print()

        self.start_time = time.time()
        self.last_report_time = self.start_time

        for i in range(self.num_simulations):
            self._simulate_one_grid()

            # Progress report every 10,000 grids
            if (i + 1) % 10_000 == 0:
                self._report_progress(i + 1)

        self._print_results()
        self._save_results()

    def _simulate_one_grid(self):
        """Simulate one random grid and collect hand statistics."""
        from src.resources.grid_cell_resource import GridCellResource

        # Create fresh deck and grid
        deck = self._create_standard_deck()

        # Create empty grid
        grid = []
        for row in range(self.config.grid_rows):
            grid_row = []
            for col in range(self.config.grid_cols):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Create state
        state = GameStateResource(
            grid=grid,
            deck=deck,
            config=self.config
        )

        grid_manager = GridManager(state, self.config)

        # Fill entire grid randomly (no freezing) - deal_grid fills all unfrozen cells
        grid_manager.deal_grid()

        # Evaluate all hands (rows + columns)
        grid_hand_counts = Counter()

        # Evaluate rows
        for row in range(self.config.grid_rows):
            cards = grid_manager.get_row_cards(row)
            if len(cards) == 5 and all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                self.hand_counts[hand.hand_type] += 1
                grid_hand_counts[hand.hand_type] += 1
                self.total_hands_evaluated += 1

        # Evaluate columns
        for col in range(self.config.grid_cols):
            cards = grid_manager.get_col_cards(col)
            if len(cards) == 5 and all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                self.hand_counts[hand.hand_type] += 1
                grid_hand_counts[hand.hand_type] += 1
                self.total_hands_evaluated += 1

        # Store per-grid counts for each hand type
        for hand_type in GameConfigResource.HAND_SCORES.keys():
            count = grid_hand_counts[hand_type]
            self.per_grid_counts[hand_type].append(count)

    def _create_standard_deck(self) -> DeckResource:
        """Create a standard 52-card deck."""
        deck = DeckResource()
        for rank in GameConfigResource.RANKS:
            for suit in GameConfigResource.SUITS:
                deck.add_card(CardResource(rank=rank, suit=suit))
        return deck

    def _report_progress(self, completed: int):
        """Print progress update."""
        current_time = time.time()
        elapsed = current_time - self.start_time
        rate = completed / elapsed
        remaining = (self.num_simulations - completed) / rate

        print(f"[{completed:,} / {self.num_simulations:,}] "
              f"{completed/self.num_simulations*100:.1f}% complete | "
              f"Rate: {rate:.0f} grids/sec | "
              f"ETA: {remaining:.0f}s")

    def _print_results(self):
        """Print comprehensive results."""
        elapsed = time.time() - self.start_time

        print()
        print("=" * 80)
        print("SIMULATION COMPLETE")
        print("=" * 80)
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Grids simulated: {self.num_simulations:,}")
        print(f"Hands evaluated: {self.total_hands_evaluated:,}")
        print(f"Rate: {self.num_simulations/elapsed:.0f} grids/sec")
        print()

        # Overall distribution
        print("=" * 80)
        print("HAND DISTRIBUTION ACROSS ALL GRIDS")
        print("=" * 80)
        print(f"{'Hand Type':<20} {'Count':>12} {'Percentage':>12} {'Theoretical':>12} {'Diff':>10}")
        print("-" * 80)

        # Sort by poker hand rank (best to worst)
        hand_order = list(GameConfigResource.HAND_SCORES.keys())

        for hand_type in hand_order:
            count = self.hand_counts[hand_type]
            percentage = (count / self.total_hands_evaluated * 100) if self.total_hands_evaluated > 0 else 0
            theoretical = self.THEORETICAL_PROBABILITIES.get(hand_type, 0)
            diff = percentage - theoretical

            print(f"{hand_type:<20} {count:>12,} {percentage:>11.3f}% {theoretical:>11.3f}% {diff:>9.2f}%")

        print("-" * 80)
        print(f"{'TOTAL':<20} {self.total_hands_evaluated:>12,} {100.0:>11.1f}%")
        print()

        # Per-grid statistics
        print("=" * 80)
        print("PER-GRID STATISTICS")
        print("=" * 80)
        print(f"{'Hand Type':<20} {'Min':>6} {'Max':>6} {'Median':>8} {'Mean':>8} {'StdDev':>8}")
        print("-" * 80)

        for hand_type in hand_order:
            counts = self.per_grid_counts[hand_type]
            if counts:
                min_val = min(counts)
                max_val = max(counts)
                median_val = median(counts)
                mean_val = mean(counts)
                std_val = stdev(counts) if len(counts) > 1 else 0

                print(f"{hand_type:<20} {min_val:>6} {max_val:>6} {median_val:>8.2f} "
                      f"{mean_val:>8.2f} {std_val:>8.2f}")
        print()

        # Hand quality analysis
        print("=" * 80)
        print("GRID QUALITY ANALYSIS")
        print("=" * 80)

        # Count grids with at least one occurrence of each hand type
        for hand_type in hand_order:
            counts = self.per_grid_counts[hand_type]
            grids_with_hand = sum(1 for c in counts if c > 0)
            percentage = (grids_with_hand / self.num_simulations * 100) if self.num_simulations > 0 else 0
            print(f"{hand_type:<20} appeared in {grids_with_hand:>10,} grids ({percentage:>6.2f}%)")
        print()

        # Special combinations
        print("=" * 80)
        print("SPECIAL COMBINATIONS")
        print("=" * 80)

        royal_flush_grids = sum(1 for c in self.per_grid_counts["Royal Flush"] if c > 0)
        multiple_royal_grids = sum(1 for c in self.per_grid_counts["Royal Flush"] if c > 1)
        no_pair_grids = sum(1 for c in self.per_grid_counts["High Card"] if c == 10)

        print(f"Grids with at least 1 Royal Flush: {royal_flush_grids:,} "
              f"({royal_flush_grids/self.num_simulations*100:.4f}%)")
        print(f"Grids with 2+ Royal Flushes: {multiple_royal_grids:,} "
              f"({multiple_royal_grids/self.num_simulations*100:.6f}%)")
        print(f"Grids with ALL High Cards (no pairs): {no_pair_grids:,} "
              f"({no_pair_grids/self.num_simulations*100:.4f}%)")
        print()

    def _save_results(self):
        """Save results to JSON file."""
        results = {
            "simulation_info": {
                "num_simulations": self.num_simulations,
                "total_hands_evaluated": self.total_hands_evaluated,
                "grid_size": f"{self.config.grid_rows}x{self.config.grid_cols}",
                "hands_per_grid": self.config.grid_rows + self.config.grid_cols,
                "sampling_method": "WITH_REPLACEMENT",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "overall_distribution": {},
            "per_grid_statistics": {},
            "theoretical_comparison": {}
        }

        # Overall distribution
        for hand_type in GameConfigResource.HAND_SCORES.keys():
            count = self.hand_counts[hand_type]
            percentage = (count / self.total_hands_evaluated * 100) if self.total_hands_evaluated > 0 else 0
            theoretical = self.THEORETICAL_PROBABILITIES.get(hand_type, 0)

            results["overall_distribution"][hand_type] = {
                "count": count,
                "percentage": round(percentage, 4),
                "theoretical_percentage": theoretical,
                "difference": round(percentage - theoretical, 4)
            }

        # Per-grid statistics
        for hand_type in GameConfigResource.HAND_SCORES.keys():
            counts = self.per_grid_counts[hand_type]
            if counts:
                results["per_grid_statistics"][hand_type] = {
                    "min": min(counts),
                    "max": max(counts),
                    "median": round(median(counts), 4),
                    "mean": round(mean(counts), 4),
                    "std_dev": round(stdev(counts), 4) if len(counts) > 1 else 0,
                    "grids_with_at_least_one": sum(1 for c in counts if c > 0)
                }

        # Save to file
        output_file = "src/tests_manual/probability_analysis/results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {output_file}")
        print()


def main():
    """Main entry point."""
    # Default to 1M simulations, but allow command-line override
    num_sims = 1_000_000
    if len(sys.argv) > 1:
        try:
            num_sims = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default 1,000,000")

    simulator = HandDistributionSimulator(num_simulations=num_sims)
    simulator.run_simulation()


if __name__ == "__main__":
    main()
