"""
GDD Compliance Tests for Section 4-4: Trading System (GDD v6.1).

Verifies game behavior matches GDD v6.1 specification for trading:
- One-directional trading (give 1 card from X to Y)
- Giving deck redraws 1 card (stays at 7 baseline)
- Receiving deck accumulates cards (can grow to 8, 9+ visible)
- 2 trade tokens per round
"""

import pytest
from src.managers.game_manager import GameManager
from src.resources.twin_hands_config_resource import TwinHandsConfig


class TestGDD_4_4_TradingSystem:
    """Test GDD v6.1 4-4: Trading System compliance."""

    @pytest.fixture
    def setup(self):
        """Create game manager for testing."""
        config = TwinHandsConfig(
            trade_tokens_per_round=2,
            visible_cards_per_deck=7
        )
        game = GameManager(config)
        game.start_game()
        return game

    def test_can_trade_1_card(self, setup):
        """GDD v6.1 4-4: Can trade 1 card one-directionally."""
        game = setup

        result = game.trade_card(source_deck=0, target_deck=1, card_index=0)

        assert result["success"] == True

    def test_can_trade_2_times_with_2_tokens(self, setup):
        """GDD v6.1 4-4: Can trade twice (2 trade tokens)."""
        game = setup

        result1 = game.trade_card(source_deck=0, target_deck=1, card_index=0)
        result2 = game.trade_card(source_deck=0, target_deck=1, card_index=0)

        assert result1["success"] == True
        assert result2["success"] == True
        assert game.state.trade_tokens == 0  # Both tokens spent

    def test_cannot_trade_without_tokens(self, setup):
        """GDD v6.1 4-4: Cannot trade if no tokens left."""
        game = setup

        # Spend both trade tokens
        game.trade_card(source_deck=0, target_deck=1, card_index=0)
        game.trade_card(source_deck=0, target_deck=1, card_index=0)

        # 3rd attempt should fail
        result = game.trade_card(source_deck=0, target_deck=1, card_index=0)

        assert result["success"] == False
        assert "trade token" in result["error"].lower()

    def test_giving_deck_draws_replacements(self, setup):
        """GDD v6.1 4-4: Giving deck redraws 1 card (stays at 7 baseline)."""
        game = setup

        deck_0_before = len(game.state.decks[0].visible_cards)

        game.trade_card(source_deck=0, target_deck=1, card_index=0)

        deck_0_after = len(game.state.decks[0].visible_cards)

        assert deck_0_after == deck_0_before, "Giving deck should stay at same card count"

    def test_receiving_deck_accumulates_cards(self, setup):
        """GDD v6.1 4-4: Receiving deck accumulates cards (can grow beyond 7)."""
        game = setup

        deck_1_before = len(game.state.decks[1].visible_cards)  # Should be 7

        game.trade_card(source_deck=0, target_deck=1, card_index=0)

        deck_1_after = len(game.state.decks[1].visible_cards)

        assert deck_1_after == deck_1_before + 1, "Receiving deck should gain 1 card"

    def test_can_stack_beyond_8_cards(self, setup):
        """GDD v6.1 4-4: Can stack to 8, 9+ visible cards."""
        game = setup

        # Trade 1 card to deck 1 (7 → 8 cards)
        game.trade_card(source_deck=0, target_deck=1, card_index=0)
        assert len(game.state.decks[1].visible_cards) == 8

        # Trade another card to deck 1 (8 → 9 cards, allowed!)
        game.trade_card(source_deck=0, target_deck=1, card_index=0)
        assert len(game.state.decks[1].visible_cards) == 9

    def test_trade_is_one_directional(self, setup):
        """GDD v6.1 4-4: Trading is one-directional (specify source and target)."""
        game = setup

        initial_deck_0 = len(game.state.decks[0].visible_cards)
        initial_deck_1 = len(game.state.decks[1].visible_cards)

        # Trade from deck 0 to deck 1
        game.trade_card(source_deck=0, target_deck=1, card_index=0)

        # Deck 0: stays at same count (redrew)
        assert len(game.state.decks[0].visible_cards) == initial_deck_0
        # Deck 1: gained 1 card
        assert len(game.state.decks[1].visible_cards) == initial_deck_1 + 1

    def test_can_trade_bidirectionally_with_separate_calls(self, setup):
        """GDD v6.1 4-4: Player can choose direction each trade."""
        game = setup

        # Trade deck 0 → deck 1
        game.trade_card(source_deck=0, target_deck=1, card_index=0)
        assert len(game.state.decks[1].visible_cards) == 8

        # Trade deck 1 → deck 0
        game.trade_card(source_deck=1, target_deck=0, card_index=0)
        assert len(game.state.decks[0].visible_cards) == 8

    # Future tests (from GDD 4-4):
    # - test_traded_cards_return_at_round_end (not yet implemented)
