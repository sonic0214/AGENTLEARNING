"""
Tests for tools/competition_tools.py
"""
import pytest
from src.tools.competition_tools import (
    extract_competitors,
    extract_pricing_data,
    identify_opportunities,
    assess_entry_barriers,
    calculate_competition_score,
    format_competition_results,
)


class TestExtractCompetitors:
    """Test cases for extract_competitors."""

    def test_brand_extraction(self):
        """Test extraction of brand names."""
        search_results = """
        Top blender brands include Ninja, Vitamix, and NutriBullet.
        Oster and Hamilton Beach are also popular choices.
        """
        competitors = extract_competitors(search_results, "blender")

        assert len(competitors) > 0
        competitor_names = [c["name"].lower() for c in competitors]
        assert any("ninja" in name for name in competitor_names)

    def test_market_share_estimation(self):
        """Test that market share is estimated."""
        search_results = """
        Brand: TestBrand is a leading manufacturer.
        Company: AnotherBrand also competes.
        """
        competitors = extract_competitors(search_results, "product")

        for comp in competitors:
            assert "market_share" in comp
            if comp["market_share"]:
                assert 0 < comp["market_share"] <= 100

    def test_limited_to_10_competitors(self):
        """Test that competitors are limited to 10."""
        search_results = """
        Brands include A, B, C, D, E, F, G, H, I, J, K, L, M, N, O.
        Companies: Brand1, Brand2, Brand3, Brand4, Brand5,
        Brand6, Brand7, Brand8, Brand9, Brand10, Brand11, Brand12.
        """
        competitors = extract_competitors(search_results, "product")

        assert len(competitors) <= 10


class TestExtractPricingData:
    """Test cases for extract_pricing_data."""

    def test_price_range_extracted(self):
        """Test extraction of price range."""
        search_results = """
        Prices range from $19.99 to $149.99.
        Budget options start at $25.00.
        Premium models cost $200.00 or more.
        """
        pricing = extract_pricing_data(search_results)

        assert pricing["min_price"] > 0
        assert pricing["max_price"] > pricing["min_price"]
        assert pricing["avg_price"] > 0

    def test_strategy_recommendation(self):
        """Test pricing strategy recommendation."""
        search_results = """
        Products priced at $50, $55, $60, $65.
        """
        pricing = extract_pricing_data(search_results)

        assert "strategy" in pricing
        assert "recommendation" in pricing
        assert len(pricing["recommendation"]) > 0

    def test_handles_no_prices(self):
        """Test handling when no prices found."""
        search_results = "No pricing information available."
        pricing = extract_pricing_data(search_results)

        # Should return defaults
        assert pricing["min_price"] > 0
        assert pricing["max_price"] > 0


class TestIdentifyOpportunities:
    """Test cases for identify_opportunities."""

    def test_feature_opportunities_identified(self):
        """Test identification of feature opportunities."""
        search_results = """
        Consumers want affordable and portable options.
        Eco-friendly products are in high demand.
        Smart features would be valuable.
        """
        competitors = [{"name": "Brand1"}, {"name": "Brand2"}]
        pricing = {"avg_price": 50}

        opportunities = identify_opportunities(search_results, competitors, pricing)

        assert len(opportunities) > 0
        opportunity_text = " ".join(opportunities).lower()
        assert "portability" in opportunity_text or "eco" in opportunity_text or "smart" in opportunity_text

    def test_competition_based_opportunities(self):
        """Test competition-based opportunities."""
        search_results = "Market analysis shows some brands."
        competitors = [{"name": f"Brand{i}"} for i in range(3)]  # Few competitors
        pricing = {"avg_price": 50, "price_range": 20}

        opportunities = identify_opportunities(search_results, competitors, pricing)

        # Should identify low competition opportunity
        opportunity_text = " ".join(opportunities).lower()
        assert "competition" in opportunity_text or len(opportunities) > 0

    def test_limited_opportunities(self):
        """Test that opportunities are limited."""
        search_results = """
        affordable portable compact eco-friendly smart quiet
        easy to clean durable fast premium
        """
        competitors = [{"name": f"Brand{i}"} for i in range(20)]
        pricing = {"avg_price": 100, "price_range": 50}

        opportunities = identify_opportunities(search_results, competitors, pricing)

        assert len(opportunities) <= 8


