"""
Tests for schemas/state_schemas.py
"""
import pytest
from datetime import datetime
from src.schemas.state_schemas import AnalysisState, AnalysisHistoryEntry
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)


class TestAnalysisHistoryEntry:
    """Test cases for AnalysisHistoryEntry."""

    def test_create_entry(self):
        """Test creating a history entry."""
        entry = AnalysisHistoryEntry(
            session_id="session-123",
            category="portable blender",
            target_market="US",
            opportunity_score=75,
            recommendation="go",
            timestamp="2025-01-15T10:00:00"
        )

        assert entry.session_id == "session-123"
        assert entry.category == "portable blender"
        assert entry.opportunity_score == 75

    def test_to_dict(self):
        """Test conversion to dictionary."""
        entry = AnalysisHistoryEntry(
            session_id="session-456",
            category="smart watch",
            target_market="UK",
            opportunity_score=60,
            recommendation="cautious",
            timestamp="2025-01-15T11:00:00"
        )

        result = entry.to_dict()

        assert isinstance(result, dict)
        assert result["session_id"] == "session-456"
        assert result["category"] == "smart watch"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "session_id": "session-789",
            "category": "fitness tracker",
            "target_market": "EU",
            "opportunity_score": 80,
            "recommendation": "go",
            "timestamp": "2025-01-15T12:00:00"
        }

        entry = AnalysisHistoryEntry.from_dict(data)

        assert entry.session_id == "session-789"
        assert entry.category == "fitness tracker"
        assert entry.opportunity_score == 80

    def test_from_dict_with_defaults(self):
        """Test creation from partial dictionary uses defaults."""
        data = {}

        entry = AnalysisHistoryEntry.from_dict(data)

        assert entry.session_id == ""
        assert entry.category == ""
        assert entry.opportunity_score == 0


