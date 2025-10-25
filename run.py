#!/usr/bin/env python3
"""
Poker Grid - Main Entry Point
Full game loop with joker shop between rounds.
"""

import sys
import io

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.managers.game_manager import GameManager
from src.managers.joker_manager import JokerManager
from src.managers.shop_manager import ShopManager
from src.resources.game_config_resource import GameConfigResource
from src.ui_adapter import UIAdapter
from src.ui.terminal_ui import TerminalUI
from src.utils.joker_loader import JokerLoader


def run_shop(game_manager: GameManager, joker_manager: JokerManager,
             shop_manager: ShopManager, ui: TerminalUI, currency_reward: dict = None):
    """
    Run the shop phase between rounds.
    Player can buy, sell, and reroll jokers.
    """
    shop_manager.open_shop()

    # Display shop header
    ui.print_shop_header(currency_reward)
    ui.print_active_jokers(joker_manager)
    ui.print_shop_inventory(shop_manager)
    ui.print_shop_commands(shop_manager.get_reroll_cost())

    # Shop loop
    while True:
        cmd_str = ui.get_input()
        action, args = ui.parse_shop_command(cmd_str)

        if action == "buy":
            slot = args[0]
            success, message = shop_manager.buy_joker(slot)
            if success:
                ui.print_message(f"✓ {message}")
            else:
                ui.print_error(message)

            # Refresh display
            ui.print_shop_header()
            ui.print_active_jokers(joker_manager)
            ui.print_shop_inventory(shop_manager)
            ui.print_shop_commands(shop_manager.get_reroll_cost())

        elif action == "sell":
            slot = args[0]
            success, message = shop_manager.sell_joker(slot)
            if success:
                ui.print_message(f"✓ {message}")
            else:
                ui.print_error(message)

            # Refresh display
            ui.print_shop_header()
            ui.print_active_jokers(joker_manager)
            ui.print_shop_inventory(shop_manager)
            ui.print_shop_commands(shop_manager.get_reroll_cost())

        elif action == "reroll":
            success, message = shop_manager.reroll_shop()
            if success:
                ui.print_message(f"✓ {message}")
            else:
                ui.print_error(message)

            # Refresh display
            ui.print_shop_header()
            ui.print_active_jokers(joker_manager)
            ui.print_shop_inventory(shop_manager)
            ui.print_shop_commands(shop_manager.get_reroll_cost())

        elif action == "done":
            shop_manager.close_shop()
            ui.print_message("\nLeaving shop...")
            print()
            break

        else:
            ui.print_error("Invalid command. Try 'b <slot>', 's <slot>', 'r', or 'd'")


