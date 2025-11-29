"""
Theme configuration for the UI.

This module provides custom CSS and theme colors.
"""
from typing import Dict

# Color palette
THEME_COLORS: Dict[str, str] = {
    # Score colors
    "score_high": "#22c55e",      # Green
    "score_medium": "#eab308",    # Yellow
    "score_low": "#ef4444",       # Red

    # Recommendation colors
    "go": "#22c55e",              # Green
    "cautious": "#f59e0b",        # Orange
    "no_go": "#ef4444",           # Red

    # Chart colors
    "primary": "#3b82f6",         # Blue
    "secondary": "#8b5cf6",       # Purple
    "accent": "#06b6d4",          # Cyan

    # Background colors
    "bg_light": "#f8fafc",        # Light gray
    "bg_card": "#ffffff",         # White
    "bg_highlight": "#f0f9ff",    # Light blue

    # Text colors
    "text_primary": "#1e293b",    # Dark gray
    "text_secondary": "#64748b",  # Medium gray
    "text_muted": "#94a3b8",      # Light gray

    # Border colors
    "border": "#e2e8f0",          # Light border
    "border_focus": "#3b82f6",    # Blue focus
}


def get_custom_css() -> str:
    """
    Get custom CSS for the Gradio application.

    Returns:
        CSS string
    """
    return """
    /* Global styles */
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }

    /* Header styling */
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1rem;
        color: #64748b;
    }

    /* Score card styling */
    .score-card {
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        transition: transform 0.2s;
    }

    .score-card:hover {
        transform: translateY(-2px);
    }

    .score-card-high {
        background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
        border: 1px solid #86efac;
    }

    .score-card-medium {
        background: linear-gradient(135deg, #fef9c3 0%, #fef08a 100%);
        border: 1px solid #fde047;
    }

    .score-card-low {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #fca5a5;
    }

    .score-value {
        font-size: 2.5rem;
        font-weight: 700;
        line-height: 1;
    }

    .score-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Recommendation badge */
    .recommendation-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 1.25rem;
    }

    .recommendation-go {
        background-color: #dcfce7;
        color: #166534;
    }

    .recommendation-cautious {
        background-color: #fef3c7;
        color: #92400e;
    }

    .recommendation-no-go {
        background-color: #fee2e2;
        color: #991b1b;
    }

    /* Analysis section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1rem;
    }

    /* Progress indicator */
    .progress-phase {
        font-size: 1rem;
        color: #3b82f6;
        font-weight: 500;
    }

    /* Data table styling */
    .history-table {
        font-size: 0.875rem;
    }

    .history-table th {
        background-color: #f8fafc;
        font-weight: 600;
    }

    /* Button styling */
    .primary-btn {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        color: white;
        font-weight: 600;
    }

    .primary-btn:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    }

    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 0.75rem;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* SWOT grid */
    .swot-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }

    .swot-item {
        padding: 1rem;
        border-radius: 0.5rem;
    }

    .swot-strengths {
        background-color: #dcfce7;
        border-left: 4px solid #22c55e;
    }

    .swot-weaknesses {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
    }

    .swot-opportunities {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
    }

    .swot-threats {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
    }

    /* Tab styling */
    .tab-nav button {
        font-weight: 500;
    }

    .tab-nav button.selected {
        border-bottom-color: #3b82f6;
        color: #3b82f6;
    }

    /* Statistics cards */
    .stat-card {
        background: white;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }

    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }

    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    """


def get_score_class(score: int) -> str:
    """
    Get CSS class based on score value.

    Args:
        score: Score value (1-100)

    Returns:
        CSS class name
    """
    if score >= 70:
        return "score-card-high"
    elif score >= 50:
        return "score-card-medium"
    else:
        return "score-card-low"


def get_recommendation_class(recommendation: str) -> str:
    """
    Get CSS class for recommendation badge.

    Args:
        recommendation: Recommendation string

    Returns:
        CSS class name
    """
    classes = {
        "go": "recommendation-go",
        "cautious": "recommendation-cautious",
        "no-go": "recommendation-no-go",
    }
    return classes.get(recommendation.lower(), "")
