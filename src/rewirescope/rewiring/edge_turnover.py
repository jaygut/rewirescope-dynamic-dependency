"""Edge turnover and species-turnover decomposition."""

from __future__ import annotations

import pandas as pd

from rewirescope.networks.bipartite import snapshot_edges, snapshot_nodes


def compare_snapshots(current: pd.DataFrame, following: pd.DataFrame) -> dict:
    edges_t = snapshot_edges(current)
    edges_next = snapshot_edges(following)
    nodes_t = snapshot_nodes(current)
    nodes_next = snapshot_nodes(following)
    persistent_nodes = nodes_t & nodes_next
    shared_edges = edges_t & edges_next
    births = edges_next - edges_t
    deaths = edges_t - edges_next
    changed = births | deaths
    rewiring_edges = {
        edge for edge in changed if edge[0] in persistent_nodes and edge[1] in persistent_nodes
    }
    species_turnover_edges = changed - rewiring_edges
    union_edges = edges_t | edges_next
    changed_n = len(changed)
    return {
        "edges_t": len(edges_t),
        "edges_next": len(edges_next),
        "shared_edges": len(shared_edges),
        "births": len(births),
        "deaths": len(deaths),
        "changed_edges": changed_n,
        "rewiring_edges": len(rewiring_edges),
        "species_turnover_edges": len(species_turnover_edges),
        "edge_turnover": 1 - (len(shared_edges) / len(union_edges)) if union_edges else 0.0,
        "rewiring_ratio": len(rewiring_edges) / changed_n if changed_n else 0.0,
        "species_turnover_ratio": len(species_turnover_edges) / changed_n if changed_n else 0.0,
    }


def transition_table(interactions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["dataset_id", "site_id"]
    for (dataset_id, site_id), group in interactions.groupby(group_cols, sort=True):
        ordered_bins = (
            group[["time_bin", "sequence"]]
            .drop_duplicates()
            .sort_values("sequence")
            .reset_index(drop=True)
        )
        for idx in range(len(ordered_bins) - 1):
            left = ordered_bins.iloc[idx]
            right = ordered_bins.iloc[idx + 1]
            current = group[group["time_bin"] == left["time_bin"]]
            following = group[group["time_bin"] == right["time_bin"]]
            metrics = compare_snapshots(current, following)
            rows.append(
                {
                    "dataset_id": dataset_id,
                    "site_id": site_id,
                    "from_time_bin": left["time_bin"],
                    "to_time_bin": right["time_bin"],
                    "from_sequence": int(left["sequence"]),
                    "to_sequence": int(right["sequence"]),
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def rewiring_events(interactions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (dataset_id, site_id), group in interactions.groupby(["dataset_id", "site_id"], sort=True):
        ordered_bins = (
            group[["time_bin", "sequence"]]
            .drop_duplicates()
            .sort_values("sequence")
            .reset_index(drop=True)
        )
        for idx in range(len(ordered_bins) - 1):
            left = ordered_bins.iloc[idx]
            right = ordered_bins.iloc[idx + 1]
            current = group[group["time_bin"] == left["time_bin"]]
            following = group[group["time_bin"] == right["time_bin"]]
            edges_t = snapshot_edges(current)
            edges_next = snapshot_edges(following)
            nodes_t = snapshot_nodes(current)
            nodes_next = snapshot_nodes(following)
            persistent_nodes = nodes_t & nodes_next
            for event_type, edge_set in {"birth": edges_next - edges_t, "death": edges_t - edges_next}.items():
                for source, target in sorted(edge_set):
                    mechanism = (
                        "partner_switching_among_persistent_taxa"
                        if source in persistent_nodes and target in persistent_nodes
                        else "species_turnover_or_observation_window_change"
                    )
                    rows.append(
                        {
                            "event_id": f"{dataset_id}:{site_id}:{left['time_bin']}:{right['time_bin']}:{event_type}:{source}:{target}",
                            "dataset_id": dataset_id,
                            "site_id": site_id,
                            "from_time_bin": left["time_bin"],
                            "to_time_bin": right["time_bin"],
                            "event_type": event_type,
                            "source_taxon_id": source,
                            "target_taxon_id": target,
                            "mechanism_hypothesis": mechanism,
                            "allowed_claim_level": "observed_rewiring",
                            "confidence": "medium",
                        }
                    )
    return pd.DataFrame(rows)
