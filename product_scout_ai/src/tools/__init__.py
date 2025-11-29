"""
Tools package for ProductScout AI.

This package contains all custom tools used by the analysis agents.
"""
from .trend_tools import (
    search_trend_data,
    extract_trend_signals,
    calculate_trend_score,
    extract_seasonality,
    extract_related_queries,
    format_trend_results,
    get_trend_tools,
)

from .market_tools import (
    search_market_data,
    extract_market_size,
    extract_growth_rate,
    determine_maturity_level,
    extract_customer_segments,
    calculate_market_score,
    format_market_results,
    get_market_tools,
)

from .competition_tools import (
    search_competition_data,
    extract_competitors,
    extract_pricing_data,
    identify_opportunities,
    assess_entry_barriers,
    calculate_competition_score,
    format_competition_results,
    get_competition_tools,
)

from .profit_tools import (
    search_profit_data,
    calculate_unit_economics,
    calculate_margins,
    calculate_monthly_projection,
    calculate_investment_requirements,
    calculate_roi_metrics,
    calculate_profit_score,
    format_profit_results,
    get_profit_tools,
    COST_STRUCTURES,
    BUDGET_RANGES,
)

__all__ = [
    # Trend tools
    "search_trend_data",
    "extract_trend_signals",
    "calculate_trend_score",
    "extract_seasonality",
    "extract_related_queries",
    "format_trend_results",
    "get_trend_tools",
    # Market tools
    "search_market_data",
    "extract_market_size",
    "extract_growth_rate",
    "determine_maturity_level",
    "extract_customer_segments",
    "calculate_market_score",
    "format_market_results",
    "get_market_tools",
    # Competition tools
    "search_competition_data",
    "extract_competitors",
    "extract_pricing_data",
    "identify_opportunities",
    "assess_entry_barriers",
    "calculate_competition_score",
    "format_competition_results",
    "get_competition_tools",
    # Profit tools
    "search_profit_data",
    "calculate_unit_economics",
    "calculate_margins",
    "calculate_monthly_projection",
    "calculate_investment_requirements",
    "calculate_roi_metrics",
    "calculate_profit_score",
    "format_profit_results",
    "get_profit_tools",
    "COST_STRUCTURES",
    "BUDGET_RANGES",
]
