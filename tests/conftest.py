"""
Pytest configuration and shared fixtures for Twin Hands
Designed to port easily to Godot GUT
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from src.resources.card_resource import CardResource
from src.resources.deck_resource import DeckResource
from src.utils.card_factory import CardFactory


@pytest.fixture
def sample_cards():
    """Sample cards for testing"""
    return {
        'ace_hearts': CardResource(rank='A', suit='H'),
        'ace_spades': CardResource(rank='A', suit='S'),
        'king_hearts': CardResource(rank='K', suit='H'),
        'queen_hearts': CardResource(rank='Q', suit='H'),
        'jack_hearts': CardResource(rank='J', suit='H'),
        'ten_hearts': CardResource(rank='T', suit='H'),
        'two_clubs': CardResource(rank='2', suit='C'),
        'two_diamonds': CardResource(rank='2', suit='D'),
        'three_clubs': CardResource(rank='3', suit='C'),
        'four_clubs': CardResource(rank='4', suit='C'),
        'five_clubs': CardResource(rank='5', suit='C'),
    }


@pytest.fixture
def empty_deck():
    """Empty DeckResource for testing"""
    return DeckResource(cards=[])


@pytest.fixture
def standard_deck():
    """Standard 52-card deck"""
    return CardFactory.create_deck_resource()


@pytest.fixture
def get_card():
    """Helper to create cards on demand"""
    def _get_card(rank: str, suit: str) -> CardResource:
        return CardResource(rank=rank, suit=suit)
    return _get_card
