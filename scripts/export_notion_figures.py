"""Export Notion-ready RewireScope figures from processed real data.

The script uses the same processed tables and visual vocabulary as the
Streamlit dashboard. It intentionally does not simulate or fabricate any
records.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rewirescope.terminal_data import load_terminal_tables
from rewirescope.viz.figures import (
    COLORS,
    FONT_COLOR,
    GRID_COLOR,
    PAPER_BG,
    PLOT_BG,
)


OUTDIR = ROOT / "outputs" / "notion_figures"
TITLE_SIZE = 34
BASE_FONT_SIZE = 24
AXIS_TITLE_SIZE = 24
TICK_SIZE = 20
ANNOTATION_SIZE = 22
FOOTNOTE_SIZE = 18


def _ensure_dirs() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)


def _export(fig: go.Figure, stem: str, width: int = 1800, height: int = 1180) -> dict[str, str]:
    html_path = OUTDIR / f"{stem}.html"
    png_path = OUTDIR / f"{stem}.png"
    fig.write_html(html_path, include_plotlyjs="cdn", full_html=True)
    fig.write_image(png_path, width=width, height=height, scale=2)
    return {"html": str(html_path), "png": str(png_path)}


def _style_export(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(size=TITLE_SIZE, color=FONT_COLOR), x=0.02, xanchor="left"),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, family="Arial, sans-serif", size=BASE_FONT_SIZE),
        legend=dict(font=dict(size=20, color=FONT_COLOR)),
    )
    fig.update_xaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(color=FONT_COLOR),
        title_font=dict(color=FONT_COLOR, size=AXIS_TITLE_SIZE),
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        zerolinecolor=GRID_COLOR,
        tickfont=dict(color=FONT_COLOR),
        title_font=dict(color=FONT_COLOR, size=AXIS_TITLE_SIZE),
    )
    return fig


def _short_taxon(taxon_id: str, limit: int = 28) -> str:
    label = str(taxon_id).replace("_", " ")
    return label if len(label) <= limit else f"{label[: limit - 3]}..."


def _every_other(values: list[str]) -> list[str]:
    if len(values) <= 10:
        return values
    ticks = values[::2]
    if values[-1] not in ticks:
        ticks.append(values[-1])
    return ticks


def _best_transition(signals: pd.DataFrame) -> pd.Series:
    """Pick the strongest observed transition without hand-selecting a result."""

    candidates = signals[signals["allowed_claim_level"] == "observed_rewiring"].copy()
    return candidates.sort_values(
        ["changed_edges", "rewiring_edges", "silent_edge_candidates"],
        ascending=False,
    ).iloc[0]


def _figure_1(tables: dict[str, pd.DataFrame], transition: pd.Series) -> go.Figure:
    edges = tables["transition_edges"]
    df = edges[
        (edges["site_id"] == transition["site_id"])
        & (edges["from_time_bin"] == transition["from_time_bin"])
        & (edges["to_time_bin"] == transition["to_time_bin"])
    ].copy()
    df["rank_weight"] = df[["interaction_count_from", "interaction_count_to"]].max(axis=1)
    display_parts = []
    quotas = {"birth": 16, "death": 16, "persisted": 14}
    for status, quota in quotas.items():
        display_parts.append(
            df[df["edge_status"] == status].sort_values("rank_weight", ascending=False).head(quota)
        )
    plot_df = pd.concat(display_parts, ignore_index=True).sort_values(["edge_status", "rank_weight"])
    plant_load = plot_df.groupby("source_taxon_id")["rank_weight"].sum().sort_values(ascending=False)
    pollinator_load = plot_df.groupby("target_taxon_id")["rank_weight"].sum().sort_values(ascending=False)
    plants = list(plant_load.index)
    pollinators = list(pollinator_load.index)
    pos: dict[str, tuple[float, float]] = {}
    for idx, node in enumerate(plants):
        pos[node] = (0.0, 1 - idx / max(1, len(plants) - 1))
    for idx, node in enumerate(pollinators):
        pos[node] = (1.0, 1 - idx / max(1, len(pollinators) - 1))

    fig = go.Figure()
    max_weight = max(float(plot_df["rank_weight"].max()), 1.0)
    status_order = ["death", "persisted", "birth"]
    for status in status_order:
        subset = plot_df[plot_df["edge_status"] == status]
        for row in subset.itertuples(index=False):
            x0, y0 = pos[row.source_taxon_id]
            x1, y1 = pos[row.target_taxon_id]
            width = max(1.3, 6.0 * math.sqrt(float(row.rank_weight) / max_weight))
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(width=width, color=COLORS[status]),
                    opacity=0.72 if status == "persisted" else 0.88,
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
    fig.add_trace(
        go.Scatter(
            x=[pos[node][0] for node in plants],
            y=[pos[node][1] for node in plants],
            mode="markers",
            marker=dict(size=13, color=COLORS["plant"], line=dict(width=1.2, color="#0B120F")),
            text=[_short_taxon(node, 24) for node in plants],
            hovertemplate="%{text}<extra></extra>",
            name="plants",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[pos[node][0] for node in pollinators],
            y=[pos[node][1] for node in pollinators],
            mode="markers",
            marker=dict(size=13, color=COLORS["pollinator"], line=dict(width=1.2, color="#0B120F")),
            text=[_short_taxon(node, 24) for node in pollinators],
            hovertemplate="%{text}<extra></extra>",
            name="pollinators",
            showlegend=False,
        )
    )
    title = f"Figure 1. Observed weekly rewiring: {transition['from_time_bin']} -> {transition['to_time_bin']}"
    status_counts = plot_df["edge_status"].value_counts().to_dict()
    label_annotations = [
        dict(
            x=-0.025,
            y=pos[node][1],
            xref="x",
            yref="y",
            xanchor="right",
            yanchor="middle",
            text=_short_taxon(node, 26),
            showarrow=False,
            font=dict(color=FONT_COLOR, size=17),
        )
        for node in plants
    ] + [
        dict(
            x=1.025,
            y=pos[node][1],
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="middle",
            text=_short_taxon(node, 26),
            showarrow=False,
            font=dict(color=FONT_COLOR, size=17),
        )
        for node in pollinators
    ]
    fig.update_layout(
        height=1030,
        margin=dict(l=260, r=270, t=115, b=118),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.20, 1.20]),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-0.04, 1.06]),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
        annotations=[
            dict(x=0, y=1.07, text="Plants", showarrow=False, font=dict(color=COLORS["plant"], size=24)),
            dict(x=1, y=1.07, text="Pollinators", showarrow=False, font=dict(color=COLORS["pollinator"], size=24)),
            *label_annotations,
            dict(
                x=0.0,
                y=-0.11,
                xref="paper",
                yref="paper",
                showarrow=False,
                align="left",
                text=(
                    "Data: rmbl_transition_edge_status.csv; top observed edges shown by status "
                    f"(birth {status_counts.get('birth', 0)}, death {status_counts.get('death', 0)}, "
                    f"persisted {status_counts.get('persisted', 0)}); "
                    f"full transition changed edges = {int(transition['changed_edges'])}."
                ),
                font=dict(color="#AFC8B7", size=FOOTNOTE_SIZE),
            ),
        ],
    )
    return _style_export(fig, title)


def _scaled_series(df: pd.DataFrame, col: str) -> pd.Series:
    series = df[col].astype(float)
    min_v = series.min()
    max_v = series.max()
    return (series - min_v) / (max_v - min_v) if max_v != min_v else series * 0


def _figure_2(tables: dict[str, pd.DataFrame], site_id: str, year: int, week: str) -> go.Figure:
    snapshots = tables["snapshots"]
    df = snapshots[(snapshots["site_id"] == site_id) & (snapshots["time_bin"].str.startswith(str(year)))].copy()
    row = snapshots[(snapshots["site_id"] == site_id) & (snapshots["time_bin"] == week)].iloc[0]
    metrics = [
        ("dependency_gini", "Gini", "#6C78FF"),
        ("top10_interaction_share", "Top-10 share", "#FF6248"),
        ("effective_taxa_load", "Effective load", "#50B878"),
        ("connectance", "Connectance", "#9A62D9"),
        ("nestedness_proxy", "Nestedness", "#F2A65A"),
        ("specialization_proxy", "Specialization", "#2ED3E6"),
    ]
    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.64, 0.36],
        specs=[[{"type": "xy"}, {"type": "polar"}]],
        subplot_titles=(
            "Structural signals scaled within selected year",
            f"Selected-week profile: {week}",
        ),
    )
    for col, label, color in metrics:
        fig.add_trace(
            go.Scatter(
                x=df["time_bin"],
                y=_scaled_series(df, col),
                mode="lines+markers",
                name=label,
                line=dict(width=4.0, color=color),
                marker=dict(size=10),
                hovertemplate=f"{label}<br>%{{x}}<br>scaled=%{{y:.3f}}<extra></extra>",
            ),
            row=1,
            col=1,
        )
    radar_metrics = [
        ("dependency_gini", "Gini"),
        ("top10_interaction_share", "Top-10"),
        ("connectance", "Connect."),
        ("nestedness_proxy", "Nested."),
        ("specialization_proxy", "Spec."),
    ]
    r = [float(row[col]) for col, _ in radar_metrics]
    theta = [label for _, label in radar_metrics]
    fig.add_trace(
        go.Scatterpolar(
            r=r + r[:1],
            theta=theta + theta[:1],
            fill="toself",
            name=week,
            line=dict(color=COLORS["silent-edge-failure"], width=4),
            fillcolor="rgba(111, 88, 166, 0.42)",
        ),
        row=1,
        col=2,
    )
    fig.update_layout(
        height=1040,
        margin=dict(l=135, r=82, t=122, b=220),
        legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="left", x=0.0, font=dict(size=19)),
        polar=dict(
            bgcolor=PLOT_BG,
            radialaxis=dict(range=[0, 1], gridcolor=GRID_COLOR, tickfont=dict(size=17, color="#BFD8C8")),
            angularaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=19, color=FONT_COLOR)),
        ),
        annotations=[
            *list(fig.layout.annotations),
            dict(
                x=0.0,
                y=-0.25,
                xref="paper",
                yref="paper",
                showarrow=False,
                align="left",
                text=(
                    "Data: rmbl_network_snapshots.csv and decision_signals.csv; "
                    "concentration is a fragility diagnostic, not a standalone collapse forecast."
                ),
                font=dict(color="#AFC8B7", size=FOOTNOTE_SIZE),
            ),
        ],
    )
    tick_values = _every_other(df["time_bin"].tolist())
    fig.update_xaxes(
        title="Week",
        tickangle=35,
        tickmode="array",
        tickvals=tick_values,
        ticktext=tick_values,
        row=1,
        col=1,
    )
    fig.update_yaxes(title="Scaled value", range=[-0.03, 1.03], row=1, col=1)
    return _style_export(fig, f"Figure 2. Dependency concentration as fragile compensation: {site_id} {year}")


def _figure_3(tables: dict[str, pd.DataFrame], site_id: str, year: int) -> go.Figure:
    windows = tables["phenology_windows"]
    silent = tables["silent"]
    ribbon_df = windows[(windows["site_id"] == site_id) & (windows["year"] == year)].copy()
    ribbon_df = (
        ribbon_df.sort_values("total_observed_load", ascending=False)
        .head(24)
        .sort_values(["guild", "first_sequence", "last_sequence"])
    )
    silent_df = silent[(silent["site_id"] == site_id) & (silent["time_bin"].str.startswith(str(year)))].copy()
    top_plants = silent_df["source_taxon_id"].value_counts().head(16).index
    matrix = (
        silent_df[silent_df["source_taxon_id"].isin(top_plants)]
        .pivot_table(index="source_taxon_id", columns="time_bin", values="target_taxon_id", aggfunc="count", fill_value=0)
        .reindex(top_plants)
    )
    sequence_labels = (
        windows[(windows["site_id"] == site_id) & (windows["year"] == year)][
            ["first_sequence", "first_time_bin"]
        ]
        .drop_duplicates()
        .rename(columns={"first_sequence": "sequence", "first_time_bin": "time_bin"})
    )
    sequence_labels = pd.concat(
        [
            sequence_labels,
            windows[(windows["site_id"] == site_id) & (windows["year"] == year)][
                ["last_sequence", "last_time_bin"]
            ]
            .drop_duplicates()
            .rename(columns={"last_sequence": "sequence", "last_time_bin": "time_bin"}),
        ],
        ignore_index=True,
    ).drop_duplicates()
    sequence_labels = sequence_labels.sort_values("sequence")
    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.52, 0.48],
        horizontal_spacing=0.2,
        specs=[[{"type": "xy"}, {"type": "heatmap"}]],
        subplot_titles=("Observed phenology / activity windows", "Candidate silent-edge flags"),
    )
    for row in ribbon_df.itertuples(index=False):
        color = COLORS["plant"] if row.guild == "plant" else COLORS["pollinator"]
        fig.add_trace(
            go.Scatter(
                x=[row.first_sequence, row.last_sequence],
                y=[row.taxon_id, row.taxon_id],
                mode="lines+markers",
                line=dict(width=8, color=color),
                marker=dict(size=9, color=color),
                showlegend=False,
                hovertemplate=(
                    f"{row.taxon_id}<br>guild={row.guild}<br>"
                    f"{row.first_time_bin} to {row.last_time_bin}<br>"
                    f"basis={row.evidence_basis}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
    fig.add_trace(
        go.Heatmap(
            z=matrix.values,
            x=list(matrix.columns),
            y=list(matrix.index),
            colorscale=[[0, "#102018"], [0.45, "#385747"], [1, COLORS["silent-edge-failure"]]],
            colorbar=dict(
                title=dict(text="candidate<br>flags", font=dict(color=FONT_COLOR, size=20)),
                tickfont=dict(color=FONT_COLOR, size=18),
            ),
            hovertemplate="plant=%{y}<br>week=%{x}<br>candidate flags=%{z}<extra></extra>",
        ),
        row=1,
        col=2,
    )
    fig.update_layout(
        height=1080,
        margin=dict(l=245, r=125, t=122, b=120),
        annotations=list(fig.layout.annotations),
    )
    sequence_ticks = sequence_labels.iloc[::3].copy()
    if not sequence_labels.empty and sequence_labels.iloc[-1]["sequence"] not in set(sequence_ticks["sequence"]):
        sequence_ticks = pd.concat([sequence_ticks, sequence_labels.tail(1)], ignore_index=True)
    fig.update_xaxes(
        title="Week",
        gridcolor=GRID_COLOR,
        tickmode="array",
        tickvals=sequence_ticks["sequence"].tolist(),
        ticktext=sequence_ticks["time_bin"].tolist(),
        tickangle=35,
        tickfont=dict(size=15),
        title_font=dict(size=20),
        row=1,
        col=1,
    )
    ribbon_taxa = ribbon_df["taxon_id"].tolist()
    fig.update_yaxes(
        title="",
        tickmode="array",
        tickvals=ribbon_taxa,
        ticktext=[_short_taxon(taxon, 26) for taxon in ribbon_taxa],
        tickfont=dict(size=16),
        gridcolor="rgba(0,0,0,0)",
        row=1,
        col=1,
    )
    heatmap_ticks = list(matrix.columns)[::3]
    if len(matrix.columns) and matrix.columns[-1] not in heatmap_ticks:
        heatmap_ticks.append(matrix.columns[-1])
    fig.update_xaxes(
        title="Week",
        tickangle=35,
        tickmode="array",
        tickvals=heatmap_ticks,
        ticktext=heatmap_ticks,
        tickfont=dict(size=15),
        title_font=dict(size=20),
        row=1,
        col=2,
    )
    heatmap_taxa = list(matrix.index)
    fig.update_yaxes(
        title="",
        tickmode="array",
        tickvals=heatmap_taxa,
        ticktext=[_short_taxon(taxon, 22) for taxon in heatmap_taxa],
        tickfont=dict(size=15),
        row=1,
        col=2,
    )
    return _style_export(fig, f"Figure 3. Timing windows and silent-edge candidates: {site_id} {year}")


def _legend_markdown(paths: dict[str, dict[str, str]], transition: pd.Series, site_id: str, year: int, week: str) -> str:
    return f"""# RewireScope Notion Figure Exports

