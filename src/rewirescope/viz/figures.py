"""Plotly figures for the RewireScope app."""

from __future__ import annotations

import math

import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from rewirescope.networks.bipartite import build_bipartite_graph


COLORS = {
    "plant": "#2F6F4E",
    "pollinator": "#B76825",
    "edge": "rgba(184, 203, 190, 0.22)",
    "persisted": "#48535B",
    "birth": "#2F6F4E",
    "death": "#9B3A32",
    "green": "#2F6F4E",
    "yellow": "#C28B1D",
    "red": "#9B3A32",
    "adaptive": "#2F6F4E",
    "compensatory-but-fragile": "#C28B1D",
    "degradative": "#9B3A32",
    "candidate-silent-edge-failure": "#5B4B8A",
    "silent-edge-failure": "#5B4B8A",
    "unresolved": "#6E7781",
}

SERIES_COLORS = ["#59C89A", "#F07A5A", "#71B7FF", "#C28B1D", "#9B8CFF", "#22D3EE"]

TEMPLATE = "plotly_dark"
PAPER_BG = "rgba(0,0,0,0)"
PLOT_BG = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(210, 232, 217, 0.18)"
FONT_COLOR = "#DDF3E4"


def _sequence_to_time_bin(sequence: int | float) -> str:
    value = int(sequence)
    return f"{value // 100}-W{value % 100:02d}"


def _short_taxon(label: str, limit: int = 34) -> str:
    text = str(label)
    return text if len(text) <= limit else f"{text[: limit - 1]}..."


