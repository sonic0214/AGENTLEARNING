#!/usr/bin/env python3
"""
Simple test to identify the root cause of empty results in ADK execution.
"""
import asyncio
import sys
import os
import json

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_agent_creation():
    """Test agent creation and configuration."""
    print("🔧 Testing Agent Creation...")

    try:
        from src.workflows.analysis_pipeline import create_pipeline
        from src.schemas.input_schemas import AnalysisRequest

        # Create pipeline
        pipeline = create_pipeline()
        print("✅ Pipeline created")

        # Create request
        request = AnalysisRequest(
            category="便携式榨汁机",
            target_market="US",
            business_model="amazon_fba",
            budget_range="medium"
        )
        print(f"✅ Request created: {request.category}")

        # Create agents
        agents = pipeline.create_pipeline_agents(request)
        print(f"✅ Agents created: {list(agents.keys())}")

        # Check parallel agent
        parallel_agent = agents.get("parallel_agent")
        if parallel_agent:
            print(f"✅ Parallel agent: {type(parallel_agent).__name__}")
            if hasattr(parallel_agent, 'sub_agents'):
                print(f"✅ Sub-agents: {len(parallel_agent.sub_agents)}")
                for i, sub_agent in enumerate(parallel_agent.sub_agents):
                    print(f"  {i+1}. {sub_agent.name} ({type(sub_agent).__name__})")
            else:
                print("❌ Parallel agent has no sub_agents")
        else:
            print("❌ No parallel agent")

        return True, agents

    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_runner_creation():
    """Test runner creation and session management."""
    print("\n🏃 Testing Runner Creation...")

    try:
        from src.workflows.runner import create_runner

        # Create runner
        runner = create_runner()
        print("✅ Runner created")

        # Test session creation
        session = asyncio.run(runner.create_session())
        print(f"✅ Session created: {type(session).__name__}")

        if hasattr(session, 'id'):
            print(f"✅ Session ID: {session.id}")
        else:
            print("❌ Session has no ID")

        return True, runner, session

    except Exception as e:
        print(f"❌ Runner creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

async def test_adk_run(runner, session, agents):
    """Test actual ADK run with minimal setup."""
    print("\n🚀 Testing ADK Execution...")

    try:
        from google.adk.runners import Runner

        # Create ADK runner
        parallel_agent = agents.get("parallel_agent")
        if not parallel_agent:
            print("❌ No parallel agent available")
            return False, None

        adk_runner = Runner(
            agent=parallel_agent,
            app_name="test_app",
            session_service=runner.session_service
        )
        print("✅ ADK Runner created")

        # Create simple message
        class SimpleMessage:
            def __init__(self, content):
                self.content = content
                self.role = "user"

        message = SimpleMessage("请分析便携式榨汁机在美国市场的机会")

        # Run with event collection
        events = []
        event_count = 0

        print("🔄 Starting event collection...")

        async for event in adk_runner.run(
            user_id="test_user",
            session_id=session.id if hasattr(session, 'id') else "test_session",
            new_message=message
        ):
            events.append(event)
            event_count += 1

            # Log event details
            print(f"📨 Event {event_count}:")
            print(f"  Type: {type(event).__name__}")

            # Check for function calls
            if hasattr(event, 'get_function_calls'):
                calls = event.get_function_calls()
                if calls:
                    print(f"  Function calls: {len(calls)}")
                    for call in calls:
                        print(f"    - {getattr(call, 'name', 'unknown')}")

            # Check for content
            if hasattr(event, 'model_dump'):
                data = event.model_dump()
                if 'content' in data:
                    print(f"  Has content: {type(data['content']).__name__}")

            print("  ---")

            # Limit events for testing
            if event_count >= 10:  # Stop after 10 events for testing
                print("🛑 Stopping event collection (test limit)")
                break

        print(f"✅ Collected {event_count} events")

        # Analyze final event
        if events:
            final_event = events[-1]
            print(f"📊 Final event type: {type(final_event).__name__}")

            # Try to extract content
            if hasattr(final_event, 'model_dump'):
                data = final_event.model_dump()
                print(f"📊 Final event keys: {list(data.keys())}")

                if 'content' in data:
                    content = data['content']
                    print(f"📊 Content type: {type(content)}")

                    if isinstance(content, dict):
                        print(f"📊 Content keys: {list(content.keys())}")
                        if 'parts' in content:
                            parts = content['parts']
                            print(f"📊 Parts count: {len(parts)}")
                            for i, part in enumerate(parts[:3]):  # Show first 3 parts
                                print(f"  Part {i+1}: {list(part.keys())}")
                                if 'text' in part:
                                    text = part['text']
                                    print(f"    Text preview: {text[:200]}...")

            return True, events
        else:
            print("❌ No events collected")
            return False, None

    except Exception as e:
        print(f"❌ ADK run failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def analyze_events(events):
    """Analyze collected events to identify issues."""
    print("\n🔍 Analyzing Events...")

    if not events:
        print("❌ No events to analyze")
        return

    # Event type distribution
    event_types = {}
    function_call_count = 0
    content_response_count = 0

    for i, event in enumerate(events):
        event_type = type(event).__name__
        event_types[event_type] = event_types.get(event_type, 0) + 1

        # Check for function calls
        if hasattr(event, 'get_function_calls'):
            calls = event.get_function_calls()
            if calls:
                function_call_count += len(calls)

        # Check for content
        if hasattr(event, 'model_dump'):
            data = event.model_dump()
            if 'content' in data:
                content_response_count += 1

    print(f"📊 Event Summary:")
    print(f"  Total events: {len(events)}")
    print(f"  Event types: {event_types}")
    print(f"  Function calls: {function_call_count}")
    print(f"  Content responses: {content_response_count}")

    # Check if we have meaningful results
    has_content = content_response_count > 0
    has_tool_calls = function_call_count > 0

    print(f"\n🎯 Issue Analysis:")
    if not has_tool_calls:
        print("  ❌ NO TOOL CALLS - Agents are not using Google Search")
    if not has_content:
        print("  ❌ NO CONTENT RESPONSES - No agent reasoning captured")
    if has_tool_calls and not has_content:
        print("  ⚠️  TOOLS CALLED BUT NO CONTENT - Tool results not processed")
    if not has_tool_calls and not has_content:
        print("  ❌ COMPLETE FAILURE - No agent activity detected")

    if has_content and has_tool_calls:
        print("  ✅ AGENTS ARE WORKING - Tool calls and content responses present")

async def main():
    """Main test execution."""
    print("🎯 ADK Execution Diagnosis Test")
    print("=" * 80)

    # Test 1: Agent Creation
    agents_ok, agents = test_agent_creation()

    # Test 2: Runner Creation
    runner_ok, runner, session = test_runner_creation()

    if not agents_ok or not runner_ok:
        print("\n❌ Basic setup failed. Cannot proceed with ADK test.")
        return

    # Test 3: ADK Execution
    adk_ok, events = await test_adk_run(runner, session, agents)

    # Test 4: Analysis
    if events:
        analyze_events(events)

    print("\n" + "=" * 80)
    print("🎯 Diagnosis Complete!")

    print("\n💡 Next Steps:")
    print("1. If 'NO TOOL CALLS' - Check agent configuration and instructions")
    print("2. If 'NO CONTENT RESPONSES' - Check result parsing and extraction")
    print("3. If 'AGENTS ARE WORKING' - Check result assembly in runner.py")

if __name__ == "__main__":
    asyncio.run(main())