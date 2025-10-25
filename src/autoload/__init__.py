"""
Autoload singletons - extends Node, added to AutoLoad in Godot.
These are globally accessible throughout the game.
"""

from .events import Events

__all__ = [
    "Events",
]