Generated from local processed real-data tables. No simulated or placeholder data are used.

## Figure 1 — Observed weekly rewiring in an RMBL plant-pollinator network

PNG: `{paths["figure_1"]["png"]}`  
HTML: `{paths["figure_1"]["html"]}`

**Legend:** Adjacent weekly RMBL plant-pollinator transition for `{transition["site_id"]}`, `{transition["from_time_bin"]}` to `{transition["to_time_bin"]}`, showing observed edge persistence, births, and deaths. Plants are left, pollinators right; line color marks transition status and line weight reflects observed visitation count. This supports the claim that ecological risk can emerge as moving interaction architecture before species inventories visibly fail. Evidence boundary: observed RMBL rewiring only; source table: `rmbl_transition_edge_status.csv`.

## Figure 2 — Dependency concentration as fragile compensation

PNG: `{paths["figure_2"]["png"]}`  
HTML: `{paths["figure_2"]["html"]}`

**Legend:** Weekly RMBL structural diagnostics for `{site_id}` in `{year}` show dependency Gini, top-10 interaction share, effective taxa load, connectance, nestedness, and specialization, with `{week}` summarized as a radar profile. The figure supports the claim that rewiring is not automatically resilience: apparent continuity can mask compensatory-but-fragile concentration into fewer taxa or pathways. Evidence boundary: real RMBL network metrics; source table: `rmbl_network_snapshots.csv`.

