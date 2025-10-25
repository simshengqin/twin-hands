"""
Reroll-Based Probability Distribution Simulator

Simulates grids with smart column reroll strategy to analyze:
- How rerolls change hand type probability distribution
- Compare 0, 1, 2, 3 rerolls per grid
- Use EV-based row upgrade strategy (focus on rows, columns are RNG)

Strategy: EV-based row upgrades
- Only consider ROW hands (columns are pure RNG when rerolled)
- Prioritize upgrades by Expected Value (rank_jump × probability)
- Reroll column that helps highest EV row upgrade
"""

import sys
import json
import time
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
from statistics import mean, median, stdev

# Add project root to path
sys.path.insert(0, 'C:\\Users\\User\\Documents\\GitHub\\poker-grid')

from src.resources.card_resource import CardResource
from src.resources.deck_resource import DeckResource
from src.resources.game_config_resource import GameConfigResource
from src.resources.grid_cell_resource import GridCellResource
from src.resources.game_state_resource import GameStateResource
from src.managers.grid_manager import GridManager
from src.utils.poker_evaluator import PokerEvaluator


class RerollDistributionSimulator:
    """Simulates grids with EV-based smart reroll strategy."""

    def __init__(self, num_simulations: int = 100_000):
        self.num_simulations = num_simulations
        self.config = GameConfigResource()

        # Results storage: [num_rerolls][stat_type]
        self.results = {}
        for num_rerolls in [0, 1, 2, 3]:
            self.results[num_rerolls] = {
                'hand_counts': Counter(),
                'per_grid_counts': defaultdict(list),
                'total_hands': 0
            }

    def run_simulation(self):
        """Run simulation for all reroll scenarios."""
        print("=" * 80)
        print("REROLL-BASED HAND DISTRIBUTION SIMULATOR")
        print("=" * 80)
        print(f"Simulations: {self.num_simulations:,} grids per scenario")
        print(f"Grid size: {self.config.grid_rows}x{self.config.grid_cols}")
        print(f"Hands per grid: {self.config.grid_rows + self.config.grid_cols}")
        print(f"Reroll scenarios: 0, 1, 2, 3 rerolls")
        print(f"Strategy: EV-based row upgrades (focus on rows, columns are RNG)")
        print("=" * 80)
        print()

        for num_rerolls in [0, 1, 2, 3]:
            print(f"Running scenario: {num_rerolls} reroll{'s' if num_rerolls != 1 else ''}...")
            start_time = time.time()

            for i in range(self.num_simulations):
                self._simulate_one_grid(num_rerolls)

                if (i + 1) % 10_000 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    remaining = (self.num_simulations - (i + 1)) / rate
                    print(f"  [{i+1:,} / {self.num_simulations:,}] "
                          f"{(i+1)/self.num_simulations*100:.1f}% | "
                          f"Rate: {rate:.0f} grids/sec | ETA: {remaining:.0f}s")

            elapsed = time.time() - start_time
            print(f"  Completed in {elapsed:.2f}s ({self.num_simulations/elapsed:.0f} grids/sec)")
            print()

        self._print_results()
        self._save_results()

    def _simulate_one_grid(self, num_rerolls: int):
        """Simulate one grid with specified number of rerolls."""
        # Create fresh deck and grid
        deck = self._create_standard_deck()
        grid = []
        for row in range(self.config.grid_rows):
            grid_row = []
            for col in range(self.config.grid_cols):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        state = GameStateResource(grid=grid, deck=deck, config=self.config)
        grid_manager = GridManager(state, self.config)

        # Initial deal
        grid_manager.deal_grid()

        # Apply rerolls using EV-based strategy
        for _ in range(num_rerolls):
            col_to_reroll = self._choose_column_to_reroll(grid_manager)
            if col_to_reroll is not None:
                self._reroll_column(grid_manager, col_to_reroll, deck)

        # Evaluate final grid (all 10 hands)
        grid_hand_counts = Counter()

        # Evaluate rows
        for row in range(self.config.grid_rows):
            cards = grid_manager.get_row_cards(row)
            if len(cards) == 5 and all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                self.results[num_rerolls]['hand_counts'][hand.hand_type] += 1
                grid_hand_counts[hand.hand_type] += 1
                self.results[num_rerolls]['total_hands'] += 1

        # Evaluate columns
        for col in range(self.config.grid_cols):
            cards = grid_manager.get_col_cards(col)
            if len(cards) == 5 and all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                self.results[num_rerolls]['hand_counts'][hand.hand_type] += 1
                grid_hand_counts[hand.hand_type] += 1
                self.results[num_rerolls]['total_hands'] += 1

        # Store per-grid counts
        for hand_type in GameConfigResource.HAND_SCORES.keys():
            count = grid_hand_counts[hand_type]
            self.results[num_rerolls]['per_grid_counts'][hand_type].append(count)

    def _choose_column_to_reroll(self, grid_manager: GridManager) -> Optional[int]:
        """
        Choose which column to reroll using EV-based row upgrade strategy.

        Returns column index (0-4) or None if no good target found.
        """
        # Only evaluate ROW hands (columns are pure RNG)
        rows = []
        for row in range(5):
            cards = grid_manager.get_row_cards(row)
            if len(cards) == 5 and all(c is not None for c in cards):
                hand = PokerEvaluator.evaluate_hand(cards)
                rows.append((row, hand, cards))

        # Priority by EV (highest first)
        # EV = rank_jump × probability

        # Priority 1: 4-to-Flush (EV = 0.8)
        for row_idx, hand, cards in rows:
            if self._has_4_suited(cards) and hand.hand_type != "Flush":
                col = self._find_offsuit_card_column(grid_manager, row_idx, cards)
                if col is not None:
                    return col

        # Priority 2: 4-to-Straight (EV = 0.6)
        for row_idx, hand, cards in rows:
            if self._has_4_to_straight(cards) and hand.hand_type not in ["Straight", "Straight Flush"]:
                col = self._find_straight_gap_column(grid_manager, row_idx, cards)
                if col is not None:
                    return col

        # Priority 3: Two Pair → Full House (EV = 0.32)
        for row_idx, hand, cards in rows:
            if hand.hand_type == "Two Pair":
                col = self._find_kicker_column(grid_manager, row_idx, cards)
                if col is not None:
                    return col

        # Priority 4: High Card → Pair (EV = 0.31)
        for row_idx, hand, cards in rows:
            if hand.hand_type == "High Card":
                # Just pick first card (any card could pair)
                col = self._get_column_for_row_position(grid_manager, row_idx, 0)
                if col is not None:
                    return col

        # Priority 5: One Pair → Two Pair (EV = 0.23)
        for row_idx, hand, cards in rows:
            if hand.hand_type == "One Pair":
                col = self._find_non_pair_column(grid_manager, row_idx, cards)
                if col is not None:
                    return col

        # Priority 6: Three of a Kind → Four of a Kind (EV = 0.08)
        for row_idx, hand, cards in rows:
            if hand.hand_type == "Three of a Kind":
                col = self._find_non_triple_column(grid_manager, row_idx, cards)
                if col is not None:
                    return col

        # Fallback: No good targets, pick random or first column
        return 0

    def _find_offsuit_card_column(self, grid_manager: GridManager, row_idx: int, cards: List[CardResource]) -> Optional[int]:
        """Find column containing the off-suit card in a 4-to-flush hand."""
        suit_counts = Counter(card.suit for card in cards)
        majority_suit = suit_counts.most_common(1)[0][0]

        for col in range(5):
            card = grid_manager.state.grid[row_idx][col].card
            if card and card.suit != majority_suit:
                return col
        return None

    def _find_straight_gap_column(self, grid_manager: GridManager, row_idx: int, cards: List[CardResource]) -> Optional[int]:
        """Find column to reroll for straight (heuristic: pick a gap or end card)."""
        # Simple heuristic: pick first card (could be smarter)
        return self._get_column_for_row_position(grid_manager, row_idx, 0)

    def _find_kicker_column(self, grid_manager: GridManager, row_idx: int, cards: List[CardResource]) -> Optional[int]:
        """Find column containing the kicker (non-pair card) in Two Pair."""
        rank_counts = Counter(card.rank for card in cards)
        pair_ranks = [rank for rank, count in rank_counts.items() if count == 2]

        for col in range(5):
            card = grid_manager.state.grid[row_idx][col].card
            if card and card.rank not in pair_ranks:
                return col
        return None

    def _find_non_pair_column(self, grid_manager: GridManager, row_idx: int, cards: List[CardResource]) -> Optional[int]:
        """Find column containing a non-pair card in One Pair."""
        rank_counts = Counter(card.rank for card in cards)
        pair_rank = next((rank for rank, count in rank_counts.items() if count == 2), None)

        if pair_rank:
            for col in range(5):
                card = grid_manager.state.grid[row_idx][col].card
                if card and card.rank != pair_rank:
                    return col
        return None

    def _find_non_triple_column(self, grid_manager: GridManager, row_idx: int, cards: List[CardResource]) -> Optional[int]:
        """Find column containing a non-triple card in Three of a Kind."""
        rank_counts = Counter(card.rank for card in cards)
        triple_rank = next((rank for rank, count in rank_counts.items() if count == 3), None)

        if triple_rank:
            for col in range(5):
                card = grid_manager.state.grid[row_idx][col].card
                if card and card.rank != triple_rank:
                    return col
        return None

    def _get_column_for_row_position(self, grid_manager: GridManager, row_idx: int, position: int) -> Optional[int]:
        """Get the column index for a specific position in a row."""
        if 0 <= position < 5:
            return position
        return None

    def _reroll_column(self, grid_manager: GridManager, col: int, deck: DeckResource):
        """Reroll a specific column by redrawing all 5 cards."""
        for row in range(5):
            card = deck.draw_random()
            cell = grid_manager.state.grid[row][col]
            cell.set_card(card)

    def _has_4_suited(self, cards: List[CardResource]) -> bool:
        """Check if hand has 4 cards of same suit."""
        if len(cards) != 5:
            return False
        suit_counts = Counter(card.suit for card in cards)
        return max(suit_counts.values()) >= 4

    def _has_4_to_straight(self, cards: List[CardResource]) -> bool:
        """Check if hand is one card away from a straight."""
        if len(cards) != 5:
            return False

        ranks = sorted([GameConfigResource.RANK_VALUES[card.rank] for card in cards])
        unique_ranks = sorted(set(ranks))

        if len(unique_ranks) < 4:
            return False

        # Check for 4 consecutive cards
        for i in range(len(unique_ranks) - 3):
            if unique_ranks[i+3] - unique_ranks[i] == 3:
                return True

        # Check for wheel (A-2-3-4-5) potential
        if set(unique_ranks) & {1, 2, 3, 4, 5}:
            wheel_cards = len(set(unique_ranks) & {1, 2, 3, 4, 5})
            if wheel_cards >= 4:
                return True

        # Check for broadway (10-J-Q-K-A) potential
        if set(unique_ranks) & {10, 11, 12, 13, 14}:
            broadway_cards = len(set(unique_ranks) & {10, 11, 12, 13, 14})
            if broadway_cards >= 4:
                return True

        return False

    def _create_standard_deck(self) -> DeckResource:
        """Create a standard 52-card deck."""
        deck = DeckResource()
        for rank in GameConfigResource.RANKS:
            for suit in GameConfigResource.SUITS:
                deck.add_card(CardResource(rank=rank, suit=suit))
        return deck

    def _print_results(self):
        """Print comprehensive comparison of all scenarios."""
        print()
        print("=" * 80)
        print("SIMULATION COMPLETE - COMPARISON ACROSS REROLL SCENARIOS")
        print("=" * 80)
        print()

        hand_order = list(GameConfigResource.HAND_SCORES.keys())

        # Overall distribution comparison
        print("=" * 80)
        print("HAND DISTRIBUTION COMPARISON")
        print("=" * 80)
        print(f"{'Hand Type':<20} {'0 Rerolls':>12} {'1 Reroll':>12} {'2 Rerolls':>12} {'3 Rerolls':>12}")
        print("-" * 80)

        for hand_type in hand_order:
            row = f"{hand_type:<20}"
            for num_rerolls in [0, 1, 2, 3]:
                count = self.results[num_rerolls]['hand_counts'][hand_type]
                total = self.results[num_rerolls]['total_hands']
                percentage = (count / total * 100) if total > 0 else 0
                row += f" {percentage:>11.3f}%"
            print(row)
        print()

        # Per-grid statistics (median)
        print("=" * 80)
        print("PER-GRID STATISTICS (Median hands per grid)")
        print("=" * 80)
        print(f"{'Hand Type':<20} {'0 Rerolls':>12} {'1 Reroll':>12} {'2 Rerolls':>12} {'3 Rerolls':>12}")
        print("-" * 80)

        for hand_type in hand_order:
            row = f"{hand_type:<20}"
            for num_rerolls in [0, 1, 2, 3]:
                counts = self.results[num_rerolls]['per_grid_counts'][hand_type]
                if counts:
                    median_val = median(counts)
                    row += f" {median_val:>12.2f}"
                else:
                    row += f" {0:>12.2f}"
            print(row)
        print()

        # Improvement analysis
        print("=" * 80)
        print("IMPROVEMENT ANALYSIS (vs 0 rerolls)")
        print("=" * 80)
        print(f"{'Hand Type':<20} {'1 Reroll':>12} {'2 Rerolls':>12} {'3 Rerolls':>12}")
        print("-" * 80)

        for hand_type in hand_order:
            baseline_count = self.results[0]['hand_counts'][hand_type]
            baseline_total = self.results[0]['total_hands']
            baseline_pct = (baseline_count / baseline_total * 100) if baseline_total > 0 else 0

            row = f"{hand_type:<20}"
            for num_rerolls in [1, 2, 3]:
                count = self.results[num_rerolls]['hand_counts'][hand_type]
                total = self.results[num_rerolls]['total_hands']
                pct = (count / total * 100) if total > 0 else 0
                diff = pct - baseline_pct
                row += f" {diff:>+11.3f}%"
            print(row)
        print()

    def _save_results(self):
        """Save results to JSON file."""
        output = {
            "simulation_info": {
                "num_simulations": self.num_simulations,
                "grid_size": f"{self.config.grid_rows}x{self.config.grid_cols}",
                "hands_per_grid": self.config.grid_rows + self.config.grid_cols,
                "reroll_scenarios": [0, 1, 2, 3],
                "strategy": "EV-based row upgrades",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "scenarios": {}
        }

        for num_rerolls in [0, 1, 2, 3]:
            scenario_data = {
                "distribution": {},
                "per_grid_stats": {}
            }

            total_hands = self.results[num_rerolls]['total_hands']

            for hand_type in GameConfigResource.HAND_SCORES.keys():
                count = self.results[num_rerolls]['hand_counts'][hand_type]
                percentage = (count / total_hands * 100) if total_hands > 0 else 0

                scenario_data["distribution"][hand_type] = {
                    "count": count,
                    "percentage": round(percentage, 4)
                }

                counts = self.results[num_rerolls]['per_grid_counts'][hand_type]
                if counts:
                    scenario_data["per_grid_stats"][hand_type] = {
                        "min": min(counts),
                        "max": max(counts),
                        "median": round(median(counts), 4),
                        "mean": round(mean(counts), 4),
                        "std_dev": round(stdev(counts), 4) if len(counts) > 1 else 0
                    }

            output["scenarios"][f"{num_rerolls}_rerolls"] = scenario_data

        output_file = "src/tests_manual/probability_analysis/reroll_results.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Results saved to: {output_file}")
        print()


def main():
    """Main entry point."""
    num_sims = 100_000
    if len(sys.argv) > 1:
        try:
            num_sims = int(sys.argv[1])
        except ValueError:
            print(f"Invalid number: {sys.argv[1]}, using default 100,000")

    simulator = RerollDistributionSimulator(num_simulations=num_sims)
    simulator.run_simulation()


if __name__ == "__main__":
    main()
