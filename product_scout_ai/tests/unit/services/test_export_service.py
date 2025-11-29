"""
Tests for services/export_service.py
"""
import pytest
from unittest.mock import Mock
import json

from src.services.export_service import (
    ExportService,
    ExportConfig,
    create_export_service,
    export_to_json,
    export_to_markdown,
)
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)
from src.schemas.state_schemas import AnalysisState
from src.workflows.analysis_pipeline import PipelineResult


class TestExportConfig:
    """Test cases for ExportConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ExportConfig()

        assert config.include_raw_data is True
        assert config.include_timestamps is True
        assert config.pretty_print is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = ExportConfig(
            include_raw_data=False,
            include_timestamps=False,
            pretty_print=False
        )

        assert config.include_raw_data is False
        assert config.include_timestamps is False
        assert config.pretty_print is False


class TestExportService:
    """Test cases for ExportService."""

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
    def sample_trend(self):
        """Create sample trend analysis."""
        return TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_seasons": ["summer"]},
            related_queries=["mini blender"]
        )

    @pytest.fixture
    def sample_market(self):
        """Create sample market analysis."""
        return MarketAnalysis(
            market_size={"tam": 1000000000},
            growth_rate=0.15,
            customer_segments=[],
            maturity_level="growing",
            market_score=70
        )

    @pytest.fixture
    def sample_competition(self):
        """Create sample competition analysis."""
        return CompetitionAnalysis(
            competitors=[{"name": "Brand1", "market_share": 30}],
            competition_score=60,
            pricing_analysis={"avg_price": 45.00},
            opportunities=["Budget segment"]
        )

    @pytest.fixture
    def sample_profit(self):
        """Create sample profit analysis."""
        return ProfitAnalysis(
            unit_economics={"retail_price": 50},
            margins={"net_margin": 0.30},
            monthly_projection={"monthly_profit": 3000},
            investment={"total_investment": 5000},
            assessment={"profitable": True},
            profit_score=72
        )

    @pytest.fixture
    def sample_evaluation(self):
        """Create sample evaluation."""
        return EvaluationResult(
            opportunity_score=70,
            dimension_scores={"trend": 75, "market": 70},
            swot_analysis={"strengths": ["Growing market"]},
            recommendation="go",
            recommendation_detail="Good opportunity with strong fundamentals",
            key_risks=["Competition", "Price pressure"],
            success_factors=["Differentiation", "Marketing"]
        )

    @pytest.fixture
    def full_state(
        self, sample_request, sample_trend, sample_market,
        sample_competition, sample_profit, sample_evaluation
    ):
        """Create fully populated state."""
        state = AnalysisState(request=sample_request)
        state.trend_analysis = sample_trend
        state.market_analysis = sample_market
        state.competition_analysis = sample_competition
        state.profit_analysis = sample_profit
        state.evaluation_result = sample_evaluation
        return state

    @pytest.fixture
    def full_result(self, full_state):
        """Create full pipeline result."""
        return PipelineResult(
            success=True,
            state=full_state,
            execution_time=10.5,
            phase_times={"analysis": 8.0, "evaluation": 2.5}
        )

    @pytest.fixture
    def failed_result(self):
        """Create failed pipeline result."""
        return PipelineResult(
            success=False,
            state=AnalysisState(),
            error="Analysis failed due to API error",
            execution_time=1.0
        )

    def test_service_initialization(self):
        """Test service initialization."""
        service = ExportService()

        assert service.config is not None

    def test_service_initialization_with_config(self):
        """Test service initialization with config."""
        config = ExportConfig(pretty_print=False)
        service = ExportService(config=config)

        assert service.config.pretty_print is False

    def test_to_json_basic(self, full_result):
        """Test basic JSON export."""
        service = ExportService()

        json_str = service.to_json(full_result)
        data = json.loads(json_str)

        assert data["success"] is True
        assert data["execution_time"] == 10.5

    def test_to_json_includes_timestamps(self, full_result):
        """Test JSON export includes timestamps."""
        service = ExportService()

        json_str = service.to_json(full_result)
        data = json.loads(json_str)

        assert "exported_at" in data

    def test_to_json_without_timestamps(self, full_result):
        """Test JSON export without timestamps."""
        config = ExportConfig(include_timestamps=False)
        service = ExportService(config=config)

        json_str = service.to_json(full_result)
        data = json.loads(json_str)

        assert "exported_at" not in data

    def test_to_json_includes_raw_data(self, full_result):
        """Test JSON export includes raw analysis data."""
        service = ExportService()

        json_str = service.to_json(full_result)
        data = json.loads(json_str)

        assert "analyses" in data
        assert data["analyses"]["trend"] is not None
        assert data["analyses"]["market"] is not None

    def test_to_json_without_raw_data(self, full_result):
        """Test JSON export without raw data."""
        config = ExportConfig(include_raw_data=False)
        service = ExportService(config=config)

        json_str = service.to_json(full_result)
        data = json.loads(json_str)

        assert "analyses" not in data

    def test_to_json_failed_result(self, failed_result):
        """Test JSON export with failed result."""
        service = ExportService()

        json_str = service.to_json(failed_result)
        data = json.loads(json_str)

        assert data["success"] is False
        assert data["error"] == "Analysis failed due to API error"

    def test_to_json_pretty_print(self, full_result):
        """Test JSON is pretty printed."""
        service = ExportService()

        json_str = service.to_json(full_result)

        # Pretty printed JSON should have newlines
        assert "\n" in json_str

    def test_to_json_compact(self, full_result):
        """Test JSON without pretty print."""
        config = ExportConfig(pretty_print=False)
        service = ExportService(config=config)

        json_str = service.to_json(full_result)

        # Compact JSON should not have newlines (except in strings)
        lines = json_str.strip().split("\n")
        assert len(lines) == 1

    def test_to_dict(self, full_result):
        """Test dictionary export."""
        service = ExportService()

        data = service.to_dict(full_result)

        assert isinstance(data, dict)
        assert data["success"] is True
        assert data["execution_time"] == 10.5

    def test_to_markdown_basic(self, full_result):
        """Test basic Markdown export."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "# Product Opportunity Analysis Report" in md
        assert "SUCCESS" in md

    def test_to_markdown_includes_request_info(self, full_result):
        """Test Markdown includes request information."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "portable blender" in md
        assert "US" in md
        assert "amazon_fba" in md

    def test_to_markdown_includes_trend_analysis(self, full_result):
        """Test Markdown includes trend analysis."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "## Trend Analysis" in md
        assert "75/100" in md
        assert "rising" in md

    def test_to_markdown_includes_market_analysis(self, full_result):
        """Test Markdown includes market analysis."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "## Market Analysis" in md
        assert "70/100" in md
        assert "growing" in md

    def test_to_markdown_includes_competition_analysis(self, full_result):
        """Test Markdown includes competition analysis."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "## Competition Analysis" in md
        assert "60/100" in md

    def test_to_markdown_includes_profit_analysis(self, full_result):
        """Test Markdown includes profit analysis."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "## Profit Analysis" in md
        assert "72/100" in md

    def test_to_markdown_includes_evaluation(self, full_result):
        """Test Markdown includes evaluation summary."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "## Evaluation Summary" in md
        assert "70/100" in md
        assert "GO" in md
        assert "Good opportunity" in md

    def test_to_markdown_includes_risks(self, full_result):
        """Test Markdown includes key risks."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "### Key Risks" in md
        assert "Competition" in md
        assert "Price pressure" in md

    def test_to_markdown_includes_success_factors(self, full_result):
        """Test Markdown includes success factors."""
        service = ExportService()

        md = service.to_markdown(full_result)

        assert "### Success Factors" in md
        assert "Differentiation" in md
        assert "Marketing" in md

    def test_to_markdown_failed_result(self, failed_result):
        """Test Markdown export with failed result."""
        service = ExportService()

        md = service.to_markdown(failed_result)

        assert "FAILED" in md
        assert "Analysis failed due to API error" in md

    def test_to_markdown_without_timestamps(self, full_result):
        """Test Markdown without timestamps."""
        config = ExportConfig(include_timestamps=False)
        service = ExportService(config=config)

        md = service.to_markdown(full_result)

        assert "*Generated:" not in md

    def test_to_summary_success(self, full_result):
        """Test summary export for successful result."""
        service = ExportService()

        summary = service.to_summary(full_result)

        assert "portable blender" in summary
        assert "70/100" in summary
        assert "GO" in summary

    def test_to_summary_failed(self, failed_result):
        """Test summary export for failed result."""
        service = ExportService()

        summary = service.to_summary(failed_result)

        assert "Analysis failed" in summary
        assert "API error" in summary

    def test_to_summary_partial_state(self, sample_request):
        """Test summary with partial state."""
        state = AnalysisState(request=sample_request)
        result = PipelineResult(success=True, state=state, execution_time=5.0)
        service = ExportService()

        summary = service.to_summary(result)

        assert "portable blender" in summary


class TestCreateExportService:
    """Test cases for create_export_service function."""

    def test_create_service_default(self):
        """Test creating service with defaults."""
        service = create_export_service()

        assert isinstance(service, ExportService)

    def test_create_service_with_config(self):
        """Test creating service with config."""
        config = ExportConfig(pretty_print=False)
        service = create_export_service(config=config)

        assert service.config.pretty_print is False


class TestExportHelperFunctions:
    """Test cases for export helper functions."""

    @pytest.fixture
    def simple_result(self):
        """Create simple pipeline result."""
        state = AnalysisState()
        return PipelineResult(success=True, state=state, execution_time=5.0)

    def test_export_to_json(self, simple_result):
        """Test export_to_json helper."""
        json_str = export_to_json(simple_result)

        data = json.loads(json_str)
        assert data["success"] is True

    def test_export_to_markdown(self, simple_result):
        """Test export_to_markdown helper."""
        md = export_to_markdown(simple_result)

        assert "# Product Opportunity Analysis Report" in md
        assert "SUCCESS" in md
