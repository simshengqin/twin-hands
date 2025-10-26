"""
GDD Compliance Tests for Section 4-4: Trading System.

Verifies game behavior matches GDD specification for trading.
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig


class TestGDD_4_4_TradingSystem:
    """Test GDD 4-4: Trading System compliance."""

    @pytest.fixture
    def setup(self):
        """Create game manager for testing."""
        config = TwinHandsConfig()
        game = GameManager(config)
        game.start_game()
        return game

    def test_can_trade_1_card(self, setup):
        """GDD 4-4: Can trade 1 card (minimum)."""
        game = setup

        result = game.trade_cards(source_deck=0, card_indices=[0])

        assert result["success"] == True

    def test_can_trade_2_cards(self, setup):
        """GDD 4-4: Can trade 2 cards."""
        game = setup

        result = game.trade_cards(source_deck=0, card_indices=[0, 1])

        assert result["success"] == True

    def test_can_trade_3_cards(self, setup):
        """GDD 4-4: Can trade 3 cards."""
        game = setup

        result = game.trade_cards(source_deck=0, card_indices=[0, 1, 2])

        assert result["success"] == True

    def test_can_trade_4_cards(self, setup):
        """GDD 4-4: Can trade 4 cards (maximum)."""
        game = setup

        result = game.trade_cards(source_deck=0, card_indices=[0, 1, 2, 3])

        assert result["success"] == True

    def test_giving_deck_draws_replacements(self, setup):
        """GDD 4-4: Giving deck immediately draws replacement cards."""
        game = setup

        deck_0_before = len(game.state.decks[0].visible_cards)

        game.trade_cards(source_deck=0, card_indices=[0, 1])

        deck_0_after = len(game.state.decks[0].visible_cards)

        assert deck_0_after == deck_0_before, "Giving deck should stay at same card count"

    def test_receiving_deck_accumulates_cards(self, setup):
        """GDD 4-4: Receiving deck accumulates cards (up to 8 max)."""
        game = setup

        deck_1_before = len(game.state.decks[1].visible_cards)

        game.trade_cards(source_deck=0, card_indices=[0, 1])

        deck_1_after = len(game.state.decks[1].visible_cards)

        assert deck_1_after == deck_1_before + 2, "Receiving deck should gain 2 cards"

    def test_max_8_visible_cards_per_deck(self, setup):
        """GDD 4-4: Maximum 8 visible cards per deck."""
        game = setup

        # Trade 4 cards to Deck 1
        game.trade_cards(source_deck=0, card_indices=[0, 1, 2, 3])

        # Deck 1 should now have 8 cards (4 + 4)
        assert len(game.state.decks[1].visible_cards) == 8

        # Cannot trade more (would exceed 8)
        result = game.trade_cards(source_deck=0, card_indices=[0])

        assert result["success"] == False
        assert "8 cards" in result["error"].lower()

    # Future tests (from GDD 4-4):
    # - test_trade_is_one_directional
    # - test_traded_cards_return_at_round_end
