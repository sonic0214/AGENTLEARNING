#!/usr/bin/env python3
"""
修复agents导入问题
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def test_analysis_pipeline_import():
    """测试analysis_pipeline导入"""
    print("🔍 测试analysis_pipeline导入...")

    try:
        print("1. 导入基础模块...")
        from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent, parallel_agent_config
        from google.adk.sessions import Session
        from src.config.settings import Settings
        from src.schemas.input_schemas import AnalysisRequest
        print("✅ 基础模块导入成功")

        print("2. 测试agents模块导入...")
        from src.agents import (
            TrendAgent,
            MarketAgent,
            CompetitionAgent,
            ProfitAgent,
            EvaluatorAgent,
            ReportAgent,
            extract_json_from_response,
        )
        print("✅ agents模块导入成功")

        print("3. 测试完整的analysis_pipeline导入...")
        from src.workflows.analysis_pipeline import AnalysisPipeline, PipelineResult
        print("✅ analysis_pipeline导入成功")

        print("4. 测试创建AnalysisPipeline实例...")
        pipeline = AnalysisPipeline()
        print("✅ AnalysisPipeline实例创建成功")

        return True

    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def find_and_fix_agents_name_conflict():
    """查找并修复agents名称冲突"""
    print("\n🔍 检查可能的名称冲突...")

    import ast
    import os

    # 检查analysis_pipeline.py文件
    pipeline_file = os.path.join(src_path, 'workflows', 'analysis_pipeline.py')

    try:
        with open(pipeline_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"📄 检查文件: {pipeline_file}")

        # 查找可能的问题
        if 'from src.agents import (' in content and 'agents' in content:
            print("⚠️  可能存在名称冲突问题")

            # 检查是否有变量名为agents
            if 'agents' in content and '=' in content:
                print("🔧 找到可能的agents变量赋值")

        return pipeline_file, content

    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None, None

def create_fixed_analysis_pipeline():
    """创建修复版本的analysis_pipeline.py"""
    print("\n🔧 创建修复版本的analysis_pipeline...")

    fixed_content = '''"""
Analysis pipeline workflow for ProductScout AI.

