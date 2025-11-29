"""
Market analysis tools using Google Search.

This module provides tools for analyzing market size, growth,
and customer segments.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import google_search
import re


def extract_market_size(search_results: str) -> Dict[str, float]:
    """
    Extract market size estimates from search results.

    Args:
        search_results: Raw search results

    Returns:
        Dictionary with TAM, SAM, SOM estimates
    """
    results_lower = search_results.lower()

    # Pattern for market size (e.g., "$1.5 billion", "2.3B USD")
    billion_pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*(?:b|billion)'
    million_pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*(?:m|million)'

    billions = re.findall(billion_pattern, results_lower)
    millions = re.findall(million_pattern, results_lower)

    # Convert to standardized values
    billion_values = [float(b) * 1_000_000_000 for b in billions]
    million_values = [float(m) * 1_000_000 for m in millions]

    all_values = billion_values + million_values
    all_values.sort(reverse=True)

    if len(all_values) >= 3:
        tam = all_values[0]
        sam = all_values[1]
        som = all_values[2]
    elif len(all_values) == 2:
        tam = all_values[0]
        sam = all_values[1]
        som = all_values[1] * 0.1
    elif len(all_values) == 1:
        tam = all_values[0]
        sam = tam * 0.3
        som = tam * 0.05
    else:
        # Default estimates
        tam = 10_000_000_000  # $10B default
        sam = 3_000_000_000
        som = 500_000_000

    return {
        "tam": tam,
        "sam": sam,
        "som": som,
        "currency": "USD"
    }


def extract_growth_rate(search_results: str) -> float:
    """
    Extract market growth rate from search results.

    Args:
        search_results: Raw search results

    Returns:
        Growth rate as decimal (e.g., 0.15 for 15%)
    """
    results_lower = search_results.lower()

    # Pattern for growth rates (e.g., "15% CAGR", "growing at 12%")
    cagr_pattern = r'(\d+(?:\.\d+)?)\s*%?\s*(?:cagr|compound annual growth)'
    growth_pattern = r'(?:grow(?:ing|th)?|increase|rise)\s*(?:of|at|by)?\s*(\d+(?:\.\d+)?)\s*%'

    cagr_matches = re.findall(cagr_pattern, results_lower)
    growth_matches = re.findall(growth_pattern, results_lower)

    all_rates = []
    for rate in cagr_matches + growth_matches:
        try:
            all_rates.append(float(rate))
        except ValueError:
            continue

    if all_rates:
        # Return average of found rates
        return sum(all_rates) / len(all_rates) / 100  # Convert to decimal
    else:
        return 0.10  # Default 10% growth


def determine_maturity_level(search_results: str) -> str:
    """
    Determine market maturity level from search results.

    Args:
        search_results: Raw search results

    Returns:
        Maturity level: emerging, growing, mature, declining
    """
    results_lower = search_results.lower()

    # Keywords for each maturity stage
    emerging_keywords = ["emerging", "new market", "nascent", "early stage", "startup"]
    growing_keywords = ["growing", "expanding", "rapid growth", "high growth", "growth stage"]
    mature_keywords = ["mature", "saturated", "established", "consolidating", "stable market"]
    declining_keywords = ["declining", "shrinking", "contracting", "disrupted"]

    scores = {
        "emerging": sum(1 for kw in emerging_keywords if kw in results_lower),
        "growing": sum(1 for kw in growing_keywords if kw in results_lower),
        "mature": sum(1 for kw in mature_keywords if kw in results_lower),
        "declining": sum(1 for kw in declining_keywords if kw in results_lower)
    }

    # Return stage with highest score, default to growing
    max_stage = max(scores, key=scores.get)
    return max_stage if scores[max_stage] > 0 else "growing"


def extract_customer_segments(search_results: str, category: str) -> List[Dict[str, Any]]:
    """
    Extract customer segment information from search results.

    Args:
        search_results: Raw search results
        category: Product category

    Returns:
        List of customer segments
    """
    results_lower = search_results.lower()

    # Common segment patterns
    segment_keywords = {
        "health_conscious": ["health", "fitness", "wellness", "healthy lifestyle"],
        "professionals": ["professional", "business", "office", "work"],
        "students": ["student", "college", "university", "young"],
        "families": ["family", "parent", "kids", "children"],
        "travelers": ["travel", "portable", "on-the-go", "commuter"],
        "budget_conscious": ["budget", "affordable", "cheap", "value"],
        "premium_buyers": ["premium", "luxury", "high-end", "quality"],
        "tech_savvy": ["smart", "tech", "connected", "digital"]
    }

    segments = []
    for segment_id, keywords in segment_keywords.items():
        keyword_count = sum(1 for kw in keywords if kw in results_lower)
        if keyword_count > 0:
            segments.append({
                "name": segment_id.replace("_", " ").title(),
                "relevance": "high" if keyword_count >= 2 else "medium",
                "keywords_found": keyword_count,
                "percentage": None  # To be estimated
            })

    # Estimate percentages
    total_relevance = sum(s["keywords_found"] for s in segments)
    if total_relevance > 0:
        for segment in segments:
            segment["percentage"] = round(segment["keywords_found"] / total_relevance * 100, 1)

    return segments[:6]  # Top 6 segments


def calculate_market_score(
    market_size: Dict[str, float],
    growth_rate: float,
    maturity: str
) -> int:
    """
    Calculate overall market score.

    Args:
        market_size: TAM/SAM/SOM values
        growth_rate: Market growth rate
        maturity: Market maturity level

    Returns:
        Market score from 1-100
    """
    score = 50

    # Size component (0-25 points)
    som = market_size.get("som", 0)
    if som > 1_000_000_000:  # $1B+
        score += 25
    elif som > 500_000_000:  # $500M+
        score += 20
    elif som > 100_000_000:  # $100M+
        score += 15
    elif som > 10_000_000:  # $10M+
        score += 10
    else:
        score += 5

    # Growth component (0-25 points)
    if growth_rate > 0.20:  # 20%+
        score += 25
    elif growth_rate > 0.15:  # 15%+
        score += 20
    elif growth_rate > 0.10:  # 10%+
        score += 15
    elif growth_rate > 0.05:  # 5%+
        score += 10
    else:
        score += 5

    # Maturity component (-10 to +10)
    maturity_adjustments = {
        "emerging": 5,
        "growing": 10,
        "mature": 0,
        "declining": -10
    }
    score += maturity_adjustments.get(maturity, 0)

    return max(1, min(100, score))


async def search_market_data(category: str, target_market: str) -> Dict[str, Any]:
    """
    Search for market data using Google Search.

    Args:
        category: Product category to analyze
        target_market: Target market (country code)

    Returns:
        Dictionary with market analysis results
    """
    # Build search queries
    queries = [
        f"{category} market size {target_market} 2024 2025 billion",
        f"{category} market growth rate CAGR",
        f"{category} target customer demographics segments"
    ]

    all_results = []
    for query in queries:
        try:
            result = await google_search(query)
            if result:
                all_results.append(str(result))
        except Exception as e:
            all_results.append(f"Error: {str(e)}")

    combined_results = "\n".join(all_results)

    # Extract market data
    market_size = extract_market_size(combined_results)
    growth_rate = extract_growth_rate(combined_results)
    maturity = determine_maturity_level(combined_results)
    segments = extract_customer_segments(combined_results, category)
    market_score = calculate_market_score(market_size, growth_rate, maturity)

    return {
        "market_size": market_size,
        "growth_rate": growth_rate,
        "customer_segments": segments,
        "maturity_level": maturity,
        "market_score": market_score,
        "raw_data": {
            "search_queries": queries,
            "results_preview": combined_results[:1000]
        }
    }


def format_market_results(results: Dict[str, Any]) -> str:
    """
    Format market analysis results for display.

    Args:
        results: Market analysis results

    Returns:
        Formatted string
    """
    market_size = results.get("market_size", {})

    def format_currency(value: float) -> str:
        if value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        else:
            return f"${value:,.0f}"

    maturity_emoji = {
        "emerging": "🌱",
        "growing": "📈",
        "mature": "🏢",
        "declining": "📉"
    }

    output = f"""
## Market Analysis Results

**Market Score:** {results.get('market_score', 'N/A')}/100

### Market Size
- **TAM:** {format_currency(market_size.get('tam', 0))}
- **SAM:** {format_currency(market_size.get('sam', 0))}
- **SOM:** {format_currency(market_size.get('som', 0))}

### Growth & Maturity
- **Growth Rate:** {results.get('growth_rate', 0) * 100:.1f}%
- **Maturity:** {maturity_emoji.get(results.get('maturity_level', ''), '❓')} {results.get('maturity_level', 'unknown').title()}

### Customer Segments
"""
    for segment in results.get("customer_segments", [])[:5]:
        pct = segment.get("percentage")
        pct_str = f" ({pct}%)" if pct else ""
        output += f"- {segment.get('name', 'Unknown')}{pct_str}\n"

    return output.strip()


def get_market_tools() -> List[Dict[str, Any]]:
    """
    Get list of market analysis tools for ADK agent registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "analyze_market",
            "description": "Analyze market size, growth, and customer segments for a product category",
            "function": search_market_data,
            "parameters": {
                "category": {"type": "string", "description": "Product category to analyze"},
                "target_market": {"type": "string", "description": "Target market country code"}
            }
        }
    ]
