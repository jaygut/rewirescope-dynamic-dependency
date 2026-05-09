"""Bipartite network utilities."""

from __future__ import annotations

import networkx as nx
import pandas as pd


def edge_table(df: pd.DataFrame) -> pd.DataFrame:
    required = {"source_taxon_id", "target_taxon_id", "interaction_count"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing edge columns: {sorted(missing)}")
    return (
        df.groupby(["source_taxon_id", "target_taxon_id"], as_index=False)["interaction_count"]
        .sum()
        .query("interaction_count > 0")
    )


def build_bipartite_graph(df: pd.DataFrame) -> nx.Graph:
    edges = edge_table(df)
    graph = nx.Graph()
    plants = sorted(edges["source_taxon_id"].unique())
    pollinators = sorted(edges["target_taxon_id"].unique())
    graph.add_nodes_from(plants, bipartite=0, guild="plant")
    graph.add_nodes_from(pollinators, bipartite=1, guild="pollinator")
    for row in edges.itertuples(index=False):
        graph.add_edge(row.source_taxon_id, row.target_taxon_id, weight=float(row.interaction_count))
    return graph


def adjacency_matrix(df: pd.DataFrame) -> pd.DataFrame:
    edges = edge_table(df)
    if edges.empty:
        return pd.DataFrame()
    matrix = edges.pivot_table(
        index="source_taxon_id",
        columns="target_taxon_id",
        values="interaction_count",
        aggfunc="sum",
        fill_value=0,
    )
    return matrix.sort_index().sort_index(axis=1)


def snapshot_edges(df: pd.DataFrame) -> set[tuple[str, str]]:
    edges = edge_table(df)
    return set(zip(edges["source_taxon_id"], edges["target_taxon_id"], strict=False))


def snapshot_nodes(df: pd.DataFrame) -> set[str]:
    edges = edge_table(df)
    return set(edges["source_taxon_id"]).union(set(edges["target_taxon_id"]))
