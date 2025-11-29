"""
Tests for agents/orchestrator.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.orchestrator import (
    OrchestratorAgent,
    create_analysis_pipeline,
    get_agent_names,
    get_agent_descriptions,
)
from src.schemas.input_schemas import AnalysisRequest
from src.config.settings import Settings


class TestOrchestratorAgent:
    """Test cases for OrchestratorAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba",
            keywords=["mini blender", "travel blender"]
        )

    def test_orchestrator_initialization(self, mock_settings):
        """Test OrchestratorAgent initialization."""
        orchestrator = OrchestratorAgent(mock_settings)

        assert orchestrator.name == "orchestrator_agent"
        assert "orchestrat" in orchestrator.description.lower()
        assert orchestrator.get_output_key() == "orchestrator_result"

    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_analysis_agents(self, mock_search, mock_llm, mock_settings, sample_request):
        """Test _create_analysis_agents creates 4 agents."""
        orchestrator = OrchestratorAgent(mock_settings)
        agents = orchestrator._create_analysis_agents(sample_request)

        assert len(agents) == 4
        assert mock_llm.call_count == 4

    @patch('src.agents.orchestrator.ParallelAgent')
    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_parallel_analysis_agent(self, mock_search, mock_llm, mock_parallel, mock_settings, sample_request):
        """Test create_parallel_analysis_agent."""
        orchestrator = OrchestratorAgent(mock_settings)
        parallel_agent = orchestrator.create_parallel_analysis_agent(sample_request)

        mock_parallel.assert_called_once()
        call_kwargs = mock_parallel.call_args[1]

        assert call_kwargs["name"] == "parallel_analysis"
        assert len(call_kwargs["sub_agents"]) == 4

    @patch('src.agents.orchestrator.SequentialAgent')
    @patch('src.agents.orchestrator.ParallelAgent')
    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_full_pipeline(self, mock_search, mock_llm, mock_parallel, mock_sequential, mock_settings, sample_request):
        """Test create_full_pipeline."""
        orchestrator = OrchestratorAgent(mock_settings)
        pipeline = orchestrator.create_full_pipeline(sample_request)

        mock_sequential.assert_called_once()
        call_kwargs = mock_sequential.call_args[1]

        assert call_kwargs["name"] == "analysis_pipeline"
        assert len(call_kwargs["sub_agents"]) == 2  # parallel + orchestrator

    @patch('src.agents.base_agent.LlmAgent')
    def test_create_agent(self, mock_llm, mock_settings):
        """Test create_agent creates the orchestrator LlmAgent."""
        orchestrator = OrchestratorAgent(mock_settings)
        agent = orchestrator.create_agent(
            category="test",
            target_market="US",
            business_model="amazon_fba",
            budget_range="medium"
        )

        mock_llm.assert_called_once()


class TestCreateAnalysisPipeline:
    """Test cases for create_analysis_pipeline function."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="smart watch",
            target_market="EU"
        )

    @patch('src.agents.orchestrator.ParallelAgent')
    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_analysis_pipeline(self, mock_search, mock_llm, mock_parallel, mock_settings, sample_request):
        """Test create_analysis_pipeline returns proper structure."""
        result = create_analysis_pipeline(sample_request, mock_settings)

        assert "parallel_agent" in result
        assert "orchestrator" in result
        assert "request" in result
        assert "settings" in result

        assert result["request"] == sample_request
        assert isinstance(result["orchestrator"], OrchestratorAgent)

    @patch('src.agents.orchestrator.ParallelAgent')
    @patch('src.agents.base_agent.LlmAgent')
    @patch('src.agents.base_agent.google_search')
    def test_create_analysis_pipeline_default_settings(self, mock_search, mock_llm, mock_parallel, sample_request):
        """Test create_analysis_pipeline with default settings."""
        result = create_analysis_pipeline(sample_request)

        assert "settings" in result
        # Should create default Settings
        assert result["settings"] is not None


class TestGetAgentNames:
    """Test cases for get_agent_names function."""

    def test_get_agent_names_returns_all(self):
        """Test get_agent_names returns all agent names."""
        names = get_agent_names()

        expected_names = [
            "orchestrator_agent",
            "trend_agent",
            "market_agent",
            "competition_agent",
            "profit_agent",
            "evaluator_agent",
            "report_agent"
        ]

        assert len(names) == 7
        for name in expected_names:
            assert name in names

    def test_get_agent_names_returns_list(self):
        """Test get_agent_names returns a list."""
        names = get_agent_names()

        assert isinstance(names, list)
        assert all(isinstance(name, str) for name in names)


class TestGetAgentDescriptions:
    """Test cases for get_agent_descriptions function."""

    def test_get_agent_descriptions_returns_dict(self):
        """Test get_agent_descriptions returns a dict."""
        descriptions = get_agent_descriptions()

        assert isinstance(descriptions, dict)

    def test_get_agent_descriptions_has_all_agents(self):
        """Test descriptions include all agents."""
        descriptions = get_agent_descriptions()
        names = get_agent_names()

        for name in names:
            assert name in descriptions
            assert len(descriptions[name]) > 0

    def test_descriptions_are_meaningful(self):
        """Test descriptions contain relevant keywords."""
        descriptions = get_agent_descriptions()

        # Check some key descriptions contain expected keywords
        assert "orchestrat" in descriptions["orchestrator_agent"].lower() or "coordinat" in descriptions["orchestrator_agent"].lower()
        assert "trend" in descriptions["trend_agent"].lower()
        assert "market" in descriptions["market_agent"].lower()
        assert "compet" in descriptions["competition_agent"].lower()
        assert "profit" in descriptions["profit_agent"].lower()
        assert "evaluat" in descriptions["evaluator_agent"].lower()
        assert "report" in descriptions["report_agent"].lower()
