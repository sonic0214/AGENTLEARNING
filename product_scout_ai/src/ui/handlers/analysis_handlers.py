"""
Analysis handlers for the UI.

This module provides event handlers for analysis operations.
"""
from typing import Dict, Any, Tuple, Optional, Generator
import asyncio

from src.schemas.input_schemas import AnalysisRequest
from src.services.analysis_service import create_analysis_service
from src.services.history_service import create_history_service
from src.workflows.analysis_pipeline import PipelineResult


# Phase descriptions for progress display
PHASE_DESCRIPTIONS = {
    "initialized": ("初始化", 0.0),
    "analyzing_trends": ("分析市场趋势", 0.15),
    "analyzing_market": ("分析市场规模", 0.35),
    "analyzing_competition": ("分析竞争格局", 0.55),
    "analyzing_profit": ("分析利润空间", 0.75),
    "evaluating": ("综合评估", 0.90),
    "generating_report": ("生成报告", 0.95),
    "completed": ("分析完成", 1.0),
    "failed": ("分析失败", 1.0),
}


def validate_inputs(
    category: str,
    market: str,
    budget: str,
    model: str,
    keywords: str
) -> Tuple[bool, str]:
    """
    Validate user inputs.

    Args:
        category: Product category
        market: Target market
        budget: Budget range
        model: Business model
        keywords: Comma-separated keywords

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not category or not category.strip():
        return False, "产品类别不能为空"

    if len(category.strip()) < 2:
        return False, "产品类别至少需要 2 个字符"

    if len(category.strip()) > 200:
        return False, "产品类别不能超过 200 个字符"

    # Parse and validate keywords
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if len(keyword_list) > 10:
            return False, "关键词不能超过 10 个"

    return True, ""


def create_analysis_request(
    category: str,
    market: str,
    budget: str,
    model: str,
    keywords: str
) -> AnalysisRequest:
    """
    Create analysis request from user inputs.

    Args:
        category: Product category
        market: Target market
        budget: Budget range
        model: Business model
        keywords: Comma-separated keywords

    Returns:
        AnalysisRequest object
    """
    keyword_list = []
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()][:10]

    return AnalysisRequest(
        category=category.strip(),
        target_market=market,
        budget_range=budget,
        business_model=model,
        keywords=keyword_list
    )


async def run_analysis(
    category: str,
    market: str,
    budget: str,
    model: str,
    keywords: str,
    progress_callback=None
) -> Tuple[bool, Dict[str, Any], str]:
    """
    Run product analysis.

    Args:
        category: Product category
        market: Target market
        budget: Budget range
        model: Business model
        keywords: Comma-separated keywords
        progress_callback: Optional progress callback function

    Returns:
        Tuple of (success, result_data, error_message)
    """
    # Validate inputs
    is_valid, error_msg = validate_inputs(category, market, budget, model, keywords)
    if not is_valid:
        return False, {}, error_msg

    try:
        # Create request
        request = create_analysis_request(category, market, budget, model, keywords)

        # Create service
        service = create_analysis_service()
        history_service = create_history_service()

        # Define progress handler
        def on_progress(phase: str, message: str):
            if progress_callback:
                desc, progress_val = PHASE_DESCRIPTIONS.get(phase, (message, 0.5))
                progress_callback(progress_val, desc)

        # Run analysis
        result = await service.analyze(request, on_progress=on_progress)

        if result.success:
            # Add to history
            history_service.add_entry(request, result)

            # Convert result to dictionary
            result_data = convert_result_to_dict(result)
            return True, result_data, ""
        else:
            return False, {}, result.error or "分析失败，请重试"

    except Exception as e:
        return False, {}, f"分析出错: {str(e)}"


def convert_result_to_dict(result: PipelineResult) -> Dict[str, Any]:
    """
    Convert PipelineResult to dictionary for UI display.

    Args:
        result: PipelineResult object

    Returns:
        Dictionary with result data
    """
    state = result.state

    data = {
        "success": result.success,
        "execution_time": result.execution_time,
        "request": None,
        "trend_analysis": None,
        "market_analysis": None,
        "competition_analysis": None,
        "profit_analysis": None,
        "evaluation_result": None,
    }

    if state:
        # Request
        if state.request:
            data["request"] = {
                "category": state.request.category,
                "target_market": state.request.target_market,
                "budget_range": state.request.budget_range,
                "business_model": state.request.business_model,
                "keywords": state.request.keywords,
            }

        # Trend Analysis
        if state.trend_analysis:
            data["trend_analysis"] = {
                "trend_score": state.trend_analysis.trend_score,
                "trend_direction": state.trend_analysis.trend_direction,
                "seasonality": state.trend_analysis.seasonality,
                "related_queries": state.trend_analysis.related_queries,
            }

        # Market Analysis
        if state.market_analysis:
            data["market_analysis"] = {
                "market_score": state.market_analysis.market_score,
                "market_size": state.market_analysis.market_size,
                "growth_rate": state.market_analysis.growth_rate,
                "customer_segments": state.market_analysis.customer_segments,
                "maturity_level": state.market_analysis.maturity_level,
            }

        # Competition Analysis
        if state.competition_analysis:
            data["competition_analysis"] = {
                "competition_score": state.competition_analysis.competition_score,
                "competitors": state.competition_analysis.competitors,
                "pricing_analysis": state.competition_analysis.pricing_analysis,
                "opportunities": state.competition_analysis.opportunities,
                "entry_barriers": getattr(state.competition_analysis, "entry_barriers", "medium"),
            }

        # Profit Analysis
        if state.profit_analysis:
            data["profit_analysis"] = {
                "profit_score": state.profit_analysis.profit_score,
                "unit_economics": state.profit_analysis.unit_economics,
                "margins": state.profit_analysis.margins,
                "monthly_projection": state.profit_analysis.monthly_projection,
                "investment": state.profit_analysis.investment,
                "assessment": state.profit_analysis.assessment,
            }

        # Evaluation Result
        if state.evaluation_result:
            data["evaluation_result"] = {
                "opportunity_score": state.evaluation_result.opportunity_score,
                "dimension_scores": state.evaluation_result.dimension_scores,
                "swot_analysis": state.evaluation_result.swot_analysis,
                "recommendation": state.evaluation_result.recommendation,
                "recommendation_detail": state.evaluation_result.recommendation_detail,
                "key_risks": state.evaluation_result.key_risks,
                "success_factors": state.evaluation_result.success_factors,
            }

    return data


def get_dimension_scores(result_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract dimension scores from result data.

    Args:
        result_data: Analysis result dictionary

    Returns:
        Dictionary of dimension names to scores
    """
    scores = {}

    if result_data.get("trend_analysis"):
        scores["趋势"] = result_data["trend_analysis"].get("trend_score", 0)

    if result_data.get("market_analysis"):
        scores["市场"] = result_data["market_analysis"].get("market_score", 0)

    if result_data.get("competition_analysis"):
        scores["竞争"] = result_data["competition_analysis"].get("competition_score", 0)

    if result_data.get("profit_analysis"):
        scores["利润"] = result_data["profit_analysis"].get("profit_score", 0)

    return scores


def get_overall_score(result_data: Dict[str, Any]) -> Tuple[int, str, str]:
    """
    Get overall score and recommendation.

    Args:
        result_data: Analysis result dictionary

    Returns:
        Tuple of (score, recommendation, detail)
    """
    eval_result = result_data.get("evaluation_result")

    # Handle None case - evaluation_result might not exist yet
    if eval_result is None:
        eval_result = {}

    score = eval_result.get("opportunity_score", 0)
    recommendation = eval_result.get("recommendation", "unknown")
    detail = eval_result.get("recommendation_detail", "")

    return score, recommendation, detail
