"""Temporal network snapshot builders."""

from __future__ import annotations

import pandas as pd

from rewirescope.networks.graph_metrics import snapshot_metrics
from rewirescope.rewiring.dependency_concentration import concentration_summary


def build_snapshots(interactions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["dataset_id", "site_id", "time_bin", "sequence"]
    for keys, group in interactions.groupby(group_cols, sort=True):
        dataset_id, site_id, time_bin, sequence = keys
        metrics = snapshot_metrics(group)
        concentration = concentration_summary(group)
        rows.append(
            {
                "snapshot_id": f"{dataset_id}:{site_id}:{time_bin}",
                "dataset_id": dataset_id,
                "site_id": site_id,
                "time_bin": time_bin,
                "sequence": int(sequence),
                **metrics,
                **concentration,
            }
        )
    return pd.DataFrame(rows).sort_values(["site_id", "sequence"]).reset_index(drop=True)
