#!/usr/bin/env python3
"""
诊断agents模块导入问题
"""
import sys
import os
import traceback

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("🔍 诊断agents模块导入问题...")

def test_import_step(step_name, import_statement):
    """逐步测试导入"""
    print(f"\n--- {step_name} ---")
    try:
        exec(import_statement)
        print(f"✅ {step_name}: 成功")
        return True
    except Exception as e:
        print(f"❌ {step_name}: 失败 - {e}")
        traceback.print_exc()
        return False

# 测试各个导入步骤
tests = [
    ("导入google.adk.agents", "from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent"),
    ("导入配置模块", "from src.config.settings import Settings"),
    ("导入提示模块", "from src.config.prompts import ORCHESTRATOR_INSTRUCTION, format_prompt"),
    ("导入schemas", "from src.schemas.input_schemas import AnalysisRequest"),
    ("导入base_agent", "from src.agents.base_agent import BaseAnalysisAgent, AgentConfig"),
    ("导入analysis_agents", "from src.agents.analysis_agents import TrendAgent, MarketAgent, CompetitionAgent, ProfitAgent"),
    ("导入evaluator_agents", "from src.agents.evaluator_agents import EvaluatorAgent, ReportAgent"),
]

success_count = 0
for step_name, import_statement in tests:
    if test_import_step(step_name, import_statement):
        success_count += 1

print(f"\n📊 测试结果: {success_count}/{len(tests)} 成功")

if success_count == len(tests):
    print("\n✅ 所有导入测试通过，尝试导入orchestrator...")
    try:
        from src.agents.orchestrator import OrchestratorAgent
        print("✅ OrchestratorAgent导入成功")

        # 尝试创建一个简单的实例
        print("🧪 测试OrchestratorAgent实例化...")
        agent = OrchestratorAgent()
        print("✅ OrchestratorAgent实例化成功")

    except Exception as e:
        print(f"❌ OrchestratorAgent相关错误: {e}")
        traceback.print_exc()
else:
    print(f"\n❌ 有 {len(tests) - success_count} 个导入步骤失败")

# 检查google.adk的具体版本和可用组件
print("\n🔍 检查google.adk模块...")
try:
    import google.adk.agents
    print("✅ google.adk.agents 模块存在")

    # 列出可用的类
    available_items = [item for item in dir(google.adk.agents) if not item.startswith('_')]
    print(f"📋 可用组件: {available_items}")

    # 特别检查ParallelAgent
    if 'ParallelAgent' in available_items:
        print("✅ ParallelAgent 可用")
    else:
        print("❌ ParallelAgent 不可用")

    if 'LlmAgent' in available_items:
        print("✅ LlmAgent 可用")
    else:
        print("❌ LlmAgent 不可用")

except ImportError as e:
    print(f"❌ google.adk.agents 导入失败: {e}")