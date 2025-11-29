"""
Competition analysis tools using Google Search.

This module provides tools for analyzing competitors, pricing,
and market entry barriers.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import google_search
import re


def extract_competitors(search_results: str, category: str) -> List[Dict[str, Any]]:
    """
    Extract competitor information from search results.

    Args:
        search_results: Raw search results
        category: Product category

    Returns:
        List of competitor information
    """
    results_lower = search_results.lower()

    # Common patterns for competitor mentions
    # Look for "brand" patterns
    brand_pattern = r'(?:brand|company|manufacturer|seller):\s*([A-Za-z][A-Za-z0-9\s]{2,20})'
    brand_matches = re.findall(brand_pattern, search_results, re.IGNORECASE)

    # Look for "best X brand" patterns
    best_brand_pattern = r'(?:best|top|leading|popular)\s+(?:\w+\s+)*brand[s]?\s*(?:include|are|like)?\s*:?\s*([A-Za-z][A-Za-z0-9\s,&]{5,100})'
    best_matches = re.findall(best_brand_pattern, search_results, re.IGNORECASE)

    # Common competitor names in various categories
    common_brands = {
        "blender": ["Ninja", "Vitamix", "NutriBullet", "Hamilton Beach", "Oster", "Blendtec", "KitchenAid"],
        "watch": ["Apple", "Samsung", "Fitbit", "Garmin", "Amazfit", "Fossil"],
        "headphone": ["Sony", "Bose", "Apple", "JBL", "Sennheiser", "Beats"],
        "default": ["Amazon Basics", "Generic", "Top Seller"]
    }

    competitors = []
    seen_brands = set()

    # Add brands from patterns
    for brand in brand_matches + best_matches:
        brand_clean = brand.strip()
        if len(brand_clean) > 2 and brand_clean.lower() not in seen_brands:
            seen_brands.add(brand_clean.lower())
            competitors.append({
                "name": brand_clean.title(),
                "source": "search",
                "market_share": None,
                "strength": "unknown"
            })

    # Add known brands if found in results
    category_lower = category.lower()
    brand_list = common_brands.get(category_lower, common_brands["default"])
    for brand in brand_list:
        if brand.lower() in results_lower and brand.lower() not in seen_brands:
            seen_brands.add(brand.lower())
            competitors.append({
                "name": brand,
                "source": "known_brand",
                "market_share": None,
                "strength": "established"
            })

    # Estimate relative market positions
    for i, comp in enumerate(competitors[:10]):
        if comp["market_share"] is None:
            comp["market_share"] = max(5, 30 - (i * 5))  # Rough estimate

    return competitors[:10]


def extract_pricing_data(search_results: str) -> Dict[str, Any]:
    """
    Extract pricing information from search results.

    Args:
        search_results: Raw search results

    Returns:
        Pricing analysis dictionary
    """
    # Pattern for prices
    price_pattern = r'\$\s*(\d+(?:\.\d{2})?)'
    prices = re.findall(price_pattern, search_results)

    price_values = [float(p) for p in prices if float(p) < 10000]  # Filter outliers

    if price_values:
        price_values.sort()
        min_price = price_values[0]
        max_price = price_values[-1]
        avg_price = sum(price_values) / len(price_values)
        median_price = price_values[len(price_values) // 2]
    else:
        min_price = 20.0
        max_price = 100.0
        avg_price = 50.0
        median_price = 45.0

    # Determine pricing strategy suggestions
    price_range = max_price - min_price
    if price_range > 100:
        strategy = "wide_range"
        recommendation = "Market has room for premium and budget positioning"
    elif avg_price > 50:
        strategy = "premium_dominant"
        recommendation = "Consider premium positioning with value differentiation"
    else:
        strategy = "competitive"
        recommendation = "Focus on value proposition and features"

    return {
        "min_price": round(min_price, 2),
        "max_price": round(max_price, 2),
        "avg_price": round(avg_price, 2),
        "median_price": round(median_price, 2),
        "price_range": round(price_range, 2),
        "strategy": strategy,
        "recommendation": recommendation,
        "sample_count": len(price_values)
    }


def identify_opportunities(
    search_results: str,
    competitors: List[Dict[str, Any]],
    pricing: Dict[str, Any]
) -> List[str]:
    """
    Identify market opportunities based on analysis.

    Args:
        search_results: Raw search results
        competitors: Competitor list
        pricing: Pricing analysis

    Returns:
        List of identified opportunities
    """
    results_lower = search_results.lower()
    opportunities = []

    # Gap analysis
    gap_indicators = [
        ("affordable", "Price-conscious segment underserved"),
        ("premium quality", "Premium segment has demand"),
        ("portable", "Portability is valued feature"),
        ("compact", "Space-saving designs in demand"),
        ("eco-friendly", "Sustainability-conscious consumers"),
        ("smart", "Smart/connected features desired"),
        ("quiet", "Noise reduction is valued"),
        ("easy to clean", "Convenience features important"),
        ("durable", "Quality and longevity valued"),
        ("fast", "Speed and efficiency important")
    ]

    for indicator, opportunity in gap_indicators:
        if indicator in results_lower:
            opportunities.append(opportunity)

    # Competition-based opportunities
    competitor_count = len(competitors)
    if competitor_count < 5:
        opportunities.append("Low competition - early mover advantage possible")
    elif competitor_count > 15:
        opportunities.append("Crowded market - differentiation critical")

    # Pricing-based opportunities
    avg_price = pricing.get("avg_price", 50)
    if avg_price > 75:
        opportunities.append("Budget segment may be underserved")
    if pricing.get("price_range", 0) < 30:
        opportunities.append("Narrow price range - innovation premium possible")

    return opportunities[:8]


def assess_entry_barriers(search_results: str, competitors: List[Dict[str, Any]]) -> str:
    """
    Assess market entry barriers.

    Args:
        search_results: Raw search results
        competitors: Competitor list

    Returns:
        Entry barrier level: low, medium, high
    """
    results_lower = search_results.lower()

    barrier_indicators = {
        "high": [
            "patent", "regulation", "certification required", "heavy investment",
            "established brands", "brand loyalty", "high capital"
        ],
        "medium": [
            "competitive", "saturated", "quality standards", "distribution",
            "marketing spend", "customer acquisition"
        ],
        "low": [
            "easy entry", "growing market", "fragmented", "low barrier",
            "new entrants", "opportunity"
        ]
    }

    scores = {"high": 0, "medium": 0, "low": 0}
    for level, keywords in barrier_indicators.items():
        scores[level] = sum(1 for kw in keywords if kw in results_lower)

    # Factor in competitor count
    competitor_count = len(competitors)
    if competitor_count > 10:
        scores["medium"] += 2
    if competitor_count > 20:
        scores["high"] += 1

    # Determine level
    if scores["high"] >= scores["medium"] and scores["high"] >= scores["low"]:
        return "high"
    elif scores["medium"] >= scores["low"]:
        return "medium"
    else:
        return "low"


def calculate_competition_score(
    competitors: List[Dict[str, Any]],
    pricing: Dict[str, Any],
    entry_barriers: str
) -> int:
    """
    Calculate competition intensity score.

    Higher score = more competitive (harder to enter)

    Args:
        competitors: Competitor list
        pricing: Pricing data
        entry_barriers: Entry barrier level

    Returns:
        Competition score 1-100
    """
    score = 50

    # Competitor count factor (0-25)
    comp_count = len(competitors)
    if comp_count > 15:
        score += 25
    elif comp_count > 10:
        score += 20
    elif comp_count > 5:
        score += 10
    else:
        score -= 10

    # Entry barrier factor (0-15)
    barrier_adjustments = {
        "high": 15,
        "medium": 5,
        "low": -10
    }
    score += barrier_adjustments.get(entry_barriers, 0)

    # Price competition factor
    price_range = pricing.get("price_range", 50)
    if price_range < 20:  # Tight pricing = high competition
        score += 10
    elif price_range > 100:  # Wide range = more room
        score -= 5

    return max(1, min(100, score))


async def search_competition_data(category: str, target_market: str) -> Dict[str, Any]:
    """
    Search for competition data using Google Search.

    Args:
        category: Product category to analyze
        target_market: Target market (country code)

    Returns:
        Dictionary with competition analysis results
    """
    queries = [
        f"best {category} brands {target_market} 2024",
        f"{category} price comparison review",
        f"{category} market competition analysis"
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

    # Extract competition data
    competitors = extract_competitors(combined_results, category)
    pricing = extract_pricing_data(combined_results)
    entry_barriers = assess_entry_barriers(combined_results, competitors)
    opportunities = identify_opportunities(combined_results, competitors, pricing)
    competition_score = calculate_competition_score(competitors, pricing, entry_barriers)

    return {
        "competitors": competitors,
        "competition_score": competition_score,
        "pricing_analysis": pricing,
        "opportunities": opportunities,
        "entry_barriers": entry_barriers,
        "raw_data": {
            "search_queries": queries,
            "results_preview": combined_results[:1000]
        }
    }


def format_competition_results(results: Dict[str, Any]) -> str:
    """
    Format competition analysis results for display.

    Args:
        results: Competition analysis results

    Returns:
        Formatted string
    """
    barrier_emoji = {
        "low": "🟢",
        "medium": "🟡",
        "high": "🔴"
    }

    pricing = results.get("pricing_analysis", {})

    output = f"""