def run_round(game_manager: GameManager, joker_manager: JokerManager, ui: TerminalUI):
    """
    Run a single round: 7 spins with column rerolls.
    Auto-score after each spin.
    Returns (continue_game, currency_reward) tuple.
    """
    # Use UIAdapter to bridge between new architecture and old UI
    adapter = UIAdapter(game_manager)

    # Calculate and display current spin's score IMMEDIATELY
    current_score, row_hands, col_hands, top_lines = game_manager.score_manager.score_current_grid()

    # Display initial state with top 3 highlighted
    ui.print_round_header(current_score)
    ui.print_trophy_box(top_lines, current_score)
    ui.print_grid_with_scores(row_hands, col_hands, top_lines)

    # Show auto-freeze message if applicable (only if freeze enabled)
    if game_manager.config.enable_freeze and game_manager.config.auto_freeze_highest_pair:
        ui.print_auto_freeze_message()

    if game_manager.config.enable_freeze:
        ui.print_freeze_info()

    # Show active jokers if any
    if joker_manager.get_joker_count() > 0:
        print(f"\nActive Jokers ({joker_manager.get_joker_count()}/{joker_manager.max_slots}):")
        for joker in joker_manager.active_jokers:
            print(f"  • {joker.get_display_name()}")
        print()

    ui.print_commands()

    # Spin phase - player can reroll columns and complete spins
    while game_manager.state.spins_left > 0:
        cmd_str = ui.get_input()
        action, args = ui.parse_command(cmd_str)

        if action == "reroll":
            # Reroll columns (GDD v1.1)
            column_indices = args
            success, message = adapter.reroll_columns(column_indices)
            if success:
                ui.print_message(f"✓ {message}")
            else:
                ui.print_error(message)

            # Recalculate score with new cards
            current_score, row_hands, col_hands, top_lines = game_manager.score_manager.score_current_grid()

            # Refresh display with updated top 3
            ui.print_round_header(current_score)
            ui.print_trophy_box(top_lines, current_score)
            ui.print_grid_with_scores(row_hands, col_hands, top_lines)

            if game_manager.config.enable_freeze:
                ui.print_freeze_info()

        elif action == "freeze":
            # Only allow freeze commands if freeze system is enabled
            if not game_manager.config.enable_freeze:
                ui.print_error("Freeze system is disabled")
                continue

            row, col = args
            success, message = adapter.toggle_freeze(row, col)
            if success:
                ui.print_message(message)
            else:
                ui.print_error(message)

            # Refresh display
            ui.print_grid()
            ui.print_freeze_info()

        elif action == "unfreeze_all":
            # Only allow unfreeze if freeze system is enabled
            if not game_manager.config.enable_freeze:
                ui.print_error("Freeze system is disabled")
                continue

            adapter.unfreeze_all()
            ui.print_message("All cells unfrozen")
            ui.print_grid()
            ui.print_freeze_info()

        elif action == "play_hand":
            # Score current grid FIRST (this locks in the spin)
            current_score, row_hands, col_hands, top_lines = adapter.score_and_update()

            # Mark spin as complete
            game_manager.state.complete_spin()

            # Check if quota reached mid-round
            round_index = game_manager.state.current_round - 1
            required_score = game_manager.config.round_quotas[round_index]

            if game_manager.state.cumulative_score >= required_score:
                print(f"\n🎉 ROUND QUOTA REACHED! ({game_manager.state.cumulative_score}/{required_score})")
                print(f"Auto-ending round with {game_manager.state.spins_left} spins remaining...")
                input("\nPress Enter to continue...")
                print()
                break  # Exit spin loop - quota reached!

            # THEN deal new grid for next spin (if spins remain)
            if game_manager.state.spins_left > 0:
                adapter.play_spin()

                # Calculate score for NEW grid
                current_score, row_hands, col_hands, top_lines = game_manager.score_manager.score_current_grid()

                # Refresh display with new grid and top 3 highlighted
                ui.print_round_header(current_score)
                ui.print_trophy_box(top_lines, current_score)
                ui.print_grid_with_scores(row_hands, col_hands, top_lines)

                # Show auto-refreeze message if applicable
                if game_manager.config.enable_freeze and game_manager.config.auto_freeze_highest_pair:
                    ui.print_auto_freeze_message()

                if game_manager.config.enable_freeze:
                    ui.print_freeze_info()

                # Show commands again
                ui.print_commands()

        elif action == "quit":
            return (False, 0)

        else:
            ui.print_error("Invalid command")
            ui.print_commands()

    # Round complete - calculate currency reward
    currency_reward = game_manager.complete_round()

    # Get required score for this round
    round_index = game_manager.state.current_round - 1  # 0-indexed
    required_score = game_manager.config.round_quotas[round_index]

    # Show final results
    ui.print_divider("=")
    print(f"ROUND {game_manager.state.current_round} COMPLETE!")
    print(f"Cumulative Score: {game_manager.state.cumulative_score} chips")
    print(f"Required: {required_score} chips")

    # Show currency reward
    if currency_reward['currency_type'] == 'tokens':
        print(f"\n🎫 TOKENS EARNED:")
        print(f"   Base reward: {currency_reward['amount']} tokens")
        if currency_reward['bonus'] > 0:
            print(f"   Early completion bonus: +{currency_reward['bonus']} tokens")
        print(f"   Total: {currency_reward['total']} tokens")
    else:
        if currency_reward['total'] > 0:
            print(f"💰 Earned ${currency_reward['total']} from {currency_reward['total']} unutilized hand(s)!")

    # Check if quota met for this round
    if game_manager.state.cumulative_score >= required_score:
        surplus = game_manager.state.cumulative_score - required_score
        print(f"✓ Round {game_manager.state.current_round} quota met! (+{surplus} chips surplus)")
    else:
        shortfall = required_score - game_manager.state.cumulative_score
        print(f"❌ ROUND {game_manager.state.current_round} FAILED!")
        print(f"Short by: {shortfall} chips")
        ui.print_divider("=")
        return (False, currency_reward)  # End game - quota not met

    ui.print_divider("=")
    print()

    return (True, currency_reward)


