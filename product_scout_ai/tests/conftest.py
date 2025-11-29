"""
ProductScout AI - Test Configuration and Fixtures
"""
import pytest
import asyncio
from typing import Dict, Any, List
from unittest.mock import MagicMock, AsyncMock


# ============================================================================
# Async Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def sample_analysis_request() -> Dict[str, Any]:
    """Sample analysis request for testing."""
    return {
        "category": "portable blender",
        "target_market": "US",
        "budget_range": "medium",
        "business_model": "amazon_fba",
        "keywords": ["portable blender", "mini blender", "travel blender"]
    }


@pytest.fixture
def sample_trend_data() -> Dict[str, Any]:
    """Sample Google Trends data for testing."""
    return {
        "keywords": ["portable blender"],
        "geo": "US",
        "timeframe": "today 12-m",
        "trends": [
            {
                "keyword": "portable blender",
                "average_interest": 65,
                "peak_interest": 100,
                "current_interest": 72,
                "yoy_change": 15,
                "trend_direction": "rising",
                "seasonality": {
                    "peak_months": ["November", "December"],
                    "low_months": ["February", "March"]
                },
                "related_queries": [
                    {"query": "portable blender usb", "trend": "rising"},
                    {"query": "mini blender", "trend": "stable"}
                ]
            }
        ],
        "overall_trend_score": 75,
        "trend_direction": "rising"
    }


@pytest.fixture
def sample_market_data() -> Dict[str, Any]:
    """Sample market analysis data for testing."""
    return {
        "tam": 8500000000,  # $8.5B
        "sam": 2200000000,  # $2.2B
        "som": 50000000,    # $50M
        "currency": "USD",
        "growth_rate": 0.12,
        "customer_segments": [
            {"name": "Fitness Enthusiasts", "percentage": 35, "description": "Health-conscious consumers"},
            {"name": "Office Workers", "percentage": 30, "description": "Busy professionals"},
            {"name": "Students", "percentage": 20, "description": "Budget-conscious young adults"},
            {"name": "Travelers", "percentage": 15, "description": "Frequent travelers"}
        ],
        "maturity_level": "growing"
    }


@pytest.fixture
def sample_competition_data() -> Dict[str, Any]:
    """Sample competition analysis data for testing."""
    return {
        "competitors": [
            {"name": "BlendJet", "market_share": 25, "price_range": {"min": 39, "max": 49}},
            {"name": "Ninja", "market_share": 20, "price_range": {"min": 29, "max": 59}},
            {"name": "Hamilton Beach", "market_share": 15, "price_range": {"min": 19, "max": 29}}
        ],
        "competition_score": 68,
        "pricing_analysis": {
            "min_price": 19,
            "max_price": 59,
            "avg_price": 35,
            "recommended_range": {"min": 25, "max": 35}
        },
        "opportunities": [
            "USB-C charging standard",
            "Larger capacity models",
            "Premium materials"
        ]
    }


@pytest.fixture
def sample_profit_data() -> Dict[str, Any]:
    """Sample profit analysis data for testing."""
    return {
        "unit_economics": {
            "selling_price": 29.99,
            "product_cost": 8.50,
            "shipping_cost": 4.50,
            "gross_profit": 16.99,
            "net_profit": 5.00
        },
        "margins": {
            "gross_margin_pct": 56.7,
            "net_margin_pct": 16.7
        },
        "costs_breakdown": {
            "platform_fee": 4.50,
            "marketing_cost": 6.00,
            "return_cost": 1.50
        },
        "monthly_projection": {
            "units": 100,
            "revenue": 2999.00,
            "gross_profit": 1699.00,
            "net_profit": 500.00
        },
        "investment": {
            "initial_inventory": 1300.00,
            "roi_monthly_pct": 38.5
        },
        "assessment": {
            "profitable": True,
            "rating": "good",
            "recommendation": "proceed"
        }
    }


@pytest.fixture
def sample_evaluation_result() -> Dict[str, Any]:
    """Sample evaluation result for testing."""
    return {
        "opportunity_score": 78,
        "swot_analysis": {
            "strengths": ["Growing market", "Good margins"],
            "weaknesses": ["High competition"],
            "opportunities": ["USB-C trend", "Outdoor market"],
            "threats": ["Price wars", "Quality issues"]
        },
        "recommendation": "go",
        "key_risks": ["Competition intensity", "Seasonal demand"],
        "success_factors": ["Product differentiation", "Marketing strategy"]
    }


# ============================================================================
# Mock Service Fixtures
# ============================================================================

@pytest.fixture
def mock_session_service():
    """Mock session service for testing."""
    service = MagicMock()
    service.create_session = AsyncMock(return_value=MagicMock(
        id="test_session_123",
        state={}
    ))
    service.get_session = AsyncMock(return_value=MagicMock(
        id="test_session_123",
        state={}
    ))
    return service


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "text": "This is a mock LLM response for testing purposes.",
        "finish_reason": "STOP"
    }


@pytest.fixture
def mock_google_search_results() -> List[Dict[str, str]]:
    """Mock Google Search results for testing."""
    return [
        {
            "title": "Portable Blender Market Report 2025",
            "snippet": "The portable blender market is expected to grow...",
            "link": "https://example.com/market-report"
        },
        {
            "title": "Best Portable Blenders Review",
            "snippet": "We tested the top portable blenders...",
            "link": "https://example.com/reviews"
        }
    ]


# ============================================================================
# Helper Functions
# ============================================================================

def assert_valid_score(score: int, min_val: int = 1, max_val: int = 100):
    """Assert that a score is within valid bounds."""
    assert isinstance(score, int), f"Score must be int, got {type(score)}"
    assert min_val <= score <= max_val, f"Score {score} not in range [{min_val}, {max_val}]"


def assert_non_empty_string(value: str, field_name: str = "value"):
    """Assert that a string is non-empty."""
    assert isinstance(value, str), f"{field_name} must be string, got {type(value)}"
    assert len(value.strip()) > 0, f"{field_name} must not be empty"


def assert_positive_number(value: float, field_name: str = "value"):
    """Assert that a number is positive."""
    assert isinstance(value, (int, float)), f"{field_name} must be number, got {type(value)}"
    assert value > 0, f"{field_name} must be positive, got {value}"