## Figure 3 — Temporal execution and candidate silent-edge failure

PNG: `{paths["figure_3"]["png"]}`  
HTML: `{paths["figure_3"]["html"]}`

**Legend:** RMBL flowering windows and pollinator activity windows are paired with candidate silent-edge flags: historically observed plant-pollinator pairs absent in a site-week despite plant flowering and pollinator activity elsewhere. The figure supports the timing claim that species co-presence is insufficient; an edge must execute within the right phenological window to remain functional. Evidence boundary: candidate screening signal only, not proof of causal interaction extinction; source tables: `rmbl_phenology_windows.csv` and `rmbl_silent_edge_candidates.csv`.
"""


def main() -> None:
    _ensure_dirs()
    tables = load_terminal_tables()
    transition = _best_transition(tables["signals"])
    site_id = str(transition["site_id"])
    year = int(str(transition["to_time_bin"])[:4])
    week = str(transition["to_time_bin"])

    figs = {
        "figure_1": _figure_1(tables, transition),
        "figure_2": _figure_2(tables, site_id, year, week),
        "figure_3": _figure_3(tables, site_id, year),
    }
    paths = {
        key: _export(fig, f"rewirescope_{key}")
        for key, fig in figs.items()
    }
    manifest = {
        "selection_rule": "Figure 1 uses the observed transition with highest changed_edges; Figures 2 and 3 use the same site-year context.",
        "site_id": site_id,
        "year": year,
        "selected_week": week,
        "transition": {
            "from_time_bin": str(transition["from_time_bin"]),
            "to_time_bin": str(transition["to_time_bin"]),
            "changed_edges": int(transition["changed_edges"]),
            "rewiring_edges": int(transition["rewiring_edges"]),
            "species_turnover_edges": int(transition["species_turnover_edges"]),
            "classification": str(transition["classification"]),
        },
        "exports": paths,
    }
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (OUTDIR / "notion_figure_legends.md").write_text(_legend_markdown(paths, transition, site_id, year, week))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