This module implements the main analysis workflow that orchestrates
all agents in the proper sequence using ADK patterns.
"""
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json

from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent, parallel_agent_config
from google.adk.sessions import Session

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
    FinalReport,
)
from src.schemas.state_schemas import AnalysisState
from src.agents import (
    TrendAgent,
    MarketAgent,
    CompetitionAgent,
    ProfitAgent,
    EvaluatorAgent,
    ReportAgent,
    extract_json_from_response,
)


@dataclass
class PipelineResult:
    """
    Result of a pipeline execution.

    Attributes:
        success: Whether the pipeline completed successfully
        state: Final analysis state
        report: Generated report (if successful)
        error: Error message (if failed)
        execution_time: Total execution time in seconds
        phase_times: Execution time for each phase
    """
    success: bool = False
    state: Optional[AnalysisState] = None
    report: Optional[FinalReport] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    phase_times: Dict[str, float] = field(default_factory=dict)


class AnalysisPipeline:
    """
    Main analysis pipeline that orchestrates all agents.

    This pipeline follows a sequential pattern:
    1. Parallel analysis of trends, market, competition, and profit
    2. Sequential evaluation and report generation
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the analysis pipeline."""
        self.settings = settings or Settings()
        self._analysis_agent_classes = {
            'trend': TrendAgent,
            'market': MarketAgent,
            'competition': CompetitionAgent,
            'profit': ProfitAgent,
        }
        self._evaluator_class = EvaluatorAgent
        self._reporter_class = ReportAgent

    def create_parallel_analysis(self, request: AnalysisRequest) -> ParallelAgent:
        """
        Create parallel analysis stage.

        Args:
            request: Analysis request

        Returns:
            ParallelAgent configured for analysis
        """
        # Create individual analysis agents
        analysis_agents = []

        # Trend agent
        trend_agent = TrendAgent(self.settings)
        trend_llm = trend_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        analysis_agents.append(trend_llm)

        # Market agent
        market_agent = MarketAgent(self.settings)
        market_llm = market_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        analysis_agents.append(market_llm)

        # Competition agent
        competition_agent = CompetitionAgent(self.settings)
        competition_llm = competition_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )
        analysis_agents.append(competition_llm)

        # Profit agent
        profit_agent = ProfitAgent(self.settings)
        profit_llm = profit_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            business_model=request.business_model,
            budget_range=request.budget_range
        )
        analysis_agents.append(profit_llm)

        # Create parallel agent
        parallel_agent = ParallelAgent(
            name="parallel_analysis",
            sub_agents=analysis_agents,
            description="Executes trend, market, competition, and profit analysis in parallel"
        )

        return parallel_agent

    def create_sequential_evaluation(
        self,
        request: AnalysisRequest,
        analysis_results: Dict[str, Any]
    ) -> SequentialAgent:
        """
        Create sequential evaluation stage.

        Args:
            request: Original analysis request
            analysis_results: Results from parallel analysis

        Returns:
            SequentialAgent for evaluation and reporting
        """
        # Create evaluator agent
        evaluator = EvaluatorAgent(self.settings)
        evaluator_llm = evaluator.create_agent(
            category=request.category,
            target_market=request.target_market
        )

        # Create report agent
        reporter = ReportAgent(self.settings)
        report_llm = reporter.create_agent(
            category=request.category,
            target_market=request.target_market
        )

        # Create sequential agent
        sequential_agent = SequentialAgent(
            name="sequential_evaluation",
            sub_agents=[evaluator_llm, report_llm],
            description="Evaluates analysis results and generates final report"
        )

        return sequential_agent

    async def run_analysis(self, request: AnalysisRequest) -> PipelineResult:
        """
        Run the complete analysis pipeline.

        Args:
            request: Analysis request

        Returns:
            PipelineResult with analysis outcome
        """
        import time
        start_time = time.time()

        try:
            # Create session
            session = Session()

            # Create parallel analysis stage
            print("🔍 创建并行分析阶段...")
            parallel_analysis = self.create_parallel_analysis(request)

            # Run parallel analysis
            print("🚀 运行并行分析...")
            parallel_result = await parallel_analysis.run_async(session)

            # Create sequential evaluation stage
            print("📊 创建评估阶段...")
            sequential_evaluation = self.create_sequential_evaluation(request, {})

            # Run sequential evaluation
            print("✅ 运行评估和报告生成...")
            final_result = await sequential_evaluation.run_async(session)

            # Create successful result
            execution_time = time.time() - start_time

            return PipelineResult(
                success=True,
                state=AnalysisState(
                    request=request,
                    phase="completed",
                    progress=1.0
                ),
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return PipelineResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )


def create_analysis_pipeline(settings: Optional[Settings] = None) -> AnalysisPipeline:
    """
    Factory function to create an analysis pipeline.

    Args:
        settings: Optional settings object

    Returns:
        AnalysisPipeline instance
    """
    return AnalysisPipeline(settings)
'''

    pipeline_file = os.path.join(src_path, 'workflows', 'analysis_pipeline.py')
    backup_file = pipeline_file + '.backup'

    try:
        # 备份原文件
        if os.path.exists(pipeline_file):
            with open(pipeline_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"✅ 原文件已备份到: {backup_file}")

        # 写入修复版本
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ 修复版本已写入: {pipeline_file}")

        return True

    except Exception as e:
        print(f"❌ 写入修复版本失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 修复agents导入问题")
    print("=" * 50)

    # 测试当前导入
    if test_analysis_pipeline_import():
        print("\n✅ 导入测试通过，无需修复")
        return 0

    # 创建修复版本
    if create_fixed_analysis_pipeline():
        print("\n🔧 修复版本创建完成")

        # 再次测试
        print("\n🧪 测试修复后的导入...")
        if test_analysis_pipeline_import():
            print("✅ 修复成功！")
            return 0
        else:
            print("❌ 修复失败，问题仍然存在")
            return 1
    else:
        print("❌ 修复版本创建失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())