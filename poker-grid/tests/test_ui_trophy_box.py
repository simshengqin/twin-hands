"""
Test trophy box UI display
Tests that trophy box correctly displays top scoring lines
"""
import sys
import io
import pytest
from src.managers.game_manager import GameManager
from src.resources.game_config_resource import GameConfigResource
from src.ui.terminal_ui import TerminalUI
from src.ui_adapter import UIAdapter
from src.resources.hand_resource import HandResource


class TestTrophyBoxDisplay:
    """Test trophy box rendering with various scenarios"""

    def test_trophy_box_displays_all_top_lines(self, started_game, capsys):
        """Trophy box shows all top scoring lines"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        # Create mock top lines
        hand1 = HandResource(hand_type="Full House", chips=40, mult=4, cards=[])
        hand2 = HandResource(hand_type="Two Pair", chips=20, mult=2, cards=[])
        hand3 = HandResource(hand_type="One Pair", chips=10, mult=2, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 160, 'hand': hand1},
            {'type': 'col', 'index': 2, 'rank': 2, 'score': 40, 'hand': hand2},
            {'type': 'row', 'index': 3, 'rank': 3, 'score': 20, 'hand': hand3},
        ]

        ui.print_trophy_box(top_lines, total=220)
        output = capsys.readouterr().out

        # Check all lines are present (by their hand types)
        assert "Full House" in output
        assert "Two Pair" in output
        assert "One Pair" in output

        # Check flat chips are shown (no mult calculations)
        assert "40 chips" in output
        assert "20 chips" in output
        assert "10 chips" in output

        # Note: Total is no longer displayed in trophy box (shown in header instead)

    def test_trophy_box_shows_rank_medals(self, started_game, capsys):
        """Trophy box displays medal emojis for ranks"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand1 = HandResource(hand_type="Flush", chips=35, mult=4, cards=[])
        hand2 = HandResource(hand_type="Straight", chips=30, mult=4, cards=[])
        hand3 = HandResource(hand_type="Three of a Kind", chips=30, mult=3, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 140, 'hand': hand1},
            {'type': 'col', 'index': 1, 'rank': 2, 'score': 120, 'hand': hand2},
            {'type': 'row', 'index': 2, 'rank': 3, 'score': 90, 'hand': hand3},
        ]

        ui.print_trophy_box(top_lines, total=350)
        output = capsys.readouterr().out

        # Check medals are present (these are the actual emoji)
        assert "🥇" in output  # Gold medal for 1st
        assert "🥈" in output  # Silver medal for 2nd
        assert "🥉" in output  # Bronze medal for 3rd

        # Check ordinal text
        assert "1st" in output
        assert "2nd" in output
        assert "3rd" in output

    def test_trophy_box_handles_ties(self, started_game, capsys):
        """Trophy box correctly displays tied ranks"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand1 = HandResource(hand_type="One Pair", chips=10, mult=2, cards=[])
        hand2 = HandResource(hand_type="One Pair", chips=10, mult=2, cards=[])
        hand3 = HandResource(hand_type="One Pair", chips=10, mult=2, cards=[])

        # All tied for 1st
        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 20, 'hand': hand1},
            {'type': 'col', 'index': 1, 'rank': 1, 'score': 20, 'hand': hand2},
            {'type': 'row', 'index': 2, 'rank': 1, 'score': 20, 'hand': hand3},
        ]

        ui.print_trophy_box(top_lines, total=60)
        output = capsys.readouterr().out

        # All should show gold medals (1st place)
        gold_medal_count = output.count("🥇")
        assert gold_medal_count == 3, f"Expected 3 gold medals for 3-way tie, got {gold_medal_count}"

        # All should show 1st
        first_count = output.count("1st")
        assert first_count == 3, f"Expected 3 '1st' labels, got {first_count}"

    def test_trophy_box_shows_line_types_and_indices(self, started_game, capsys):
        """Trophy box displays line type (Row/Col) and index"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand = HandResource(hand_type="Straight", chips=30, mult=4, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 120, 'hand': hand},
            {'type': 'col', 'index': 4, 'rank': 2, 'score': 120, 'hand': hand},
            {'type': 'row', 'index': 2, 'rank': 3, 'score': 120, 'hand': hand},
        ]

        ui.print_trophy_box(top_lines, total=360)
        output = capsys.readouterr().out

        # Check line type identifiers
        assert "Row 0" in output
        assert "Col 4" in output
        assert "Row 2" in output

    def test_trophy_box_uses_box_drawing_characters(self, started_game, capsys):
        """Trophy box uses Unicode box-drawing characters"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand = HandResource(hand_type="High Card", chips=5, mult=1, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 5, 'hand': hand},
        ]

        ui.print_trophy_box(top_lines, total=5)
        output = capsys.readouterr().out

        # Check for box drawing characters
        assert "┌" in output  # Top left corner
        assert "┐" in output  # Top right corner
        assert "└" in output  # Bottom left corner
        assert "┘" in output  # Bottom right corner
        assert "│" in output  # Vertical line
        assert "─" in output  # Horizontal line
        # Note: No longer using T-junctions (├ ┤) since we removed the separator line

    def test_trophy_box_handles_empty_list(self, started_game, capsys):
        """Trophy box handles empty top_lines gracefully"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        # Empty list should not print anything
        ui.print_trophy_box([], total=0)
        output = capsys.readouterr().out

        # Should produce no output
        assert output == ""

    def test_trophy_box_handles_single_line(self, started_game, capsys):
        """Trophy box works with just one top line"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand = HandResource(hand_type="Royal Flush", chips=100, mult=8, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 800, 'hand': hand},
        ]

        ui.print_trophy_box(top_lines, total=800)
        output = capsys.readouterr().out

        # Should still display properly
        assert "Royal Flush" in output
        assert "100 chips" in output
        assert "🥇" in output
        # Note: No longer displaying "TOP N TOTAL" line

    def test_trophy_box_with_real_game_scoring(self, started_game):
        """Trophy box integrates correctly with real game scoring"""
        game = started_game

        # Play a hand
        game.play_spin()

        # Score it
        current_score, row_hands, col_hands, top_lines = game.score_manager.score_current_grid()

        # Create UI and display trophy box
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        # Should not raise any errors
        ui.print_trophy_box(top_lines, current_score)

        # Verify top_lines structure
        assert len(top_lines) > 0, "Should have at least one scoring line"
        assert len(top_lines) <= 3, "Should have at most 3 top lines"

        for line in top_lines:
            # Verify required keys
            assert 'type' in line
            assert 'index' in line
            assert 'rank' in line
            assert 'score' in line
            assert 'hand' in line

            # Verify types
            assert line['type'] in ['row', 'col']
            assert isinstance(line['index'], int)
            assert line['rank'] in [1, 2, 3]
            assert isinstance(line['score'], int)
            assert hasattr(line['hand'], 'chips')
            assert hasattr(line['hand'], 'mult')

    def test_trophy_box_total_matches_sum(self, started_game):
        """Trophy box total matches sum of top line scores"""
        game = started_game

        hand1 = HandResource(hand_type="Flush", chips=35, mult=4, cards=[])
        hand2 = HandResource(hand_type="Straight", chips=30, mult=4, cards=[])
        hand3 = HandResource(hand_type="Two Pair", chips=20, mult=2, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 140, 'hand': hand1},
            {'type': 'col', 'index': 1, 'rank': 2, 'score': 120, 'hand': hand2},
            {'type': 'row', 'index': 2, 'rank': 3, 'score': 40, 'hand': hand3},
        ]

        # Calculate expected total
        expected_total = sum(line['score'] for line in top_lines)
        assert expected_total == 300

        # Test with correct total
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        # Should work without errors when total matches
        ui.print_trophy_box(top_lines, expected_total)

    def test_trophy_box_handles_various_hand_types(self, started_game, capsys):
        """Trophy box displays all poker hand types correctly"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        # Test with various hand types
        hand_types = [
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

        for hand_type in hand_types:
            hand = HandResource(hand_type=hand_type, chips=10, mult=2, cards=[])
            top_lines = [
                {'type': 'row', 'index': 0, 'rank': 1, 'score': 20, 'hand': hand},
            ]

            ui.print_trophy_box(top_lines, total=20)
            output = capsys.readouterr().out

            # Each hand type should appear in output
            assert hand_type in output, f"{hand_type} not found in trophy box output"


class TestTrophyBoxAlignment:
    """Test trophy box formatting and alignment (behavior-based, not fragile)"""

    def test_trophy_box_borders_are_consistent(self, started_game, capsys):
        """Trophy box has consistent border lines"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand = HandResource(hand_type="Flush", chips=35, mult=4, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 140, 'hand': hand},
            {'type': 'col', 'index': 1, 'rank': 2, 'score': 140, 'hand': hand},
            {'type': 'row', 'index': 2, 'rank': 3, 'score': 140, 'hand': hand},
        ]

        ui.print_trophy_box(top_lines, total=420)
        output = capsys.readouterr().out

        lines = output.strip().split('\n')

        # Find all lines with borders
        top_border = [line for line in lines if line.startswith('┌')][0]
        bottom_border = [line for line in lines if line.startswith('└')][0]

        # Top and bottom borders should have same length
        assert len(top_border) == len(bottom_border), "Top and bottom borders should match"

    def test_trophy_box_each_content_line_has_borders(self, started_game, capsys):
        """Every content line in trophy box starts and ends with │"""
        game = started_game
        adapter = UIAdapter(game)
        ui = TerminalUI(adapter)

        hand = HandResource(hand_type="Straight", chips=30, mult=4, cards=[])

        top_lines = [
            {'type': 'row', 'index': 0, 'rank': 1, 'score': 120, 'hand': hand},
            {'type': 'col', 'index': 1, 'rank': 2, 'score': 120, 'hand': hand},
        ]

        ui.print_trophy_box(top_lines, total=240)
        output = capsys.readouterr().out

        lines = output.strip().split('\n')

        # Find content lines (those with │ on both sides, excluding borders)
        content_lines = [
            line for line in lines
            if line.startswith('│') and line.endswith('│')
            and not line.startswith('├') and not line.startswith('┌') and not line.startswith('└')
        ]

        # Should have 2 content lines (no longer showing total line)
        assert len(content_lines) == 2, f"Expected 2 content lines, got {len(content_lines)}"

        # All content lines should have matching left and right borders
        for line in content_lines:
            assert line[0] == '│', "Content line should start with │"
            assert line[-1] == '│', "Content line should end with │"
