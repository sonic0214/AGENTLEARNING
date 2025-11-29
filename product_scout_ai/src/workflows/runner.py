"""
Pipeline runner for executing analysis workflows.

This module provides the execution engine for running
analysis pipelines with ADK.
"""
from typing import Dict, Any, Optional, AsyncGenerator, Callable
from dataclasses import dataclass
from datetime import datetime
import asyncio
import uuid
import logging

from google.adk.runners import Runner  # type: ignore
from google.adk.sessions import InMemorySessionService, Session  # type: ignore
try:
    from google.genai import types  # ADK Content and Part types
except ImportError:
    # Fallback to try different import path
    try:
        from google.adk import types as genai_types  # ADK Content and Part types
    except ImportError:
        # Final fallback
        types = None

from src.config.settings import Settings
from src.schemas.input_schemas import AnalysisRequest
from src.schemas.output_schemas import (
    TrendAnalysis,
    MarketAnalysis,
    CompetitionAnalysis,
    ProfitAnalysis,
    EvaluationResult,
)
from src.schemas.state_schemas import AnalysisState
from src.agents import extract_json_from_response
from src.utils.logger import get_logger, log_phase_start, log_phase_complete, log_agent_call, log_agent_input_detailed, log_agent_output_detailed, log_agent_event, log_tool_call
from src.utils.safe_access import safe_dict_path, is_non_empty_list
from src.utils.result import Result, ErrorContext, ErrorCategory
from src.utils.error_messages import get_error_message

from .analysis_pipeline import AnalysisPipeline, PipelineResult


@dataclass
class RunnerConfig:
    """
    Configuration for the pipeline runner.

    Attributes:
        app_name: Application name for sessions
        max_retries: Maximum retry attempts for failed phases
        timeout_seconds: Timeout for each phase
        enable_streaming: Whether to enable streaming responses
    """
    app_name: str = "product_scout_ai"
    max_retries: int = 3
    timeout_seconds: int = 120
    enable_streaming: bool = True


