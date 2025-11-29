"""
Tests for agents/evaluator_agents.py
"""
import pytest
from unittest.mock import Mock, patch

from src.agents.evaluator_agents import (
    EvaluatorAgent,
    ReportAgent,
    create_evaluator_agent,
    create_report_agent,
)
from src.config.settings import Settings


class TestEvaluatorAgent:
    """Test cases for EvaluatorAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analysis results."""
        return {
            "trend_analysis": '{"trend_score": 75, "trend_direction": "rising"}',
            "market_analysis": '{"market_score": 70, "maturity_level": "growing"}',
            "competition_analysis": '{"competition_score": 60, "entry_barriers": "medium"}',
            "profit_analysis": '{"profit_score": 65, "margins": {"net_margin": 0.25}}'
        }

    def test_evaluator_agent_initialization(self, mock_settings):
        """Test EvaluatorAgent initialization."""
        agent = EvaluatorAgent(mock_settings)

        assert agent.name == "evaluator_agent"
        assert "evaluat" in agent.description.lower()
        assert agent.get_output_key() == "evaluation_result"

    @patch('src.agents.base_agent.LlmAgent')
    def test_evaluator_agent_create(self, mock_llm, mock_settings, sample_analyses):
        """Test EvaluatorAgent creation with analysis results."""
        agent = EvaluatorAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="portable blender",
            target_market="US",
            **sample_analyses
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "evaluator_agent"
        assert "portable blender" in call_kwargs["instruction"]

    def test_evaluator_agent_no_tools(self, mock_settings):
        """Test EvaluatorAgent has no external tools."""
        agent = EvaluatorAgent(mock_settings)

        # Evaluator doesn't need external tools
        assert agent.config.tools == []


class TestReportAgent:
    """Test cases for ReportAgent."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_results(self):
        """Create sample analysis and evaluation results."""
        return {
            "trend_analysis": '{"trend_score": 75}',
            "market_analysis": '{"market_score": 70}',
            "competition_analysis": '{"competition_score": 60}',
            "profit_analysis": '{"profit_score": 65}',
            "evaluation_result": '{"opportunity_score": 68, "recommendation": "go"}'
        }

    def test_report_agent_initialization(self, mock_settings):
        """Test ReportAgent initialization."""
        agent = ReportAgent(mock_settings)

        assert agent.name == "report_agent"
        assert "report" in agent.description.lower()
        assert agent.get_output_key() == "final_report"

    @patch('src.agents.base_agent.LlmAgent')
    def test_report_agent_create(self, mock_llm, mock_settings, sample_results):
        """Test ReportAgent creation with all results."""
        agent = ReportAgent(mock_settings)
        llm_agent = agent.create_agent(
            category="smart watch",
            target_market="EU",
            **sample_results
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]

        assert call_kwargs["name"] == "report_agent"
        assert "smart watch" in call_kwargs["instruction"]

    def test_report_agent_no_tools(self, mock_settings):
        """Test ReportAgent has no external tools."""
        agent = ReportAgent(mock_settings)

        assert agent.config.tools == []


class TestFactoryFunctions:
    """Test cases for factory functions."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analyses."""
        return {
            "trend_analysis": '{"trend_score": 75}',
            "market_analysis": '{"market_score": 70}',
            "competition_analysis": '{"competition_score": 60}',
            "profit_analysis": '{"profit_score": 65}'
        }

    @patch('src.agents.base_agent.LlmAgent')
    def test_create_evaluator_agent(self, mock_llm, mock_settings, sample_analyses):
        """Test create_evaluator_agent factory."""
        agent = create_evaluator_agent(
            category="test product",
            target_market="US",
            settings=mock_settings,
            **sample_analyses
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "evaluator_agent"

    @patch('src.agents.base_agent.LlmAgent')
    def test_create_report_agent(self, mock_llm, mock_settings, sample_analyses):
        """Test create_report_agent factory."""
        evaluation_result = '{"opportunity_score": 70, "recommendation": "cautious"}'

        agent = create_report_agent(
            category="gadget",
            target_market="UK",
            evaluation_result=evaluation_result,
            settings=mock_settings,
            **sample_analyses
        )

        mock_llm.assert_called_once()
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs["name"] == "report_agent"
