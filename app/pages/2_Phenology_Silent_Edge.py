from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from rewirescope.terminal_data import bins_for, load_terminal_tables, site_year_options
from rewirescope.terminal_ui import apply_terminal_style, boundary_callout, metric_strip, source_note
from rewirescope.viz.figures import phenology_ribbons, silent_edge_heatmap


st.set_page_config(page_title="Phenology + Silent Edge Failure", layout="wide")
apply_terminal_style()


@st.cache_data(show_spinner=False)
def load_data():
    return load_terminal_tables()


tables = load_data()
interactions = tables["interactions"]
windows = tables["phenology_windows"]
silent = tables["silent"]

st.title("Phenology + Silent Edge Failure")
st.caption("Real RMBL flowering windows and observed pollinator activity windows")
boundary_callout(
    "<strong>Strict label:</strong> silent-edge outputs are candidate flags. They mean an expected pair was absent while endpoint taxa were active in the observed site-week; they are not proof of causal failure."
)

sites, years = site_year_options(interactions)
c1, c2, c3 = st.columns(3)
site = c1.selectbox("Site", sites)
year = c2.selectbox("Year", years)
bins = bins_for(interactions, site, year)
week = c3.selectbox("Week", bins, index=min(4, len(bins) - 1))

filtered_silent = silent[(silent["site_id"] == site) & (silent["time_bin"] == week)]
site_year_silent = silent[(silent["site_id"] == site) & (silent["time_bin"].str.startswith(str(year)))]
metric_strip(
    [
        ("Candidate flags this week", f"{len(filtered_silent):,}", "rmbl_silent_edge_candidates rows for selected site-week"),
        ("Candidate flags this year", f"{len(site_year_silent):,}", "rmbl_silent_edge_candidates rows for selected site-year"),
        ("Plant windows", f"{len(windows[(windows['site_id'] == site) & (windows['year'] == year) & (windows['guild'] == 'plant')]):,}", "rmbl_phenology_windows guild=plant"),
        ("Pollinator windows", f"{len(windows[(windows['site_id'] == site) & (windows['year'] == year) & (windows['guild'] == 'pollinator')]):,}", "rmbl_phenology_windows guild=pollinator"),
    ]
)

left, right = st.columns([1.2, 1])
with left:
    guild_filter = st.radio("Ribbon filter", ["all", "plant", "pollinator"], horizontal=True)
    guild = None if guild_filter == "all" else guild_filter
    st.plotly_chart(phenology_ribbons(windows, site, year, guild), use_container_width=True)
    source_note("rmbl_phenology_windows.csv", "first_time_bin, last_time_bin, evidence_basis")
with right:
    st.plotly_chart(silent_edge_heatmap(silent, site, year), use_container_width=True)
    source_note("rmbl_silent_edge_candidates.csv", "candidate_type, source_taxon_id, target_taxon_id")

st.subheader("Candidate Silent-Edge Records")
cols = [
    "time_bin",
    "source_taxon_id",
    "target_taxon_id",
    "candidate_type",
    "confidence",
    "evidence_summary",
]
st.dataframe(filtered_silent[cols], use_container_width=True, hide_index=True)
