"""
Integration tests for the pipeline system.

These tests verify that multiple components work together correctly.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import (
    AnalysisPipeline,
    PipelineResult,
    create_pipeline,
    get_pipeline_phases,
)
from src.workflows.runner import PipelineRunner, RunnerConfig, create_runner
from src.services.analysis_service import (
    AnalysisService,
    AnalysisServiceConfig,
    create_analysis_service,
)
from src.services.history_service import HistoryService, create_history_service
from src.services.export_service import ExportService, export_to_json, export_to_markdown


class TestPipelineAgentIntegration:
    """Test pipeline and agent integration."""

    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings."""
        settings = Mock(spec=Settings)
        settings.MODEL_NAME = "gemini-2.0-flash"
        return settings

    def test_pipeline_creates_all_agents(self, sample_request, mock_settings):
        """Test pipeline creates all required agents."""
        pipeline = create_pipeline(settings=mock_settings)
        agents = pipeline.create_pipeline_agents(sample_request)

        assert "parallel_agent" in agents
        assert "trend_agent" in agents
        assert "market_agent" in agents
        assert "competition_agent" in agents
        assert "profit_agent" in agents
        assert agents["request"] == sample_request

    def test_pipeline_phases_are_complete(self):
        """Test all expected phases are defined."""
        phases = get_pipeline_phases()

        expected_phases = [
            "initialized",
            "analyzing_trends",
            "analyzing_market",
            "analyzing_competition",
            "analyzing_profit",
            "evaluating",
            "generating_report",
            "completed"
        ]

        assert phases == expected_phases


class TestRunnerPipelineIntegration:
    """Test runner and pipeline integration."""

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="smart watch",
            target_market="EU",
            budget_range="high",
            business_model="private_label"
        )

    def test_runner_creates_pipeline(self):
        """Test runner can create and initialize pipeline."""
        runner = create_runner()
        pipeline = runner.initialize_pipeline()

        assert pipeline is not None
        assert isinstance(pipeline, AnalysisPipeline)

    def test_runner_with_custom_config(self):
        """Test runner accepts custom configuration."""
        config = RunnerConfig(
            app_name="test_app",
            max_retries=5,
            timeout_seconds=300
        )
        runner = create_runner(config=config)

        assert runner.config.app_name == "test_app"
        assert runner.config.max_retries == 5
        assert runner.config.timeout_seconds == 300

    @pytest.mark.asyncio
    @patch('src.workflows.runner.Runner')
    @patch('src.workflows.runner.InMemorySessionService')
    async def test_runner_executes_analysis(self, mock_session_service, mock_runner_class, sample_request):
        """Test runner executes analysis successfully."""
        mock_service = Mock()
        mock_session = Mock()
        mock_service.create_session.return_value = mock_session
        mock_session_service.return_value = mock_service

        runner = create_runner()
        result = await runner.run_analysis(sample_request)

        assert result is not None
        assert isinstance(result, PipelineResult)
        assert result.state is not None


class TestServicePipelineIntegration:
    """Test service and pipeline integration."""

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="gaming mouse",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    @pytest.fixture
    def mock_result(self):
        """Create mock pipeline result."""
        state = AnalysisState()
        state.trend_analysis = TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={},
            related_queries=[]
        )
        return PipelineResult(
            success=True,
            state=state,
            execution_time=5.0
        )

    @patch('src.services.analysis_service.PipelineRunner')
    def test_service_creates_runner(self, mock_runner_class):
        """Test service creates runner correctly."""
        service = create_analysis_service()

        mock_runner_class.assert_called_once()
        assert service is not None

    @patch('src.services.analysis_service.PipelineRunner')
    def test_service_accepts_config(self, mock_runner_class):
        """Test service accepts configuration."""
        config = AnalysisServiceConfig(
            enable_caching=True,
            max_concurrent_analyses=10
        )
        service = create_analysis_service(config=config)

        assert service.config.enable_caching is True
        assert service.config.max_concurrent_analyses == 10

    @pytest.mark.asyncio
    @patch('src.services.analysis_service.PipelineRunner')
    async def test_service_runs_analysis(self, mock_runner_class, sample_request, mock_result):
        """Test service runs analysis through pipeline."""
        mock_runner = Mock()
        mock_runner.run_analysis = AsyncMock(return_value=mock_result)
        mock_runner.initialize_pipeline = Mock()
        mock_runner.create_session = Mock()
        mock_runner_class.return_value = mock_runner

        service = create_analysis_service()
        result = await service.analyze(sample_request)

        assert result.success is True
        mock_runner.run_analysis.assert_called_once()


