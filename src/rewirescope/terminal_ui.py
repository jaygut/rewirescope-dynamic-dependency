"""Shared Streamlit UI primitives for the RewireScope terminal."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st


CLASS_ORDER = [
    "adaptive",
    "compensatory-but-fragile",
    "degradative",
    "candidate-silent-edge-failure",
    "unresolved",
]

CLASS_LABELS = {
    "adaptive": "adaptive",
    "compensatory-but-fragile": "compensatory-but-fragile",
    "degradative": "degradative",
    "candidate-silent-edge-failure": "candidate silent-edge failure",
    "silent-edge-failure": "candidate silent-edge failure",
    "unresolved": "unresolved",
}

CLAIM_LABELS = {
    "observed_rewiring": "observed rewiring",
    "partial_contrast": "partial contrast",
    "inferred_dependency": "inferred dependency",
    "metrics_only": "metrics only",
}

CLAIM_CLASSES = {
    "observed_rewiring": "green",
    "partial_contrast": "yellow",
    "inferred_dependency": "red",
    "metrics_only": "gray",
}


def apply_terminal_style() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 0.85rem; padding-bottom: 2rem; max-width: 1560px;}
        [data-testid="stSidebar"] {min-width: 17rem !important;}
        [data-testid="stSidebarNav"] {padding-top: 0.6rem;}
        [data-testid="stToolbar"], .stDeployButton, header [data-testid="stToolbar"] {
            visibility: hidden !important;
            height: 0 !important;
        }
        h1, h2, h3 {letter-spacing: 0 !important;}
        h1 {font-size: 2.1rem !important; line-height: 1.02 !important; margin-bottom: 0.48rem !important;}
        h2 {font-size: 1.55rem !important; margin-top: 1.1rem !important;}
        h3 {font-size: 1.15rem !important;}
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
            overflow-wrap: normal;
            word-break: keep-all;
        }
        div[data-testid="stMetricValue"] {
            color: #f1fff5 !important;
            font-size: 2rem;
            overflow-wrap: normal;
            word-break: keep-all;
            hyphens: none;
        }
        .rs-metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(164px, 1fr));
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
            overflow: hidden;
        }
        .rs-metric-card.rs-candidate-card {
            border-color: #c28b1d;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035), 0 0 0 1px rgba(194, 139, 29, 0.16);
        }
        .rs-metric-label {
            color: #d9f1dd;
            font-size: 0.76rem;
            font-weight: 680;
            line-height: 1.2;
            overflow-wrap: normal;
            word-break: keep-all;
        }
        .rs-metric-value {
            color: #f3fff6;
            font-size: 2rem;
            font-weight: 670;
            line-height: 1.04;
            margin-top: 0.44rem;
            overflow-wrap: normal;
            word-break: keep-all;
            hyphens: none;
            white-space: nowrap;
        }
        .rs-metric-value--text {
            font-size: 1.15rem;
            line-height: 1.16;
            white-space: normal;
            overflow-wrap: break-word;
        }
        .rs-metric-help {
            color: #91aa99;
            font-size: 0.66rem;
            line-height: 1.16;
            margin-top: 0.35rem;
            overflow-wrap: normal;
            word-break: keep-all;
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
            background: #f8f1e3;
            color: #362f21;
            border-radius: 8px;
            padding: 0.9rem 1rem;
            margin: 0.5rem 0 1rem 0;
        }
        .rs-callout-dark {
            border: 1px solid #2f4e3e;
            background: #0f1b15;
            color: #d9f1dd;
            border-radius: 8px;
            padding: 0.86rem 1rem;
            margin: 0.5rem 0 1rem 0;
        }
        .rs-small {font-size: 0.82rem; color: #647067;}
        .rs-claim-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.72rem;
            margin: 0.6rem 0 1rem 0;
        }
        .rs-claim-card {
            min-height: 96px;
            background: #102018;
            border: 1px solid #2c4738;
            border-radius: 8px;
            padding: 0.82rem 0.88rem;
            overflow: hidden;
        }
        .rs-claim-title {
            color: #f0fff4;
            font-size: 0.88rem;
            line-height: 1.2;
            font-weight: 760;
            margin-bottom: 0.38rem;
            word-break: keep-all;
            hyphens: none;
        }
        .rs-claim-copy {
            color: #a7bdae;
            font-size: 0.76rem;
            line-height: 1.28;
        }
        .rs-pill {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            max-width: 100%;
            border-radius: 999px;
            padding: 0.2rem 0.52rem;
            font-size: 0.78rem;
            font-weight: 760;
            line-height: 1.1;
            white-space: nowrap;
            word-break: keep-all;
            hyphens: none;
        }
        .rs-pill-green {background: rgba(47, 111, 78, 0.18); color: #bff1cd; border: 1px solid rgba(47, 111, 78, 0.7);}
        .rs-pill-yellow {background: rgba(194, 139, 29, 0.18); color: #f5d58b; border: 1px solid rgba(194, 139, 29, 0.75);}
        .rs-pill-red {background: rgba(155, 58, 50, 0.20); color: #f1b8ad; border: 1px solid rgba(155, 58, 50, 0.78);}
        .rs-pill-purple {background: rgba(91, 75, 138, 0.23); color: #d4c7ff; border: 1px solid rgba(119, 101, 184, 0.78);}
        .rs-pill-gray {background: rgba(110, 119, 129, 0.22); color: #d5dee6; border: 1px solid rgba(125, 137, 148, 0.72);}
        .rs-module-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.86rem;
            margin-top: 0.6rem;
        }
        .rs-module-card {
            background: #102018;
            border: 1px solid #2c4738;
            border-radius: 8px;
            min-height: 142px;
            padding: 0.95rem 1rem;
        }
        .rs-module-title {
            color: #f3fff6;
            font-weight: 760;
            font-size: 1rem;
            margin: 0.42rem 0 0.36rem 0;
        }
        .rs-module-copy {
            color: #a7bdae;
            font-size: 0.8rem;
            line-height: 1.32;
        }
        .rs-ghost-panel {
            border: 1px dashed #466656;
            border-radius: 8px;
            background:
                linear-gradient(90deg, rgba(47, 111, 78, 0.08) 1px, transparent 1px),
                linear-gradient(rgba(47, 111, 78, 0.08) 1px, transparent 1px),
                #0d1712;
            background-size: 28px 28px;
            min-height: 240px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.2rem;
            margin: 0.55rem 0 1rem 0;
        }
        .rs-ghost-inner {
            max-width: 760px;
            text-align: center;
        }
        .rs-ghost-title {
            color: #f3fff6;
            font-weight: 760;
            font-size: 1.05rem;
            margin-bottom: 0.4rem;
        }
        .rs-ghost-copy {
            color: #a7bdae;
            font-size: 0.86rem;
            line-height: 1.38;
        }
        @media (max-width: 980px) {
            .rs-claim-grid, .rs-module-grid {grid-template-columns: repeat(2, minmax(0, 1fr));}
        }
        @media (max-width: 640px) {
            .rs-claim-grid, .rs-module-grid {grid-template-columns: 1fr;}
        }
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


def quiet_callout(text: str) -> None:
    st.markdown(f'<div class="rs-callout-dark">{text}</div>', unsafe_allow_html=True)


def claim_label(value: str) -> str:
    return CLAIM_LABELS.get(str(value), str(value).replace("_", " "))


def classification_label(value: str) -> str:
    return CLASS_LABELS.get(str(value), str(value).replace("_", " "))


def claim_pill(value: str) -> str:
    raw = str(value).replace(" ", "_")
    color = CLAIM_CLASSES.get(raw, "gray")
    return f'<span class="rs-pill rs-pill-{color}">{escape(claim_label(raw))}</span>'


def classification_pill(value: str) -> str:
    raw = str(value)
    color = {
        "adaptive": "green",
        "compensatory-but-fragile": "yellow",
        "degradative": "red",
        "candidate-silent-edge-failure": "purple",
        "silent-edge-failure": "purple",
        "unresolved": "gray",
    }.get(raw, "gray")
    return f'<span class="rs-pill rs-pill-{color}">{escape(classification_label(raw))}</span>'


def _format_help_text(text: str) -> str:
    raw = str(text)
    if "." in raw and " " not in raw and "/" not in raw:
        left, right = raw.split(".", 1)
        return f"{left} -> {right}"
    return raw


def metric_strip(metrics: list[tuple[str, str, str]]) -> None:
    cards = []
    for metric in metrics:
        label, value, help_text = metric[:3]
        raw_value = str(value)
        label_l = str(label).lower()
        is_claim = label_l == "allowed claim" or raw_value in CLAIM_LABELS
        is_class = label_l == "decision signal" or raw_value in CLASS_LABELS
        is_candidate = "candidate" in label_l or raw_value in {"candidate-silent-edge-failure", "silent-edge-failure"}
        card_class = "rs-metric-card rs-candidate-card" if is_candidate else "rs-metric-card"
        value_class = "rs-metric-value"
        if len(raw_value) > 12 and not is_claim and not is_class:
            value_class += " rs-metric-value--text"
        if is_claim:
            rendered_value = claim_pill(raw_value)
        elif is_class:
            rendered_value = classification_pill(raw_value)
        else:
            rendered_value = escape(raw_value)
        cards.append(
            f"<div class=\"{card_class}\">"
            f"<div class=\"rs-metric-label\">{escape(str(label))}</div>"
            f"<div class=\"{value_class}\">{rendered_value}</div>"
            f"<div class=\"rs-metric-help\">{escape(_format_help_text(str(help_text)))}</div>"
            "</div>"
        )
    st.markdown(
        f"<div class=\"rs-metric-grid\">{''.join(cards)}</div>",
        unsafe_allow_html=True,
    )


def claim_axis_strip() -> None:
    items = [
        ("Composition", "which taxa are present"),
        ("Topology", "who depends on whom"),
        ("Timing", "when edges can execute"),
        ("Forcing", "what loads the system"),
        ("Rewiring", "how dependency architecture moves"),
    ]
    cards = "".join(
        "<div class=\"rs-claim-card\">"
        f"<div class=\"rs-claim-title\">{escape(title)}</div>"
        f"<div class=\"rs-claim-copy\">{escape(copy)}</div>"
        "</div>"
        for title, copy in items
    )
    st.markdown(f"<div class=\"rs-claim-grid\">{cards}</div>", unsafe_allow_html=True)


def module_card(title: str, claim_level: str, copy: str) -> None:
    st.markdown(
        "<div class=\"rs-module-card\">"
        f"{claim_pill(claim_level)}"
        f"<div class=\"rs-module-title\">{escape(title)}</div>"
        f"<div class=\"rs-module-copy\">{escape(copy)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def classification_glossary() -> None:
    items = [
        ("adaptive", "Partner switching without material concentration increase."),
        ("compensatory-but-fragile", "Similar edge volume, but load concentrates into fewer taxa."),
        ("degradative", "Edges or connectance decline as dependency concentration rises."),
        ("candidate-silent-edge-failure", "Expected edge absent while endpoint taxa remain active."),
        ("unresolved", "Signals are mixed or below decision thresholds."),
    ]
    cards = "".join(
        "<div class=\"rs-claim-card\">"
        f"{classification_pill(key)}"
        f"<div class=\"rs-claim-copy\" style=\"margin-top:0.45rem;\">{escape(copy)}</div>"
        "</div>"
        for key, copy in items
    )
    st.markdown(f"<div class=\"rs-claim-grid\">{cards}</div>", unsafe_allow_html=True)


def ghost_panel(title: str, copy: str, requirement: str | None = None, claim_after: str | None = None) -> None:
    requirement_text = f"<br><strong>Unlock:</strong> {escape(requirement)}" if requirement else ""
    claim_text = f"<br><strong>Claim after unlock:</strong> {escape(claim_after)}" if claim_after else ""
    st.markdown(
        "<div class=\"rs-ghost-panel\"><div class=\"rs-ghost-inner\">"
        f"<div class=\"rs-ghost-title\">{escape(title)}</div>"
        f"<div class=\"rs-ghost-copy\">{escape(copy)}{requirement_text}{claim_text}</div>"
        "</div></div>",
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
