#!/usr/bin/env python3
"""
Simple test for persistence functionality
"""
import os

def test_persistence():
    """Test if persistence is working correctly."""
    print("🧪 Testing persistence functionality...")

    # Test 1: Check if data directory exists
    data_dir = "."
    if os.path.exists(data_dir):
        print(f"✅ Data directory exists: {data_dir}")
    else:
        print(f"❌ Data directory missing: {data_dir}")
        return False

    # Test 2: Check if history file exists after adding entry
    history_file = "analysis_history.json"
    if os.path.exists(history_file):
        print(f"✅ History file exists: {history_file}")
        file_size = os.path.getsize(history_file)
        print(f"📏 History file size: {file_size} bytes")
        return True
    else:
        print(f"❌ History file not found: {history_file}")
        return False

if __name__ == "__main__":
    success = test_persistence()
    if success:
        print("✅ Persistence test PASSED!")
    else:
        print("❌ Persistence test FAILED!")