"""
Specialized analysis agents for ProductScout AI.

This module defines the specialized agents for each analysis dimension:
- TrendAgent: Analyzes market trends
- MarketAgent: Analyzes market size and segments
- CompetitionAgent: Analyzes competition landscape
- ProfitAgent: Analyzes profitability
"""
from typing import Optional, List, Any
from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from src.config.settings import Settings
from src.config.prompts import (
    TREND_AGENT_INSTRUCTION,
    MARKET_AGENT_INSTRUCTION,
    COMPETITION_AGENT_INSTRUCTION,
    PROFIT_AGENT_INSTRUCTION,
    format_prompt,
)
from src.tools.trend_tools import get_trend_tools
from src.tools.market_tools import get_market_tools
from src.tools.competition_tools import get_competition_tools
from src.tools.profit_tools import get_profit_tools

from .base_agent import BaseAnalysisAgent, AgentConfig


class TrendAgent(BaseAnalysisAgent):
    """
    Agent for analyzing market trends.

    Uses Google Search to analyze:
    - Search volume trends
    - Seasonality patterns
    - Related queries
    - Trend direction
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize TrendAgent."""
        config = AgentConfig(
            name="trend_agent",
            description="Analyzes market trends, search patterns, and seasonality for product categories",
            instruction_template=TREND_AGENT_INSTRUCTION,
            tools=[google_search],
            output_key="trend_analysis"
        )
        super().__init__(config, settings)

    def create_agent(self, category: str, target_market: str, **kwargs) -> LlmAgent:
        """
        Create trend analysis agent.

        Args:
            category: Product category to analyze
            target_market: Target market (country code)

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            **kwargs
        )


class MarketAgent(BaseAnalysisAgent):
    """
    Agent for analyzing market size and segments.

    Analyzes:
    - TAM/SAM/SOM estimates
    - Growth rate
    - Market maturity
    - Customer segments
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize MarketAgent."""
        config = AgentConfig(
            name="market_agent",
            description="Analyzes market size, growth potential, and customer segments",
            instruction_template=MARKET_AGENT_INSTRUCTION,
            tools=[google_search],
            output_key="market_analysis"
        )
        super().__init__(config, settings)

    def create_agent(self, category: str, target_market: str, **kwargs) -> LlmAgent:
        """
        Create market analysis agent.

        Args:
            category: Product category to analyze
            target_market: Target market (country code)

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            **kwargs
        )


class CompetitionAgent(BaseAnalysisAgent):
    """
    Agent for analyzing competition landscape.

    Analyzes:
    - Key competitors
    - Pricing strategies
    - Market entry barriers
    - Competitive opportunities
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize CompetitionAgent."""
        config = AgentConfig(
            name="competition_agent",
            description="Analyzes competitors, pricing, and market entry barriers",
            instruction_template=COMPETITION_AGENT_INSTRUCTION,
            tools=[google_search],
            output_key="competition_analysis"
        )
        super().__init__(config, settings)

    def create_agent(self, category: str, target_market: str, **kwargs) -> LlmAgent:
        """
        Create competition analysis agent.

        Args:
            category: Product category to analyze
            target_market: Target market (country code)

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            **kwargs
        )


class ProfitAgent(BaseAnalysisAgent):
    """
    Agent for analyzing profitability.

    Analyzes:
    - Unit economics
    - Profit margins
    - ROI projections
    - Investment requirements
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize ProfitAgent."""
        config = AgentConfig(
            name="profit_agent",
            description="Analyzes profitability, unit economics, and ROI potential",
            instruction_template=PROFIT_AGENT_INSTRUCTION,
            tools=[google_search],
            output_key="profit_analysis"
        )
        super().__init__(config, settings)

    def create_agent(
        self,
        category: str,
        target_market: str,
        business_model: str = "amazon_fba",
        budget_range: str = "medium",
        **kwargs
    ) -> LlmAgent:
        """
        Create profit analysis agent.

        Args:
            category: Product category to analyze
            target_market: Target market (country code)
            business_model: Business model (amazon_fba, dropshipping, etc.)
            budget_range: Budget range (low, medium, high)

        Returns:
            Configured LlmAgent
        """
        return super().create_agent(
            category=category,
            target_market=target_market,
            business_model=business_model,
            budget_range=budget_range,
            **kwargs
        )


# Factory functions for creating agents
def create_trend_agent(
    category: str,
    target_market: str,
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create a trend analysis agent.

    Args:
        category: Product category
        target_market: Target market
        settings: Application settings

    Returns:
        Configured trend analysis agent
    """
    agent = TrendAgent(settings)
    return agent.create_agent(category=category, target_market=target_market)


def create_market_agent(
    category: str,
    target_market: str,
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create a market analysis agent.

    Args:
        category: Product category
        target_market: Target market
        settings: Application settings

    Returns:
        Configured market analysis agent
    """
    agent = MarketAgent(settings)
    return agent.create_agent(category=category, target_market=target_market)


def create_competition_agent(
    category: str,
    target_market: str,
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create a competition analysis agent.

    Args:
        category: Product category
        target_market: Target market
        settings: Application settings

    Returns:
        Configured competition analysis agent
    """
    agent = CompetitionAgent(settings)
    return agent.create_agent(category=category, target_market=target_market)


def create_profit_agent(
    category: str,
    target_market: str,
    business_model: str = "amazon_fba",
    budget_range: str = "medium",
    settings: Optional[Settings] = None
) -> LlmAgent:
    """
    Factory function to create a profit analysis agent.

    Args:
        category: Product category
        target_market: Target market
        business_model: Business model
        budget_range: Budget range
        settings: Application settings

    Returns:
        Configured profit analysis agent
    """
    agent = ProfitAgent(settings)
    return agent.create_agent(
        category=category,
        target_market=target_market,
        business_model=business_model,
        budget_range=budget_range
    )


def get_all_analysis_agents(
    category: str,
    target_market: str,
    business_model: str = "amazon_fba",
    budget_range: str = "medium",
    settings: Optional[Settings] = None
) -> List[LlmAgent]:
    """
    Create all four analysis agents.

    Args:
        category: Product category
        target_market: Target market
        business_model: Business model
        budget_range: Budget range
        settings: Application settings

    Returns:
        List of configured analysis agents
    """
    return [
        create_trend_agent(category, target_market, settings),
        create_market_agent(category, target_market, settings),
        create_competition_agent(category, target_market, settings),
        create_profit_agent(category, target_market, business_model, budget_range, settings),
    ]
