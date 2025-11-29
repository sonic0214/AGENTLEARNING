#!/usr/bin/env python3
"""
Manual fix for runner.py to implement result parsing.

This script manually adds the missing result parsing functionality
to the runner.py file.
"""
import sys
import os
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def fix_runner_py():
    """Manually fix the runner.py file by adding result parsing methods."""

    print("🔧 Manually fixing runner.py...")

    # Read current runner.py
    runner_path = os.path.join('src', 'workflows', 'runner.py')
    with open(runner_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the helper methods to add
    helper_methods = '''
    def _extract_result_from_final_event(self, result, state):
        """Extract analysis results from the final ADK event."""
        try:
            result_data = result.model_dump()
            self.logger.info(f"📊 Final result keys: {list(result_data.keys())}")

            # Look for content in result
            if 'content' in result_data:
                content = result_data['content']
                if isinstance(content, dict) and 'parts' in content:
                    parts = content['parts']
                    self.logger.info(f"📄 Found {len(parts)} content parts")

                    for i, part in enumerate(parts):
                        if isinstance(part, dict) and 'text' in part:
                            text = part['text']
                            self.logger.info(f"📝 Part {i+1} text length: {len(text)} chars")
                            self.logger.info(f"📝 Part {i+1} preview: {text[:200]}...")

                            # Try to extract JSON from text
                            from src.agents import extract_json_from_response
                            json_data = extract_json_from_response(text)
                            if json_data:
                                self.logger.info(f"🔍 Part {i+1} JSON keys: {list(json_data.keys())}")

                                # Store in appropriate state field
                                if 'trend_score' in json_data or 'trend_direction' in json_data:
                                    from src.schemas.output_schemas import TrendAnalysis
                                    state.trend_analysis = TrendAnalysis.from_dict(json_data)
                                    self.logger.info(f"✅ Trend analysis parsed from final result")

                                elif 'market_score' in json_data or 'market_size' in json_data:
                                    from src.schemas.output_schemas import MarketAnalysis
                                    state.market_analysis = MarketAnalysis.from_dict(json_data)
                                    self.logger.info(f"✅ Market analysis parsed from final result")

                                elif 'competition_score' in json_data or 'competitors' in json_data:
                                    from src.schemas.output_schemas import CompetitionAnalysis
                                    state.competition_analysis = CompetitionAnalysis.from_dict(json_data)
                                    self.logger.info(f"✅ Competition analysis parsed from final result")

                                elif 'profit_score' in json_data or 'unit_economics' in json_data:
                                    from src.schemas.output_schemas import ProfitAnalysis
                                    state.profit_analysis = ProfitAnalysis.from_dict(json_data)
                                    self.logger.info(f"✅ Profit analysis parsed from final result")

        except Exception as e:
            self.logger.error(f"❌ Failed to extract from final result: {str(e)}", exc_info=True)

    def _extract_agent_result_from_events(self, events):
        """Extract individual agent results from ADK events."""
        agent_results = {}

        try:
            for event in events:
                event_data = event.model_dump()
                self.logger.info(f"📨 Processing event: {type(event).__name__}")

                # Check for function responses (tool results)
                if hasattr(event, 'get_function_responses'):
                    responses = event.get_function_responses()
                    for response in responses:
                        agent_name = self._identify_agent_from_tool_call(response)
                        if agent_name and hasattr(response, 'response'):
                            result = response.response
                            self.logger.info(f"🔧 Tool result for {agent_name}: {type(result)}")

                            # Parse JSON from tool result
                            if isinstance(result, dict):
                                if agent_name not in agent_results:
                                    agent_results[agent_name] = result
                                else:
                                    agent_results[agent_name].update(result)

                # Check for content responses
                if hasattr(event, 'model_dump'):
                    event_data = event.model_dump()
                    if 'content' in event_data:
                        content = event_data['content']
                        if isinstance(content, dict) and 'parts' in content:
                            parts = content['parts']
                            for part in parts:
                                if isinstance(part, dict) and 'text' in part:
                                    text = part['text']
                                    self.logger.info(f"🤖 Content response: {len(text)} chars")

                                    # Try to identify agent and extract JSON
                                    from src.agents import extract_json_from_response
                                    json_data = extract_json_from_response(text)
                                    if json_data:
                                        # Identify agent based on content
                                        agent_name = self._identify_agent_from_content(json_data)
                                        if agent_name:
                                            if agent_name not in agent_results:
                                                agent_results[agent_name] = json_data
                                            self.logger.info(f"✅ Identified {agent_name} analysis")

            return agent_results

        except Exception as e:
            self.logger.error(f"❌ Failed to extract agent results: {str(e)}", exc_info=True)
            return {}

    def _identify_agent_from_tool_call(self, tool_response):
        """Identify agent name from tool call/response."""
        if hasattr(tool_response, 'name'):
            if tool_response.name == 'google_search':
                # Would need to check context or args to identify which agent
                return 'analysis_agent'  # Default fallback
        return None

    def _identify_agent_from_content(self, json_data):
        """Identify agent name from content JSON data."""
        if not json_data:
            return None

        # Look for characteristic keys in each agent type
        if any(key in json_data for key in ['trend_score', 'trend_direction', 'seasonality']):
            return 'trend_agent'
        elif any(key in json_data for key in ['market_score', 'market_size', 'customer_segments']):
            return 'market_agent'
        elif any(key in json_data for key in ['competition_score', 'competitors', 'pricing_analysis']):
            return 'competition_agent'
        elif any(key in json_data for key in ['profit_score', 'unit_economics', 'investment']):
            return 'profit_agent'
        elif any(key in json_data for key in ['opportunity_score', 'dimension_scores']):
            return 'evaluator_agent'

        return None
'''

    # Find the class definition and add helper methods
    class_match = re.search(r'(class PipelineRunner:.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)\n    def __init__', content)

    if class_match:
        # Insert helper methods before __init__ method
        insert_pos = class_match.end() - 4  # Insert before __init__
        fixed_content = content[:insert_pos] + helper_methods + content[insert_pos:]

        # Write fixed content
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"✅ Fixed runner.py: {runner_path}")
        return True
    else:
        print("❌ Could not find PipelineRunner class definition")
        return False

if __name__ == "__main__":
    success = fix_runner_py()
    if success:
        print("\n🎉 Manual fix completed!")
        print("\n💡 The fix adds:")
        print("  ✅ Result extraction from final ADK event")
        print("  ✅ Individual agent result identification")
        print("  ✅ Proper error handling and logging")
        print("  ✅ JSON parsing from agent responses")
        print("\n🚀 Now test your analysis request with the fixed runner!")
    else:
        print("\n❌ Manual fix failed!")