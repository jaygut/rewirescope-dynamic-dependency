"""Shared data loading for the Streamlit terminal."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rewirescope.demo import build_all


PROCESSED = Path("data/processed")
SUMMARY_PATH = Path("outputs/demo_exports/terminal_summary.json")


TABLE_FILES = {
    "registry": PROCESSED / "source_buildability_audit.csv",
    "interactions": PROCESSED / "rmbl_interactions.csv",
    "snapshots": PROCESSED / "rmbl_network_snapshots.csv",
    "transitions": PROCESSED / "rmbl_transition_metrics.csv",
    "transition_edges": PROCESSED / "rmbl_transition_edge_status.csv",
    "taxon_load": PROCESSED / "rmbl_taxon_load_timeseries.csv",
    "phenology_windows": PROCESSED / "rmbl_phenology_windows.csv",
    "signals": PROCESSED / "decision_signals.csv",
    "events": PROCESSED / "rmbl_rewiring_events.csv",
    "silent": PROCESSED / "rmbl_silent_edge_candidates.csv",
    "plant_presence": PROCESSED / "rmbl_plant_presence.csv",
    "burkle_contrast": PROCESSED / "burkle_historical_contrast.csv",
    "burkle_phenology": PROCESSED / "burkle_phenology_overlap_loss.csv",
    "burkle_summary": PROCESSED / "burkle_contrast_summary.csv",
}


def ensure_processed() -> None:
    missing = [path for path in TABLE_FILES.values() if not path.exists()]
    if missing or not SUMMARY_PATH.exists():
        build_all()


def load_terminal_tables() -> dict[str, pd.DataFrame]:
    ensure_processed()
    return {name: pd.read_csv(path) for name, path in TABLE_FILES.items()}


def load_terminal_summary() -> dict:
    ensure_processed()
    return json.loads(SUMMARY_PATH.read_text())


def site_year_options(interactions: pd.DataFrame) -> tuple[list[str], list[int]]:
    sites = sorted(interactions["site_id"].unique().tolist())
    years = sorted(interactions["time_bin"].str.slice(0, 4).astype(int).unique().tolist())
    return sites, years


def bins_for(interactions: pd.DataFrame, site_id: str, year: int) -> list[str]:
    return sorted(
        interactions[
            (interactions["site_id"] == site_id)
            & (interactions["time_bin"].str.startswith(str(year)))
        ]["time_bin"].unique().tolist()
    )


def transition_options(signals: pd.DataFrame, site_id: str, year: int) -> pd.DataFrame:
    return signals[
        (signals["site_id"] == site_id)
        & (signals["from_time_bin"].str.startswith(str(year)))
    ].sort_values("from_sequence")
