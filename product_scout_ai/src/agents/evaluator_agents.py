"""
Evaluator and Report agents for ProductScout AI.

This module defines:
- EvaluatorAgent: Synthesizes all analyses into overall evaluation
- ReportAgent: Generates final comprehensive report
"""
from typing import Optional, Dict, Any
from google.adk.agents import LlmAgent

from src.config.settings import Settings
from src.config.prompts import (
    EVALUATOR_AGENT_INSTRUCTION,
    REPORT_AGENT_INSTRUCTION,
    format_prompt,
)
from .base_agent import BaseAnalysisAgent, AgentConfig


class EvaluatorAgent(BaseAnalysisAgent):
    """
    Agent for evaluating overall opportunity.

    Synthesizes results from all analysis agents to produce:
    - Overall opportunity score
    - SWOT analysis
    - Go/No-Go recommendation
    - Risk assessment
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize EvaluatorAgent."""
        config = AgentConfig(
            name="evaluator_agent",
            description="Evaluates overall opportunity by synthesizing all analysis results",
            instruction_template=EVALUATOR_AGENT_INSTRUCTION,
            tools=[],  # Evaluator doesn't need external tools
            output_key="evaluation_result"
        )
        super().__init__(config, settings)

    def create_agent(
        self,
        category: str,
        target_market: str,
        trend_analysis: str,
        market_analysis: str,
        competition_analysis: str,
        profit_analysis: str,
        **kwargs
    ) -> LlmAgent:
        """
        Create evaluator agent with all analysis results.

        Args:
            category: Product category
            target_market: Target market
            trend_analysis: JSON string of trend analysis
            market_analysis: JSON string of market analysis
            competition_analysis: JSON string of competition analysis
            profit_analysis: JSON string of profit analysis

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            trend_analysis=trend_analysis,
            market_analysis=market_analysis,
            competition_analysis=competition_analysis,
            profit_analysis=profit_analysis,
            **kwargs
        )


class ReportAgent(BaseAnalysisAgent):
    """
    Agent for generating final report.

    Creates comprehensive markdown report including:
    - Executive summary
    - Detailed analysis results
    - Recommendations
    - Action items
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize ReportAgent."""
        config = AgentConfig(
            name="report_agent",
            description="Generates comprehensive analysis report in markdown format",
            instruction_template=REPORT_AGENT_INSTRUCTION,
            tools=[],  # Report agent doesn't need external tools
            output_key="final_report"
        )
        super().__init__(config, settings)

    def create_agent(
        self,
        category: str,
        target_market: str,
        trend_analysis: str,
        market_analysis: str,
        competition_analysis: str,
        profit_analysis: str,
        evaluation_result: str,
        **kwargs
    ) -> LlmAgent:
        """
        Create report agent with all analysis and evaluation results.

        Args:
            category: Product category
            target_market: Target market
            trend_analysis: JSON string of trend analysis
            market_analysis: JSON string of market analysis
            competition_analysis: JSON string of competition analysis
            profit_analysis: JSON string of profit analysis
            evaluation_result: JSON string of evaluation result

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            trend_analysis=trend_analysis,
            market_analysis=market_analysis,
            competition_analysis=competition_analysis,
            profit_analysis=profit_analysis,
            evaluation_result=evaluation_result,
            **kwargs
        )


# Factory functions
def create_evaluator_agent(
    category: str,
    target_market: str,
    trend_analysis: str,
    market_analysis: str,
    competition_analysis: str,
    profit_analysis: str,
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create an evaluator agent.

    Args:
        category: Product category
        target_market: Target market
        trend_analysis: Trend analysis results (JSON string)
        market_analysis: Market analysis results (JSON string)
        competition_analysis: Competition analysis results (JSON string)
        profit_analysis: Profit analysis results (JSON string)
        settings: Application settings

    Returns:
        Configured evaluator agent
    """
    agent = EvaluatorAgent(settings)
    return agent.create_agent(
        category=category,
        target_market=target_market,
        trend_analysis=trend_analysis,
        market_analysis=market_analysis,
        competition_analysis=competition_analysis,
        profit_analysis=profit_analysis
    )


def create_report_agent(
    category: str,
    target_market: str,
    trend_analysis: str,
    market_analysis: str,
    competition_analysis: str,
    profit_analysis: str,
    evaluation_result: str,
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create a report agent.

    Args:
        category: Product category
        target_market: Target market
        trend_analysis: Trend analysis results (JSON string)
        market_analysis: Market analysis results (JSON string)
        competition_analysis: Competition analysis results (JSON string)
        profit_analysis: Profit analysis results (JSON string)
        evaluation_result: Evaluation results (JSON string)
        settings: Application settings

    Returns:
        Configured report agent
    """
    agent = ReportAgent(settings)
    return agent.create_agent(
        category=category,
        target_market=target_market,
        trend_analysis=trend_analysis,
        market_analysis=market_analysis,
        competition_analysis=competition_analysis,
        profit_analysis=profit_analysis,
        evaluation_result=evaluation_result
    )
