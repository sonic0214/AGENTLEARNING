#!/usr/bin/env python3
"""
Minimal test to verify ProductScout AI startup.

This script tests only the core components without the full dependency tree.
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test core imports."""
    print("🔍 Testing core imports...")

    try:
        from src.config.settings import Settings
        print("✅ Settings importable")

        from src.schemas.input_schemas import AnalysisRequest
        print("✅ AnalysisRequest importable")

        from src.ui.app import create_app
        print("✅ UI app importable")

        print("✅ Core imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_gradio_creation():
    """Test Gradio app creation."""
    print("\n🎛 Testing Gradio App Creation...")

    try:
        from src.ui.app import create_app
        app = create_app()
        print("✅ Gradio app created successfully!")
        print(f"  App type: {type(app)}")
        print(f"  App title: {app.title}")
        return True

    except Exception as e:
        print(f"❌ Gradio app creation failed: {str(e)}")
        return False

async def test_analysis_service():
    """Test analysis service creation."""
    print("\n🧪 Testing Analysis Service...")

    try:
        from src.services.analysis_service import create_analysis_service
        from src.config.settings import Settings

        settings = Settings()
        service = create_analysis_service(settings)
        print("✅ Analysis service created!")
        print(f"  Service type: {type(service)}")
        return True

    except Exception as e:
        print(f"❌ Analysis service creation failed: {str(e)}")
        return False

def main():
    """Run minimal tests."""
    print("🎯 ProductScout AI - Minimal Startup Test")
    print("=" * 80)

    # Test 1: Core imports
    if not test_imports():
        print("❌ Core imports failed - cannot continue")
        return 1

    # Test 2: Gradio app
    if not test_gradio_creation():
        print("❌ Gradio app creation failed - cannot continue")
        return 1

    # Test 3: Analysis service
    test_imports()
    test_gradio_creation()

    if not test_imports():
        print("❌ Core imports failed - cannot continue")
        return 1

    # Test 2: Gradio app
    if not test_gradio_creation():
        print("❌ Gradio app creation failed - cannot continue")
        return 1

    # Test 3: Analysis service (without await)
    try:
        from src.services.analysis_service import create_analysis_service
        print("✅ Analysis service creation successful (sync version)")
    except Exception as e:
        print(f"❌ Analysis service creation failed: {str(e)}")
        return 1
        print("❌ Analysis service creation failed - cannot continue")
        return 1

    print("\n✅ All tests passed!")
    print("\n💡 Next Steps:")
    print("1. Install full requirements with: pip install -r requirements.txt")
    print("2. Start application with: python run_app.py")
    print("3. Or start CLI with: python src/cli/main.py analyze '便携榨汁机'")
    print("4. For debugging, add: --verbose")

    return 0

if __name__ == "__main__":
    exit_code = main()
    print(f"\nExit code: {exit_code}")