"""
Chart components for the UI.

This module provides Plotly chart builders for visualizations.
"""
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px

from ..utils.theme import THEME_COLORS


def create_radar_chart(
    scores: Dict[str, int],
    title: str = "维度分析",
    color: Optional[str] = None
) -> go.Figure:
    """
    Create a radar chart for dimension scores.

    Args:
        scores: Dictionary of dimension names to scores
        title: Chart title
        color: Optional fill color

    Returns:
        Plotly Figure
    """
    categories = list(scores.keys())
    values = list(scores.values())

    # Check if we have valid data before creating chart
    if not categories or not values:
        # Return empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="暂无分析数据",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=title,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )
        return fig

    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fill_color = color or THEME_COLORS["primary"]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor=f'rgba({int(fill_color[1:3], 16)}, {int(fill_color[3:5], 16)}, {int(fill_color[5:7], 16)}, 0.3)',
        line=dict(color=fill_color, width=2),
        name='分数'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20', '40', '60', '80', '100'],
                gridcolor='#e2e8f0',
            ),
            angularaxis=dict(
                gridcolor='#e2e8f0',
            ),
            bgcolor='white',
        ),
        showlegend=False,
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1e293b')
        ),
        margin=dict(l=60, r=60, t=60, b=60),
        paper_bgcolor='white',
    )

    return fig


def create_bar_chart(
    scores: Dict[str, int],
    title: str = "分数对比"
) -> go.Figure:
    """
    Create a horizontal bar chart for scores.

    Args:
        scores: Dictionary of dimension names to scores
        title: Chart title

    Returns:
        Plotly Figure
    """
    categories = list(scores.keys())
    values = list(scores.values())

    # Assign colors based on score values
    colors = []
    for score in values:
        if score >= 70:
            colors.append(THEME_COLORS["score_high"])
        elif score >= 50:
            colors.append(THEME_COLORS["score_medium"])
        else:
            colors.append(THEME_COLORS["score_low"])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(width=0)
        ),
        text=[f'{v}' for v in values],
        textposition='outside',
        textfont=dict(size=12, color='#1e293b')
    ))

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1e293b')
        ),
        xaxis=dict(
            range=[0, 110],
            title='分数',
            gridcolor='#e2e8f0',
            zeroline=False,
        ),
        yaxis=dict(
            title='',
            autorange='reversed',
        ),
        margin=dict(l=100, r=40, t=60, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
    )

    return fig


def create_comparison_radar(
    analysis_a: Dict[str, int],
    analysis_b: Dict[str, int],
    name_a: str = "分析 A",
    name_b: str = "分析 B",
    title: str = "对比分析"
) -> go.Figure:
    """
    Create an overlaid radar chart for comparing two analyses.

    Args:
        analysis_a: First analysis scores
        analysis_b: Second analysis scores
        name_a: Name for first analysis
        name_b: Name for second analysis
        title: Chart title

    Returns:
        Plotly Figure
    """
    categories = list(analysis_a.keys())

    # Close the polygons
    categories_closed = categories + [categories[0]]
    values_a = list(analysis_a.values()) + [list(analysis_a.values())[0]]
    values_b = list(analysis_b.values()) + [list(analysis_b.values())[0]]

    fig = go.Figure()

    # First analysis trace
    fig.add_trace(go.Scatterpolar(
        r=values_a,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.2)',
        line=dict(color=THEME_COLORS["primary"], width=2),
        name=name_a
    ))

    # Second analysis trace
    fig.add_trace(go.Scatterpolar(
        r=values_b,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(139, 92, 246, 0.2)',
        line=dict(color=THEME_COLORS["secondary"], width=2),
        name=name_b
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                gridcolor='#e2e8f0',
            ),
            angularaxis=dict(
                gridcolor='#e2e8f0',
            ),
            bgcolor='white',
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1e293b')
        ),
        margin=dict(l=60, r=60, t=60, b=80),
        paper_bgcolor='white',
    )

    return fig


def create_score_gauge(
    score: int,
    title: str = "机会评分",
    max_value: int = 100
) -> go.Figure:
    """
    Create a gauge chart for displaying a single score.

    Args:
        score: Score value
        title: Chart title
        max_value: Maximum score value

    Returns:
        Plotly Figure
    """
    # Determine color based on score
    if score >= 70:
        bar_color = THEME_COLORS["score_high"]
    elif score >= 50:
        bar_color = THEME_COLORS["score_medium"]
    else:
        bar_color = THEME_COLORS["score_low"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#1e293b'}},
        number={'font': {'size': 48, 'color': '#1e293b'}},
        gauge={
            'axis': {
                'range': [0, max_value],
                'tickwidth': 1,
                'tickcolor': '#e2e8f0',
                'tickvals': [0, 25, 50, 75, 100],
            },
            'bar': {'color': bar_color, 'thickness': 0.8},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#e2e8f0',
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 70], 'color': '#fef9c3'},
                {'range': [70, 100], 'color': '#dcfce7'},
            ],
            'threshold': {
                'line': {'color': '#1e293b', 'width': 2},
                'thickness': 0.8,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=20),
        height=250,
    )

    return fig


def create_trend_chart(
    data: List[Dict[str, Any]],
    title: str = "趋势分析"
) -> go.Figure:
    """
    Create a line chart for trend data.

    Args:
        data: List of data points with 'date' and 'value' keys
        title: Chart title

    Returns:
        Plotly Figure
    """
    if not data:
        # Return empty chart
        fig = go.Figure()
        fig.update_layout(
            title=dict(text=title, x=0.5),
            annotations=[dict(
                text="暂无数据",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=16, color='#64748b')
            )]
        )
        return fig

    dates = [d.get('date', '') for d in data]
    values = [d.get('value', 0) for d in data]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode='lines+markers',
        line=dict(color=THEME_COLORS["primary"], width=2),
        marker=dict(size=6, color=THEME_COLORS["primary"]),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)',
    ))

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1e293b')
        ),
        xaxis=dict(
            title='日期',
            gridcolor='#e2e8f0',
        ),
        yaxis=dict(
            title='数值',
            gridcolor='#e2e8f0',
        ),
        margin=dict(l=60, r=40, t=60, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
    )

    return fig


def create_pie_chart(
    data: Dict[str, float],
    title: str = "分布图"
) -> go.Figure:
    """
    Create a pie chart for distribution data.

    Args:
        data: Dictionary of labels to values
        title: Chart title

    Returns:
        Plotly Figure
    """
    labels = list(data.keys())
    values = list(data.values())

    colors = [
        THEME_COLORS["primary"],
        THEME_COLORS["secondary"],
        THEME_COLORS["accent"],
        THEME_COLORS["score_high"],
        THEME_COLORS["score_medium"],
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors[:len(labels)]),
        textinfo='label+percent',
        textfont=dict(size=12),
    )])

    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, color='#1e293b')
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
    )

    return fig
