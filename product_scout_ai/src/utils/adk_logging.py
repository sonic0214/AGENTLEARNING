"""
ADK Event logging utilities for detailed agent execution tracking.

This module provides enhanced logging for Google ADK events,
including model calls, tool usage, and agent reasoning steps.
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

from google.adk.runners import Event
from src.utils.safe_access import safe_dict_path, is_non_empty_list


class ADKEventLogger:
    """
    Enhanced logger for ADK events with detailed agent tracking.

    Provides detailed logging of:
    - Individual agent events
    - Model calls and responses
    - Tool usage (Google Search)
    - Agent reasoning steps
    - Performance metrics
    """

    def __init__(self, logger: logging.Logger, debug_mode: bool = True):
        """
        Initialize ADK event logger.

        Args:
            logger: Base logger instance
            debug_mode: Whether to log detailed debug information
        """
        self.logger = logger
        self.debug_mode = debug_mode
        self.agent_events: Dict[str, list] = {}  # Track events by agent
        self.start_time = datetime.now()

    def log_event(self, event: Event, event_index: int) -> None:
        """
        Log a single ADK event with detailed analysis.

        Args:
            event: ADK Event object
            event_index: Sequential event index
        """
        try:
            # Basic event info
            event_time = datetime.now()
            elapsed_time = (event_time - self.start_time).total_seconds()

            # Extract event data
            event_data = event.model_dump() if hasattr(event, 'model_dump') else {}

            # Determine event type and agent
            event_info = self._classify_event(event_data)
            agent_name = event_info.get('agent_name', 'unknown_agent')

            # Log basic event info
            self.logger.info(f"🤖 Event {event_index} [{elapsed_time:.2f}s]: {event_info['type']} (Agent: {agent_name})")

            # Log detailed content
            if self.debug_mode:
                self._log_event_details(event, event_info, agent_name, event_index)

            # Track by agent
            if agent_name not in self.agent_events:
                self.agent_events[agent_name] = []
            self.agent_events[agent_name].append({
                'event_index': event_index,
                'timestamp': event_time,
                'type': event_info['type'],
                'event_data': event_data
            })

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to log event {event_index}: {e}")

    def _classify_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify event type and extract relevant information.

        Args:
            event_data: Event data dictionary

        Returns:
            Dictionary with classification info
        """
        # Check for function calls (tool usage)
        function_calls = event_data.get('function_calls', [])
        if function_calls:
            return {
                'type': 'tool_call',
                'agent_name': self._extract_agent_from_tools(function_calls),
                'tools': [call.get('name', 'unknown') for call in function_calls],
                'content': f"Calling {len(function_calls)} tool(s): {', '.join([call.get('name', 'unknown') for call in function_calls])}"
            }

        # Check for function responses (tool results)
        function_responses = event_data.get('function_responses', [])
        if function_responses:
            return {
                'type': 'tool_response',
                'agent_name': self._extract_agent_from_tools(function_responses),
                'tools': [resp.get('name', 'unknown') for resp in function_responses],
                'content': f"Received {len(function_responses)} tool response(s)"
            }

        # Check for content responses
        if 'content' in event_data:
            content = event_data['content']

            # Safe access to parts[0].text
            text = None
            if isinstance(content, dict) and 'parts' in content:
                parts = content['parts']
                if is_non_empty_list(parts) and isinstance(parts[0], dict) and 'text' in parts[0]:
                    text = parts[0]['text']
                else:
                    # Fallback to safe path navigation
                    text = safe_dict_path(content, 'parts.0.text')

            if text:
                # Determine agent from content
                agent_name = self._extract_agent_from_content(text)
                return {
                    'type': 'content_response',
                    'agent_name': agent_name,
                    'content_preview': text[:200] + "..." if len(text) > 200 else text,
                    'content_length': len(text)
                }

        # Check for final response
        if event_data.get('is_final_response', False):
            return {
                'type': 'final_response',
                'agent_name': 'system',
                'content': 'Agent execution completed'
            }

        # Default classification
        return {
            'type': 'other',
            'agent_name': 'unknown_agent',
            'content': 'Unknown event type'
        }

    def _extract_agent_from_tools(self, tools: list) -> str:
        """
        Extract agent name from tool calls/responses.

        Args:
            tools: List of tool call/response objects

        Returns:
            Agent name string
        """
        if not tools:
            return 'unknown_agent'

        # Try to identify from tool parameters
        for tool in tools:
            if 'name' in tool and tool['name'] == 'google_search':
                # Look at search query to infer agent type
                if 'args' in tool and 'query' in tool['args']:
                    query = tool['args']['query'].lower()
                    if any(keyword in query for keyword in ['trend', 'search', 'volume']):
                        return 'trend_agent'
                    elif any(keyword in query for keyword in ['market', 'size', 'segment', 'customer']):
                        return 'market_agent'
                    elif any(keyword in query for keyword in ['competitor', 'competition', 'price']):
                        return 'competition_agent'
                    elif any(keyword in query for keyword in ['profit', 'margin', 'cost', 'roi']):
                        return 'profit_agent'

        return 'analysis_agent'

    def _extract_agent_from_content(self, text: str) -> str:
        """
        Extract agent name from response content.

        Args:
            text: Response text content

        Returns:
            Agent name string
        """
        text_lower = text.lower()

        # Look for characteristic phrases
        if any(keyword in text_lower for keyword in ['trend analysis', 'search trends', 'seasonality']):
            return 'trend_agent'
        elif any(keyword in text_lower for keyword in ['market size', 'tam', 'sam', 'som', 'customer segment']):
            return 'market_agent'
        elif any(keyword in text_lower for keyword in ['competitor', 'competition', 'market share']):
            return 'competition_agent'
        elif any(keyword in text_lower for keyword in ['profit', 'margin', 'roi', 'unit economics']):
            return 'profit_agent'

        return 'analysis_agent'

    def _log_event_details(self, event: Event, event_info: Dict[str, Any], agent_name: str, event_index: int) -> None:
        """
        Log detailed event information.

        Args:
            event: ADK Event object
            event_info: Event classification info
            agent_name: Name of the agent
            event_index: Event index number
        """
        try:
            event_type = event_info['type']

            if event_type == 'tool_call':
                # Log tool usage details
                function_calls = event.get_function_calls()
                self.logger.info(f"🔧 Tool Calls ({agent_name}):")
                for i, call in enumerate(function_calls):
                    self.logger.info(f"  {i+1}. {call.name}")
                    if hasattr(call, 'args') and call.args:
                        self.logger.info(f"     Args: {json.dumps(call.args, ensure_ascii=False)}")

            elif event_type == 'tool_response':
                # Log tool results
                function_responses = event.get_function_responses()
                self.logger.info(f"📋 Tool Responses ({agent_name}):")
                for i, response in enumerate(function_responses):
                    self.logger.info(f"  {i+1}. {response.name}")
                    if hasattr(response, 'response') and response.response:
                        # Truncate long responses
                        response_str = str(response.response)
                        if len(response_str) > 300:
                            self.logger.info(f"     Result: {response_str[:300]}...")
                            self.logger.info(f"     (truncated, total length: {len(response_str)})")
                        else:
                            self.logger.info(f"     Result: {response_str}")

            elif event_type == 'content_response':
                # Log agent reasoning
                content_preview = event_info.get('content_preview', '')
                content_length = event_info.get('content_length', 0)
                self.logger.info(f"💭 Agent Reasoning ({agent_name}):")
                self.logger.info(f"     Length: {content_length} characters")
                self.logger.info(f"     Preview: {content_preview}")

            elif event_type == 'final_response':
                self.logger.info(f"✅ Final Response: Agent execution completed")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to log details for event {event_index}: {e}")

    def log_summary(self) -> None:
        """Log execution summary with agent-specific statistics."""
        total_time = (datetime.now() - self.start_time).total_seconds()

        self.logger.info("=" * 80)
        self.logger.info("🎯 ADK EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"⏱️  Total execution time: {total_time:.2f}s")
        self.logger.info(f"🤖 Agents tracked: {len(self.agent_events)}")

        for agent_name, events in self.agent_events.items():
            self.logger.info(f"\n--- {agent_name.upper()} ---")
            self.logger.info(f"   Events: {len(events)}")

            # Count event types
            event_types = {}
            for event in events:
                event_type = event['type']
                event_types[event_type] = event_types.get(event_type, 0) + 1

            for event_type, count in event_types.items():
                self.logger.info(f"   {event_type}: {count}")

        self.logger.info("=" * 80)

    def get_agent_timeline(self, agent_name: str) -> list:
        """
        Get timeline of events for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of events for the agent
        """
        return self.agent_events.get(agent_name, [])

    def extract_agent_outputs(self) -> Dict[str, Any]:
        """
        Extract final outputs for each agent.

        Returns:
            Dictionary mapping agent names to their outputs
        """
        outputs = {}

        for agent_name, events in self.agent_events.items():
            # Look for final content responses
            for event in reversed(events):  # Start from last events
                if event['type'] == 'content_response':
                    event_data = event['event_data']
                    if 'content' in event_data:
                        content = event_data['content']

                        # Safe access to parts[0].text
                        text = None
                        if isinstance(content, dict) and 'parts' in content:
                            parts = content['parts']
                            if is_non_empty_list(parts) and isinstance(parts[0], dict) and 'text' in parts[0]:
                                text = parts[0]['text']
                            else:
                                # Fallback to safe path navigation
                                text = safe_dict_path(content, 'parts.0.text')

                        if text:
                            outputs[agent_name] = text
                            break

        return outputs


def create_adk_logger(base_logger: logging.Logger, debug_mode: bool = True) -> ADKEventLogger:
    """
    Factory function to create ADK event logger.

    Args:
        base_logger: Base logger instance
        debug_mode: Whether to enable detailed debug logging

    Returns:
        Configured ADKEventLogger instance
    """
    return ADKEventLogger(base_logger, debug_mode)