"""Partner-switching summaries."""

from __future__ import annotations

import pandas as pd


def partner_counts(interactions: pd.DataFrame) -> pd.DataFrame:
    source_counts = (
        interactions.groupby(["site_id", "time_bin", "source_taxon_id"])["target_taxon_id"]
        .nunique()
        .reset_index(name="partner_count")
        .rename(columns={"source_taxon_id": "taxon_id"})
        .assign(guild="plant")
    )
    target_counts = (
        interactions.groupby(["site_id", "time_bin", "target_taxon_id"])["source_taxon_id"]
        .nunique()
        .reset_index(name="partner_count")
        .rename(columns={"target_taxon_id": "taxon_id"})
        .assign(guild="pollinator")
    )
    return pd.concat([source_counts, target_counts], ignore_index=True)
