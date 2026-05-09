from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.ingest.lazaro import workbook_audit
from rewirescope.terminal_data import load_terminal_tables
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, ghost_panel, metric_strip


st.set_page_config(page_title="Disturbance Rewiring Gate", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
registry = tables["registry"]
row = registry[registry["dataset_id"] == "lazaro_gomez_martinez"].iloc[0]
audit = workbook_audit()

st.title("Disturbance Rewiring Gate")
st.caption("Lázaro & Gómez-Martínez habitat-loss seasonal rewiring module")
boundary_callout(
    "<strong>No fake analytics:</strong> this page remains a source-status module until the XLSX workbook is locally available and inspected."
)

metric_strip(
    [
        ("Allowed claim", str(row["allowed_claim_level"]), "source_buildability_audit.allowed_claim_level"),
        ("Snapshot rebuild", str(row["rebuild_network_snapshots"]), "source_buildability_audit.rebuild_network_snapshots"),
        ("Rewiring visualization", str(row["visualize_rewiring_events"]), "source_buildability_audit.visualize_rewiring_events"),
        ("Workbook inspected", "yes" if audit["exists"] and audit["problem"] is None else "no", "local workbook audit"),
    ]
)

ghost_panel(
    "Habitat-Loss Rewiring Gradient",
    "No seasonal plant-pollinator network or habitat-gradient chart is rendered until the source workbook is present and its raw edge columns pass inspection.",
    requirement="site, season, plant taxon, pollinator taxon, interaction count, and habitat-loss gradient",
    claim_after="partial contrast or observed rewiring, depending on repeated raw edge coverage",
)

st.subheader("Current Audit")
st.dataframe(pd.DataFrame([audit]), use_container_width=True, hide_index=True)

st.subheader("Required Before Analytics Render")
st.dataframe(
    pd.DataFrame(
        [
            {"requirement": "site", "needed_for": "site-level networks", "status": "pending workbook inspection"},
            {"requirement": "season or sampling period", "needed_for": "seasonal rewiring", "status": "pending workbook inspection"},
            {"requirement": "plant taxon", "needed_for": "bipartite source nodes", "status": "pending workbook inspection"},
            {"requirement": "pollinator taxon", "needed_for": "bipartite target nodes", "status": "pending workbook inspection"},
            {"requirement": "interaction count", "needed_for": "weighted edges", "status": "pending workbook inspection"},
            {"requirement": "habitat-loss gradient", "needed_for": "disturbance classification", "status": "source metadata supports gradient"},
        ]
    ),
    use_container_width=True,
    hide_index=True,
)
