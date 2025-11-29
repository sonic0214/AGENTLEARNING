#!/usr/bin/env python3
"""
Demo script showing enhanced ADK event logging capabilities.

This script demonstrates how to capture detailed reasoning logs
from each agent during parallel execution.
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.adk_logging import create_adk_logger, ADKEventLogger
from src.utils.logger import setup_logger, get_logger
from src.workflows.runner import create_runner
from src.schemas.input_schemas import AnalysisRequest


async def demo_enhanced_logging():
    """Demonstrate enhanced ADK logging with parallel agents."""
    print("🎯 ADK Enhanced Logging Demo")
    print("=" * 60)

    # Setup logger
    logger = setup_logger("adk_demo", level=logging.INFO)
    logger.info("Starting ADK logging demonstration...")

    # Create sample analysis request
    request = AnalysisRequest(
        category="便携式榨汁机",
        target_market="US",
        business_model="amazon_fba",
        budget_range="medium",
        keywords=["便携", "健康", "健身"]
    )

    logger.info(f"📝 Analysis request: {request.category} ({request.target_market})")

    # Create runner
    runner = create_runner()

    try:
        # Run analysis with enhanced logging
        logger.info("🚀 Starting analysis with detailed logging...")

        result = await runner.run_analysis(request)

        if result.success:
            logger.info("✅ Analysis completed successfully!")
            logger.info(f"⏱️  Total execution time: {result.execution_time:.2f}s")

            # Show phase times
            if result.phase_times:
                logger.info("📊 Phase breakdown:")
                for phase, time_spent in result.phase_times.items():
                    logger.info(f"  {phase}: {time_spent:.2f}s")
        else:
            logger.error("❌ Analysis failed")
            if result.error:
                logger.error(f"Error: {result.error}")

    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}", exc_info=True)

    print("\n" + "=" * 60)
    print("🎯 Demo completed!")
    print("\n📋 Key Features Demonstrated:")
    print("  ✅ Detailed ADK event tracking")
    print("  ✅ Individual agent identification")
    print("  ✅ Tool usage logging (Google Search)")
    print("  ✅ Agent reasoning capture")
    print("  ✅ Execution timeline")
    print("  ✅ Performance metrics")
    print("\n💡 To see detailed agent reasoning, check the logs above!")
    print("📁 Logs are also saved to logs/adk_demo.log if configured.")


def demonstrate_manual_event_logging():
    """Demonstrate manual event logging with simulated ADK events."""
    print("\n" + "🔧 Manual Event Logging Demo")
    print("=" * 60)

    # Create logger
    base_logger = setup_logger("manual_demo", level=logging.INFO)
    adk_logger = create_adk_logger(base_logger, debug_mode=True)

    # Simulate different types of events
    from google.adk.runners import Event

    simulated_events = [
        # TrendAgent searching
        {
            "function_calls": [
                {"name": "google_search", "args": {"query": "portable blender market trends 2024"}}
            ]
        },

        # MarketAgent analysis
        {
            "function_responses": [
                {"name": "google_search", "response": "Market size: $2.3B, Growth: 8.5% annually"}
            ]
        },

        # CompetitionAgent results
        {
            "content": {
                "parts": [{"text": "Competition analysis: 5 major competitors, moderate entry barriers"}]
            }
        },

        # ProfitAgent calculations
        {
            "content": {
                "parts": [{"text": "Profit analysis: Unit cost $12, Selling price $45, Margin 73%"}]
            }
        },

        # Final response
        {
            "is_final_response": True
        }
    ]

    print("📝 Simulating ADK events with detailed logging...\n")

    # Log each simulated event
    for i, event_data in enumerate(simulated_events):
        # Create Event object (simulated)
        event = Event.model_validate(event_data)
        adk_logger.log_event(event, i + 1)
        print()  # Add spacing

    # Show summary
    adk_logger.log_summary()

    print(f"\n🎯 Manual demo completed! Total simulated events: {len(simulated_events)}")


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Full ADK execution with enhanced logging")
    print("2. Manual event simulation")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "1":
        asyncio.run(demo_enhanced_logging())
    elif choice == "2":
        demonstrate_manual_event_logging()
    else:
        print("Invalid choice. Exiting.")