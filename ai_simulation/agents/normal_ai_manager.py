"""
Normal AI Manager
Heuristic AI to mimic an average player.
Fair: reads only public state.
"""

from typing import List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.resources.game_state_resource import GameStateResource
    from src.resources.game_config_resource import GameConfigResource
    from src.managers.joker_manager import JokerManager
    from src.resources.card_resource import CardResource


class NormalAIManager:
    """
    Average-behavior AI:
    - Freeze aligned highest pair; else two highest same-suit; else no freeze.
    - In shop: buy affordable simple multipliers/chips if slot available.
    """

    def __init__(self, state: 'GameStateResource', config: 'GameConfigResource', joker_manager: Optional['JokerManager'] = None):
        self.state = state
        self.config = config
        self.joker_manager = joker_manager

    def recommend_freezes(self, max_to_freeze: int = 2) -> List[Tuple[int, int]]:
        """
        Recommend up to N cells to freeze based on simple heuristics.
        Returns list of (row, col).
        """
        # Gather all cards
        cards = []
        for r in range(self.config.grid_rows):
            for c in range(self.config.grid_cols):
                cell = self.state.grid[r][c]
                if cell.card:
                    cards.append((cell.card, r, c))

        # 1) Aligned best pair
        aligned = self._find_best_aligned_pair(cards)
        if aligned:
            return aligned[:max_to_freeze]

        # 2) Two highest same suit
        suited = self._find_best_suited(cards)
        if suited:
            return suited[:max_to_freeze]

        return []

    def _find_best_aligned_pair(self, all_cards: List[Tuple['CardResource', int, int]]) -> Optional[List[Tuple[int, int]]]:
        positions_by_rank = {}
        for card, r, c in all_cards:
            positions_by_rank.setdefault(card.rank, []).append((r, c))

        best = None
        best_val = -1
        for rank, positions in positions_by_rank.items():
            if len(positions) < 2:
                continue
            for i in range(len(positions)):
                for j in range(i + 1, len(positions)):
                    (r1, c1), (r2, c2) = positions[i], positions[j]
                    if r1 == r2 or c1 == c2:
                        val = self.config.RANK_VALUES[rank]
                        if val > best_val:
                            best_val = val
                            best = [(r1, c1), (r2, c2)]
        return best

    def _find_best_suited(self, all_cards: List[Tuple['CardResource', int, int]]) -> Optional[List[Tuple[int, int]]]:
        # Pick top 2 by rank of same suit
        by_suit = {}
        for card, r, c in all_cards:
            by_suit.setdefault(card.suit, []).append((card, r, c))

        best = None
        best_val = -1
        for suit, items in by_suit.items():
            if len(items) < 2:
                continue
            # sort by rank value desc
            items.sort(key=lambda t: self.config.RANK_VALUES[t[0].rank], reverse=True)
            top_two = items[:2]
            val = sum(self.config.RANK_VALUES[t[0].rank] for t in top_two)
            if val > best_val:
                best_val = val
                best = [(top_two[0][1], top_two[0][2]), (top_two[1][1], top_two[1][2])]
        return best

    def recommend_shop_action(self, shop_display: List[dict], reroll_cost: int) -> Tuple[str, int]:
        """
        Recommend a single shop action.
        Returns (action, index) like ('buy', i), ('reroll', -1), or ('none', -1)
        """
        if not self.joker_manager:
            return ("none", -1)

        # Buy first affordable +m or +c with open slot
        if self.joker_manager.has_empty_slot():
            for item in shop_display:
                j = item.get('joker')
                if not j:
                    continue
                if j.bonus_type in ('+m', '+c') and self.state.can_afford(j.cost):
                    return ("buy", item['index'])

        # Otherwise consider reroll if affordable
        if self.state.can_afford(reroll_cost):
            return ("reroll", -1)

        return ("none", -1)

    # Backwards-compat convenience: wrap single action in a list if present
    def recommend_shop_actions(self, shop_display: List[dict]) -> List[Tuple[str, int]]:
        action, idx = self.recommend_shop_action(shop_display, reroll_cost=5)
        return [(action, idx)] if action != "none" else []

