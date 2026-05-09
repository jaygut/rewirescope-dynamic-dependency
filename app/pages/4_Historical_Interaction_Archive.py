from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.terminal_data import load_terminal_tables
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, metric_strip, source_note
from rewirescope.viz.figures import burkle_contrast_bars, burkle_contrast_network


st.set_page_config(page_title="Historical Interaction Archive", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
contrast = tables["burkle_contrast"]
phenology = tables["burkle_phenology"]

st.title("Historical Interaction Archive")
st.caption("Burkle, Marlin & Knight | contemporary Dryad/Zenodo files plus labeled historical reconstruction")
boundary_callout(
    "<strong>Permanent label:</strong> partial historical contrast, not dense temporal rewiring. The historical edge list is an unweighted paper-figure reconstruction, not a raw historical event table."
)

counts = contrast["edge_status"].value_counts()
metric_strip(
    [
        ("Contrast edges", f"{len(contrast):,}", "burkle_historical_contrast rows"),
        ("Lost historical edges", f"{int(counts.get('lost', 0)):,}", "edge_status=lost"),
        ("Persisted edges", f"{int(counts.get('persisted', 0)):,}", "edge_status=persisted"),
        ("Novel contemporary edges", f"{int(counts.get('novel_contemporary', 0)):,}", "edge_status=novel_contemporary"),
    ]
)

left, right = st.columns([1, 1.35])
with left:
    st.plotly_chart(burkle_contrast_bars(contrast), use_container_width=True)
    statuses = st.multiselect(
        "Network edge statuses",
        ["lost", "persisted", "novel_contemporary"],
        default=["lost", "persisted", "novel_contemporary"],
    )
with right:
    st.plotly_chart(burkle_contrast_network(contrast, statuses), use_container_width=True)
    source_note("burkle_historical_contrast.csv", "edge_status, source_taxon_id, target_taxon_id")

st.subheader("Phenological Overlap Loss")
fig = px.histogram(
    phenology,
    x="overlap_delta_days",
    color="edge_status",
    barmode="overlay",
    color_discrete_map={"lost": "#9B3A32", "persisted": "#2F6F4E"},
    title="Overlap Delta on Historical/Reconstructed Edges",
)
fig.update_layout(template="plotly_white", height=380, margin=dict(l=10, r=10, t=45, b=10))
st.plotly_chart(fig, use_container_width=True)
source_note("burkle_phenology_overlap_loss.csv", "old_overlap_days, now_overlap_days, overlap_delta_days")

st.subheader("Contrast Records")
st.dataframe(contrast.head(400), use_container_width=True, hide_index=True)
