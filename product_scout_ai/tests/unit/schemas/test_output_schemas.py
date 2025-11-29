"""
Tests for schemas/output_schemas.py
"""
import pytest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
    FinalReport,
    ScoreOutOfBoundsError,
    validate_score,
)


class TestValidateScore:
    """Test cases for validate_score function."""

    def test_valid_score_in_range(self):
        """Test that valid score returns unchanged."""
        assert validate_score(50) == 50
        assert validate_score(1) == 1
        assert validate_score(100) == 100

    def test_score_below_min_raises(self):
        """Test that score below minimum raises error."""
        with pytest.raises(ScoreOutOfBoundsError) as exc_info:
            validate_score(0)

        assert "outside valid range" in str(exc_info.value)

    def test_score_above_max_raises(self):
        """Test that score above maximum raises error."""
        with pytest.raises(ScoreOutOfBoundsError) as exc_info:
            validate_score(101)

        assert "outside valid range" in str(exc_info.value)

    def test_custom_range(self):
        """Test custom min/max range."""
        assert validate_score(5, min_val=1, max_val=10) == 5

        with pytest.raises(ScoreOutOfBoundsError):
            validate_score(11, min_val=1, max_val=10)

    def test_string_score_converted(self):
        """Test that string scores are converted to int."""
        assert validate_score("50") == 50

    def test_invalid_string_raises(self):
        """Test that invalid string raises error."""
        with pytest.raises(ScoreOutOfBoundsError) as exc_info:
            validate_score("invalid")

        assert "must be an integer" in str(exc_info.value)


class TestTrendAnalysis:
    """Test cases for TrendAnalysis."""

    def test_valid_trend_analysis(self):
        """Test creating valid TrendAnalysis."""
        trend = TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_months": ["11", "12"]},
            related_queries=[{"query": "mini blender", "score": 80}]
        )

        assert trend.trend_score == 75
        assert trend.trend_direction == "rising"

    def test_invalid_trend_direction_raises(self):
        """Test that invalid trend_direction raises error."""
        with pytest.raises(ValueError) as exc_info:
            TrendAnalysis(
                trend_score=50,
                trend_direction="invalid",
                seasonality={},
                related_queries=[]
            )

        assert "Invalid trend_direction" in str(exc_info.value)

    def test_invalid_score_raises(self):
        """Test that invalid score raises error."""
        with pytest.raises(ScoreOutOfBoundsError):
            TrendAnalysis(
                trend_score=150,
                trend_direction="rising",
                seasonality={},
                related_queries=[]
            )

    def test_to_dict(self):
        """Test conversion to dictionary."""
        trend = TrendAnalysis(
            trend_score=60,
            trend_direction="stable",
            seasonality={"peak_months": ["6", "7"]},
            related_queries=[]
        )

        result = trend.to_dict()

        assert isinstance(result, dict)
        assert result["trend_score"] == 60
        assert result["trend_direction"] == "stable"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "trend_score": 80,
            "trend_direction": "rising",
            "seasonality": {"peak": "summer"},
            "related_queries": [{"query": "test"}]
        }

        trend = TrendAnalysis.from_dict(data)

        assert trend.trend_score == 80
        assert trend.trend_direction == "rising"

    def test_from_dict_with_defaults(self):
        """Test creation from partial dictionary uses defaults."""
        data = {}

        trend = TrendAnalysis.from_dict(data)

        assert trend.trend_score == 50
        assert trend.trend_direction == "stable"

    def test_to_json(self):
        """Test JSON conversion."""
        trend = TrendAnalysis(
            trend_score=70,
            trend_direction="declining",
            seasonality={},
            related_queries=[]
        )

        json_str = trend.to_json()

        assert '"trend_score": 70' in json_str
        assert '"trend_direction": "declining"' in json_str


class TestMarketAnalysis:
    """Test cases for MarketAnalysis."""

    def test_valid_market_analysis(self):
        """Test creating valid MarketAnalysis."""
        market = MarketAnalysis(
            market_size={"tam": 1000000, "sam": 500000, "som": 50000, "currency": "USD"},
            growth_rate=0.15,
            customer_segments=[{"name": "fitness", "percentage": 40}],
            maturity_level="growing",
            market_score=70
        )

        assert market.market_score == 70
        assert market.maturity_level == "growing"

    def test_invalid_maturity_level_raises(self):
        """Test that invalid maturity_level raises error."""
        with pytest.raises(ValueError) as exc_info:
            MarketAnalysis(
                market_size={},
                growth_rate=0.1,
                customer_segments=[],
                maturity_level="invalid"
            )

        assert "Invalid maturity_level" in str(exc_info.value)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        market = MarketAnalysis(
            market_size={"tam": 1000000},
            growth_rate=0.2,
            customer_segments=[],
            maturity_level="emerging",
            market_score=80
        )

        result = market.to_dict()

        assert result["market_score"] == 80
        assert result["maturity_level"] == "emerging"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "market_size": {"tam": 500000},
            "growth_rate": 0.1,
            "customer_segments": [],
            "maturity_level": "mature",
            "market_score": 60
        }

        market = MarketAnalysis.from_dict(data)

        assert market.maturity_level == "mature"
        assert market.market_score == 60


