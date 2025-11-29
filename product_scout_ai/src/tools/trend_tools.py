"""
Trend analysis tools using Google Trends data.

This module provides tools for analyzing product trends using
Google Search via the ADK's built-in google_search tool.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import google_search
import json
import re


def extract_trend_signals(search_results: str) -> Dict[str, Any]:
    """
    Extract trend signals from search results.

    Args:
        search_results: Raw search results from google_search

    Returns:
        Dictionary with extracted trend signals
    """
    # Parse search results for trend indicators
    results_lower = search_results.lower()

    # Trend direction signals
    rising_signals = ["growing", "increasing", "trending", "popular", "rising", "surge", "boom"]
    declining_signals = ["declining", "decreasing", "falling", "dropping", "slowing"]
    stable_signals = ["stable", "steady", "consistent", "flat"]

    rising_count = sum(1 for signal in rising_signals if signal in results_lower)
    declining_count = sum(1 for signal in declining_signals if signal in results_lower)
    stable_count = sum(1 for signal in stable_signals if signal in results_lower)

    if rising_count > declining_count and rising_count > stable_count:
        direction = "rising"
    elif declining_count > rising_count and declining_count > stable_count:
        direction = "declining"
    else:
        direction = "stable"

    # Extract growth percentages if mentioned
    growth_pattern = r'(\d+(?:\.\d+)?)\s*%?\s*(?:growth|increase|rise)'
    growth_matches = re.findall(growth_pattern, results_lower)
    growth_rates = [float(m) for m in growth_matches] if growth_matches else []

    return {
        "trend_direction": direction,
        "rising_signals": rising_count,
        "declining_signals": declining_count,
        "stable_signals": stable_count,
        "growth_rates": growth_rates,
        "raw_results": search_results[:2000]  # Truncate for storage
    }


def calculate_trend_score(signals: Dict[str, Any]) -> int:
    """
    Calculate trend score from extracted signals.

    Args:
        signals: Extracted trend signals

    Returns:
        Trend score from 1-100
    """
    base_score = 50

    # Adjust based on direction
    direction = signals.get("trend_direction", "stable")
    if direction == "rising":
        base_score += 20
    elif direction == "declining":
        base_score -= 20

    # Adjust based on signal strength
    rising = signals.get("rising_signals", 0)
    declining = signals.get("declining_signals", 0)
    net_signals = rising - declining
    base_score += min(max(net_signals * 5, -20), 20)

    # Adjust based on growth rates
    growth_rates = signals.get("growth_rates", [])
    if growth_rates:
        avg_growth = sum(growth_rates) / len(growth_rates)
        if avg_growth > 20:
            base_score += 10
        elif avg_growth > 10:
            base_score += 5

    # Clamp to valid range
    return max(1, min(100, base_score))


def extract_seasonality(search_results: str, category: str) -> Dict[str, Any]:
    """
    Extract seasonality patterns from search results.

    Args:
        search_results: Raw search results
        category: Product category

    Returns:
        Seasonality information
    """
    results_lower = search_results.lower()

    # Season keywords
    seasons = {
        "spring": ["spring", "march", "april", "may"],
        "summer": ["summer", "june", "july", "august", "hot weather"],
        "fall": ["fall", "autumn", "september", "october", "november"],
        "winter": ["winter", "december", "january", "february", "holiday", "christmas"]
    }

    peak_seasons = []
    for season, keywords in seasons.items():
        if any(kw in results_lower for kw in keywords):
            peak_seasons.append(season)

    # Month detection
    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]
    peak_months = [m for m in months if m in results_lower]

    return {
        "peak_seasons": peak_seasons if peak_seasons else ["year-round"],
        "peak_months": peak_months[:3] if peak_months else [],
        "is_seasonal": len(peak_seasons) < 4 and len(peak_seasons) > 0,
        "seasonality_notes": f"Based on analysis of {category}"
    }


def extract_related_queries(search_results: str, category: str) -> List[Dict[str, str]]:
    """
    Extract related search queries from results.

    Args:
        search_results: Raw search results
        category: Product category

    Returns:
        List of related queries with relevance scores
    """
    results_lower = search_results.lower()

    # Common product-related terms
    related_terms = [
        "best", "top", "review", "cheap", "affordable", "premium",
        "comparison", "vs", "alternative", "portable", "mini", "professional"
    ]

    found_queries = []
    for term in related_terms:
        if term in results_lower:
            found_queries.append({
                "query": f"{term} {category}",
                "relevance": "high" if results_lower.count(term) > 2 else "medium"
            })

    return found_queries[:10]  # Limit to 10 queries


async def search_trend_data(category: str, target_market: str) -> Dict[str, Any]:
    """
    Search for trend data using Google Search.

    This function uses the ADK's built-in google_search tool to find
    trend information about a product category.

    Args:
        category: Product category to analyze
        target_market: Target market (country code)

    Returns:
        Dictionary with trend analysis results
    """
    # Build search queries for trend analysis
    queries = [
        f"{category} market trends {target_market} 2024 2025",
        f"{category} popularity growth statistics",
        f"{category} consumer demand trends"
    ]

    all_results = []
    for query in queries:
        try:
            result = await google_search(query)
            if result:
                all_results.append(str(result))
        except Exception as e:
            all_results.append(f"Error searching: {str(e)}")

    combined_results = "\n".join(all_results)

    # Extract signals and calculate score
    signals = extract_trend_signals(combined_results)
    trend_score = calculate_trend_score(signals)
    seasonality = extract_seasonality(combined_results, category)
    related_queries = extract_related_queries(combined_results, category)

    return {
        "trend_score": trend_score,
        "trend_direction": signals["trend_direction"],
        "seasonality": seasonality,
        "related_queries": related_queries,
        "raw_data": {
            "signals": signals,
            "search_queries": queries
        }
    }


def format_trend_results(results: Dict[str, Any]) -> str:
    """
    Format trend results for display or agent consumption.

    Args:
        results: Trend analysis results

    Returns:
        Formatted string representation
    """
    direction_emoji = {
        "rising": "📈",
        "stable": "➡️",
        "declining": "📉"
    }

    emoji = direction_emoji.get(results.get("trend_direction", "stable"), "❓")

    output = f"""
## Trend Analysis Results

**Trend Score:** {results.get('trend_score', 'N/A')}/100
**Direction:** {emoji} {results.get('trend_direction', 'unknown').title()}

### Seasonality
- Peak Seasons: {', '.join(results.get('seasonality', {}).get('peak_seasons', ['N/A']))}
- Is Seasonal: {'Yes' if results.get('seasonality', {}).get('is_seasonal') else 'No'}

### Related Queries
"""
    for query in results.get("related_queries", [])[:5]:
        output += f"- {query.get('query', 'N/A')} ({query.get('relevance', 'N/A')})\n"

    return output.strip()


# Tool function for ADK agent registration
def get_trend_tools() -> List[Dict[str, Any]]:
    """
    Get list of trend analysis tools for ADK agent registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "analyze_trends",
            "description": "Analyze market trends for a product category using Google Search",
            "function": search_trend_data,
            "parameters": {
                "category": {"type": "string", "description": "Product category to analyze"},
                "target_market": {"type": "string", "description": "Target market country code"}
            }
        }
    ]
