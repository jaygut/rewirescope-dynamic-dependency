"""Evidence table generation."""

from __future__ import annotations

import pandas as pd


def evidence_table(registry: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "dataset_id",
        "allowed_claim_level",
        "rebuild_network_snapshots",
        "visualize_rewiring_events",
        "observed_pairwise_edges",
        "repeated_time_bins",
        "raw_interaction_counts",
        "audit_notes",
    ]
    return registry[columns].copy()
