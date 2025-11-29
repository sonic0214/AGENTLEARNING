"""
Input schemas - Data models for user input
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum


class BudgetRange(str, Enum):
    """Budget range options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BusinessModel(str, Enum):
    """Business model options."""
    AMAZON_FBA = "amazon_fba"
    AMAZON_FBM = "amazon_fbm"
    DROPSHIPPING = "dropshipping"
    PRIVATE_LABEL = "private_label"
    WHOLESALE = "wholesale"
    RETAIL_ARBITRAGE = "retail_arbitrage"


class TargetMarket(str, Enum):
    """Common target market codes."""
    US = "US"
    UK = "UK"
    DE = "DE"
    FR = "FR"
    JP = "JP"
    CA = "CA"
    AU = "AU"
    GLOBAL = "GLOBAL"


class ValidationError(Exception):
    """Exception raised for input validation errors."""
    pass


@dataclass
class AnalysisRequest:
    """
    Request model for product opportunity analysis.

    Attributes:
        category: Product category or niche to analyze
        target_market: Target market/region code (default: US)
        budget_range: Budget level - low/medium/high (default: medium)
        business_model: Business model type (default: amazon_fba)
        keywords: Additional keywords for analysis
    """
    category: str
    target_market: str = "US"
    budget_range: str = "medium"
    business_model: str = "amazon_fba"
    keywords: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Normalize and validate inputs after initialization."""
        # Normalize string fields
        self.category = self.category.strip() if self.category else ""
        self.target_market = self.target_market.upper().strip()
        self.budget_range = self.budget_range.lower().strip()
        self.business_model = self.business_model.lower().strip()

        # Normalize keywords
        if self.keywords:
            self.keywords = [k.strip() for k in self.keywords if k and k.strip()]

    def validate(self) -> bool:
        """
        Validate the analysis request.

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If validation fails
        """
        # Category is required and non-empty
        if not self.category:
            raise ValidationError("Category is required and cannot be empty")

        if len(self.category) < 2:
            raise ValidationError("Category must be at least 2 characters")

        if len(self.category) > 200:
            raise ValidationError("Category must be less than 200 characters")

        # Validate budget_range
        valid_budgets = {"low", "medium", "high"}
        if self.budget_range not in valid_budgets:
            raise ValidationError(
                f"Invalid budget_range: {self.budget_range}. Must be one of {valid_budgets}"
            )

        # Validate business_model
        valid_models = {e.value for e in BusinessModel}
        if self.business_model not in valid_models:
            raise ValidationError(
                f"Invalid business_model: {self.business_model}. Must be one of {valid_models}"
            )

        # Validate keywords length
        if len(self.keywords) > 10:
            raise ValidationError("Maximum 10 keywords allowed")

        return True

    def to_dict(self) -> dict:
        """
        Convert to dictionary.

        Returns:
            dict: Dictionary representation
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisRequest":
        """
        Create instance from dictionary.

        Args:
            data: Dictionary with request data

        Returns:
            AnalysisRequest instance
        """
        return cls(
            category=data.get("category", ""),
            target_market=data.get("target_market", "US"),
            budget_range=data.get("budget_range", "medium"),
            business_model=data.get("business_model", "amazon_fba"),
            keywords=data.get("keywords", []),
        )

    def get_all_keywords(self) -> List[str]:
        """
        Get all keywords including the category.

        Returns:
            List of all keywords for analysis
        """
        all_keywords = [self.category]
        all_keywords.extend(self.keywords)
        return list(set(all_keywords))  # Remove duplicates


@dataclass
class UserPreferences:
    """
    User preferences for analysis customization.

    Attributes:
        risk_tolerance: User's risk tolerance level
        min_margin: Minimum acceptable profit margin (decimal)
        preferred_categories: List of preferred product categories
        excluded_categories: Categories to exclude from analysis
        max_competition_score: Maximum acceptable competition score
    """
    risk_tolerance: str = "medium"  # low, medium, high
    min_margin: float = 0.15  # 15% minimum margin
    preferred_categories: List[str] = field(default_factory=list)
    excluded_categories: List[str] = field(default_factory=list)
    max_competition_score: int = 80  # 1-100

    def __post_init__(self):
        """Validate preferences after initialization."""
        # Normalize risk_tolerance
        self.risk_tolerance = self.risk_tolerance.lower().strip()

    def validate(self) -> bool:
        """
        Validate user preferences.

        Returns:
            bool: True if valid

        Raises:
            ValidationError: If validation fails
        """
        valid_risk = {"low", "medium", "high"}
        if self.risk_tolerance not in valid_risk:
            raise ValidationError(
                f"Invalid risk_tolerance: {self.risk_tolerance}. Must be one of {valid_risk}"
            )

        if not 0 <= self.min_margin <= 1:
            raise ValidationError("min_margin must be between 0 and 1")

        if not 1 <= self.max_competition_score <= 100:
            raise ValidationError("max_competition_score must be between 1 and 100")

        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """Create instance from dictionary."""
        return cls(
            risk_tolerance=data.get("risk_tolerance", "medium"),
            min_margin=data.get("min_margin", 0.15),
            preferred_categories=data.get("preferred_categories", []),
            excluded_categories=data.get("excluded_categories", []),
            max_competition_score=data.get("max_competition_score", 80),
        )