def empty_figure(title: str = "No data for current filter") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=title, x=0.5, y=0.5, showarrow=False, font=dict(size=14, color="#6E7781"))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=35, b=10),
        template=TEMPLATE,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def metric_timeseries(snapshots: pd.DataFrame, site_id: str, year: int) -> go.Figure:
    df = snapshots[(snapshots["site_id"] == site_id) & (snapshots["time_bin"].str.startswith(str(year)))]
    if df.empty:
        return empty_figure()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time_bin"], y=df["edges_n"], mode="lines+markers", name="Edges"))
    fig.add_trace(
        go.Scatter(
            x=df["time_bin"],
            y=df["dependency_gini"],
            mode="lines+markers",
            name="Dependency Gini",
            yaxis="y2",
        )
    )
    fig.update_layout(
        height=340,
        margin=dict(l=54, r=56, t=72, b=42),
        template=TEMPLATE,
        title="Network Movement",
        yaxis=dict(title="Edges"),
        yaxis2=dict(title="Gini", overlaying="y", side="right", range=[0, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig


def transition_decomposition(signals: pd.DataFrame, site_id: str, year: int) -> go.Figure:
    df = signals[(signals["site_id"] == site_id) & (signals["from_time_bin"].str.startswith(str(year)))]
    if df.empty:
        return empty_figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["to_time_bin"], y=df["rewiring_edges"], name="Rewiring among persistent taxa"))
    fig.add_trace(go.Bar(x=df["to_time_bin"], y=df["species_turnover_edges"], name="Species-turnover component"))
    fig.update_layout(
        barmode="stack",
        height=330,
        margin=dict(l=54, r=18, t=78, b=46),
        template=TEMPLATE,
        title="Why Edges Changed",
        yaxis_title="Changed edges",
        legend=dict(orientation="h", yanchor="bottom", y=1.15, xanchor="right", x=1),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig


def classification_strip(signals: pd.DataFrame, site_id: str, year: int) -> go.Figure:
    df = signals[(signals["site_id"] == site_id) & (signals["from_time_bin"].str.startswith(str(year)))].copy()
    if df.empty:
        return empty_figure()
    df["signal_row"] = "decision signal"
    fig = px.scatter(
        df,
        x="to_time_bin",
        y="signal_row",
        color="classification",
        color_discrete_map=COLORS,
        hover_data=["edge_turnover", "rewiring_ratio", "evidence_summary"],
    )
    fig.update_traces(marker=dict(size=16, symbol="square"))
    fig.update_layout(
        height=160,
        margin=dict(l=10, r=10, t=42, b=28),
        template=TEMPLATE,
        title="Weekly Decision Signals",
        yaxis_title="",
        xaxis_title="",
        showlegend=False,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    return fig


def edge_persistence_heatmap(interactions: pd.DataFrame, site_id: str, year: int, max_edges: int = 80) -> go.Figure:
    df = interactions[(interactions["site_id"] == site_id) & (interactions["time_bin"].str.startswith(str(year)))]
    if df.empty:
        return empty_figure()
    df = df.copy()
    df["edge"] = df["source_taxon_id"] + " | " + df["target_taxon_id"]
    edge_order = (
        df.groupby("edge")["interaction_count"].sum().sort_values(ascending=False).head(max_edges).index
    )
    matrix = (
        df[df["edge"].isin(edge_order)]
        .pivot_table(index="edge", columns="time_bin", values="interaction_count", aggfunc="sum", fill_value=0)
        .reindex(edge_order)
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=(matrix.values > 0).astype(int),
            x=list(matrix.columns),
            y=list(matrix.index),
            colorscale=[[0, "#0d1712"], [0.35, "#1f3b31"], [1, "#59C89A"]],
            showscale=False,
        )
    )
    fig.update_layout(
        height=520,
        margin=dict(l=178, r=16, t=52, b=70),
        template=TEMPLATE,
        title="Edge Persistence",
        xaxis_title="Week",
        yaxis_title="Observed edge",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(tickangle=35, tickfont=dict(size=10), gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(tickfont=dict(size=9), automargin=True)
    return fig


def network_snapshot(interactions: pd.DataFrame, site_id: str, time_bin: str, top_edges: int = 90) -> go.Figure:
    df = interactions[(interactions["site_id"] == site_id) & (interactions["time_bin"] == time_bin)]
    if df.empty:
        return empty_figure()
    df = (
        df.groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"]
        .sum()
        .sort_values("interaction_count", ascending=False)
        .head(top_edges)
    )
    graph = build_bipartite_graph(df)
    plants = sorted([n for n, d in graph.nodes(data=True) if d["guild"] == "plant"])
    pollinators = sorted([n for n, d in graph.nodes(data=True) if d["guild"] == "pollinator"])
    pos = {}
    for idx, node in enumerate(plants):
        y = 1 - idx / max(1, len(plants) - 1)
        pos[node] = (0, y)
    for idx, node in enumerate(pollinators):
        y = 1 - idx / max(1, len(pollinators) - 1)
        pos[node] = (1, y)
    edge_traces = []
    max_weight = max([d["weight"] for _, _, d in graph.edges(data=True)] or [1])
    for source, target, data in graph.edges(data=True):
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_traces.append(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=max(0.6, 4 * math.sqrt(data["weight"] / max_weight)), color=COLORS["edge"]),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    node_x, node_y, node_color, node_text = [], [], [], []
    for node, data in graph.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_color.append(COLORS[data["guild"]])
        node_text.append(node)
    fig = go.Figure(edge_traces)
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker=dict(size=9, color=node_color, line=dict(width=0.5, color="#1f2933")),
            text=node_text,
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
    )
    fig.update_layout(
        height=620,
        margin=dict(l=24, r=24, t=58, b=24),
        template=TEMPLATE,
        title=f"Observed Plant-Pollinator Network: {time_bin}",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.08, 1.08]),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
        annotations=[
            dict(x=0, y=1.07, text="Plants", showarrow=False, font=dict(color=COLORS["plant"], size=13)),
            dict(x=1, y=1.07, text="Pollinators", showarrow=False, font=dict(color=COLORS["pollinator"], size=13)),
        ],
    )
    return fig


def burkle_contrast_bars(contrast: pd.DataFrame) -> go.Figure:
    if contrast.empty:
        return empty_figure()
    counts = contrast["edge_status"].value_counts().rename_axis("edge_status").reset_index(name="n")
    fig = px.bar(counts, x="edge_status", y="n", color="edge_status", color_discrete_map={
        "persisted": "#2F6F4E",
        "lost": "#9B3A32",
        "novel_contemporary": "#C28B1D",
    })
    fig.update_layout(
        height=340,
        margin=dict(l=54, r=18, t=60, b=46),
        template=TEMPLATE,
        title="Historical Contrast Edge Status",
        xaxis_title="",
        yaxis_title="Edges",
        showlegend=False,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig


def evidence_gate_matrix(registry: pd.DataFrame) -> go.Figure:
    if registry.empty:
        return empty_figure()
    cols = ["observed_pairwise_edges", "repeated_time_bins", "raw_interaction_counts"]
    labels = ["Pairwise<br>edges", "Repeated<br>time bins", "Raw<br>counts"]
    matrix = []
    text = []
    for _, row in registry.iterrows():
        values = []
        txt = []
        for col in cols:
            value = row.get(col)
            if value is True:
                values.append(2)
                txt.append("yes")
            elif value is False:
                values.append(0)
                txt.append("no")
            else:
                values.append(1)
                txt.append("pending")
        matrix.append(values)
        text.append(txt)
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=labels,
            y=registry["dataset_id"],
            text=text,
            texttemplate="%{text}",
            textfont=dict(size=12, color="#F4FFF5"),
            colorscale=[[0, COLORS["red"]], [0.5, COLORS["yellow"]], [1, COLORS["green"]]],
            showscale=False,
            hovertemplate="dataset=%{y}<br>gate=%{x}<br>status=%{text}<extra></extra>",
        )
    )
    fig.update_layout(
        height=310,
        margin=dict(l=170, r=18, t=48, b=82),
        template=TEMPLATE,
        title="Evidence Gate Matrix",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
        xaxis_title="",
        yaxis_title="",
        xaxis=dict(tickangle=0, tickfont=dict(size=11), side="bottom"),
        yaxis=dict(tickfont=dict(size=12)),
    )
    return fig