class TestHistoryExportIntegration:
    """Test history and export service integration."""

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    @pytest.fixture
    def sample_result(self):
        """Create sample result with full state."""
        state = AnalysisState()
        state.request = AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )
        state.trend_analysis = TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_seasons": ["summer"]},
            related_queries=["mini blender"]
        )
        state.market_analysis = MarketAnalysis(
            market_size={"tam": 1000000000},
            growth_rate=0.15,
            customer_segments=[],
            maturity_level="growing",
            market_score=70
        )
        state.competition_analysis = CompetitionAnalysis(
            competitors=[{"name": "Brand1"}],
            competition_score=60,
            pricing_analysis={"avg_price": 45},
            opportunities=["Budget segment"]
        )
        state.profit_analysis = ProfitAnalysis(
            unit_economics={"retail_price": 50},
            margins={"net_margin": 0.30},
            monthly_projection={"monthly_profit": 3000},
            investment={"total_investment": 5000},
            assessment={"profitable": True},
            profit_score=72
        )
        state.evaluation_result = EvaluationResult(
            opportunity_score=70,
            dimension_scores={"trend": 75, "market": 70},
            swot_analysis={"strengths": ["Growing market"]},
            recommendation="go",
            recommendation_detail="Good opportunity",
            key_risks=["Competition"],
            success_factors=["Differentiation"]
        )

        return PipelineResult(
            success=True,
            state=state,
            execution_time=10.5
        )

    def test_history_stores_and_exports(self, sample_request, sample_result):
        """Test history stores result and export works."""
        history = create_history_service()

        # Add entry
        entry = history.add_entry(sample_request, sample_result)
        assert entry is not None

        # Export to JSON
        json_output = export_to_json(sample_result)
        assert "success" in json_output
        assert "true" in json_output.lower()

        # Export to Markdown
        md_output = export_to_markdown(sample_result)
        assert "# Product Opportunity Analysis Report" in md_output
        assert "portable blender" in md_output

    def test_history_statistics_match_exports(self, sample_request, sample_result):
        """Test history statistics are consistent."""
        history = create_history_service()

        # Add multiple entries
        for _ in range(3):
            history.add_entry(sample_request, sample_result)

        stats = history.get_statistics()

        assert stats["total_analyses"] == 3
        assert stats["successful"] == 3
        assert stats["categories"]["portable blender"] == 3


