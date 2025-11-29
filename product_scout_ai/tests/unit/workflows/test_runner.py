"""
Tests for workflows/runner.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime

from src.workflows.runner import (
    PipelineRunner,
    RunnerConfig,
    create_runner,
    quick_analyze,
)
from src.workflows.analysis_pipeline import PipelineResult
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)
from src.schemas.state_schemas import AnalysisState
from src.config.settings import Settings


class TestRunnerConfig:
    """Test cases for RunnerConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RunnerConfig()

        assert config.app_name == "product_scout_ai"
        assert config.max_retries == 3
        assert config.timeout_seconds == 120
        assert config.enable_streaming is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = RunnerConfig(
            app_name="custom_app",
            max_retries=5,
            timeout_seconds=300,
            enable_streaming=False
        )

        assert config.app_name == "custom_app"
        assert config.max_retries == 5
        assert config.timeout_seconds == 300
        assert config.enable_streaming is False

    def test_partial_override(self):
        """Test partial configuration override."""
        config = RunnerConfig(max_retries=10)

        assert config.max_retries == 10
        # Other values should be defaults
        assert config.app_name == "product_scout_ai"
        assert config.enable_streaming is True


class TestPipelineRunner:
    """Test cases for PipelineRunner."""

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
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    def test_runner_initialization_default(self):
        """Test runner initialization with defaults."""
        runner = PipelineRunner()

        assert runner.config is not None
        assert runner.config.app_name == "product_scout_ai"
        assert runner._pipeline is None
        assert runner._current_session is None

    def test_runner_initialization_with_settings(self, mock_settings):
        """Test runner initialization with settings."""
        runner = PipelineRunner(settings=mock_settings)

        assert runner.settings == mock_settings

    def test_runner_initialization_with_config(self):
        """Test runner initialization with config."""
        config = RunnerConfig(app_name="test_app")
        runner = PipelineRunner(config=config)

        assert runner.config.app_name == "test_app"

    @patch('src.workflows.runner.InMemorySessionService')
    def test_create_session(self, mock_session_service):
        """Test session creation."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        runner = PipelineRunner()
        session = runner.create_session(user_id="test_user")

        mock_service.create_session.assert_called_once()
        call_kwargs = mock_service.create_session.call_args[1]
        assert call_kwargs["user_id"] == "test_user"
        assert call_kwargs["app_name"] == "product_scout_ai"
        assert runner._current_session == mock_session

    @patch('src.workflows.runner.InMemorySessionService')
    def test_create_session_anonymous(self, mock_session_service):
        """Test session creation for anonymous user."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        runner = PipelineRunner()
        session = runner.create_session()

        call_kwargs = mock_service.create_session.call_args[1]
        assert call_kwargs["user_id"] == "anonymous"

    @patch('src.workflows.runner.InMemorySessionService')
    def test_get_session(self, mock_session_service):
        """Test getting existing session."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.get_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        runner = PipelineRunner()
        session = runner.get_session("session-123")

        mock_service.get_session.assert_called_once()
        call_kwargs = mock_service.get_session.call_args[1]
        assert call_kwargs["session_id"] == "session-123"

    @patch('src.workflows.runner.AnalysisPipeline')
    def test_initialize_pipeline(self, mock_pipeline_class, mock_settings):
        """Test pipeline initialization."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline

        runner = PipelineRunner(settings=mock_settings)
        pipeline = runner.initialize_pipeline()

        mock_pipeline_class.assert_called_once_with(
            settings=mock_settings,
            on_phase_complete=None
        )
        assert runner._pipeline == mock_pipeline

    @patch('src.workflows.runner.AnalysisPipeline')
    def test_initialize_pipeline_with_callback(self, mock_pipeline_class, mock_settings):
        """Test pipeline initialization with callback."""
        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline
        callback = Mock()

        runner = PipelineRunner(settings=mock_settings)
        pipeline = runner.initialize_pipeline(on_phase_complete=callback)

        call_kwargs = mock_pipeline_class.call_args[1]
        assert call_kwargs["on_phase_complete"] == callback

    @pytest.mark.asyncio
    @patch('src.workflows.runner.AnalysisPipeline')
    @patch('src.workflows.runner.Runner')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_run_analysis_success(
        self, mock_session_service, mock_runner_class, mock_pipeline_class,
        mock_settings, sample_request
    ):
        """Test successful analysis run."""
        # Setup mocks
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        mock_pipeline = Mock()
        mock_pipeline.create_pipeline_agents.return_value = {
            "parallel_agent": Mock()
        }
        mock_pipeline_class.return_value = mock_pipeline

        runner = PipelineRunner(settings=mock_settings)
        result = await runner.run_analysis(sample_request)

        assert result.success is True
        assert result.state is not None
        assert result.execution_time >= 0

    @pytest.mark.asyncio
    @patch('src.workflows.runner.AnalysisPipeline')
    @patch('src.workflows.runner.Runner')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_run_analysis_with_existing_session(
        self, mock_session_service, mock_runner_class, mock_pipeline_class,
        mock_settings, sample_request
    ):
        """Test analysis run with existing session."""
        mock_service = Mock()
        mock_session_service.return_value = mock_service

        mock_pipeline = Mock()
        mock_pipeline.create_pipeline_agents.return_value = {
            "parallel_agent": Mock()
        }
        mock_pipeline_class.return_value = mock_pipeline

        existing_session = Mock()

        runner = PipelineRunner(settings=mock_settings)
        result = await runner.run_analysis(sample_request, session=existing_session)

        # Should not create new session
        mock_service.create_session.assert_not_called()
        assert result.success is True

    @pytest.mark.asyncio
    @patch('src.workflows.runner.AnalysisPipeline')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_run_analysis_failure(
        self, mock_session_service, mock_pipeline_class,
        mock_settings, sample_request
    ):
        """Test analysis run with failure."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        mock_pipeline = Mock()
        mock_pipeline.create_pipeline_agents.side_effect = Exception("Pipeline error")
        mock_pipeline_class.return_value = mock_pipeline

        runner = PipelineRunner(settings=mock_settings)
        result = await runner.run_analysis(sample_request)

        assert result.success is False
        assert result.error == "Pipeline error"

    @pytest.mark.asyncio
    @patch('src.workflows.runner.AnalysisPipeline')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_run_with_streaming(
        self, mock_session_service, mock_pipeline_class,
        mock_settings, sample_request
    ):
        """Test streaming analysis run."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline

        runner = PipelineRunner(settings=mock_settings)

        updates = []
        async for update in runner.run_with_streaming(sample_request):
            updates.append(update)

        assert len(updates) > 0
        assert updates[0]["type"] == "started"
        assert updates[-1]["type"] == "completed"

    @pytest.mark.asyncio
    @patch('src.workflows.runner.AnalysisPipeline')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_streaming_phases(
        self, mock_session_service, mock_pipeline_class,
        mock_settings, sample_request
    ):
        """Test streaming includes all phases."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        mock_pipeline = Mock()
        mock_pipeline_class.return_value = mock_pipeline

        runner = PipelineRunner(settings=mock_settings)

        phases_seen = set()
        async for update in runner.run_with_streaming(sample_request):
            if "phase" in update:
                phases_seen.add(update["phase"])

        # Should have all phases
        expected_phases = {
            "initialized", "analyzing_trends", "analyzing_market",
            "analyzing_competition", "analyzing_profit",
            "evaluating", "generating_report", "completed"
        }
        assert phases_seen == expected_phases

    def test_process_agent_output_trend(self, mock_settings):
        """Test processing trend agent output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '{"trend_score": 75, "trend_direction": "rising", "seasonality": {}, "related_queries": []}'
        updated_state = runner.process_agent_output("trend_agent", output, state)

        assert updated_state.trend_analysis is not None
        assert updated_state.trend_analysis.trend_score == 75

    def test_process_agent_output_market(self, mock_settings):
        """Test processing market agent output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '{"market_size": {"tam": 1000000}, "growth_rate": 0.15, "customer_segments": [], "maturity_level": "growing", "market_score": 70}'
        updated_state = runner.process_agent_output("market_agent", output, state)

        assert updated_state.market_analysis is not None
        assert updated_state.market_analysis.market_score == 70

    def test_process_agent_output_competition(self, mock_settings):
        """Test processing competition agent output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '{"competitors": [], "competition_score": 60, "pricing_analysis": {}, "opportunities": []}'
        updated_state = runner.process_agent_output("competition_agent", output, state)

        assert updated_state.competition_analysis is not None
        assert updated_state.competition_analysis.competition_score == 60

    def test_process_agent_output_profit(self, mock_settings):
        """Test processing profit agent output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '{"unit_economics": {}, "margins": {}, "monthly_projection": {}, "investment": {}, "assessment": {}, "profit_score": 72}'
        updated_state = runner.process_agent_output("profit_agent", output, state)

        assert updated_state.profit_analysis is not None
        assert updated_state.profit_analysis.profit_score == 72

    def test_process_agent_output_evaluator(self, mock_settings):
        """Test processing evaluator agent output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '''
        {
            "opportunity_score": 70,
            "dimension_scores": {},
            "swot_analysis": {},
            "recommendation": "go",
            "recommendation_detail": "Good opportunity",
            "key_risks": [],
            "success_factors": []
        }
        '''
        updated_state = runner.process_agent_output("evaluator_agent", output, state)

        assert updated_state.evaluation_result is not None
        assert updated_state.evaluation_result.opportunity_score == 70

    def test_process_agent_output_invalid_json(self, mock_settings):
        """Test processing invalid JSON output."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = "Not valid JSON"
        updated_state = runner.process_agent_output("trend_agent", output, state)

        # Should not crash, state should be unchanged
        assert updated_state.trend_analysis is None

    def test_process_agent_output_unknown_agent(self, mock_settings):
        """Test processing output from unknown agent."""
        runner = PipelineRunner(settings=mock_settings)
        state = AnalysisState()

        output = '{"some": "data"}'
        updated_state = runner.process_agent_output("unknown_agent", output, state)

        # Should not crash
        assert updated_state is not None


class TestCreateRunner:
    """Test cases for create_runner factory function."""

    def test_create_runner_default(self):
        """Test creating runner with defaults."""
        runner = create_runner()

        assert runner is not None
        assert isinstance(runner, PipelineRunner)
        assert runner.config.app_name == "product_scout_ai"

    def test_create_runner_with_settings(self):
        """Test creating runner with settings."""
        settings = Mock(spec=Settings)
        runner = create_runner(settings=settings)

        assert runner.settings == settings

    def test_create_runner_with_config(self):
        """Test creating runner with config."""
        config = RunnerConfig(app_name="custom_app", max_retries=5)
        runner = create_runner(config=config)

        assert runner.config.app_name == "custom_app"
        assert runner.config.max_retries == 5


class TestQuickAnalyze:
    """Test cases for quick_analyze function."""

    @pytest.mark.asyncio
    @patch('src.workflows.runner.create_runner')
    async def test_quick_analyze_default_params(self, mock_create_runner):
        """Test quick_analyze with default parameters."""
        mock_runner = Mock()
        mock_result = PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_create_runner.return_value = mock_runner

        result = await quick_analyze("portable blender")

        mock_create_runner.assert_called_once()
        mock_runner.run_analysis.assert_called_once()

        call_args = mock_runner.run_analysis.call_args[0][0]
        assert call_args.category == "portable blender"
        assert call_args.target_market == "US"
        assert call_args.business_model == "amazon_fba"
        assert call_args.budget_range == "medium"

    @pytest.mark.asyncio
    @patch('src.workflows.runner.create_runner')
    async def test_quick_analyze_custom_params(self, mock_create_runner):
        """Test quick_analyze with custom parameters."""
        mock_runner = Mock()
        mock_result = PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_create_runner.return_value = mock_runner

        result = await quick_analyze(
            category="smart watch",
            target_market="EU",
            business_model="dropshipping",
            budget_range="high"
        )

        call_args = mock_runner.run_analysis.call_args[0][0]
        assert call_args.category == "smart watch"
        assert call_args.target_market == "EU"
        assert call_args.business_model == "dropshipping"
        assert call_args.budget_range == "high"

    @pytest.mark.asyncio
    @patch('src.workflows.runner.create_runner')
    async def test_quick_analyze_returns_result(self, mock_create_runner):
        """Test quick_analyze returns PipelineResult."""
        mock_runner = Mock()
        mock_result = PipelineResult(
            success=True,
            state=AnalysisState(),
            execution_time=5.0
        )
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_create_runner.return_value = mock_runner

        result = await quick_analyze("test category")

        assert isinstance(result, PipelineResult)
        assert result.success is True