class TestCompetitionAnalysis:
    """Test cases for CompetitionAnalysis."""

    def test_valid_competition_analysis(self):
        """Test creating valid CompetitionAnalysis."""
        competition = CompetitionAnalysis(
            competitors=[{"name": "CompA", "market_share": 30}],
            competition_score=65,
            pricing_analysis={"avg_price": 29.99},
            opportunities=["niche market"],
            entry_barriers="high"
        )

        assert competition.competition_score == 65
        assert len(competition.competitors) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        competition = CompetitionAnalysis(
            competitors=[],
            competition_score=50,
            pricing_analysis={},
            opportunities=["opportunity1", "opportunity2"]
        )

        result = competition.to_dict()

        assert result["competition_score"] == 50
        assert len(result["opportunities"]) == 2

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "competitors": [{"name": "Test"}],
            "competition_score": 75,
            "pricing_analysis": {"min": 10, "max": 50},
            "opportunities": [],
            "entry_barriers": "low"
        }

        competition = CompetitionAnalysis.from_dict(data)

        assert competition.competition_score == 75
        assert competition.entry_barriers == "low"


class TestProfitAnalysis:
    """Test cases for ProfitAnalysis."""

    def test_valid_profit_analysis(self):
        """Test creating valid ProfitAnalysis."""
        profit = ProfitAnalysis(
            unit_economics={"cost": 10, "price": 30, "profit": 20},
            margins={"gross": 0.66, "net": 0.45},
            monthly_projection={"revenue": 10000, "profit": 4500},
            investment={"initial": 5000, "monthly": 2000},
            assessment={"profitable": True, "rating": "good"},
            profit_score=72
        )

        assert profit.profit_score == 72
        assert profit.margins["gross"] == 0.66

    def test_to_dict(self):
        """Test conversion to dictionary."""
        profit = ProfitAnalysis(
            unit_economics={},
            margins={},
            monthly_projection={},
            investment={},
            assessment={"profitable": False},
            profit_score=40
        )

        result = profit.to_dict()

        assert result["profit_score"] == 40

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "unit_economics": {"cost": 15},
            "margins": {"gross": 0.5},
            "monthly_projection": {},
            "investment": {},
            "assessment": {"profitable": True},
            "profit_score": 65
        }

        profit = ProfitAnalysis.from_dict(data)

        assert profit.profit_score == 65


class TestEvaluationResult:
    """Test cases for EvaluationResult."""

    def test_valid_evaluation_result(self):
        """Test creating valid EvaluationResult."""
        evaluation = EvaluationResult(
            opportunity_score=78,
            dimension_scores={"trend": 80, "market": 75, "competition": 70, "profit": 85},
            swot_analysis={
                "strengths": ["growing market"],
                "weaknesses": ["high competition"],
                "opportunities": ["new segments"],
                "threats": ["market saturation"]
            },
            recommendation="go",
            recommendation_detail="Strong opportunity with manageable risks",
            key_risks=["competition"],
            success_factors=["differentiation"]
        )

        assert evaluation.opportunity_score == 78
        assert evaluation.recommendation == "go"

    def test_invalid_recommendation_raises(self):
        """Test that invalid recommendation raises error."""
        with pytest.raises(ValueError) as exc_info:
            EvaluationResult(
                opportunity_score=50,
                dimension_scores={},
                swot_analysis={},
                recommendation="invalid",
                recommendation_detail="",
                key_risks=[],
                success_factors=[]
            )

        assert "Invalid recommendation" in str(exc_info.value)

    def test_get_recommendation_emoji(self):
        """Test recommendation emoji mapping."""
        go_eval = EvaluationResult(
            opportunity_score=80,
            dimension_scores={},
            swot_analysis={},
            recommendation="go",
            recommendation_detail="",
            key_risks=[],
            success_factors=[]
        )
        assert go_eval.get_recommendation_emoji() == "✅"

        cautious_eval = EvaluationResult(
            opportunity_score=55,
            dimension_scores={},
            swot_analysis={},
            recommendation="cautious",
            recommendation_detail="",
            key_risks=[],
            success_factors=[]
        )
        assert cautious_eval.get_recommendation_emoji() == "⚠️"

        nogo_eval = EvaluationResult(
            opportunity_score=30,
            dimension_scores={},
            swot_analysis={},
            recommendation="no-go",
            recommendation_detail="",
            key_risks=[],
            success_factors=[]
        )
        assert nogo_eval.get_recommendation_emoji() == "❌"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        evaluation = EvaluationResult(
            opportunity_score=65,
            dimension_scores={"trend": 70},
            swot_analysis={"strengths": []},
            recommendation="cautious",
            recommendation_detail="Proceed with caution",
            key_risks=["risk1"],
            success_factors=["factor1"]
        )

        result = evaluation.to_dict()

        assert result["opportunity_score"] == 65
        assert result["recommendation"] == "cautious"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "opportunity_score": 72,
            "dimension_scores": {"market": 75},
            "swot_analysis": {"strengths": ["strong brand"]},
            "recommendation": "go",
            "recommendation_detail": "Good opportunity",
            "key_risks": [],
            "success_factors": []
        }

        evaluation = EvaluationResult.from_dict(data)

        assert evaluation.opportunity_score == 72
        assert evaluation.recommendation == "go"


