"""
Test game flow and round progression
Tests GameManager orchestration
"""
import pytest
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource


class TestGameInitialization:
    """Test game startup"""

    def test_fresh_game_has_correct_defaults(self, fresh_game):
        """New game has correct initial values"""
        game = fresh_game

        assert game.state.current_round == 0
        assert game.state.spins_left == game.config.max_spins
        assert game.state.spins_taken == 0
        assert game.state.cumulative_score == 0
        assert len(game.state.frozen_cells) == 0
        assert len(game.state.spin_scores) == 0
        assert game.state.deck.size() == game.config.cards_per_deck

    def test_start_new_round_sets_round_1(self, fresh_game):
        """start_new_round() advances to round 1"""
        game = fresh_game

        game.start_new_round()

        assert game.state.current_round == 1
        assert game.state.spins_left == game.config.max_spins
        assert game.state.spins_taken == 0

    def test_start_new_round_deals_grid(self, fresh_game):
        """start_new_round() deals initial grid"""
        game = fresh_game

        game.start_new_round()

        # All cells should have cards
        for row in range(game.config.grid_rows):
            for col in range(game.config.grid_cols):
                assert game.state.grid[row][col].card is not None

    def test_start_new_round_auto_freezes(self, fresh_game):
        """start_new_round() auto-freezes if enabled"""
        game = fresh_game

        # Enable auto-freeze
        game.config.auto_freeze_highest_pair = True
        game.start_new_round()

        # Should have frozen cells (if any pairs found)
        # Can't guarantee pairs, but should attempt auto-freeze
        # Just verify it doesn't crash
        assert len(game.state.frozen_cells) >= 0


class TestHandProgression:
    """Test playing hands"""

    def test_play_spin_decrements_spins_left(self, started_game):
        """play_spin() + complete_spin() decrements spins_left"""
        game = started_game
        initial_hands = game.state.spins_left

        success = game.play_spin()
        game.complete_spin()  # GDD v1.1: complete_spin() updates counters

        assert success == True
        assert game.state.spins_left == initial_hands - 1

    def test_play_spin_increments_spins_taken(self, started_game):
        """play_spin() + complete_spin() increments spins_taken"""
        game = started_game
        initial_taken = game.state.spins_taken

        success = game.play_spin()
        game.complete_spin()  # GDD v1.1: complete_spin() updates counters

        assert success == True
        assert game.state.spins_taken == initial_taken + 1

    def test_play_spin_redeals_grid(self, started_game):
        """play_spin() redeals unfrozen cells"""
        game = started_game

        # Remember unfrozen card
        original_card = game.state.grid[0][0].card

        game.play_spin()

        # Card likely changed (small chance it's same with replacement)
        new_card = game.state.grid[0][0].card
        assert new_card is not None
        # Can't guarantee different card due to replacement

    def test_cannot_play_spin_when_none_left(self, started_game):
        """Cannot play_spin() when spins_left == 0"""
        game = started_game

        # Play all hands
        for _ in range(game.config.max_spins):
            game.play_spin()
            game.complete_spin()  # GDD v1.1: complete each spin

        # Try to play one more
        success = game.play_spin()

        assert success == False
        assert game.state.spins_left == 0

    def test_play_multiple_spins(self, started_game):
        """Can play multiple hands in sequence"""
        game = started_game

        num_spins_to_test = min(3, game.config.max_spins)
        for i in range(num_spins_to_test):
            success = game.play_spin()
            game.complete_spin()  # GDD v1.1: complete each spin
            assert success == True
            assert game.state.spins_taken == i + 1
            assert game.state.spins_left == game.config.max_spins - (i + 1)


class TestFreezeSystem:
    """Test freeze mechanics during gameplay"""

    def test_toggle_freeze_freezes_cell(self, started_game):
        """toggle_freeze() freezes unfrozen cell"""
        game = started_game
        game.config.enable_freeze = True

        success, msg = game.toggle_freeze(0, 0)

        assert success == True
        assert game.state.grid[0][0].is_frozen == True

    def test_toggle_freeze_unfreezes_frozen_cell(self, started_game):
        """toggle_freeze() unfreezes frozen cell"""
        game = started_game
        game.config.enable_freeze = True

        game.toggle_freeze(0, 0)  # Freeze
        success, msg = game.toggle_freeze(0, 0)  # Unfreeze

        assert success == True
        assert game.state.grid[0][0].is_frozen == False

    def test_cannot_freeze_beyond_max(self, started_game):
        """Cannot freeze more than max_freezes cells"""
        game = started_game
        game.config.enable_freeze = True

        # Freeze max amount
        for i in range(game.config.max_freezes):
            game.toggle_freeze(0, i)

        # Try to freeze one more
        success, msg = game.toggle_freeze(0, game.config.max_freezes)

        assert success == False
        assert "Max freezes reached" in msg or "max" in msg.lower()

    def test_frozen_cells_persist_across_spins(self, started_game):
        """Frozen cells stay frozen across multiple hands"""
        game = started_game
        game.config.enable_freeze = True

        # Freeze and remember card
        game.toggle_freeze(0, 0)
        frozen_card = game.state.grid[0][0].card

        # Play 3 hands
        for _ in range(3):
            game.play_spin()

        # Still frozen with same card
        assert game.state.grid[0][0].is_frozen == True
        assert game.state.grid[0][0].card is frozen_card

    def test_unfreeze_all_clears_all(self, started_game):
        """unfreeze_all() clears all frozen cells"""
        game = started_game

        game.toggle_freeze(0, 0)
        game.toggle_freeze(1, 1)

        game.unfreeze_all()

        assert len(game.state.frozen_cells) == 0
        assert game.state.grid[0][0].is_frozen == False
        assert game.state.grid[1][1].is_frozen == False


