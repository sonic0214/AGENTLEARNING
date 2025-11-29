#!/usr/bin/env python3
"""
Integration test to validate ADK agent execution and result parsing.

This test verifies:
1. ADK Runner execution with parallel agents
2. Agent creation and configuration
3. Event generation and collection
4. Result extraction and parsing
5. Identify the root cause of empty results
"""
import asyncio
import sys
import os
import json
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.workflows.runner import create_runner
from src.workflows.analysis_pipeline import create_pipeline
from src.schemas.input_schemas import AnalysisRequest
from src.utils.logger import setup_logger


class ADKExecutionValidator:
    """Validator for ADK execution pipeline."""

    def __init__(self):
        self.logger = setup_logger("adk_validator", level=logging.DEBUG)
        self.test_results = {
            "pipeline_creation": False,
            "agent_creation": False,
            "parallel_agent_creation": False,
            "runner_creation": False,
            "session_creation": False,
            "execution_events": False,
            "result_extraction": False,
            "state_parsing": False,
            "issues_found": []
        }

    async def validate_pipeline_creation(self):
        """Validate AnalysisPipeline creation."""
        self.logger.info("🔧 Testing pipeline creation...")

        try:
            # Test pipeline factory
            pipeline = create_pipeline()
            self.logger.info(f"✅ Pipeline created: {type(pipeline).__name__}")

            # Test pipeline methods
            request = AnalysisRequest(
                category="便携式榨汁机",
                target_market="US",
                business_model="amazon_fba",
                budget_range="medium"
            )

            agents = pipeline.create_pipeline_agents(request)
            self.logger.info(f"✅ Pipeline agents created: {list(agents.keys())}")

            # Verify all agents are created
            expected_agents = ["parallel_agent", "trend_agent", "market_agent", "competition_agent", "profit_agent"]
            for agent_name in expected_agents:
                if agent_name in agents:
                    self.logger.info(f"✅ {agent_name}: {type(agents[agent_name]).__name__}")
                    self.test_results["agent_creation"] = True
                else:
                    self.logger.error(f"❌ Missing agent: {agent_name}")
                    self.test_results["issues_found"].append(f"Missing agent: {agent_name}")

            # Verify parallel agent
            parallel_agent = agents.get("parallel_agent")
            if parallel_agent:
                self.logger.info(f"✅ Parallel agent: {type(parallel_agent).__name__}")
                self.test_results["parallel_agent_creation"] = True
                self.test_results["pipeline_creation"] = True

                # Check sub_agents
                if hasattr(parallel_agent, 'sub_agents'):
                    self.logger.info(f"✅ Sub-agents: {len(parallel_agent.sub_agents)}")
                else:
                    self.logger.warning("⚠️  Parallel agent has no sub_agents attribute")
            else:
                self.logger.error("❌ No parallel agent created")
                self.test_results["issues_found"].append("No parallel agent created")

        except Exception as e:
            self.logger.error(f"❌ Pipeline creation failed: {str(e)}", exc_info=True)
            self.test_results["issues_found"].append(f"Pipeline creation error: {str(e)}")

    async def validate_runner_creation(self):
        """Validate PipelineRunner creation."""
        self.logger.info("🔧 Testing runner creation...")

        try:
            runner = create_runner()
            self.logger.info(f"✅ Runner created: {type(runner).__name__}")
            self.test_results["runner_creation"] = True

            # Test session creation
            session = await runner.create_session()
            self.logger.info(f"✅ Session created: {type(session).__name__}")
            if session:
                self.test_results["session_creation"] = True
            else:
                self.logger.error("❌ Session creation returned None")
                self.test_results["issues_found"].append("Session creation returned None")

        except Exception as e:
            self.logger.error(f"❌ Runner creation failed: {str(e)}", exc_info=True)
            self.test_results["issues_found"].append(f"Runner creation error: {str(e)}")

    async def validate_adk_execution(self):
        """Validate actual ADK execution with detailed logging."""
        self.logger.info("🔧 Testing ADK execution...")

        try:
            runner = create_runner()
            request = AnalysisRequest(
                category="便携式榨汁机",
                target_market="US",
                business_model="amazon_fba",
                budget_range="medium"
            )

            # Patch ADK Runner to capture calls
            with patch('src.workflows.runner.Runner') as MockRunner:
                # Create mock runner that simulates events
                mock_runner_instance = MagicMock()
                mock_runner_instance.run.return_value = self._generate_mock_events()
                MockRunner.return_value = mock_runner_instance

                # Execute analysis
                result = await runner.run_analysis(request)

                # Validate result
                self.logger.info(f"📊 Result type: {type(result)}")
                self.logger.info(f"📊 Result success: {result.success}")
                self.logger.info(f"📊 Result state: {type(result.state)}")

                if result.success:
                    self.test_results["execution_events"] = True
                    self.logger.info("✅ ADK execution completed successfully")

                    # Check if state has analysis results
                    self._validate_analysis_state(result.state)
                else:
                    self.logger.error(f"❌ ADK execution failed: {result.error}")
                    self.test_results["issues_found"].append(f"Execution failed: {result.error}")

        except Exception as e:
            self.logger.error(f"❌ ADK execution failed: {str(e)}", exc_info=True)
            self.test_results["issues_found"].append(f"ADK execution error: {str(e)}")

    def _generate_mock_events(self):
        """Generate mock ADK events for testing."""
        from google.adk.runners import Event

        events = []

        # Mock trend agent events
        trend_search_call = Event.model_validate({
            "function_calls": [
                {
                    "name": "google_search",
                    "args": {"query": "便携式榨汁机 市场趋势"}
                }
            ]
        })
        events.append(trend_search_call)

        trend_search_response = Event.model_validate({
            "function_responses": [
                {
                    "name": "google_search",
                    "response": {
                        "results": [
                            {"title": "2024便携式榨汁机市场趋势", "snippet": "搜索量上升35%"},
                            {"title": "便携式榨汁机竞争分析", "snippet": "主要品牌5个"}
                        ]
                    }
                }
            ]
        })
        events.append(trend_search_response)

        trend_response = Event.model_validate({
            "content": {
                "parts": [
                    {
                        "text": json.dumps({
                            "trend_score": 85,
                            "trend_direction": "rising",
                            "seasonality": {
                                "peak_months": [5, 6, 7],
                                "low_months": [11, 12],
                                "seasonal_impact": "high"
                            },
                            "related_queries": [
                                {"query": "便携果汁机", "trend": "rising"},
                                {"query": "充电榨汁机", "trend": "rising"}
                            ],
                            "analysis_summary": "便携式榨汁机市场呈现强劲上升趋势"
                        }, ensure_ascii=False)
                    }
                ]
            ]
        })
        events.append(trend_response)

        # Mock market agent events
        market_search_call = Event.model_validate({
            "function_calls": [
                {
                    "name": "google_search",
                    "args": {"query": "便携式榨汁机 市场规模 客户细分"}
                }
            ]
        })
        events.append(market_search_call)

        market_response = Event.model_validate({
            "content": {
                "parts": [
                    {
                        "text": json.dumps({
                            "market_score": 78,
                            "market_size": {
                                "tam": 5000000000,
                                "sam": 1500000000,
                                "som": 300000000,
                                "currency": "USD"
                            },
                            "growth_rate": 0.12,
                            "customer_segments": [
                                {"name": "健身爱好者", "percentage": 45},
                                {"name": "健康生活方式", "percentage": 35},
                                {"name": "忙碌专业人士", "percentage": 20}
                            ],
                            "maturity_level": "growing"
                        }, ensure_ascii=False)
                    }
                ]
            ]
        })
        events.append(market_response)

        # Mock competition and profit agent events...
        # (Similar structure)

        # Final response
        final_event = Event.model_validate({
            "is_final_response": True
        })
        events.append(final_event)

        self.logger.info(f"📝 Generated {len(events)} mock events")
        return events

    def _validate_analysis_state(self, state):
        """Validate that analysis results are properly stored in state."""
        self.logger.info("🔍 Validating analysis state...")

        issues = []

        # Check trend analysis
        if not state.trend_analysis:
            issues.append("Trend analysis not stored in state")
        else:
            self.logger.info(f"✅ Trend analysis: {type(state.trend_analysis)}")

        # Check market analysis
        if not state.market_analysis:
            issues.append("Market analysis not stored in state")
        else:
            self.logger.info(f"✅ Market analysis: {type(state.market_analysis)}")

        # Check competition analysis
        if not state.competition_analysis:
            issues.append("Competition analysis not stored in state")
        else:
            self.logger.info(f"✅ Competition analysis: {type(state.competition_analysis)}")

        # Check profit analysis
        if not state.profit_analysis:
            issues.append("Profit analysis not stored in state")
        else:
            self.logger.info(f"✅ Profit analysis: {type(state.profit_analysis)}")

        if issues:
            for issue in issues:
                self.logger.error(f"❌ State issue: {issue}")
                self.test_results["issues_found"].extend(issues)
            self.test_results["state_parsing"] = False
        else:
            self.logger.info("✅ All analysis results properly stored")
            self.test_results["state_parsing"] = True

    async def validate_result_extraction(self):
        """Validate result extraction from ADK events."""
        self.logger.info("🔧 Testing result extraction...")

        try:
            # Test the current implementation
            from src.utils.adk_logging import ADKEventLogger, create_adk_logger
            from google.adk.runners import Event

            logger = setup_logger("result_test", level=logging.DEBUG)
            adk_logger = ADKEventLogger(logger, debug_mode=True)

            # Create mock events with actual analysis data
            mock_events = self._generate_mock_events()

            for i, event in enumerate(mock_events):
                adk_logger.log_event(event, i + 1)

            # Test extraction
            agent_outputs = adk_logger.extract_agent_outputs()

            if agent_outputs:
                self.logger.info("✅ Agent outputs extracted:")
                for agent_name, output in agent_outputs.items():
                    self.logger.info(f"  {agent_name}: {len(output)} chars")

                self.test_results["result_extraction"] = True
            else:
                self.logger.error("❌ No agent outputs extracted")
                self.test_results["issues_found"].append("No agent outputs extracted")
                self.test_results["result_extraction"] = False

            # Show summary
            adk_logger.log_summary()

        except Exception as e:
            self.logger.error(f"❌ Result extraction failed: {str(e)}", exc_info=True)
            self.test_results["issues_found"].append(f"Result extraction error: {str(e)}")

    def generate_test_report(self):
        """Generate comprehensive test report."""
        self.logger.info("\n" + "="*80)
        self.logger.info("📋 ADK EXECUTION VALIDATION REPORT")
        self.logger.info("="*80)

        total_tests = len([k for k, v in self.test_results.items() if isinstance(v, bool)])
        passed_tests = len([k for k, v in self.test_results.items() if isinstance(v, bool) and v])

        self.logger.info(f"📊 Tests Summary: {passed_tests}/{total_tests} passed")

        # Test results
        for test_name, result in self.test_results.items():
            if isinstance(result, bool):
                status = "✅ PASS" if result else "❌ FAIL"
                self.logger.info(f"{status}: {test_name}")

        # Issues
        if self.test_results["issues_found"]:
            self.logger.info("\n❌ Issues Found:")
            for i, issue in enumerate(self.test_results["issues_found"], 1):
                self.logger.info(f"  {i}. {issue}")

        # Recommendations
        self._generate_recommendations()

        self.logger.info("="*80)

    def _generate_recommendations(self):
        """Generate recommendations based on test results."""
        self.logger.info("\n💡 Recommendations:")

        if not self.test_results["pipeline_creation"]:
            self.logger.info("  🔧 Fix pipeline creation and agent initialization")

        if not self.test_results["agent_creation"]:
            self.logger.info("  🔧 Ensure all 4 agents are properly created")

        if not self.test_results["parallel_agent_creation"]:
            self.logger.info("  🔧 Verify ParallelAgent sub_agents configuration")

        if not self.test_results["execution_events"]:
            self.logger.info("  🔧 Check ADK Runner execution and event generation")

        if not self.test_results["state_parsing"]:
            self.logger.info("  🔧 Implement result parsing in runner.py:")
            self.logger.info("     # TODO: Parse and store results in state")
            self.logger.info("     state.trend_analysis = parse_trend_result(result)")
            self.logger.info("     state.market_analysis = parse_market_result(result)")
            self.logger.info("     state.competition_analysis = parse_competition_result(result)")
            self.logger.info("     state.profit_analysis = parse_profit_result(result)")

        if not self.test_results["result_extraction"]:
            self.logger.info("  🔧 Improve agent output extraction from events")
            self.logger.info("  🔧 Check event content structure and JSON parsing")


async def main():
    """Main test execution."""
    validator = ADKExecutionValidator()

    print("🎯 ADK Execution Validation Test")
    print("="*80)

    # Run all tests
    await validator.validate_pipeline_creation()
    await validator.validate_runner_creation()
    await validator.validate_result_extraction()
    await validator.validate_adk_execution()

    # Generate report
    validator.generate_test_report()

    print("\n🎯 Test completed! Check logs above for detailed results.")
    print("📁 Logs saved to: logs/adk_validator.log (if file logging enabled)")


if __name__ == "__main__":
    asyncio.run(main())