"""Network metric calculations with transparent ecological proxies."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from rewirescope.networks.bipartite import adjacency_matrix


def connectance(matrix: pd.DataFrame) -> float:
    if matrix.empty:
        return 0.0
    possible = matrix.shape[0] * matrix.shape[1]
    if possible == 0:
        return 0.0
    return float((matrix > 0).sum().sum() / possible)


def shannon_effective_partners(weights: pd.Series | np.ndarray) -> float:
    values = np.asarray(weights, dtype=float)
    values = values[values > 0]
    if values.size == 0:
        return 0.0
    probabilities = values / values.sum()
    entropy = -float(np.sum(probabilities * np.log(probabilities)))
    return float(math.exp(entropy))


def specialization_proxy(matrix: pd.DataFrame) -> float:
    """Return a 0-1 proxy where higher means interaction load is more specialized.

    This is not H2'. It is a transparent proxy based on the gap between observed
    effective partners and the maximum possible partner count.
    """

    if matrix.empty:
        return 0.0
    values = []
    for _, row in matrix.iterrows():
        if row.sum() > 0 and matrix.shape[1] > 1:
            eff = shannon_effective_partners(row.values)
            values.append(1 - ((eff - 1) / (matrix.shape[1] - 1)))
    for _, col in matrix.items():
        if col.sum() > 0 and matrix.shape[0] > 1:
            eff = shannon_effective_partners(col.values)
            values.append(1 - ((eff - 1) / (matrix.shape[0] - 1)))
    return float(np.mean(values)) if values else 0.0


def nestedness_proxy(matrix: pd.DataFrame) -> float:
    """Approximate binary NODF-like nestedness on a 0-1 scale."""

    if matrix.empty:
        return 0.0
    binary = (matrix.values > 0).astype(int)
    scores: list[float] = []
    for axis_matrix in (binary, binary.T):
        degrees = axis_matrix.sum(axis=1)
        for i in range(axis_matrix.shape[0]):
            for j in range(i + 1, axis_matrix.shape[0]):
                high, low = (i, j) if degrees[i] >= degrees[j] else (j, i)
                if degrees[low] == 0 or degrees[high] == degrees[low]:
                    continue
                overlap = np.logical_and(axis_matrix[high] > 0, axis_matrix[low] > 0).sum()
                scores.append(float(overlap / degrees[low]))
    return float(np.mean(scores)) if scores else 0.0


def snapshot_metrics(df: pd.DataFrame) -> dict:
    matrix = adjacency_matrix(df)
    plants_n = int(matrix.shape[0]) if not matrix.empty else 0
    pollinators_n = int(matrix.shape[1]) if not matrix.empty else 0
    edges_n = int((matrix > 0).sum().sum()) if not matrix.empty else 0
    total_weight = float(matrix.values.sum()) if not matrix.empty else 0.0
    return {
        "plants_n": plants_n,
        "pollinators_n": pollinators_n,
        "nodes_n": plants_n + pollinators_n,
        "edges_n": edges_n,
        "interaction_weight": total_weight,
        "connectance": connectance(matrix),
        "nestedness_proxy": nestedness_proxy(matrix),
        "specialization_proxy": specialization_proxy(matrix),
    }
