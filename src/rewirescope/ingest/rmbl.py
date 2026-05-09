"""Ingestion for the RMBL / CaraDonna observed plant-pollinator dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


INTERACTIONS_PATH = Path("data/raw/rmbl_caradonna/caradonna_rmbl_interaction_networks_data_EDI.csv")
PHENOLOGY_PATH = Path("data/raw/rmbl_caradonna/caradonna_rmbl_flowering_phenology_data_EDI.csv")

REQUIRED_INTERACTION_COLUMNS = {
    "year",
    "date",
    "week_num",
    "site",
    "transect",
    "plant",
    "pollinator",
    "interactions",
}


def load_interactions(path: str | Path = INTERACTIONS_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_INTERACTION_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"RMBL interactions missing columns: {sorted(missing)}")
    df["date"] = pd.to_datetime(df["date"])
    df["time_bin"] = df["year"].astype(str) + "-W" + df["week_num"].astype(int).astype(str).str.zfill(2)
    df["site_id"] = df["site"].astype(str)
    df["source_taxon_id"] = df["plant"].astype(str)
    df["target_taxon_id"] = df["pollinator_2013"].fillna(df["pollinator"]).astype(str)
    df["interaction_count"] = pd.to_numeric(df["interactions"], errors="coerce").fillna(0).astype(float)
    df["sequence"] = df["year"].astype(int) * 100 + df["week_num"].astype(int)
    return df


def load_phenology(path: str | Path = PHENOLOGY_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"year", "site", "plant", "transect", "week_num", "flower_count"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"RMBL phenology missing columns: {sorted(missing)}")
    df["time_bin"] = df["year"].astype(str) + "-W" + df["week_num"].astype(int).astype(str).str.zfill(2)
    df["site_id"] = df["site"].astype(str)
    df["sequence"] = df["year"].astype(int) * 100 + df["week_num"].astype(int)
    return df


def normalize_interactions(df: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_interactions() if df is None else df.copy()
    normalized = pd.DataFrame(
        {
            "dataset_id": "rmbl_caradonna",
            "site_id": df["site_id"],
            "time_bin": df["time_bin"],
            "sequence": df["sequence"],
            "timestamp": df["date"],
            "source_taxon_id": df["source_taxon_id"],
            "target_taxon_id": df["target_taxon_id"],
            "interaction_type": "pollination_visit",
            "interaction_count": df["interaction_count"],
            "interaction_strength": df["interaction_count"],
            "evidence_type": "direct_observation",
            "confidence": "high",
            "plant": df["plant"],
            "pollinator": df["pollinator"],
            "pollinator_group": df.get("pollinator_group", "unknown"),
        }
    )
    return normalized


def flowering_presence(phenology: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_phenology() if phenology is None else phenology.copy()
    grouped = (
        df.groupby(["site_id", "time_bin", "sequence", "plant"], as_index=False)["flower_count"]
        .sum()
        .rename(columns={"plant": "taxon_id"})
    )
    grouped["present"] = grouped["flower_count"] > 0
    return grouped
