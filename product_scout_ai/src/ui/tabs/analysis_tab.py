"""
Analysis tab for the Gradio UI.

This module provides the main analysis interface.
"""
import gradio as gr
import asyncio
import concurrent.futures
from typing import Dict, Any, Tuple, Optional

from ..handlers.analysis_handlers import (
    run_analysis,
    validate_inputs,
    get_dimension_scores,
    get_overall_score,
)
from ..components.charts import create_radar_chart, create_bar_chart
from ..components.score_cards import (
    format_score_card,
    format_overall_score,
    format_dimension_scores,
)
from ..components.result_panels import (
    format_trend_analysis,
    format_market_analysis,
    format_competition_analysis,
    format_profit_analysis,
    format_swot_analysis,
    format_risks_and_factors,
)
from ..utils.compatibility import apply_gradio_fixes


# Market options
MARKET_OPTIONS = ["US", "EU", "UK", "CA", "AU", "JP", "DE", "FR"]

# Budget options
BUDGET_OPTIONS = ["low", "medium", "high"]
BUDGET_LABELS = {"low": "Low Budget", "medium": "Medium Budget", "high": "High Budget"}

# Business model options
MODEL_OPTIONS = ["amazon_fba", "dropshipping", "private_label", "wholesale"]
MODEL_LABELS = {
    "amazon_fba": "Amazon FBA",
    "dropshipping": "Dropshipping",
    "private_label": "Private Label",
    "wholesale": "Wholesale"
}


