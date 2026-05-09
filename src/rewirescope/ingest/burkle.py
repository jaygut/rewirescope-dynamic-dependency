"""Ingestion for Burkle, Marlin, and Knight partial historical contrast data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path("data/raw/burkle_120yr")
CURRENT_INTERACTIONS = BASE / "dryad - interactions now.csv"
OLD_RECONSTRUCTION = BASE / "old_edgelist_paper_figure_reconstruction.csv"
PLANT_PHENOLOGY = BASE / "dryad - plant phen.csv"
BEE_PHENOLOGY = BASE / "dryad - bee phen.csv"


def load_current_interactions(path: str | Path = CURRENT_INTERACTIONS) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "#sum.ints" in df.columns:
        df = df.rename(columns={"#sum.ints": "interaction_count"})
    required = {"plant", "bee", "interaction_count"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Burkle contemporary interactions missing columns: {sorted(missing)}")
    return df


def load_old_reconstruction(path: str | Path = OLD_RECONSTRUCTION) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"plant", "bee"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Burkle historical reconstruction missing columns: {sorted(missing)}")
    df["interaction_count"] = df.get("edge", 1)
    return df[["plant", "bee", "interaction_count"]]


def load_phenology() -> tuple[pd.DataFrame, pd.DataFrame]:
    plants = pd.read_csv(PLANT_PHENOLOGY)
    bees = pd.read_csv(BEE_PHENOLOGY)
    return plants, bees


def historical_contrast() -> pd.DataFrame:
    old = load_old_reconstruction()
    now = load_current_interactions()
    old_edges = set(zip(old["plant"], old["bee"], strict=False))
    now_edges = set(zip(now["plant"], now["bee"], strict=False))
    rows = []
    for plant, bee in sorted(old_edges | now_edges):
        if (plant, bee) in old_edges and (plant, bee) in now_edges:
            status = "persisted"
        elif (plant, bee) in old_edges:
            status = "lost"
        else:
            status = "novel_contemporary"
        rows.append(
            {
                "dataset_id": "burkle_120yr",
                "site_id": "carlinville_il",
                "time_window": "robertson_1800s_vs_2009_2010",
                "source_taxon_id": plant,
                "target_taxon_id": bee,
                "edge_status": status,
                "allowed_claim_level": "partial_contrast",
                "evidence_type": (
                    "direct_observation_contemporary_plus_paper_figure_reconstruction_historical"
                ),
            }
        )
    return pd.DataFrame(rows)


def phenology_overlap_loss() -> pd.DataFrame:
    plants, bees = load_phenology()
    plant_cols = {"plant": "plant", "startRob": "plant_start_old", "endRob": "plant_end_old", "startnow": "plant_start_now", "endnow": "plant_end_now"}
    bee_cols = {"bee species": "bee", "Rob start": "bee_start_old", "Rob end": "bee_end_old", "start now": "bee_start_now", "end now": "bee_end_now"}
    plants = plants.rename(columns=plant_cols)
    bees = bees.rename(columns=bee_cols)
    contrast = historical_contrast()
    old_edges = contrast[contrast["edge_status"].isin(["persisted", "lost"])].copy()
    merged = old_edges.merge(plants, left_on="source_taxon_id", right_on="plant", how="left")
    merged = merged.merge(bees, left_on="target_taxon_id", right_on="bee", how="left")
    merged["old_overlap_days"] = (
        merged[["plant_end_old", "bee_end_old"]].min(axis=1)
        - merged[["plant_start_old", "bee_start_old"]].max(axis=1)
        + 1
    ).clip(lower=0)
    merged["now_overlap_days"] = (
        merged[["plant_end_now", "bee_end_now"]].min(axis=1)
        - merged[["plant_start_now", "bee_start_now"]].max(axis=1)
        + 1
    ).clip(lower=0)
    merged["overlap_delta_days"] = merged["now_overlap_days"] - merged["old_overlap_days"]
    return merged[
        [
            "source_taxon_id",
            "target_taxon_id",
            "edge_status",
            "old_overlap_days",
            "now_overlap_days",
            "overlap_delta_days",
        ]
    ]
