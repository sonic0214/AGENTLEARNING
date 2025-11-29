"""
Tests for schemas/input_schemas.py
"""
import pytest
from src.schemas.input_schemas import (
    AnalysisRequest,
    UserPreferences,
    ValidationError,
    BudgetRange,
    BusinessModel,
)


class TestAnalysisRequest:
    """Test cases for AnalysisRequest."""

    def test_valid_input_creates_object(self):
        """Test that valid input creates an AnalysisRequest object."""
        request = AnalysisRequest(
            category="portable blender",
            target_market="US",
            budget_range="medium",
            business_model="amazon_fba",
            keywords=["mini blender", "travel blender"]
        )

        assert request.category == "portable blender"
        assert request.target_market == "US"
        assert request.budget_range == "medium"
        assert request.business_model == "amazon_fba"
        assert len(request.keywords) == 2

    def test_invalid_empty_category_raises(self):
        """Test that empty category raises ValidationError."""
        request = AnalysisRequest(category="")

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "Category is required" in str(exc_info.value)

    def test_invalid_short_category_raises(self):
        """Test that too short category raises ValidationError."""
        request = AnalysisRequest(category="a")

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "at least 2 characters" in str(exc_info.value)

    def test_invalid_long_category_raises(self):
        """Test that too long category raises ValidationError."""
        request = AnalysisRequest(category="a" * 250)

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "less than 200 characters" in str(exc_info.value)

    def test_default_values(self):
        """Test that default values are set correctly."""
        request = AnalysisRequest(category="test product")

        assert request.target_market == "US"
        assert request.budget_range == "medium"
        assert request.business_model == "amazon_fba"
        assert request.keywords == []

    def test_target_market_normalized_to_uppercase(self):
        """Test that target_market is normalized to uppercase."""
        request = AnalysisRequest(category="test", target_market="us")

        assert request.target_market == "US"

    def test_budget_range_normalized_to_lowercase(self):
        """Test that budget_range is normalized to lowercase."""
        request = AnalysisRequest(category="test", budget_range="HIGH")

        assert request.budget_range == "high"

    def test_invalid_budget_range_raises(self):
        """Test that invalid budget_range raises ValidationError."""
        request = AnalysisRequest(category="test", budget_range="invalid")

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "Invalid budget_range" in str(exc_info.value)

    def test_invalid_business_model_raises(self):
        """Test that invalid business_model raises ValidationError."""
        request = AnalysisRequest(category="test", business_model="invalid_model")

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "Invalid business_model" in str(exc_info.value)

    def test_too_many_keywords_raises(self):
        """Test that more than 10 keywords raises ValidationError."""
        request = AnalysisRequest(
            category="test",
            keywords=[f"keyword{i}" for i in range(15)]
        )

        with pytest.raises(ValidationError) as exc_info:
            request.validate()

        assert "Maximum 10 keywords" in str(exc_info.value)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        request = AnalysisRequest(
            category="portable blender",
            target_market="US",
            keywords=["mini blender"]
        )

        result = request.to_dict()

        assert isinstance(result, dict)
        assert result["category"] == "portable blender"
        assert result["target_market"] == "US"
        assert result["keywords"] == ["mini blender"]

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "category": "smart watch",
            "target_market": "UK",
            "budget_range": "high",
            "business_model": "dropshipping",
            "keywords": ["fitness tracker"]
        }

        request = AnalysisRequest.from_dict(data)

        assert request.category == "smart watch"
        assert request.target_market == "UK"
        assert request.budget_range == "high"
        assert request.business_model == "dropshipping"
        assert request.keywords == ["fitness tracker"]

    def test_from_dict_with_defaults(self):
        """Test creation from partial dictionary uses defaults."""
        data = {"category": "test product"}

        request = AnalysisRequest.from_dict(data)

        assert request.category == "test product"
        assert request.target_market == "US"
        assert request.budget_range == "medium"

    def test_get_all_keywords(self):
        """Test get_all_keywords includes category."""
        request = AnalysisRequest(
            category="portable blender",
            keywords=["mini blender", "travel blender"]
        )

        all_keywords = request.get_all_keywords()

        assert "portable blender" in all_keywords
        assert "mini blender" in all_keywords
        assert "travel blender" in all_keywords

    def test_get_all_keywords_removes_duplicates(self):
        """Test get_all_keywords removes duplicates."""
        request = AnalysisRequest(
            category="blender",
            keywords=["blender", "mini blender"]  # "blender" is duplicate
        )

        all_keywords = request.get_all_keywords()

        assert all_keywords.count("blender") == 1

    def test_keywords_whitespace_normalized(self):
        """Test that keyword whitespace is normalized."""
        request = AnalysisRequest(
            category="test",
            keywords=["  spaced keyword  ", "", "  "]
        )

        # Empty strings should be filtered out
        assert "spaced keyword" in request.keywords
        assert "" not in request.keywords

    def test_category_whitespace_normalized(self):
        """Test that category whitespace is normalized."""
        request = AnalysisRequest(category="  portable blender  ")

        assert request.category == "portable blender"


class TestUserPreferences:
    """Test cases for UserPreferences."""

    def test_default_values(self):
        """Test default preference values."""
        prefs = UserPreferences()

        assert prefs.risk_tolerance == "medium"
        assert prefs.min_margin == 0.15
        assert prefs.preferred_categories == []
        assert prefs.excluded_categories == []
        assert prefs.max_competition_score == 80

    def test_valid_preferences(self):
        """Test valid preferences creation."""
        prefs = UserPreferences(
            risk_tolerance="high",
            min_margin=0.25,
            max_competition_score=60
        )

        assert prefs.validate() is True

    def test_invalid_risk_tolerance(self):
        """Test invalid risk_tolerance raises error."""
        prefs = UserPreferences(risk_tolerance="invalid")

        with pytest.raises(ValidationError) as exc_info:
            prefs.validate()

        assert "Invalid risk_tolerance" in str(exc_info.value)

    def test_invalid_min_margin_too_high(self):
        """Test min_margin > 1 raises error."""
        prefs = UserPreferences(min_margin=1.5)

        with pytest.raises(ValidationError) as exc_info:
            prefs.validate()

        assert "min_margin must be between" in str(exc_info.value)

    def test_invalid_min_margin_negative(self):
        """Test negative min_margin raises error."""
        prefs = UserPreferences(min_margin=-0.1)

        with pytest.raises(ValidationError) as exc_info:
            prefs.validate()

        assert "min_margin must be between" in str(exc_info.value)

    def test_invalid_competition_score(self):
        """Test invalid max_competition_score raises error."""
        prefs = UserPreferences(max_competition_score=150)

        with pytest.raises(ValidationError) as exc_info:
            prefs.validate()

        assert "max_competition_score must be between" in str(exc_info.value)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        prefs = UserPreferences(risk_tolerance="low")

        result = prefs.to_dict()

        assert isinstance(result, dict)
        assert result["risk_tolerance"] == "low"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "risk_tolerance": "high",
            "min_margin": 0.30,
            "preferred_categories": ["electronics"]
        }

        prefs = UserPreferences.from_dict(data)

        assert prefs.risk_tolerance == "high"
        assert prefs.min_margin == 0.30
        assert prefs.preferred_categories == ["electronics"]
