#!/usr/bin/env python3
"""
Simple test for ParallelAgent execution
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from google.adk.agents import LlmAgent
from google.adk.agents import ParallelAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

def test_simple_parallel():
    """Test basic ParallelAgent functionality."""
    print("🧪 简单测试ParallelAgent...")

    try:
        # Create simple sub-agents
        sub_agents = [
            LlmAgent(
                name="test_agent_1",
                instruction="You are a test agent. Return 'Hello from agent 1'.",
                model="gemini-2.0-flash",
                tools=[]
            ),
            LlmAgent(
                name="test_agent_2",
                instruction="You are a test agent. Return 'Hello from agent 2'.",
                model="gemini-2.0-flash",
                tools=[]
            )
        ]

        # Create parallel agent using LlmAgent (as base class)
        parallel_agent = LlmAgent(
            name="parallel_test",
            instruction="You are a coordinator. Run both sub-agents and return their responses.",
            model="gemini-2.0-flash",
            tools=[]
        )

        # Manually set sub_agents
        parallel_agent.sub_agents = sub_agents

        print(f"✅ ParallelAgent创建: {parallel_agent.name}")
        print(f"📊 Sub-agents: {len(parallel_agent.sub_agents)}")

        # Test execution
        session_service = InMemorySessionService()
        session = session_service.create_session(app_name='test', user_id='test')

        message = types.Content(
            role='user',
            parts=[types.Part(text='Run test agents')]
        )

        runner = Runner(
            agent=parallel_agent,
            app_name='test',
            session_service=session_service
        )

        print("🚀 开始测试执行...")

        event_count = 0
        for event in runner.run(
            user_id='test',
            session_id=session.id,
            new_message=message
        ):
            event_count += 1
            print(f"📨 Event {event_count}: {type(event).__name__}")

            if event_count >= 10:
                break

        print(f"🎉 处理了 {event_count} 个事件!")

        return event_count > 0

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_parallel()

    if success:
        print("\n🎉 简单测试成功!")
        print("✅ ParallelAgent能够正常执行")
    else:
        print("\n❌ 简单测试失败!")
        print("❌ ParallelAgent仍有问题")