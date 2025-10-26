"""
Tests for TwinHandsConfig resource.
Verifies config values match GDD specifications.
"""
from src.resources.twin_hands_config_resource import TwinHandsConfig


def test_config_defaults_match_gdd():
    """Test config defaults match GDD specifications"""
    config = TwinHandsConfig()

    # GDD 5-2: max 8 rounds
    assert config.max_rounds == 8

    # GDD 4-3: 4 hand tokens, 3 trade tokens
    assert config.hand_tokens_per_round == 4
    assert config.trade_tokens_per_round == 3

    # GDD 4-3: max 2 hands per deck
    assert config.max_hands_per_deck == 2

    # GDD 4-4: max 8 visible per deck (4 base + 4 from trades)
    assert config.max_visible_per_deck == 8

    # GDD 5-3: 1.3× quota scaling
    assert config.quota_scaling == 1.3


def test_hand_scores_match_gdd_4_7():
    """Test HAND_SCORES constant matches GDD 4-7"""
    # GDD 4-7: Hand rankings and base scores
    assert TwinHandsConfig.HAND_SCORES["Royal Flush"] == 60
    assert TwinHandsConfig.HAND_SCORES["Straight Flush"] == 50
    assert TwinHandsConfig.HAND_SCORES["Four of a Kind"] == 30
    assert TwinHandsConfig.HAND_SCORES["Flush"] == 20
    assert TwinHandsConfig.HAND_SCORES["Straight"] == 18
    assert TwinHandsConfig.HAND_SCORES["Three of a Kind"] == 15
    assert TwinHandsConfig.HAND_SCORES["Two Pair"] == 10
    assert TwinHandsConfig.HAND_SCORES["Pair"] == 6
    assert TwinHandsConfig.HAND_SCORES["High Card"] == 3


def test_round_quotas_calculated_from_gdd_5_3():
    """Test round quotas match GDD 5-3 progression (1.3× scaling)"""
    config = TwinHandsConfig()

    # GDD 5-3: Round quotas
    assert config.round_quotas[0] == 300    # Round 1
    assert config.round_quotas[1] == 390    # Round 2 (300 × 1.3)
    assert config.round_quotas[2] == 507    # Round 3 (390 × 1.3)
    assert config.round_quotas[3] == 659    # Round 4
    assert config.round_quotas[4] == 857    # Round 5
    assert config.round_quotas[5] == 1114   # Round 6
    assert config.round_quotas[6] == 1448   # Round 7
    assert config.round_quotas[7] == 1882   # Round 8
    assert len(config.round_quotas) == 8


def test_config_is_godot_ready():
    """Test config structure is Godot-ready (lowercase attrs, UPPERCASE constants)"""
    config = TwinHandsConfig()

    # Instance attributes are lowercase (will be @export in Godot)
    assert hasattr(config, 'max_rounds')
    assert hasattr(config, 'hand_tokens_per_round')

    # Class constants are UPPERCASE
    assert hasattr(TwinHandsConfig, 'HAND_SCORES')
    assert isinstance(TwinHandsConfig.HAND_SCORES, dict)