def create_analysis_tab():
    """
    Create the Analysis tab layout.

    Returns:
        Dictionary of component references
    """
    with gr.Tab("🔍 Product Analysis", id="analysis"):
        # Header
        gr.Markdown("""
        ## New Product Analysis

        Enter the product category you want to analyze. The system will provide comprehensive evaluation across four dimensions: trends, market, competition, and profitability.
        """)

        # Input Section
        with gr.Row():
            with gr.Column(scale=2):
                category_input = gr.Textbox(
                    label="Product Category *",
                    placeholder="e.g., portable juicer, smart watch, yoga mat...",
                    lines=1,
                    info="Enter the product category or keywords you want to analyze"
                )
                keywords_input = gr.Textbox(
                    label="Additional Keywords (Optional)",
                    placeholder="e.g., portable, outdoor, fitness (comma separated)",
                    lines=1,
                    info="Maximum 10 keywords, comma separated"
                )

            with gr.Column(scale=1):
                market_dropdown = gr.Dropdown(
                    choices=MARKET_OPTIONS,
                    value="US",
                    label="Target Market",
                    info="Select the market you want to enter"
                )
                budget_radio = gr.Radio(
                    choices=BUDGET_OPTIONS,
                    value="medium",
                    label="Budget Range",
                    info="Your initial investment budget"
                )
                model_dropdown = gr.Dropdown(
                    choices=MODEL_OPTIONS,
                    value="amazon_fba",
                    label="Business Model",
                    info="The sales model you plan to adopt"
                )

        # Buttons
        with gr.Row():
            run_btn = gr.Button(
                "🚀 Start Analysis",
                variant="primary",
                size="lg",
                scale=2
            )
            clear_btn = gr.Button(
                "🗑️ Clear",
                variant="secondary",
                size="lg",
                scale=1
            )

        # Status/Progress
        status_box = gr.Textbox(
            label="Status",
            value="Ready",
            interactive=False,
            visible=True
        )

        # Error message
        error_box = gr.Markdown(visible=False)

        # Results Section (initially hidden)
        with gr.Column(visible=False) as results_section:
            gr.Markdown("---")
            gr.Markdown("## 📊 Analysis Results")

            # Overall Score Section
            overall_score_html = gr.HTML()

            # Dimension Scores
            gr.Markdown("### Dimension Scores")
            with gr.Row():
                trend_score_num = gr.Number(
                    label="Trend Score",
                    precision=0,
                    interactive=False
                )
                market_score_num = gr.Number(
                    label="Market Score",
                    precision=0,
                    interactive=False
                )
                competition_score_num = gr.Number(
                    label="Competition Score",
                    precision=0,
                    interactive=False
                )
                profit_score_num = gr.Number(
                    label="Profit Score",
                    precision=0,
                    interactive=False
                )

            # Charts Row
            with gr.Row():
                radar_chart = gr.Plot(label="Dimension Radar Chart")
                bar_chart = gr.Plot(label="Score Bar Chart")

            # Detailed Analysis Sections
            gr.Markdown("### Detailed Analysis")

            with gr.Accordion("📈 Trend Analysis", open=False):
                trend_details = gr.Markdown()

            with gr.Accordion("🌍 Market Analysis", open=False):
                market_details = gr.Markdown()

            with gr.Accordion("⚔️ Competition Analysis", open=False):
                competition_details = gr.Markdown()

            with gr.Accordion("💰 Profit Analysis", open=False):
                profit_details = gr.Markdown()

            with gr.Accordion("📋 SWOT Analysis", open=True):
                swot_details = gr.Markdown()

            with gr.Accordion("⚠️ Risks & Success Factors", open=True):
                risks_factors_details = gr.Markdown()

        # State to store result
        result_state = gr.State(value=None)

        # Event Handlers
        def on_analyze_click(category, market, budget, model, keywords, progress=gr.Progress()):
            """Handle analyze button click."""
            # Validate
            is_valid, error = validate_inputs(category, market, budget, model, keywords)
            if not is_valid:
                return (
                    gr.update(value=f"❌ {error}"),  # status
                    gr.update(visible=True, value=f"**Error**: {error}"),  # error
                    gr.update(visible=False),  # results
                    None, None, None, None,  # scores
                    None, None,  # charts
                    "", "", "", "", "", "",  # details
                    "",  # overall
                    None,  # state
                )

            # Update status
            yield (
                gr.update(value="🔄 Analyzing..."),
                gr.update(visible=False),
                gr.update(visible=False),
                None, None, None, None,
                None, None,
                "", "", "", "", "", "",
                "",
                None,
            )

            # Run analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                def progress_callback(value, desc):
                    progress(value, desc=desc)

                success, result_data, error_msg = loop.run_until_complete(
                    run_analysis(category, market, budget, model, keywords, progress_callback)
                )

                if not success:
                    yield (
                        gr.update(value=f"❌ Analysis Failed"),
                        gr.update(visible=True, value=f"**Error**: {error_msg}"),
                        gr.update(visible=False),
                        None, None, None, None,
                        None, None,
                        "", "", "", "", "", "",
                        "",
                        None,
                    )
                    return

                # Extract data
                dimension_scores = get_dimension_scores(result_data)
                overall_score, recommendation, detail = get_overall_score(result_data)

                # Create charts
                radar = create_radar_chart(dimension_scores, "Dimension Analysis")
                bar = create_bar_chart(dimension_scores, "Score Comparison")

                # Format details
                trend = result_data.get("trend_analysis", {})
                market_data = result_data.get("market_analysis", {})
                competition = result_data.get("competition_analysis", {})
                profit = result_data.get("profit_analysis", {})
                evaluation = result_data.get("evaluation_result", {})

                trend_md = format_trend_analysis(trend)
                market_md = format_market_analysis(market_data)
                competition_md = format_competition_analysis(competition)
                profit_md = format_profit_analysis(profit)
                swot_md = format_swot_analysis(evaluation.get("swot_analysis", {}))
                risks_md = format_risks_and_factors(
                    evaluation.get("key_risks", []),
                    evaluation.get("success_factors", [])
                )

                # Overall score HTML
                overall_html = format_overall_score(overall_score, recommendation, detail)

                yield (
                    gr.update(value=f"✅ Analysis Complete (Time: {result_data.get('execution_time', 0):.1f}s)"),
                    gr.update(visible=False),
                    gr.update(visible=True),
                    dimension_scores.get("Trend", dimension_scores.get("趋势", 0)),
                    dimension_scores.get("Market", dimension_scores.get("市场", 0)),
                    dimension_scores.get("Competition", dimension_scores.get("竞争", 0)),
                    dimension_scores.get("Profit", dimension_scores.get("利润", 0)),
                    radar,
                    bar,
                    trend_md,
                    market_md,
                    competition_md,
                    profit_md,
                    swot_md,
                    risks_md,
                    overall_html,
                    result_data,
                )

            finally:
                loop.close()

        def on_clear_click():
            """Handle clear button click."""
            return (
                "",  # category
                "",  # keywords
                "US",  # market
                "medium",  # budget
                "amazon_fba",  # model
                gr.update(value="准备就绪"),  # status
                gr.update(visible=False),  # error
                gr.update(visible=False),  # results
                None, None, None, None,  # scores
                None, None,  # charts
                "", "", "", "", "", "",  # details
                "",  # overall
                None,  # state
            )

        # Wire up events
        run_btn.click(
            fn=on_analyze_click,
            inputs=[
                category_input, market_dropdown, budget_radio,
                model_dropdown, keywords_input
            ],
            outputs=[
                status_box, error_box, results_section,
                trend_score_num, market_score_num,
                competition_score_num, profit_score_num,
                radar_chart, bar_chart,
                trend_details, market_details,
                competition_details, profit_details,
                swot_details, risks_factors_details,
                overall_score_html, result_state
            ]
        )

        clear_btn.click(
            fn=on_clear_click,
            outputs=[
                category_input, keywords_input, market_dropdown,
                budget_radio, model_dropdown, status_box,
                error_box, results_section,
                trend_score_num, market_score_num,
                competition_score_num, profit_score_num,
                radar_chart, bar_chart,
                trend_details, market_details,
                competition_details, profit_details,
                swot_details, risks_factors_details,
                overall_score_html, result_state
            ]
        )

    return {
        "category_input": category_input,
        "keywords_input": keywords_input,
        "market_dropdown": market_dropdown,
        "budget_radio": budget_radio,
        "model_dropdown": model_dropdown,
        "run_btn": run_btn,
        "clear_btn": clear_btn,
        "result_state": result_state,
    }