def transition_diff_network(
    transition_edges: pd.DataFrame,
    site_id: str,
    from_time_bin: str,
    to_time_bin: str,
    max_edges: int = 140,
) -> go.Figure:
    df = transition_edges[
        (transition_edges["site_id"] == site_id)
        & (transition_edges["from_time_bin"] == from_time_bin)
        & (transition_edges["to_time_bin"] == to_time_bin)
    ].copy()
    if df.empty:
        return empty_figure()
    df["rank_weight"] = df[["interaction_count_from", "interaction_count_to"]].max(axis=1)
    df = df.sort_values(["edge_status", "rank_weight"], ascending=[True, False]).head(max_edges)
    plants = sorted(df["source_taxon_id"].unique())
    pollinators = sorted(df["target_taxon_id"].unique())
    pos = {}
    for idx, node in enumerate(plants):
        pos[node] = (0, 1 - idx / max(1, len(plants) - 1))
    for idx, node in enumerate(pollinators):
        pos[node] = (1, 1 - idx / max(1, len(pollinators) - 1))
    fig = go.Figure()
    max_weight = max(float(df["rank_weight"].max()), 1.0)
    status_order = ["death", "persisted", "birth"]
    for status in status_order:
        subset = df[df["edge_status"] == status]
        for row in subset.itertuples(index=False):
            x0, y0 = pos[row.source_taxon_id]
            x1, y1 = pos[row.target_taxon_id]
            width = max(0.7, 4.0 * math.sqrt(float(row.rank_weight) / max_weight))
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(width=width, color=COLORS[status]),
                    opacity=0.78 if status == "persisted" else 0.9,
                    name=status,
                    legendgroup=status,
                    showlegend=not any(trace.name == status for trace in fig.data),
                    hovertemplate=(
                        f"{row.source_taxon_id} -> {row.target_taxon_id}<br>"
                        f"status={status}<br>"
                        f"from={row.interaction_count_from}<br>"
                        f"to={row.interaction_count_to}<extra></extra>"
                    ),
                )
            )
    node_x, node_y, node_color, node_text = [], [], [], []
    for node in plants:
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_color.append(COLORS["plant"])
        node_text.append(node)
    for node in pollinators:
        node_x.append(pos[node][0])
        node_y.append(pos[node][1])
        node_color.append(COLORS["pollinator"])
        node_text.append(node)
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            marker=dict(size=9, color=node_color, line=dict(width=0.5, color="#1f2933")),
            text=node_text,
            hovertemplate="%{text}<extra></extra>",
            name="taxa",
            showlegend=False,
        )
    )
    fig.update_layout(
        height=620,
        margin=dict(l=24, r=24, t=84, b=24),
        template=TEMPLATE,
        title=f"Observed Transition Diff: {from_time_bin} -> {to_time_bin}",
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.08, 1.08]),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.13, xanchor="right", x=1),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
        annotations=[
            dict(x=0, y=1.07, text="Plants", showarrow=False, font=dict(color=COLORS["plant"], size=13)),
            dict(x=1, y=1.07, text="Pollinators", showarrow=False, font=dict(color=COLORS["pollinator"], size=13)),
        ],
    )
    return fig


