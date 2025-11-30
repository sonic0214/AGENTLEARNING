"""
Export service for ProductScout AI.

This module provides services for exporting analysis results
to various formats.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.schemas.output_schemas import FinalReport, EvaluationResult
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult


@dataclass
class ExportConfig:
    """
    Configuration for export service.

    Attributes:
        include_raw_data: Include raw analysis data in exports
        include_timestamps: Include timestamps in exports
        pretty_print: Pretty print JSON exports
    """
    include_raw_data: bool = True
    include_timestamps: bool = True
    pretty_print: bool = True


class ExportService:
    """
    Service for exporting analysis results.

    Provides functionality to export results to JSON, Markdown,
    and other formats.
    """

    def __init__(self, config: Optional[ExportConfig] = None):
        """
        Initialize the export service.

        Args:
            config: Export configuration
        """
        self.config = config or ExportConfig()

    def to_json(self, result: PipelineResult) -> str:
        """
        Export result to JSON format.

        Args:
            result: Pipeline result

        Returns:
            JSON string
        """
        data = self._build_export_data(result)

        indent = 2 if self.config.pretty_print else None
        return json.dumps(data, indent=indent, default=str)

    def to_dict(self, result: PipelineResult) -> Dict[str, Any]:
        """
        Export result to dictionary.

        Args:
            result: Pipeline result

        Returns:
            Dictionary with export data
        """
        return self._build_export_data(result)

    def to_markdown(self, result: PipelineResult) -> str:
        """
        Export result to Markdown format.

        Args:
            result: Pipeline result

        Returns:
            Markdown string
        """
        lines = []

        # Header
        lines.append("# Product Opportunity Analysis Report")
        lines.append("")

        if self.config.include_timestamps:
            lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
            lines.append("")

        # Status
        status = "SUCCESS" if result.success else "FAILED"
        lines.append(f"**Status:** {status}")
        lines.append(f"**Execution Time:** {result.execution_time:.2f}s")
        lines.append("")

        if result.error:
            lines.append(f"**Error:** {result.error}")
            lines.append("")

        # Request info
        if result.state and result.state.request:
            req = result.state.request
            lines.append("## Analysis Request")
            lines.append("")
            lines.append(f"- **Category:** {req.category}")
            lines.append(f"- **Target Market:** {req.target_market}")
            lines.append(f"- **Business Model:** {req.business_model}")
            lines.append(f"- **Budget Range:** {req.budget_range}")
            lines.append("")

        # Trend analysis
        if result.state and result.state.trend_analysis:
            trend = result.state.trend_analysis
            lines.append("## Trend Analysis")
            lines.append("")
            lines.append(f"- **Trend Score:** {trend.trend_score}/100")
            lines.append(f"- **Trend Direction:** {trend.trend_direction}")
            lines.append("")

        # Market analysis
        if result.state and result.state.market_analysis:
            market = result.state.market_analysis
            lines.append("## Market Analysis")
            lines.append("")
            lines.append(f"- **Market Score:** {market.market_score}/100")
            lines.append(f"- **Growth Rate:** {market.growth_rate:.1%}")
            lines.append(f"- **Maturity Level:** {market.maturity_level}")
            lines.append("")

        # Competition analysis
        if result.state and result.state.competition_analysis:
            comp = result.state.competition_analysis
            lines.append("## Competition Analysis")
            lines.append("")
            lines.append(f"- **Competition Score:** {comp.competition_score}/100")
            lines.append(f"- **Competitors Found:** {len(comp.competitors)}")
            lines.append("")

        # Profit analysis
        if result.state and result.state.profit_analysis:
            profit = result.state.profit_analysis
            lines.append("## Profit Analysis")
            lines.append("")
            lines.append(f"- **Profit Score:** {profit.profit_score}/100")
            lines.append("")

        # Evaluation
        if result.state and result.state.evaluation_result:
            eval_result = result.state.evaluation_result
            lines.append("## Evaluation Summary")
            lines.append("")
            lines.append(f"- **Opportunity Score:** {eval_result.opportunity_score}/100")
            lines.append(f"- **Recommendation:** {eval_result.recommendation.upper()}")
            lines.append(f"- **Detail:** {eval_result.recommendation_detail}")
            lines.append("")

            if eval_result.key_risks:
                lines.append("### Key Risks")
                for risk in eval_result.key_risks:
                    lines.append(f"- {risk}")
                lines.append("")

            if eval_result.success_factors:
                lines.append("### Success Factors")
                for factor in eval_result.success_factors:
                    lines.append(f"- {factor}")
                lines.append("")

        return "\n".join(lines)

    def to_summary(self, result: PipelineResult) -> str:
        """
        Export result to brief summary format.

        Args:
            result: Pipeline result

        Returns:
            Summary string
        """
        if not result.success:
            return f"Analysis failed: {result.error}"

        lines = []

        if result.state and result.state.request:
            lines.append(f"Category: {result.state.request.category}")

        if result.state and result.state.evaluation_result:
            eval_result = result.state.evaluation_result
            lines.append(f"Score: {eval_result.opportunity_score}/100")
            lines.append(f"Recommendation: {eval_result.recommendation.upper()}")
            lines.append(f"Summary: {eval_result.recommendation_detail}")

        return " | ".join(lines)

    def _build_export_data(self, result: PipelineResult) -> Dict[str, Any]:
        """Build export data dictionary."""
        data: Dict[str, Any] = {
            "success": result.success,
            "execution_time": result.execution_time
        }

        if self.config.include_timestamps:
            data["exported_at"] = datetime.now().isoformat()

        if result.error:
            data["error"] = result.error

        if result.state:
            data["request"] = (
                result.state.request.to_dict()
                if result.state.request else None
            )

            if self.config.include_raw_data:
                # Build analyses with better fallback handling
                analyses = {}

                # Trend analysis
                if result.state and result.state.trend_analysis:
                    try:
                        analyses["trend"] = result.state.trend_analysis.to_dict()
                    except Exception:
                        # Fallback to basic structure
                        analyses["trend"] = {
                            "trend_score": getattr(result.state.trend_analysis, 'trend_score', 50),
                            "trend_direction": getattr(result.state.trend_analysis, 'trend_direction', 'stable'),
                            "seasonality": getattr(result.state.trend_analysis, 'seasonality', {}),
                            "related_queries": getattr(result.state.trend_analysis, 'related_queries', [])
                        }
                else:
                    analyses["trend"] = None

                # Market analysis
                if result.state and result.state.market_analysis:
                    try:
                        analyses["market"] = result.state.market_analysis.to_dict()
                    except Exception:
                        analyses["market"] = {
                            "market_score": getattr(result.state.market_analysis, 'market_score', 50),
                            "market_size": getattr(result.state.market_analysis, 'market_size', 'Unknown'),
                            "growth_rate": getattr(result.state.market_analysis, 'growth_rate', 'Unknown'),
                            "customer_segments": getattr(result.state.market_analysis, 'customer_segments', [])
                        }
                else:
                    analyses["market"] = None

                # Competition analysis
                if result.state and result.state.competition_analysis:
                    try:
                        analyses["competition"] = result.state.competition_analysis.to_dict()
                    except Exception:
                        analyses["competition"] = {
                            "competition_score": getattr(result.state.competition_analysis, 'competition_score', 50),
                            "competitors": getattr(result.state.competition_analysis, 'competitors', []),
                            "entry_barriers": getattr(result.state.competition_analysis, 'entry_barriers', 'Medium'),
                            "pricing_range": getattr(result.state.competition_analysis, 'pricing_range', 'Unknown')
                        }
                else:
                    analyses["competition"] = None

                # Profit analysis
                if result.state and result.state.profit_analysis:
                    try:
                        analyses["profit"] = result.state.profit_analysis.to_dict()
                    except Exception:
                        analyses["profit"] = {
                            "profit_score": getattr(result.state.profit_analysis, 'profit_score', 50),
                            "unit_economics": getattr(result.state.profit_analysis, 'unit_economics', {}),
                            "roi_estimate": getattr(result.state.profit_analysis, 'roi_estimate', 'Unknown'),
                            "break_even_time": getattr(result.state.profit_analysis, 'break_even_time', 'Unknown')
                        }
                else:
                    analyses["profit"] = None

                data["analyses"] = analyses

            data["evaluation"] = (
                result.state.evaluation_result.to_dict()
                if result.state.evaluation_result else None
            )

        if result.phase_times:
            data["phase_times"] = result.phase_times

        return data


def create_export_service(
    config: Optional[ExportConfig] = None
) -> ExportService:
    """
    Factory function to create an export service.

    Args:
        config: Export configuration

    Returns:
        Configured ExportService
    """
    return ExportService(config)


def export_to_json(result: PipelineResult) -> str:
    """
    Quick export to JSON.

    Args:
        result: Pipeline result

    Returns:
        JSON string
    """
    service = create_export_service()
    return service.to_json(result)


def export_to_markdown(result: PipelineResult) -> str:
    """
    Quick export to Markdown.

    Args:
        result: Pipeline result

    Returns:
        Markdown string
    """
    service = create_export_service()
    return service.to_markdown(result)
