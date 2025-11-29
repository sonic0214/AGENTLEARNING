"""
Tests for tools/profit_tools.py
"""
import pytest
from src.tools.profit_tools import (
    calculate_unit_economics,
    calculate_margins,
    calculate_monthly_projection,
    calculate_investment_requirements,
    calculate_roi_metrics,
    calculate_profit_score,
    format_profit_results,
    COST_STRUCTURES,
    BUDGET_RANGES,
)


class TestCalculateUnitEconomics:
    """Test cases for calculate_unit_economics."""

    def test_amazon_fba_unit_economics(self):
        """Test Amazon FBA unit economics calculation."""
        cost_data = {"estimated_cogs": 10.00, "estimated_shipping": 3.00}
        unit_econ = calculate_unit_economics(50.00, "amazon_fba", cost_data)

        assert unit_econ["retail_price"] == 50.00
        assert unit_econ["cogs"] == 10.00
        assert "fulfillment_fee" in unit_econ
        assert "referral_fee" in unit_econ
        assert unit_econ["total_costs"] > 0
        assert "profit_per_unit" in unit_econ

    def test_dropshipping_unit_economics(self):
        """Test dropshipping unit economics calculation."""
        cost_data = {"estimated_cogs": 15.00, "estimated_shipping": 5.00}
        unit_econ = calculate_unit_economics(45.00, "dropshipping", cost_data)

        assert unit_econ["retail_price"] == 45.00
        assert "platform_fee" in unit_econ
        assert "advertising" in unit_econ
        assert unit_econ["total_costs"] > 0

    def test_private_label_unit_economics(self):
        """Test private label unit economics calculation."""
        cost_data = {"estimated_cogs": 8.00, "estimated_shipping": 2.00}
        unit_econ = calculate_unit_economics(40.00, "private_label", cost_data)

        assert unit_econ["retail_price"] == 40.00
        assert "manufacturing" in unit_econ
        assert "marketing" in unit_econ
        assert unit_econ["profit_per_unit"] is not None

    def test_profit_calculation_accuracy(self):
        """Test that profit = retail - total_costs."""
        cost_data = {"estimated_cogs": 10.00, "estimated_shipping": 5.00}
        unit_econ = calculate_unit_economics(100.00, "amazon_fba", cost_data)

        expected_profit = unit_econ["retail_price"] - unit_econ["total_costs"]
        assert abs(unit_econ["profit_per_unit"] - expected_profit) < 0.01


class TestCalculateMargins:
    """Test cases for calculate_margins."""

    def test_margin_calculation(self):
        """Test margin calculations."""
        unit_econ = {
            "retail_price": 50.00,
            "cogs": 12.50,
            "total_costs": 35.00,
            "profit_per_unit": 15.00
        }
        margins = calculate_margins(unit_econ)

        assert "gross_margin" in margins
        assert "net_margin" in margins
        assert "markup" in margins
        assert 0 < margins["gross_margin"] < 1
        assert margins["net_margin"] == 0.30  # 15/50

    def test_margin_percentages(self):
        """Test margin percentage formatting."""
        unit_econ = {
            "retail_price": 100.00,
            "cogs": 25.00,
            "total_costs": 60.00,
            "profit_per_unit": 40.00
        }
        margins = calculate_margins(unit_econ)

        assert margins["gross_margin_percent"] == 75.0  # (100-25)/100
        assert margins["net_margin_percent"] == 40.0  # 40/100


class TestCalculateMonthlyProjection:
    """Test cases for calculate_monthly_projection."""

    def test_monthly_revenue_projection(self):
        """Test monthly revenue projection."""
        unit_econ = {
            "retail_price": 40.00,
            "total_costs": 25.00,
            "profit_per_unit": 15.00
        }
        projection = calculate_monthly_projection(unit_econ, 200)

        assert projection["units_per_month"] == 200
        assert projection["monthly_revenue"] == 8000.00  # 40 * 200
        assert projection["monthly_profit"] == 3000.00  # 15 * 200
        assert projection["annual_profit"] == 36000.00  # 3000 * 12

    def test_zero_units(self):
        """Test with zero units."""
        unit_econ = {
            "retail_price": 50.00,
            "total_costs": 30.00,
            "profit_per_unit": 20.00
        }
        projection = calculate_monthly_projection(unit_econ, 0)

        assert projection["monthly_revenue"] == 0
        assert projection["monthly_profit"] == 0


