# Poker Grid - Terminal UI
# Display and input handling (like UI layer in Godot)

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Type hints only - not imported at runtime
    from src.resources.hand_resource import HandResource as Hand
    from src.ui_adapter import UIAdapter


class TerminalUI:
    """Handles all terminal display and user input."""

    def __init__(self, game):
        """
        Initialize UI with game adapter.
        In the new architecture, this receives a UIAdapter that wraps GameManager.
        """
        self.game = game

    def clear_screen(self):
        """Clear the terminal (optional, can be noisy)."""
        # Uncomment if you want screen clearing
        # import os
        # os.system('cls' if os.name == 'nt' else 'clear')
        pass

    def print_divider(self, char="=", length=60):
        """Print a visual divider."""
        print(char * length)

    def print_round_header(self, current_spin_score: int = 0):
        """
        Print round information with current spin preview.

        Args:
            current_spin_score: Score for the current (unsaved) spin
        """
        state = self.game.state
        config = self.game.config

        # Get current round's quota target
        round_index = state.current_round - 1
        round_quota = config.round_quotas[round_index] if round_index < len(config.round_quotas) else config.quota_target

        self.print_divider()
        print(f"POKER GRID - Round {state.current_round}/{config.rounds_per_session}")
        # Display spins starting from 1 instead of 0
        current_spin = state.spins_taken + 1 if state.spins_left > 0 else state.spins_taken
        print(f"Spin: {current_spin}/{config.spins_per_quota} | Reroll Tokens: {state.reroll_tokens_left}/{config.reroll_tokens_per_quota}")

        # Show current spin score and projected total
        if current_spin_score > 0:
            projected = state.cumulative_score + current_spin_score
            needed = round_quota - projected
            print(f"Current Spin: {current_spin_score} chips | Total: {state.cumulative_score} → {projected} / {round_quota} ({needed} needed)")
        else:
            print(f"Score: {state.cumulative_score} / {round_quota} (Round {state.current_round} Quota)")

        self.print_divider()

    def print_grid(self, top_lines: List[dict] = None):
        """
        Display the current 5x5 grid with row/col indices.
        Highlights top scoring lines in rank-based colors.

        Args:
            top_lines: List of top scoring lines with 'type', 'index', 'rank' keys
        """
        from src.utils.color_util import ColorUtil

        state = self.game.state

        # Build highlight map: {('row', idx): rank} and {('col', idx): rank}
        highlight_map = {}
        if top_lines:
            for line in top_lines:
                key = (line['type'], line['index'])
                # Use highest rank if there are ties
                if key not in highlight_map or line['rank'] < highlight_map[key]:
                    highlight_map[key] = line['rank']

        print("\n    ", end="")

        # Column headers
        for col in range(state.config.grid_cols):
            print(f"  {col}  ", end="")
        print()

        # Print each row
        for row_idx in range(state.config.grid_rows):
            # Check if this row is highlighted
            row_rank = highlight_map.get(('row', row_idx), None)

            print(f" {row_idx} |", end="")
            for col_idx in range(state.config.grid_cols):
                cell = state.grid[row_idx][col_idx]

                # Determine if this cell should be colored for highlighting
                col_rank = highlight_map.get(('col', col_idx), None)

                # Use the best rank (lower number = better)
                cell_rank = None
                if row_rank and col_rank:
                    cell_rank = min(row_rank, col_rank)
                elif row_rank:
                    cell_rank = row_rank
                elif col_rank:
                    cell_rank = col_rank

                # Get card string
                # Result grid (top_lines provided): NO suit colors at all
                # Playing grid (top_lines is None): show colored suits
                if cell.card:
                    if top_lines is not None:
                        # Result grid - no suit colors (to avoid conflicts with highlights)
                        card_str = cell.card.get_display_string(colored=False)
                    else:
                        # Playing grid - show colored suits
                        card_str = str(cell.card)
                else:
                    card_str = "  "

                # Format cell with frozen marker
                if cell.is_frozen:
                    cell_display = f" {card_str:3}*"
                else:
                    cell_display = f" {card_str:3} "

                # Apply color if highlighted
                if cell_rank:
                    cell_display = ColorUtil.colorize(cell_display, cell_rank)

                print(cell_display, end="")
            print()
        print()

    def print_grid_with_scores(self, row_hands: List, col_hands: List, top_lines: List[dict] = None):
        """
        Display grid with scores on the side and bottom.
        Highlights contributing cards in top 3 hands with rank colors (Balatro-style).

        Args:
            row_hands: List of HandResource for each row
            col_hands: List of HandResource for each column
            top_lines: List of top scoring lines for medal display
        """
        from src.utils.color_util import ColorUtil
        from src.utils.poker_evaluator import PokerEvaluator

        state = self.game.state

        # Build rank map for medals
        rank_map = {}  # {('row', idx): rank} or {('col', idx): rank}
        if top_lines:
            for line in top_lines:
                key = (line['type'], line['index'])
                if key not in rank_map or line['rank'] < rank_map[key]:
                    rank_map[key] = line['rank']

        # Build highlight map: {(row, col): rank} for contributing cards
        highlight_map = {}  # Maps grid position to the highest rank color
        if top_lines:
            for line in top_lines:
                hand = line['hand']
                line_type = line['type']
                line_index = line['index']
                rank = line['rank']

                # Get contributing cards for this hand
                contributing_cards = PokerEvaluator.get_contributing_cards(hand)

                # Get the original unsorted cards from the grid
                if line_type == 'row':
                    original_cards = state.get_row(line_index)
                else:  # 'col'
                    original_cards = state.get_col(line_index)

                # Map contributing cards to their positions in the original unsorted row/col
                # We need to match by rank AND suit since there can be duplicates
                contributing_ranks_suits = [(c.rank, c.suit) for c in contributing_cards]

                for original_idx, original_card in enumerate(original_cards):
                    card_key = (original_card.rank, original_card.suit)
                    if card_key in contributing_ranks_suits:
                        # Determine grid position based on line type
                        if line_type == 'row':
                            grid_pos = (line_index, original_idx)
                        else:  # 'col'
                            grid_pos = (original_idx, line_index)

                        # Use highest rank (1 > 2 > 3) if cell is in multiple hands
                        if grid_pos not in highlight_map or rank < highlight_map[grid_pos]:
                            highlight_map[grid_pos] = rank

                        # Remove from list to handle duplicates correctly
                        contributing_ranks_suits.remove(card_key)

        # Medal lookup
        medals = {1: '🥇', 2: '🥈', 3: '🥉'}

        # Column headers centered over each 5-char card column
        # Format: 5 spaces + "0" + 4 spaces + "1" + 4 spaces + ...
        print("      0    1    2    3    4")
        print("    ┌─────────────────────────┐")

        # Print each row with score on the right
        for row_idx in range(state.config.grid_rows):
            row_rank = rank_map.get(('row', row_idx), None)

            print(f" {row_idx}  │", end="")
            for col_idx in range(state.config.grid_cols):
                cell = state.grid[row_idx][col_idx]

                # Check if this cell should be highlighted
                cell_rank = highlight_map.get((row_idx, col_idx), None)

                # Get card string (colored suits)
                if cell.card:
                    card_str = str(cell.card)

                    # Apply rank color highlight if in top 3 contributing cards
                    if cell_rank:
                        rank_color = ColorUtil.get_rank_color(cell_rank)
                        card_str = f"{rank_color}{cell.card.rank}{cell.card.get_display_string(colored=True)[len(cell.card.rank):]}"

                    # Card is always 2 visual chars (e.g., "K♣", "T♥")
                    # Don't use string formatting on ANSI-colored strings
                    # Format: space + card + 2 spaces = 5 chars per column
                    if cell.is_frozen:
                        cell_display = f" {card_str} *"
                    else:
                        cell_display = f" {card_str}  "
                else:
                    cell_display = "     "  # 5 spaces for empty cell

                print(cell_display, end="")

            # Row score on the right
            row_score = row_hands[row_idx].chips
            medal = medals.get(row_rank, '  ') if row_rank else '  '
            print(f"│ {row_score:3} {medal}")

        print("    └─────────────────────────┘")

        # Column scores on the bottom (each in 5-char column)
        print("     ", end="")  # 5 spaces to align with first card column
        for col_idx in range(state.config.grid_cols):
            col_score = col_hands[col_idx].chips
            print(f" {col_score:>2}  ", end="")  # Score right-aligned in 5-char column
        print()

        # Column medals on bottom (each in 5-char column)
        print("     ", end="")  # 5 spaces to align with first card column
        for col_idx in range(state.config.grid_cols):
            col_rank = rank_map.get(('col', col_idx), None)
            medal = medals.get(col_rank, '  ') if col_rank else '  '
            print(f" {medal}  ", end="")  # Medal centered in 5-char column
        print()

    def print_freeze_info(self):
        """Show freeze information (only if freeze system is enabled)."""
        state = self.game.state
        config = self.game.config

        # Skip if freeze system is disabled
        if not config.enable_freeze:
            return

        freezes_used = len(state.frozen_cells)
        freezes_left = config.max_freezes - freezes_used

        print(f"Freezes: {freezes_used}/{config.max_freezes} used ({freezes_left} remaining)")

        if state.frozen_cells:
            frozen_str = ", ".join(f"({r},{c})" for r, c in state.frozen_cells)
            frozen_cards = [str(state.grid[r][c].card) for r, c in state.frozen_cells]
            print(f"Frozen cells: {frozen_str} -> {', '.join(frozen_cards)}")
        print()

    def _get_rank_label_with_tie(self, top_lines: List[dict], line_key: tuple, rank: int) -> str:
        """
        Get rank label with "tied" suffix if multiple lines share the same rank.

        Args:
            top_lines: List of top scoring lines
            line_key: Tuple of ('row'/'col', index)
            rank: The rank (1, 2, or 3)

        Returns:
            Colorized label like "(1st)", "(2nd tied)", "(3rd)"
        """
        from src.utils.color_util import ColorUtil

        # Count how many lines have this rank
        lines_with_rank = [line for line in top_lines if line['rank'] == rank]

        # Determine label
        rank_names = {1: "1st", 2: "2nd", 3: "3rd"}
        base_label = rank_names.get(rank, "")

        if len(lines_with_rank) > 1:
            label = f"({base_label} tied)"
        else:
            label = f"({base_label})"

        return ColorUtil.colorize(label, rank)

    def print_trophy_box(self, top_lines: List[dict], total: int):
        """
        Display a compact trophy box showing top 3 scoring lines with emoji medals.

        Args:
            top_lines: List of top scoring lines with 'type', 'index', 'rank', 'score', 'hand' keys
            total: Total score (sum of top lines)
        """
        if not top_lines:
            return

        # Medal emojis for ranks
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        ordinals = {1: "1st", 2: "2nd", 3: "3rd"}

        # First pass: build all line content (without borders)
        line_contents = []
        for line in top_lines:
            rank = line['rank']
            medal = medals.get(rank, "  ")
            line_type = line['type'].capitalize()
            index = line['index']
            hand = line['hand']
            hand_type = hand.hand_type
            chips = hand.chips
            score = line['score']
            rank_text = ordinals.get(rank, f"{rank}th")

            # Format: "🥇 1st: Row 0 (Full House) 70 chips"
            content = f" {medal} {rank_text}: {line_type} {index} ({hand_type}) {chips} chips "
            line_contents.append(content)

        # Find max visual width (emoji takes 2 display columns but len() counts it as 1)
        # So we add 1 to account for the visual width difference
        max_visual_width = max(len(c) + 1 for c in line_contents)  # +1 for emoji

        # Build the box
        print(f"\n┌{'─' * max_visual_width}┐")

        # Print each line with proper padding
        for content in line_contents:
            visual_length = len(content) + 1  # +1 for emoji visual width
            padding = max_visual_width - visual_length
            print(f"│{content}{' ' * padding}│")

        print(f"└{'─' * max_visual_width}┘")

    def print_line_scores(self, row_hands: List, col_hands: List, total: int, top_lines: List[dict] = None):
        """
        Display detailed scoring for each line with flat chip values.
        Highlights top 3 scoring lines with rank markers and colors.

        Args:
            row_hands: List of row hand resources
            col_hands: List of column hand resources
            total: Total score (sum of top 3 lines)
            top_lines: List of top scoring lines with 'type', 'index', 'rank', 'score' keys
        """
        from src.utils.color_util import ColorUtil

        # Show trophy box first if we have top lines
        if top_lines:
            self.print_trophy_box(top_lines, total)

        # Build rank map for quick lookup
        rank_map = {}
        if top_lines:
            for line in top_lines:
                key = (line['type'], line['index'])
                rank_map[key] = line['rank']

        self.print_divider("-")
        print("SCORING BREAKDOWN:")
        self.print_divider("-")

        # Columns first (as per user request)
        print("\nCOLUMNS:")
        for i, hand in enumerate(col_hands):
            score = hand.get_score()
            rank = rank_map.get(('col', i), None)

            # Format the line (flat chips only, no mult display)
            line_str = f"  Col {i}: {hand.hand_type:20s} ({hand.chips:3d} chips)"

            # Add rank marker and colorize if in top 3
            if rank:
                rank_label = self._get_rank_label_with_tie(top_lines, ('col', i), rank)
                line_str = ColorUtil.colorize(line_str, rank) + f" {rank_label}"

            print(line_str)

        # Rows second
        print("\nROWS:")
        for i, hand in enumerate(row_hands):
            score = hand.get_score()
            rank = rank_map.get(('row', i), None)

            # Format the line (flat chips only, no mult display)
            line_str = f"  Row {i}: {hand.hand_type:20s} ({hand.chips:3d} chips)"

            # Add rank marker and colorize if in top 3
            if rank:
                rank_label = self._get_rank_label_with_tie(top_lines, ('row', i), rank)
                line_str = ColorUtil.colorize(line_str, rank) + f" {rank_label}"

            print(line_str)

        self.print_divider("-")
        print()

    def print_commands(self):
        """Print available commands."""
        config = self.game.config
        state = self.game.state

        print("Commands:")

        # Column reroll commands (GDD v1.1)
        print(f"  r <cols>       - Reroll columns (e.g., 'r024' or 'r 0 2 4') [Tokens: {state.reroll_tokens_left}/{config.reroll_tokens_per_quota}]")

        # Only show freeze commands if freeze system is enabled
        if config.enable_freeze:
            print("  f <row> <col>  - Toggle freeze on cell (e.g., 'f 2 3')")
            print("  u              - Unfreeze all cells")

        print("  s              - Complete spin (score and continue)")
        print("  q              - Quit session")
        print()

    def get_input(self) -> Optional[str]:
        """Get user input."""
        try:
            return input("> ").strip().lower()
        except EOFError:
            return "q"
        except KeyboardInterrupt:
            return "q"

    def parse_command(self, cmd: str) -> tuple:
        """
        Parse user command.
        Returns (action, args) where action is one of:
        'reroll', 'freeze', 'unfreeze_all', 'play_hand' (complete spin), 'quit', 'invalid'
        """
        if not cmd:
            return ("invalid", [])

        parts = cmd.split()
        action = parts[0]

        if action.startswith("r") and len(action) > 1:
            # Support "r1", "r12", "r034" format (no spaces)
            try:
                column_indices = [int(char) for char in action[1:]]
                return ("reroll", column_indices)
            except ValueError:
                return ("invalid", [])

        elif action == "r" and len(parts) >= 2:
            # Reroll columns with spaces: "r 0 2 4"
            try:
                column_indices = [int(col) for col in parts[1:]]
                return ("reroll", column_indices)
            except ValueError:
                return ("invalid", [])

        elif action == "f" and len(parts) == 3:
            try:
                row = int(parts[1])
                col = int(parts[2])
                return ("freeze", [row, col])
            except ValueError:
                return ("invalid", [])

        elif action == "u":
            return ("unfreeze_all", [])

        elif action == "s":
            # Complete spin (score and continue)
            return ("play_hand", [])

        elif action == "q":
            return ("quit", [])

        else:
            return ("invalid", [])

    def print_round_result(self, round_score: int):
        """Display the result of the completed round."""
        state = self.game.state
        config = self.game.config

        self.print_divider("=")
        print(f"ROUND {state.current_round} COMPLETE!")
        print(f"Round Score: {round_score} chips")
        print(f"Total Score: {state.total_score} / {config.quota_target}")
        self.print_divider("=")
        print()

    def print_session_result(self):
        """Display final session result."""
        state = self.game.state
        config = self.game.config
        result = self.game.get_session_result()

        self.print_divider("=", 60)
        print("SESSION COMPLETE!")
        self.print_divider("=", 60)

        print(f"\nRounds Played: {state.current_round}/{config.rounds_per_session}")
        print(f"Final Score: {state.total_score}")
        print(f"Quota Target: {config.quota_target}")

        print("\nRound Breakdown:")
        for i, score in enumerate(state.round_scores, 1):
            print(f"  Round {i}: {score} chips")

        self.print_divider("-")
        if result == "WIN":
            print("🎉 YOU WIN! Quota reached!")
        else:
            shortfall = config.quota_target - state.total_score
            print(f"❌ LOSE. Short by {shortfall} chips.")

        self.print_divider("=", 60)

    def ask_continue(self) -> bool:
        """Ask if player wants to continue to next round."""
        if self.game.is_session_complete():
            return False

        print(f"\nContinue to Round {self.game.state.current_round + 1}? (y/n): ", end="")
        response = input().strip().lower()
        return response in ["y", "yes"]

    def print_message(self, message: str):
        """Print a generic message."""
        print(message)

    def print_error(self, error: str):
        """Print an error message."""
        print(f"❌ {error}")

    def print_auto_freeze_message(self):
        """Print message about auto-freeze (only if freeze system is enabled)."""
        config = self.game.config
        state = self.game.state

        # Skip if freeze system is disabled
        if not config.enable_freeze:
            return

        if not state.frozen_cells:
            print("🔓 No auto-freeze (no suitable combination found)")
            print()
            return

        frozen_cards = [state.grid[r][c].card for r, c in state.frozen_cells]
        frozen_str = ", ".join(f"({r},{c})" for r, c in state.frozen_cells)

        # Determine freeze type
        if len(frozen_cards) == 2:
            card1, card2 = frozen_cards
            pos1, pos2 = state.frozen_cells

            # Check if it's a pair
            if card1.rank == card2.rank:
                # Check if same row or column
                if pos1[0] == pos2[0]:
                    freeze_type = f"pair of {card1.rank}s (same row)"
                elif pos1[1] == pos2[1]:
                    freeze_type = f"pair of {card1.rank}s (same column)"
                else:
                    freeze_type = f"pair of {card1.rank}s"
            # Check if same suit
            elif card1.suit == card2.suit:
                freeze_type = f"{card1}{card2} (same suit: {card1.suit})"
            else:
                freeze_type = f"{card1} {card2}"

            print(f"🔒 Auto-frozen: {freeze_type} at {frozen_str}")
            print()

    def print_spin_preview(self, current_score: int):
        """Show current spin score and projected cumulative with quota tracking."""
        state = self.game.state
        config = self.game.config
        round_index = state.current_round - 1
        required = config.round_quotas[round_index] if round_index < len(config.round_quotas) else config.quota_target
        projected = state.cumulative_score + current_score
        remaining = required - projected

        print(f"\n💡 Current Spin Score: {current_score} chips")
        print(f"   Cumulative (so far): {state.cumulative_score} chips")
        print(f"   After this spin: {projected}/{required} chips ({remaining} needed)")

    # === SHOP UI METHODS ===

    def print_shop_header(self, currency_reward: dict = None):
        """Display shop header with currency info (money or tokens)."""
        state = self.game.state
        config = self.game.config

        self.print_divider("=")
        print("JOKER SHOP")
        self.print_divider("=")

        # Show currency reward if provided
        if currency_reward:
            if currency_reward['currency_type'] == 'tokens':
                print(f"\n🎫 TOKENS EARNED:")
                print(f"   Base reward: {currency_reward['amount']} tokens")
                if currency_reward['bonus'] > 0:
                    print(f"   Early completion bonus: +{currency_reward['bonus']} tokens")
                print(f"   Total: {currency_reward['total']} tokens")
            else:
                if currency_reward['total'] > 0:
                    print(f"\n💰 Earned ${currency_reward['total']} from {currency_reward['total']} unutilized hand(s)!")

        # Show current currency balance
        if config.use_token_system:
            print(f"\n🎫 Tokens: {state.tokens}")
        else:
            print(f"\n💵 Money: ${state.money}")

        print()

    def print_active_jokers(self, joker_manager):
        """Display player's currently owned jokers."""
        config = self.game.config

        if joker_manager.get_joker_count() == 0:
            print("Active Jokers: None")
            print()
            return

        print(f"Active Jokers ({joker_manager.get_joker_count()}/{joker_manager.max_slots}):")
        for i, joker in enumerate(joker_manager.active_jokers):
            sell_value = joker.sell_value

            # Show sell value in tokens or money
            if config.use_token_system:
                sell_str = f"{sell_value} tokens"
            else:
                sell_str = f"${sell_value}"

            print(f"  [{i+1}] {joker.get_display_name()} (Sell: {sell_str})")
            print(f"      {joker.get_description()}")
        print()

    def print_shop_inventory(self, shop_manager):
        """Display the 3 shop slots with joker details."""
        config = self.game.config

        self.print_divider("-")
        print("SHOP INVENTORY:")
        self.print_divider("-")

        inventory = shop_manager.get_shop_display()

        for item in inventory:
            if item['joker']:
                # Show cost in tokens or money based on config
                if config.use_token_system:
                    cost_str = f"{item['cost']} tokens"
                else:
                    cost_str = f"${item['cost']}"

                print(f"\n[{item['index'] + 1}] {item['name']} - {cost_str} [{item['rarity']}]")
                print(f"    {item['description']}")
            else:
                print(f"\n[{item['index'] + 1}] [EMPTY SLOT]")

        print()

    def print_shop_commands(self, reroll_cost: int):
        """Show available shop commands."""
        config = self.game.config

        self.print_divider("-")
        print("Commands:")
        print(f"  b <slot>  - Buy joker from slot (1-3)")
        print(f"  s <slot>  - Sell active joker (1-{5})")  # Max slots is 5

        # Show reroll cost in tokens or money
        if config.use_token_system:
            print(f"  r         - Reroll shop ({reroll_cost} tokens)")
        else:
            print(f"  r         - Reroll shop (${reroll_cost})")

        print(f"  d         - Done shopping (continue to next round)")
        self.print_divider("-")
        print()

    def parse_shop_command(self, cmd: str) -> tuple:
        """
        Parse shop command.
        Returns (action, args) where action is:
        'buy', 'sell', 'reroll', 'done', 'invalid'
        """
        if not cmd:
            return ("invalid", [])

        parts = cmd.split()
        action = parts[0]

        if action == "b" and len(parts) == 2:
            try:
                slot = int(parts[1]) - 1  # Convert to 0-indexed
                return ("buy", [slot])
            except ValueError:
                return ("invalid", [])

        elif action == "s" and len(parts) == 2:
            try:
                slot = int(parts[1]) - 1  # Convert to 0-indexed
                return ("sell", [slot])
            except ValueError:
                return ("invalid", [])

        elif action == "r":
            return ("reroll", [])

        elif action == "d":
            return ("done", [])

        else:
            return ("invalid", [])
