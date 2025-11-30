"""
Comparison tab for the Gradio UI.

This module provides the comparison analysis interface.
"""
import gradio as gr
from typing import Dict, Any, List, Optional

from ..handlers.history_handlers import (
    get_history_for_dropdown,
    get_entry_by_index,
)
from ..components.charts import create_comparison_radar, create_bar_chart


def create_comparison_tab():
    """
    Create the Comparison tab layout.

    Returns:
        Dictionary of component references
    """
    with gr.Tab("⚖️ Comparison", id="compare"):
        gr.Markdown("""
        ## Comparison Analysis

        Select two historical analysis results to compare and understand the differences between different products or markets.
        """)

        # Selection Row
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Analysis A")
                analysis_a = gr.Dropdown(
                    choices=[],
                    label="Select First Analysis",
                    info="Choose from history"
                )
                summary_a = gr.Markdown("*Please select an analysis*")

            with gr.Column():
                gr.Markdown("### Analysis B")
                analysis_b = gr.Dropdown(
                    choices=[],
                    label="Select Second Analysis",
                    info="Choose from history"
                )
                summary_b = gr.Markdown("*Please select an analysis*")

        # Refresh and Compare buttons
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh List", scale=1)
            compare_btn = gr.Button("📊 Start Comparison", variant="primary", scale=2)

        # Comparison Results (initially hidden)
        with gr.Column(visible=False) as comparison_results:
            gr.Markdown("---")
            gr.Markdown("## Comparison Results")

            # Comparison Chart
            comparison_chart = gr.Plot(label="Radar Chart Comparison")

            # Score Comparison Table
            gr.Markdown("### Score Comparison")
            comparison_table = gr.Dataframe(
                headers=["Dimension", "Analysis A", "Analysis B", "Difference", "Winner"],
                datatype=["str", "number", "number", "number", "str"],
                interactive=False
            )

            # Summary
            comparison_summary = gr.Markdown()

        # State for storing selections
        state_a = gr.State(value=None)
        state_b = gr.State(value=None)

        # Event handlers
        def refresh_dropdown_options():
            """Refresh the dropdown options."""
            options = get_history_for_dropdown()
            return (
                gr.update(choices=options),
                gr.update(choices=options)
            )

        def on_select_a(selection):
            """Handle selection of analysis A."""
            if not selection:
                return "*Please select an analysis*", None

            # Parse index from selection
            try:
                options = get_history_for_dropdown()
                idx = options.index(selection)
                entry = get_entry_by_index(idx)

                if entry and entry.get("state") and entry["state"].get("evaluation_result"):
                    eval_result = entry["state"]["evaluation_result"]
                    score = eval_result.get("opportunity_score", 0)
                    rec = eval_result.get("recommendation", "N/A").upper()
                    category = entry.get("request", {}).get("category", "N/A")

                    summary = f"""
**Product**: {category}
**Score**: {score}/100
**Recommendation**: {rec}
"""
                    return summary, entry
                else:
                    return "*Incomplete data*", entry

            except Exception as e:
                return f"*Loading failed: {str(e)}*", None

        def on_select_b(selection):
            """Handle selection of analysis B."""
            if not selection:
                return "*Please select an analysis*", None

            try:
                options = get_history_for_dropdown()
                idx = options.index(selection)
                entry = get_entry_by_index(idx)

                if entry and entry.get("state") and entry["state"].get("evaluation_result"):
                    eval_result = entry["state"]["evaluation_result"]
                    score = eval_result.get("opportunity_score", 0)
                    rec = eval_result.get("recommendation", "N/A").upper()
                    category = entry.get("request", {}).get("category", "N/A")

                    summary = f"""
**Product**: {category}
**Score**: {score}/100
**Recommendation**: {rec}
"""
                    return summary, entry
                else:
                    return "*Incomplete data*", entry

            except Exception as e:
                return f"*Loading failed: {str(e)}*", None

        def on_compare(entry_a, entry_b):
            """Perform comparison between two analyses."""
            if not entry_a or not entry_b:
                return (
                    gr.update(visible=False),
                    None,
                    [],
                    "Please select two analyses to compare"
                )

            try:
                # Extract scores
                state_a_data = entry_a.get("state", {})
                state_b_data = entry_b.get("state", {})

                scores_a = {}
                scores_b = {}

                # Trend
                if state_a_data.get("trend_analysis"):
                    scores_a["Trend"] = state_a_data["trend_analysis"].trend_score
                if state_b_data.get("trend_analysis"):
                    scores_b["Trend"] = state_b_data["trend_analysis"].trend_score

                # Market
                if state_a_data.get("market_analysis"):
                    scores_a["Market"] = state_a_data["market_analysis"].market_score
                if state_b_data.get("market_analysis"):
                    scores_b["Market"] = state_b_data["market_analysis"].market_score

                # Competition
                if state_a_data.get("competition_analysis"):
                    scores_a["Competition"] = state_a_data["competition_analysis"].competition_score
                if state_b_data.get("competition_analysis"):
                    scores_b["Competition"] = state_b_data["competition_analysis"].competition_score

                # Profit
                if state_a_data.get("profit_analysis"):
                    scores_a["Profit"] = state_a_data["profit_analysis"].profit_score
                if state_b_data.get("profit_analysis"):
                    scores_b["Profit"] = state_b_data["profit_analysis"].profit_score

                # Get names
                name_a = entry_a.get("request", {}).get("category", "Analysis A") if entry_a.get("request") else "Analysis A"
                name_b = entry_b.get("request", {}).get("category", "Analysis B") if entry_b.get("request") else "Analysis B"

                # Create comparison chart
                chart = create_comparison_radar(scores_a, scores_b, name_a, name_b, "Dimension Comparison")

                # Create comparison table
                table_data = []
                for dim in ["Trend", "Market", "Competition", "Profit"]:
                    score_a = scores_a.get(dim, 0)
                    score_b = scores_b.get(dim, 0)
                    diff = score_a - score_b
                    winner = name_a if diff > 0 else (name_b if diff < 0 else "Tie")
                    table_data.append([dim, score_a, score_b, diff, winner])

                # Overall scores
                eval_a = state_a_data.get("evaluation_result")
                eval_b = state_b_data.get("evaluation_result")

                # Defensive access - handle both dict and object
                if eval_a:
                    overall_a = eval_a.get("opportunity_score", 0) if isinstance(eval_a, dict) else eval_a.opportunity_score
                else:
                    overall_a = 0

                if eval_b:
                    overall_b = eval_b.get("opportunity_score", 0) if isinstance(eval_b, dict) else eval_b.opportunity_score
                else:
                    overall_b = 0
                overall_diff = overall_a - overall_b
                overall_winner = name_a if overall_diff > 0 else (name_b if overall_diff < 0 else "Tie")
                table_data.append(["Overall", overall_a, overall_b, overall_diff, overall_winner])

                # Summary
                if overall_diff > 10:
                    summary = f"### Comparison Conclusion\n\n**{name_a}** performs better overall, with an opportunity score {abs(overall_diff)} points higher."
                elif overall_diff < -10:
                    summary = f"### Comparison Conclusion\n\n**{name_b}** performs better overall, with an opportunity score {abs(overall_diff)} points higher."
                else:
                    summary = f"### Comparison Conclusion\n\nBoth products have similar opportunity scores (difference of {abs(overall_diff)} points). Selection depends on specific circumstances."

                return (
                    gr.update(visible=True),
                    chart,
                    table_data,
                    summary
                )

            except Exception as e:
                return (
                    gr.update(visible=False),
                    None,
                    [],
                    f"Comparison failed: {str(e)}"
                )

        # Wire events
        refresh_btn.click(
            fn=refresh_dropdown_options,
            outputs=[analysis_a, analysis_b]
        )

        analysis_a.change(
            fn=on_select_a,
            inputs=[analysis_a],
            outputs=[summary_a, state_a]
        )

        analysis_b.change(
            fn=on_select_b,
            inputs=[analysis_b],
            outputs=[summary_b, state_b]
        )

        compare_btn.click(
            fn=on_compare,
            inputs=[state_a, state_b],
            outputs=[comparison_results, comparison_chart, comparison_table, comparison_summary]
        )

    return {
        "analysis_a": analysis_a,
        "analysis_b": analysis_b,
        "compare_btn": compare_btn,
    }
