"""
Profit analysis tools for unit economics and ROI calculations.

This module provides tools for analyzing profitability,
unit economics, and investment requirements.
"""
from typing import Dict, Any, List, Optional
from google.adk.tools import google_search
import re


# Cost structure constants by business model
COST_STRUCTURES = {
    "amazon_fba": {
        "fulfillment_fee_percent": 0.15,  # ~15% FBA fees
        "referral_fee_percent": 0.15,  # ~15% referral
        "storage_fee_monthly": 0.50,  # per unit
        "advertising_percent": 0.10,  # 10% PPC
        "returns_percent": 0.05,  # 5% returns
    },
    "dropshipping": {
        "platform_fee_percent": 0.03,  # Payment processing
        "advertising_percent": 0.20,  # Higher ad spend
        "returns_percent": 0.08,  # Higher returns
        "shipping_cost": 5.00,  # Per unit shipping
    },
    "private_label": {
        "manufacturing_multiplier": 0.25,  # 25% of retail as COGS
        "shipping_percent": 0.10,
        "marketing_percent": 0.15,
        "overhead_percent": 0.05,
    },
    "wholesale": {
        "wholesale_discount": 0.50,  # Buy at 50% of retail
        "fulfillment_percent": 0.10,
        "marketing_percent": 0.08,
        "overhead_percent": 0.05,
    }
}

# Budget range configurations
BUDGET_RANGES = {
    "low": {"min": 1000, "max": 5000, "units_target": 100},
    "medium": {"min": 5000, "max": 20000, "units_target": 500},
    "high": {"min": 20000, "max": 100000, "units_target": 2000},
}


def extract_cost_data(search_results: str, category: str) -> Dict[str, float]:
    """
    Extract cost data from search results.

    Args:
        search_results: Raw search results
        category: Product category

    Returns:
        Dictionary with cost estimates
    """
    results_lower = search_results.lower()

    # Extract manufacturing/wholesale costs
    cost_pattern = r'(?:cost|wholesale|manufacturing).*?\$\s*(\d+(?:\.\d{2})?)'
    cost_matches = re.findall(cost_pattern, results_lower)

    # Extract shipping costs
    shipping_pattern = r'(?:shipping|freight).*?\$\s*(\d+(?:\.\d{2})?)'
    shipping_matches = re.findall(shipping_pattern, results_lower)

    costs = [float(c) for c in cost_matches if float(c) < 500]
    shipping = [float(s) for s in shipping_matches if float(s) < 100]

    return {
        "estimated_cogs": sum(costs) / len(costs) if costs else 15.00,
        "estimated_shipping": sum(shipping) / len(shipping) if shipping else 5.00,
        "sample_count": len(costs)
    }


