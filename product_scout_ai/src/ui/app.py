"""
Main Gradio application for ProductScout AI.

This module provides the main application entry point.
"""
import gradio as gr
from typing import Optional

# Apply compatibility fixes for Python 3.9
try:
    from ..utils.compatibility import *
except ImportError:
    pass

from .tabs.analysis_tab import create_analysis_tab
from .tabs.history_tab import create_history_tab
from .tabs.comparison_tab import create_comparison_tab
from .tabs.export_tab import create_export_tab
from .utils.theme import get_custom_css


def create_app() -> gr.Blocks:
    """
    Create the main Gradio application.

    Returns:
        Gradio Blocks application
    """
    # Gradio 6.x compatible - minimal configuration
    with gr.Blocks() as app:

        # Header
        gr.Markdown("""
        # 🔍 ProductScout AI

        ### 智能产品机会分析平台

        基于 AI 多智能体技术，从趋势、市场、竞争和利润四个维度全面评估产品机会。
        """)

        # Main Tabs
        with gr.Tabs() as tabs:
            analysis_components = create_analysis_tab()
            history_components = create_history_tab()
            comparison_components = create_comparison_tab()
            export_components = create_export_tab()

        # Footer
        gr.Markdown("""
        ---
        <center>
        <small>ProductScout AI v0.1.0 | Powered by Google ADK & Gemini</small>
        </center>
        """)

    return app


def main(
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    share: bool = False,
    debug: bool = False
) -> None:
    """
    Launch the Gradio application.

    Args:
        server_name: Server hostname
        server_port: Server port
        share: Whether to create a public link
        debug: Enable debug mode
    """
    app = create_app()

    # Enable queuing for async operations
    app.queue(max_size=10)

    # Launch
    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
    )


if __name__ == "__main__":
    main()
