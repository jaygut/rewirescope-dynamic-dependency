"""Shared Streamlit UI primitives for the RewireScope terminal."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st


CLASS_ORDER = [
    "adaptive",
    "compensatory-but-fragile",
    "degradative",
    "silent-edge-failure",
    "unresolved",
]


def apply_terminal_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.05rem; padding-bottom: 2rem; max-width: 1560px;}
        h1, h2, h3 {letter-spacing: 0 !important;}
        h1 {line-height: 1.02 !important; margin-bottom: 0.65rem !important;}
        h2, h3 {line-height: 1.12 !important;}
        div[data-testid="stMetric"] {
            background: #102018;
            border: 1px solid #2c4738;
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
        }
        div[data-testid="stMetricLabel"] p {
            font-size: 0.74rem;
            color: #d6ecd9 !important;
            white-space: normal;
            overflow-wrap: anywhere;
        }
        div[data-testid="stMetricValue"] {
            color: #f1fff5 !important;
            font-size: 2rem;
            overflow-wrap: anywhere;
        }
        .rs-metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
            gap: 0.72rem;
            margin: 0.65rem 0 1rem 0;
        }
        .rs-metric-card {
            min-height: 86px;
            background: #102018;
            border: 1px solid #2c4738;
            border-radius: 8px;
            padding: 0.78rem 0.86rem;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
        }
        .rs-metric-label {
            color: #d9f1dd;
            font-size: 0.76rem;
            font-weight: 680;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }
        .rs-metric-value {
            color: #f3fff6;
            font-size: 2rem;
            font-weight: 670;
            line-height: 1.04;
            margin-top: 0.44rem;
            overflow-wrap: anywhere;
        }
        .rs-metric-help {
            color: #91aa99;
            font-size: 0.66rem;
            line-height: 1.16;
            margin-top: 0.35rem;
            overflow-wrap: anywhere;
        }
        .rs-thesis {
            border: 1px solid #d9e3de;
            border-left: 7px solid #2f6f4e;
            background: linear-gradient(90deg, #f7faf8, #ffffff);
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }
        .rs-thesis-title {font-size: 1.8rem; font-weight: 760; color: #1f302b; margin-bottom: 0.25rem;}
        .rs-thesis-sub {font-size: 0.98rem; color: #48535b;}
        .rs-callout {
            border: 1px solid #eadfc8;
            background: #fffaf0;
            color: #3d3321;
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin: 0.5rem 0 1rem 0;
        }
        .rs-small {font-size: 0.82rem; color: #647067;}
        div[data-testid="stDataFrame"] {
            border-radius: 8px;
            overflow: hidden;
        }
        .stPlotlyChart {
            margin-top: 0.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def thesis_banner() -> None:
    st.markdown(
        """
        <div class="rs-thesis">
            <div class="rs-thesis-title">Nature is not declining in place. It is changing shape.</div>
            <div class="rs-thesis-sub">
            RewireScope reads composition + topology + timing + environmental forcing + rewiring as one evidence-gated dependency system.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def boundary_callout(text: str) -> None:
    st.markdown(f'<div class="rs-callout">{text}</div>', unsafe_allow_html=True)


def metric_strip(metrics: list[tuple[str, str, str]]) -> None:
    cards = []
    for label, value, help_text in metrics:
        cards.append(
            "<div class=\"rs-metric-card\">"
            f"<div class=\"rs-metric-label\">{escape(str(label))}</div>"
            f"<div class=\"rs-metric-value\">{escape(str(value))}</div>"
            f"<div class=\"rs-metric-help\">{escape(str(help_text))}</div>"
            "</div>"
        )
    st.markdown(
        f"<div class=\"rs-metric-grid\">{''.join(cards)}</div>",
        unsafe_allow_html=True,
    )


def evidence_gate_rail(registry: pd.DataFrame) -> None:
    view = registry[
        [
            "dataset_id",
            "allowed_claim_level",
            "rebuild_network_snapshots",
            "visualize_rewiring_events",
        ]
    ].rename(
        columns={
            "dataset_id": "dataset",
            "allowed_claim_level": "claim",
            "rebuild_network_snapshots": "network snapshots",
            "visualize_rewiring_events": "rewiring events",
        }
    )
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        height=214,
        column_config={
            "dataset": st.column_config.TextColumn("dataset", width="medium"),
            "claim": st.column_config.TextColumn("claim", width="medium"),
            "network snapshots": st.column_config.TextColumn("network snapshots", width="small"),
            "rewiring events": st.column_config.TextColumn("rewiring events", width="small"),
        },
    )


def source_note(table: str, columns: str) -> None:
    st.caption(f"Data source: `{table}` | columns: {columns}")


def classification_counts(signals: pd.DataFrame) -> pd.DataFrame:
    counts = signals["classification"].value_counts().reindex(CLASS_ORDER, fill_value=0)
    return counts.rename_axis("classification").reset_index(name="transitions")
