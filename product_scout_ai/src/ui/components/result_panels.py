"""
Result panel components for the UI.

This module provides functions for formatting analysis results.
"""
from typing import Dict, List, Any, Optional

from ..utils.formatters import (
    format_percentage,
    format_currency,
    format_market_size,
    format_trend_direction,
    format_score_label,
)


def format_trend_analysis(trend_analysis: Optional[Dict[str, Any]]) -> str:
    """
    Format trend analysis results as Markdown.

    Args:
        trend_analysis: Trend analysis data

    Returns:
        Markdown formatted string
    """
    if not trend_analysis:
        return "*暂无趋势分析数据*"

    score = trend_analysis.get("trend_score", 0)
    direction = trend_analysis.get("trend_direction", "unknown")
    seasonality = trend_analysis.get("seasonality", {})
    related_queries = trend_analysis.get("related_queries", [])

    md = f"""
### 趋势评分: {score}/100 ({format_score_label(score)})

**趋势方向**: {format_trend_direction(direction)}

"""

    if seasonality:
        md += "**季节性特征**:\n"
        peak_seasons = seasonality.get("peak_seasons", [])
        if peak_seasons:
            md += f"- 旺季: {', '.join(peak_seasons)}\n"
        low_seasons = seasonality.get("low_seasons", [])
        if low_seasons:
            md += f"- 淡季: {', '.join(low_seasons)}\n"
        md += "\n"

    if related_queries:
        md += "**相关搜索词**:\n"
        for query in related_queries[:5]:
            if isinstance(query, dict):
                q = query.get("query", query.get("term", ""))
                md += f"- {q}\n"
            else:
                md += f"- {query}\n"

    return md


def format_market_analysis(market_analysis: Optional[Dict[str, Any]]) -> str:
    """
    Format market analysis results as Markdown.

    Args:
        market_analysis: Market analysis data

    Returns:
        Markdown formatted string
    """
    if not market_analysis:
        return "*暂无市场分析数据*"

    score = market_analysis.get("market_score", 0)
    market_size = market_analysis.get("market_size", {})
    growth_rate = market_analysis.get("growth_rate", 0)
    maturity = market_analysis.get("maturity_level", "unknown")
    segments = market_analysis.get("customer_segments", [])

    maturity_labels = {
        "emerging": "🌱 新兴市场",
        "growing": "📈 成长市场",
        "mature": "🏢 成熟市场",
        "declining": "📉 衰退市场",
    }

    md = f"""
### 市场评分: {score}/100 ({format_score_label(score)})

**市场规模**:
- TAM (总市场): {format_market_size(market_size.get('tam', 0))}
- SAM (可服务市场): {format_market_size(market_size.get('sam', 0))}
- SOM (可获取市场): {format_market_size(market_size.get('som', 0))}

**年增长率**: {format_percentage(growth_rate)}

**市场成熟度**: {maturity_labels.get(maturity, maturity)}

"""

    if segments:
        md += "**目标客群**:\n"
        for segment in segments[:5]:
            if isinstance(segment, dict):
                name = segment.get("segment", segment.get("name", ""))
                md += f"- {name}\n"
            else:
                md += f"- {segment}\n"

    return md


def format_competition_analysis(competition_analysis: Optional[Dict[str, Any]]) -> str:
    """
    Format competition analysis results as Markdown.

    Args:
        competition_analysis: Competition analysis data

    Returns:
        Markdown formatted string
    """
    if not competition_analysis:
        return "*暂无竞争分析数据*"

    score = competition_analysis.get("competition_score", 0)
    competitors = competition_analysis.get("competitors", [])
    pricing = competition_analysis.get("pricing_analysis", {})
    opportunities = competition_analysis.get("opportunities", [])
    barriers = competition_analysis.get("entry_barriers", "medium")

    barrier_labels = {
        "low": "🟢 低门槛",
        "medium": "🟡 中等门槛",
        "high": "🔴 高门槛",
    }

    # Competition score is inverse - higher means more competitive (harder)
    difficulty_label = "激烈" if score >= 70 else ("中等" if score >= 40 else "较低")

    md = f"""
### 竞争评分: {score}/100 (竞争{difficulty_label})

**进入门槛**: {barrier_labels.get(barriers, barriers)}

"""

    if pricing:
        avg_price = pricing.get("average_price", pricing.get("avg_price", 0))
        price_range = pricing.get("price_range", {})
        if isinstance(price_range, dict):
            min_p = price_range.get("min", 0)
            max_p = price_range.get("max", 0)
        elif isinstance(price_range, list) and len(price_range) >= 2:
            min_p, max_p = price_range[0], price_range[1]
        else:
            min_p, max_p = 0, 0

        md += f"""**定价分析**:
- 平均价格: {format_currency(avg_price)}
- 价格区间: {format_currency(min_p)} - {format_currency(max_p)}

"""

    if competitors:
        md += "**主要竞争对手**:\n"
        for comp in competitors[:5]:
            if isinstance(comp, dict):
                name = comp.get("name", "")
                share = comp.get("market_share", 0)
                if share:
                    md += f"- {name} (市场份额: {format_percentage(share/100 if share > 1 else share)})\n"
                else:
                    md += f"- {name}\n"
            else:
                md += f"- {comp}\n"
        md += "\n"

    if opportunities:
        md += "**市场机会**:\n"
        for opp in opportunities[:5]:
            md += f"- {opp}\n"

    return md


