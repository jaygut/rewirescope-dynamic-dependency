import json
from pathlib import Path

import pandas as pd

from rewirescope.demo import build_all


def test_transition_edge_status_reconciles_with_transition_metrics():
    tables = build_all()
    transition_edges = tables["rmbl_transition_edge_status"]
    transitions = tables["rmbl_transition_metrics"]

    counts = (
        transition_edges.groupby(["site_id", "from_time_bin", "to_time_bin", "edge_status"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    merged = transitions.merge(counts, on=["site_id", "from_time_bin", "to_time_bin"], how="left")

    assert (merged["births"] == merged["birth"]).all()
    assert (merged["deaths"] == merged["death"]).all()
    assert (merged["shared_edges"] == merged["persisted"]).all()


def test_taxon_load_sums_reconcile_with_interaction_counts():
    tables = build_all()
    interactions = tables["rmbl_interactions"]
    taxon_load = tables["rmbl_taxon_load_timeseries"]

    interaction_totals = (
        interactions.groupby(["site_id", "time_bin"])["interaction_count"].sum().sort_index()
    )
    load_totals = (
        taxon_load.groupby(["site_id", "time_bin"])["interaction_load"].sum().sort_index()
    )

    pd.testing.assert_series_equal(load_totals, interaction_totals * 2, check_names=False)


def test_phenology_windows_are_observed_only_and_year_bounded():
    tables = build_all()
    windows = tables["rmbl_phenology_windows"]

    assert set(windows["evidence_basis"].unique()) == {"flower_count", "observed_visits"}
    assert {"site_id", "year", "taxon_id", "guild", "first_time_bin", "last_time_bin"}.issubset(windows.columns)
    assert (windows["first_time_bin"].str.slice(0, 4).astype(int) == windows["year"]).all()
    assert (windows["last_time_bin"].str.slice(0, 4).astype(int) == windows["year"]).all()


def test_terminal_summary_matches_processed_tables():
    tables = build_all()
    summary = json.loads(Path("outputs/demo_exports/terminal_summary.json").read_text())

    assert summary["rmbl"]["observed_visit_records"] == len(tables["rmbl_interactions"])
    assert summary["rmbl"]["weekly_network_snapshots"] == len(tables["rmbl_network_snapshots"])
    assert summary["rmbl"]["transition_decision_signals"] == len(tables["decision_signals"])
    assert summary["rmbl"]["rewiring_event_records"] == len(tables["rmbl_rewiring_events"])
    assert summary["rmbl"]["candidate_silent_edge_flags"] == len(tables["rmbl_silent_edge_candidates"])
    assert summary["burkle"]["contrast_edges"] == len(tables["burkle_historical_contrast"])


def test_gated_sources_remain_non_observed_rewiring():
    registry = build_all()["burkle_historical_contrast"]  # ensures outputs are current
    del registry
    source = pd.read_csv("data/processed/source_buildability_audit.csv")
    gated = source[source["dataset_id"].isin(["lazaro_gomez_martinez", "noaa_ecomon", "helgoland_roads"])]

    assert not (gated["allowed_claim_level"] == "observed_rewiring").any()
