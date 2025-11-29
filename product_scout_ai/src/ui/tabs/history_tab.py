"""
History tab for the Gradio UI.

This module provides the history browsing interface.
"""
import gradio as gr
import pandas as pd
from typing import Dict, Any

from ..handlers.history_handlers import (
    get_history_dataframe,
    get_history_statistics,
    clear_history,
)


# Market filter options
MARKET_FILTER_OPTIONS = ["全部", "US", "EU", "UK", "CA", "AU", "JP", "DE", "FR"]


def create_history_tab():
    """
    Create the History tab layout.

    Returns:
        Dictionary of component references
    """
    with gr.Tab("📋 历史记录", id="history"):
        gr.Markdown("""
        ## 分析历史

        查看过去的产品分析记录，支持按类别和市场筛选。
        """)

        # Statistics Row
        with gr.Row():
            total_stat = gr.Number(label="总分析数", precision=0, interactive=False)
            success_stat = gr.Number(label="成功次数", precision=0, interactive=False)
            rate_stat = gr.Number(label="成功率 (%)", precision=1, interactive=False)
            avg_time_stat = gr.Number(label="平均耗时 (s)", precision=1, interactive=False)

        gr.Markdown("---")

        # Filters Row
        with gr.Row():
            category_filter = gr.Textbox(
                label="按类别筛选",
                placeholder="输入关键词...",
                max_lines=1,
                scale=2
            )
            market_filter = gr.Dropdown(
                choices=MARKET_FILTER_OPTIONS,
                value="全部",
                label="按市场筛选",
                scale=1
            )
            success_filter = gr.Checkbox(
                label="仅显示成功",
                value=False,
                scale=1
            )
            refresh_btn = gr.Button("🔄 刷新", scale=1)

        # History Table
        history_table = gr.Dataframe(
            headers=["日期", "产品类别", "市场", "模式", "评分", "建议", "耗时", "状态"],
            datatype=["str", "str", "str", "str", "number", "str", "str", "str"],
            interactive=False,
            wrap=True,
            label="历史记录"
        )

        # Actions Row
        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空历史", variant="stop")
            clear_confirm = gr.Markdown(visible=False)

        # Event handlers
        def load_history(category: str, market: str, success_only: bool):
            """Load history with filters."""
            df = get_history_dataframe(category, market, success_only)
            stats = get_history_statistics()

            return (
                stats["total"],
                stats["successful"],
                stats["success_rate"] * 100 if stats["success_rate"] else 0,
                stats["avg_time"],
                df
            )

        def on_clear_history():
            """Clear all history."""
            count = clear_history()
            df = get_history_dataframe()
            stats = get_history_statistics()

            return (
                stats["total"],
                stats["successful"],
                stats["success_rate"] * 100 if stats["success_rate"] else 0,
                stats["avg_time"],
                df,
                gr.update(visible=True, value=f"✅ 已清除 {count} 条记录")
            )

        # Initial load on tab select
        def on_tab_select():
            """Load data when tab is selected."""
            return load_history("", "全部", False)

        # Wire events
        refresh_btn.click(
            fn=load_history,
            inputs=[category_filter, market_filter, success_filter],
            outputs=[total_stat, success_stat, rate_stat, avg_time_stat, history_table]
        )

        category_filter.change(
            fn=load_history,
            inputs=[category_filter, market_filter, success_filter],
            outputs=[total_stat, success_stat, rate_stat, avg_time_stat, history_table]
        )

        market_filter.change(
            fn=load_history,
            inputs=[category_filter, market_filter, success_filter],
            outputs=[total_stat, success_stat, rate_stat, avg_time_stat, history_table]
        )

        success_filter.change(
            fn=load_history,
            inputs=[category_filter, market_filter, success_filter],
            outputs=[total_stat, success_stat, rate_stat, avg_time_stat, history_table]
        )

        clear_btn.click(
            fn=on_clear_history,
            outputs=[total_stat, success_stat, rate_stat, avg_time_stat, history_table, clear_confirm]
        )

    return {
        "category_filter": category_filter,
        "market_filter": market_filter,
        "success_filter": success_filter,
        "history_table": history_table,
        "refresh_btn": refresh_btn,
    }
