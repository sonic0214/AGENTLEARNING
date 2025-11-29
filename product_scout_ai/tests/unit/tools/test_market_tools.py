"""
Tests for tools/market_tools.py
"""
import pytest
from src.tools.market_tools import (
    extract_market_size,
    extract_growth_rate,
    determine_maturity_level,
    extract_customer_segments,
    calculate_market_score,
    format_market_results,
)


class TestExtractMarketSize:
    """Test cases for extract_market_size."""

    def test_extract_billion_values(self):
        """Test extracting billion dollar market sizes."""
        search_results = """
        The global market is valued at $15.5 billion.
        TAM is estimated at $20B with SAM around $5 billion.
        """
        market_size = extract_market_size(search_results)

        assert market_size["tam"] >= 1_000_000_000
        assert "currency" in market_size
        assert market_size["currency"] == "USD"

    def test_extract_million_values(self):
        """Test extracting million dollar market sizes."""
        search_results = """
        The niche market is worth $500 million.
        Serviceable market is about $150M.
        """
        market_size = extract_market_size(search_results)

        assert market_size["tam"] >= 100_000_000

    def test_tam_sam_som_hierarchy(self):
        """Test that TAM >= SAM >= SOM."""
        search_results = """
        Total market is $10 billion, addressable is $3 billion,
        obtainable market share is $500 million.
        """
        market_size = extract_market_size(search_results)

        assert market_size["tam"] >= market_size["sam"]
        assert market_size["sam"] >= market_size["som"]

    def test_default_values_when_no_data(self):
        """Test default values when no market size found."""
        search_results = "No specific market size mentioned."
        market_size = extract_market_size(search_results)

        assert market_size["tam"] > 0
        assert market_size["sam"] > 0
        assert market_size["som"] > 0


class TestExtractGrowthRate:
    """Test cases for extract_growth_rate."""

    def test_cagr_extracted(self):
        """Test CAGR extraction."""
        search_results = """
        The market has a 12.5% CAGR.
        Compound annual growth rate of 15%.
        """
        growth_rate = extract_growth_rate(search_results)

        assert 0.10 <= growth_rate <= 0.20

    def test_growth_percentage_extracted(self):
        """Test growth percentage extraction."""
        search_results = """
        The market is growing at 18% annually.
        Industry growing by 20% year over year.
        """
        growth_rate = extract_growth_rate(search_results)

        assert growth_rate > 0.15

    def test_default_when_no_growth_found(self):
        """Test default growth rate when not found."""
        search_results = "Market information without specific growth rates."
        growth_rate = extract_growth_rate(search_results)

        assert growth_rate == 0.10  # Default 10%


class TestDetermineMaturityLevel:
    """Test cases for determine_maturity_level."""

    def test_emerging_market_detected(self):
        """Test emerging market detection."""
        search_results = """
        This is an emerging market with early stage companies.
        New market opportunities for startups. Nascent industry.
        """
        maturity = determine_maturity_level(search_results)

        assert maturity == "emerging"

    def test_growing_market_detected(self):
        """Test growing market detection."""
        search_results = """
        The market is experiencing rapid growth and expanding.
        High growth sector with expanding customer base.
        """
        maturity = determine_maturity_level(search_results)

        assert maturity == "growing"

    def test_mature_market_detected(self):
        """Test mature market detection."""
        search_results = """
        This is a mature market with established players.
        The saturated industry is consolidating.
        """
        maturity = determine_maturity_level(search_results)

        assert maturity == "mature"

    def test_declining_market_detected(self):
        """Test declining market detection."""
        search_results = """
        The market is declining with shrinking demand.
        Industry is contracting and being disrupted.
        """
        maturity = determine_maturity_level(search_results)

        assert maturity == "declining"

    def test_default_to_growing(self):
        """Test default to growing when unclear."""
        search_results = "Generic market information without indicators."
        maturity = determine_maturity_level(search_results)

        assert maturity == "growing"


