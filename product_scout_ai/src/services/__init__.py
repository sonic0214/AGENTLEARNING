"""
Services package for ProductScout AI.

This package contains high-level service interfaces for
the analysis system.
"""
from .analysis_service import (
    AnalysisService,
    AnalysisServiceConfig,
    create_analysis_service,
    quick_analysis,
)

from .history_service import (
    HistoryService,
    HistoryServiceConfig,
    ServiceHistoryEntry,
    create_history_service,
)

from .export_service import (
    ExportService,
    ExportConfig,
    create_export_service,
    export_to_json,
    export_to_markdown,
)

__all__ = [
    # Analysis Service
    "AnalysisService",
    "AnalysisServiceConfig",
    "create_analysis_service",
    "quick_analysis",
    # History Service
    "HistoryService",
    "HistoryServiceConfig",
    "ServiceHistoryEntry",
    "create_history_service",
    # Export Service
    "ExportService",
    "ExportConfig",
    "create_export_service",
    "export_to_json",
    "export_to_markdown",
]
