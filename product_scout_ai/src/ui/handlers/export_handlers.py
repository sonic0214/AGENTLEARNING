"""
Export handlers for the UI.

This module provides event handlers for export operations.
"""
from typing import Dict, Any, Tuple, Optional
import json
from datetime import datetime

from src.services.export_service import create_export_service
from src.workflows.analysis_pipeline import PipelineResult
from src.schemas.state_schemas import AnalysisState


def get_export_preview(
    result_data: Dict[str, Any],
    format_type: str = "JSON"
) -> str:
    """
    Get export preview content.

    Args:
        result_data: Analysis result data
        format_type: Export format (JSON, Markdown)

    Returns:
        Preview content string
    """
    if not result_data:
        return "没有可导出的数据"

    if format_type == "JSON":
        return json.dumps(result_data, indent=2, ensure_ascii=False)
    elif format_type == "Markdown":
        return _format_as_markdown(result_data)
    else:
        return _format_as_summary(result_data)


def export_analysis(
    result_data: Dict[str, Any],
    format_type: str = "JSON",
    filename: Optional[str] = None
) -> Tuple[str, str]:
    """
    Export analysis result.

    Args:
        result_data: Analysis result data
        format_type: Export format
        filename: Optional filename

    Returns:
        Tuple of (content, filename)
    """
    if not result_data:
        return "", ""

    # Generate content
    if format_type == "JSON":
        content = json.dumps(result_data, indent=2, ensure_ascii=False)
        ext = ".json"
    elif format_type == "Markdown":
        content = _format_as_markdown(result_data)
        ext = ".md"
    else:
        content = _format_as_summary(result_data)
        ext = ".txt"

    # Generate filename
    if not filename:
        category = result_data.get("request", {}).get("category", "analysis")
        category_slug = category.replace(" ", "_")[:30]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{category_slug}_{timestamp}{ext}"

    return content, filename


def _format_as_markdown(data: Dict[str, Any]) -> str:
    """Format result data as Markdown."""
    request = data.get("request", {})
    trend = data.get("trend_analysis", {})
    market = data.get("market_analysis", {})
    competition = data.get("competition_analysis", {})
    profit = data.get("profit_analysis", {})
    evaluation = data.get("evaluation_result", {})

    md = f"""# 产品机会分析报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 分析请求

| 项目 | 内容 |
|------|------|
| 产品类别 | {request.get('category', 'N/A')} |
| 目标市场 | {request.get('target_market', 'N/A')} |
| 预算范围 | {request.get('budget_range', 'N/A')} |
| 商业模式 | {request.get('business_model', 'N/A')} |

---

## 综合评估

- **机会评分**: {evaluation.get('opportunity_score', 0)}/100
- **建议**: {evaluation.get('recommendation', 'N/A').upper()}
- **说明**: {evaluation.get('recommendation_detail', 'N/A')}

### 维度评分

| 维度 | 评分 |
|------|------|
| 趋势 | {trend.get('trend_score', 0)}/100 |
| 市场 | {market.get('market_score', 0)}/100 |
| 竞争 | {competition.get('competition_score', 0)}/100 |
| 利润 | {profit.get('profit_score', 0)}/100 |

---

## 趋势分析

- **趋势评分**: {trend.get('trend_score', 0)}/100
- **趋势方向**: {trend.get('trend_direction', 'N/A')}

---

## 市场分析

- **市场评分**: {market.get('market_score', 0)}/100
- **增长率**: {market.get('growth_rate', 0) * 100:.1f}%
- **成熟度**: {market.get('maturity_level', 'N/A')}

---

## 竞争分析

- **竞争评分**: {competition.get('competition_score', 0)}/100
- **进入门槛**: {competition.get('entry_barriers', 'N/A')}

---

## 利润分析

- **利润评分**: {profit.get('profit_score', 0)}/100

---

## SWOT 分析

"""
    swot = evaluation.get('swot_analysis', {})
    if swot:
        if swot.get('strengths'):
            md += "### 优势\n"
            for item in swot['strengths']:
                md += f"- {item}\n"
            md += "\n"

        if swot.get('weaknesses'):
            md += "### 劣势\n"
            for item in swot['weaknesses']:
                md += f"- {item}\n"
            md += "\n"

        if swot.get('opportunities'):
            md += "### 机会\n"
            for item in swot['opportunities']:
                md += f"- {item}\n"
            md += "\n"

        if swot.get('threats'):
            md += "### 威胁\n"
            for item in swot['threats']:
                md += f"- {item}\n"
            md += "\n"

    md += """---

## 关键风险

"""
    risks = evaluation.get('key_risks', [])
    if risks:
        for risk in risks:
            md += f"- {risk}\n"
    else:
        md += "- 暂无\n"

    md += """
## 成功要素

"""
    factors = evaluation.get('success_factors', [])
    if factors:
        for factor in factors:
            md += f"- {factor}\n"
    else:
        md += "- 暂无\n"

    md += """
---

*由 ProductScout AI 生成*
"""

    return md


def _format_as_summary(data: Dict[str, Any]) -> str:
    """Format result data as brief summary."""
    request = data.get("request", {})
    evaluation = data.get("evaluation_result", {})

    category = request.get('category', 'N/A')
    market = request.get('target_market', 'N/A')
    score = evaluation.get('opportunity_score', 0)
    recommendation = evaluation.get('recommendation', 'N/A').upper()
    detail = evaluation.get('recommendation_detail', '')

    summary = f"""ProductScout AI 分析摘要
========================

产品: {category}
市场: {market}
评分: {score}/100
建议: {recommendation}

{detail}

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    return summary
