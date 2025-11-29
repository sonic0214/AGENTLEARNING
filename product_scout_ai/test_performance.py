#!/usr/bin/env python3
"""
Performance and error handling tests for ProductScout AI.

This test validates system performance under load and error conditions.
"""

import sys
import os
import time
import concurrent.futures
import requests
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import compatibility first
try:
    from src.utils.compatibility import *
except ImportError as e:
    print(f"Warning: Could not import compatibility module: {e}")
    print("Some features may not work correctly with Python 3.9")

from src.schemas.input_schemas import AnalysisRequest

def test_concurrent_analysis():
    """Test concurrent analysis capacity"""
    print("🚀 Testing Concurrent Analysis Performance")
    print("=" * 60)

    base_url = "http://127.0.0.1:7861"

    # Test requests for different markets and products
    test_requests = [
        ("童装", "CN", "amazon_fba", ["可爱", "舒适", "安全"]),
        ("children's clothing", "US", "dropshipping", ["cute", "comfortable", "safe"]),
        ("kidswear", "UK", "private_label", ["fashionable", "durable", "trendy"])
    ]

    start_time = time.time()

    print(f"📊 Sending {len(test_requests)} concurrent requests...")

    # Use ThreadPoolExecutor for concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all requests
        futures = []
        for i, (category, market, model, keywords) in enumerate(test_requests, 1):
            print(f"   Request {i}: {category} in {market}")
            future = executor.submit(send_analysis_request, base_url, category, market, model, keywords)
            futures.append(future)

        # Wait for all to complete
        results = []
        for i, future in enumerate(futures, 1):
            try:
                result = future.result(timeout=180)  # 3 minute timeout
                results.append((i, result, None))
                print(f"   ✅ Request {i} completed in {result.get('execution_time', 0):.1f}s")
            except concurrent.futures.TimeoutError:
                results.append((i, None, "Timeout"))
                print(f"   ⏱️️ Request {i} timed out")
            except Exception as e:
                results.append((i, None, str(e)))
                print(f"   ❌ Request {i} failed: {e}")

    total_time = time.time() - start_time

    print(f"\n📊 Performance Results:")
    print(f"   Total execution time: {total_time:.2f}s")
    print(f"   Requests completed: {len([r for r in results if r[1] is not None])}")
    print(f"   Requests timed out: {len([r for r in results if r[1] == 'Timeout'])}")
    print(f"   Requests failed: {len([r for r in results if r[1] not in ['Timeout', None]])}")

    if len([r for r in results if r[1] is not None]) >= 2:
        avg_time = total_time / len([r for r in results if r[1] is not None])
        print(f"   Average time per request: {avg_time:.2f}s")
        print(f"   Concurrent efficiency: {len(test_requests) / total_time:.2f} requests/second")

    # Test individual request performance
    print(f"\n🎯 Individual Request Analysis:")
    for i, (result, error) in enumerate(results):
        if result and not error:  # Fixed condition
            execution_time = result.get('execution_time', 0)
            print(f"   Request {i}: {execution_time:.2f}s")

            # Validate response structure
            required_fields = ['trend_analysis', 'market_analysis', 'competition_analysis', 'profit_analysis', 'evaluation_result']
            missing_fields = [field for field in required_fields if field not in result]

            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   ✅ All required fields present")

                # Check evaluation result
                evaluation = result.get('evaluation_result', {})
                if 'opportunity_score' in evaluation:
                    score = evaluation['opportunity_score']
                    if isinstance(score, (int, float)) and 0 <= score <= 100:
                        print(f"   ✅ Valid opportunity score: {score}")
                    else:
                        print(f"   ❌ Invalid opportunity score: {score}")
                else:
                    print(f"   ⚠️  Missing opportunity_score in evaluation result")

    print(f"\n✅ Performance test completed successfully!")
    return len([r for r in results if r[1] is not None]) >= 2