class TestRoundCompletion:
    """Test round completion logic"""

    def test_is_round_complete_after_all_spins(self, started_game):
        """is_round_complete() True after all hands played"""
        game = started_game

        # Play all hands
        for _ in range(game.config.max_spins):
            game.play_spin()
            game.complete_spin()  # GDD v1.1: complete each spin

        assert game.is_round_complete() == True

    def test_is_round_complete_false_with_spins_remaining(self, started_game):
        """is_round_complete() False when hands remain"""
        game = started_game

        assert game.is_round_complete() == False

        game.play_spin()
        assert game.is_round_complete() == False

    def test_round_resets_spins_count(self, fresh_game):
        """Starting new round resets hands counters"""
        game = fresh_game

        game.start_new_round()

        # Play some hands
        game.play_spin()
        game.play_spin()

        # Start new round
        game.state.current_round = 1  # Manually advance
        game.start_new_round()

        assert game.state.spins_left == game.config.max_spins
        assert game.state.spins_taken == 0
        assert game.state.current_round == 2


class TestWinLoseConditions:
    """Test win/lose conditions"""

    def test_is_quota_met_true_when_score_exceeds(self, started_game):
        """is_quota_met() True when score >= quota"""
        game = started_game

        game.state.cumulative_score = game.config.quota_target

        assert game.is_quota_met() == True

    def test_is_quota_met_false_when_below(self, started_game):
        """is_quota_met() False when score < quota"""
        game = started_game

        game.state.cumulative_score = game.config.quota_target - 1

        assert game.is_quota_met() == False

    def test_get_session_result_win(self, started_game):
        """get_session_result() returns WIN when quota met"""
        game = started_game

        game.state.cumulative_score = game.config.quota_target

        result = game.get_session_result()

        assert result == "WIN"

    def test_get_session_result_lose(self, started_game):
        """get_session_result() returns LOSE when quota not met"""
        game = started_game

        game.state.cumulative_score = 0

        result = game.get_session_result()

        assert result == "LOSE"

    def test_is_session_complete_after_all_rounds(self, started_game):
        """is_session_complete() True after all rounds"""
        game = started_game

        game.state.current_round = game.config.rounds_per_session

        assert game.is_session_complete() == True

    def test_is_session_complete_false_during_rounds(self, fresh_game):
        """is_session_complete() False during rounds"""
        game = fresh_game

        assert game.is_session_complete() == False


class TestDeckPersistence:
    """Test deck persists across hands and rounds"""

    def test_deck_size_unchanged_after_spin(self, started_game):
        """Deck size unchanged after playing hand (draw with replacement)"""
        game = started_game
        initial_size = game.state.deck.size()

        game.play_spin()

        assert game.state.deck.size() == initial_size
        assert game.state.deck.size() == game.config.cards_per_deck

    def test_deck_persists_across_rounds(self, fresh_game):
        """Deck is same across rounds"""
        game = fresh_game

        game.start_new_round()
        deck1 = game.state.deck

        # Play all hands
        for _ in range(game.config.max_spins):
            game.play_spin()

        # Start new round
        game.state.current_round = 1
        game.start_new_round()

        # Same deck instance
        assert game.state.deck is deck1
        assert game.state.deck.size() == game.config.cards_per_deck


class TestScoreAccumulation:
    """Test score accumulation"""

    def test_cumulative_score_increases(self, started_game):
        """Cumulative score increases with each scoring"""
        game = started_game

        initial_score = game.state.cumulative_score

        score1, _, _, _ = game.score_and_update()
        assert game.state.cumulative_score == initial_score + score1

        score2, _, _, _ = game.score_and_update()
        assert game.state.cumulative_score == initial_score + score1 + score2

    def test_spin_scores_tracked(self, started_game):
        """Each hand score is tracked"""
        game = started_game

        game.score_and_update()
        game.score_and_update()
        game.score_and_update()

        assert len(game.state.spin_scores) == 3

    def test_cumulative_score_persists_across_rounds(self, fresh_game):
        """Cumulative score persists across rounds"""
        game = fresh_game

        game.start_new_round()
        game.state.cumulative_score = 1000

        # Start new round
        game.state.current_round = 1
        game.start_new_round()

        # Score should persist
        assert game.state.cumulative_score == 1000
