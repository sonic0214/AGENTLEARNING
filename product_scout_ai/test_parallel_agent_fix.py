#!/usr/bin/env python3
"""
测试ParallelAgent修复
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def test_parallel_agent_creation():
    """测试ParallelAgent创建是否正常"""
    print("🧪 测试ParallelAgent创建修复...")

    try:
        print("1. 测试导入...")
        from google.adk.agents import ParallelAgent
        from google.adk.agents import LlmAgent
        print("✅ 导入成功")

        print("2. 测试创建基本ParallelAgent...")
        parallel_agent = ParallelAgent(
            name="test_parallel",
            sub_agents=[],
            description="Test parallel agent"
        )
        print("✅ ParallelAgent创建成功")

        print("3. 测试create_pipeline_agents方法...")
        from src.workflows.analysis_pipeline import AnalysisPipeline
        from src.schemas.input_schemas import AnalysisRequest

        # 创建pipeline实例
        pipeline = AnalysisPipeline()

        # 创建测试请求
        test_request = AnalysisRequest(
            category="test",
            target_market="test",
            business_model="test",
            budget_range="test",
            keywords=[]
        )

        # 测试创建pipeline agents
        agents_dict = pipeline.create_pipeline_agents(test_request)
        print(f"✅ Pipeline agents创建成功: {list(agents_dict.keys())}")

        # 验证parallel_agent是否正确创建
        if 'parallel_agent' in agents_dict:
            parallel_agent = agents_dict['parallel_agent']
            print(f"✅ ParallelAgent类型: {type(parallel_agent)}")
            print(f"✅ ParallelAgent名称: {parallel_agent.name}")
            print(f"✅ Sub-agents数量: {len(parallel_agent.sub_agents) if hasattr(parallel_agent, 'sub_agents') else 'N/A'}")
        else:
            print("❌ 'parallel_agent' 不在agents_dict中")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parallel_agent_creation()
    print(f"\n📊 测试结果: {'✅ 成功' if success else '❌ 失败'}")
    sys.exit(0 if success else 1)