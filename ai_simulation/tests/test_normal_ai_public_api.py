import types
import builtins

import pytest

from ai_simulation import NormalAIManager
from src.resources.card_resource import CardResource
from src.resources.grid_cell_resource import GridCellResource
from src.resources.joker_resource import JokerResource


class GuardedState:
    """
    Minimal state surface that NormalAI is allowed to read.
    Any access outside allowed_attrs raises AttributeError.
    """

    __slots__ = ("grid", "_money")

    def __init__(self, grid, money: int):
        object.__setattr__(self, "grid", grid)
        object.__setattr__(self, "_money", money)

    # Public API that NormalAI uses
    def can_afford(self, amount: int) -> bool:
        return self._money >= amount

    # Guard unexpected attribute access
    def __getattr__(self, name):
        raise AttributeError(f"NormalAI must not access state.{name}")


class GuardedConfig:
    __slots__ = ("grid_rows", "grid_cols", "RANK_VALUES")

    def __init__(self, rows=5, cols=5):
        object.__setattr__(self, "grid_rows", rows)
        object.__setattr__(self, "grid_cols", cols)
        object.__setattr__(self, "RANK_VALUES", {
            "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
            "T": 10, "J": 11, "Q": 12, "K": 13, "A": 14
        })

    def __getattr__(self, name):
        raise AttributeError(f"NormalAI must not access config.{name}")


class FakeJokerManager:
    def __init__(self, has_slot=True):
        self._has_slot = has_slot

    def has_empty_slot(self) -> bool:
        return self._has_slot


def make_grid_with_aligned_pair(rows=5, cols=5):
    grid = [[GridCellResource(row=r, col=c) for c in range(cols)] for r in range(rows)]
    # Place pair of Aces aligned in row 0, col 0 and col 2
    grid[0][0].set_card(CardResource("A", "H"))
    grid[0][2].set_card(CardResource("A", "D"))
    # Fill a few other random cards
    grid[1][1].set_card(CardResource("K", "S"))
    grid[2][3].set_card(CardResource("7", "C"))
    return grid


def test_normal_ai_recommends_aligned_pair_freeze():
    config = GuardedConfig()
    grid = make_grid_with_aligned_pair(config.grid_rows, config.grid_cols)
    state = GuardedState(grid, money=0)
    ai = NormalAIManager(state, config, joker_manager=None)

    picks = ai.recommend_freezes(max_to_freeze=2)
    assert set(picks) == {(0, 0), (0, 2)}


def test_normal_ai_shop_suggests_simple_buy_first_affordable():
    config = GuardedConfig()
    grid = make_grid_with_aligned_pair(config.grid_rows, config.grid_cols)
    state = GuardedState(grid, money=10)
    jm = FakeJokerManager(has_slot=True)
    ai = NormalAIManager(state, config, joker_manager=jm)

    j1 = JokerResource(
        id="j_plus_m",
        name="Hat",
        rarity="Common",
        cost=4,
        effect_type="instant",
        trigger="always",
        condition_type="",
        condition_value="",
        bonus_type="+m",
        bonus_value=2,
        per_card=False,
    )

    shop_display = [
        {"index": 0, "joker": j1, "name": j1.get_display_name(), "description": j1.get_description(), "cost": j1.cost, "rarity": j1.rarity},
        {"index": 1, "joker": None, "name": "[EMPTY]", "description": "No joker", "cost": 0, "rarity": ""},
        {"index": 2, "joker": None, "name": "[EMPTY]", "description": "No joker", "cost": 0, "rarity": ""},
    ]

    action = ai.recommend_shop_action(shop_display, reroll_cost=5)
    assert action == ("buy", 0)


def test_normal_ai_no_hidden_access(monkeypatch):
    """
    Ensure NormalAI does not touch attributes outside the guarded surface.
    Accessing any other attribute should raise AttributeError (caught by test if it happens).
    """
    config = GuardedConfig()
    grid = make_grid_with_aligned_pair(config.grid_rows, config.grid_cols)
    state = GuardedState(grid, money=0)
    ai = NormalAIManager(state, config, joker_manager=None)

    # If NormalAI tries to access, e.g., state.deck or config.max_hands, it would raise here.
    picks = ai.recommend_freezes()
    assert isinstance(picks, list)
