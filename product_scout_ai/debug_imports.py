#!/usr/bin/env python3
"""
Debug script to check import paths and modules.

This script will help identify why the imports are failing
when running the UI application.
"""
import sys
import os
import importlib.util

def debug_imports():
    """Debug Python import paths and module availability."""
    print("🔍 Debug: Python Imports and Module Check")
    print("=" * 60)

    # Current working directory
    cwd = os.getcwd()
    print(f"📍 Current directory: {cwd}")

    # Python path
    python_path = sys.executable
    print(f"🐍 Python executable: {python_path}")

    # sys.path
    print(f"🛤 sys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

    # Check src in path
    src_in_path = any('src' in path for path in sys.path)
    print(f"📦 'src' in sys.path: {src_in_path}")

    # Check for ProductScout src specifically
    current_dir = os.path.dirname(os.path.abspath(__file__))
    expected_src = os.path.join(current_dir, 'src')
    actual_src = None

    for path in sys.path:
        if path.endswith('product_scout_ai'):
            actual_src = os.path.dirname(path)
            break

    if actual_src:
        print(f"✅ ProductScout src found at: {actual_src}")
    else:
        print(f"❌ ProductScout src not found in sys.path")

    # Test imports with current working directory
    os.chdir(current_dir)

    test_modules = [
        ('src.ui.app', 'create_app'),
        ('src.config.settings', 'Settings'),
        ('src.schemas.input_schemas', 'AnalysisRequest'),
        ('src.services.analysis_service', 'create_analysis_service'),
        ('src.services.export_service', 'create_export_service'),
        ('src.ui.tabs.analysis_tab', 'create_analysis_tab'),
        ('src.workflows.analysis_pipeline', 'AnalysisPipeline'),
        ('src.workflows.runner', 'PipelineRunner'),
        ('src.utils.adk_logging', 'create_adk_logger'),
        ('src.utils.logger', 'setup_logger'),
        ('src.agents.analysis_agents', 'create_trend_agent'),
    ]

    print(f"\n🧪 Testing imports from current directory: {current_dir}")

    for module_name, import_func in test_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: Import successful")
        except ImportError as e:
            print(f"❌ {module_name}: Import failed - {str(e)}")
        except Exception as e:
            print(f"❌ {module_name}: Unexpected error - {str(e)}")

    # Try changing to src directory
    original_cwd = os.getcwd()
    try:
        os.chdir(current_dir)
        print(f"🔄 Changed to: {current_dir}")

        # Retry imports
        print(f"\n🔄 Retrying imports...")
        all_success = True
        for module_name, import_func in test_modules:
            try:
                __import__(module_name)
                print(f"✅ {module_name}: Import successful (from src)")
            except ImportError as e:
                print(f"❌ {module_name}: Import failed - {str(e)}")
                all_success = False
            except Exception as e:
                print(f"❌ {module_name}: Unexpected error - {str(e)}")
                all_success = False

        if all_success:
            print(f"✅ All imports successful from src directory!")
        else:
            print(f"⚠️ Some imports failed even from src directory")

    finally:
        os.chdir(original_cwd)

    print("\n" + "=" * 60)
    print("📋 Recommendations:")
    if all_success:
        print("✅ All imports working correctly from src directory")
        print("🚀 You can now run: python3 run_ui.py")
    else:
        print("❌ There are still import issues")
        print("💡 Try running from the correct directory:")
        print(f"   cd {current_dir}")
        print(f"   python3 run_ui.py")

    return all_success

if __name__ == "__main__":
    debug_imports()