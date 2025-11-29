"""
Agents package for ProductScout AI.

This package contains all agents used in the multi-agent analysis system.
"""
from .base_agent import (
    BaseAnalysisAgent,
    AgentConfig,
    create_analysis_agent,
    validate_agent_output,
    extract_json_from_response,
)

from .analysis_agents import (
    TrendAgent,
    MarketAgent,
    CompetitionAgent,
    ProfitAgent,
    create_trend_agent,
    create_market_agent,
    create_competition_agent,
    create_profit_agent,
    get_all_analysis_agents,
)

from .evaluator_agents import (
    EvaluatorAgent,
    ReportAgent,
    create_evaluator_agent,
    create_report_agent,
)

from .orchestrator import (
    OrchestratorAgent,
    create_analysis_pipeline,
    get_agent_names,
    get_agent_descriptions,
)

__all__ = [
    # Base agent
    "BaseAnalysisAgent",
    "AgentConfig",
    "create_analysis_agent",
    "validate_agent_output",
    "extract_json_from_response",
    # Analysis agents
    "TrendAgent",
    "MarketAgent",
    "CompetitionAgent",
    "ProfitAgent",
    "create_trend_agent",
    "create_market_agent",
    "create_competition_agent",
    "create_profit_agent",
    "get_all_analysis_agents",
    # Evaluator agents
    "EvaluatorAgent",
    "ReportAgent",
    "create_evaluator_agent",
    "create_report_agent",
    # Orchestrator
    "OrchestratorAgent",
    "create_analysis_pipeline",
    "get_agent_names",
    "get_agent_descriptions",
]
