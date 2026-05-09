from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.terminal_data import bins_for, load_terminal_tables, site_year_options
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, metric_strip, source_note
from rewirescope.viz.figures import (
    concentration_radar,
    concentration_small_multiples,
    taxon_load_rank_bars,
)


st.set_page_config(page_title="Dependency Concentration", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
interactions = tables["interactions"]
snapshots = tables["snapshots"]
signals = tables["signals"]
taxon_load = tables["taxon_load"]

st.title("Dependency Concentration")
st.caption("Real weekly load concentration, effective taxa load, connectance, nestedness proxy, and specialization proxy")
boundary_callout(
    "<strong>Interpretation boundary:</strong> concentration is a fragility diagnostic, not a standalone collapse forecast. Compensatory-but-fragile labels are tied to observed transition deltas."
)

sites, years = site_year_options(interactions)
c1, c2, c3 = st.columns(3)
site = c1.selectbox("Site", sites)
year = c2.selectbox("Year", years)
bins = bins_for(interactions, site, year)
week = c3.selectbox("Week", bins, index=min(4, len(bins) - 1))

current = snapshots[(snapshots["site_id"] == site) & (snapshots["time_bin"] == week)].iloc[0]
metric_strip(
    [
        ("Dependency Gini", f"{current['dependency_gini']:.3f}", "rmbl_network_snapshots.dependency_gini"),
        ("Top-10 share", f"{current['top10_interaction_share']:.3f}", "rmbl_network_snapshots.top10_interaction_share"),
        ("Effective taxa load", f"{current['effective_taxa_load']:.2f}", "rmbl_network_snapshots.effective_taxa_load"),
        ("Connectance", f"{current['connectance']:.3f}", "rmbl_network_snapshots.connectance"),
        ("Nestedness proxy", f"{current['nestedness_proxy']:.3f}", "rmbl_network_snapshots.nestedness_proxy"),
        ("Specialization proxy", f"{current['specialization_proxy']:.3f}", "rmbl_network_snapshots.specialization_proxy"),
    ]
)

left, right = st.columns([1.4, 1])
with left:
    st.plotly_chart(concentration_small_multiples(snapshots, site, year), use_container_width=True)
    source_note("rmbl_network_snapshots.csv", "dependency_gini, top10_interaction_share, effective_taxa_load, connectance")
with right:
    st.plotly_chart(concentration_radar(snapshots, site, week), use_container_width=True)

st.subheader("Taxon Load Leaderboard")
guild = st.radio("Guild", ["all", "plant", "pollinator"], horizontal=True)
st.plotly_chart(
    taxon_load_rank_bars(taxon_load, site, week, None if guild == "all" else guild),
    use_container_width=True,
)
source_note("rmbl_taxon_load_timeseries.csv", "taxon_id, guild, interaction_load")

st.subheader("Compensatory-but-Fragile Diagnostics")
fragile = signals[
    (signals["site_id"] == site)
    & (signals["from_time_bin"].str.startswith(str(year)))
    & (signals["classification"] == "compensatory-but-fragile")
]
cols = [
    "time_window",
    "edges_delta",
    "dependency_gini_delta",
    "effective_taxa_load_delta",
    "rewiring_ratio",
    "evidence_summary",
    "falsification_condition",
]
st.dataframe(fragile[cols], use_container_width=True, hide_index=True)
