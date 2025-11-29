#!/usr/bin/env python3
"""
端到端集成测试 - 电视产品分析
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.schemas.input_schemas import AnalysisRequest
from src.workflows.runner import PipelineRunner, RunnerConfig
from src.config.settings import Settings


async def test_tv_analysis():
    """测试电视产品分析的完整流程"""
    print("=" * 80)
    print("🚀 开始端到端集成测试 - 产品: 电视")
    print("=" * 80)

    # 1. 创建分析请求
    request = AnalysisRequest(
        category="电视",
        target_market="US",
        business_model="amazon_fba",
        budget_range="medium"
    )

    print(f"\n✅ 创建分析请求:")
    print(f"   产品类别: {request.category}")
    print(f"   目标市场: {request.target_market}")
    print(f"   商业模式: {request.business_model}")
    print(f"   预算范围: {request.budget_range}")

    # 2. 初始化设置和运行器
    print(f"\n🔧 初始化系统...")
    settings = Settings()
    config = RunnerConfig(
        app_name="product_scout_ai_test",
        max_retries=3,
        timeout_seconds=300,
        enable_streaming=True
    )

    runner = PipelineRunner(settings=settings, config=config)

    # 3. 初始化Pipeline
    print(f"📦 初始化分析管道...")
    runner.initialize_pipeline()

    # 4. 创建会话
    print(f"🔑 创建分析会话...")
    session = await runner.create_session(user_id="test_user")
    print(f"   会话ID: {session.session_id if hasattr(session, 'session_id') else 'N/A'}")

    # 5. 运行分析
    print(f"\n{'=' * 80}")
    print(f"🚀 开始执行分析...")
    print(f"{'=' * 80}\n")

    try:
        result = await runner.run_analysis(
            request=request,
            session=session
        )

        # 6. 检查结果
        print(f"\n{'=' * 80}")
        print(f"📊 分析结果:")
        print(f"{'=' * 80}")

        if result.is_ok():
            pipeline_result = result.unwrap()
            state = pipeline_result.state

            print(f"✅ 分析成功完成!")
            print(f"\n⏱️  执行时间: {pipeline_result.execution_time:.2f}秒")
            print(f"📝 当前阶段: {state.current_phase}")

            # 显示各阶段执行时间
            if pipeline_result.phase_times:
                print(f"\n⏲️  各阶段执行时间:")
                for phase, duration in pipeline_result.phase_times.items():
                    print(f"   - {phase}: {duration:.2f}秒")

            # 显示分析结果
            print(f"\n📈 分析结果摘要:")

            if state.trend_analysis:
                print(f"   ✓ 趋势分析: 已完成")
                if hasattr(state.trend_analysis, 'trend_score'):
                    print(f"     分数: {state.trend_analysis.trend_score}/100")
            else:
                print(f"   ✗ 趋势分析: 未完成")

            if state.market_analysis:
                print(f"   ✓ 市场分析: 已完成")
                if hasattr(state.market_analysis, 'market_score'):
                    print(f"     分数: {state.market_analysis.market_score}/100")
            else:
                print(f"   ✗ 市场分析: 未完成")

            if state.competition_analysis:
                print(f"   ✓ 竞争分析: 已完成")
                if hasattr(state.competition_analysis, 'competition_score'):
                    print(f"     分数: {state.competition_analysis.competition_score}/100")
            else:
                print(f"   ✗ 竞争分析: 未完成")

            if state.profit_analysis:
                print(f"   ✓ 利润分析: 已完成")
                if hasattr(state.profit_analysis, 'profit_score'):
                    print(f"     分数: {state.profit_analysis.profit_score}/100")
            else:
                print(f"   ✗ 利润分析: 未完成")

            if hasattr(state, 'evaluation_result') and state.evaluation_result:
                print(f"   ✓ 综合评估: 已完成")
                if isinstance(state.evaluation_result, dict):
                    print(f"     机会分数: {state.evaluation_result.get('opportunity_score', 'N/A')}/100")
                    print(f"     建议: {state.evaluation_result.get('recommendation', 'N/A')}")
            else:
                print(f"   ✗ 综合评估: 未完成")

            if hasattr(state, 'report_text') and state.report_text:
                print(f"   ✓ 分析报告: 已生成")
                print(f"     报告长度: {len(state.report_text)} 字符")
            else:
                print(f"   ✗ 分析报告: 未生成")

            # 显示完整报告（如果有）
            if hasattr(state, 'report_text') and state.report_text:
                print(f"\n{'=' * 80}")
                print(f"📄 完整分析报告:")
                print(f"{'=' * 80}\n")
                print(state.report_text)

            print(f"\n{'=' * 80}")
            print(f"✅ 端到端测试成功完成!")
            print(f"{'=' * 80}")
            return True

        else:
            error_context = result.unwrap_err()
            print(f"❌ 分析失败!")
            print(f"\n错误信息:")
            print(f"   类别: {error_context.category}")
            print(f"   消息: {error_context.message}")
            print(f"   阶段: {error_context.phase}")
            if error_context.technical_detail:
                print(f"   技术细节: {error_context.technical_detail}")

            print(f"\n{'=' * 80}")
            print(f"❌ 端到端测试失败!")
            print(f"{'=' * 80}")
            return False

    except Exception as e:
        print(f"\n❌ 测试过程中发生异常:")
        print(f"   {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

        print(f"\n{'=' * 80}")
        print(f"❌ 端到端测试异常终止!")
        print(f"{'=' * 80}")
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_tv_analysis())
    sys.exit(0 if success else 1)