class TestCalculateInvestmentRequirements:
    """Test cases for calculate_investment_requirements."""

    def test_low_budget_investment(self):
        """Test low budget investment calculation."""
        unit_econ = {"cogs": 10.00}
        investment = calculate_investment_requirements(unit_econ, "low", "amazon_fba")

        assert investment["total_investment"] > 0
        assert investment["initial_inventory"] > 0
        assert investment["marketing_budget"] > 0
        assert investment["total_investment"] <= BUDGET_RANGES["low"]["max"] * 2

    def test_high_budget_investment(self):
        """Test high budget investment calculation."""
        unit_econ = {"cogs": 15.00}
        investment = calculate_investment_requirements(unit_econ, "high", "amazon_fba")

        assert investment["total_investment"] > BUDGET_RANGES["low"]["max"]
        assert investment["units_to_purchase"] == BUDGET_RANGES["high"]["units_target"]

    def test_business_model_specific_costs(self):
        """Test business model specific costs."""
        unit_econ = {"cogs": 10.00}

        fba_investment = calculate_investment_requirements(unit_econ, "medium", "amazon_fba")
        dropship_investment = calculate_investment_requirements(unit_econ, "medium", "dropshipping")

        # Different setup costs for different models
        assert fba_investment["setup_costs"] != dropship_investment["setup_costs"]


class TestCalculateRoiMetrics:
    """Test cases for calculate_roi_metrics."""

    def test_roi_calculation(self):
        """Test ROI calculation."""
        monthly_projection = {
            "monthly_profit": 3000.00,
            "annual_profit": 36000.00
        }
        investment = {"total_investment": 10000.00}

        roi = calculate_roi_metrics(monthly_projection, investment)

        assert roi["annual_roi"] == 3.6  # 36000/10000
        assert roi["annual_roi_percent"] == 360.0
        assert roi["profitable"] is True

    def test_payback_period(self):
        """Test payback period calculation."""
        monthly_projection = {
            "monthly_profit": 2000.00,
            "annual_profit": 24000.00
        }
        investment = {"total_investment": 6000.00}

        roi = calculate_roi_metrics(monthly_projection, investment)

        assert roi["payback_months"] == 3.0  # 6000/2000

    def test_rating_assignment(self):
        """Test profitability rating assignment."""
        # Excellent - payback <= 3 months
        roi_excellent = calculate_roi_metrics(
            {"monthly_profit": 5000, "annual_profit": 60000},
            {"total_investment": 10000}
        )
        assert roi_excellent["rating"] == "A"

        # Challenging - payback > 12 months
        roi_challenging = calculate_roi_metrics(
            {"monthly_profit": 500, "annual_profit": 6000},
            {"total_investment": 10000}
        )
        assert roi_challenging["rating"] == "D"

    def test_zero_profit_handling(self):
        """Test handling of zero profit."""
        roi = calculate_roi_metrics(
            {"monthly_profit": 0, "annual_profit": 0},
            {"total_investment": 10000}
        )

        assert roi["profitable"] is False
        assert roi["payback_months"] is None


