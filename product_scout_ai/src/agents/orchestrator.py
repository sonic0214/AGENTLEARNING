"""
Orchestrator agent for ProductScout AI.

This module defines the main orchestrator that coordinates
all analysis agents using ADK's multi-agent patterns.
"""
from typing import Optional, List, Dict, Any
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

from src.config.settings import Settings
from src.config.prompts import ORCHESTRATOR_INSTRUCTION, format_prompt
from src.schemas.input_schemas import AnalysisRequest

from .base_agent import BaseAnalysisAgent, AgentConfig
from .analysis_agents import (
    TrendAgent,
    MarketAgent,
    CompetitionAgent,
    ProfitAgent,
)
from .evaluator_agents import EvaluatorAgent, ReportAgent


class OrchestratorAgent(BaseAnalysisAgent):
    """
    Main orchestrator agent for the analysis pipeline.

    Coordinates the multi-agent workflow:
    1. Parallel execution of 4 analysis agents
    2. Sequential evaluation of results
    3. Report generation

    Uses ADK's ParallelAgent and SequentialAgent patterns.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize OrchestratorAgent."""
        config = AgentConfig(
            name="orchestrator_agent",
            description="Orchestrates the multi-agent product analysis workflow",
            instruction_template=ORCHESTRATOR_INSTRUCTION,
            tools=[],
            output_key="orchestrator_result"
        )
        super().__init__(config, settings)

        # Sub-agents (created lazily)
        self._trend_agent: Optional[TrendAgent] = None
        self._market_agent: Optional[MarketAgent] = None
        self._competition_agent: Optional[CompetitionAgent] = None
        self._profit_agent: Optional[ProfitAgent] = None
        self._evaluator_agent: Optional[EvaluatorAgent] = None
        self._report_agent: Optional[ReportAgent] = None

    def _create_analysis_agents(self, request: AnalysisRequest) -> List[LlmAgent]:
        """
        Create the four parallel analysis agents.

        Args:
            request: Analysis request with parameters

        Returns:
            List of configured analysis agents
        """
        self._trend_agent = TrendAgent(self.settings)
        self._market_agent = MarketAgent(self.settings)
        self._competition_agent = CompetitionAgent(self.settings)
        self._profit_agent = ProfitAgent(self.settings)

        return [
            self._trend_agent.create_agent(
                category=request.category,
                target_market=request.target_market
            ),
            self._market_agent.create_agent(
                category=request.category,
                target_market=request.target_market
            ),
            self._competition_agent.create_agent(
                category=request.category,
                target_market=request.target_market
            ),
            self._profit_agent.create_agent(
                category=request.category,
                target_market=request.target_market,
                business_model=request.business_model,
                budget_range=request.budget_range
            ),
        ]

    def create_parallel_analysis_agent(self, request: AnalysisRequest) -> ParallelAgent:
        """
        Create ParallelAgent for concurrent analysis execution.

        Args:
            request: Analysis request

        Returns:
            ParallelAgent containing all 4 analysis agents
        """
        analysis_agents = self._create_analysis_agents(request)

        return ParallelAgent(
            name="parallel_analysis",
            sub_agents=analysis_agents,
            description="Executes trend, market, competition, and profit analysis in parallel"
        )

    def create_full_pipeline(self, request: AnalysisRequest) -> SequentialAgent:
        """
        Create the full analysis pipeline.

        The pipeline structure:
        1. ParallelAgent: 4 analysis agents run concurrently
        2. EvaluatorAgent: Synthesizes all results
        3. ReportAgent: Generates final report

        Note: In practice, the evaluator and report agents need
        results from previous stages, so they're created dynamically
        after parallel analysis completes.

        Args:
            request: Analysis request

        Returns:
            SequentialAgent representing the full pipeline
        """
        # Create the parallel analysis stage
        parallel_analysis = self.create_parallel_analysis_agent(request)

        # Create orchestrator instruction with request details
        orchestrator_instruction = format_prompt(
            self.config.instruction_template,
            category=request.category,
            target_market=request.target_market,
            business_model=request.business_model,
            budget_range=request.budget_range
        )

        # Create the orchestrator LlmAgent
        orchestrator_llm = LlmAgent(
            name=self.config.name,
            model=self.settings.MODEL_NAME,
            instruction=orchestrator_instruction,
            description=self.config.description,
        )

        # Return sequential pipeline
        # Note: For dynamic evaluation based on parallel results,
        # we use the SequentialAgent with the orchestrator to coordinate
        return SequentialAgent(
            name="analysis_pipeline",
            sub_agents=[parallel_analysis, orchestrator_llm],
            description="Full product analysis pipeline"
        )

    def create_agent(self, **kwargs) -> LlmAgent:
        """
        Create the orchestrator LlmAgent.

        This creates just the orchestrator agent itself,
        not the full pipeline.
        """
        return super().create_agent(**kwargs)


def create_analysis_pipeline(
    request: AnalysisRequest,
    settings: Optional[Settings] = None
) -> Dict[str, Any]:
    """
    Create the complete analysis pipeline configuration.

    Returns a dictionary containing all pipeline components
    for flexible execution.

    Args:
        request: Analysis request
        settings: Application settings

    Returns:
        Dictionary with pipeline components:
        - parallel_agent: ParallelAgent for concurrent analysis
        - orchestrator: OrchestratorAgent instance
        - request: Original request
    """
    orchestrator = OrchestratorAgent(settings)
    parallel_agent = orchestrator.create_parallel_analysis_agent(request)

    return {
        "parallel_agent": parallel_agent,
        "orchestrator": orchestrator,
        "request": request,
        "settings": settings or Settings()
    }


def get_agent_names() -> List[str]:
    """
    Get list of all agent names in the pipeline.

    Returns:
        List of agent name strings
    """
    return [
        "orchestrator_agent",
        "trend_agent",
        "market_agent",
        "competition_agent",
        "profit_agent",
        "evaluator_agent",
        "report_agent"
    ]


def get_agent_descriptions() -> Dict[str, str]:
    """
    Get descriptions for all agents.

    Returns:
        Dictionary mapping agent names to descriptions
    """
    return {
        "orchestrator_agent": "Coordinates the multi-agent analysis workflow",
        "trend_agent": "Analyzes market trends and seasonality",
        "market_agent": "Analyzes market size and customer segments",
        "competition_agent": "Analyzes competitors and pricing",
        "profit_agent": "Analyzes profitability and ROI",
        "evaluator_agent": "Synthesizes analyses into overall evaluation",
        "report_agent": "Generates comprehensive final report"
    }