def calculate_unit_economics(
    retail_price: float,
    business_model: str,
    cost_data: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate unit economics for a product.

    Args:
        retail_price: Selling price
        business_model: Business model type
        cost_data: Extracted cost data

    Returns:
        Unit economics breakdown
    """
    structure = COST_STRUCTURES.get(business_model, COST_STRUCTURES["amazon_fba"])
    cogs = cost_data.get("estimated_cogs", retail_price * 0.25)
    shipping = cost_data.get("estimated_shipping", 5.00)

    if business_model == "amazon_fba":
        fulfillment_fee = retail_price * structure["fulfillment_fee_percent"]
        referral_fee = retail_price * structure["referral_fee_percent"]
        storage_fee = structure["storage_fee_monthly"]
        advertising = retail_price * structure["advertising_percent"]
        returns_cost = retail_price * structure["returns_percent"]

        total_costs = cogs + shipping + fulfillment_fee + referral_fee + storage_fee + advertising + returns_cost
        profit_per_unit = retail_price - total_costs

        return {
            "retail_price": retail_price,
            "cogs": round(cogs, 2),
            "shipping": round(shipping, 2),
            "fulfillment_fee": round(fulfillment_fee, 2),
            "referral_fee": round(referral_fee, 2),
            "storage_fee": round(storage_fee, 2),
            "advertising": round(advertising, 2),
            "returns_cost": round(returns_cost, 2),
            "total_costs": round(total_costs, 2),
            "profit_per_unit": round(profit_per_unit, 2)
        }

    elif business_model == "dropshipping":
        platform_fee = retail_price * structure["platform_fee_percent"]
        advertising = retail_price * structure["advertising_percent"]
        returns_cost = retail_price * structure["returns_percent"]
        ship_cost = structure["shipping_cost"]

        total_costs = cogs + platform_fee + advertising + returns_cost + ship_cost
        profit_per_unit = retail_price - total_costs

        return {
            "retail_price": retail_price,
            "cogs": round(cogs, 2),
            "platform_fee": round(platform_fee, 2),
            "shipping": round(ship_cost, 2),
            "advertising": round(advertising, 2),
            "returns_cost": round(returns_cost, 2),
            "total_costs": round(total_costs, 2),
            "profit_per_unit": round(profit_per_unit, 2)
        }

    else:  # private_label or wholesale
        manufacturing = retail_price * structure.get("manufacturing_multiplier", 0.30)
        shipping_cost = retail_price * structure.get("shipping_percent", 0.10)
        marketing = retail_price * structure.get("marketing_percent", 0.15)
        overhead = retail_price * structure.get("overhead_percent", 0.05)

        total_costs = manufacturing + shipping_cost + marketing + overhead
        profit_per_unit = retail_price - total_costs

        return {
            "retail_price": retail_price,
            "manufacturing": round(manufacturing, 2),
            "shipping": round(shipping_cost, 2),
            "marketing": round(marketing, 2),
            "overhead": round(overhead, 2),
            "total_costs": round(total_costs, 2),
            "profit_per_unit": round(profit_per_unit, 2)
        }


def calculate_margins(unit_economics: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate profit margins.

    Args:
        unit_economics: Unit economics data

    Returns:
        Margin calculations
    """
    retail = unit_economics.get("retail_price", 1)
    profit = unit_economics.get("profit_per_unit", 0)
    total_costs = unit_economics.get("total_costs", 0)
    cogs = unit_economics.get("cogs", unit_economics.get("manufacturing", 0))

    gross_margin = (retail - cogs) / retail if retail > 0 else 0
    net_margin = profit / retail if retail > 0 else 0
    markup = (retail - cogs) / cogs if cogs > 0 else 0

    return {
        "gross_margin": round(gross_margin, 4),
        "net_margin": round(net_margin, 4),
        "markup": round(markup, 4),
        "gross_margin_percent": round(gross_margin * 100, 2),
        "net_margin_percent": round(net_margin * 100, 2)
    }


def calculate_monthly_projection(
    unit_economics: Dict[str, float],
    units_per_month: int
) -> Dict[str, float]:
    """
    Calculate monthly revenue and profit projections.

    Args:
        unit_economics: Unit economics data
        units_per_month: Expected monthly sales volume

    Returns:
        Monthly projections
    """
    retail = unit_economics.get("retail_price", 0)
    profit_per_unit = unit_economics.get("profit_per_unit", 0)
    total_costs = unit_economics.get("total_costs", 0)

    monthly_revenue = retail * units_per_month
    monthly_costs = total_costs * units_per_month
    monthly_profit = profit_per_unit * units_per_month
    annual_profit = monthly_profit * 12

    return {
        "units_per_month": units_per_month,
        "monthly_revenue": round(monthly_revenue, 2),
        "monthly_costs": round(monthly_costs, 2),
        "monthly_profit": round(monthly_profit, 2),
        "annual_revenue": round(monthly_revenue * 12, 2),
        "annual_profit": round(annual_profit, 2)
    }


def calculate_investment_requirements(
    unit_economics: Dict[str, float],
    budget_range: str,
    business_model: str
) -> Dict[str, float]:
    """
    Calculate investment requirements.

    Args:
        unit_economics: Unit economics data
        budget_range: Budget range (low/medium/high)
        business_model: Business model type

    Returns:
        Investment breakdown
    """
    budget_config = BUDGET_RANGES.get(budget_range, BUDGET_RANGES["medium"])
    cogs = unit_economics.get("cogs", unit_economics.get("manufacturing", 15))
    units_target = budget_config["units_target"]

    inventory_cost = cogs * units_target
    marketing_budget = budget_config["max"] * 0.20
    operational_reserve = budget_config["max"] * 0.15

    # Business model specific costs
    if business_model == "amazon_fba":
        setup_costs = 500  # Brand registry, listing optimization
        monthly_fees = 40  # Professional seller account
    elif business_model == "dropshipping":
        setup_costs = 200  # Store setup
        monthly_fees = 30  # Platform fees
    else:
        setup_costs = 1000  # Product development
        monthly_fees = 100  # Various subscriptions

    total_investment = inventory_cost + marketing_budget + operational_reserve + setup_costs

    return {
        "initial_inventory": round(inventory_cost, 2),
        "marketing_budget": round(marketing_budget, 2),
        "operational_reserve": round(operational_reserve, 2),
        "setup_costs": round(setup_costs, 2),
        "monthly_fees": round(monthly_fees, 2),
        "total_investment": round(total_investment, 2),
        "units_to_purchase": units_target
    }


def calculate_roi_metrics(
    monthly_projection: Dict[str, float],
    investment: Dict[str, float]
) -> Dict[str, Any]:
    """
    Calculate ROI and payback metrics.

    Args:
        monthly_projection: Monthly projections
        investment: Investment requirements

    Returns:
        ROI metrics
    """
    total_investment = investment.get("total_investment", 1)
    monthly_profit = monthly_projection.get("monthly_profit", 0)
    annual_profit = monthly_projection.get("annual_profit", 0)

    # Payback period in months
    payback_months = total_investment / monthly_profit if monthly_profit > 0 else float('inf')

    # Annual ROI
    annual_roi = (annual_profit / total_investment) if total_investment > 0 else 0

    # Profitability assessment
    if payback_months <= 3:
        assessment = "excellent"
        rating = "A"
    elif payback_months <= 6:
        assessment = "good"
        rating = "B"
    elif payback_months <= 12:
        assessment = "moderate"
        rating = "C"
    else:
        assessment = "challenging"
        rating = "D"

    return {
        "payback_months": round(payback_months, 1) if payback_months != float('inf') else None,
        "annual_roi": round(annual_roi, 4),
        "annual_roi_percent": round(annual_roi * 100, 2),
        "profitable": monthly_profit > 0,
        "rating": rating,
        "recommendation": f"{assessment.title()} opportunity - {payback_months:.1f} month payback" if payback_months != float('inf') else "Review pricing strategy"
    }


def calculate_profit_score(
    margins: Dict[str, float],
    roi_metrics: Dict[str, Any]
) -> int:
    """
    Calculate overall profit score.

    Args:
        margins: Margin calculations
        roi_metrics: ROI metrics

    Returns:
        Profit score 1-100
    """
    score = 50

    # Margin component (0-30)
    net_margin = margins.get("net_margin", 0)
    if net_margin > 0.30:
        score += 30
    elif net_margin > 0.20:
        score += 25
    elif net_margin > 0.15:
        score += 20
    elif net_margin > 0.10:
        score += 15
    elif net_margin > 0.05:
        score += 10
    elif net_margin > 0:
        score += 5
    else:
        score -= 20

    # ROI component (0-20)
    roi = roi_metrics.get("annual_roi", 0)
    if roi > 1.0:  # 100%+ ROI
        score += 20
    elif roi > 0.5:  # 50%+ ROI
        score += 15
    elif roi > 0.25:  # 25%+ ROI
        score += 10
    else:
        score += 5

    # Payback component (-10 to +10)
    payback = roi_metrics.get("payback_months", 12)
    if payback and payback <= 3:
        score += 10
    elif payback and payback <= 6:
        score += 5
    elif payback and payback > 12:
        score -= 10

    return max(1, min(100, score))


async def search_profit_data(
    category: str,
    target_market: str,
    business_model: str,
    budget_range: str,
    avg_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Analyze profitability for a product category.

    Args:
        category: Product category
        target_market: Target market
        business_model: Business model type
        budget_range: Budget range
        avg_price: Optional average price (if known from competition analysis)

    Returns:
        Profit analysis results
    """
    queries = [
        f"{category} wholesale cost price {target_market}",
        f"{category} {business_model} profit margin",
        f"{category} manufacturing cost supplier"
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

    # Extract cost data
    cost_data = extract_cost_data(combined_results, category)

    # Use provided price or estimate from cost
    retail_price = avg_price or (cost_data["estimated_cogs"] * 3)  # 3x markup default

    # Calculate all metrics
    unit_economics = calculate_unit_economics(retail_price, business_model, cost_data)
    margins = calculate_margins(unit_economics)

    # Estimate monthly units based on budget
    budget_config = BUDGET_RANGES.get(budget_range, BUDGET_RANGES["medium"])
    estimated_monthly_units = budget_config["units_target"] // 2  # Conservative estimate

    monthly_projection = calculate_monthly_projection(unit_economics, estimated_monthly_units)
    investment = calculate_investment_requirements(unit_economics, budget_range, business_model)
    roi_metrics = calculate_roi_metrics(monthly_projection, investment)
    profit_score = calculate_profit_score(margins, roi_metrics)

    return {
        "unit_economics": unit_economics,
        "margins": margins,
        "monthly_projection": monthly_projection,
        "investment": investment,
        "assessment": roi_metrics,
        "profit_score": profit_score,
        "raw_data": {
            "search_queries": queries,
            "cost_data": cost_data
        }
    }


def format_profit_results(results: Dict[str, Any]) -> str:
    """
    Format profit analysis results for display.

    Args:
        results: Profit analysis results

    Returns:
        Formatted string
    """
    unit_econ = results.get("unit_economics", {})
    margins = results.get("margins", {})
    projection = results.get("monthly_projection", {})
    investment = results.get("investment", {})
    assessment = results.get("assessment", {})

    rating_emoji = {
        "A": "🌟",
        "B": "✅",
        "C": "⚠️",
        "D": "❌"
    }

    output = f"""
## Profit Analysis Results

**Profit Score:** {results.get('profit_score', 'N/A')}/100
**Rating:** {rating_emoji.get(assessment.get('rating', ''), '❓')} {assessment.get('rating', 'N/A')}

### Unit Economics
- **Retail Price:** ${unit_econ.get('retail_price', 0):.2f}
- **Total Costs:** ${unit_econ.get('total_costs', 0):.2f}
- **Profit/Unit:** ${unit_econ.get('profit_per_unit', 0):.2f}

### Margins
- **Gross Margin:** {margins.get('gross_margin_percent', 0):.1f}%
- **Net Margin:** {margins.get('net_margin_percent', 0):.1f}%

### Monthly Projection ({projection.get('units_per_month', 0)} units)
- **Revenue:** ${projection.get('monthly_revenue', 0):,.2f}
- **Profit:** ${projection.get('monthly_profit', 0):,.2f}

### Investment Required
- **Total Investment:** ${investment.get('total_investment', 0):,.2f}
- **Payback Period:** {assessment.get('payback_months', 'N/A')} months
- **Annual ROI:** {assessment.get('annual_roi_percent', 0):.1f}%

### Assessment
{assessment.get('recommendation', 'N/A')}
"""
    return output.strip()


def get_profit_tools() -> List[Dict[str, Any]]:
    """
    Get list of profit analysis tools for ADK agent registration.

    Returns:
        List of tool definitions
    """
    return [
        {
            "name": "analyze_profit",
            "description": "Analyze profitability, unit economics, and ROI for a product",
            "function": search_profit_data,
            "parameters": {
                "category": {"type": "string", "description": "Product category"},
                "target_market": {"type": "string", "description": "Target market"},
                "business_model": {"type": "string", "description": "Business model"},
                "budget_range": {"type": "string", "description": "Budget range"},
                "avg_price": {"type": "number", "description": "Average price (optional)"}
            }
        }
    ]
