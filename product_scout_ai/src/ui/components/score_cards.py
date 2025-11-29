"""
Score card components for the UI.

This module provides functions for score display styling.
"""
from typing import Tuple

from ..utils.theme import THEME_COLORS


def get_score_color(score: int) -> str:
    """
    Get color based on score value.

    Args:
        score: Score value (1-100)

    Returns:
        Hex color string
    """
    if score >= 70:
        return THEME_COLORS["score_high"]
    elif score >= 50:
        return THEME_COLORS["score_medium"]
    else:
        return THEME_COLORS["score_low"]


def get_recommendation_style(recommendation: str) -> Tuple[str, str, str]:
    """
    Get styling for recommendation display.

    Args:
        recommendation: Recommendation string (go/cautious/no-go)

    Returns:
        Tuple of (color, emoji, text)
    """
    styles = {
        "go": (THEME_COLORS["go"], "✅", "推荐进入"),
        "cautious": (THEME_COLORS["cautious"], "⚠️", "谨慎考虑"),
        "no-go": (THEME_COLORS["no_go"], "❌", "不建议"),
    }
    return styles.get(recommendation.lower(), ("#6b7280", "❓", "未知"))


def format_score_display(score: int, label: str) -> str:
    """
    Format a score for HTML display.

    Args:
        score: Score value
        label: Score label

    Returns:
        HTML string for score display
    """
    color = get_score_color(score)

    return f"""
<div style="text-align: center; padding: 1rem;">
    <div style="font-size: 2.5rem; font-weight: 700; color: {color};">{score}</div>
    <div style="font-size: 0.875rem; color: #64748b; margin-top: 0.25rem;">{label}</div>
</div>
"""


def format_score_card(
    score: int,
    title: str,
    subtitle: str = "",
    show_bar: bool = True
) -> str:
    """
    Format a complete score card as HTML.

    Args:
        score: Score value
        title: Card title
        subtitle: Optional subtitle
        show_bar: Whether to show progress bar

    Returns:
        HTML string for score card
    """
    color = get_score_color(score)

    bar_html = ""
    if show_bar:
        bar_html = f"""
<div style="
    width: 100%;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    margin-top: 0.75rem;
    overflow: hidden;
">
    <div style="
        width: {score}%;
        height: 100%;
        background: {color};
        border-radius: 4px;
        transition: width 0.5s ease;
    "></div>
</div>
"""

    subtitle_html = ""
    if subtitle:
        subtitle_html = f'<div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem;">{subtitle}</div>'

    return f"""
<div style="
    background: white;
    border-radius: 0.75rem;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid #e2e8f0;
">
    <div style="font-size: 0.875rem; font-weight: 500; color: #64748b;">{title}</div>
    <div style="font-size: 2rem; font-weight: 700; color: {color}; margin-top: 0.5rem;">{score}</div>
    {subtitle_html}
    {bar_html}
</div>
"""


def format_recommendation_badge(recommendation: str, detail: str = "") -> str:
    """
    Format recommendation as HTML badge.

    Args:
        recommendation: Recommendation string
        detail: Optional detail text

    Returns:
        HTML string for recommendation badge
    """
    color, emoji, text = get_recommendation_style(recommendation)

    # Background color with opacity
    if recommendation.lower() == "go":
        bg_color = "#dcfce7"
        text_color = "#166534"
    elif recommendation.lower() == "cautious":
        bg_color = "#fef3c7"
        text_color = "#92400e"
    else:
        bg_color = "#fee2e2"
        text_color = "#991b1b"

    detail_html = ""
    if detail:
        detail_html = f'<div style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">{detail}</div>'

    return f"""
<div style="text-align: center; padding: 1rem;">
    <div style="
        display: inline-block;
        padding: 0.75rem 2rem;
        border-radius: 9999px;
        background: {bg_color};
        color: {text_color};
        font-weight: 600;
        font-size: 1.25rem;
    ">
        {emoji} {text}
    </div>
    {detail_html}
</div>
"""


def format_dimension_scores(scores: dict) -> str:
    """
    Format dimension scores as HTML grid.

    Args:
        scores: Dictionary of dimension names to scores

    Returns:
        HTML string for scores grid
    """
    cards_html = ""
    for name, score in scores.items():
        color = get_score_color(score)
        cards_html += f"""
<div style="
    background: white;
    border-radius: 0.5rem;
    padding: 1rem;
    text-align: center;
    border: 1px solid #e2e8f0;
">
    <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">{name}</div>
    <div style="font-size: 1.5rem; font-weight: 700; color: {color}; margin-top: 0.25rem;">{score}</div>
</div>
"""

    return f"""
<div style="
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
">
    {cards_html}
</div>
"""


def format_overall_score(score: int, recommendation: str, detail: str = "") -> str:
    """
    Format overall score section as HTML.

    Args:
        score: Overall opportunity score
        recommendation: Recommendation string
        detail: Optional detail text

    Returns:
        HTML string for overall score section
    """
    score_color = get_score_color(score)
    rec_color, rec_emoji, rec_text = get_recommendation_style(recommendation)

    if recommendation.lower() == "go":
        rec_bg = "#dcfce7"
    elif recommendation.lower() == "cautious":
        rec_bg = "#fef3c7"
    else:
        rec_bg = "#fee2e2"

    return f"""
<div style="
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    border-radius: 1rem;
    padding: 2rem;
    text-align: center;
    border: 1px solid #e2e8f0;
">
    <div style="font-size: 0.875rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
        机会评分
    </div>
    <div style="
        font-size: 4rem;
        font-weight: 800;
        color: {score_color};
        line-height: 1;
        margin: 0.5rem 0;
    ">
        {score}
    </div>
    <div style="font-size: 0.875rem; color: #94a3b8; margin-bottom: 1rem;">满分 100</div>

    <div style="
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 9999px;
        background: {rec_bg};
        color: {rec_color};
        font-weight: 600;
        font-size: 1rem;
    ">
        {rec_emoji} {rec_text}
    </div>

    {f'<div style="font-size: 0.875rem; color: #64748b; margin-top: 1rem; max-width: 400px; margin-left: auto; margin-right: auto;">{detail}</div>' if detail else ''}
</div>
"""
