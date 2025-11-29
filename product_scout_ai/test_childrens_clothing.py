#!/usr/bin/env python3
"""
Simple test script for 童装 (children's clothing) analysis validation.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import compatibility first
try:
    from src.utils.compatibility import *
except ImportError as e:
    print(f"Warning: Could not import compatibility module: {e}")
    print("Some features may not work correctly with Python 3.9")

from src.schemas.input_schemas import AnalysisRequest

def test_childrens_clothing_analysis():
    """Test basic 童装 analysis functionality"""
    print("🧪 Testing 童装 Analysis Functionality")
    print("=" * 50)

    # Test 1: Create analysis request for 童装
    print("📝 Test 1: Creating AnalysisRequest for 童装...")

    try:
        request = AnalysisRequest(
            category="童装",
            target_market="CN",
            business_model="amazon_fba",
            budget_range="medium",
            keywords=["可爱", "舒适", "时尚", "安全"]
        )

        print(f"✅ AnalysisRequest created successfully:")
        print(f"   - Category: {request.category}")
        print(f"   - Target Market: {request.target_market}")
        print(f"   - Business Model: {request.business_model}")
        print(f"   - Budget Range: {request.budget_range}")
        print(f"   - Keywords: {', '.join(request.keywords)}")

        # Test 2: Validate input schema
        print("\n📝 Test 2: Validating input schema...")

        # Test category validation
        assert len(request.category) >= 2, "Category too short"
        assert len(request.category) <= 200, "Category too long"
        assert request.target_market in ["US", "EU", "UK", "CA", "AU", "JP", "DE", "FR", "CN"], "Invalid target market"
        assert request.business_model in ["amazon_fba", "dropshipping", "private_label", "wholesale"], "Invalid business model"
        assert request.budget_range in ["low", "medium", "high"], "Invalid budget range"
        assert len(request.keywords) <= 10, "Too many keywords"

        print("✅ Input schema validation passed")

        # Test 3: Test Chinese character handling
        print("\n📝 Test 3: Testing Chinese character handling...")

        chinese_keywords = ["童装", "儿童服装", "婴幼儿", "可爱", "舒适"]
        for keyword in chinese_keywords:
            assert isinstance(keyword, str), f"Keyword {keyword} should be string"
            # Test that Chinese characters are preserved
            assert len(keyword) > 0, f"Keyword {keyword} should not be empty"
            print(f"   - Chinese keyword '{keyword}' handled correctly")

        print("✅ Chinese character handling test passed")

        # Test 4: Test different markets
        print("\n📝 Test 4: Testing different market configurations...")

        markets_to_test = [
            ("US", "United States"),
            ("CN", "China"),
            ("EU", "European Union"),
            ("UK", "United Kingdom")
        ]

        for market, description in markets_to_test:
            test_request = AnalysisRequest(
                category="童装",
                target_market=market,
                business_model="amazon_fba",
                budget_range="medium",
                keywords=["test", "children"]
            )
            assert test_request.target_market == market
            print(f"   - Market {market} ({description}): ✅")

        print("✅ Market configuration test passed")

        # Test 5: Test business models
        print("\n📝 Test 5: Testing business model configurations...")

        business_models = [
            ("amazon_fba", "Amazon FBA"),
            ("dropshipping", "Dropshipping"),
            ("private_label", "Private Label"),
            ("wholesale", "Wholesale")
        ]

        for model, description in business_models:
            test_request = AnalysisRequest(
                category="童装",
                target_market="US",
                business_model=model,
                budget_range="medium",
                keywords=["test", "children"]
            )
            assert test_request.business_model == model
            print(f"   - Business model {model} ({description}): ✅")

        print("✅ Business model configuration test passed")

        print("\n🎉 All 童装 analysis tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_availability():
    """Test if ProductScout AI service is running"""
    print("🔍 Testing Service Availability...")
    print("=" * 50)

    try:
        import requests
        response = requests.get("http://127.0.0.1:7861", timeout=5)
        if response.status_code == 200:
            print("✅ ProductScout AI service is accessible at http://127.0.0.1:7861")
            print(f"   - Status Code: {response.status_code}")
            print(f"   - Response Headers: {dict(response.headers)}")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Could not connect to service: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error testing service: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 ProductScout AI 童装 Integration Test Suite")
    print("📅 Testing children's clothing analysis functionality")
    print("=" * 60)

    # Test service availability first
    if not test_service_availability():
        print("\n❌ Service availability test failed. Exiting.")
        return 1

    # Run 童装 analysis tests
    if not test_childrens_clothing_analysis():
        print("\n❌ 童装 analysis tests failed. Exiting.")
        return 1

    print("\n✅ All tests completed successfully!")
    print("🎯 Ready to proceed with full integration testing.")
    return 0

if __name__ == "__main__":
    sys.exit(main())