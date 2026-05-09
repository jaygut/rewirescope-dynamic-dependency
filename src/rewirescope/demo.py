"""End-to-end processed data build for the RewireScope POC."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from rewirescope.audit import load_source_registry, registry_rows
from rewirescope.classify.decision_signal import classify_transitions
from rewirescope.ingest import burkle, lazaro, rmbl
from rewirescope.networks.temporal_graphs import build_snapshots
from rewirescope.rewiring.edge_turnover import rewiring_events, transition_table
from rewirescope.rewiring.silent_edge_failure import detect_candidates
from rewirescope.reporting.decision_memo import summarize_signals


PROCESSED = Path("data/processed")
TABLES = Path("outputs/tables")
SUMMARY_PATH = Path("outputs/demo_exports/terminal_summary.json")


def ensure_dirs() -> None:
    for path in [PROCESSED, TABLES, Path("outputs/demo_exports")]:
        path.mkdir(parents=True, exist_ok=True)


def transition_edge_status(interactions: pd.DataFrame) -> pd.DataFrame:
    """Build edge-level persisted, birth, and death records for each adjacent transition."""

    rows: list[dict] = []
    for (dataset_id, site_id), group in interactions.groupby(["dataset_id", "site_id"], sort=True):
        bins = (
            group[["time_bin", "sequence"]]
            .drop_duplicates()
            .sort_values("sequence")
            .reset_index(drop=True)
        )
        for idx in range(len(bins) - 1):
            left = bins.iloc[idx]
            right = bins.iloc[idx + 1]
            current = (
                group[group["time_bin"] == left["time_bin"]]
                .groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"]
                .sum()
            )
            following = (
                group[group["time_bin"] == right["time_bin"]]
                .groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"]
                .sum()
            )
            current_edges = {
                (row.source_taxon_id, row.target_taxon_id): float(row.interaction_count)
                for row in current.itertuples(index=False)
            }
            following_edges = {
                (row.source_taxon_id, row.target_taxon_id): float(row.interaction_count)
                for row in following.itertuples(index=False)
            }
            for source, target in sorted(set(current_edges) | set(following_edges)):
                before = current_edges.get((source, target), 0.0)
                after = following_edges.get((source, target), 0.0)
                if before > 0 and after > 0:
                    status = "persisted"
                elif after > 0:
                    status = "birth"
                else:
                    status = "death"
                rows.append(
                    {
                        "dataset_id": dataset_id,
                        "site_id": site_id,
                        "from_time_bin": left["time_bin"],
                        "to_time_bin": right["time_bin"],
                        "from_sequence": int(left["sequence"]),
                        "to_sequence": int(right["sequence"]),
                        "source_taxon_id": source,
                        "target_taxon_id": target,
                        "edge_status": status,
                        "interaction_count_from": before,
                        "interaction_count_to": after,
                        "interaction_count_delta": after - before,
                        "allowed_claim_level": "observed_rewiring",
                        "evidence_type": "direct_observation",
                    }
                )
    return pd.DataFrame(rows)


def taxon_load_timeseries(interactions: pd.DataFrame) -> pd.DataFrame:
    """Weekly observed interaction load by taxon and guild."""

    plants = (
        interactions.groupby(["dataset_id", "site_id", "time_bin", "sequence", "source_taxon_id"], as_index=False)[
            "interaction_count"
        ]
        .sum()
        .rename(columns={"source_taxon_id": "taxon_id", "interaction_count": "interaction_load"})
        .assign(guild="plant")
    )
    pollinators = (
        interactions.groupby(["dataset_id", "site_id", "time_bin", "sequence", "target_taxon_id"], as_index=False)[
            "interaction_count"
        ]
        .sum()
        .rename(columns={"target_taxon_id": "taxon_id", "interaction_count": "interaction_load"})
        .assign(guild="pollinator")
    )
    return pd.concat([plants, pollinators], ignore_index=True).sort_values(
        ["site_id", "sequence", "guild", "interaction_load"],
        ascending=[True, True, True, False],
    )


def phenology_windows(interactions: pd.DataFrame, plant_presence: pd.DataFrame) -> pd.DataFrame:
    """Observed activity windows from flower counts and visit records only."""

    plant_active = plant_presence[plant_presence["present"]].copy()
    plant_active["year"] = plant_active["time_bin"].str.slice(0, 4).astype(int)
    plant_windows = (
        plant_active.groupby(["site_id", "year", "taxon_id"], as_index=False)
        .agg(
            first_sequence=("sequence", "min"),
            last_sequence=("sequence", "max"),
            first_time_bin=("time_bin", "min"),
            last_time_bin=("time_bin", "max"),
            active_bins=("time_bin", "nunique"),
            total_observed_load=("flower_count", "sum"),
        )
        .assign(guild="plant", evidence_basis="flower_count")
    )
    pollinator_load = taxon_load_timeseries(interactions)
    pollinator_load = pollinator_load[pollinator_load["guild"] == "pollinator"]
    pollinator_load["year"] = pollinator_load["time_bin"].str.slice(0, 4).astype(int)
    pollinator_windows = (
        pollinator_load.groupby(["site_id", "year", "taxon_id"], as_index=False)
        .agg(
            first_sequence=("sequence", "min"),
            last_sequence=("sequence", "max"),
            first_time_bin=("time_bin", "min"),
            last_time_bin=("time_bin", "max"),
            active_bins=("time_bin", "nunique"),
            total_observed_load=("interaction_load", "sum"),
        )
        .assign(guild="pollinator", evidence_basis="observed_visits")
    )
    columns = [
        "site_id",
        "year",
        "taxon_id",
        "guild",
        "first_sequence",
        "last_sequence",
        "first_time_bin",
        "last_time_bin",
        "active_bins",
        "total_observed_load",
        "evidence_basis",
    ]
    return pd.concat([plant_windows[columns], pollinator_windows[columns]], ignore_index=True)


def terminal_summary(
    tables: dict[str, pd.DataFrame],
    registry: pd.DataFrame,
) -> dict:
    interactions = tables["rmbl_interactions"]
    snapshots = tables["rmbl_network_snapshots"]
    signals = tables["decision_signals"]
    events = tables["rmbl_rewiring_events"]
    silent = tables["rmbl_silent_edge_candidates"]
    burkle_contrast = tables["burkle_historical_contrast"]
    gate_counts = registry["rebuild_network_snapshots"].value_counts(dropna=False).to_dict()
    class_counts = signals["classification"].value_counts().to_dict()
    burkle_counts = burkle_contrast["edge_status"].value_counts().to_dict()
    return {
        "rmbl": {
            "observed_visit_records": int(len(interactions)),
            "observed_visit_count": float(interactions["interaction_count"].sum()),
            "unique_observed_edges": int(
                interactions[["source_taxon_id", "target_taxon_id"]].drop_duplicates().shape[0]
            ),
            "weekly_network_snapshots": int(len(snapshots)),
            "transition_decision_signals": int(len(signals)),
            "rewiring_event_records": int(len(events)),
            "candidate_silent_edge_flags": int(len(silent)),
            "sites": sorted(interactions["site_id"].unique().tolist()),
            "years": sorted(interactions["time_bin"].str.slice(0, 4).astype(int).unique().tolist()),
            "date_min": str(pd.to_datetime(interactions["timestamp"]).min().date()),
            "date_max": str(pd.to_datetime(interactions["timestamp"]).max().date()),
            "classification_counts": {str(k): int(v) for k, v in class_counts.items()},
        },
        "burkle": {
            "contrast_edges": int(len(burkle_contrast)),
            "edge_status_counts": {str(k): int(v) for k, v in burkle_counts.items()},
            "allowed_claim_level": "partial_contrast",
        },
        "source_gates": {str(k): int(v) for k, v in gate_counts.items()},
    }


def build_rmbl() -> dict[str, pd.DataFrame]:
    interactions = rmbl.normalize_interactions()
    phenology = rmbl.load_phenology()
    plant_presence = rmbl.flowering_presence(phenology)
    snapshots = build_snapshots(interactions)
    transitions = transition_table(interactions)
    silent = detect_candidates(interactions, plant_presence)
    signals = classify_transitions(transitions, snapshots, silent)
    events = rewiring_events(interactions)
    transition_edges = transition_edge_status(interactions)
    taxon_load = taxon_load_timeseries(interactions)
    phenology = phenology_windows(interactions, plant_presence)
    return {
        "rmbl_interactions": interactions,
        "rmbl_plant_presence": plant_presence,
        "rmbl_network_snapshots": snapshots,
        "rmbl_transition_metrics": transitions,
        "rmbl_transition_edge_status": transition_edges,
        "rmbl_taxon_load_timeseries": taxon_load,
        "rmbl_phenology_windows": phenology,
        "rmbl_silent_edge_candidates": silent,
        "decision_signals": signals,
        "rmbl_rewiring_events": events,
    }


def build_burkle() -> dict[str, pd.DataFrame]:
    contrast = burkle.historical_contrast()
    phenology = burkle.phenology_overlap_loss()
    summary = (
        contrast["edge_status"]
        .value_counts()
        .rename_axis("edge_status")
        .reset_index(name="edge_count")
        .assign(dataset_id="burkle_120yr", allowed_claim_level="partial_contrast")
    )
    return {
        "burkle_historical_contrast": contrast,
        "burkle_phenology_overlap_loss": phenology,
        "burkle_contrast_summary": summary,
    }


def write_outputs(tables: dict[str, pd.DataFrame]) -> None:
    ensure_dirs()
    for name, table in tables.items():
        table.to_csv(PROCESSED / f"{name}.csv", index=False)
    registry = registry_rows(load_source_registry())
    registry.to_csv(PROCESSED / "source_buildability_audit.csv", index=False)
    registry.to_csv(TABLES / "source_buildability_audit.csv", index=False)
    if "decision_signals" in tables:
        summarize_signals(tables["decision_signals"]).to_csv(TABLES / "decision_signal_summary.csv", index=False)
    pd.DataFrame([lazaro.workbook_audit()]).to_csv(TABLES / "lazaro_workbook_audit.csv", index=False)
    if {"rmbl_interactions", "rmbl_network_snapshots", "decision_signals", "rmbl_rewiring_events", "rmbl_silent_edge_candidates", "burkle_historical_contrast"}.issubset(tables):
        SUMMARY_PATH.write_text(json.dumps(terminal_summary(tables, registry), indent=2))


def build_all() -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    tables.update(build_rmbl())
    tables.update(build_burkle())
    write_outputs(tables)
    return tables