class TestStateFlowIntegration:
    """Test state flow through the system."""

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return AnalysisRequest(
            category="wireless earbuds",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

    def test_state_preserves_request(self, sample_request):
        """Test state preserves original request."""
        state = AnalysisState(request=sample_request)

        assert state.request == sample_request
        assert state.request.category == "wireless earbuds"

    def test_state_tracks_phase_changes(self, sample_request):
        """Test state tracks phase changes."""
        state = AnalysisState(request=sample_request)

        phases_visited = []

        state.set_phase("initialized")
        phases_visited.append(state.current_phase)

        state.set_phase("analyzing_trends")
        phases_visited.append(state.current_phase)

        state.set_phase("completed")
        phases_visited.append(state.current_phase)

        assert phases_visited == ["initialized", "analyzing_trends", "completed"]

    def test_state_to_session_roundtrip(self, sample_request):
        """Test state survives session roundtrip."""
        state = AnalysisState(request=sample_request)
        state.set_phase("analyzing_market")
        state.trend_analysis = TrendAnalysis(
            trend_score=80,
            trend_direction="rising",
            seasonality={},
            related_queries=[]
        )

        # Convert to session dict
        session_dict = state.to_session_dict()

        # Restore from session dict
        restored_state = AnalysisState.from_session_dict(session_dict)

        assert restored_state.current_phase == "analyzing_market"
        assert restored_state.trend_analysis is not None
        assert restored_state.trend_analysis.trend_score == 80


class TestEndToEndScenarios:
    """End-to-end scenario tests."""

    @pytest.fixture
    def full_state(self):
        """Create fully populated state."""
        request = AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba"
        )

        state = AnalysisState(request=request)
        state.trend_analysis = TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_seasons": ["summer"]},
            related_queries=["mini blender", "travel blender"]
        )
        state.market_analysis = MarketAnalysis(
            market_size={"tam": 1000000000, "sam": 300000000, "som": 50000000},
            growth_rate=0.15,
            customer_segments=["fitness enthusiasts", "travelers"],
            maturity_level="growing",
            market_score=70
        )
        state.competition_analysis = CompetitionAnalysis(
            competitors=[
                {"name": "BlendJet", "market_share": 35},
                {"name": "Nutribullet Go", "market_share": 25}
            ],
            competition_score=60,
            pricing_analysis={"avg_price": 45.00, "price_range": [25, 80]},
            opportunities=["Budget segment", "Premium features"]
        )
        state.profit_analysis = ProfitAnalysis(
            unit_economics={"retail_price": 50, "cost": 20, "profit_per_unit": 15},
            margins={"gross_margin": 0.60, "net_margin": 0.30},
            monthly_projection={"units": 200, "revenue": 10000, "profit": 3000},
            investment={"inventory": 3000, "marketing": 2000, "total": 5000},
            assessment={"profitable": True, "roi": 0.60},
            profit_score=72
        )
        state.evaluation_result = EvaluationResult(
            opportunity_score=70,
            dimension_scores={
                "trend": 75,
                "market": 70,
                "competition": 60,
                "profit": 72
            },
            swot_analysis={
                "strengths": ["Growing market", "Good margins"],
                "weaknesses": ["Competitive market"],
                "opportunities": ["New features", "Budget segment"],
                "threats": ["Price competition"]
            },
            recommendation="go",
            recommendation_detail="Good opportunity with strong fundamentals",
            key_risks=["Competition from established brands", "Price pressure"],
            success_factors=["Product differentiation", "Strong marketing", "Good reviews"]
        )

        return state

    def test_full_analysis_flow(self, full_state):
        """Test complete analysis flow produces valid output."""
        result = PipelineResult(
            success=True,
            state=full_state,
            execution_time=15.5,
            phase_times={
                "trend_analysis": 3.0,
                "market_analysis": 4.0,
                "competition_analysis": 3.5,
                "profit_analysis": 3.0,
                "evaluation": 2.0
            }
        )

        # Verify result structure
        assert result.success is True
        assert result.execution_time == 15.5
        assert len(result.phase_times) == 5

        # Verify state has all analyses
        assert result.state.trend_analysis is not None
        assert result.state.market_analysis is not None
        assert result.state.competition_analysis is not None
        assert result.state.profit_analysis is not None
        assert result.state.evaluation_result is not None

        # Verify scores are in valid range
        assert 0 <= result.state.trend_analysis.trend_score <= 100
        assert 0 <= result.state.market_analysis.market_score <= 100
        assert 0 <= result.state.competition_analysis.competition_score <= 100
        assert 0 <= result.state.profit_analysis.profit_score <= 100
        assert 0 <= result.state.evaluation_result.opportunity_score <= 100

    def test_export_formats_complete(self, full_state):
        """Test all export formats work with full state."""
        result = PipelineResult(
            success=True,
            state=full_state,
            execution_time=15.5
        )

        # JSON export
        json_output = export_to_json(result)
        assert "portable blender" in json_output
        assert "70" in json_output  # opportunity score
        assert "go" in json_output  # recommendation

        # Markdown export
        md_output = export_to_markdown(result)
        assert "# Product Opportunity Analysis Report" in md_output
        assert "portable blender" in md_output
        assert "## Trend Analysis" in md_output
        assert "## Market Analysis" in md_output
        assert "## Competition Analysis" in md_output
        assert "## Profit Analysis" in md_output
        assert "## Evaluation Summary" in md_output
        assert "GO" in md_output  # recommendation

    def test_history_records_complete_analysis(self, full_state):
        """Test history records complete analysis correctly."""
        result = PipelineResult(
            success=True,
            state=full_state,
            execution_time=15.5
        )

        history = create_history_service()
        entry = history.add_entry(full_state.request, result)

        assert entry.success is True
        assert entry.execution_time == 15.5
        assert entry.request.category == "portable blender"

        # Verify search works
        found = history.get_by_category("portable blender")
        assert len(found) == 1
        assert found[0].request.category == "portable blender"
