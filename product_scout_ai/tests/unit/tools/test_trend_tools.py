"""
Tests for tools/trend_tools.py
"""
import pytest
from src.tools.trend_tools import (
    extract_trend_signals,
    calculate_trend_score,
    extract_seasonality,
    extract_related_queries,
    format_trend_results,
)


class TestExtractTrendSignals:
    """Test cases for extract_trend_signals."""

    def test_rising_trend_detected(self):
        """Test that rising trend signals are detected."""
        search_results = """
        The portable blender market is growing rapidly with increasing demand.
        Sales are trending upward with a surge in consumer interest.
        The market is experiencing a boom in popularity.
        """
        signals = extract_trend_signals(search_results)

        assert signals["trend_direction"] == "rising"
        assert signals["rising_signals"] > 0

    def test_declining_trend_detected(self):
        """Test that declining trend signals are detected."""
        search_results = """
        Market sales are declining as consumer interest is falling.
        The category is slowing down with dropping demand.
        Industry experts note decreasing market share.
        """
        signals = extract_trend_signals(search_results)

        assert signals["trend_direction"] == "declining"
        assert signals["declining_signals"] > 0

    def test_stable_trend_detected(self):
        """Test that stable trend is detected as default."""
        search_results = """
        The market remains steady with consistent sales.
        Consumer demand is flat but stable over time.
        """
        signals = extract_trend_signals(search_results)

        assert signals["trend_direction"] == "stable"

    def test_growth_rates_extracted(self):
        """Test that growth rates are extracted from text."""
        search_results = """
        The market showed 15% growth last year.
        Analysts predict 20% increase in demand.
        """
        signals = extract_trend_signals(search_results)

        assert len(signals["growth_rates"]) > 0
        assert 15.0 in signals["growth_rates"] or 20.0 in signals["growth_rates"]

    def test_empty_results_returns_stable(self):
        """Test empty results default to stable."""
        signals = extract_trend_signals("")

        assert signals["trend_direction"] == "stable"


class TestCalculateTrendScore:
    """Test cases for calculate_trend_score."""

    def test_rising_trend_high_score(self):
        """Test that rising trends get higher scores."""
        signals = {
            "trend_direction": "rising",
            "rising_signals": 5,
            "declining_signals": 0,
            "stable_signals": 0,
            "growth_rates": [15.0]
        }
        score = calculate_trend_score(signals)

        assert score >= 70

    def test_declining_trend_low_score(self):
        """Test that declining trends get lower scores."""
        signals = {
            "trend_direction": "declining",
            "rising_signals": 0,
            "declining_signals": 5,
            "stable_signals": 0,
            "growth_rates": []
        }
        score = calculate_trend_score(signals)

        assert score <= 40

    def test_stable_trend_medium_score(self):
        """Test that stable trends get medium scores."""
        signals = {
            "trend_direction": "stable",
            "rising_signals": 1,
            "declining_signals": 1,
            "stable_signals": 2,
            "growth_rates": []
        }
        score = calculate_trend_score(signals)

        assert 40 <= score <= 60

    def test_score_bounded(self):
        """Test that score is always within 1-100."""
        # Very negative signals
        signals_negative = {
            "trend_direction": "declining",
            "rising_signals": 0,
            "declining_signals": 100,
            "stable_signals": 0,
            "growth_rates": []
        }
        assert 1 <= calculate_trend_score(signals_negative) <= 100

        # Very positive signals
        signals_positive = {
            "trend_direction": "rising",
            "rising_signals": 100,
            "declining_signals": 0,
            "stable_signals": 0,
            "growth_rates": [50, 60, 70]
        }
        assert 1 <= calculate_trend_score(signals_positive) <= 100


class TestExtractSeasonality:
    """Test cases for extract_seasonality."""

    def test_summer_seasonality_detected(self):
        """Test that summer seasonality is detected."""
        search_results = """
        Portable blenders are most popular in summer months.
        Sales peak in June, July and August.
        Hot weather drives demand for smoothie makers.
        """
        seasonality = extract_seasonality(search_results, "portable blender")

        assert "summer" in seasonality["peak_seasons"]
        assert seasonality["is_seasonal"] is True

    def test_winter_holiday_seasonality(self):
        """Test that winter/holiday seasonality is detected."""
        search_results = """
        Gift sales peak during the holiday season.
        December and Christmas drive the highest demand.
        Winter months see increased consumer spending.
        """
        seasonality = extract_seasonality(search_results, "gift items")

        assert "winter" in seasonality["peak_seasons"]

    def test_year_round_product(self):
        """Test products without clear seasonality."""
        search_results = """
        This product category shows consistent demand.
        Sales are relatively even throughout the year.
        """
        seasonality = extract_seasonality(search_results, "office supplies")

        assert "year-round" in seasonality["peak_seasons"]

    def test_peak_months_extracted(self):
        """Test that specific months are extracted."""
        search_results = """
        Sales peak in November and December.
        January also shows strong performance.
        """
        seasonality = extract_seasonality(search_results, "electronics")

        assert len(seasonality["peak_months"]) > 0


class TestExtractRelatedQueries:
    """Test cases for extract_related_queries."""

    def test_related_terms_found(self):
        """Test that related terms are found."""
        search_results = """
        Best portable blender reviews show top models.
        Cheap alternatives are also popular.
        Professional users prefer premium options.
        """
        queries = extract_related_queries(search_results, "portable blender")

        assert len(queries) > 0
        query_texts = [q["query"] for q in queries]
        assert any("best" in q for q in query_texts)

    def test_relevance_scoring(self):
        """Test that relevance is scored based on frequency."""
        search_results = """
        Best products. Best reviews. Best options. Best deals.
        Cheap alternatives available.
        """
        queries = extract_related_queries(search_results, "blender")

        # "best" appears multiple times, should have high relevance
        best_queries = [q for q in queries if "best" in q["query"]]
        if best_queries:
            assert best_queries[0]["relevance"] == "high"

    def test_limited_to_10_queries(self):
        """Test that queries are limited to 10."""
        search_results = """
        Best top review cheap affordable premium comparison vs
        alternative portable mini professional budget quality
        """
        queries = extract_related_queries(search_results, "product")

        assert len(queries) <= 10


class TestFormatTrendResults:
    """Test cases for format_trend_results."""

    def test_format_rising_trend(self):
        """Test formatting of rising trend results."""
        results = {
            "trend_score": 75,
            "trend_direction": "rising",
            "seasonality": {
                "peak_seasons": ["summer"],
                "is_seasonal": True
            },
            "related_queries": [
                {"query": "best blender", "relevance": "high"},
                {"query": "cheap blender", "relevance": "medium"}
            ]
        }
        formatted = format_trend_results(results)

        assert "75/100" in formatted
        assert "Rising" in formatted
        assert "📈" in formatted
        assert "summer" in formatted

    def test_format_declining_trend(self):
        """Test formatting of declining trend results."""
        results = {
            "trend_score": 30,
            "trend_direction": "declining",
            "seasonality": {"peak_seasons": ["winter"], "is_seasonal": False},
            "related_queries": []
        }
        formatted = format_trend_results(results)

        assert "30/100" in formatted
        assert "Declining" in formatted
        assert "📉" in formatted

    def test_format_with_empty_queries(self):
        """Test formatting with no related queries."""
        results = {
            "trend_score": 50,
            "trend_direction": "stable",
            "seasonality": {"peak_seasons": ["year-round"], "is_seasonal": False},
            "related_queries": []
        }
        formatted = format_trend_results(results)

        assert "50/100" in formatted
        assert "Stable" in formatted
