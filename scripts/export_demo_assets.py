#!/usr/bin/env python3
"""Export a few standalone HTML figures for the demo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from rewirescope.demo import build_all
from rewirescope.viz.figures import (
    burkle_contrast_bars,
    classification_strip,
    edge_persistence_heatmap,
    metric_timeseries,
)


def main() -> None:
    build_all()
    out = Path("outputs/figures")
    out.mkdir(parents=True, exist_ok=True)
    interactions = pd.read_csv("data/processed/rmbl_interactions.csv")
    snapshots = pd.read_csv("data/processed/rmbl_network_snapshots.csv")
    signals = pd.read_csv("data/processed/decision_signals.csv")
    contrast = pd.read_csv("data/processed/burkle_historical_contrast.csv")
    site = sorted(interactions["site_id"].unique())[0]
    year = int(interactions["time_bin"].str.slice(0, 4).astype(int).min())
    metric_timeseries(snapshots, site, year).write_html(out / "rmbl_network_movement.html")
    transition_decomp = classification_strip(signals, site, year)
    transition_decomp.write_html(out / "rmbl_decision_signal.html")
    edge_persistence_heatmap(interactions, site, year).write_html(out / "rmbl_edge_persistence.html")
    burkle_contrast_bars(contrast).write_html(out / "burkle_historical_contrast.html")
    print(f"Exported figures to {out}")


if __name__ == "__main__":
    main()