def phenology_ribbons(
    windows: pd.DataFrame,
    site_id: str,
    year: int | None = None,
    guild: str | None = None,
    top_n: int = 50,
) -> go.Figure:
    df = windows[windows["site_id"] == site_id].copy()
    if year is not None and "year" in df.columns:
        df = df[df["year"] == year]
    if guild:
        df = df[df["guild"] == guild]
    if df.empty:
        return empty_figure()
    df = df.sort_values("total_observed_load", ascending=False).head(top_n)
    df = df.sort_values(["guild", "first_sequence", "last_sequence"])
    min_seq = int(df["first_sequence"].min())
    max_seq = int(df["last_sequence"].max())
    week_labels = [_sequence_to_time_bin(seq) for seq in range(min_seq, max_seq + 1)]
    tick_labels = week_labels[:: max(1, len(week_labels) // 8)]
    if week_labels and week_labels[-1] not in tick_labels:
        tick_labels.append(week_labels[-1])
    fig = go.Figure()
    for row in df.itertuples(index=False):
        color = COLORS["plant"] if row.guild == "plant" else COLORS["pollinator"]
        fig.add_trace(
            go.Scatter(
                x=[row.first_time_bin, row.last_time_bin],
                y=[_short_taxon(row.taxon_id), _short_taxon(row.taxon_id)],
                mode="lines+markers",
                line=dict(width=7, color=color),
                marker=dict(size=7, color=color),
                hovertemplate=(
                    f"{row.taxon_id}<br>guild={row.guild}<br>"
                    f"{row.first_time_bin} to {row.last_time_bin}<br>"
                    f"basis={row.evidence_basis}<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.update_layout(
        height=max(340, min(900, 120 + 18 * len(df))),
        margin=dict(l=174, r=16, t=56, b=66),
        template=TEMPLATE,
        title="Observed Phenology / Activity Windows",
        xaxis_title="Week",
        yaxis_title="Taxon",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=week_labels,
        tickmode="array",
        tickvals=tick_labels,
        ticktext=tick_labels,
        tickangle=0,
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
    )
    fig.update_yaxes(automargin=True, tickfont=dict(size=10))
    return fig


def silent_edge_heatmap(silent: pd.DataFrame, site_id: str, year: int, max_plants: int = 40) -> go.Figure:
    df = silent[(silent["site_id"] == site_id) & (silent["time_bin"].str.startswith(str(year)))].copy()
    if df.empty:
        return empty_figure("No candidate silent-edge flags for current filter")
    top_plants = df["source_taxon_id"].value_counts().head(max_plants).index
    matrix = (
        df[df["source_taxon_id"].isin(top_plants)]
        .pivot_table(index="source_taxon_id", columns="time_bin", values="target_taxon_id", aggfunc="count", fill_value=0)
        .reindex(top_plants)
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=list(matrix.columns),
            y=list(matrix.index),
            colorscale=[[0, "#0d1712"], [0.45, "#2d4738"], [1, COLORS["candidate-silent-edge-failure"]]],
            colorbar=dict(title="candidate<br>flags"),
        )
    )
    fig.update_layout(
        height=520,
        margin=dict(l=146, r=18, t=56, b=66),
        template=TEMPLATE,
        title="Candidate Flags by Flowering Plant",
        xaxis_title="Week",
        yaxis_title="Plant",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(tickangle=35, tickfont=dict(size=10), gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(tickfont=dict(size=10), automargin=True)
    return fig


def taxon_load_rank_bars(
    taxon_load: pd.DataFrame,
    site_id: str,
    time_bin: str,
    guild: str | None = None,
    top_n: int = 20,
) -> go.Figure:
    df = taxon_load[(taxon_load["site_id"] == site_id) & (taxon_load["time_bin"] == time_bin)].copy()
    if guild:
        df = df[df["guild"] == guild]
    if df.empty:
        return empty_figure()
    df = df.sort_values("interaction_load", ascending=False).head(top_n).sort_values("interaction_load")
    fig = px.bar(
        df,
        x="interaction_load",
        y="taxon_id",
        color="guild",
        orientation="h",
        color_discrete_map={"plant": COLORS["plant"], "pollinator": COLORS["pollinator"]},
        hover_data=["time_bin", "site_id"],
    )
    fig.update_layout(
        height=max(320, min(700, 120 + 24 * len(df))),
        margin=dict(l=172, r=18, t=78, b=54),
        template=TEMPLATE,
        title=f"Observed Interaction Load: {time_bin}",
        xaxis_title="Interaction load",
        yaxis_title="Taxon",
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(automargin=True, tickfont=dict(size=10))
    return fig


def concentration_small_multiples(snapshots: pd.DataFrame, site_id: str, year: int) -> go.Figure:
    df = snapshots[(snapshots["site_id"] == site_id) & (snapshots["time_bin"].str.startswith(str(year)))]
    if df.empty:
        return empty_figure()
    metrics = [
        ("dependency_gini", "Dependency Gini", SERIES_COLORS[0]),
        ("top10_interaction_share", "Top-10 Share", SERIES_COLORS[1]),
        ("effective_taxa_load", "Effective Load", SERIES_COLORS[2]),
        ("connectance", "Connectance", SERIES_COLORS[3]),
        ("nestedness_proxy", "Nestedness", SERIES_COLORS[4]),
        ("specialization_proxy", "Specialization", SERIES_COLORS[5]),
    ]
    fig = make_subplots(
        rows=len(metrics),
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.045,
        subplot_titles=[label for _, label, _ in metrics],
    )
    for idx, (col, label, color) in enumerate(metrics, start=1):
        series = df[col].astype(float)
        min_v = series.min()
        max_v = series.max()
        scaled = (series - min_v) / (max_v - min_v) if max_v != min_v else series * 0
        fig.add_trace(
            go.Scatter(
                x=df["time_bin"],
                y=scaled,
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=2.2),
                marker=dict(size=5, color=color),
                showlegend=False,
                hovertemplate=f"{label}<br>%{{x}}<br>scaled=%{{y:.3f}}<extra></extra>",
            ),
            row=idx,
            col=1,
        )
        fig.update_yaxes(range=[-0.05, 1.05], showticklabels=False, row=idx, col=1)
    fig.update_layout(
        height=520,
        margin=dict(l=38, r=22, t=76, b=58),
        template=TEMPLATE,
        title="Structural Signal Small Multiples",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_annotations(font=dict(size=11, color=FONT_COLOR), x=0.0, xanchor="left")
    fig.update_xaxes(tickangle=35, tickfont=dict(size=10), gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_xaxes(title_text="Week", row=len(metrics), col=1)
    return fig


def concentration_radar(snapshots: pd.DataFrame, site_id: str, time_bin: str) -> go.Figure:
    row = snapshots[(snapshots["site_id"] == site_id) & (snapshots["time_bin"] == time_bin)]
    if row.empty:
        return empty_figure()
    row = row.iloc[0]
    metrics = [
        "dependency_gini",
        "top10_interaction_share",
        "connectance",
        "nestedness_proxy",
        "specialization_proxy",
    ]
    values = [float(row[m]) for m in metrics]
    labels = ["Gini", "Top-10", "Connect.", "Nested.", "Spec."]
    fig = go.Figure(
        data=go.Scatterpolar(
            r=values + values[:1],
            theta=labels + labels[:1],
            fill="toself",
            line=dict(color=COLORS["candidate-silent-edge-failure"]),
            name=time_bin,
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=78, r=78, t=58, b=58),
        template=TEMPLATE,
        title=f"Structural Profile: {time_bin}",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
        polar=dict(
            bgcolor=PLOT_BG,
            domain=dict(x=[0.16, 0.84], y=[0.04, 0.86]),
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(size=10, color="#BFD8C8"),
                gridcolor=GRID_COLOR,
                linecolor=GRID_COLOR,
            ),
            angularaxis=dict(tickfont=dict(size=11, color=FONT_COLOR), gridcolor=GRID_COLOR, linecolor=GRID_COLOR),
        ),
        showlegend=False,
    )
    return fig


def burkle_contrast_network(contrast: pd.DataFrame, statuses: list[str] | None = None, max_edges: int = 180) -> go.Figure:
    df = contrast.copy()
    if statuses:
        df = df[df["edge_status"].isin(statuses)]
    if df.empty:
        return empty_figure()
    degree_taxa = pd.concat([df["source_taxon_id"], df["target_taxon_id"]]).value_counts()
    df = df.assign(
        source_degree=df["source_taxon_id"].map(degree_taxa),
        target_degree=df["target_taxon_id"].map(degree_taxa),
        status_order=df["edge_status"].map({"lost": 0, "persisted": 1, "novel_contemporary": 2}).fillna(9),
    )
    df = df.sort_values(["source_degree", "target_degree", "status_order"], ascending=[False, False, True]).head(max_edges)
    plants = df["source_taxon_id"].value_counts().head(34).index.tolist()
    bees = df["target_taxon_id"].value_counts().head(34).index.tolist()
    df = df[df["source_taxon_id"].isin(plants) & df["target_taxon_id"].isin(bees)].copy()

    code = {"lost": -1, "persisted": 0, "novel_contemporary": 1}
    matrix = pd.DataFrame(float("nan"), index=plants, columns=bees)
    text = pd.DataFrame("", index=plants, columns=bees)
    for row in df.itertuples(index=False):
        matrix.loc[row.source_taxon_id, row.target_taxon_id] = code.get(row.edge_status, 0)
        text.loc[row.source_taxon_id, row.target_taxon_id] = row.edge_status

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=[_short_taxon(v, 24) for v in matrix.columns],
            y=[_short_taxon(v, 28) for v in matrix.index],
            text=text.values,
            colorscale=[
                [0.0, COLORS["death"]],
                [0.49, COLORS["death"]],
                [0.50, COLORS["green"]],
                [0.74, COLORS["green"]],
                [0.75, COLORS["yellow"]],
                [1.0, COLORS["yellow"]],
            ],
            zmin=-1,
            zmax=1,
            showscale=False,
            hovertemplate="plant=%{y}<br>pollinator=%{x}<br>status=%{text}<extra></extra>",
        )
    )
    fig.update_layout(
        height=620,
        margin=dict(l=178, r=22, t=66, b=132),
        template=TEMPLATE,
        title="Burkle Contrast Edge Matrix (partial contrast)",
        xaxis_title="Pollinator",
        yaxis_title="Plant",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=11),
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(size=9), automargin=True)
    fig.update_yaxes(tickfont=dict(size=9), automargin=True)
    return fig


def burkle_overlap_histogram(phenology: pd.DataFrame) -> go.Figure:
    if phenology.empty:
        return empty_figure()
    fig = px.histogram(
        phenology,
        x="overlap_delta_days",
        color="edge_status",
        barmode="overlay",
        opacity=0.72,
        color_discrete_map={"lost": COLORS["death"], "persisted": COLORS["green"]},
        title="Phenological Overlap Change on Historical/Reconstructed Edges",
    )
    fig.update_layout(
        template=TEMPLATE,
        height=390,
        margin=dict(l=54, r=18, t=76, b=48),
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="right", x=1),
        xaxis_title="Overlap delta days",
        yaxis_title="Edges",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR)
    return fig
