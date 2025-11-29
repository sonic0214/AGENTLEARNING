"""
State schemas - Session state data models
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime

from .input_schemas import AnalysisRequest
from .output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)


@dataclass
class AnalysisHistoryEntry:
    """
    A single entry in the analysis history.

    Attributes:
        session_id: Session ID for this analysis
        category: Product category analyzed
        target_market: Target market
        opportunity_score: Final opportunity score
        recommendation: Final recommendation
        timestamp: When the analysis was performed
    """
    session_id: str
    category: str
    target_market: str
    opportunity_score: int
    recommendation: str
    timestamp: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisHistoryEntry":
        """Create from dictionary."""
        return cls(
            session_id=data.get("session_id", ""),
            category=data.get("category", ""),
            target_market=data.get("target_market", ""),
            opportunity_score=data.get("opportunity_score", 0),
            recommendation=data.get("recommendation", ""),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class AnalysisState:
    """
    Session state for an analysis workflow.

    This class represents the complete state of an analysis session,
    including the request, all intermediate results, and history.

    Attributes:
        request: Original analysis request
        trend_analysis: Results from trend analysis agent
        market_analysis: Results from market analysis agent
        competition_analysis: Results from competition analysis agent
        profit_analysis: Results from profit analysis agent
        evaluation_result: Results from evaluator agent
        analysis_history: History of previous analyses
        current_phase: Current phase of analysis
        error_message: Error message if analysis failed
        created_at: Timestamp when session was created
        updated_at: Timestamp when session was last updated
    """
    request: Optional[AnalysisRequest] = None
    trend_analysis: Optional[TrendAnalysis] = None
    market_analysis: Optional[MarketAnalysis] = None
    competition_analysis: Optional[CompetitionAnalysis] = None
    profit_analysis: Optional[ProfitAnalysis] = None
    evaluation_result: Optional[EvaluationResult] = None
    analysis_history: List[AnalysisHistoryEntry] = field(default_factory=list)
    current_phase: str = "initialized"
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()

    def set_phase(self, phase: str) -> None:
        """
        Set the current analysis phase.

        Valid phases:
        - initialized: Initial state
        - analyzing_trends: Running trend analysis
        - analyzing_market: Running market analysis
        - analyzing_competition: Running competition analysis
        - analyzing_profit: Running profit analysis
        - evaluating: Running evaluation
        - generating_report: Generating final report
        - completed: Analysis complete
        - failed: Analysis failed
        """
        valid_phases = {
            "initialized",
            "analyzing_trends",
            "analyzing_market",
            "analyzing_competition",
            "analyzing_profit",
            "evaluating",
            "generating_report",
            "completed",
            "failed",
        }
        if phase not in valid_phases:
            raise ValueError(f"Invalid phase: {phase}. Must be one of {valid_phases}")

        self.current_phase = phase
        self.update_timestamp()

    def set_error(self, message: str) -> None:
        """Set error state with message."""
        self.error_message = message
        self.set_phase("failed")

    def is_complete(self) -> bool:
        """Check if all analysis phases are complete."""
        return (
            self.trend_analysis is not None
            and self.market_analysis is not None
            and self.competition_analysis is not None
            and self.profit_analysis is not None
            and self.evaluation_result is not None
        )

    def add_to_history(self, session_id: str) -> None:
        """Add current analysis to history."""
        if self.request and self.evaluation_result:
            entry = AnalysisHistoryEntry(
                session_id=session_id,
                category=self.request.category,
                target_market=self.request.target_market,
                opportunity_score=self.evaluation_result.opportunity_score,
                recommendation=self.evaluation_result.recommendation,
                timestamp=datetime.now().isoformat(),
            )
            self.analysis_history.append(entry)
            self.update_timestamp()

    def to_dict(self) -> dict:
        """
        Convert to dictionary for session storage.

        Returns:
            Dictionary representation suitable for session state
        """
        result = {
            "current_phase": self.current_phase,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "analysis_history": [h.to_dict() for h in self.analysis_history],
        }

        if self.request:
            result["request"] = self.request.to_dict()

        if self.trend_analysis:
            result["trend_analysis"] = self.trend_analysis.to_dict()

        if self.market_analysis:
            result["market_analysis"] = self.market_analysis.to_dict()

        if self.competition_analysis:
            result["competition_analysis"] = self.competition_analysis.to_dict()

        if self.profit_analysis:
            result["profit_analysis"] = self.profit_analysis.to_dict()

        if self.evaluation_result:
            result["evaluation_result"] = self.evaluation_result.to_dict()

        return result

    def to_session_dict(self) -> Dict[str, Any]:
        """
        Convert to flat dictionary for ADK session state.

        The ADK session state expects a flat dictionary structure
        where each key can be referenced in agent instructions.

        Returns:
            Flat dictionary for session state
        """
        state = {
            "current_phase": self.current_phase,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

        if self.request:
            state["category"] = self.request.category
            state["target_market"] = self.request.target_market
            state["budget_range"] = self.request.budget_range
            state["business_model"] = self.request.business_model
            state["keywords"] = self.request.keywords

        if self.trend_analysis:
            state["trend_analysis"] = self.trend_analysis.to_dict()

        if self.market_analysis:
            state["market_analysis"] = self.market_analysis.to_dict()

        if self.competition_analysis:
            state["competition_analysis"] = self.competition_analysis.to_dict()

        if self.profit_analysis:
            state["profit_analysis"] = self.profit_analysis.to_dict()

        if self.evaluation_result:
            state["evaluation_result"] = self.evaluation_result.to_dict()

        if self.error_message:
            state["error_message"] = self.error_message

        return state

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisState":
        """
        Create instance from dictionary.

        Args:
            data: Dictionary with state data

        Returns:
            AnalysisState instance
        """
        state = cls()

        state.current_phase = data.get("current_phase", "initialized")
        state.error_message = data.get("error_message")
        state.created_at = data.get("created_at", datetime.now().isoformat())
        state.updated_at = data.get("updated_at", datetime.now().isoformat())

        if "request" in data:
            state.request = AnalysisRequest.from_dict(data["request"])

        if "trend_analysis" in data:
            state.trend_analysis = TrendAnalysis.from_dict(data["trend_analysis"])

        if "market_analysis" in data:
            state.market_analysis = MarketAnalysis.from_dict(data["market_analysis"])

        if "competition_analysis" in data:
            state.competition_analysis = CompetitionAnalysis.from_dict(data["competition_analysis"])

        if "profit_analysis" in data:
            state.profit_analysis = ProfitAnalysis.from_dict(data["profit_analysis"])

        if "evaluation_result" in data:
            state.evaluation_result = EvaluationResult.from_dict(data["evaluation_result"])

        if "analysis_history" in data:
            state.analysis_history = [
                AnalysisHistoryEntry.from_dict(h) for h in data["analysis_history"]
            ]

        return state

    @classmethod
    def from_session_dict(cls, state: Dict[str, Any]) -> "AnalysisState":
        """
        Create instance from ADK session state dictionary.

        Args:
            state: Flat dictionary from session state

        Returns:
            AnalysisState instance
        """
        analysis_state = cls()

        analysis_state.current_phase = state.get("current_phase", "initialized")
        analysis_state.created_at = state.get("created_at", datetime.now().isoformat())
        analysis_state.updated_at = state.get("updated_at", datetime.now().isoformat())
        analysis_state.error_message = state.get("error_message")

        # Reconstruct request if category exists
        if "category" in state:
            analysis_state.request = AnalysisRequest(
                category=state.get("category", ""),
                target_market=state.get("target_market", "US"),
                budget_range=state.get("budget_range", "medium"),
                business_model=state.get("business_model", "amazon_fba"),
                keywords=state.get("keywords", []),
            )

        if "trend_analysis" in state and state["trend_analysis"]:
            analysis_state.trend_analysis = TrendAnalysis.from_dict(state["trend_analysis"])

        if "market_analysis" in state and state["market_analysis"]:
            analysis_state.market_analysis = MarketAnalysis.from_dict(state["market_analysis"])

        if "competition_analysis" in state and state["competition_analysis"]:
            analysis_state.competition_analysis = CompetitionAnalysis.from_dict(state["competition_analysis"])

        if "profit_analysis" in state and state["profit_analysis"]:
            analysis_state.profit_analysis = ProfitAnalysis.from_dict(state["profit_analysis"])

        if "evaluation_result" in state and state["evaluation_result"]:
            analysis_state.evaluation_result = EvaluationResult.from_dict(state["evaluation_result"])

        return analysis_state
