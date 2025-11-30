# ProductScout AI

> An intelligent product opportunity analysis platform powered by Google ADK and Gemini AI

[![Google ADK](https://img.shields.io/badge/Google-ADK-4285F4?logo=google)](https://google.github.io/adk-docs/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-8E75B2)](https://ai.google.dev/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Why Agents?](#why-agents)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [ADK Implementation](#adk-implementation)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

**ProductScout AI** is an advanced multi-agent system built on Google's Agent Development Kit (ADK) that helps entrepreneurs, e-commerce sellers, and product managers identify profitable product opportunities through comprehensive AI-powered market analysis.

The system leverages **parallel agent execution**, **Google Search integration**, and **Gemini AI models** to analyze products across four critical dimensions: market trends, market size, competition landscape, and profitability potential.

## Problem Statement

Identifying profitable product opportunities in today's competitive e-commerce landscape is challenging and time-consuming. Traditional market research requires:

- **Manual data collection** from multiple sources (Google Trends, market reports, competitor analysis)
- **Hours of analysis** to synthesize insights across different dimensions
- **Expert knowledge** in market analysis, financial modeling, and competitive strategy
- **Significant cost** for professional market research services ($5,000-$50,000 per report)

ProductScout AI solves this by **automating comprehensive market analysis** through intelligent AI agents that work in parallel, delivering actionable insights in minutes instead of weeks.

## Why Agents?

Agents are uniquely suited for product opportunity analysis because:

1. **Parallel Processing**: Multiple specialized agents analyze different dimensions simultaneously (trends, market size, competition, profitability), dramatically reducing analysis time from hours to minutes.

2. **Specialized Expertise**: Each agent is optimized for a specific analysis domain with custom prompts, tools, and evaluation criteria, ensuring deep, focused insights.

3. **Tool Integration**: Agents leverage Google Search, web scraping, and data analysis tools to gather real-time market intelligence autonomously.

4. **Adaptive Reasoning**: LLM-powered agents can interpret ambiguous market signals, identify patterns, and provide contextual recommendations that rule-based systems cannot.

5. **Collaborative Intelligence**: The orchestrator agent synthesizes outputs from all analysis agents into cohesive evaluation reports, mimicking how expert analysts collaborate.

## Key Features

### Multi-Agent System Architecture

- **4 Parallel Analysis Agents**: Trend, Market, Competition, and Profit analysis running concurrently
- **Sequential Coordination**: Orchestrator → Parallel Analysis → Evaluation → Report Generation
- **State Management**: In-memory session service with persistent analysis state
- **Error Handling**: Robust fallback mechanisms and graceful degradation

### Google ADK Integration

- **LlmAgent**: Each specialized agent powered by Gemini models
- **ParallelAgent**: Concurrent execution of 4 analysis agents
- **SequentialAgent**: Coordinated pipeline from analysis to report generation
- **Runner & Sessions**: ADK's execution engine with session management
- **Built-in Tools**: Google Search integration for real-time data

### Analysis Capabilities

- **Trend Analysis**: Search volume trends, seasonality patterns, growth trajectories
- **Market Analysis**: TAM/SAM/SOM estimation, market maturity, customer segmentation
- **Competition Analysis**: Competitor identification, pricing strategies, market barriers
- **Profit Analysis**: Unit economics, margin analysis, ROI projections
- **SWOT Synthesis**: Comprehensive evaluation with opportunity scoring (0-100)

### User Interface

- **Gradio Web Interface**: Interactive UI with real-time progress tracking
- **Analysis History**: Browse and compare previous analyses
- **Export Options**: JSON and Markdown report generation
- **Visual Charts**: Score cards, comparison charts, trend visualizations

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ProductScout AI Pipeline                  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Orchestrator    │ (SequentialAgent)
                    │     Agent        │
                    └────────┬─────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │       Parallel Analysis Phase         │
         │         (ParallelAgent)               │
         └───────────────────────────────────────┘
                             │
         ┌───────────────────┴──────────────────┐
         │                                       │
    ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐
    │  Trend   │  │ Market   │  │Competition│  │ Profit  │
    │  Agent   │  │  Agent   │  │  Agent    │  │  Agent  │
    │          │  │          │  │           │  │         │
    │ Gemini   │  │ Gemini   │  │ Gemini    │  │ Gemini  │
    │ +Search  │  │ +Search  │  │ +Search   │  │ +Search │
    └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
         │            │             │             │
         └────────────┴─────────────┴─────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Evaluator      │ (LlmAgent)
                    │     Agent        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    Report        │ (LlmAgent)
                    │     Agent        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Final Report    │
                    │  (Markdown/JSON) │
                    └──────────────────┘
```

### Data Flow

1. **User Input** → Analysis Request (category, market, business model, budget)
2. **Orchestrator** → Creates and coordinates parallel analysis agents
3. **Parallel Execution** → 4 agents analyze simultaneously using Google Search
4. **State Collection** → Results stored in AnalysisState object
5. **Evaluation** → Synthesizes findings into opportunity score (0-100)
6. **Report Generation** → Creates comprehensive markdown report
7. **Output** → Report displayed in UI and saved to local files

## Installation

### Prerequisites

- Python 3.10 or higher
- Google Cloud API key (for Gemini AI)
- Internet connection (for Google Search tool)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/AgentLearning.git
cd AgentLearning/product_scout_ai
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure API Keys

Create a `.env` file in the `product_scout_ai` directory:

```bash
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.0-flash-exp  # or gemini-1.5-pro
```

To get your Google API key:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into your `.env` file

## Quick Start

### Launch Web Interface

```bash
# From product_scout_ai directory
python run_app.py
```

The Gradio interface will open at `http://localhost:7860`

### Run Analysis

1. **Enter Product Category**: e.g., "wireless headphones", "smart home devices"
2. **Select Target Market**: US, UK, CN, JP, etc.
3. **Choose Business Model**: Amazon FBA, Dropshipping, Private Label, etc.
4. **Set Budget Range**: Low ($1K-$5K), Medium ($5K-$20K), High ($20K+)
5. **Click "Start Analysis"**

### View Results

Results include:
- **Opportunity Score**: Overall score (0-100)
- **Dimension Scores**: Individual scores for Trend, Market, Competition, Profit
- **SWOT Analysis**: Strengths, Weaknesses, Opportunities, Threats
- **Recommendations**: Go/Cautious/Avoid with detailed reasoning
- **Comprehensive Report**: Markdown-formatted analysis

## Usage Examples

### Example 1: CLI Usage (Direct API)

```python
import asyncio
from src.workflows.runner import quick_analyze

async def main():
    result = await quick_analyze(
        category="mechanical keyboards",
        target_market="US",
        business_model="amazon_fba",
        budget_range="medium"
    )

    # Check if successful
    if result.is_ok():
        pipeline_result = result.unwrap()
        state = pipeline_result.state

        print(f"Opportunity Score: {state.evaluation_score}/100")
        print(f"Recommendation: {state.evaluation_result.recommendation}")
        print(f"\nReport:\n{state.report_text}")
    else:
        error = result.unwrap_err()
        print(f"Error: {error.message}")

asyncio.run(main())
```

### Example 2: Custom Agent Configuration

```python
from src.agents.orchestrator import OrchestratorAgent
from src.schemas.input_schemas import AnalysisRequest
from src.config.settings import Settings

# Custom settings
settings = Settings(
    MODEL_NAME="gemini-1.5-pro",
    MAX_TOKENS=8192,
    TEMPERATURE=0.7
)

# Create orchestrator
orchestrator = OrchestratorAgent(settings)

# Create request
request = AnalysisRequest(
    category="smart watches",
    target_market="UK",
    business_model="dropshipping",
    budget_range="low"
)

# Build pipeline
pipeline = orchestrator.create_full_pipeline(request)
```

### Example 3: Batch Analysis

```python
import asyncio
from src.workflows.runner import PipelineRunner

async def batch_analyze(categories):
    runner = PipelineRunner()
    results = []

    for category in categories:
        request = AnalysisRequest(
            category=category,
            target_market="US",
            business_model="amazon_fba",
            budget_range="medium"
        )

        result = await runner.run_analysis(request)
        results.append({
            "category": category,
            "result": result
        })

    return results

categories = ["yoga mats", "phone cases", "pet toys"]
results = asyncio.run(batch_analyze(categories))
```

## ADK Implementation

### Key ADK Concepts Applied

#### 1. Multi-Agent Patterns

```python
from google.adk.agents import ParallelAgent, SequentialAgent, LlmAgent

# Parallel execution of 4 specialized agents
parallel_agent = ParallelAgent(
    name="parallel_analysis",
    sub_agents=[trend_agent, market_agent, competition_agent, profit_agent],
    description="Executes 4 analysis dimensions concurrently"
)

# Sequential pipeline: Analysis → Evaluation → Report
sequential_pipeline = SequentialAgent(
    name="analysis_pipeline",
    sub_agents=[parallel_agent, evaluator_agent, report_agent],
    description="Full product analysis workflow"
)
```

#### 2. Sessions & State Management

```python
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Create session service
session_service = InMemorySessionService()

# Create session for analysis
session = await session_service.create_session(
    app_name="product_scout_ai",
    user_id="user123",
    session_id="analysis_001"
)

# Create runner with session
runner = Runner(
    agent=parallel_agent,
    app_name="product_scout_ai",
    session_service=session_service
)
```

#### 3. Built-in Tools

```python
from google.adk.tools import google_search

# Create agent with Google Search tool
trend_agent = LlmAgent(
    name="trend_agent",
    model="gemini-2.0-flash-exp",
    instruction="Analyze market trends using search data...",
    tools=[google_search]  # Built-in Google Search integration
)
```

#### 4. Observability

```python
from src.utils.logger import get_logger, log_agent_call, log_phase_complete

logger = get_logger(__name__)

# Log agent execution
log_agent_call(logger, "TrendAgent", "Analyzing wireless headphones")

# Log phase completion
log_phase_complete(logger, "parallel_analysis", elapsed_time=12.5)
```

### ADK Features Demonstrated

✅ **Multi-agent system**: ParallelAgent (4 agents) + SequentialAgent (3-phase pipeline)
✅ **LLM-powered agents**: All agents use Gemini models
✅ **Built-in tools**: Google Search integration
✅ **Sessions & Memory**: InMemorySessionService for state management
✅ **Observability**: Comprehensive logging with phase tracking
✅ **Error handling**: Result type pattern with structured error contexts

## Project Structure

```
product_scout_ai/
├── src/
│   ├── agents/              # Agent definitions
│   │   ├── base_agent.py    # Base agent class
│   │   ├── analysis_agents.py  # Trend, Market, Competition, Profit agents
│   │   ├── evaluator_agents.py # Evaluator & Report agents
│   │   └── orchestrator.py  # Main orchestrator
│   │
│   ├── workflows/           # Pipeline execution
│   │   ├── analysis_pipeline.py  # Pipeline configuration
│   │   └── runner.py        # ADK Runner integration
│   │
│   ├── config/              # Configuration
│   │   ├── settings.py      # Application settings
│   │   └── prompts.py       # Agent prompts & instructions
│   │
│   ├── schemas/             # Data models
│   │   ├── input_schemas.py    # Request schemas
│   │   ├── output_schemas.py   # Analysis result schemas
│   │   └── state_schemas.py    # Pipeline state schemas
│   │
│   ├── tools/               # Custom tools (placeholder)
│   │   ├── trend_tools.py
│   │   ├── market_tools.py
│   │   ├── competition_tools.py
│   │   └── profit_tools.py
│   │
│   ├── services/            # Business logic
│   │   ├── analysis_service.py  # Analysis orchestration
│   │   ├── export_service.py    # Report export
│   │   └── history_service.py   # Analysis history
│   │
│   ├── ui/                  # Gradio interface
│   │   ├── app.py           # Main Gradio app
│   │   ├── tabs/            # UI tabs (analysis, history, export)
│   │   ├── handlers/        # Event handlers
│   │   ├── components/      # Reusable UI components
│   │   └── utils/           # UI utilities
│   │
│   └── utils/               # Shared utilities
│       ├── logger.py        # Logging utilities
│       ├── result.py        # Result type (Ok/Err)
│       ├── adk_logging.py   # Enhanced ADK event logging
│       └── error_messages.py
│
├── tests/                   # Test suites
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
│
├── reports/                 # Generated analysis reports
├── data/                    # Cached data
├── docs/                    # Documentation
├── examples/                # Usage examples
│
├── run_app.py              # Main application launcher
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not committed)
```

## Documentation

- **[ADK Documentation](https://google.github.io/adk-docs/)**: Official Google ADK guide
- **[Project Documentation](./docs/)**: Architecture, API reference, guides
- **[Example Reports](./reports/)**: Sample analysis outputs

## Demo Video

### TBD
[Watch the 3-minute demo on YouTube](https://youtube.com/your-video-link)

The demo covers:
- Problem statement and market opportunity
- Why agents are ideal for this use case
- System architecture walkthrough
- Live demonstration of analysis
- Results and insights

## Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/unit/agents/
pytest tests/integration/

# Run with coverage
pytest --cov=src tests/
```

## Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional
MODEL_NAME=gemini-2.0-flash-exp  # Default model
MAX_TOKENS=8192                  # Max output tokens
TEMPERATURE=0.7                  # LLM temperature
LOG_LEVEL=INFO                   # Logging level
```

### Model Options

- **gemini-2.0-flash-exp**: Fast, cost-effective (recommended for production)
- **gemini-1.5-pro**: More capable, higher quality (recommended for complex analysis)
- **gemini-1.5-flash**: Balanced performance and cost

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run linters
flake8 src/
black src/
mypy src/

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Google ADK Team**: For the excellent Agent Development Kit
- **Google Gemini**: For powerful LLM capabilities
- **Gradio Team**: For the intuitive UI framework
- **Open Source Community**: For countless libraries and tools

## Contact

- **Author**: Sonic0214
- **Email**: buffoon1234@gmail.com
- **GitHub**: [@sonic0214](https://github.com/sonic0214)
- **Project Link**: [https://github.com/sonic0214/AgentLearning](https://github.com/sonic0214/AgentLearning)

---

**Built with ❤️ using Google ADK and Gemini AI**

*Submitted for the Google Agent Development Kit Marathon 2025*
