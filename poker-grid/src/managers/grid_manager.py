"""
Grid Manager - Godot-ready grid controller
Manages grid operations: dealing, freezing, auto-freeze logic.
In Godot: extends Node
"""

from typing import List, Tuple, Optional


class GridManager:
    """
    Manages grid-specific operations.
    In Godot, this would extend Node and handle grid logic.

    GDScript equivalent:
    class_name GridManager
    extends Node

    var state: GameStateResource
    var config: GameConfig
    """

    def __init__(self, state: 'GameStateResource', config: 'GameConfigResource'):
        """
        Initialize the grid manager.
        In Godot, this would be _ready() function.
        """
        self.state = state
        self.config = config

    def deal_grid(self) -> None:
        """
        Deal cards to all unfrozen cells from the single shared deck.
        Cards are drawn WITH replacement (duplicates allowed).
        Emits Events.cards_dealt signal.
        """
        from src.autoload.events import Events

        for row_idx in range(self.config.grid_rows):
            for col_idx in range(self.config.grid_cols):
                cell = self.state.grid[row_idx][col_idx]

                # Skip frozen cells
                if cell.is_frozen:
                    continue

                # Draw from the shared deck (with replacement)
                card = self.state.deck.draw_random()
                cell.set_card(card)

        Events.emit_cards_dealt()
        Events.emit_grid_updated()

    def auto_freeze_highest_pair(self) -> None:
        """
        Auto-freeze the best combination:
        Priority 1: Highest pair in same row/column
        Priority 2: Two highest cards of same suit
        Priority 3: Don't freeze
        """
        # Collect all cards with their positions
        all_cards = []
        for row_idx in range(self.config.grid_rows):
            for col_idx in range(self.config.grid_cols):
                cell = self.state.grid[row_idx][col_idx]
                if cell.card:
                    all_cards.append((cell.card, row_idx, col_idx))

        # Priority 1: Find pairs in same row or column
        best_pair = self._find_best_aligned_pair(all_cards)
        if best_pair:
            for row, col in best_pair:
                self.state.freeze_cell(row, col)
            return

        # Priority 2: Find two highest cards of same suit
        best_suited = self._find_best_suited_cards(all_cards)
        if best_suited:
            for row, col in best_suited:
                self.state.freeze_cell(row, col)
            return

        # Priority 3: Don't freeze anything

    def _find_best_aligned_pair(
        self,
        all_cards: List[Tuple['CardResource', int, int]]
    ) -> Optional[List[Tuple[int, int]]]:
        """Find the highest pair that's in the same row or column."""
        # Group by rank
        rank_positions = {}
        for card, row, col in all_cards:
            if card.rank not in rank_positions:
                rank_positions[card.rank] = []
            rank_positions[card.rank].append((row, col))

        # Find pairs that are aligned (same row or same column)
        aligned_pairs = []
        for rank, positions in rank_positions.items():
            if len(positions) < 2:
                continue

            # Check all pairs of positions
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    pos1, pos2 = positions[i], positions[j]
                    # Same row or same column?
                    if pos1[0] == pos2[0] or pos1[1] == pos2[1]:
                        rank_value = self.config.RANK_VALUES[rank]
                        aligned_pairs.append((rank_value, rank, [pos1, pos2]))

        if not aligned_pairs:
            return None

        # Return highest ranked aligned pair
        aligned_pairs.sort(key=lambda x: x[0], reverse=True)
        return aligned_pairs[0][2]

    def _find_best_suited_cards(
        self,
        all_cards: List[Tuple['CardResource', int, int]]
    ) -> Optional[List[Tuple[int, int]]]:
        """Find the two highest cards of the same suit."""
        # Group by suit
        suit_cards = {}
        for card, row, col in all_cards:
            if card.suit not in suit_cards:
                suit_cards[card.suit] = []
            suit_cards[card.suit].append((card, row, col))

        # Find suits with at least 2 cards
        best_suited = None
        best_value = 0

        for suit, cards in suit_cards.items():
            if len(cards) < 2:
                continue

            # Sort by rank value, take top 2
            cards.sort(key=lambda x: self.config.RANK_VALUES[x[0].rank], reverse=True)
            top_two = cards[:2]

            # Sum of top 2 values
            total_value = sum(self.config.RANK_VALUES[c[0].rank] for c in top_two)

            if total_value > best_value:
                best_value = total_value
                best_suited = [(c[1], c[2]) for c in top_two]

        return best_suited

    def get_row_cards(self, row_index: int) -> List['CardResource']:
        """Get all cards in a row."""
        return [cell.card for cell in self.state.grid[row_index] if cell.card]

    def get_col_cards(self, col_index: int) -> List['CardResource']:
        """Get all cards in a column."""
        return [self.state.grid[row][col_index].card
                for row in range(self.config.grid_rows)
                if self.state.grid[row][col_index].card]
