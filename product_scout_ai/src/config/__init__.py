"""Configuration module"""
from .settings import settings, Settings
from .prompts import (
    TREND_AGENT_INSTRUCTION,
    MARKET_AGENT_INSTRUCTION,
    COMPETITION_AGENT_INSTRUCTION,
    PROFIT_AGENT_INSTRUCTION,
    EVALUATOR_AGENT_INSTRUCTION,
    REPORT_AGENT_INSTRUCTION,
    format_prompt,
)

__all__ = [
    "settings",
    "Settings",
    "TREND_AGENT_INSTRUCTION",
    "MARKET_AGENT_INSTRUCTION",
    "COMPETITION_AGENT_INSTRUCTION",
    "PROFIT_AGENT_INSTRUCTION",
    "EVALUATOR_AGENT_INSTRUCTION",
    "REPORT_AGENT_INSTRUCTION",
    "format_prompt",
]