class PipelineRunner:
    """
    Execution engine for analysis pipelines.

    Handles the actual execution of pipelines using ADK's
    Runner and Session management.
    """

    def __init__(self, settings: Optional[Settings] = None, config: Optional[RunnerConfig] = None):
        """Initialize the pipeline runner."""
        self.config = config or RunnerConfig()
        self.settings = settings or Settings()  # Add settings attribute
        self.logger = get_logger(__name__)
        self.session_service = InMemorySessionService()

    def _parse_result_from_final_result(self, result, state):
        """Parse analysis results from the final ADK result."""
        try:
            result_data = result.model_dump()
            self.logger.info(f"🔍 Final result keys: {list(result_data.keys())}")

            # Look for content in result
            if 'content' in result_data:
                content = result_data['content']

                # Safe access to parts[0].text with fallback
                text = None
                if isinstance(content, dict) and 'parts' in content:
                    parts = content['parts']
                    if is_non_empty_list(parts) and isinstance(parts[0], dict) and 'text' in parts[0]:
                        text = parts[0]['text']
                    else:
                        # Fallback to safe path navigation
                        text = safe_dict_path(content, 'parts.0.text')

                if text:
                    self.logger.info(f"📄 Final result text length: {len(text)} chars")

                    # Try to extract JSON from text
                    json_data = extract_json_from_response(text)

                    if json_data:
                        self.logger.info(f"🔧 Extracted JSON from final result: {list(json_data.keys())}")
                        self._store_json_data_in_state(json_data, state)
                    else:
                        self.logger.warning("⚠️  No JSON found in final result text")
                else:
                    self.logger.warning("⚠️  No text found in content parts")
            else:
                self.logger.warning("⚠️  No content found in final result")

        except Exception as e:
            self.logger.error(f"❌ Failed to parse final result: {str(e)}", exc_info=True)

    def _store_json_data_in_state(self, json_data, state):
        """Store JSON data in the appropriate state fields."""
        try:
            # Trend analysis
            if 'trend_score' in json_data:
                state.trend_analysis = self._create_trend_analysis(json_data)
                self.logger.info(f"✅ Trend analysis stored: score={json_data.get('trend_score', 0)}")

            # Market analysis
            if 'market_score' in json_data:
                state.market_analysis = self._create_market_analysis(json_data)
                self.logger.info(f"✅ Market analysis stored: score={json_data.get('market_score', 0)}")

            # Competition analysis
            if 'competition_score' in json_data:
                state.competition_analysis = self._create_competition_analysis(json_data)
                self.logger.info(f"✅ Competition analysis stored: score={json_data.get('competition_score', 0)}")

            # Profit analysis
            if 'profit_score' in json_data:
                state.profit_analysis = self._create_profit_analysis(json_data)
                self.logger.info(f"✅ Profit analysis stored: score={json_data.get('profit_score', 0)}")

        except Exception as e:
            self.logger.error(f"❌ Failed to store JSON data in state: {str(e)}", exc_info=True)

    def _create_trend_analysis(self, json_data):
        """Create TrendAnalysis object from JSON data."""
        from src.schemas.output_schemas import TrendAnalysis
        return TrendAnalysis.from_dict(json_data)

    def _create_market_analysis(self, json_data):
        """Create MarketAnalysis object from JSON data."""
        from src.schemas.output_schemas import MarketAnalysis
        return MarketAnalysis.from_dict(json_data)

    def _create_competition_analysis(self, json_data):
        """Create CompetitionAnalysis object from JSON data."""
        from src.schemas.output_schemas import CompetitionAnalysis
        return CompetitionAnalysis.from_dict(json_data)

    def _create_profit_analysis(self, json_data):
        """Create ProfitAnalysis object from JSON data."""
        from src.schemas.output_schemas import ProfitAnalysis
        return ProfitAnalysis.from_dict(json_data)

    def _parse_trend_result(self, output):
        """Parse trend analysis result from agent output."""
        from src.agents import extract_json_from_response
        from src.schemas.output_schemas import TrendAnalysis

        try:
            json_data = extract_json_from_response(output)
            if json_data:
                return TrendAnalysis.from_dict(json_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to parse trend result: {str(e)}", exc_info=True)
            return None

    def _parse_market_result(self, output):
        """Parse market analysis result from agent output."""
        from src.agents import extract_json_from_response
        from src.schemas.output_schemas import MarketAnalysis

        try:
            json_data = extract_json_from_response(output)
            if json_data:
                return MarketAnalysis.from_dict(json_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to parse market result: {str(e)}", exc_info=True)
            return None

    def _parse_competition_result(self, output):
        """Parse competition analysis result from agent output."""
        from src.agents import extract_json_from_response
        from src.schemas.output_schemas import CompetitionAnalysis

        try:
            json_data = extract_json_from_response(output)
            if json_data:
                return CompetitionAnalysis.from_dict(json_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to parse competition result: {str(e)}", exc_info=True)
            return None

    def _parse_profit_result(self, output):
        """Parse profit analysis result from agent output."""
        from src.agents import extract_json_from_response
        from src.schemas.output_schemas import ProfitAnalysis

        try:
            json_data = extract_json_from_response(output)
            if json_data:
                return ProfitAnalysis.from_dict(json_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to parse profit result: {str(e)}", exc_info=True)
            return None

        # Pipeline instance
        self._pipeline: Optional[AnalysisPipeline] = None

        # Current session
        self._current_session: Optional[Session] = None

    async def create_session(self, user_id: Optional[str] = None) -> Session:
        """
        Create a new session for analysis.

        Args:
            user_id: Optional user identifier

        Returns:
            New Session instance
        """
        session_id = str(uuid.uuid4())
        user = user_id or "anonymous"

        # InMemorySessionService.create_session is async
        session = await self.session_service.create_session(
            app_name=self.config.app_name,
            user_id=user,
            session_id=session_id
        )

        # Store the session ID for consistent access
        self._last_session_id = session_id
        self._current_session = session

        # Log session creation for debugging
        self.logger.info(f"✅ Session created: {session_id}")
        self.logger.info(f"   App name: {self.config.app_name}")
        self.logger.info(f"   User ID: {user}")

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get an existing session.

        Args:
            session_id: Session ID

        Returns:
            Session if found, None otherwise
        """
        return self.session_service.get_session(
            app_name=self.config.app_name,
            user_id="*",  # Any user
            session_id=session_id
        )

    def initialize_pipeline(
        self,
        on_phase_complete: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> AnalysisPipeline:
        """
        Initialize the analysis pipeline.

        Args:
            on_phase_complete: Callback for phase completion

        Returns:
            Initialized pipeline
        """
        self._pipeline = AnalysisPipeline(
            settings=self.settings,
            on_phase_complete=on_phase_complete
        )
        return self._pipeline

    async def run_analysis(
        self,
        request: AnalysisRequest,
        session: Optional[Session] = None,
        on_phase_complete: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run a complete analysis with structured error handling.

        This method orchestrates the full analysis pipeline:
        1. Initialize state
        2. Run parallel analysis phase
        3. Run evaluation phase
        4. Generate report

        Args:
            request: Analysis request
            session: Optional existing session

        Returns:
            Result containing either:
            - Ok(PipelineResult): Successful analysis with state and report
            - Err(ErrorContext): Business-level error with context
        """
        start_time = datetime.now()
        phase_times: Dict[str, float] = {}

        # Create or use session with consistent user_id
        if session is None:
            session = await self.create_session(user_id="system")

        # Initialize state
        state = AnalysisState(request=request)
        state.set_phase("initialized")

        # Initialize pipeline if needed
        if self._pipeline is None:
            self.initialize_pipeline()

        try:
            # Phase 1: Parallel Analysis
            phase_start = datetime.now()
            state.set_phase("analyzing_trends")
            log_phase_start(self.logger, "parallel_analysis", "Running parallel agents (trend, market, competition, profit)")

            # Create pipeline agents
            self.logger.info("📦 Creating pipeline agents...")
            pipeline_agents = self._pipeline.create_pipeline_agents(request)
            self.logger.info(f"✅ Created {len(pipeline_agents)} pipeline agents")

            # Create ADK runner for parallel agent
            self.logger.info("🏃 Initializing ADK Runner for parallel execution...")
            agents_dict = self._pipeline.create_pipeline_agents(request)

            parallel_runner = Runner(
                agent=agents_dict["parallel_agent"],
                app_name=self.config.app_name,
                session_service=self.session_service
            )

            # Run parallel analysis using ADK
            self.logger.info("🚀 Executing parallel analysis agents...")
            log_agent_call(self.logger, "ParallelAgent", f"Analyzing category: {request.category}")

            try:
                # Import enhanced ADK logging
                from src.utils.adk_logging import create_adk_logger

                # Create enhanced logger for ADK events
                adk_logger = create_adk_logger(self.logger, debug_mode=True)

                # Actually run the agents using ADK
                events = []
                event_count = 0

                # Create proper ADK Content message
                message_text = f"请分析产品类别 '{request.category}' 在市场 '{request.target_market}' 的机会"
                if types is not None:
                    message = types.Content(
                        role="user",
                        parts=[types.Part(text=message_text)]
                    )
                else:
                    # Fallback if types not available
                    message = {
                        "role": "user",
                        "content": message_text
                    }

                # Log parallel agents input with醒目 formatting
                log_agent_input_detailed(
                    logger=self.logger,
                    agent_name="PARALLEL_AGENTS_INPUT",
                    instruction=message_text,
                    tools=["google_search"]  # All agents have google_search tool
                )

                self.logger.info(f"📨 Created message - Type: {type(message).__name__}, Text length: {len(message_text)}")
                self.logger.info("📡 Starting detailed ADK event logging...")

                # Extract session information for ADK runner
                # Get session ID
                if hasattr(session, 'id'):
                    session_id_str = session.id
                elif hasattr(session, 'session_id'):
                    session_id_str = session.session_id
                else:
                    session_id_str = getattr(self, '_last_session_id', str(uuid.uuid4()))

                # Get user ID from session
                user_id_str = session.user_id if hasattr(session, 'user_id') else "system"

                self.logger.info(f"🔑 Session ID: {session_id_str}")
                self.logger.info(f"👤 User ID: {user_id_str}")
                self.logger.info(f"🤖 Parallel agent sub-agents: {len(pipeline_agents['parallel_agent'].sub_agents)}")

                # Run parallel analysis
                try:
                    self.logger.info("🔄 Starting runner.run_async() async generator...")

                    async for event in parallel_runner.run_async(
                        user_id=user_id_str,
                        session_id=session_id_str,
                        new_message=message
                    ):
                        events.append(event)
                        event_count += 1

                        # Enhanced event logging with ADK logger
                        adk_logger.log_event(event, event_count)

                        # Check if this is a content event from an agent
                        if hasattr(event, 'content') and event.content:
                            self.logger.info(f"🤖 Agent content captured: {type(event.content).__name__}")
                            if hasattr(event.content, 'parts') and event.content.parts:
                                for i, part in enumerate(event.content.parts):
                                    if hasattr(part, 'text') and part.text:
                                        # Log detailed agent output with醒目 formatting
                                        log_agent_output_detailed(
                                            logger=self.logger,
                                            agent_name=f"Agent_{event_count}",
                                            output_text=part.text,
                                            output_type=f"PART_{i+1}_of_{len(event.content.parts)}"
                                        )
                                        self.logger.info(f"📝 Agent part {i}: {len(part.text)} characters")

                        # Keep the original debug log for compatibility
                        if self.logger.isEnabledFor(logging.DEBUG):
                            self.logger.debug(f"📨 Agent event {event_count}: {type(event).__name__} - {str(event)[:100] if len(str(event)) > 100 else str(event)}")

                        # Add timeout protection for very long executions
                        if event_count > 100:  # Safety limit
                            self.logger.warning("⚠️ Event limit reached, stopping generator to prevent infinite loop")
                            break

                    self.logger.info("🏁 Generator exhausted (loop completed)")

                except StopIteration:
                    self.logger.info("⚠️  Generator raised StopIteration immediately")
                except Exception as gen_error:
                    self.logger.error(f"❌ Generator error: {gen_error}", exc_info=True)
                    raise

                # Log execution summary
                adk_logger.log_summary()

                # Collect final result from events (safely handle empty list)
                result = events[-1] if events and len(events) > 0 else None
                self.logger.info(f"✅ Processed {event_count} agent events")

                # Always try to extract agent outputs, even if no final result
                agent_outputs = adk_logger.extract_agent_outputs()

                if agent_outputs:
                    self.logger.info(f"🎯 SUCCESSFULLY EXTRACTED {len(agent_outputs)} AGENT OUTPUTS:")
                    for agent_name, output in agent_outputs.items():
                        self.logger.info(f"   🤖 {agent_name.upper()}: {len(output)} characters")
                        if len(output) > 0:
                            self.logger.info(f"      Preview: {output[:150]}..." if len(output) > 150 else output)
                else:
                    self.logger.warning("⚠️ No agent outputs extracted from events")

                if result:
                    self.logger.info(f"📊 Final result type: {type(result).__name__}")
                    self.logger.info(f"📊 Agent response length: {len(str(result))} chars")

                # Parse and store results in state using enhanced logging
                    try:
                        # Extract individual agent outputs from events
                        agent_outputs = adk_logger.extract_agent_outputs()

                        if agent_outputs:
                            self.logger.info(f"🔍 Extracting {len(agent_outputs)} agent outputs from events...")

                            # Store each agent's output in state
                            for agent_name, output in agent_outputs.items():
                                if agent_name == "trend_agent":
                                    state.trend_analysis = self._parse_trend_result(output)
                                elif agent_name == "market_agent":
                                    state.market_analysis = self._parse_market_result(output)
                                elif agent_name == "competition_agent":
                                    state.competition_analysis = self._parse_competition_result(output)
                                elif agent_name == "profit_agent":
                                    state.profit_analysis = self._parse_profit_result(output)

                            self.logger.info("✅ All agent outputs parsed and stored in state")
                        else:
                            self.logger.warning("⚠️  No agent outputs extracted from events")

                            # If no individual outputs, try to parse from final result
                            if result and hasattr(result, 'model_dump'):
                                self.logger.info("🔍 Attempting to parse from final result...")
                                self._parse_result_from_final_result(result, state)

                    except Exception as parse_error:
                        self.logger.error(f"❌ Failed to parse agent outputs: {str(parse_error)}", exc_info=True)
                        # Fallback: try basic parsing
                        if result and hasattr(result, 'model_dump'):
                            self._parse_result_from_final_result(result, state)

            except Exception as e:
                self.logger.error(f"❌ Agent execution failed: {str(e)}", exc_info=True)
                raise

            elapsed = (datetime.now() - phase_start).total_seconds()
            phase_times["parallel_analysis"] = elapsed
            log_phase_complete(self.logger, "parallel_analysis", elapsed)

            # Phase 2: Evaluation (would run after parallel results)
            phase_start = datetime.now()
            state.set_phase("evaluating")
            log_phase_start(self.logger, "evaluation", "Evaluating opportunity score and generating recommendations")

            # Extract individual agent outputs for evaluation
            try:
                # Get agent outputs from the enhanced logging
                agent_outputs = adk_logger.extract_agent_outputs()

                trend_analysis = agent_outputs.get("trend_agent", "No trend analysis available")
                market_analysis = agent_outputs.get("market_agent", "No market analysis available")
                competition_analysis = agent_outputs.get("competition_agent", "No competition analysis available")
                profit_analysis = agent_outputs.get("profit_agent", "No profit analysis available")

                self.logger.info("🎯 SYNTHESIZING AGENT OUTPUTS FOR EVALUATION")
                self.logger.info(f"   Trend: {len(trend_analysis)} chars")
                self.logger.info(f"   Market: {len(market_analysis)} chars")
                self.logger.info(f"   Competition: {len(competition_analysis)} chars")
                self.logger.info(f"   Profit: {len(profit_analysis)} chars")

                # Create and run evaluation agent
                from src.agents.evaluator_agents import EvaluatorAgent
                evaluation_agent = EvaluatorAgent()
                eval_llm_agent = evaluation_agent.create_agent(
                    category=request.category,
                    target_market=request.target_market,
                    trend_analysis=trend_analysis,
                    market_analysis=market_analysis,
                    competition_analysis=competition_analysis,
                    profit_analysis=profit_analysis
                )

                # Create evaluation runner
                eval_runner = Runner(
                    agent=eval_llm_agent,
                    app_name=self.config.app_name,
                    session_service=self.session_service
                )

                # Run evaluation
                # Create simple evaluation trigger message
                eval_instruction = f"请综合分析以上结果，生成最终评估报告"

                # Create evaluation message
                if types is not None:
                    eval_message = types.Content(
                        role="user",
                        parts=[types.Part(text=eval_instruction)]
                    )
                else:
                    # Fallback for evaluation message
                    eval_message = {
                        "role": "user",
                        "content": eval_instruction
                    }

                # Log evaluation agent input with醒目 formatting
                log_agent_input_detailed(
                    logger=self.logger,
                    agent_name="EVALUATION_AGENT_INPUT",
                    instruction=eval_instruction,
                    tools=None
                )

                self.logger.info("🔍 Starting evaluation agent execution...")
                eval_events = []

                async for event in eval_runner.run_async(
                    user_id=user_id_str,
                    session_id=session_id_str,
                    new_message=eval_message
                ):
                    eval_events.append(event)

                    # Log evaluation progress
                    if hasattr(event, 'content') and event.content:
                        self.logger.info(f"📊 Evaluation content captured: {type(event.content).__name__}")
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for i, part in enumerate(event.content.parts):
                                if hasattr(part, 'text') and part.text:
                                    # Log detailed evaluation agent output with醒目 formatting
                                    log_agent_output_detailed(
                                        logger=self.logger,
                                        agent_name="EVALUATION_AGENT",
                                        output_text=part.text,
                                        output_type=f"EVAL_PART_{i+1}"
                                    )
                                    self.logger.info(f"   Analysis: {part.text[:100]}..." if len(part.text) > 100 else part.text)

                    # Limit evaluation events for safety
                    if len(eval_events) > 50:
                        self.logger.warning("⚠️ Evaluation event limit reached, proceeding to final result")
                        break

                # Parse evaluation result
                if eval_events:
                    final_eval_event = eval_events[-1] if eval_events else None
                    if final_eval_event and hasattr(final_eval_event, 'content'):
                        eval_content = final_eval_event.content
                        if hasattr(eval_content, 'parts') and eval_content.parts:
                            eval_text = ""
                            for part in eval_content.parts:
                                if hasattr(part, 'text') and part.text:
                                    eval_text += part.text

                            if eval_text:
                                # Parse evaluation result from JSON
                                evaluation_result_dict = extract_json_from_response(eval_text)

                                if evaluation_result_dict:
                                    # Convert dict to EvaluationResult object
                                    from src.schemas.output_schemas import EvaluationResult
                                    state.evaluation_result = EvaluationResult.from_dict(evaluation_result_dict)
                                    state.evaluation_score = state.evaluation_result.opportunity_score

                                    self.logger.info(f"🎯 EVALUATION COMPLETED:")
                                    self.logger.info(f"   Score: {state.evaluation_score}/100")
                                    self.logger.info(f"   Recommendation: {state.evaluation_result.recommendation}")
                                else:
                                    self.logger.warning("⚠️ Failed to parse evaluation JSON, using fallback")
                                    from src.schemas.output_schemas import EvaluationResult
                                    state.evaluation_result = EvaluationResult(
                                        opportunity_score=50,
                                        dimension_scores={"trend": 50, "market": 50, "competition": 50, "profit": 50},
                                        swot_analysis={"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
                                        recommendation="cautious",
                                        recommendation_detail="Evaluation parsing failed - using fallback values",
                                        key_risks=["Unable to parse evaluation results"],
                                        success_factors=["Manual review recommended"]
                                    )
                                    state.evaluation_score = 50
                            else:
                                self.logger.warning("⚠️ No evaluation text content found")
                        else:
                            self.logger.warning("⚠️ No evaluation content parts found")
                    else:
                        self.logger.warning("⚠️ No evaluation events captured")
                else:
                    self.logger.warning("⚠️ Evaluation agent produced no events")

            except Exception as eval_error:
                self.logger.error(f"❌ Evaluation phase failed: {eval_error}", exc_info=True)
                # Fallback to basic evaluation
                from src.schemas.output_schemas import EvaluationResult
                state.evaluation_result = EvaluationResult(
                    opportunity_score=50,
                    dimension_scores={"trend": 30, "market": 30, "competition": 30, "profit": 30},
                    swot_analysis={"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
                    recommendation="cautious",
                    recommendation_detail="Analysis completed but evaluation failed - manual review recommended",
                    key_risks=["Incomplete analysis"],
                    success_factors=["Requires validation"]
                )
                state.evaluation_score = 50

            elapsed = (datetime.now() - phase_start).total_seconds()
            phase_times["evaluation"] = elapsed
            log_phase_complete(self.logger, "evaluation", elapsed)

            # Phase 3: Report Generation
            phase_start = datetime.now()
            state.set_phase("generating_report")
            log_phase_start(self.logger, "report_generation", "Generating final report")

            try:
                # Get all analysis results for report generation
                trend_analysis = state.trend_analysis or "No trend analysis available"
                market_analysis = state.market_analysis or "No market analysis available"
                competition_analysis = state.competition_analysis or "No competition analysis available"
                profit_analysis = state.profit_analysis or "No profit analysis available"

                # Get evaluation_result, create fallback if needed
                if state.evaluation_result:
                    evaluation_result = state.evaluation_result
                else:
                    from src.schemas.output_schemas import EvaluationResult
                    evaluation_result = EvaluationResult(
                        opportunity_score=50,
                        dimension_scores={"trend": 50, "market": 50, "competition": 50, "profit": 50},
                        swot_analysis={"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
                        recommendation="cautious",
                        recommendation_detail="Basic analysis completed - requires detailed review",
                        key_risks=["No evaluation available"],
                        success_factors=["Manual review needed"]
                    )

                self.logger.info("📋 SYNTHESIZING RESULTS FOR REPORT GENERATION")
                self.logger.info(f"   Trend: {len(trend_analysis)} chars")
                self.logger.info(f"   Market: {len(market_analysis)} chars")
                self.logger.info(f"   Competition: {len(competition_analysis)} chars")
                self.logger.info(f"   Profit: {len(profit_analysis)} chars")
                self.logger.info(f"   Evaluation Score: {evaluation_result.opportunity_score}")

                # Create and run report agent
                from src.agents.evaluator_agents import ReportAgent
                report_agent = ReportAgent()

                # Convert evaluation_result to JSON string (it's now always an object)
                eval_result_str = evaluation_result.to_json()

                report_llm_agent = report_agent.create_agent(
                    category=request.category,
                    target_market=request.target_market,
                    trend_analysis=str(trend_analysis),
                    market_analysis=str(market_analysis),
                    competition_analysis=str(competition_analysis),
                    profit_analysis=str(profit_analysis),
                    evaluation_result=eval_result_str
                )

                # Create report runner
                report_runner = Runner(
                    agent=report_llm_agent,
                    app_name=self.config.app_name,
                    session_service=self.session_service
                )

                # Create simple report trigger message
                report_instruction = f"请生成完整的分析报告"

                # Create report message
                if types is not None:
                    report_message = types.Content(
                        role="user",
                        parts=[types.Part(text=report_instruction)]
                    )
                else:
                    # Fallback for report message
                    report_message = {
                        "role": "user",
                        "content": report_instruction
                    }

                # Log report agent input with醒目 formatting
                log_agent_input_detailed(
                    logger=self.logger,
                    agent_name="REPORT_AGENT_INPUT",
                    instruction=report_instruction,
                    tools=None
                )

                self.logger.info("📝 Starting report agent execution...")
                report_events = []

                async for event in report_runner.run_async(
                    user_id=user_id_str,
                    session_id=session_id_str,
                    new_message=report_message
                ):
                    report_events.append(event)

                    # Log report generation progress
                    if hasattr(event, 'content') and event.content:
                        self.logger.info(f"📄 Report content captured: {type(event.content).__name__}")
                        if hasattr(event.content, 'parts') and event.content.parts:
                            for i, part in enumerate(event.content.parts):
                                if hasattr(part, 'text') and part.text:
                                    # Log detailed report agent output with醒目 formatting
                                    log_agent_output_detailed(
                                        logger=self.logger,
                                        agent_name="REPORT_AGENT",
                                        output_text=part.text,
                                        output_type=f"REPORT_PART_{i+1}"
                                    )
                                    self.logger.info(f"📝 Report section: {len(part.text)} characters")

                    # Limit report events for safety
                    if len(report_events) > 100:
                        self.logger.warning("⚠️ Report event limit reached, using current results")
                        break

                # Parse report result
                if report_events:
                    final_report_event = report_events[-1] if report_events else None
                    if final_report_event and hasattr(final_report_event, 'content'):
                        report_content = final_report_event.content
                        if hasattr(report_content, 'parts') and report_content.parts:
                            report_text = ""
                            for part in report_content.parts:
                                if hasattr(part, 'text') and part.text:
                                    report_text += part.text

                            if report_text:
                                # Store report text directly (no parsing needed for markdown report)
                                state.report_text = report_text
                                state.report_result = {"report_text": report_text}

                                self.logger.info("📋 REPORT GENERATION COMPLETED:")
                                self.logger.info(f"   Report Length: {len(report_text)} characters")

                                # Check report content
                                has_executive_summary = "Executive Summary" in report_text or "执行摘要" in report_text
                                has_swot = "SWOT" in report_text or "优势" in report_text
                                has_recommendations = "Recommendation" in report_text or "建议" in report_text

                                self.logger.info(f"   Has Executive Summary: {has_executive_summary}")
                                self.logger.info(f"   Has SWOT Analysis: {has_swot}")
                                self.logger.info(f"   Has Recommendations: {has_recommendations}")

                            else:
                                self.logger.warning("⚠️ No report text content found")
                        else:
                            self.logger.warning("⚠️ No report content parts found")
                    else:
                        self.logger.warning("⚠️ No report events captured")
                else:
                    self.logger.warning("⚠️ Report agent produced no events")

            except Exception as report_error:
                self.logger.error(f"❌ Report generation failed: {report_error}", exc_info=True)
                # Fallback to basic report
                fallback_report = f"""
# Product Opportunity Analysis Report

## Category: {request.category}
## Target Market: {request.target_market}

## Executive Summary
This analysis was completed with available data. A comprehensive evaluation requires full agent execution.

## Analysis Results
- **Trend Analysis**: {trend_analysis[:200] if trend_analysis else 'Not available'}...
- **Market Analysis**: {market_analysis[:200] if market_analysis else 'Not available'}...
- **Competition Analysis**: {competition_analysis[:200] if competition_analysis else 'Not available'}...
- **Profit Analysis**: {profit_analysis[:200] if profit_analysis else 'Not available'}...

## Evaluation Score: {evaluation_result.opportunity_score}/100

## Recommendation
{evaluation_result.recommendation.upper()}

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                state.report_text = fallback_report
                state.report_result = {"report_text": fallback_report}

            elapsed = (datetime.now() - phase_start).total_seconds()
            phase_times["report_generation"] = elapsed
            log_phase_complete(self.logger, "report_generation", elapsed)

            # Mark complete
            state.set_phase("completed")
            self.logger.info("🎉 Pipeline execution completed")

            execution_time = (datetime.now() - start_time).total_seconds()

            # Save report to local file
            try:
                self._save_report_to_file(state, request)
            except Exception as save_error:
                self.logger.warning(f"⚠️ Failed to save report to file: {save_error}")

            return Result.Ok(PipelineResult(
                success=True,
                state=state,
                execution_time=execution_time,
                phase_times=phase_times
            ))

        except ImportError as e:
            state.set_error(str(e))
            execution_time = (datetime.now() - start_time).total_seconds()

            return Result.Err(ErrorContext(
                category=ErrorCategory.CONFIGURATION,
                message=get_error_message(ErrorCategory.CONFIGURATION),
                technical_detail=str(e),
                phase=state.current_phase
            ))

        except IndexError as e:
            state.set_error(str(e))
            execution_time = (datetime.now() - start_time).total_seconds()

            return Result.Err(ErrorContext(
                category=ErrorCategory.PARSING,
                message=get_error_message(ErrorCategory.PARSING),
                technical_detail=str(e),
                phase=state.current_phase
            ))

        except asyncio.TimeoutError:
            state.set_error("Analysis timed out")
            execution_time = (datetime.now() - start_time).total_seconds()

            return Result.Err(ErrorContext(
                category=ErrorCategory.TIMEOUT,
                message=get_error_message(ErrorCategory.TIMEOUT),
                technical_detail=f"Analysis exceeded {self.config.timeout_seconds}s timeout",
                phase=state.current_phase
            ))

        except Exception as e:
            state.set_error(str(e))
            execution_time = (datetime.now() - start_time).total_seconds()

            # Categorize other exceptions
            error_category = ErrorCategory.AGENT_EXECUTION
            if "api" in str(e).lower() or "network" in str(e).lower():
                error_category = ErrorCategory.EXTERNAL_API
            elif "resource" in str(e).lower() or "memory" in str(e).lower():
                error_category = ErrorCategory.RESOURCE

            return Result.Err(ErrorContext(
                category=error_category,
                message=get_error_message(error_category),
                technical_detail=str(e),
                phase=state.current_phase
            ))

    async def run_with_streaming(
        self,
        request: AnalysisRequest,
        session: Optional[Session] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Run analysis with streaming progress updates.

        Args:
            request: Analysis request
            session: Optional existing session

        Yields:
            Progress updates as dictionaries
        """
        start_time = datetime.now()

        # Create session
        if session is None:
            session = await self.create_session()

        # Initialize
        state = AnalysisState(request=request)

        yield {
            "type": "started",
            "phase": "initialized",
            "message": "Analysis started",
            "timestamp": datetime.now().isoformat()
        }

        # Initialize pipeline
        if self._pipeline is None:
            self.initialize_pipeline()

        # Phase updates
        phases = [
            ("analyzing_trends", "Analyzing market trends..."),
            ("analyzing_market", "Analyzing market size..."),
            ("analyzing_competition", "Analyzing competition..."),
            ("analyzing_profit", "Analyzing profitability..."),
            ("evaluating", "Evaluating opportunity..."),
            ("generating_report", "Generating report..."),
        ]

        for phase, message in phases:
            state.set_phase(phase)
            yield {
                "type": "progress",
                "phase": phase,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
            # Simulate phase execution
            await asyncio.sleep(0.1)

        state.set_phase("completed")

        yield {
            "type": "completed",
            "phase": "completed",
            "message": "Analysis complete",
            "execution_time": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }

    def process_agent_output(
        self,
        agent_name: str,
        output: str,
        state: AnalysisState
    ) -> AnalysisState:
        """
        Process output from an agent and update state.

        Args:
            agent_name: Name of the agent
            output: Raw output from agent
            state: Current analysis state

        Returns:
            Updated analysis state
        """
        data = extract_json_from_response(output)

        if data is None:
            return state

        try:
            if agent_name == "trend_agent":
                state.trend_analysis = TrendAnalysis.from_dict(data)
            elif agent_name == "market_agent":
                state.market_analysis = MarketAnalysis.from_dict(data)
            elif agent_name == "competition_agent":
                state.competition_analysis = CompetitionAnalysis.from_dict(data)
            elif agent_name == "profit_agent":
                state.profit_analysis = ProfitAnalysis.from_dict(data)
            elif agent_name == "evaluator_agent":
                state.evaluation_result = EvaluationResult.from_dict(data)
        except (ValueError, KeyError) as e:
            # Log error but don't fail
            pass

        state.update_timestamp()
        return state

    def _save_report_to_file(
        self,
        state: AnalysisState,
        request: AnalysisRequest
    ) -> None:
        """
        Save analysis report to local file.

        Args:
            state: Analysis state containing report
            request: Original analysis request
        """
        from pathlib import Path
        import json

        # Create reports directory if it doesn't exist
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        category_slug = request.category.replace(" ", "_").replace("/", "_")
        base_filename = f"{category_slug}_{request.target_market}_{timestamp}"

        # Save Markdown report
        if hasattr(state, 'report_text') and state.report_text:
            md_file = reports_dir / f"{base_filename}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(state.report_text)
            self.logger.info(f"📄 Markdown report saved: {md_file}")

        # Save JSON data (complete analysis results)
        json_file = reports_dir / f"{base_filename}.json"
        export_data = {
            "metadata": {
                "category": request.category,
                "target_market": request.target_market,
                "business_model": request.business_model,
                "budget_range": request.budget_range,
                "timestamp": timestamp,
                "generated_at": datetime.now().isoformat()
            },
            "evaluation": {
                "score": getattr(state, 'evaluation_score', 0),
                "result": getattr(state, 'evaluation_result', {})
            },
            "analyses": {
                "trend": state.trend_analysis.to_dict() if state.trend_analysis and hasattr(state.trend_analysis, 'to_dict') else str(state.trend_analysis),
                "market": state.market_analysis.to_dict() if state.market_analysis and hasattr(state.market_analysis, 'to_dict') else str(state.market_analysis),
                "competition": state.competition_analysis.to_dict() if state.competition_analysis and hasattr(state.competition_analysis, 'to_dict') else str(state.competition_analysis),
                "profit": state.profit_analysis.to_dict() if state.profit_analysis and hasattr(state.profit_analysis, 'to_dict') else str(state.profit_analysis)
            },
            "report_text": getattr(state, 'report_text', '')
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info(f"📊 JSON data saved: {json_file}")


def create_runner(
    settings: Optional[Settings] = None,
    config: Optional[RunnerConfig] = None
) -> PipelineRunner:
    """
    Factory function to create a pipeline runner.

    Args:
        settings: Application settings
        config: Runner configuration

    Returns:
        Configured PipelineRunner
    """
    return PipelineRunner(settings, config)


async def quick_analyze(
    category: str,
    target_market: str = "US",
    business_model: str = "amazon_fba",
    budget_range: str = "medium"
) -> PipelineResult:
    """
    Quick analysis helper function.

    Args:
        category: Product category
        target_market: Target market
        business_model: Business model
        budget_range: Budget range

    Returns:
        Analysis result
    """
    request = AnalysisRequest(
        category=category,
        target_market=target_market,
        business_model=business_model,
        budget_range=budget_range
    )

    runner = create_runner()
    return await runner.run_analysis(request)