## Competition Analysis Results

**Competition Score:** {results.get('competition_score', 'N/A')}/100 (higher = more competitive)
**Entry Barriers:** {barrier_emoji.get(results.get('entry_barriers', ''), '❓')} {results.get('entry_barriers', 'unknown').title()}

### Pricing Analysis
- **Range:** ${pricing.get('min_price', 0):.2f} - ${pricing.get('max_price', 0):.2f}
- **Average:** ${pricing.get('avg_price', 0):.2f}
- **Strategy:** {pricing.get('recommendation', 'N/A')}

### Top Competitors
"""
    for comp in results.get("competitors", [])[:5]:
        share = comp.get("market_share", "?")
        output += f"- {comp.get('name', 'Unknown')} (Est. {share}% share)\n"

    output += "\n### Opportunities\n"
    for opp in results.get("opportunities", [])[:5]:
        output += f"- {opp}\n"

    return output.strip()


def get_competition_tools() -> List[Dict[str, Any]]:
    """
    Get list of competition analysis tools for ADK agent registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "analyze_competition",
            "description": "Analyze competitors, pricing, and market entry barriers",
            "function": search_competition_data,
            "parameters": {
                "category": {"type": "string", "description": "Product category to analyze"},
                "target_market": {"type": "string", "description": "Target market country code"}
            }
        }
    ]