class TestFinalReport:
    """Test cases for FinalReport."""

    @pytest.fixture
    def sample_analyses(self):
        """Create sample analysis objects for testing."""
        return {
            "trend": TrendAnalysis(
                trend_score=75,
                trend_direction="rising",
                seasonality={},
                related_queries=[]
            ),
            "market": MarketAnalysis(
                market_size={"tam": 1000000},
                growth_rate=0.15,
                customer_segments=[],
                maturity_level="growing",
                market_score=70
            ),
            "competition": CompetitionAnalysis(
                competitors=[],
                competition_score=60,
                pricing_analysis={},
                opportunities=[]
            ),
            "profit": ProfitAnalysis(
                unit_economics={},
                margins={},
                monthly_projection={},
                investment={},
                assessment={},
                profit_score=65
            ),
            "evaluation": EvaluationResult(
                opportunity_score=70,
                dimension_scores={},
                swot_analysis={},
                recommendation="go",
                recommendation_detail="Recommended",
                key_risks=[],
                success_factors=[]
            )
        }

    def test_valid_final_report(self, sample_analyses):
        """Test creating valid FinalReport."""
        report = FinalReport(
            category="portable blender",
            target_market="US",
            trend_analysis=sample_analyses["trend"],
            market_analysis=sample_analyses["market"],
            competition_analysis=sample_analyses["competition"],
            profit_analysis=sample_analyses["profit"],
            evaluation=sample_analyses["evaluation"],
            report_markdown="# Report",
            generated_at="2025-01-15T10:00:00"
        )

        assert report.category == "portable blender"
        assert report.target_market == "US"

    def test_to_dict(self, sample_analyses):
        """Test conversion to dictionary."""
        report = FinalReport(
            category="test product",
            target_market="UK",
            trend_analysis=sample_analyses["trend"],
            market_analysis=sample_analyses["market"],
            competition_analysis=sample_analyses["competition"],
            profit_analysis=sample_analyses["profit"],
            evaluation=sample_analyses["evaluation"]
        )

        result = report.to_dict()

        assert result["category"] == "test product"
        assert "trend_analysis" in result
        assert "evaluation" in result

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "category": "smart watch",
            "target_market": "EU",
            "trend_analysis": {"trend_score": 80, "trend_direction": "rising"},
            "market_analysis": {"maturity_level": "growing"},
            "competition_analysis": {"competition_score": 55},
            "profit_analysis": {"profit_score": 60},
            "evaluation": {"opportunity_score": 70, "recommendation": "cautious"},
            "report_markdown": "# Test Report",
            "generated_at": "2025-01-15"
        }

        report = FinalReport.from_dict(data)

        assert report.category == "smart watch"
        assert report.target_market == "EU"
        assert report.trend_analysis.trend_score == 80

    def test_get_summary(self, sample_analyses):
        """Test report summary generation."""
        report = FinalReport(
            category="portable blender",
            target_market="US",
            trend_analysis=sample_analyses["trend"],
            market_analysis=sample_analyses["market"],
            competition_analysis=sample_analyses["competition"],
            profit_analysis=sample_analyses["profit"],
            evaluation=sample_analyses["evaluation"]
        )

        summary = report.get_summary()

        assert "portable blender" in summary
        assert "US" in summary
        assert "70/100" in summary
        assert "GO" in summary

    def test_to_json(self, sample_analyses):
        """Test JSON conversion."""
        report = FinalReport(
            category="test",
            target_market="US",
            trend_analysis=sample_analyses["trend"],
            market_analysis=sample_analyses["market"],
            competition_analysis=sample_analyses["competition"],
            profit_analysis=sample_analyses["profit"],
            evaluation=sample_analyses["evaluation"]
        )

        json_str = report.to_json()

        assert '"category": "test"' in json_str
        assert '"target_market": "US"' in json_str
