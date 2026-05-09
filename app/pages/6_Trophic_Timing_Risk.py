from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.ingest.ecomon import SOURCE as ECOMON
from rewirescope.ingest.helgoland import SOURCE as HELGOLAND
from rewirescope.terminal_data import load_terminal_tables
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, metric_strip


st.set_page_config(page_title="Trophic Timing Risk Gate", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
registry = tables["registry"]
marine_registry = registry[registry["dataset_id"].isin(["noaa_ecomon", "helgoland_roads"])]

st.title("Trophic Timing Risk Gate")
st.caption("NOAA EcoMon and Helgoland Roads | inferred dynamic dependency only until abundance data are ingested")
boundary_callout(
    "<strong>Evidence boundary:</strong> no observed pairwise trophic edges are present in the audited sources. No inferred association graph is rendered until real abundance time series are ingested."
)

metric_strip(
    [
        ("Marine sources", f"{len(marine_registry):,}", "source_buildability_audit rows"),
        ("Observed pairwise trophic edges", "0", "audited source boundary"),
        ("Allowed claim", "inferred dependency", "source_buildability_audit.allowed_claim_level"),
        ("Rendered analytic charts", "0", "no local abundance time series ingested yet"),
    ]
)

st.subheader("Source Status")
status_view = marine_registry[
    [
        "dataset_id",
        "title",
        "allowed_claim_level",
        "rebuild_network_snapshots",
        "visualize_rewiring_events",
    ]
]
st.dataframe(
    status_view,
    use_container_width=True,
    hide_index=True,
    column_config={
        "dataset_id": st.column_config.TextColumn("dataset_id", width="small"),
        "title": st.column_config.TextColumn("title", width="large"),
        "allowed_claim_level": st.column_config.TextColumn("allowed_claim_level", width="medium"),
        "rebuild_network_snapshots": st.column_config.TextColumn("network snapshots", width="small"),
        "visualize_rewiring_events": st.column_config.TextColumn("rewiring events", width="small"),
    },
)

st.subheader("Source Metadata")
metadata = pd.DataFrame([ECOMON, HELGOLAND])[["dataset_id", "title", "url", "edge_boundary"]]
st.dataframe(
    metadata,
    use_container_width=True,
    hide_index=True,
    column_config={
        "dataset_id": st.column_config.TextColumn("dataset_id", width="small"),
        "title": st.column_config.TextColumn("title", width="large"),
        "url": st.column_config.LinkColumn("url", width="large"),
        "edge_boundary": st.column_config.TextColumn("edge_boundary", width="large"),
    },
)

st.subheader("Decision-Grade Upgrade Path")
st.dataframe(
    pd.DataFrame(
        [
            {"requirement": "time-aligned abundance table", "status": "not yet ingested locally", "claim_after": "inferred dependency"},
            {"requirement": "environmental forcing columns", "status": "source-supported, not yet normalized", "claim_after": "forcing overlay"},
            {"requirement": "diet/gut-content/direct trophic observations", "status": "not present in audited sources", "claim_after": "observed edge only if acquired"},
            {"requirement": "uncertainty-labeled association method", "status": "future implementation", "claim_after": "inferred edge confidence"},
        ]
    ),
    use_container_width=True,
    hide_index=True,
)
