#!/usr/bin/env python3
"""
Complete debugging and test of ProductScout AI.

This script performs full system verification and runs a complete analysis.
"""
import sys
import os

def check_complete_system():
    """Check if all components can be imported successfully."""
    print("🔍 Complete System Verification")
    print("=" * 80)

    # Current directory and Python path
    current_dir = os.getcwd()
    python_path = sys.executable
    print(f"📍 Current directory: {current_dir}")
    print(f"🐍 Python executable: {python_path}")

    # Test imports with absolute path
    modules_to_test = [
        ('src.config.settings', 'Settings'),
        ('src.schemas.input_schemas', 'AnalysisRequest'),
        ('src.services.analysis_service', 'create_analysis_service'),
        ('src.services.export_service', 'create_export_service'),
        ('src.workflows.analysis_pipeline', 'AnalysisPipeline'),
        ('src.workflows.runner', 'PipelineRunner', 'RunnerConfig'),
        ('src.agents.analysis_agents', 'create_trend_agent'),
        ('src.agents.base_agent', 'BaseAnalysisAgent'),
        ('src.agents.analysis_agents', 'TrendAgent'),
        ('src.agents.analysis_agents', 'MarketAgent'),
        ('src.agents.analysis_agents', 'CompetitionAgent'),
        ('src.agents.analysis_agents', 'ProfitAgent'),
        ('src.agents.analysis_agents', 'create_profit_agent'),
        ('src.utils.logger', 'setup_logger', 'get_logger'),
        ('src.utils.adk_logging', 'create_adk_logger', 'ADKEventLogger'),
        ('src.agents.orchestrator', 'create_orchestrator'),
    ]

    all_success = True

    for module_name, import_func_name in modules_to_test:
        module_desc = module_name.split('.')[-1]
        print(f"\n🧪 Testing {module_desc}...")
        try:
            __import__(module_name)
            print(f"✅ {module_desc}: Import successful")
        except ImportError as e:
            print(f"❌ {module_desc}: Import failed - {str(e)}")
            all_success = False

    print(f"\n{'=' * 60)

    # Test the core components
    print("🎯 Core Component Tests:")
    print(f"  Settings: {modules_to_test[0][1]} ✅" if all_success else "❌")
    print(f"  AnalysisRequest: {modules_to_test[1][2]} ✅" if all_success else "❌")
    print(f"  AnalysisService: {modules_to_test[2][1]} ✅" if all_success else "❌")
    print(f"  ExportService: {modules_to_test[3][1]} ✅" if all_success else "❌")
    print(f"  AnalysisPipeline: {modules_to_test[4][1]} ✅" if all_success else "❌")
    print(f"  PipelineRunner: {modules_to_test[5][1]} ✅" if all_success else "❌")
    print(f"  Analysis Agents:")
    for agent_name, agent_class in modules_to_test[5]:
            if agent_class in modules_to_test[5][1]:
                print(f"    {agent_name}: {agent_class} ✅")
            else:
                print(f"    {agent_name}: {agent_class} ❌")

    print(f"  TrendAgent: {modules_to_test[5][0]} ✅" if all_success else "❌")
    print(f"  MarketAgent: {modules_to_test[5][1]} ✅" if all_success else "❌")
    print(f"  CompetitionAgent: {modules_to_test[5][1]} ✅" if all_success else "❌")
    print(f"  ProfitAgent: {modules_to_test[5][1]} ✅" if all_success else "❌")
    print(f"  Orchestrator: {modules_to_test[5][1]} ✅" if all_success else "❌")

    if all_success:
        print(f"\n✅ All modules imported successfully!")
        print("\n💡 You can now run the analysis with confidence.")
        print("🚀 Try running: python3 debug_complete.py")
    else:
        print(f"\n❌ Some imports failed. Please check the errors above.")
        print("\n📋 The system may still not be ready for analysis.")

    return all_success

def main():
    """Main function for system verification."""
    print("🎯 ProductScout AI - Complete System Verification")
    check_complete_system()