def format_profit_analysis(profit_analysis: Optional[Dict[str, Any]]) -> str:
    """
    Format profit analysis results as Markdown.

    Args:
        profit_analysis: Profit analysis data

    Returns:
        Markdown formatted string
    """
    if not profit_analysis:
        return "*暂无利润分析数据*"

    score = profit_analysis.get("profit_score", 0)
    unit_econ = profit_analysis.get("unit_economics", {})
    margins = profit_analysis.get("margins", {})
    projection = profit_analysis.get("monthly_projection", {})
    investment = profit_analysis.get("investment", {})
    assessment = profit_analysis.get("assessment", {})

    md = f"""
### 利润评分: {score}/100 ({format_score_label(score)})

**单位经济**:
- 售价: {format_currency(unit_econ.get('retail_price', unit_econ.get('product_cost', 0) * 2))}
- 成本: {format_currency(unit_econ.get('product_cost', unit_econ.get('cost', 0)))}
- 单位利润: {format_currency(unit_econ.get('profit_per_unit', 0))}

**利润率**:
- 毛利率: {format_percentage(margins.get('gross_margin', 0))}
- 净利率: {format_percentage(margins.get('net_margin', 0))}

"""

    if projection:
        md += f"""**月度预测**:
- 预估销量: {projection.get('units_sold', projection.get('units', 0))} 件
- 预估收入: {format_currency(projection.get('revenue', 0))}
- 预估利润: {format_currency(projection.get('profit', 0))}

"""

    if investment:
        md += f"""**投资需求**:
- 库存投入: {format_currency(investment.get('inventory_cost', investment.get('inventory', 0)))}
- 总投资: {format_currency(investment.get('total_investment', investment.get('total', 0)))}

"""

    if assessment:
        is_profitable = assessment.get("profitable", False)
        roi = assessment.get("roi", 0)
        status = "✅ 有盈利潜力" if is_profitable else "❌ 盈利困难"
        md += f"""**盈利评估**: {status}
- ROI: {format_percentage(roi)}
"""

    return md


def format_swot_analysis(swot: Optional[Dict[str, List[str]]]) -> str:
    """
    Format SWOT analysis as Markdown.

    Args:
        swot: SWOT analysis data

    Returns:
        Markdown formatted string
    """
    if not swot:
        return "*暂无 SWOT 分析数据*"

    md = ""

    sections = [
        ("strengths", "💪 优势 (Strengths)", "#22c55e"),
        ("weaknesses", "⚠️ 劣势 (Weaknesses)", "#ef4444"),
        ("opportunities", "🚀 机会 (Opportunities)", "#3b82f6"),
        ("threats", "🔥 威胁 (Threats)", "#f59e0b"),
    ]

    for key, title, color in sections:
        items = swot.get(key, [])
        if items:
            md += f"### {title}\n"
            for item in items:
                md += f"- {item}\n"
            md += "\n"

    return md if md else "*暂无 SWOT 分析数据*"


def format_risks_and_factors(
    risks: Optional[List[str]],
    factors: Optional[List[str]]
) -> str:
    """
    Format key risks and success factors as Markdown.

    Args:
        risks: List of key risks
        factors: List of success factors

    Returns:
        Markdown formatted string
    """
    md = ""

    if risks:
        md += "### ⚠️ 关键风险\n"
        for risk in risks:
            md += f"- {risk}\n"
        md += "\n"

    if factors:
        md += "### ✅ 成功要素\n"
        for factor in factors:
            md += f"- {factor}\n"

    return md if md else "*暂无风险和成功要素分析*"


def format_full_report(result: Dict[str, Any]) -> str:
    """
    Format full analysis report as Markdown.

    Args:
        result: Complete analysis result

    Returns:
        Markdown formatted string
    """
    state = result.get("state", {})
    request = state.get("request", {})

    md = f"""# 产品机会分析报告

**产品类别**: {request.get('category', 'N/A')}
**目标市场**: {request.get('target_market', 'N/A')}
**商业模式**: {request.get('business_model', 'N/A')}
**预算范围**: {request.get('budget_range', 'N/A')}

---

## 趋势分析
{format_trend_analysis(state.get('trend_analysis'))}

---

## 市场分析
{format_market_analysis(state.get('market_analysis'))}

---

## 竞争分析
{format_competition_analysis(state.get('competition_analysis'))}

---

## 利润分析
{format_profit_analysis(state.get('profit_analysis'))}

---

## SWOT 分析
{format_swot_analysis(state.get('evaluation_result', {}).get('swot_analysis'))}

---

## 风险与成功要素
{format_risks_and_factors(
    state.get('evaluation_result', {}).get('key_risks'),
    state.get('evaluation_result', {}).get('success_factors')
)}

---

*报告生成时间: {result.get('exported_at', 'N/A')}*
"""

    return md
