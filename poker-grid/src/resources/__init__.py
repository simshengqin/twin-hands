"""
Custom Resource classes - extends Resource in Godot.
These represent data structures that can be saved as .tres files.
"""

from .card_resource import CardResource
from .hand_resource import HandResource
from .game_config_resource import GameConfigResource
from .grid_cell_resource import GridCellResource
from .deck_resource import DeckResource
from .game_state_resource import GameStateResource

__all__ = [
    "CardResource",
    "HandResource",
    "GameConfigResource",
    "GridCellResource",
    "DeckResource",
    "GameStateResource",
]
