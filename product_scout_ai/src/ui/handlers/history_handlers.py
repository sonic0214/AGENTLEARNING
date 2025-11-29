"""
History handlers for the UI.

This module provides event handlers for history operations.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd

from src.services.history_service import create_history_service


# Global history service instance
_history_service = None


def get_history_service():
    """Get or create history service instance."""
    global _history_service
    if _history_service is None:
        _history_service = create_history_service()
    return _history_service


def get_history_dataframe(
    category_filter: str = "",
    market_filter: str = "全部",
    success_only: bool = False
) -> pd.DataFrame:
    """
    Get history entries as DataFrame for display.

    Args:
        category_filter: Filter by category (partial match)
        market_filter: Filter by market
        success_only: Only show successful analyses

    Returns:
        DataFrame with history entries
    """
    history = get_history_service()

    # Get entries with filters
    entries = history.search(
        category=category_filter if category_filter else None,
        market=market_filter if market_filter != "全部" else None,
        success_only=success_only
    )

    # Convert to list of dicts for DataFrame
    data = []
    for entry in entries:
        if entry.request:
            # Get score from state if available
            score = 0
            recommendation = "N/A"
            if entry.state and entry.state.evaluation_result:
                score = entry.state.evaluation_result.opportunity_score
                recommendation = entry.state.evaluation_result.recommendation

            data.append({
                "日期": entry.timestamp.strftime("%Y-%m-%d %H:%M") if hasattr(entry, 'timestamp') else "N/A",
                "产品类别": entry.request.category,
                "市场": entry.request.target_market,
                "模式": entry.request.business_model,
                "评分": score,
                "建议": recommendation.upper() if recommendation else "N/A",
                "耗时": f"{entry.execution_time:.1f}s" if entry.execution_time else "N/A",
                "状态": "✅ 成功" if entry.success else "❌ 失败",
            })

    if not data:
        return pd.DataFrame(columns=[
            "日期", "产品类别", "市场", "模式", "评分", "建议", "耗时", "状态"
        ])

    return pd.DataFrame(data)


def get_history_statistics() -> Dict[str, Any]:
    """
    Get history statistics.

    Returns:
        Dictionary with statistics
    """
    history = get_history_service()
    stats = history.get_statistics()

    return {
        "total": stats.get("total_analyses", 0),
        "successful": stats.get("successful", 0),
        "failed": stats.get("failed", 0),
        "success_rate": stats.get("success_rate", 0),
        "avg_time": stats.get("average_execution_time", 0),
        "categories": stats.get("categories", {}),
        "markets": stats.get("markets", {}),
    }


def search_history(
    category: str = "",
    market: str = "全部",
    success_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Search history with filters.

    Args:
        category: Category filter
        market: Market filter
        success_only: Only successful analyses

    Returns:
        List of matching history entries
    """
    history = get_history_service()

    entries = history.search(
        category=category if category else None,
        market=market if market != "全部" else None,
        success_only=success_only
    )

    results = []
    for entry in entries:
        result_dict = {
            "timestamp": entry.timestamp.isoformat() if hasattr(entry, 'timestamp') else None,
            "request": None,
            "success": entry.success,
            "execution_time": entry.execution_time,
        }

        if entry.request:
            result_dict["request"] = {
                "category": entry.request.category,
                "target_market": entry.request.target_market,
                "budget_range": entry.request.budget_range,
                "business_model": entry.request.business_model,
            }

        if entry.state:
            result_dict["state"] = {
                "evaluation_result": None
            }
            if entry.state.evaluation_result:
                result_dict["state"]["evaluation_result"] = {
                    "opportunity_score": entry.state.evaluation_result.opportunity_score,
                    "recommendation": entry.state.evaluation_result.recommendation,
                }

        results.append(result_dict)

    return results


def get_history_for_dropdown() -> List[str]:
    """
    Get history entries formatted for dropdown selection.

    Returns:
        List of formatted strings for dropdown
    """
    history = get_history_service()
    entries = history.get_recent(limit=50)

    options = []
    for i, entry in enumerate(entries):
        if entry.request:
            category = entry.request.category
            market = entry.request.target_market
            date = entry.timestamp.strftime("%m/%d %H:%M") if hasattr(entry, 'timestamp') else "N/A"
            score = 0
            if entry.state and entry.state.evaluation_result:
                score = entry.state.evaluation_result.opportunity_score

            label = f"[{date}] {category} ({market}) - 评分: {score}"
            options.append(label)

    return options


def add_to_history(
    request,
    state,
    success: bool,
    execution_time: float
) -> None:
    """
    Add a new entry to history.

    Args:
        request: Analysis request object
        state: Analysis state with results
        success: Whether analysis succeeded
        execution_time: Time taken in seconds
    """
    history = get_history_service()
    history.add_entry(
        request=request,
        state=state,
        success=success,
        execution_time=execution_time
    )


def clear_history() -> int:
    """
    Clear all history entries.

    Returns:
        Number of entries cleared
    """
    history = get_history_service()
    return history.clear()


def get_entry_by_index(index: int) -> Optional[Dict[str, Any]]:
    """
    Get a specific history entry by index.

    Args:
        index: Entry index (0-based)

    Returns:
        Entry data or None
    """
    history = get_history_service()
    entries = history.get_recent(limit=50)

    if 0 <= index < len(entries):
        entry = entries[index]
        return {
            "request": entry.request,
            "state": entry.state,
            "success": entry.success,
            "execution_time": entry.execution_time,
            "timestamp": entry.timestamp if hasattr(entry, 'timestamp') else None,
        }

    return None
