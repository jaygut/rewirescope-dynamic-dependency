from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.terminal_data import (
    load_terminal_summary,
    load_terminal_tables,
    site_year_options,
)
from rewirescope.terminal_ui import (
    apply_terminal_style,
    boundary_callout,
    claim_axis_strip,
    evidence_gate_rail,
    metric_strip,
    module_card,
    source_note,
    thesis_banner,
)
from rewirescope.viz.figures import edge_persistence_heatmap, evidence_gate_matrix


st.set_page_config(
    page_title="RewireScope",
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

st.subheader("Claim System")
claim_axis_strip()

boundary_callout(
    "<strong>Evidence boundary:</strong> inferred links are never labeled as observed rewiring. "
    "Every visible analytic panel is powered by local processed data or source metadata."
)

st.subheader("Live Evidence Gates")
gate_left, gate_right = st.columns([0.9, 1.15])
with gate_left:
    evidence_gate_rail(registry)
    source_note("source_buildability_audit.csv", "allowed_claim_level, rebuild_network_snapshots, visualize_rewiring_events")
with gate_right:
    st.plotly_chart(evidence_gate_matrix(registry), use_container_width=True)

st.subheader("Signature Observed Evidence")
sites, years = site_year_options(interactions)
default_site = sites[0]
default_year = years[0]
st.plotly_chart(edge_persistence_heatmap(interactions, default_site, default_year, max_edges=48), use_container_width=True)
source_note("rmbl_interactions.csv", "source_taxon_id, target_taxon_id, time_bin, interaction_count")

st.subheader("Modules")
top_a, top_b, top_c = st.columns(3)
with top_a:
    module_card(
        "Observed Rewiring Core",
        "observed_rewiring",
        "Direct weekly plant-pollinator edge births, deaths, persistence, and rewiring decomposition.",
    )
    st.page_link("pages/1_Observed_Rewiring_Core.py", label="Open Observed Rewiring Core")
with top_b:
    module_card(
        "Phenology + Silent Edge",
        "observed_rewiring",
        "Flowering and observed pollinator activity windows with candidate silent-edge flags.",
    )
    st.page_link("pages/2_Phenology_Silent_Edge.py", label="Open Phenology + Silent Edge")
with top_c:
    module_card(
        "Dependency Concentration",
        "observed_rewiring",
        "Load concentration, effective taxa load, and compensatory-but-fragile diagnostics.",
    )
    st.page_link("pages/3_Dependency_Concentration.py", label="Open Dependency Concentration")

bottom_a, bottom_b, bottom_c = st.columns(3)
with bottom_a:
    module_card(
        "Historical Interaction Archive",
        "partial_contrast",
        "Burkle historical versus contemporary contrast with permanent partial-contrast labeling.",
    )
    st.page_link("pages/4_Historical_Interaction_Archive.py", label="Open Historical Archive")
with bottom_b:
    module_card(
        "Disturbance Rewiring",
        "partial_contrast",
        "Habitat-loss module held behind a workbook-inspection evidence gate.",
    )
    st.page_link("pages/5_Disturbance_Rewiring.py", label="Open Disturbance Gate")
with bottom_c:
    module_card(
        "Trophic Timing Risk",
        "inferred_dependency",
        "Marine timing expansion gated until real abundance time series are ingested.",
    )
    st.page_link("pages/6_Trophic_Timing_Risk.py", label="Open Trophic Timing Gate")