class TestCalculateProfitScore:
    """Test cases for calculate_profit_score."""

    def test_high_margin_high_roi_scores_high(self):
        """Test high margin and ROI scores high."""
        margins = {"net_margin": 0.35}
        roi = {"annual_roi": 1.5, "payback_months": 2}

        score = calculate_profit_score(margins, roi)

        assert score >= 80

    def test_low_margin_scores_low(self):
        """Test low margin scores low."""
        margins = {"net_margin": 0.03}
        roi = {"annual_roi": 0.1, "payback_months": 24}

        score = calculate_profit_score(margins, roi)

        assert score <= 50

    def test_negative_margin_penalty(self):
        """Test negative margin gets penalty."""
        margins = {"net_margin": -0.10}
        roi = {"annual_roi": -0.5, "payback_months": None}

        score = calculate_profit_score(margins, roi)

        assert score < 50

    def test_score_bounded(self):
        """Test score is always 1-100."""
        # Very good
        score_high = calculate_profit_score(
            {"net_margin": 0.50},
            {"annual_roi": 5.0, "payback_months": 1}
        )
        assert 1 <= score_high <= 100

        # Very bad
        score_low = calculate_profit_score(
            {"net_margin": -0.20},
            {"annual_roi": -1.0, "payback_months": 100}
        )
        assert 1 <= score_low <= 100


class TestFormatProfitResults:
    """Test cases for format_profit_results."""

    def test_format_profitable_results(self):
        """Test formatting of profitable results."""
        results = {
            "profit_score": 78,
            "unit_economics": {
                "retail_price": 49.99,
                "total_costs": 32.00,
                "profit_per_unit": 17.99
            },
            "margins": {
                "gross_margin_percent": 70.0,
                "net_margin_percent": 36.0
            },
            "monthly_projection": {
                "units_per_month": 250,
                "monthly_revenue": 12497.50,
                "monthly_profit": 4497.50
            },
            "investment": {
                "total_investment": 8500.00
            },
            "assessment": {
                "rating": "A",
                "payback_months": 1.9,
                "annual_roi_percent": 635.0,
                "recommendation": "Excellent opportunity"
            }
        }
        formatted = format_profit_results(results)

        assert "78/100" in formatted
        assert "🌟" in formatted  # A rating emoji
        assert "$49.99" in formatted
        assert "$17.99" in formatted
        assert "36.0%" in formatted
        assert "1.9 months" in formatted

    def test_format_unprofitable_results(self):
        """Test formatting of unprofitable results."""
        results = {
            "profit_score": 25,
            "unit_economics": {
                "retail_price": 20.00,
                "total_costs": 22.00,
                "profit_per_unit": -2.00
            },
            "margins": {
                "gross_margin_percent": 25.0,
                "net_margin_percent": -10.0
            },
            "monthly_projection": {
                "units_per_month": 100,
                "monthly_revenue": 2000.00,
                "monthly_profit": -200.00
            },
            "investment": {
                "total_investment": 5000.00
            },
            "assessment": {
                "rating": "D",
                "payback_months": None,
                "annual_roi_percent": -48.0,
                "recommendation": "Review pricing strategy"
            }
        }
        formatted = format_profit_results(results)

        assert "25/100" in formatted
        assert "❌" in formatted  # D rating emoji
        assert "-$2.00" in formatted or "$-2.00" in formatted


class TestCostStructures:
    """Test cases for cost structure constants."""

    def test_all_business_models_defined(self):
        """Test that all business models have cost structures."""
        expected_models = ["amazon_fba", "dropshipping", "private_label", "wholesale"]

        for model in expected_models:
            assert model in COST_STRUCTURES
            assert len(COST_STRUCTURES[model]) > 0


class TestBudgetRanges:
    """Test cases for budget range constants."""

    def test_budget_ranges_hierarchy(self):
        """Test that budget ranges increase appropriately."""
        assert BUDGET_RANGES["low"]["max"] < BUDGET_RANGES["medium"]["max"]
        assert BUDGET_RANGES["medium"]["max"] < BUDGET_RANGES["high"]["max"]

    def test_budget_ranges_have_required_fields(self):
        """Test budget ranges have required fields."""
        for range_name, config in BUDGET_RANGES.items():
            assert "min" in config
            assert "max" in config
            assert "units_target" in config
