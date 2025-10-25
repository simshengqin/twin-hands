"""
Test GameConfigResource
Tests configuration and constants
"""
import pytest
from src.resources.game_config_resource import GameConfigResource


class TestConfigDefaults:
    """Test configuration can be created and has valid values"""

    def test_config_creation(self, config):
        """Config can be created"""
        assert config is not None
        assert isinstance(config, GameConfigResource)


class TestCardConstants:
    """Test card-related constants"""

    def test_suits_count(self, config):
        """4 suits in deck"""
        assert len(config.SUITS) == 4
        assert set(config.SUITS) == {'H', 'D', 'C', 'S'}

    def test_ranks_count(self, config):
        """13 ranks in deck"""
        assert len(config.RANKS) == 13
        expected_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        assert config.RANKS == expected_ranks

    def test_rank_values_correct(self, config):
        """Rank values are correct"""
        assert config.RANK_VALUES['2'] == 2
        assert config.RANK_VALUES['9'] == 9
        assert config.RANK_VALUES['T'] == 10
        assert config.RANK_VALUES['J'] == 11
        assert config.RANK_VALUES['Q'] == 12
        assert config.RANK_VALUES['K'] == 13
        assert config.RANK_VALUES['A'] == 14

    def test_rank_values_ascending(self, config):
        """Rank values are in ascending order"""
        values = [config.RANK_VALUES[rank] for rank in config.RANKS]
        assert values == sorted(values)

    def test_ace_is_highest(self, config):
        """Ace has highest value"""
        assert config.RANK_VALUES['A'] == 14
        assert config.RANK_VALUES['A'] > config.RANK_VALUES['K']


class TestHandScores:
    """Test poker hand score constants"""

    def test_all_hand_types_defined(self, config):
        """All 11 poker hands have scores (including Five of a Kind)"""
        expected_hands = [
            "Five of a Kind",
            "Royal Flush",
            "Straight Flush",
            "Four of a Kind",
            "Full House",
            "Flush",
            "Straight",
            "Three of a Kind",
            "Two Pair",
            "One Pair",
            "High Card"
        ]

        for hand in expected_hands:
            assert hand in config.HAND_SCORES

    def test_hand_scores_structure(self, config):
        """All hand scores are flat chip values (integers)"""
        for hand_type, chips in config.HAND_SCORES.items():
            assert isinstance(chips, int), f"{hand_type} score should be int, got {type(chips)}"
            assert chips > 0, f"{hand_type} chips should be positive, got {chips}"

    def test_hand_scores_descending(self, config):
        """Hand scores are in descending order of rarity (flat chips)"""
        scores = config.HAND_SCORES

        # Verify correct poker hand ranking order
        assert scores["Five of a Kind"] > scores["Royal Flush"]
        assert scores["Royal Flush"] > scores["Straight Flush"]
        assert scores["Straight Flush"] > scores["Four of a Kind"]
        assert scores["Four of a Kind"] > scores["Full House"]
        assert scores["Full House"] > scores["Flush"]
        assert scores["Flush"] > scores["Straight"]
        assert scores["Straight"] > scores["Three of a Kind"]
        assert scores["Three of a Kind"] > scores["Two Pair"]
        assert scores["Two Pair"] > scores["One Pair"]
        assert scores["One Pair"] > scores["High Card"]

    def test_high_card_lowest_score(self, config):
        """High Card has lowest chip value"""
        scores = config.HAND_SCORES
        high_card_score = scores["High Card"]

        for hand_type, chips in scores.items():
            if hand_type != "High Card":
                assert high_card_score <= chips, f"High Card ({high_card_score}) should be <= {hand_type} ({chips})"

    def test_five_of_a_kind_worth_most(self, config):
        """Five of a Kind is worth most chips (rarest hand)"""
        scores = config.HAND_SCORES
        five_kind_score = scores["Five of a Kind"]

        for hand_type, chips in scores.items():
            if hand_type != "Five of a Kind":
                assert five_kind_score > chips, f"Five of a Kind ({five_kind_score}) should be > {hand_type} ({chips})"


class TestConfigModification:
    """Test config can be modified"""

    def test_can_change_max_spins(self):
        """Can modify max_spins"""
        config = GameConfigResource()

        config.max_spins = 10

        assert config.max_spins == 10

    def test_can_change_quota(self):
        """Can modify quota_target"""
        config = GameConfigResource()

        config.quota_target = 10000

        assert config.quota_target == 10000

    def test_can_disable_auto_freeze(self):
        """Can disable auto_freeze"""
        config = GameConfigResource()

        config.auto_freeze_highest_pair = False

        assert config.auto_freeze_highest_pair == False

    def test_config_duplicate_creates_copy(self):
        """duplicate() creates independent copy"""
        config = GameConfigResource()
        config.max_spins = 10

        config_copy = config.duplicate()

        assert config_copy is not config
        assert config_copy.max_spins == 10

        # Modifying copy doesn't affect original
        config_copy.max_spins = 5
        assert config.max_spins == 10


class TestConfigValidation:
    """Test config values make sense"""

    def test_grid_size_positive(self, config):
        """Grid size is positive"""
        assert config.grid_rows > 0
        assert config.grid_cols > 0

    def test_max_spins_positive(self, config):
        """max_spins is positive"""
        assert config.max_spins > 0

    def test_max_freezes_non_negative(self, config):
        """max_freezes is non-negative"""
        assert config.max_freezes >= 0

    def test_quota_target_positive(self, config):
        """quota_target is positive"""
        assert config.quota_target > 0

    def test_rounds_per_session_positive(self, config):
        """rounds_per_session is positive"""
        assert config.rounds_per_session > 0

    def test_max_freezes_less_than_grid_size(self, config):
        """max_freezes doesn't exceed grid size"""
        assert config.max_freezes <= (config.grid_rows * config.grid_cols)
