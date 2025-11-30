"""
Export tab for the Gradio UI.

This module provides the export functionality interface.
"""
import gradio as gr
from typing import Dict, Any, Optional
import tempfile
import os

from ..handlers.history_handlers import get_history_for_dropdown, get_entry_by_index
from ..handlers.export_handlers import get_export_preview, export_analysis
from ..handlers.analysis_handlers import convert_result_to_dict


# Export format options
FORMAT_OPTIONS = ["JSON", "Markdown", "Summary"]


def create_export_tab():
    """
    Create the Export tab layout.

    Returns:
        Dictionary of component references
    """
    with gr.Tab("📤 Export Report", id="export"):
        gr.Markdown("""
        ## Export Analysis Report

        Export analysis results as JSON or Markdown format for easy sharing and archiving.
        """)

        # Selection Row
        with gr.Row():
            with gr.Column(scale=2):
                analysis_select = gr.Dropdown(
                    choices=[],
                    label="Select Analysis to Export",
                    info="Choose an analysis from history"
                )
            with gr.Column(scale=1):
                refresh_btn = gr.Button("🔄 Refresh List")

        # Export Options
        with gr.Row():
            format_radio = gr.Radio(
                choices=FORMAT_OPTIONS,
                value="Markdown",
                label="Export Format",
                info="Select the export file format"
            )

        # Action Buttons
        with gr.Row():
            preview_btn = gr.Button("👁️ Preview", scale=1)
            export_btn = gr.Button("📥 Download", variant="primary", scale=2)

        # Preview Section
        gr.Markdown("### Preview")
        preview_content = gr.Code(
            label="Export Preview",
            language="markdown",
            interactive=False,
            lines=20
        )

        # Download output (hidden file component)
        download_file = gr.File(label="Download File", visible=False)

        # State for selected entry
        selected_entry = gr.State(value=None)

        # Event handlers
        def refresh_options():
            """Refresh dropdown options."""
            options = get_history_for_dropdown()
            return gr.update(choices=options)

        def on_select(selection):
            """Handle analysis selection."""
            if not selection:
                return None

            try:
                options = get_history_for_dropdown()
                idx = options.index(selection)
                entry = get_entry_by_index(idx)
                return entry
            except Exception:
                return None

        def on_preview(entry, format_type):
            """Generate preview."""
            if not entry:
                return "Please select an analysis first"

            try:
                # Convert entry to result dict format
                result_data = {
                    "success": entry.get("success", False),
                    "execution_time": entry.get("execution_time", 0),
                }

                if entry.get("request"):
                    req = entry["request"]
                    result_data["request"] = {
                        "category": req.category if hasattr(req, 'category') else req.get("category"),
                        "target_market": req.target_market if hasattr(req, 'target_market') else req.get("target_market"),
                        "budget_range": req.budget_range if hasattr(req, 'budget_range') else req.get("budget_range"),
                        "business_model": req.business_model if hasattr(req, 'business_model') else req.get("business_model"),
                    }

                state = entry.get("state")
                if state:
                    # Trend Analysis
                    if hasattr(state, 'trend_analysis') and state.trend_analysis:
                        ta = state.trend_analysis
                        result_data["trend_analysis"] = {
                            "trend_score": ta.trend_score,
                            "trend_direction": ta.trend_direction,
                            "seasonality": ta.seasonality,
                            "related_queries": ta.related_queries,
                        }

                    # Market Analysis
                    if hasattr(state, 'market_analysis') and state.market_analysis:
                        ma = state.market_analysis
                        result_data["market_analysis"] = {
                            "market_score": ma.market_score,
                            "market_size": ma.market_size,
                            "growth_rate": ma.growth_rate,
                            "customer_segments": ma.customer_segments,
                            "maturity_level": ma.maturity_level,
                        }

                    # Competition Analysis
                    if hasattr(state, 'competition_analysis') and state.competition_analysis:
                        ca = state.competition_analysis
                        result_data["competition_analysis"] = {
                            "competition_score": ca.competition_score,
                            "competitors": ca.competitors,
                            "pricing_analysis": ca.pricing_analysis,
                            "opportunities": ca.opportunities,
                        }

                    # Profit Analysis
                    if hasattr(state, 'profit_analysis') and state.profit_analysis:
                        pa = state.profit_analysis
                        result_data["profit_analysis"] = {
                            "profit_score": pa.profit_score,
                            "unit_economics": pa.unit_economics,
                            "margins": pa.margins,
                            "monthly_projection": pa.monthly_projection,
                            "investment": pa.investment,
                            "assessment": pa.assessment,
                        }

                    # Evaluation Result
                    if hasattr(state, 'evaluation_result') and state.evaluation_result:
                        er = state.evaluation_result
                        result_data["evaluation_result"] = {
                            "opportunity_score": er.opportunity_score,
                            "dimension_scores": er.dimension_scores,
                            "swot_analysis": er.swot_analysis,
                            "recommendation": er.recommendation,
                            "recommendation_detail": er.recommendation_detail,
                            "key_risks": er.key_risks,
                            "success_factors": er.success_factors,
                        }

                # Map format type
                fmt_map = {"JSON": "JSON", "Markdown": "Markdown", "Summary": "Summary"}
                fmt = fmt_map.get(format_type, "Markdown")

                content = get_export_preview(result_data, fmt)
                return content

            except Exception as e:
                return f"Preview generation failed: {str(e)}"

        def on_export(entry, format_type):
            """Export and create download file."""
            if not entry:
                return gr.update(visible=False)

            try:
                # Convert entry to result dict
                result_data = {}

                if entry.get("request"):
                    req = entry["request"]
                    result_data["request"] = {
                        "category": req.category if hasattr(req, 'category') else req.get("category"),
                        "target_market": req.target_market if hasattr(req, 'target_market') else req.get("target_market"),
                        "budget_range": req.budget_range if hasattr(req, 'budget_range') else req.get("budget_range"),
                        "business_model": req.business_model if hasattr(req, 'business_model') else req.get("business_model"),
                    }

                state = entry.get("state")
                if state:
                    if hasattr(state, 'trend_analysis') and state.trend_analysis:
                        ta = state.trend_analysis
                        result_data["trend_analysis"] = {
                            "trend_score": ta.trend_score,
                            "trend_direction": ta.trend_direction,
                        }
                    if hasattr(state, 'market_analysis') and state.market_analysis:
                        ma = state.market_analysis
                        result_data["market_analysis"] = {
                            "market_score": ma.market_score,
                            "growth_rate": ma.growth_rate,
                            "maturity_level": ma.maturity_level,
                        }
                    if hasattr(state, 'competition_analysis') and state.competition_analysis:
                        ca = state.competition_analysis
                        result_data["competition_analysis"] = {
                            "competition_score": ca.competition_score,
                            "entry_barriers": getattr(ca, 'entry_barriers', 'medium'),
                        }
                    if hasattr(state, 'profit_analysis') and state.profit_analysis:
                        pa = state.profit_analysis
                        result_data["profit_analysis"] = {
                            "profit_score": pa.profit_score,
                        }
                    if hasattr(state, 'evaluation_result') and state.evaluation_result:
                        er = state.evaluation_result
                        result_data["evaluation_result"] = {
                            "opportunity_score": er.opportunity_score,
                            "recommendation": er.recommendation,
                            "recommendation_detail": er.recommendation_detail,
                            "swot_analysis": er.swot_analysis,
                            "key_risks": er.key_risks,
                            "success_factors": er.success_factors,
                        }

                # Map format type
                fmt_map = {"JSON": "JSON", "Markdown": "Markdown", "Summary": "Summary"}
                fmt = fmt_map.get(format_type, "Markdown")

                content, filename = export_analysis(result_data, fmt)

                # Create temp file
                suffix = ".json" if fmt == "JSON" else (".md" if fmt == "Markdown" else ".txt")
                with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
                    f.write(content)
                    temp_path = f.name

                return gr.update(value=temp_path, visible=True)

            except Exception as e:
                return gr.update(visible=False)

        # Wire events
        refresh_btn.click(
            fn=refresh_options,
            outputs=[analysis_select]
        )

        analysis_select.change(
            fn=on_select,
            inputs=[analysis_select],
            outputs=[selected_entry]
        )

        preview_btn.click(
            fn=on_preview,
            inputs=[selected_entry, format_radio],
            outputs=[preview_content]
        )

        export_btn.click(
            fn=on_export,
            inputs=[selected_entry, format_radio],
            outputs=[download_file]
        )

    return {
        "analysis_select": analysis_select,
        "format_radio": format_radio,
        "preview_btn": preview_btn,
        "export_btn": export_btn,
    }
