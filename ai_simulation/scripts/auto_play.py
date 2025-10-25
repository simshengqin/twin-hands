"""
Auto Play Sessions with NormalAI and SmartAI
Run: python ai_simulation/scripts/auto_play.py [--ai normal|smart|both] [--samples N] [--seed S] [--lines K]
"""

import os
import sys
import io
from typing import List, Tuple, Optional
import argparse
import random
from contextlib import redirect_stdout
from pathlib import Path

# Ensure project root on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Ensure UTF-8 output on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

from ai_simulation import NormalAIManager, SmartAIManager
from src.ui_adapter import UIAdapter
from src.ui.terminal_ui import TerminalUI
from src.resources.game_config_resource import GameConfigResource
from src.managers.game_manager import GameManager
from src.managers.joker_manager import JokerManager
from src.managers.shop_manager import ShopManager
from src.utils.joker_loader import JokerLoader


def apply_freezes(game: GameManager, freezes: List[Tuple[int, int]]):
    # Reset and apply exact freeze set
    game.unfreeze_all()
    max_f = min(len(freezes), game.config.max_freezes)
    for i in range(max_f):
        r, c = freezes[i]
        game.toggle_freeze(r, c)


def shop_phase(state, joker_manager: JokerManager, ai, available_jokers, ui: TerminalUI, actions_log: List[str]):
    shop = ShopManager(state, joker_manager, available_jokers)
    shop.open_shop()

    # Print initial shop view
    ui.print_shop_header(money_earned=state.hands_left)
    ui.print_active_jokers(joker_manager)
    ui.print_shop_inventory(shop)
    ui.print_shop_commands(shop.get_reroll_cost())

    # Limit iterations to avoid infinite loops
    for _ in range(10):
        display = shop.get_shop_display()
        action, idx = ai.recommend_shop_action(display, shop.get_reroll_cost())
        if action == 'buy':
            # Capture target name before buy
            item = next((it for it in display if it.get('index') == idx), None)
            jname = item['name'] if item and item.get('name') else f"slot {idx}"
            ok, msg = shop.buy_joker(idx)
            actions_log.append(f"buy:{jname}")
            ui.print_message(("V " if ok else "? ") + msg)
        elif action == 'sell':
            # Capture joker name before sell
            jname = joker_manager.active_jokers[idx].get_display_name() if 0 <= idx < len(joker_manager.active_jokers) else f"idx {idx}"
            ok, msg = shop.sell_joker(idx)
            actions_log.append(f"sell:{jname}")
            ui.print_message(("V " if ok else "? ") + msg)
        elif action == 'reroll':
            ok, msg = shop.reroll_shop()
            actions_log.append("reroll")
            ui.print_message(("V " if ok else "? ") + msg)
        else:
            break

        # Refresh shop view after each action
        ui.print_shop_header()
        ui.print_active_jokers(joker_manager)
        ui.print_shop_inventory(shop)
        ui.print_shop_commands(shop.get_reroll_cost())

    shop.close_shop()


