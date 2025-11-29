"""
Tests for agents/analysis_agents.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.analysis_agents import (
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
from src.config.settings import Settings


class TestTrendAgent:
    """Test cases for TrendAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    def test_trend_agent_initialization(self, mock_settings):
        """Test TrendAgent initialization."""
        agent = TrendAgent(mock_settings)

        assert agent.name == "trend_agent"
        assert "trend" in agent.description.lower()
        assert agent.get_output_key() == "trend_analysis"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_trend_agent_create(self, mock_search, mock_llm, mock_settings):
        """Test TrendAgent creation."""
        agent = TrendAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="portable blender",
            target_market="US"
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "trend_agent"
        assert "portable blender" in call_kwargs["instruction"]
        assert "US" in call_kwargs["instruction"]


class TestMarketAgent:
    """Test cases for MarketAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    def test_market_agent_initialization(self, mock_settings):
        """Test MarketAgent initialization."""
        agent = MarketAgent(mock_settings)

        assert agent.name == "market_agent"
        assert "market" in agent.description.lower()
        assert agent.get_output_key() == "market_analysis"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_market_agent_create(self, mock_search, mock_llm, mock_settings):
        """Test MarketAgent creation."""
        agent = MarketAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="smart watch",
            target_market="EU"
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "market_agent"
        assert "smart watch" in call_kwargs["instruction"]


class TestCompetitionAgent:
    """Test cases for CompetitionAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    def test_competition_agent_initialization(self, mock_settings):
        """Test CompetitionAgent initialization."""
        agent = CompetitionAgent(mock_settings)

        assert agent.name == "competition_agent"
        assert "compet" in agent.description.lower()
        assert agent.get_output_key() == "competition_analysis"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_competition_agent_create(self, mock_search, mock_llm, mock_settings):
        """Test CompetitionAgent creation."""
        agent = CompetitionAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="fitness tracker",
            target_market="UK"
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "competition_agent"


class TestProfitAgent:
    """Test cases for ProfitAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    def test_profit_agent_initialization(self, mock_settings):
        """Test ProfitAgent initialization."""
        agent = ProfitAgent(mock_settings)

        assert agent.name == "profit_agent"
        assert "profit" in agent.description.lower()
        assert agent.get_output_key() == "profit_analysis"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_profit_agent_create(self, mock_search, mock_llm, mock_settings):
        """Test ProfitAgent creation with all parameters."""
        agent = ProfitAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="electronics",
            target_market="US",
            business_model="dropshipping",
            budget_range="high"
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "profit_agent"
        assert "electronics" in call_kwargs["instruction"]

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_profit_agent_default_business_model(self, mock_search, mock_llm, mock_settings):
        """Test ProfitAgent with default business model."""
        agent = ProfitAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="test",
            target_market="US"
        )

        # Should work without specifying business_model and budget_range
        mock_llm.assert_called_once()


class TestFactoryFunctions:
    """Test cases for factory functions."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_trend_agent(self, mock_search, mock_llm, mock_settings):
        """Test create_trend_agent factory."""
        agent = create_trend_agent("blender", "US", mock_settings)

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "trend_agent"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_market_agent(self, mock_search, mock_llm, mock_settings):
        """Test create_market_agent factory."""
        agent = create_market_agent("watch", "UK", mock_settings)

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "market_agent"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_competition_agent(self, mock_search, mock_llm, mock_settings):
        """Test create_competition_agent factory."""
        agent = create_competition_agent("headphones", "EU", mock_settings)

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "competition_agent"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_profit_agent(self, mock_search, mock_llm, mock_settings):
        """Test create_profit_agent factory."""
        agent = create_profit_agent(
            "gadget",
            "US",
            "amazon_fba",
            "medium",
            mock_settings
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "profit_agent"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_get_all_analysis_agents(self, mock_search, mock_llm, mock_settings):
        """Test get_all_analysis_agents returns all 4 agents."""
        agents = get_all_analysis_agents(
            category="product",
            target_market="US",
            settings=mock_settings
        )

        assert len(agents) == 4
        assert mock_llm.call_count == 4

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_get_all_analysis_agents_with_params(self, mock_search, mock_llm, mock_settings):
        """Test get_all_analysis_agents with all parameters."""
        agents = get_all_analysis_agents(
            category="electronics",
            target_market="EU",
            business_model="dropshipping",
            budget_range="high",
            settings=mock_settings
        )

        assert len(agents) == 4


class TestAgentTools:
    """Test cases for agent tools configuration."""

    @pytest.fixture
    def mock_settings(self):
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_agents_have_google_search(self, mock_search, mock_llm, mock_settings):
        """Test all analysis agents have google_search tool."""
        agents_classes = [TrendAgent, MarketAgent, CompetitionAgent, ProfitAgent]

        for AgentClass in agents_classes:
            mock_llm.reset_mock()
            agent = AgentClass(mock_settings)

            if AgentClass == ProfitAgent:
                agent.create_agent("test", "US", "amazon_fba", "medium")
            else:
                agent.create_agent("test", "US")

            call_kwargs = mock_llm.call_args[1]
            assert "tools" in call_kwargs
            assert mock_search in call_kwargs["tools"]
