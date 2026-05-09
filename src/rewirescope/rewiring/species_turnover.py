"""Species turnover helpers."""

from __future__ import annotations

import pandas as pd

from rewirescope.networks.bipartite import snapshot_nodes


def node_turnover(current: pd.DataFrame, following: pd.DataFrame) -> dict:
    nodes_t = snapshot_nodes(current)
    nodes_next = snapshot_nodes(following)
    union = nodes_t | nodes_next
    shared = nodes_t & nodes_next
    return {
        "nodes_t": len(nodes_t),
        "nodes_next": len(nodes_next),
        "shared_nodes": len(shared),
        "node_turnover": 1 - len(shared) / len(union) if union else 0.0,
    }