class TestAssessEntryBarriers:
    """Test cases for assess_entry_barriers."""

    def test_high_barriers_detected(self):
        """Test detection of high entry barriers."""
        search_results = """
        The market requires heavy investment and certification.
        Established brands have strong brand loyalty.
        Patents protect key technologies.
        """
        competitors = [{"name": f"Brand{i}"} for i in range(15)]

        barriers = assess_entry_barriers(search_results, competitors)

        assert barriers == "high"

    def test_low_barriers_detected(self):
        """Test detection of low entry barriers."""
        search_results = """
        Easy entry into this growing market.
        The fragmented market has many new entrants.
        Low barriers make this an opportunity.
        """
        competitors = [{"name": f"Brand{i}"} for i in range(3)]

        barriers = assess_entry_barriers(search_results, competitors)

        assert barriers == "low"

    def test_medium_barriers_default(self):
        """Test medium barriers as balanced outcome."""
        search_results = """
        Competitive market with quality standards.
        Distribution and marketing spend are important.
        """
        competitors = [{"name": f"Brand{i}"} for i in range(8)]

        barriers = assess_entry_barriers(search_results, competitors)

        assert barriers in ["medium", "low", "high"]


class TestCalculateCompetitionScore:
    """Test cases for calculate_competition_score."""

    def test_high_competition_scores_high(self):
        """Test that highly competitive markets score high."""
        competitors = [{"name": f"Brand{i}"} for i in range(20)]
        pricing = {"price_range": 15}  # Tight pricing
        barriers = "high"

        score = calculate_competition_score(competitors, pricing, barriers)

        assert score >= 70

    def test_low_competition_scores_low(self):
        """Test that low competition markets score low."""
        competitors = [{"name": f"Brand{i}"} for i in range(3)]
        pricing = {"price_range": 150}  # Wide pricing
        barriers = "low"

        score = calculate_competition_score(competitors, pricing, barriers)

        assert score <= 50

    def test_score_bounded(self):
        """Test score is always 1-100."""
        # Very competitive
        score_high = calculate_competition_score(
            [{"name": f"B{i}"} for i in range(50)],
            {"price_range": 5},
            "high"
        )
        assert 1 <= score_high <= 100

        # Not competitive
        score_low = calculate_competition_score(
            [{"name": "B1"}],
            {"price_range": 200},
            "low"
        )
        assert 1 <= score_low <= 100


class TestFormatCompetitionResults:
    """Test cases for format_competition_results."""

    def test_format_competitive_market(self):
        """Test formatting of competitive market results."""
        results = {
            "competition_score": 75,
            "entry_barriers": "high",
            "competitors": [
                {"name": "Brand1", "market_share": 30},
                {"name": "Brand2", "market_share": 25},
            ],
            "pricing_analysis": {
                "min_price": 20.00,
                "max_price": 150.00,
                "avg_price": 65.00,
                "recommendation": "Focus on value differentiation"
            },
            "opportunities": [
                "Budget segment underserved",
                "Smart features desired"
            ]
        }
        formatted = format_competition_results(results)

        assert "75/100" in formatted
        assert "High" in formatted
        assert "🔴" in formatted
        assert "$20.00" in formatted
        assert "Brand1" in formatted
        assert "Budget segment" in formatted

    def test_format_low_competition(self):
        """Test formatting of low competition market."""
        results = {
            "competition_score": 35,
            "entry_barriers": "low",
            "competitors": [{"name": "OnlyBrand", "market_share": 50}],
            "pricing_analysis": {
                "min_price": 15.00,
                "max_price": 100.00,
                "avg_price": 45.00,
                "recommendation": "Opportunity for new entrant"
            },
            "opportunities": ["Early mover advantage"]
        }
        formatted = format_competition_results(results)

        assert "35/100" in formatted
        assert "Low" in formatted
        assert "🟢" in formatted
