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
    with gr.Tab("⚖️ 对比分析", id="compare"):
        gr.Markdown("""
        ## 对比分析

        选择两个历史分析结果进行对比，直观了解不同产品或市场的差异。
        """)

        # Selection Row
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 分析 A")
                analysis_a = gr.Dropdown(
                    choices=[],
                    label="选择第一个分析",
                    info="从历史记录中选择"
                )
                summary_a = gr.Markdown("*请选择一个分析*")

            with gr.Column():
                gr.Markdown("### 分析 B")
                analysis_b = gr.Dropdown(
                    choices=[],
                    label="选择第二个分析",
                    info="从历史记录中选择"
                )
                summary_b = gr.Markdown("*请选择一个分析*")

        # Refresh and Compare buttons
        with gr.Row():
            refresh_btn = gr.Button("🔄 刷新列表", scale=1)
            compare_btn = gr.Button("📊 开始对比", variant="primary", scale=2)

        # Comparison Results (initially hidden)
        with gr.Column(visible=False) as comparison_results:
            gr.Markdown("---")
            gr.Markdown("## 对比结果")

            # Comparison Chart
            comparison_chart = gr.Plot(label="雷达图对比")

            # Score Comparison Table
            gr.Markdown("### 评分对比")
            comparison_table = gr.Dataframe(
                headers=["维度", "分析 A", "分析 B", "差异", "优势方"],
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
                return "*请选择一个分析*", None

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
**产品**: {category}
**评分**: {score}/100
**建议**: {rec}
"""
                    return summary, entry
                else:
                    return "*数据不完整*", entry

            except Exception as e:
                return f"*加载失败: {str(e)}*", None

        def on_select_b(selection):
            """Handle selection of analysis B."""
            if not selection:
                return "*请选择一个分析*", None

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
**产品**: {category}
**评分**: {score}/100
**建议**: {rec}
"""
                    return summary, entry
                else:
                    return "*数据不完整*", entry

            except Exception as e:
                return f"*加载失败: {str(e)}*", None

        def on_compare(entry_a, entry_b):
            """Perform comparison between two analyses."""
            if not entry_a or not entry_b:
                return (
                    gr.update(visible=False),
                    None,
                    [],
                    "请选择两个分析进行对比"
                )

            try:
                # Extract scores
                state_a_data = entry_a.get("state", {})
                state_b_data = entry_b.get("state", {})

                scores_a = {}
                scores_b = {}

                # Trend
                if state_a_data.get("trend_analysis"):
                    scores_a["趋势"] = state_a_data["trend_analysis"].trend_score
                if state_b_data.get("trend_analysis"):
                    scores_b["趋势"] = state_b_data["trend_analysis"].trend_score

                # Market
                if state_a_data.get("market_analysis"):
                    scores_a["市场"] = state_a_data["market_analysis"].market_score
                if state_b_data.get("market_analysis"):
                    scores_b["市场"] = state_b_data["market_analysis"].market_score

                # Competition
                if state_a_data.get("competition_analysis"):
                    scores_a["竞争"] = state_a_data["competition_analysis"].competition_score
                if state_b_data.get("competition_analysis"):
                    scores_b["竞争"] = state_b_data["competition_analysis"].competition_score

                # Profit
                if state_a_data.get("profit_analysis"):
                    scores_a["利润"] = state_a_data["profit_analysis"].profit_score
                if state_b_data.get("profit_analysis"):
                    scores_b["利润"] = state_b_data["profit_analysis"].profit_score

                # Get names
                name_a = entry_a.get("request", {}).get("category", "分析 A") if entry_a.get("request") else "分析 A"
                name_b = entry_b.get("request", {}).get("category", "分析 B") if entry_b.get("request") else "分析 B"

                # Create comparison chart
                chart = create_comparison_radar(scores_a, scores_b, name_a, name_b, "维度对比")

                # Create comparison table
                table_data = []
                for dim in ["趋势", "市场", "竞争", "利润"]:
                    score_a = scores_a.get(dim, 0)
                    score_b = scores_b.get(dim, 0)
                    diff = score_a - score_b
                    winner = name_a if diff > 0 else (name_b if diff < 0 else "相同")
                    table_data.append([dim, score_a, score_b, diff, winner])

                # Overall scores
                eval_a = state_a_data.get("evaluation_result")
                eval_b = state_b_data.get("evaluation_result")

                overall_a = eval_a.opportunity_score if eval_a else 0
                overall_b = eval_b.opportunity_score if eval_b else 0
                overall_diff = overall_a - overall_b
                overall_winner = name_a if overall_diff > 0 else (name_b if overall_diff < 0 else "相同")
                table_data.append(["总分", overall_a, overall_b, overall_diff, overall_winner])

                # Summary
                if overall_diff > 10:
                    summary = f"### 对比结论\n\n**{name_a}** 整体表现更优，机会评分高出 {abs(overall_diff)} 分。"
                elif overall_diff < -10:
                    summary = f"### 对比结论\n\n**{name_b}** 整体表现更优，机会评分高出 {abs(overall_diff)} 分。"
                else:
                    summary = f"### 对比结论\n\n两个产品的机会评分相近（差异 {abs(overall_diff)} 分），需要根据具体情况选择。"

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
                    f"对比失败: {str(e)}"
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
