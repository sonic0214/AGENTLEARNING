"""
End-to-end tests for ProductScout AI Gradio UI.

These tests verify the UI functionality by testing handlers and components directly.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ui.handlers.analysis_handlers import (
    validate_inputs,
    create_analysis_request,
    get_dimension_scores,
    get_overall_score,
)
from src.ui.handlers.history_handlers import (
    get_history_dataframe,
    get_history_statistics,
    get_history_for_dropdown,
    clear_history,
)
from src.ui.handlers.export_handlers import (
    get_export_preview,
    export_analysis,
)
from src.ui.components.charts import (
    create_radar_chart,
    create_bar_chart,
    create_comparison_radar,
)
from src.ui.utils.formatters import (
    format_score,
    format_percentage,
    format_currency,
    format_trend_direction,
    format_recommendation,
    format_number,
    format_duration,
    format_market_size,
    format_score_label,
)


class TestInputValidation:
    """Test input validation for analysis tab."""

    def test_valid_inputs(self):
        """Test validation with valid inputs."""
        is_valid, error = validate_inputs("智能手表", "US", "1000-5000", "B2C零售", "")
        assert is_valid is True
        assert error == ""

    def test_empty_category(self):
        """Test validation with empty category."""
        is_valid, error = validate_inputs("", "US", "1000-5000", "B2C零售", "")
        assert is_valid is False
        assert "产品类别" in error

    def test_short_category(self):
        """Test validation with very short category."""
        is_valid, error = validate_inputs("A", "US", "1000-5000", "B2C零售", "")
        assert is_valid is False
        assert "字符" in error

    def test_whitespace_only_category(self):
        """Test validation with whitespace-only category."""
        is_valid, error = validate_inputs("   ", "US", "1000-5000", "B2C零售", "")
        assert is_valid is False
        assert "产品类别" in error

    def test_too_many_keywords(self):
        """Test validation with too many keywords."""
        many_keywords = ",".join([f"keyword{i}" for i in range(15)])
        is_valid, error = validate_inputs("智能手表", "US", "1000-5000", "B2C零售", many_keywords)
        assert is_valid is False
        assert "关键词" in error


class TestAnalysisRequestCreation:
    """Test analysis request creation."""

    def test_create_request_with_defaults(self):
        """Test creating request with default values."""
        request = create_analysis_request(
            category="智能手表",
            market="US",
            budget="1000-5000",
            model="B2C零售",
            keywords=""
        )
        assert request.category == "智能手表"
        assert request.target_market == "US"
        assert request.budget_range == "1000-5000"
        assert request.business_model.lower() == "b2c零售"
        assert request.keywords == []

    def test_create_request_with_keywords(self):
        """Test creating request with keywords."""
        request = create_analysis_request(
            category="无线耳机",
            market="EU",
            budget="500-2000",
            model="B2B批发",
            keywords="蓝牙, 降噪, 运动"
        )
        assert request.category == "无线耳机"
        assert len(request.keywords) == 3
        assert "蓝牙" in request.keywords

    def test_create_request_strips_whitespace(self):
        """Test that request strips whitespace from category."""
        request = create_analysis_request(
            category="  手机配件  ",
            market="US",
            budget="500-2000",
            model="B2C零售",
            keywords=""
        )
        assert request.category == "手机配件"


class TestHistoryHandlers:
    """Test history management handlers."""

    def test_get_empty_history(self):
        """Test getting history when empty."""
        clear_history()
        df = get_history_dataframe()
        assert len(df) == 0

    def test_get_history_statistics_empty(self):
        """Test statistics when history is empty."""
        clear_history()
        stats = get_history_statistics()
        assert stats["total"] == 0
        assert stats["successful"] == 0
        assert stats["avg_time"] == 0

    def test_get_history_for_dropdown_empty(self):
        """Test dropdown options when history is empty."""
        clear_history()
        options = get_history_for_dropdown()
        assert len(options) == 0

    def test_history_dataframe_columns(self):
        """Test that history dataframe has correct columns."""
        df = get_history_dataframe()
        expected_columns = ["日期", "产品类别", "市场", "模式", "评分", "建议", "耗时", "状态"]
        assert list(df.columns) == expected_columns


class TestExportHandlers:
    """Test export functionality handlers."""

    def test_export_preview_json(self):
        """Test JSON export preview."""
        result_data = {
            "request": {
                "category": "测试产品",
                "target_market": "US"
            },
            "evaluation_result": {
                "opportunity_score": 75,
                "recommendation": "proceed"
            }
        }

        content = get_export_preview(result_data, "JSON")
        assert "测试产品" in content
        assert "75" in content

    def test_export_preview_summary(self):
        """Test Summary export preview."""
        result_data = {
            "request": {
                "category": "摘要测试",
                "target_market": "UK"
            },
            "evaluation_result": {
                "opportunity_score": 65,
                "recommendation": "cautious"
            }
        }

        content = get_export_preview(result_data, "Summary")
        assert len(content) > 0

    def test_export_analysis_json(self):
        """Test full JSON export."""
        result_data = {
            "request": {
                "category": "导出测试",
                "target_market": "CA"
            }
        }

        content, filename = export_analysis(result_data, "JSON")
        assert ".json" in filename
        assert "导出测试" in content

    def test_export_analysis_with_empty_data(self):
        """Test export with minimal data."""
        result_data = {"request": {"category": "空数据测试"}}
        content, filename = export_analysis(result_data, "JSON")
        assert len(content) > 0
        assert len(filename) > 0


class TestChartComponents:
    """Test chart generation components."""

    def test_create_radar_chart(self):
        """Test radar chart creation."""
        scores = {
            "趋势": 75,
            "市场": 80,
            "竞争": 65,
            "利润": 70
        }

        fig = create_radar_chart(scores, "测试雷达图")
        assert fig is not None
        assert hasattr(fig, 'data')

    def test_create_bar_chart(self):
        """Test bar chart creation."""
        scores = {
            "维度A": 85,
            "维度B": 72,
            "维度C": 90
        }

        fig = create_bar_chart(scores, "测试柱状图")
        assert fig is not None
        assert hasattr(fig, 'data')

    def test_create_comparison_radar(self):
        """Test comparison radar chart creation."""
        scores_a = {"趋势": 70, "市场": 75, "竞争": 80, "利润": 65}
        scores_b = {"趋势": 80, "市场": 70, "竞争": 75, "利润": 85}

        fig = create_comparison_radar(
            scores_a, scores_b,
            "产品A", "产品B",
            "对比测试"
        )
        assert fig is not None
        assert len(fig.data) >= 2

    def test_create_bar_chart_with_single_value(self):
        """Test bar chart with single value."""
        scores = {"唯一": 50}
        fig = create_bar_chart(scores, "单值测试")
        assert fig is not None


class TestFormatters:
    """Test utility formatters."""

    def test_format_score(self):
        """Test score formatting."""
        assert format_score(85) == "85/100"
        assert format_score(0) == "0/100"
        assert format_score(100) == "100/100"

    def test_format_percentage(self):
        """Test percentage formatting."""
        assert "75" in format_percentage(0.75)
        assert "%" in format_percentage(0.75)
        assert "50" in format_percentage(0.5)

    def test_format_currency(self):
        """Test currency formatting."""
        result = format_currency(1000)
        assert "$" in result
        assert "1" in result

    def test_format_currency_with_different_currencies(self):
        """Test currency formatting with different currencies."""
        usd = format_currency(1000, "USD")
        eur = format_currency(1000, "EUR")
        assert "$" in usd
        assert "€" in eur

    def test_format_trend_direction(self):
        """Test trend direction formatting."""
        rising = format_trend_direction("rising")
        declining = format_trend_direction("declining")
        stable = format_trend_direction("stable")

        assert "上升" in rising
        assert "下降" in declining
        assert "稳定" in stable

    def test_format_recommendation(self):
        """Test recommendation formatting."""
        go = format_recommendation("go")
        cautious = format_recommendation("cautious")
        no_go = format_recommendation("no-go")

        assert "推荐" in go
        assert "谨慎" in cautious
        assert "不建议" in no_go

    def test_format_number(self):
        """Test number formatting."""
        result = format_number(1000000)
        assert "1,000,000" == result

    def test_format_duration(self):
        """Test duration formatting."""
        assert "30.0s" == format_duration(30)
        assert "1m" in format_duration(90)
        assert "1h" in format_duration(3700)

    def test_format_market_size(self):
        """Test market size formatting."""
        assert "B" in format_market_size(1_500_000_000)
        assert "M" in format_market_size(50_000_000)
        assert "K" in format_market_size(50_000)

    def test_format_score_label(self):
        """Test score label formatting."""
        assert format_score_label(85) == "优秀"
        assert format_score_label(75) == "良好"
        assert format_score_label(65) == "中等"
        assert format_score_label(45) == "一般"
        assert format_score_label(30) == "较差"


class TestDimensionScores:
    """Test dimension score extraction."""

    def test_get_dimension_scores_empty(self):
        """Test extracting scores from empty data."""
        scores = get_dimension_scores({})
        assert scores == {}

    def test_get_dimension_scores_partial(self):
        """Test extracting scores from partial data."""
        result_data = {
            "trend_analysis": {"trend_score": 75},
            "market_analysis": {"market_score": 80}
        }
        scores = get_dimension_scores(result_data)
        assert scores["趋势"] == 75
        assert scores["市场"] == 80
        assert "竞争" not in scores

    def test_get_dimension_scores_full(self):
        """Test extracting all scores."""
        result_data = {
            "trend_analysis": {"trend_score": 75},
            "market_analysis": {"market_score": 80},
            "competition_analysis": {"competition_score": 65},
            "profit_analysis": {"profit_score": 70}
        }
        scores = get_dimension_scores(result_data)
        assert len(scores) == 4


class TestOverallScore:
    """Test overall score extraction."""

    def test_get_overall_score_empty(self):
        """Test getting score from empty data."""
        score, rec, detail = get_overall_score({})
        assert score == 0
        assert rec == "unknown"
        assert detail == ""

    def test_get_overall_score_valid(self):
        """Test getting score from valid data."""
        result_data = {
            "evaluation_result": {
                "opportunity_score": 78,
                "recommendation": "go",
                "recommendation_detail": "市场前景良好"
            }
        }
        score, rec, detail = get_overall_score(result_data)
        assert score == 78
        assert rec == "go"
        assert "市场" in detail


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_special_characters_in_category(self):
        """Test handling special characters in category."""
        is_valid, _ = validate_inputs("产品<script>test</script>", "US", "1000", "B2C零售", "")
        assert is_valid is True

    def test_very_long_category(self):
        """Test handling very long category name."""
        long_category = "A" * 500
        is_valid, error = validate_inputs(long_category, "US", "1000", "B2C零售", "")
        assert is_valid is False
        assert "200" in error

    def test_unicode_in_inputs(self):
        """Test handling unicode characters."""
        is_valid, _ = validate_inputs("日本語製品", "JP", "1000-5000", "B2C零售", "")
        assert is_valid is True

    def test_chart_with_negative_scores(self):
        """Test charts handle negative scores."""
        scores = {"A": -10, "B": 50, "C": 100}
        fig = create_bar_chart(scores, "负数测试")
        assert fig is not None

    def test_chart_with_large_scores(self):
        """Test charts handle large scores."""
        scores = {"A": 10000, "B": 50000, "C": 100000}
        fig = create_bar_chart(scores, "大数测试")
        assert fig is not None

    def test_format_unknown_recommendation(self):
        """Test formatting unknown recommendation."""
        result = format_recommendation("unknown_value")
        assert result == "unknown_value"

    def test_format_unknown_trend(self):
        """Test formatting unknown trend direction."""
        result = format_trend_direction("unknown")
        assert result == "unknown"


class TestExportFormats:
    """Test different export formats."""

    def test_json_export_structure(self):
        """Test JSON export has proper structure."""
        result_data = {
            "request": {"category": "测试"},
            "evaluation_result": {"opportunity_score": 80}
        }
        content, _ = export_analysis(result_data, "JSON")
        import json
        parsed = json.loads(content)
        assert "request" in parsed
        assert parsed["request"]["category"] == "测试"

    def test_export_filename_format(self):
        """Test export filename format."""
        result_data = {"request": {"category": "测试产品"}}

        _, json_name = export_analysis(result_data, "JSON")
        assert json_name.endswith(".json")
        assert "测试产品" in json_name

        _, md_name = export_analysis(result_data, "Markdown")
        assert md_name.endswith(".md")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
