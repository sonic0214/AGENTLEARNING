"""
Formatting utilities for the UI.

This module provides functions for formatting data for display.
"""
from typing import Optional
from datetime import datetime


def format_number(value: float, precision: int = 0) -> str:
    """
    Format a number with thousand separators.

    Args:
        value: Number to format
        precision: Decimal places

    Returns:
        Formatted string
    """
    if precision == 0:
        return f"{int(value):,}"
    return f"{value:,.{precision}f}"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format a decimal as percentage.

    Args:
        value: Decimal value (0.25 = 25%)
        precision: Decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{precision}f}%"


def format_currency(value: float, currency: str = "USD", precision: int = 0) -> str:
    """
    Format a number as currency.

    Args:
        value: Amount
        currency: Currency code
        precision: Decimal places

    Returns:
        Formatted currency string
    """
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
    }
    symbol = symbols.get(currency, currency + " ")

    if precision == 0:
        return f"{symbol}{int(value):,}"
    return f"{symbol}{value:,.{precision}f}"


def format_timestamp(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object.

    Args:
        dt: Datetime object (uses current time if None)
        format_str: Format string

    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_market_size(value: float) -> str:
    """
    Format market size with appropriate suffix.

    Args:
        value: Market size value

    Returns:
        Formatted string with B/M/K suffix
    """
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.1f}K"
    else:
        return f"${value:.0f}"


def format_score_label(score: int) -> str:
    """
    Get descriptive label for a score.

    Args:
        score: Score value (1-100)

    Returns:
        Descriptive label
    """
    if score >= 80:
        return "优秀"
    elif score >= 70:
        return "良好"
    elif score >= 60:
        return "中等"
    elif score >= 40:
        return "一般"
    else:
        return "较差"


def format_score(score: int, max_score: int = 100) -> str:
    """
    Format a score as fraction.

    Args:
        score: Score value
        max_score: Maximum score

    Returns:
        Formatted score string (e.g., "85/100")
    """
    return f"{score}/{max_score}"


def format_trend_direction(direction: str) -> str:
    """
    Format trend direction with emoji.

    Args:
        direction: Trend direction string

    Returns:
        Direction with emoji
    """
    directions = {
        "rising": "📈 上升",
        "stable": "➡️ 稳定",
        "declining": "📉 下降",
    }
    return directions.get(direction.lower(), direction)


def format_recommendation(recommendation: str) -> str:
    """
    Format recommendation with styling.

    Args:
        recommendation: Recommendation string (go/cautious/no-go)

    Returns:
        Formatted recommendation
    """
    recommendations = {
        "go": "✅ 推荐进入",
        "cautious": "⚠️ 谨慎考虑",
        "no-go": "❌ 不建议",
    }
    return recommendations.get(recommendation.lower(), recommendation)
