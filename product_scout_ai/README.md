# ProductScout AI

> AI-powered product opportunity analysis using Google ADK Multi-Agent System

## Overview

ProductScout AI is an intelligent product research assistant that helps e-commerce sellers and entrepreneurs discover profitable market opportunities. Built on Google's Agent Development Kit (ADK), it leverages a multi-agent architecture to provide comprehensive analysis across trends, market size, competition, and profitability.

## Features

- **Trend Analysis**: Analyze search trends, seasonality patterns, and emerging opportunities
- **Market Intelligence**: Estimate market size (TAM/SAM/SOM) and identify customer segments
- **Competition Analysis**: Identify competitors, analyze pricing strategies, discover market gaps
- **Profit Evaluation**: Calculate unit economics, margins, and ROI projections
- **Comprehensive Reports**: Generate actionable insights with Go/No-Go recommendations

## Architecture

```
User Input → Orchestrator Agent
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼               ▼
Trend Agent   Market Agent   Competition Agent   Profit Agent
    └───────────────┴───────────────┘
                    │
                    ▼
            Evaluator Agent
                    │
                    ▼
            Report Generator
```

## Quick Start

### Prerequisites

- Python 3.10+
- Google API Key (Gemini)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/product-scout-ai.git
cd product-scout-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Usage

#### CLI

```bash
# Analyze a product category
python -m src.cli.main analyze -c "portable blender" -m US

# View analysis history
python -m src.cli.main history -u user123
```

#### Python API

```python
from src.workflows.orchestrator import ProductScoutOrchestrator
from src.schemas.input_schemas import AnalysisRequest

# Create analysis request
request = AnalysisRequest(
    category="portable blender",
    target_market="US",
    budget_range="medium"
)

# Run analysis
orchestrator = ProductScoutOrchestrator()
report = await orchestrator.analyze(request)
print(report)
```

## Project Structure

```
product_scout_ai/
├── src/
│   ├── config/          # Configuration and prompts
│   ├── schemas/         # Data models
│   ├── tools/           # Custom analysis tools
│   ├── agents/          # ADK agents
│   ├── workflows/       # Pipeline orchestration
│   ├── services/        # Business logic services
│   ├── cli/             # Command line interface
│   └── api/             # REST API (optional)
├── tests/               # Test suites
├── examples/            # Usage examples
└── docs/                # Documentation
```

## Key ADK Concepts Used

- **Multi-Agent System**: Parallel + Sequential agent orchestration
- **Custom Tools**: Trend analysis, profit calculation tools
- **Built-in Tools**: Google Search integration
- **Sessions & State**: Analysis history and state management
- **Agent Evaluation**: Opportunity scoring system

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Code Style

```bash
# Format code
black src tests

# Lint
ruff check src tests

# Type check
mypy src
```

## Deployment

### Cloud Run

```bash
# Build and deploy
gcloud run deploy product-scout-ai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## License

MIT License

## Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- Powered by Gemini AI

---

*Created for the Google ADK Hackathon 2025*