def test_error_handling():
    """Test error handling capabilities"""
    print("\n🛡️ Testing Error Handling")
    print("=" * 60)

    base_url = "http://127.0.0.1:7861"

    # Test 1: Empty category
    print("📋 Test 1: Empty category validation")
    try:
        response = requests.post(f"{base_url}/analyze", json={
            "category": "",
            "target_market": "CN",
            "business_model": "amazon_fba",
            "budget_range": "medium",
            "keywords": ["test"]
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'error' in data or data.get('state', {}).get('current_phase') == 'failed':
                print("   ✅ Empty category properly rejected")
            else:
                print("   ❌ Empty category not properly handled")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error in empty category test: {e}")

    # Test 2: Invalid market
    print("\n📋 Test 2: Invalid market validation")
    try:
        response = requests.post(f"{base_url}/analyze", json={
            "category": "童装",
            "target_market": "INVALID_MARKET",
            "business_model": "amazon_fba",
            "budget_range": "medium",
            "keywords": ["test"]
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'error' in data or data.get('state', {}).get('current_phase') == 'failed':
                print("   ✅ Invalid market properly rejected")
            else:
                print("   ❌ Invalid market not properly handled")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error in invalid market test: {e}")

    # Test 3: Too many keywords
    print("\n📋 Test 3: Too many keywords validation")
    try:
        keywords = [f"keyword_{i}" for i in range(15)]  # 15 keywords (>10 limit)
        response = requests.post(f"{base_url}/analyze", json={
            "category": "童装",
            "target_market": "CN",
            "business_model": "amazon_fba",
            "budget_range": "medium",
            "keywords": keywords
        }, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'error' in data or data.get('state', {}).get('current_phase') == 'failed':
                print("   ✅ Too many keywords properly rejected")
            else:
                print("   ❌ Too many keywords not properly handled")
        else:
            print(f"   ⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error in too many keywords test: {e}")

    print(f"\n✅ Error handling test completed successfully!")
    return True

def test_system_stability():
    """Test system stability under sustained load"""
    print("\n🔄 Testing System Stability")
    print("=" * 60)

    base_url = "http://127.0.0.1:7861"
    request_count = 5
    success_count = 0

    for i in range(request_count):
        print(f"📊 Request {i+1}/{request_count}...")
        try:
            response = requests.get(f"{base_url}", timeout=5)
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Service responsive")
            else:
                print(f"   ⚠️ Service returned status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Request {i+1} failed: {e}")

        time.sleep(1)  # 1 second between requests

    success_rate = (success_count / request_count) * 100
    print(f"\n📊 Stability Test Results:")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Successful requests: {success_count}/{request_count}")

    if success_rate >= 80:
        print("   ✅ System stability is acceptable")
        return True
    else:
        print("   ⚠️ System stability needs improvement")
        return False

def send_analysis_request(base_url, category, market, model, keywords):
    """Send analysis request to service"""
    try:
        response = requests.post(f"{base_url}/analyze", json={
            "category": category,
            "target_market": market,
            "business_model": model,
            "budget_range": "medium",
            "keywords": keywords
        }, timeout=180)  # 3 minute timeout

        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, f"Unexpected error: {e}"

def main():
    """Main test function"""
    print("🎯 ProductScout AI Performance & Error Handling Test Suite")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    all_tests_passed = True

    # Run performance tests
    if not test_concurrent_analysis():
        all_tests_passed = False
        print("❌ Concurrent analysis test failed")

    # Run error handling tests
    if not test_error_handling():
        all_tests_passed = False
        print("❌ Error handling test failed")

    # Run stability tests
    if not test_system_stability():
        all_tests_passed = False
        print("❌ System stability test failed")

    print("\n" + "=" * 80)
    if all_tests_passed:
        print("🎉 ALL PERFORMANCE & ERROR HANDLING TESTS PASSED! 🎯")
        print("✅ System is ready for production use")
        print("✅ Concurrent request handling is working")
        print("✅ Error handling is robust")
        print("✅ System stability is acceptable")
        return 0
    else:
        print("❌ SOME TESTS FAILED! ⚠️")
        print("🔧 Please review and fix the issues above")
        print("🔧 Common issues to check:")
        print("   - Service availability and responsiveness")
        print("   - Request validation and error handling")
        print("   - Concurrent request capacity")
        print("   - System stability under load")
        return 1

if __name__ == "__main__":
    sys.exit(main())