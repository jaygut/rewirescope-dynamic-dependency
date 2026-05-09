"""Interaction strength change metrics."""

from __future__ import annotations

import pandas as pd


def strength_shift(current: pd.DataFrame, following: pd.DataFrame) -> pd.DataFrame:
    left = current.groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"].sum()
    right = following.groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"].sum()
    merged = left.merge(
        right,
        on=["source_taxon_id", "target_taxon_id"],
        how="inner",
        suffixes=("_t", "_next"),
    )
    merged["strength_delta"] = merged["interaction_count_next"] - merged["interaction_count_t"]
    merged["relative_strength_delta"] = merged["strength_delta"] / merged["interaction_count_t"].replace(0, pd.NA)
    return merged
