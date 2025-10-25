"""
Test reroll system (GDD v1.1)
Tests RerollManager and column reroll mechanics
"""
import pytest
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource


class TestRerollInitialization:
    """Test reroll system startup"""

    def test_fresh_game_has_correct_reroll_tokens(self, fresh_game):
        """New game has correct reroll token count from config"""
        game = fresh_game
        game.start_new_round()

        assert game.state.reroll_tokens_left == game.config.reroll_tokens_per_quota
        assert game.state.spins_taken == 0

    def test_reroll_tokens_reset_each_round(self, fresh_game):
        """Reroll tokens reset each round (no carryover)"""
        game = fresh_game

        # Round 1
        game.start_new_round()
        initial_tokens = game.config.reroll_tokens_per_quota
        game.state.reroll_tokens_left = initial_tokens // 2  # Spend some tokens
        game.state.spins_taken = 3

        # Round 2
        game.start_new_round()

        # Tokens should reset to config value
        assert game.state.reroll_tokens_left == game.config.reroll_tokens_per_quota
        assert game.state.spins_taken == 0


class TestColumnReroll:
    """Test column reroll mechanics"""

    def test_can_reroll_single_column(self, started_game):
        """Player can reroll a single column"""
        game = started_game
        initial_tokens = game.state.reroll_tokens_left

        # Save original cards from column 0
        original_cards = [game.state.grid[row][0].card for row in range(game.config.grid_rows)]

        # Reroll column 0
        success, message = game.reroll_columns([0])

        assert success is True
        assert "Rerolled 1 column(s) for 1 token(s)" in message
        assert game.state.reroll_tokens_left == initial_tokens - 1

        # Cards should be different (with very high probability)
        new_cards = [game.state.grid[row][0].card for row in range(game.config.grid_rows)]
        # At least one card should be different
        assert any(orig != new for orig, new in zip(original_cards, new_cards))

    def test_can_reroll_multiple_columns(self, started_game):
        """Player can reroll multiple columns at once"""
        game = started_game
        initial_tokens = game.state.reroll_tokens_left

        # Reroll columns 0, 2, 4
        success, message = game.reroll_columns([0, 2, 4])

        assert success is True
        assert "Rerolled 3 column(s) for 3 token(s)" in message
        assert game.state.reroll_tokens_left == initial_tokens - 3

    def test_cannot_reroll_with_insufficient_tokens(self, started_game):
        """Player cannot reroll if they don't have enough tokens"""
        game = started_game

        # Spend most tokens
        game.state.reroll_tokens_left = 2

        # Try to reroll 3 columns (costs 3 tokens)
        success, message = game.reroll_columns([0, 1, 2])

        assert success is False
        assert "Not enough tokens" in message
        assert game.state.reroll_tokens_left == 2  # No change

    def test_cannot_reroll_invalid_column(self, started_game):
        """Player cannot reroll invalid column indices"""
        game = started_game
        initial_tokens = game.state.reroll_tokens_left

        # Try to reroll column beyond grid size
        invalid_column = game.config.grid_cols
        success, message = game.reroll_columns([invalid_column])

        assert success is False
        assert "Invalid column index" in message
        assert game.state.reroll_tokens_left == initial_tokens  # No tokens spent

    def test_reroll_respects_frozen_cells(self, started_game):
        """Reroll should not affect frozen cells"""
        game = started_game

        # Enable freeze system for this test
        game.config.enable_freeze = True
        game.config.max_freezes = 5

        # Freeze a cell in column 0
        game.state.freeze_cell(0, 0)
        frozen_card = game.state.grid[0][0].card

        # Reroll column 0
        game.reroll_columns([0])

        # Frozen cell should have same card
        assert game.state.grid[0][0].card == frozen_card
        assert game.state.grid[0][0].is_frozen is True


class TestSpinTracking:
    """Test spin tracking"""

    def test_complete_spin_increments_counter(self, started_game):
        """complete_spin() increments spin counter"""
        game = started_game

        assert game.state.spins_taken == 0

        game.complete_spin()
        assert game.state.spins_taken == 1

        game.complete_spin()
        assert game.state.spins_taken == 2

    def test_is_spins_complete_checks_quota(self, started_game):
        """is_spins_complete() checks if all spins used"""
        game = started_game

        game.state.spins_taken = game.config.spins_per_quota - 1
        assert game.is_spins_complete() is False

        game.state.spins_taken = game.config.spins_per_quota
        assert game.is_spins_complete() is True

        game.state.spins_taken = game.config.spins_per_quota + 1
        assert game.is_spins_complete() is True


class TestRerollCost:
    """Test reroll cost calculations"""

    def test_reroll_cost_scales_with_columns(self, started_game):
        """Reroll cost is 1 token per column"""
        game = started_game

        # Test with different column counts
        assert game.reroll_manager.get_reroll_cost(1) == 1
        assert game.reroll_manager.get_reroll_cost(3) == 3
        assert game.reroll_manager.get_reroll_cost(5) == 5

    def test_can_reroll_checks_affordability(self, started_game):
        """can_reroll checks if player can afford the cost"""
        game = started_game

        # Player has full tokens - can afford multiple columns
        can_reroll, msg = game.reroll_manager.can_reroll_columns([0, 1, 2])
        assert can_reroll is True

        # Spend down to 2 tokens
        game.state.reroll_tokens_left = 2

        # Can afford 2 columns
        can_reroll, msg = game.reroll_manager.can_reroll_columns([0, 1])
        assert can_reroll is True

        # Cannot afford 3 columns
        can_reroll, msg = game.reroll_manager.can_reroll_columns([0, 1, 2])
        assert can_reroll is False


class TestDeckConfiguration:
    """Test GDD v1.1 deck changes"""

    def test_deck_has_full_52_cards(self, fresh_game):
        """Deck contains full standard 52-card deck (ranks 2-A)"""
        game = fresh_game

        # Check config constants - should have all 13 ranks
        expected_ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
        assert GameConfigResource.RANKS == expected_ranks
        assert len(GameConfigResource.RANKS) == 13

        # Check deck size: 13 ranks × 4 suits = 52 cards
        game.start_new_round()
        # Note: With draw-with-replacement, deck size stays at 52
        # But we can check that drawn cards use the full rank set
        all_ranks_seen = set()
        for row in range(5):
            for col in range(5):
                card = game.state.grid[row][col].card
                assert card.rank in expected_ranks
                all_ranks_seen.add(card.rank)

        # With 25 cards drawn, we should see multiple ranks (not all 13, but  > 1)
        assert len(all_ranks_seen) > 1, "Should see variety of ranks in 25 cards"
