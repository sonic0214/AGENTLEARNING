"""
Output schemas - Data models for analysis outputs
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json


class ScoreOutOfBoundsError(Exception):
    """Exception raised when a score is outside valid bounds."""
    pass


def validate_score(score: int, min_val: int = 1, max_val: int = 100) -> int:
    """
    Validate and return a score within bounds.

    Args:
        score: The score to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        The validated score

    Raises:
        ScoreOutOfBoundsError: If score is outside bounds
    """
    if not isinstance(score, int):
        try:
            score = int(score)
        except (ValueError, TypeError):
            raise ScoreOutOfBoundsError(f"Score must be an integer, got {type(score)}")

    if score < min_val or score > max_val:
        raise ScoreOutOfBoundsError(
            f"Score {score} is outside valid range [{min_val}, {max_val}]"
        )
    return score


@dataclass
class TrendAnalysis:
    """
    Trend analysis results.

    Attributes:
        trend_score: Overall trend score (1-100)
        trend_direction: Direction of trend (rising/stable/declining)
        seasonality: Seasonality information
        related_queries: Related search queries
        raw_data: Optional raw data from analysis
    """
    trend_score: int
    trend_direction: str  # rising, stable, declining
    seasonality: Dict[str, Any]
    related_queries: List[Dict[str, str]]
    raw_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate after initialization."""
        self.trend_score = validate_score(self.trend_score)

        valid_directions = {"rising", "stable", "declining"}
        if self.trend_direction not in valid_directions:
            raise ValueError(
                f"Invalid trend_direction: {self.trend_direction}. "
                f"Must be one of {valid_directions}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TrendAnalysis":
        """Create instance from dictionary."""
        return cls(
            trend_score=data.get("trend_score", 50),
            trend_direction=data.get("trend_direction", "stable"),
            seasonality=data.get("seasonality", {}),
            related_queries=data.get("related_queries", []),
            raw_data=data.get("raw_data"),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class MarketAnalysis:
    """
    Market analysis results.

    Attributes:
        market_size: TAM/SAM/SOM values
        growth_rate: Market growth rate (decimal)
        customer_segments: Target customer segments
        maturity_level: Market maturity level
        market_score: Overall market score (1-100)
    """
    market_size: Dict[str, float]  # tam, sam, som, currency
    growth_rate: float
    customer_segments: List[Dict[str, Any]]
    maturity_level: str  # emerging, growing, mature, declining
    market_score: int = 50

    def __post_init__(self):
        """Validate after initialization."""
        self.market_score = validate_score(self.market_score)

        valid_maturity = {"emerging", "growing", "mature", "declining"}
        if self.maturity_level not in valid_maturity:
            raise ValueError(
                f"Invalid maturity_level: {self.maturity_level}. "
                f"Must be one of {valid_maturity}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MarketAnalysis":
        """Create instance from dictionary."""
        return cls(
            market_size=data.get("market_size", {"tam": 0, "sam": 0, "som": 0, "currency": "USD"}),
            growth_rate=data.get("growth_rate", 0.0),
            customer_segments=data.get("customer_segments", []),
            maturity_level=data.get("maturity_level", "growing"),
            market_score=data.get("market_score", 50),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CompetitionAnalysis:
    """
    Competition analysis results.

    Attributes:
        competitors: List of competitor information
        competition_score: Competition intensity score (1-100, higher = more competitive)
        pricing_analysis: Pricing strategy analysis
        opportunities: Market opportunities identified
        entry_barriers: Entry barrier assessment
    """
    competitors: List[Dict[str, Any]]
    competition_score: int
    pricing_analysis: Dict[str, Any]
    opportunities: List[str]
    entry_barriers: str = "medium"

    def __post_init__(self):
        """Validate after initialization."""
        self.competition_score = validate_score(self.competition_score)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "CompetitionAnalysis":
        """Create instance from dictionary."""
        return cls(
            competitors=data.get("competitors", []),
            competition_score=data.get("competition_score", 50),
            pricing_analysis=data.get("pricing_analysis", {}),
            opportunities=data.get("opportunities", []),
            entry_barriers=data.get("entry_barriers", "medium"),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ProfitAnalysis:
    """
    Profit analysis results.

    Attributes:
        unit_economics: Unit economics breakdown
        margins: Margin calculations
        monthly_projection: Monthly revenue projections
        investment: Investment requirements
        assessment: Profitability assessment
        profit_score: Overall profit score (1-100)
    """
    unit_economics: Dict[str, float]
    margins: Dict[str, float]
    monthly_projection: Dict[str, float]
    investment: Dict[str, float]
    assessment: Dict[str, Any]
    profit_score: int = 50

    def __post_init__(self):
        """Validate after initialization."""
        self.profit_score = validate_score(self.profit_score)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProfitAnalysis":
        """Create instance from dictionary."""
        return cls(
            unit_economics=data.get("unit_economics", {}),
            margins=data.get("margins", {}),
            monthly_projection=data.get("monthly_projection", {}),
            investment=data.get("investment", {}),
            assessment=data.get("assessment", {"profitable": False, "rating": "unknown", "recommendation": "unknown"}),
            profit_score=data.get("profit_score", 50),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class EvaluationResult:
    """
    Overall evaluation results.

    Attributes:
        opportunity_score: Overall opportunity score (1-100)
        dimension_scores: Individual dimension scores
        swot_analysis: SWOT analysis
        recommendation: Final recommendation
        recommendation_detail: Detailed recommendation
        key_risks: Key risk factors
        success_factors: Critical success factors
    """
    opportunity_score: int
    dimension_scores: Dict[str, int]
    swot_analysis: Dict[str, List[str]]
    recommendation: str  # go, cautious, no-go
    recommendation_detail: str
    key_risks: List[str]
    success_factors: List[str]

    def __post_init__(self):
        """Validate after initialization."""
        self.opportunity_score = validate_score(self.opportunity_score)

        valid_recommendations = {"go", "cautious", "no-go"}
        if self.recommendation not in valid_recommendations:
            raise ValueError(
                f"Invalid recommendation: {self.recommendation}. "
                f"Must be one of {valid_recommendations}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EvaluationResult":
        """Create instance from dictionary."""
        return cls(
            opportunity_score=data.get("opportunity_score", 50),
            dimension_scores=data.get("dimension_scores", {}),
            swot_analysis=data.get("swot_analysis", {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}),
            recommendation=data.get("recommendation", "cautious"),
            recommendation_detail=data.get("recommendation_detail", ""),
            key_risks=data.get("key_risks", []),
            success_factors=data.get("success_factors", []),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def get_recommendation_emoji(self) -> str:
        """Get emoji for recommendation."""
        emojis = {
            "go": "✅",
            "cautious": "⚠️",
            "no-go": "❌"
        }
        return emojis.get(self.recommendation, "❓")


@dataclass
class FinalReport:
    """
    Complete analysis report.

    Attributes:
        category: Product category analyzed
        target_market: Target market
        trend_analysis: Trend analysis results
        market_analysis: Market analysis results
        competition_analysis: Competition analysis results
        profit_analysis: Profit analysis results
        evaluation: Overall evaluation
        report_markdown: Full report in Markdown format
        generated_at: Timestamp of report generation
    """
    category: str
    target_market: str
    trend_analysis: TrendAnalysis
    market_analysis: MarketAnalysis
    competition_analysis: CompetitionAnalysis
    profit_analysis: ProfitAnalysis
    evaluation: EvaluationResult
    report_markdown: str = ""
    generated_at: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "target_market": self.target_market,
            "trend_analysis": self.trend_analysis.to_dict(),
            "market_analysis": self.market_analysis.to_dict(),
            "competition_analysis": self.competition_analysis.to_dict(),
            "profit_analysis": self.profit_analysis.to_dict(),
            "evaluation": self.evaluation.to_dict(),
            "report_markdown": self.report_markdown,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FinalReport":
        """Create instance from dictionary."""
        return cls(
            category=data.get("category", ""),
            target_market=data.get("target_market", "US"),
            trend_analysis=TrendAnalysis.from_dict(data.get("trend_analysis", {})),
            market_analysis=MarketAnalysis.from_dict(data.get("market_analysis", {})),
            competition_analysis=CompetitionAnalysis.from_dict(data.get("competition_analysis", {})),
            profit_analysis=ProfitAnalysis.from_dict(data.get("profit_analysis", {})),
            evaluation=EvaluationResult.from_dict(data.get("evaluation", {})),
            report_markdown=data.get("report_markdown", ""),
            generated_at=data.get("generated_at", ""),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def get_summary(self) -> str:
        """Get a brief summary of the report."""
        return (
            f"Analysis: {self.category} ({self.target_market})\n"
            f"Opportunity Score: {self.evaluation.opportunity_score}/100\n"
            f"Recommendation: {self.evaluation.get_recommendation_emoji()} {self.evaluation.recommendation.upper()}"
        )
