from __future__ import annotations

import pandas as pd
import plotly.express as px


def make_y_label(unit: str) -> str:
    if unit == "%":
        return "Percent (%)"
    if unit:
        return unit
    return "Value"


def make_date_formats(frequency: str, df: pd.DataFrame) -> tuple[str, str]:
    frequency_text = str(frequency).lower()
    if not frequency_text and "frequency" in df.columns:
        normalized_frequencies = {
            str(value).lower() for value in df["frequency"].dropna().unique() if str(value).strip()
        }
        if len(normalized_frequencies) == 1:
            frequency_text = normalized_frequencies.pop()

    if "month" in frequency_text:
        return "%b %Y", "%b\n%Y"
    return "%d %b %Y", "%b\n%Y"


def build_line_chart(df: pd.DataFrame, chart_title: str, unit: str, frequency: str):
    hover_date_format, tick_date_format = make_date_formats(frequency, df)

    fig = px.line(
        df,
        x="date",
        y="value",
        color="series_name",
        title=chart_title,
        template="plotly_white",
    )

    fig.update_traces(
        line=dict(width=3),
        hovertemplate=(
            "<b>%{fullData.name}</b><br>"
            f"Date: %{{x|{hover_date_format}}}<br>"
            "Value: %{y}<extra></extra>"
        ),
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=make_y_label(unit),
        hovermode="x unified",
        font=dict(color="black", size=14),
        title=dict(font=dict(color="black", size=22), x=0.02, xanchor="left"),
        legend=dict(
            title=None,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="black", size=12),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=80, b=20),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#333333",
            font=dict(color="black", size=13),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#D9D9D9",
        linecolor="black",
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
        tickformat=tick_date_format,
        hoverformat=hover_date_format,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#D9D9D9",
        zeroline=False,
        linecolor="black",
        tickfont=dict(color="black"),
        title_font=dict(color="black"),
    )

    return fig
