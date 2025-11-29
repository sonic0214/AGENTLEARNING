#!/usr/bin/env python3
"""
Fix for runner.py to implement result parsing and state updates.

This script will patch the runner.py to properly parse and store
agent results in the analysis state.
"""
import sys
import os
import re

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def get_runner_py_content():
    """Get the current runner.py content."""
    runner_path = os.path.join('src', 'workflows', 'runner.py')
    with open(runner_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def create_fixed_content():
    """Create fixed runner.py content with proper result parsing."""
    original_content = get_runner_py_content()

    # Find the section to replace
    todo_section = """                    # TODO: Parse and store results in state
                    # state.trend_analysis = parse_trend_result(result)
                    # state.market_analysis = parse_market_result(result)
                    # state.competition_analysis = parse_competition_result(result)
                    # state.profit_analysis = parse_profit_result(result)"""

    # Create the replacement section
    replacement = """                    # Parse and store results in state using enhanced logging
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
                            self._parse_result_from_final_result(result, state)"""

    # Replace the TODO section
    fixed_content = original_content.replace(todo_section, replacement)

    # Add helper method at the end of the class
    class_end_pattern = r'(def process_agent_output\(self.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n\n)'

    # Find the end of the PipelineRunner class
    helper_methods = '''
    def _parse_result_from_final_result(self, result, state):
        """Parse analysis results from the final ADK result."""
        try:
            result_data = result.model_dump()
            self.logger.info(f"🔍 Final result keys: {list(result_data.keys())}")

            # Look for content in result
            if 'content' in result_data:
                content = result_data['content']
                if isinstance(content, dict) and 'parts' in content:
                    parts = content['parts']
                    if parts and 'text' in parts[0]:
                        text = parts[0]['text']
                        self.logger.info(f"📄 Final result text length: {len(text)} chars")

                        # Try to extract JSON from text
                        from src.agents import extract_json_from_response
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
'''

    # Add helper methods after the PipelineRunner class
    class_pattern = r'(class PipelineRunner:.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n(?:.*?\n)*?.*?\n)'
    class_end = re.search(class_pattern, fixed_content, re.DOTALL)

    if class_end:
        # Insert helper methods before the next function or class
        end_pos = class_end.end()
        final_content = (
            fixed_content[:end_pos] +
            helper_methods +
            fixed_content[end_pos:]
        )
    else:
        final_content = fixed_content

    return final_content

def apply_fix():
    """Apply the fix to runner.py."""
    try:
        # Create backup
        runner_path = os.path.join('src', 'workflows', 'runner.py')
        backup_path = runner_path + '.backup'

        original_content = get_runner_py_content()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✅ Backup created: {backup_path}")

        # Write fixed content
        fixed_content = create_fixed_content()
        with open(runner_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Fixed runner.py: {runner_path}")

        print("🎯 Fix Summary:")
        print("  ✅ Added proper result parsing from ADK events")
        print("  ✅ Added fallback parsing from final result")
        print("  ✅ Added comprehensive error handling")
        print("  ✅ Added helper methods for each analysis type")
        print("  ✅ Added detailed logging for debugging")

        return True

    except Exception as e:
        print(f"❌ Failed to apply fix: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Applying result parsing fix to runner.py...")
    print("=" * 80)

    success = apply_fix()

    if success:
        print("\n🎉 Fix applied successfully!")
        print("📋 Next steps:")
        print("1. Test the fixed runner with your analysis request")
        print("2. Check logs for detailed agent execution and result parsing")
        print("3. Verify that state.trend_analysis, state.market_analysis, etc. are populated")
        print("4. The enhanced ADK logging should show individual agent outputs")
    else:
        print("\n❌ Fix failed. Check the error messages above.")