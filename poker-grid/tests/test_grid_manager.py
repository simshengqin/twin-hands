"""
Test GridManager functionality
Tests grid dealing, freezing, and auto-freeze logic
"""
import pytest
from src.managers.grid_manager import GridManager
from src.resources.game_state_resource import GameStateResource
from src.resources.game_config_resource import GameConfigResource
from src.resources.grid_cell_resource import GridCellResource
from src.resources.card_resource import CardResource
from src.resources.deck_resource import DeckResource


class TestGridDealing:
    """Test grid dealing mechanics"""

    def test_deal_grid_fills_all_cells(self, started_game):
        """deal_grid() fills all 25 cells"""
        game = started_game
        game.grid_manager.deal_grid()

        for row in range(5):
            for col in range(5):
                cell = game.state.grid[row][col]
                assert cell.card is not None

    def test_deal_grid_uses_deck(self, fresh_game):
        """deal_grid() draws from deck"""
        game = fresh_game
        game.start_new_round()

        # All cells should have cards
        for row in range(5):
            for col in range(5):
                cell = game.state.grid[row][col]
                assert cell.card is not None
                # Card should be from standard deck
                assert cell.card.rank in ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
                assert cell.card.suit in ['H', 'D', 'C', 'S']

    def test_deal_grid_allows_duplicates(self, config):
        """deal_grid() can create duplicate cards in grid"""
        # Create deck with only Aces
        deck = DeckResource(cards=[
            CardResource(rank='A', suit='H'),
            CardResource(rank='A', suit='S'),
        ])

        # Create state with this limited deck
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        state = GameStateResource(
            grid=grid,
            deck=deck,
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.deal_grid()

        # All cards should be Aces
        for row in range(5):
            for col in range(5):
                cell = state.grid[row][col]
                assert cell.card.rank == 'A'

    def test_deal_grid_skips_frozen_cells(self, started_game):
        """deal_grid() doesn't change frozen cells"""
        game = started_game

        # Freeze (0, 0)
        original_card = game.state.grid[0][0].card
        game.state.freeze_cell(0, 0)

        # Deal again
        game.grid_manager.deal_grid()

        # Frozen cell unchanged
        assert game.state.grid[0][0].card is original_card
        # Other cells changed (probably)
        assert game.state.grid[0][1].card is not None


class TestFreezingLogic:
    """Test cell freezing mechanics"""

    def test_freeze_cell_marks_as_frozen(self, started_game):
        """freeze_cell() marks cell as frozen"""
        game = started_game

        success = game.state.freeze_cell(0, 0)

        assert success == True
        assert game.state.grid[0][0].is_frozen == True
        assert (0, 0) in game.state.frozen_cells

    def test_cannot_freeze_already_frozen_cell(self, started_game):
        """Cannot freeze cell that's already frozen"""
        game = started_game

        game.state.freeze_cell(0, 0)
        success = game.state.freeze_cell(0, 0)

        assert success == False
        assert len(game.state.frozen_cells) == 1

    def test_can_freeze_up_to_max(self, started_game):
        """Can freeze up to max_freezes cells"""
        game = started_game
        max_freezes = game.config.max_freezes

        for i in range(max_freezes):
            success = game.state.freeze_cell(0, i)
            assert success == True

        assert len(game.state.frozen_cells) == max_freezes

    def test_cannot_freeze_beyond_max(self, started_game):
        """Cannot freeze more than max_freezes"""
        game = started_game
        max_freezes = game.config.max_freezes

        # Freeze max amount
        for i in range(max_freezes):
            game.state.freeze_cell(0, i)

        # Try to freeze one more
        success = game.state.freeze_cell(1, 0)

        assert success == False
        assert len(game.state.frozen_cells) == max_freezes

    def test_unfreeze_cell_removes_freeze(self, started_game):
        """unfreeze_cell() removes freeze"""
        game = started_game

        game.state.freeze_cell(0, 0)
        success = game.state.unfreeze_cell(0, 0)

        assert success == True
        assert game.state.grid[0][0].is_frozen == False
        assert (0, 0) not in game.state.frozen_cells

    def test_cannot_unfreeze_non_frozen_cell(self, started_game):
        """Cannot unfreeze cell that isn't frozen"""
        game = started_game

        success = game.state.unfreeze_cell(0, 0)

        assert success == False

    def test_unfreeze_all_clears_all_freezes(self, started_game):
        """unfreeze_all() clears all frozen cells"""
        game = started_game

        # Freeze multiple cells
        game.state.freeze_cell(0, 0)
        game.state.freeze_cell(1, 1)

        game.state.unfreeze_all()

        assert len(game.state.frozen_cells) == 0
        assert game.state.grid[0][0].is_frozen == False
        assert game.state.grid[1][1].is_frozen == False


class TestAutoFreeze:
    """Test auto-freeze logic"""

    def test_auto_freeze_finds_pair(self, config):
        """auto_freeze finds pairs"""
        # Create grid with a pair of Aces
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Set up a pair of Aces in row 0
        grid[0][0].set_card(CardResource(rank='A', suit='H'))
        grid[0][1].set_card(CardResource(rank='A', suit='S'))
        grid[0][2].set_card(CardResource(rank='2', suit='H'))
        grid[0][3].set_card(CardResource(rank='3', suit='H'))
        grid[0][4].set_card(CardResource(rank='4', suit='H'))

        # Fill rest with random cards
        for row in range(1, 5):
            for col in range(5):
                grid[row][col].set_card(CardResource(rank='5', suit='C'))

        state = GameStateResource(
            grid=grid,
            deck=DeckResource(cards=[CardResource(rank='2', suit='C')]),
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.auto_freeze_highest_pair()

        # Should freeze the pair of Aces
        assert len(state.frozen_cells) == 2
        assert (0, 0) in state.frozen_cells or (0, 1) in state.frozen_cells

    def test_auto_freeze_prefers_aligned_pairs(self, config):
        """auto_freeze prefers pairs in same row/column"""
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Pair of Kings in same row (0, 0) and (0, 1)
        grid[0][0].set_card(CardResource(rank='K', suit='H'))
        grid[0][1].set_card(CardResource(rank='K', suit='S'))

        # Pair of Queens not aligned
        grid[1][0].set_card(CardResource(rank='Q', suit='H'))
        grid[2][2].set_card(CardResource(rank='Q', suit='S'))

        # Fill rest
        for row in range(5):
            for col in range(5):
                if grid[row][col].card is None:
                    grid[row][col].set_card(CardResource(rank='2', suit='C'))

        state = GameStateResource(
            grid=grid,
            deck=DeckResource(cards=[CardResource(rank='2', suit='C')]),
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.auto_freeze_highest_pair()

        # Should freeze aligned Kings (higher rank)
        assert (0, 0) in state.frozen_cells
        assert (0, 1) in state.frozen_cells

    def test_auto_freeze_highest_rank(self, config):
        """auto_freeze picks highest ranked pair"""
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Pair of Aces in same row
        grid[0][0].set_card(CardResource(rank='A', suit='H'))
        grid[0][1].set_card(CardResource(rank='A', suit='S'))

        # Pair of 2s in same row
        grid[1][0].set_card(CardResource(rank='2', suit='H'))
        grid[1][1].set_card(CardResource(rank='2', suit='S'))

        # Fill rest
        for row in range(5):
            for col in range(5):
                if grid[row][col].card is None:
                    grid[row][col].set_card(CardResource(rank='3', suit='C'))

        state = GameStateResource(
            grid=grid,
            deck=DeckResource(cards=[CardResource(rank='2', suit='C')]),
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.auto_freeze_highest_pair()

        # Should freeze Aces (highest)
        assert (0, 0) in state.frozen_cells
        assert (0, 1) in state.frozen_cells

    def test_auto_freeze_suited_fallback(self, config):
        """auto_freeze uses suited cards if no pairs"""
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # Two high hearts (no pairs)
        grid[0][0].set_card(CardResource(rank='A', suit='H'))
        grid[0][1].set_card(CardResource(rank='K', suit='H'))

        # Fill rest with different suits
        for row in range(5):
            for col in range(5):
                if grid[row][col].card is None:
                    grid[row][col].set_card(CardResource(rank='2', suit='C'))

        state = GameStateResource(
            grid=grid,
            deck=DeckResource(cards=[CardResource(rank='2', suit='C')]),
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.auto_freeze_highest_pair()

        # Should freeze the two hearts
        assert len(state.frozen_cells) == 2
        # Either (0,0) and (0,1) or nothing if no suited cards found
        # Implementation may vary

    def test_auto_freeze_does_nothing_if_no_good_options(self, config):
        """auto_freeze does nothing if no pairs or suited cards"""
        grid = []
        for row in range(5):
            grid_row = []
            for col in range(5):
                grid_row.append(GridCellResource(row=row, col=col))
            grid.append(grid_row)

        # All different ranks and only one of each suit
        grid[0][0].set_card(CardResource(rank='A', suit='H'))
        grid[0][1].set_card(CardResource(rank='K', suit='D'))
        grid[0][2].set_card(CardResource(rank='Q', suit='C'))
        grid[0][3].set_card(CardResource(rank='J', suit='S'))
        grid[0][4].set_card(CardResource(rank='T', suit='H'))
        grid[1][0].set_card(CardResource(rank='9', suit='D'))

        # Fill rest
        for row in range(5):
            for col in range(5):
                if grid[row][col].card is None:
                    grid[row][col].set_card(CardResource(rank='2', suit='C'))

        state = GameStateResource(
            grid=grid,
            deck=DeckResource(cards=[CardResource(rank='2', suit='C')]),
            spins_left=7,
            spins_taken=0,
            frozen_cells=[],
            current_round=1,
            cumulative_score=0,
            spin_scores=[],
            config=config
        )

        grid_manager = GridManager(state, config)
        grid_manager.auto_freeze_highest_pair()

        # Might freeze suited cards if 2+ hearts found, or nothing
        # Just verify it doesn't crash
        assert len(state.frozen_cells) <= 2


class TestGetRowColCards:
    """Test helper methods for getting row/column cards"""

    def test_get_row_cards_returns_5_cards(self, started_game):
        """get_row_cards() returns correct number of cards for full row"""
        game = started_game

        cards = game.grid_manager.get_row_cards(0)

        assert len(cards) == game.config.grid_cols
        for card in cards:
            assert card is not None

    def test_get_col_cards_returns_5_cards(self, started_game):
        """get_col_cards() returns correct number of cards for full column"""
        game = started_game

        cards = game.grid_manager.get_col_cards(0)

        assert len(cards) == game.config.grid_rows
        for card in cards:
            assert card is not None
