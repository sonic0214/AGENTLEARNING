"""
UI tabs package.

Tab layouts for the Gradio application.
"""
from .analysis_tab import create_analysis_tab
from .history_tab import create_history_tab
from .comparison_tab import create_comparison_tab
from .export_tab import create_export_tab

__all__ = [
    "create_analysis_tab",
    "create_history_tab",
    "create_comparison_tab",
    "create_export_tab",
]
