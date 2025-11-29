"""
Workflows package for ProductScout AI.

This package contains the analysis pipeline and execution workflows.
"""
from .analysis_pipeline import (
    AnalysisPipeline,
    PipelineResult,
    create_pipeline,
    get_pipeline_phases,
    get_phase_description,
)

from .runner import (
    PipelineRunner,
    RunnerConfig,
    create_runner,
    quick_analyze,
)

__all__ = [
    # Pipeline
    "AnalysisPipeline",
    "PipelineResult",
    "create_pipeline",
    "get_pipeline_phases",
    "get_phase_description",
    # Runner
    "PipelineRunner",
    "RunnerConfig",
    "create_runner",
    "quick_analyze",
]
