import types

from src.managers.score_manager import ScoreManager
from src.resources.game_state_resource import GameStateResource
from src.resources.grid_cell_resource import GridCellResource
from src.resources.card_resource import CardResource
from src.resources.game_config_resource import GameConfigResource


def test_scoremanager_sums_only_top_k(monkeypatch):
    # Build a full 5x5 grid with arbitrary identical cards
    config = GameConfigResource()
    config.lines_scored_per_hand = 3
    rows, cols = config.grid_rows, config.grid_cols

    grid = [[GridCellResource(row=r, col=c) for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            grid[r][c].set_card(CardResource("A", "H"))

    state = GameStateResource(grid=grid, config=config)

    # Patch PokerEvaluator to yield deterministic line scores in row-major then col order
    # Sequence 10 values (rows 5 then cols 5)
    sequence = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10]

    class FakeHand:
        def __init__(self, chips, mult):
            self.cards = []
            self.hand_type = "Test"
            self.chips = chips
            self.mult = mult

    call_index = {"i": 0}

    def fake_evaluate_hand(cards):
        i = call_index["i"]
        call_index["i"] = i + 1
        return FakeHand(chips=sequence[i], mult=1)

    import src.utils.poker_evaluator as pe
    monkeypatch.setattr(pe.PokerEvaluator, "evaluate_hand", staticmethod(fake_evaluate_hand))

    sm = ScoreManager(state, config, joker_manager=None)
    total, row_hands, col_hands, top_lines = sm.score_current_grid()

    assert total == sum(sequence[:3])  # 100 + 90 + 80
    assert len(top_lines) == 3

