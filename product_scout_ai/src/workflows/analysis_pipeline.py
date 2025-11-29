"""
Analysis pipeline workflow for ProductScout AI.

This module implements the main analysis workflow that orchestrates
all agents in the proper sequence using ADK patterns.
"""
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.sessions import Session  # type: ignore

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
    FinalReport,
)
from src.schemas.state_schemas import AnalysisState
from src.agents import (
    TrendAgent,
    MarketAgent,
    CompetitionAgent,
    ProfitAgent,
    EvaluatorAgent,
    ReportAgent,
    extract_json_from_response,
)


@dataclass
class PipelineResult:
    """
    Result of a pipeline execution.

    Attributes:
        success: Whether the pipeline completed successfully
        state: Final analysis state
        report: Generated report (if successful)
        error: Error message (if failed)
        execution_time: Total execution time in seconds
        phase_times: Execution time for each phase
    """
    success: bool
    state: AnalysisState
    report: Optional[FinalReport] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    phase_times: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "state": self.state.to_dict(),
            "report": self.report.to_dict() if self.report else None,
            "error": self.error,
            "execution_time": self.execution_time,
            "phase_times": self.phase_times,
        }


class AnalysisPipeline:
    """
    Main analysis pipeline that coordinates all agents.

    The pipeline follows this structure:
    1. Parallel Phase: Run 4 analysis agents concurrently
       - TrendAgent
       - MarketAgent
       - CompetitionAgent
       - ProfitAgent
    2. Evaluation Phase: Synthesize results with EvaluatorAgent
    3. Report Phase: Generate final report with ReportAgent
    """

    def __init__(
        self,
        settings: Optional[Settings] = None,
        on_phase_complete: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        """
        Initialize the pipeline.

        Args:
            settings: Application settings
            on_phase_complete: Callback when a phase completes
        """
        self.settings = settings or Settings()
        self.on_phase_complete = on_phase_complete

        # Initialize agent instances
        self._trend_agent = TrendAgent(self.settings)
        self._market_agent = MarketAgent(self.settings)
        self._competition_agent = CompetitionAgent(self.settings)
        self._profit_agent = ProfitAgent(self.settings)
        self._evaluator_agent = EvaluatorAgent(self.settings)
        self._report_agent = ReportAgent(self.settings)

    def _notify_phase_complete(self, phase: str, result: Dict[str, Any]) -> None:
        """Notify callback of phase completion."""
        if self.on_phase_complete:
            self.on_phase_complete(phase, result)

    async def _run_parallel_analysis(
        self,
        request: AnalysisRequest,
        state: AnalysisState
    ) -> AnalysisState:
        """
        Run the four analysis agents in parallel.

        Args:
            request: Analysis request
            state: Current analysis state

        Returns:
            Updated analysis state with all analysis results
        """
        state.set_phase("analyzing_trends")

        # Create all analysis agents
        trend_agent = self._trend_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        market_agent = self._market_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        competition_agent = self._competition_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        profit_agent = self._profit_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            business_model=request.business_model,
            budget_range=request.budget_range
        )

        # Create parallel agent
        parallel_agent = ParallelAgent(
            name="parallel_analysis",
            sub_agents=[trend_agent, market_agent, competition_agent, profit_agent],
            description="Run all four analyses in parallel"
        )

        # Execute parallel analysis
        # Note: In real execution, this would use ADK's runner
        # For now, we simulate the structure
        start_time = datetime.now()

        # The actual execution would be handled by ADK's runner
        # This returns the parallel agent for use with ADK

        return state, parallel_agent

    def _parse_trend_result(self, result: str) -> Optional[TrendAnalysis]:
        """Parse trend analysis result from agent output."""
        data = extract_json_from_response(result)
        if data:
            try:
                return TrendAnalysis.from_dict(data)
            except (ValueError, KeyError):
                pass
        return None

    def _parse_market_result(self, result: str) -> Optional[MarketAnalysis]:
        """Parse market analysis result from agent output."""
        data = extract_json_from_response(result)
        if data:
            try:
                return MarketAnalysis.from_dict(data)
            except (ValueError, KeyError):
                pass
        return None

    def _parse_competition_result(self, result: str) -> Optional[CompetitionAnalysis]:
        """Parse competition analysis result from agent output."""
        data = extract_json_from_response(result)
        if data:
            try:
                return CompetitionAnalysis.from_dict(data)
            except (ValueError, KeyError):
                pass
        return None

    def _parse_profit_result(self, result: str) -> Optional[ProfitAnalysis]:
        """Parse profit analysis result from agent output."""
        data = extract_json_from_response(result)
        if data:
            try:
                return ProfitAnalysis.from_dict(data)
            except (ValueError, KeyError):
                pass
        return None

    def _parse_evaluation_result(self, result: str) -> Optional[EvaluationResult]:
        """Parse evaluation result from agent output."""
        data = extract_json_from_response(result)
        if data:
            try:
                return EvaluationResult.from_dict(data)
            except (ValueError, KeyError):
                pass
        return None

    def create_pipeline_agents(self, request: AnalysisRequest) -> Dict[str, Any]:
        """
        Create all pipeline agents for ADK execution.

        Args:
            request: Analysis request

        Returns:
            Dictionary containing all configured agents
        """
        # Create analysis agents
        trend_agent = self._trend_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        market_agent = self._market_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        competition_agent = self._competition_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        profit_agent = self._profit_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            business_model=request.business_model,
            budget_range=request.budget_range
        )

        # Create parallel analysis agent directly
        try:
            parallel_agent = ParallelAgent(
                name="parallel_analysis",
                sub_agents=[trend_agent, market_agent, competition_agent, profit_agent],
                description="Execute all analyses concurrently"
            )
        except Exception as e:
            print(f"Error creating ParallelAgent: {e}")
            # Fallback to simple agent
            from google.adk.agents import LlmAgent  # type: ignore
            parallel_agent = LlmAgent(
                name="parallel_analysis",
                instruction="You are a parallel analysis coordinator. Execute all provided sub-agents concurrently and return their results.",
                model="gemini-2.0-flash"
            )
            # Add sub_agents manually (workaround)
            parallel_agent.sub_agents = [trend_agent, market_agent, competition_agent, profit_agent]

        agents_dict = {
            "parallel_agent": parallel_agent,
            "trend_agent": trend_agent,
            "market_agent": market_agent,
            "competition_agent": competition_agent,
            "profit_agent": profit_agent,
            "request": request
        }
        return agents_dict

    def create_evaluator(
        self,
        request: AnalysisRequest,
        trend_analysis: TrendAnalysis,
        market_analysis: MarketAnalysis,
        competition_analysis: CompetitionAnalysis,
        profit_analysis: ProfitAnalysis
    ) -> LlmAgent:
        """
        Create evaluator agent with analysis results.

        Args:
            request: Original request
            trend_analysis: Trend analysis results
            market_analysis: Market analysis results
            competition_analysis: Competition analysis results
            profit_analysis: Profit analysis results

        Returns:
            Configured evaluator agent
        """
        return self._evaluator_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            trend_analysis=trend_analysis.to_json(),
            market_analysis=market_analysis.to_json(),
            competition_analysis=competition_analysis.to_json(),
            profit_analysis=profit_analysis.to_json()
        )

    def create_report_generator(
        self,
        request: AnalysisRequest,
        trend_analysis: TrendAnalysis,
        market_analysis: MarketAnalysis,
        competition_analysis: CompetitionAnalysis,
        profit_analysis: ProfitAnalysis,
        evaluation_result: EvaluationResult
    ) -> LlmAgent:
        """
        Create report generator agent with all results.

        Args:
            request: Original request
            trend_analysis: Trend analysis results
            market_analysis: Market analysis results
            competition_analysis: Competition analysis results
            profit_analysis: Profit analysis results
            evaluation_result: Evaluation results

        Returns:
            Configured report agent
        """
        return self._report_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            trend_analysis=trend_analysis.to_json(),
            market_analysis=market_analysis.to_json(),
            competition_analysis=competition_analysis.to_json(),
            profit_analysis=profit_analysis.to_json(),
            evaluation_result=evaluation_result.to_json()
        )

    def build_full_pipeline(self, request: AnalysisRequest) -> SequentialAgent:
        """
        Build the complete analysis pipeline as a SequentialAgent.

        Note: This creates the structural pipeline. Dynamic evaluation
        and report generation require intermediate results, so they
        need to be handled by a workflow runner.

        Args:
            request: Analysis request

        Returns:
            SequentialAgent containing the full pipeline structure
        """
        agents_dict = self.create_pipeline_agents(request)

        return SequentialAgent(
            name="product_analysis_pipeline",
            sub_agents=[agents_dict["parallel_agent"]],
            description="Complete product opportunity analysis pipeline"
        )

    def get_state_from_session(self, session: Session) -> AnalysisState:
        """
        Extract analysis state from ADK session.

        Args:
            session: ADK session

        Returns:
            AnalysisState from session
        """
        return AnalysisState.from_session_dict(session.state)

    def update_session_state(
        self,
        session: Session,
        state: AnalysisState
    ) -> None:
        """
        Update ADK session with analysis state.

        Args:
            session: ADK session
            state: Analysis state to save
        """
        session_dict = state.to_session_dict()
        for key, value in session_dict.items():
            session.state[key] = value