def run_game():
    """Main game loop with shop system."""
    # Initialize with new architecture
    config = GameConfigResource()
    joker_manager = JokerManager(max_slots=5)
    game_manager = GameManager(config, joker_manager)
    adapter = UIAdapter(game_manager)
    ui = TerminalUI(adapter)

    # Load available jokers
    print("Loading jokers...")
    available_jokers = JokerLoader.load_p0_jokers()
    print(f"Loaded {len(available_jokers)} jokers\n")

    # Create shop manager
    shop_manager = ShopManager(game_manager.state, joker_manager, available_jokers, config)

    # Welcome message
    ui.print_divider("=", 60)
    print("Welcome to POKER GRID!")
    print(f"Goal: Complete {config.rounds_per_session} rounds")
    print(f"Spins per quota: {config.max_spins}")
    if config.enable_freeze:
        print(f"Auto-freeze highest pair: {'ON' if config.auto_freeze_highest_pair else 'OFF'}")
    else:
        print(f"Freeze system: DISABLED")
    ui.print_divider("=", 60)
    print()

    # Main game loop: multiple rounds with shop between
    currency_reward = None

    while game_manager.state.current_round < config.rounds_per_session:
        # Start new round
        game_manager.start_new_round()

        # Run the round
        continue_game, currency_reward = run_round(game_manager, joker_manager, ui)

        if not continue_game:
            # Player quit OR failed to meet round quota
            round_index = game_manager.state.current_round - 1
            if round_index < len(config.round_quotas) and game_manager.state.cumulative_score < config.round_quotas[round_index]:
                # Failed quota
                ui.print_divider("=", 60)
                print("GAME OVER - QUOTA NOT MET")
                ui.print_divider("=", 60)
                print(f"\n❌ YOU LOSE. Failed to meet Round {game_manager.state.current_round} quota.")
                print(f"Final score: {game_manager.state.cumulative_score}")
                print(f"Required: {config.round_quotas[round_index]}")
                print(f"Rounds completed: {game_manager.state.current_round}/{config.rounds_per_session}")
                ui.print_divider("=", 60)
            else:
                ui.print_message("\nGame quit early.")
            return

        if adapter.is_session_complete():
            break

        # Open shop between rounds
        print(f"\n{'='*60}")
        print(f"Preparing for Round {game_manager.state.current_round + 1}...")
        print(f"{'='*60}\n")

        run_shop(game_manager, joker_manager, shop_manager, ui, currency_reward)

    # Show final results
    ui.print_divider("=", 60)
    print("GAME COMPLETE!")
    ui.print_divider("=", 60)

    print(f"\n🎉 YOU WIN! Completed all {config.rounds_per_session} rounds!")
    print(f"Final score: {game_manager.state.cumulative_score}")

    if config.use_token_system:
        print(f"Tokens remaining: {game_manager.state.tokens} tokens")
    else:
        print(f"Money remaining: ${game_manager.state.money}")

    print(f"Final jokers: {joker_manager.get_joker_count()}")
    ui.print_divider("=", 60)


if __name__ == "__main__":
    run_game()
