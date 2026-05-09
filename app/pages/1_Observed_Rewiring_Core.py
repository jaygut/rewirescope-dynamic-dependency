from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.terminal_data import (
    load_terminal_tables,
    site_year_options,
    transition_options,
)
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, metric_strip, source_note
from rewirescope.viz.figures import (
    classification_strip,
    edge_persistence_heatmap,
    network_snapshot,
    transition_decomposition,
    transition_diff_network,
)


st.set_page_config(page_title="Observed Rewiring Core", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
interactions = tables["interactions"]
snapshots = tables["snapshots"]
signals = tables["signals"]
transition_edges = tables["transition_edges"]

st.title("Observed Rewiring Core")
st.caption("RMBL / CaraDonna EDI weekly plant-pollinator interaction data | observed pairwise edges")
boundary_callout(
    "<strong>Claim level:</strong> observed rewiring. This page uses direct plant-pollinator visit records, repeated weekly time bins, and raw interaction counts."
)

sites, years = site_year_options(interactions)
c1, c2, c3 = st.columns([1, 1, 2])
site = c1.selectbox("Site", sites)
year = c2.selectbox("Year", years)
transitions = transition_options(signals, site, year)
transition_labels = [f"{r.from_time_bin} -> {r.to_time_bin}" for r in transitions.itertuples(index=False)]
selected_transition = c3.selectbox("Transition", transition_labels)
from_time_bin, to_time_bin = selected_transition.split(" -> ")
mode = st.radio("Network view", ["Transition diff", "Snapshot at destination week"], horizontal=True)

row = transitions[
    (transitions["from_time_bin"] == from_time_bin) & (transitions["to_time_bin"] == to_time_bin)
].iloc[0]
metric_strip(
    [
        ("Births", f"{int(row['births']):,}", "decision_signals.births"),
        ("Deaths", f"{int(row['deaths']):,}", "decision_signals.deaths"),
        ("Rewiring edges", f"{int(row['rewiring_edges']):,}", "decision_signals.rewiring_edges"),
        ("Species-turnover edges", f"{int(row['species_turnover_edges']):,}", "decision_signals.species_turnover_edges"),
        ("Edge turnover", f"{row['edge_turnover']:.3f}", "decision_signals.edge_turnover"),
        ("Decision signal", str(row["classification"]), "decision_signals.classification"),
    ]
)

left, right = st.columns([1.35, 1])
with left:
    if mode == "Transition diff":
        st.plotly_chart(
            transition_diff_network(transition_edges, site, from_time_bin, to_time_bin),
            use_container_width=True,
        )
        source_note("rmbl_transition_edge_status.csv", "edge_status, interaction_count_from, interaction_count_to")
    else:
        st.plotly_chart(network_snapshot(interactions, site, to_time_bin), use_container_width=True)
        source_note("rmbl_interactions.csv", "source_taxon_id, target_taxon_id, interaction_count")
with right:
    st.plotly_chart(transition_decomposition(signals, site, year), use_container_width=True)
    st.plotly_chart(classification_strip(signals, site, year), use_container_width=True)

st.subheader("Edge Persistence")
st.plotly_chart(edge_persistence_heatmap(interactions, site, year), use_container_width=True)

st.subheader("Transition Evidence")
columns = [
    "time_window",
    "classification",
    "confidence",
    "edge_turnover",
    "rewiring_ratio",
    "species_turnover_ratio",
    "evidence_summary",
    "falsification_condition",
]
st.dataframe(transitions[columns], use_container_width=True, hide_index=True)
