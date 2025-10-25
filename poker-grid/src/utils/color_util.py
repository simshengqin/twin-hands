"""
Color Utility - Terminal color formatting
Provides ANSI color codes for rank-based highlighting.
"""


class ColorUtil:
    """
    Static utility for terminal color formatting.
    Optimized for dark backgrounds.
    """

    # ANSI color codes for dark backgrounds (1st/2nd/3rd place)
    FIRST = '\033[93m'     # 1st place (bright yellow)
    SECOND = '\033[96m'    # 2nd place (bright cyan)
    THIRD = '\033[95m'     # 3rd place (bright magenta)
    RESET = '\033[0m'      # Reset to default

    @staticmethod
    def get_rank_color(rank: int) -> str:
        """
        Get ANSI color code for a given rank.

        Args:
            rank: 1 for 1st place, 2 for 2nd place, 3 for 3rd place

        Returns:
            ANSI color code string
        """
        if rank == 1:
            return ColorUtil.FIRST
        elif rank == 2:
            return ColorUtil.SECOND
        elif rank == 3:
            return ColorUtil.THIRD
        else:
            return ''

    @staticmethod
    def colorize(text: str, rank: int) -> str:
        """
        Wrap text in rank-based color codes.

        Args:
            text: Text to colorize
            rank: 1, 2, or 3 for rank-based coloring

        Returns:
            Colored text with ANSI codes
        """
        color = ColorUtil.get_rank_color(rank)
        if color:
            return f"{color}{text}{ColorUtil.RESET}"
        return text

    @staticmethod
    def get_rank_label(rank: int) -> str:
        """
        Get colorized rank label.

        Args:
            rank: 1, 2, or 3

        Returns:
            Colorized rank label like "(1st)", "(2nd)", "(3rd)"
        """
        labels = {
            1: "(1st)",
            2: "(2nd)",
            3: "(3rd)"
        }
        label = labels.get(rank, "")
        return ColorUtil.colorize(label, rank)
