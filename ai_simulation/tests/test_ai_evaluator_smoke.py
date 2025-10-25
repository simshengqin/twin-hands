from ai_simulation import AIEvaluator
from src.resources.card_resource import CardResource
from src.resources.game_config_resource import GameConfigResource


def test_ai_evaluator_smoke_runs():
    config = GameConfigResource()
    rows, cols = config.grid_rows, config.grid_cols

    # Simple grid: fill with random duplicates for a deterministic shape
    # We only care that the function runs and returns a float.
    card = CardResource("A", "H")
    grid_cards = [[card for _ in range(cols)] for _ in range(rows)]
    frozen = [(0, 0), (0, 1)]

    ev = AIEvaluator.estimate_expected_score(
        grid_cards=grid_cards,
        frozen_cells=frozen,
        config=config,
        active_jokers=[],
        samples=5,
    )
    assert isinstance(ev, float)
    assert ev >= 0.0

