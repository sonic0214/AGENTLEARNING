#!/usr/bin/env python3
"""
测试最终修复后的导入
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def test_all_imports():
    """测试所有关键导入"""
    print("🧪 测试修复后的所有导入...")
    print("=" * 60)

    tests = [
        # Basic ADK imports
        ("google.adk.agents基本导入", "from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent"),

        # Sessions import
        ("google.adk.sessions导入", "from google.adk.sessions import Session"),

        # Config imports
        ("配置模块导入", "from src.config.settings import Settings"),
        ("提示模块导入", "from src.config.prompts import ORCHESTRATOR_INSTRUCTION, format_prompt"),

        # Schemas imports
        ("输入schemas导入", "from src.schemas.input_schemas import AnalysisRequest"),
        ("输出schemas导入", "from src.schemas.output_schemas import TrendAnalysis, MarketAnalysis, CompetitionAnalysis, ProfitAnalysis"),
        ("状态schemas导入", "from src.schemas.state_schemas import AnalysisState"),

        # Agents imports
        ("基础agent导入", "from src.agents.base_agent import BaseAnalysisAgent, AgentConfig"),
        ("分析agents导入", "from src.agents.analysis_agents import TrendAgent, MarketAgent, CompetitionAgent, ProfitAgent"),
        ("评估agents导入", "from src.agents.evaluator_agents import EvaluatorAgent, ReportAgent"),
        ("orchestrator导入", "from src.agents.orchestrator import OrchestratorAgent"),

        # Pipeline imports
        ("analysis_pipeline导入", "from src.workflows.analysis_pipeline import AnalysisPipeline, PipelineResult"),
        ("runner导入", "from src.workflows.runner import PipelineRunner, RunnerConfig"),
    ]

    success_count = 0
    failed_tests = []

    for test_name, import_statement in tests:
        print(f"\n🔍 {test_name}")
        try:
            exec(import_statement)
            print(f"   ✅ 成功")
            success_count += 1
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            failed_tests.append((test_name, str(e)))

    print(f"\n📊 导入测试结果:")
    print(f"   成功: {success_count}/{len(tests)}")
    print(f"   失败: {len(failed_tests)}")

    if failed_tests:
        print(f"\n❌ 失败的导入:")
        for test_name, error in failed_tests:
            print(f"   - {test_name}: {error}")
        return False
    else:
        print(f"\n✅ 所有导入测试通过!")
        return True

def test_pipeline_creation():
    """测试完整的pipeline创建"""
    print(f"\n🔧 测试AnalysisPipeline创建...")

    try:
        from src.workflows.analysis_pipeline import AnalysisPipeline
        from src.schemas.input_schemas import AnalysisRequest

        # 创建pipeline实例
        pipeline = AnalysisPipeline()
        print("   ✅ AnalysisPipeline实例创建成功")

        # 创建测试请求
        test_request = AnalysisRequest(
            category="电子产品",
            target_market="国内市场",
            business_model="电商",
            budget_range="中等",
            keywords=["测试"]
        )
        print("   ✅ AnalysisRequest创建成功")

        # 测试create_pipeline_agents
        agents_dict = pipeline.create_pipeline_agents(test_request)
        print(f"   ✅ Pipeline agents创建成功: {list(agents_dict.keys())}")

        # 验证parallel_agent
        if 'parallel_agent' in agents_dict:
            parallel_agent = agents_dict['parallel_agent']
            print(f"   ✅ ParallelAgent类型: {type(parallel_agent)}")
            print(f"   ✅ ParallelAgent名称: {parallel_agent.name}")
            return True
        else:
            print("   ❌ parallel_agent不在agents_dict中")
            return False

    except Exception as e:
        print(f"   ❌ Pipeline创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 ProductScout AI 最终导入测试")
    print("=" * 80)

    # 测试所有导入
    imports_success = test_all_imports()

    if imports_success:
        # 测试pipeline创建
        pipeline_success = test_pipeline_creation()

        if pipeline_success:
            print(f"\n🎉 所有测试通过! 应用应该可以正常启动了")
            return 0
        else:
            print(f"\n❌ Pipeline创建测试失败")
            return 1
    else:
        print(f"\n❌ 导入测试失败，无法继续")
        return 1

if __name__ == "__main__":
    sys.exit(main())