def play_session(ai_kind: str, samples: int = 120, lines_scored: Optional[int] = None, seed: Optional[int] = None) -> List[str]:
    # Collect per-round summaries for console output
    round_summaries: List[str] = []

    config = GameConfigResource()
    if lines_scored is not None:
        config.lines_scored_per_hand = int(lines_scored)
    joker_manager = JokerManager(max_slots=5)
    game = GameManager(config, joker_manager)

    if seed is not None:
        try:
            random.seed(seed)
        except Exception:
            pass

    if ai_kind == 'normal':
        ai = NormalAIManager(game.state, config, joker_manager)
    elif ai_kind == 'smart':
        ai = SmartAIManager(game.state, config, joker_manager)
    else:
        raise ValueError("ai_kind must be 'normal' or 'smart'")

    available_jokers = JokerLoader.load_p0_jokers()

    # UI setup for detailed logs
    adapter = UIAdapter(game)
    ui = TerminalUI(adapter)

    # Capture detailed UI output to a log buffer
    log_buffer = io.StringIO()
    with redirect_stdout(log_buffer):
        print(f"\n=== Starting session with {ai_kind} ===")

        while game.state.current_round < config.rounds_per_session:
            game.start_new_round()

            # Round header and initial grid
            ui.print_round_header()
            ui.print_grid()

            # Hands within the round
            while game.state.hands_left > 0:
                # Decide freezes on current grid before redeal
                if ai_kind == 'smart':
                    freezes = ai.recommend_freezes(max_to_freeze=config.max_freezes, samples=samples)
                else:
                    freezes = ai.recommend_freezes(max_to_freeze=config.max_freezes)
                apply_freezes(game, freezes)

                if freezes:
                    ui.print_message(f"AI froze: {', '.join(str(t) for t in freezes)}")
                else:
                    ui.print_message("AI froze: none")
                ui.print_grid()

                if not game.play_hand():
                    break

                current_score, row_hands, col_hands, top_lines = game.score_and_update()

                ui.print_message(f"\n=== HAND {game.state.hands_taken}/{config.max_hands} COMPLETE ===")
                # Show results grid with highlights
                ui.print_grid(top_lines)
                # Show per-line breakdown
                ui.print_line_scores(row_hands, col_hands, current_score, top_lines)
                # Cumulative status
                print(f"Cumulative Score: {game.state.cumulative_score} chips")
                print(f"Hands Remaining: {game.state.hands_left}/{config.max_hands}")

                # Early stop if round quota met
                round_idx = game.state.current_round - 1
                required = config.round_quotas[round_idx]
                if game.state.cumulative_score >= required:
                    print(f"\n?? ROUND QUOTA REACHED! ({game.state.cumulative_score}/{required})")
                    print(f"Auto-ending round with {game.state.hands_left} hands remaining...\n")
                    break

            # Capture summary for console before completing round (hands_left pre-complete)
            hands_left_end = game.state.hands_left
            round_score = game.state.cumulative_score
            round_num = game.state.current_round
            summary_line = f"{ai_kind.capitalize()} - Round {round_num}: score {round_score}, hands left {hands_left_end}"
            round_summaries.append(summary_line)
            print(f"SUMMARY: {summary_line}")

            money_earned = game.complete_round()

            # Shop between rounds
            actions_log: List[str] = []
            shop_phase(game.state, joker_manager, ai, available_jokers, ui, actions_log)
            if actions_log:
                print("SHOP_ACTIONS: " + ", ".join(actions_log))

            # Win condition after each round
            if game.state.current_round >= config.rounds_per_session:
                break

        ui.print_divider("=", 60)
        print("SESSION RESULT")
        ui.print_divider("=", 60)
        print(f"Final score: {game.state.cumulative_score}")
        print(f"Active Jokers: {[j.get_display_name() for j in joker_manager.active_jokers]}")

    # Write captured log to file under ai_simulation/logs/
    logs_dir = Path(ROOT) / "ai_simulation" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / ("normal_ai.log" if ai_kind == 'normal' else "smart_ai.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(log_buffer.getvalue())

    return round_summaries


def main():
    parser = argparse.ArgumentParser(description="Auto-play Poker Grid with AI controllers")
    parser.add_argument("--ai", choices=["normal", "smart", "both"], default="both", help="Which AI to run")
    parser.add_argument("--samples", type=int, default=120, help="Samples for SmartAI EV per freeze candidate")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    parser.add_argument("--lines", type=int, default=None, help="Override lines_scored_per_hand (top-K lines to sum)")
    args = parser.parse_args()

    summaries: List[str] = []
    if args.ai in ("normal", "both"):
        summaries += play_session('normal', samples=args.samples, lines_scored=args.lines, seed=args.seed)
    if args.ai in ("smart", "both"):
        summaries += play_session('smart', samples=args.samples, lines_scored=args.lines, seed=args.seed)

    # Print concise per-round summaries only
    for s in summaries:
        print(s)


if __name__ == "__main__":
    main()