class TestAnalysisState:
    """Test cases for AnalysisState."""

    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba",
            keywords=["mini blender"]
        )

    @pytest.fixture
    def sample_trend_analysis(self):
        """Create sample trend analysis."""
        return TrendAnalysis(
            trend_score=75,
            trend_direction="rising",
            seasonality={"peak_months": ["6", "7"]},
            related_queries=[]
        )

    @pytest.fixture
    def sample_market_analysis(self):
        """Create sample market analysis."""
        return MarketAnalysis(
            market_size={"tam": 1000000, "sam": 500000, "som": 50000},
            growth_rate=0.15,
            customer_segments=[],
            maturity_level="growing",
            market_score=70
        )

    @pytest.fixture
    def sample_competition_analysis(self):
        """Create sample competition analysis."""
        return CompetitionAnalysis(
            competitors=[],
            competition_score=60,
            pricing_analysis={},
            opportunities=[]
        )

    @pytest.fixture
    def sample_profit_analysis(self):
        """Create sample profit analysis."""
        return ProfitAnalysis(
            unit_economics={},
            margins={},
            monthly_projection={},
            investment={},
            assessment={},
            profit_score=65
        )

    @pytest.fixture
    def sample_evaluation(self):
        """Create sample evaluation result."""
        return EvaluationResult(
            opportunity_score=70,
            dimension_scores={},
            swot_analysis={},
            recommendation="go",
            recommendation_detail="Recommended",
            key_risks=[],
            success_factors=[]
        )

    def test_default_state(self):
        """Test default state initialization."""
        state = AnalysisState()

        assert state.request is None
        assert state.trend_analysis is None
        assert state.market_analysis is None
        assert state.competition_analysis is None
        assert state.profit_analysis is None
        assert state.evaluation_result is None
        assert state.current_phase == "initialized"
        assert state.error_message is None
        assert len(state.analysis_history) == 0

    def test_state_with_request(self, sample_request):
        """Test state with request."""
        state = AnalysisState(request=sample_request)

        assert state.request is not None
        assert state.request.category == "portable blender"

    def test_set_phase_valid(self):
        """Test setting valid phase."""
        state = AnalysisState()

        state.set_phase("analyzing_trends")
        assert state.current_phase == "analyzing_trends"

        state.set_phase("completed")
        assert state.current_phase == "completed"

    def test_set_phase_invalid_raises(self):
        """Test that setting invalid phase raises error."""
        state = AnalysisState()

        with pytest.raises(ValueError) as exc_info:
            state.set_phase("invalid_phase")

        assert "Invalid phase" in str(exc_info.value)

    def test_set_error(self):
        """Test setting error state."""
        state = AnalysisState()

        state.set_error("Something went wrong")

        assert state.error_message == "Something went wrong"
        assert state.current_phase == "failed"

    def test_is_complete_false_when_missing_analyses(self, sample_request):
        """Test is_complete returns False when analyses are missing."""
        state = AnalysisState(request=sample_request)

        assert state.is_complete() is False

    def test_is_complete_true_when_all_analyses_present(
        self,
        sample_request,
        sample_trend_analysis,
        sample_market_analysis,
        sample_competition_analysis,
        sample_profit_analysis,
        sample_evaluation
    ):
        """Test is_complete returns True when all analyses present."""
        state = AnalysisState(
            request=sample_request,
            trend_analysis=sample_trend_analysis,
            market_analysis=sample_market_analysis,
            competition_analysis=sample_competition_analysis,
            profit_analysis=sample_profit_analysis,
            evaluation_result=sample_evaluation
        )

        assert state.is_complete() is True

    def test_add_to_history(
        self,
        sample_request,
        sample_evaluation
    ):
        """Test adding analysis to history."""
        state = AnalysisState(
            request=sample_request,
            evaluation_result=sample_evaluation
        )

        state.add_to_history("session-123")

        assert len(state.analysis_history) == 1
        assert state.analysis_history[0].session_id == "session-123"
        assert state.analysis_history[0].category == "portable blender"

    def test_add_to_history_no_request_or_evaluation(self):
        """Test add_to_history does nothing without request/evaluation."""
        state = AnalysisState()

        state.add_to_history("session-123")

        assert len(state.analysis_history) == 0

    def test_update_timestamp(self):
        """Test timestamp updates."""
        state = AnalysisState()
        original_updated_at = state.updated_at

        # Small delay to ensure timestamp changes
        import time
        time.sleep(0.01)

        state.update_timestamp()

        assert state.updated_at != original_updated_at

    def test_to_dict(
        self,
        sample_request,
        sample_trend_analysis,
        sample_market_analysis
    ):
        """Test conversion to dictionary."""
        state = AnalysisState(
            request=sample_request,
            trend_analysis=sample_trend_analysis,
            market_analysis=sample_market_analysis,
            current_phase="analyzing_competition"
        )

        result = state.to_dict()

        assert isinstance(result, dict)
        assert result["current_phase"] == "analyzing_competition"
        assert "request" in result
        assert "trend_analysis" in result
        assert "market_analysis" in result

    def test_to_session_dict(
        self,
        sample_request,
        sample_trend_analysis
    ):
        """Test conversion to flat session dictionary."""
        state = AnalysisState(
            request=sample_request,
            trend_analysis=sample_trend_analysis,
            current_phase="analyzing_market"
        )

        result = state.to_session_dict()

        assert result["category"] == "portable blender"
        assert result["target_market"] == "US"
        assert result["current_phase"] == "analyzing_market"
        assert "trend_analysis" in result

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "current_phase": "analyzing_trends",
            "error_message": None,
            "created_at": "2025-01-15T10:00:00",
            "updated_at": "2025-01-15T10:30:00",
            "request": {
                "category": "smart watch",
                "target_market": "UK",
                "budget_range": "high",
                "business_model": "dropshipping",
                "keywords": []
            },
            "trend_analysis": {
                "trend_score": 80,
                "trend_direction": "rising",
                "seasonality": {},
                "related_queries": []
            },
            "analysis_history": []
        }

        state = AnalysisState.from_dict(data)

        assert state.current_phase == "analyzing_trends"
        assert state.request.category == "smart watch"
        assert state.trend_analysis.trend_score == 80

    def test_from_dict_minimal(self):
        """Test creation from minimal dictionary."""
        data = {}

        state = AnalysisState.from_dict(data)

        assert state.current_phase == "initialized"
        assert state.request is None

    def test_from_session_dict(self):
        """Test creation from flat session dictionary."""
        session_state = {
            "category": "portable blender",
            "target_market": "US",
            "budget_range": "medium",
            "business_model": "amazon_fba",
            "keywords": ["mini blender"],
            "current_phase": "analyzing_market",
            "trend_analysis": {
                "trend_score": 75,
                "trend_direction": "rising",
                "seasonality": {},
                "related_queries": []
            }
        }

        state = AnalysisState.from_session_dict(session_state)

        assert state.request.category == "portable blender"
        assert state.trend_analysis.trend_score == 75
        assert state.current_phase == "analyzing_market"

    def test_from_session_dict_without_category(self):
        """Test creation from session dict without category."""
        session_state = {
            "current_phase": "initialized"
        }

        state = AnalysisState.from_session_dict(session_state)

        assert state.request is None
        assert state.current_phase == "initialized"

    def test_round_trip_to_dict_from_dict(
        self,
        sample_request,
        sample_trend_analysis,
        sample_market_analysis,
        sample_competition_analysis,
        sample_profit_analysis,
        sample_evaluation
    ):
        """Test that to_dict/from_dict roundtrip preserves data."""
        original = AnalysisState(
            request=sample_request,
            trend_analysis=sample_trend_analysis,
            market_analysis=sample_market_analysis,
            competition_analysis=sample_competition_analysis,
            profit_analysis=sample_profit_analysis,
            evaluation_result=sample_evaluation,
            current_phase="completed"
        )

        data = original.to_dict()
        restored = AnalysisState.from_dict(data)

        assert restored.current_phase == original.current_phase
        assert restored.request.category == original.request.category
        assert restored.trend_analysis.trend_score == original.trend_analysis.trend_score
        assert restored.evaluation_result.opportunity_score == original.evaluation_result.opportunity_score

    def test_all_valid_phases(self):
        """Test all valid phase transitions."""
        state = AnalysisState()
        valid_phases = [
            "initialized",
            "analyzing_trends",
            "analyzing_market",
            "analyzing_competition",
            "analyzing_profit",
            "evaluating",
            "generating_report",
            "completed",
            "failed"
        ]

        for phase in valid_phases:
            state.set_phase(phase)
            assert state.current_phase == phase
