"""
AI Simulation package
Agents, utilities, and scripts for AI experiments (outside src/).
"""

from .utils.ai_evaluator import AIEvaluator
from .agents.normal_ai_manager import NormalAIManager
from .agents.smart_ai_manager import SmartAIManager

__all__ = [
    "AIEvaluator",
    "NormalAIManager",
    "SmartAIManager",
]