class TestExtractCustomerSegments:
    """Test cases for extract_customer_segments."""

    def test_health_segment_detected(self):
        """Test health-conscious segment detection."""
        search_results = """
        Health and fitness enthusiasts are driving demand.
        Wellness-focused consumers prefer premium options.
        """
        segments = extract_customer_segments(search_results, "blender")

        segment_names = [s["name"] for s in segments]
        assert any("health" in name.lower() for name in segment_names)

    def test_budget_segment_detected(self):
        """Test budget-conscious segment detection."""
        search_results = """
        Budget shoppers look for affordable options.
        Value-conscious consumers drive the cheap segment.
        """
        segments = extract_customer_segments(search_results, "electronics")

        segment_names = [s["name"] for s in segments]
        assert any("budget" in name.lower() for name in segment_names)

    def test_percentage_calculation(self):
        """Test segment percentage calculation."""
        search_results = """
        Health health health fitness wellness.
        Budget affordable cheap.
        Professional.
        """
        segments = extract_customer_segments(search_results, "product")

        # Check percentages add up reasonably
        total_pct = sum(s["percentage"] for s in segments if s["percentage"])
        assert total_pct > 0

    def test_limited_to_6_segments(self):
        """Test that segments are limited to 6."""
        search_results = """
        Health fitness wellness student college young family parent
        travel portable professional budget affordable premium luxury
        tech smart connected digital
        """
        segments = extract_customer_segments(search_results, "product")

        assert len(segments) <= 6


class TestCalculateMarketScore:
    """Test cases for calculate_market_score."""

    def test_large_market_high_growth_scores_high(self):
        """Test large growing market gets high score."""
        market_size = {"tam": 10_000_000_000, "sam": 3_000_000_000, "som": 1_000_000_000}
        growth_rate = 0.25
        maturity = "growing"

        score = calculate_market_score(market_size, growth_rate, maturity)

        assert score >= 80

    def test_small_market_low_growth_scores_low(self):
        """Test small declining market gets low score."""
        market_size = {"tam": 5_000_000, "sam": 1_000_000, "som": 100_000}
        growth_rate = 0.02
        maturity = "declining"

        score = calculate_market_score(market_size, growth_rate, maturity)

        assert score <= 50

    def test_score_bounded(self):
        """Test score is always 1-100."""
        # Very small market
        score_low = calculate_market_score(
            {"som": 1000}, 0.01, "declining"
        )
        assert 1 <= score_low <= 100

        # Very large market
        score_high = calculate_market_score(
            {"som": 100_000_000_000}, 0.50, "growing"
        )
        assert 1 <= score_high <= 100


class TestFormatMarketResults:
    """Test cases for format_market_results."""

    def test_format_large_market(self):
        """Test formatting of large market results."""
        results = {
            "market_score": 85,
            "market_size": {
                "tam": 10_000_000_000,
                "sam": 3_000_000_000,
                "som": 500_000_000,
                "currency": "USD"
            },
            "growth_rate": 0.15,
            "maturity_level": "growing",
            "customer_segments": [
                {"name": "Health Conscious", "percentage": 40},
                {"name": "Professionals", "percentage": 30}
            ]
        }
        formatted = format_market_results(results)

        assert "85/100" in formatted
        assert "$10.0B" in formatted
        assert "15.0%" in formatted
        assert "Growing" in formatted
        assert "📈" in formatted

    def test_format_small_market(self):
        """Test formatting of smaller market."""
        results = {
            "market_score": 45,
            "market_size": {
                "tam": 50_000_000,
                "sam": 10_000_000,
                "som": 1_000_000,
                "currency": "USD"
            },
            "growth_rate": 0.08,
            "maturity_level": "mature",
            "customer_segments": []
        }
        formatted = format_market_results(results)

        assert "45/100" in formatted
        assert "$50.0M" in formatted
        assert "Mature" in formatted