def create_pipeline(
    settings: Optional[Settings] = None,
    on_phase_complete: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> AnalysisPipeline:
    """
    Factory function to create an analysis pipeline.

    Args:
        settings: Application settings
        on_phase_complete: Callback for phase completion

    Returns:
        Configured AnalysisPipeline
    """
    return AnalysisPipeline(settings, on_phase_complete)


def get_pipeline_phases() -> List[str]:
    """
    Get list of pipeline phases.

    Returns:
        List of phase names in order
    """
    return [
        "initialized",
        "analyzing_trends",
        "analyzing_market",
        "analyzing_competition",
        "analyzing_profit",
        "evaluating",
        "generating_report",
        "completed"
    ]


def get_phase_description(phase: str) -> str:
    """
    Get human-readable description for a phase.

    Args:
        phase: Phase name

    Returns:
        Phase description
    """
    descriptions = {
        "initialized": "Pipeline initialized, ready to start",
        "analyzing_trends": "Analyzing market trends and search patterns",
        "analyzing_market": "Analyzing market size and customer segments",
        "analyzing_competition": "Analyzing competitors and pricing",
        "analyzing_profit": "Analyzing profitability and ROI",
        "evaluating": "Evaluating overall opportunity",
        "generating_report": "Generating final report",
        "completed": "Analysis complete",
        "failed": "Analysis failed"
    }
    return descriptions.get(phase, "Unknown phase")
