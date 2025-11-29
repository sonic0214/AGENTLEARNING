"""
Tests for workflows/analysis_pipeline.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.workflows.analysis_pipeline import (
    AnalysisPipeline,
    PipelineResult,
    create_pipeline,
    get_pipeline_phases,
    get_phase_description,
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
from src.config.settings import Settings


class TestPipelineResult:
    """Test cases for PipelineResult."""

    def test_successful_result(self):
        """Test creating a successful result."""
        state = AnalysisState()
        result = PipelineResult(
            success=True,
            state=state,
            execution_time=5.5,
            phase_times={"analysis": 3.0, "evaluation": 2.5}
        )

        assert result.success is True
        assert result.error is None
        assert result.execution_time == 5.5

    def test_failed_result(self):
        """Test creating a failed result."""
        state = AnalysisState()
        state.set_error("Something went wrong")

        result = PipelineResult(
            success=False,
            state=state,
            error="Something went wrong",
            execution_time=1.0
        )

        assert result.success is False
        assert result.error == "Something went wrong"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        state = AnalysisState()
        result = PipelineResult(
            success=True,
            state=state,
            execution_time=3.0,
            phase_times={"phase1": 1.0, "phase2": 2.0}
        )

        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["execution_time"] == 3.0
        assert "state" in result_dict
        assert result_dict["phase_times"]["phase1"] == 1.0


class TestAnalysisPipeline:
    """Test cases for AnalysisPipeline."""

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

    @pytest.fixture
    def sample_trend_analysis(self):
        """Create sample trend analysis."""
        return TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_seasons": ["summer"]},
            related_queries=[]
        )

    @pytest.fixture
    def sample_market_analysis(self):
        """Create sample market analysis."""
        return MarketAnalysis(
            market_size={"tam": 1000000000, "sam": 300000000, "som": 50000000},
            growth_rate=0.15,
            customer_segments=[],
            maturity_level="growing",
            market_score=70
        )

    @pytest.fixture
    def sample_competition_analysis(self):
        """Create sample competition analysis."""
        return CompetitionAnalysis(
            competitors=[{"name": "Brand1", "market_share": 30}],
            competition_score=60,
            pricing_analysis={"avg_price": 45.00},
            opportunities=["Budget segment"]
        )

    @pytest.fixture
    def sample_profit_analysis(self):
        """Create sample profit analysis."""
        return ProfitAnalysis(
            unit_economics={"retail_price": 50, "profit_per_unit": 15},
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
            recommendation_detail="Good opportunity",
            key_risks=["Competition"],
            success_factors=["Differentiation"]
        )

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    def test_pipeline_initialization(
        self, mock_report, mock_eval, mock_profit, mock_comp, mock_market, mock_trend, mock_settings
    ):
        """Test pipeline initialization."""
        pipeline = AnalysisPipeline(mock_settings)

        assert pipeline.settings == mock_settings
        mock_trend.assert_called_once()
        mock_market.assert_called_once()
        mock_comp.assert_called_once()
        mock_profit.assert_called_once()

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    def test_pipeline_with_callback(
        self, mock_report, mock_eval, mock_profit, mock_comp, mock_market, mock_trend, mock_settings
    ):
        """Test pipeline with phase complete callback."""
        callback = Mock()
        pipeline = AnalysisPipeline(mock_settings, on_phase_complete=callback)

        assert pipeline.on_phase_complete == callback

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    @patch('src.workflows.analysis_pipeline.ParallelAgent')
    def test_create_pipeline_agents(
        self, mock_parallel, mock_report, mock_eval, mock_profit,
        mock_comp, mock_market, mock_trend, mock_settings, sample_request
    ):
        """Test creating pipeline agents."""
        # Setup mock agent instances
        mock_trend_instance = Mock()
        mock_trend.return_value = mock_trend_instance
        mock_market_instance = Mock()
        mock_market.return_value = mock_market_instance
        mock_comp_instance = Mock()
        mock_comp.return_value = mock_comp_instance
        mock_profit_instance = Mock()
        mock_profit.return_value = mock_profit_instance

        pipeline = AnalysisPipeline(mock_settings)
        agents = pipeline.create_pipeline_agents(sample_request)

        assert "parallel_agent" in agents
        assert "trend_agent" in agents
        assert "market_agent" in agents
        assert "competition_agent" in agents
        assert "profit_agent" in agents
        assert "request" in agents
        assert agents["request"] == sample_request

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    def test_create_evaluator(
        self, mock_report, mock_eval, mock_profit, mock_comp, mock_market, mock_trend,
        mock_settings, sample_request, sample_trend_analysis, sample_market_analysis,
        sample_competition_analysis, sample_profit_analysis
    ):
        """Test creating evaluator agent."""
        mock_eval_instance = Mock()
        mock_eval.return_value = mock_eval_instance

        pipeline = AnalysisPipeline(mock_settings)
        evaluator = pipeline.create_evaluator(
            sample_request,
            sample_trend_analysis,
            sample_market_analysis,
            sample_competition_analysis,
            sample_profit_analysis
        )

        mock_eval_instance.create_agent.assert_called_once()

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    def test_create_report_generator(
        self, mock_report, mock_eval, mock_profit, mock_comp, mock_market, mock_trend,
        mock_settings, sample_request, sample_trend_analysis, sample_market_analysis,
        sample_competition_analysis, sample_profit_analysis, sample_evaluation
    ):
        """Test creating report generator agent."""
        mock_report_instance = Mock()
        mock_report.return_value = mock_report_instance

        pipeline = AnalysisPipeline(mock_settings)
        report_gen = pipeline.create_report_generator(
            sample_request,
            sample_trend_analysis,
            sample_market_analysis,
            sample_competition_analysis,
            sample_profit_analysis,
            sample_evaluation
        )

        mock_report_instance.create_agent.assert_called_once()

    @patch('src.workflows.analysis_pipeline.TrendAgent')
    @patch('src.workflows.analysis_pipeline.MarketAgent')
    @patch('src.workflows.analysis_pipeline.CompetitionAgent')
    @patch('src.workflows.analysis_pipeline.ProfitAgent')
    @patch('src.workflows.analysis_pipeline.EvaluatorAgent')
    @patch('src.workflows.analysis_pipeline.ReportAgent')
    @patch('src.workflows.analysis_pipeline.SequentialAgent')
    @patch('src.workflows.analysis_pipeline.ParallelAgent')
    def test_build_full_pipeline(
        self, mock_parallel, mock_sequential, mock_report, mock_eval,
        mock_profit, mock_comp, mock_market, mock_trend, mock_settings, sample_request
    ):
        """Test building full pipeline."""
        pipeline = AnalysisPipeline(mock_settings)
        full_pipeline = pipeline.build_full_pipeline(sample_request)

        mock_sequential.assert_called_once()
        call_kwargs = mock_sequential.call_args[1]
        assert call_kwargs["name"] == "product_analysis_pipeline"

    def test_parse_trend_result_valid(self):
        """Test parsing valid trend result."""
        pipeline = create_pipeline()
        result = '{"trend_score": 75, "trend_direction": "rising", "seasonality": {}, "related_queries": []}'

        parsed = pipeline._parse_trend_result(result)

        assert parsed is not None
        assert parsed.trend_score == 75
        assert parsed.trend_direction == "rising"

    def test_parse_trend_result_invalid(self):
        """Test parsing invalid trend result."""
        pipeline = create_pipeline()
        result = "Not valid JSON"

        parsed = pipeline._parse_trend_result(result)

        assert parsed is None

    def test_parse_market_result_valid(self):
        """Test parsing valid market result."""
        pipeline = create_pipeline()
        result = '{"market_size": {"tam": 1000000}, "growth_rate": 0.15, "customer_segments": [], "maturity_level": "growing", "market_score": 70}'

        parsed = pipeline._parse_market_result(result)

        assert parsed is not None
        assert parsed.market_score == 70

    def test_parse_competition_result_valid(self):
        """Test parsing valid competition result."""
        pipeline = create_pipeline()
        result = '{"competitors": [], "competition_score": 60, "pricing_analysis": {}, "opportunities": []}'

        parsed = pipeline._parse_competition_result(result)

        assert parsed is not None
        assert parsed.competition_score == 60

    def test_parse_profit_result_valid(self):
        """Test parsing valid profit result."""
        pipeline = create_pipeline()
        result = '{"unit_economics": {}, "margins": {}, "monthly_projection": {}, "investment": {}, "assessment": {}, "profit_score": 65}'

        parsed = pipeline._parse_profit_result(result)

        assert parsed is not None
        assert parsed.profit_score == 65

    def test_parse_evaluation_result_valid(self):
        """Test parsing valid evaluation result."""
        pipeline = create_pipeline()
        result = '''
        {
            "opportunity_score": 70,
            "dimension_scores": {},
            "swot_analysis": {},
            "recommendation": "go",
            "recommendation_detail": "Good",
            "key_risks": [],
            "success_factors": []
        }
        '''

        parsed = pipeline._parse_evaluation_result(result)

        assert parsed is not None
        assert parsed.opportunity_score == 70
        assert parsed.recommendation == "go"


class TestCreatePipeline:
    """Test cases for create_pipeline factory function."""

    def test_create_pipeline_default(self):
        """Test creating pipeline with defaults."""
        pipeline = create_pipeline()

        assert pipeline is not None
        assert isinstance(pipeline, AnalysisPipeline)

    def test_create_pipeline_with_callback(self):
        """Test creating pipeline with callback."""
        callback = Mock()
        pipeline = create_pipeline(on_phase_complete=callback)

        assert pipeline.on_phase_complete == callback


class TestGetPipelinePhases:
    """Test cases for get_pipeline_phases function."""

    def test_returns_all_phases(self):
        """Test that all phases are returned."""
        phases = get_pipeline_phases()

        assert "initialized" in phases
        assert "analyzing_trends" in phases
        assert "analyzing_market" in phases
        assert "analyzing_competition" in phases
        assert "analyzing_profit" in phases
        assert "evaluating" in phases
        assert "generating_report" in phases
        assert "completed" in phases

    def test_phases_in_order(self):
        """Test phases are in correct order."""
        phases = get_pipeline_phases()

        assert phases[0] == "initialized"
        assert phases[-1] == "completed"

    def test_returns_list(self):
        """Test returns a list."""
        phases = get_pipeline_phases()

        assert isinstance(phases, list)


class TestGetPhaseDescription:
    """Test cases for get_phase_description function."""

    def test_known_phases(self):
        """Test descriptions for known phases."""
        assert "trend" in get_phase_description("analyzing_trends").lower()
        assert "market" in get_phase_description("analyzing_market").lower()
        assert "compet" in get_phase_description("analyzing_competition").lower()
        assert "profit" in get_phase_description("analyzing_profit").lower()
        assert "evaluat" in get_phase_description("evaluating").lower()
        assert "report" in get_phase_description("generating_report").lower()

    def test_unknown_phase(self):
        """Test description for unknown phase."""
        desc = get_phase_description("unknown_phase")

        assert desc == "Unknown phase"

    def test_completed_phase(self):
        """Test description for completed phase."""
        desc = get_phase_description("completed")

        assert "complete" in desc.lower()
