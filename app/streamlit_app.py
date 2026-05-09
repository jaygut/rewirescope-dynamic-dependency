from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.reporting.decision_memo import summarize_signals
from rewirescope.terminal_data import (
    bins_for,
    load_terminal_summary,
    load_terminal_tables,
    site_year_options,
)
from rewirescope.terminal_ui import (
    apply_terminal_style,
    boundary_callout,
    classification_counts,
    evidence_gate_rail,
    metric_strip,
    source_note,
    thesis_banner,
)
from rewirescope.viz.figures import (
    classification_strip,
    concentration_small_multiples,
    evidence_gate_matrix,
    metric_timeseries,
    network_snapshot,
    transition_decomposition,
)


st.set_page_config(
    page_title="RewireScope Intelligence Terminal",
    page_icon="RS",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables(), load_terminal_summary()


tables, summary = load_data()
interactions = tables["interactions"]
snapshots = tables["snapshots"]
signals = tables["signals"]
registry = tables["registry"]

st.title("RewireScope Intelligence Terminal")
st.caption("Dynamic dependency intelligence for ecological networks under change")
thesis_banner()

rmbl = summary["rmbl"]
burkle = summary["burkle"]
metric_strip(
    [
        ("Observed RMBL visit records", f"{rmbl['observed_visit_records']:,}", "data/processed/rmbl_interactions.csv rows"),
        ("Weekly network snapshots", f"{rmbl['weekly_network_snapshots']:,}", "data/processed/rmbl_network_snapshots.csv rows"),
        ("Transition decision signals", f"{rmbl['transition_decision_signals']:,}", "data/processed/decision_signals.csv rows"),
        ("Rewiring event records", f"{rmbl['rewiring_event_records']:,}", "data/processed/rmbl_rewiring_events.csv rows"),
        ("Candidate silent-edge flags", f"{rmbl['candidate_silent_edge_flags']:,}", "data/processed/rmbl_silent_edge_candidates.csv rows"),
        ("Burkle contrast edges", f"{burkle['contrast_edges']:,}", "data/processed/burkle_historical_contrast.csv rows"),
    ]
)

st.subheader("Scientific Claim")
c1, c2, c3, c4, c5 = st.columns(5)
c1.info("Composition\n\nwhat is present")
c2.info("Topology\n\nwhat depends on what")
c3.info("Timing\n\nwhen edges execute")
c4.info("Forcing\n\nwhat loads the system")
c5.info("Rewiring\n\nhow dependency architecture moves")

boundary_callout(
    "<strong>Evidence boundary:</strong> inferred links are never labeled as observed rewiring. "
    "Every visible analytic panel is powered by local processed data or source metadata."
)

st.subheader("Live Evidence Gates")
left, right = st.columns([1.1, 1])
with left:
    evidence_gate_rail(registry)
    source_note("source_buildability_audit.csv", "allowed_claim_level, rebuild_network_snapshots, visualize_rewiring_events")
with right:
    st.plotly_chart(evidence_gate_matrix(registry), use_container_width=True)

st.subheader("Observed Rewiring Core")
sites, years = site_year_options(interactions)
control_a, control_b, control_c = st.columns([1, 1, 2])
site = control_a.selectbox("Site", sites)
year = control_b.selectbox("Year", years)
bins = bins_for(interactions, site, year)
week = control_c.select_slider("Week", options=bins, value=bins[min(4, len(bins) - 1)])

week_snapshot = snapshots[(snapshots["site_id"] == site) & (snapshots["time_bin"] == week)].iloc[0]
metric_strip(
    [
        ("Edges this week", f"{int(week_snapshot['edges_n']):,}", "rmbl_network_snapshots.edges_n"),
        ("Plants", f"{int(week_snapshot['plants_n']):,}", "rmbl_network_snapshots.plants_n"),
        ("Pollinators", f"{int(week_snapshot['pollinators_n']):,}", "rmbl_network_snapshots.pollinators_n"),
        ("Dependency Gini", f"{week_snapshot['dependency_gini']:.3f}", "rmbl_network_snapshots.dependency_gini"),
    ]
)

main_left, main_right = st.columns([1.25, 1])
with main_left:
    st.plotly_chart(network_snapshot(interactions, site, week), use_container_width=True)
    source_note("rmbl_interactions.csv", "site_id, time_bin, source_taxon_id, target_taxon_id, interaction_count")
with main_right:
    st.plotly_chart(metric_timeseries(snapshots, site, year), use_container_width=True)
    st.plotly_chart(classification_strip(signals, site, year), use_container_width=True)

st.subheader("Movement Decomposition")
d1, d2 = st.columns(2)
with d1:
    st.plotly_chart(transition_decomposition(signals, site, year), use_container_width=True)
with d2:
    st.plotly_chart(concentration_small_multiples(snapshots, site, year), use_container_width=True)

st.subheader("Decision Signal Distribution")
summary_left, summary_right = st.columns([1, 1])
with summary_left:
    st.dataframe(classification_counts(signals), use_container_width=True, hide_index=True)
with summary_right:
    st.dataframe(summarize_signals(signals), use_container_width=True, hide_index=True)
