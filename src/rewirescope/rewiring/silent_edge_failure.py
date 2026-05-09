"""Silent-edge-failure candidate detection."""

from __future__ import annotations

import pandas as pd


def expected_edges_from_history(interactions: pd.DataFrame, min_total_weight: float = 1.0) -> set[tuple[str, str]]:
    totals = interactions.groupby(["source_taxon_id", "target_taxon_id"])["interaction_count"].sum()
    return {edge for edge, value in totals.items() if value >= min_total_weight}


def pollinator_presence(interactions: pd.DataFrame) -> pd.DataFrame:
    return (
        interactions.groupby(["site_id", "time_bin", "sequence", "target_taxon_id"], as_index=False)[
            "interaction_count"
        ]
        .sum()
        .rename(columns={"target_taxon_id": "taxon_id"})
        .assign(present=lambda df: df["interaction_count"] > 0)
    )


def detect_candidates(
    interactions: pd.DataFrame,
    plant_presence: pd.DataFrame,
    expected_edges: set[tuple[str, str]] | None = None,
    max_candidates_per_bin: int = 200,
) -> pd.DataFrame:
    expected_edges = expected_edges or expected_edges_from_history(interactions)
    observed_by_bin = {
        key: set(zip(group["source_taxon_id"], group["target_taxon_id"], strict=False))
        for key, group in interactions.groupby(["site_id", "time_bin"], sort=True)
    }
    plant_present = plant_presence[plant_presence["present"]].copy()
    poll_present = pollinator_presence(interactions)
    poll_present = poll_present[poll_present["present"]].copy()
    plant_by_bin = {
        key: set(group["taxon_id"])
        for key, group in plant_present.groupby(["site_id", "time_bin"], sort=True)
    }
    poll_by_bin = {
        key: set(group["taxon_id"])
        for key, group in poll_present.groupby(["site_id", "time_bin"], sort=True)
    }
    sequence_by_bin = (
        interactions[["site_id", "time_bin", "sequence"]]
        .drop_duplicates()
        .set_index(["site_id", "time_bin"])["sequence"]
        .to_dict()
    )
    rows = []
    for key in sorted(observed_by_bin):
        observed = observed_by_bin.get(key, set())
        plants = plant_by_bin.get(key, set())
        pollinators = poll_by_bin.get(key, set())
        candidates = [
            (plant, pollinator)
            for plant, pollinator in expected_edges
            if plant in plants and pollinator in pollinators and (plant, pollinator) not in observed
        ]
        for plant, pollinator in sorted(candidates)[:max_candidates_per_bin]:
            site_id, time_bin = key
            rows.append(
                {
                    "dataset_id": "rmbl_caradonna",
                    "site_id": site_id,
                    "time_bin": time_bin,
                    "sequence": int(sequence_by_bin[key]),
                    "source_taxon_id": plant,
                    "target_taxon_id": pollinator,
                    "candidate_type": "silent_edge_failure_candidate",
                    "evidence_summary": "Expected pair absent while plant flowered and pollinator was observed with another plant in the same site-week.",
                    "allowed_claim_level": "observed_rewiring",
                    "confidence": "low",
                }
            )
    return pd.DataFrame(rows)
