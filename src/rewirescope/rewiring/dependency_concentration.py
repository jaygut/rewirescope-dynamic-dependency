"""Dependency concentration metrics."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def gini(values: pd.Series | np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[arr >= 0]
    if arr.size == 0 or np.all(arr == 0):
        return 0.0
    arr = np.sort(arr)
    n = arr.size
    cumulative = np.cumsum(arr)
    return float((n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n)


def top_share(values: pd.Series | np.ndarray, fraction: float = 0.10) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[arr > 0]
    if arr.size == 0:
        return 0.0
    k = max(1, math.ceil(arr.size * fraction))
    return float(np.sort(arr)[-k:].sum() / arr.sum())


def effective_number(values: pd.Series | np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[arr > 0]
    if arr.size == 0:
        return 0.0
    p = arr / arr.sum()
    return float(math.exp(-np.sum(p * np.log(p))))


def concentration_summary(interactions: pd.DataFrame) -> dict:
    source_load = interactions.groupby("source_taxon_id")["interaction_count"].sum()
    target_load = interactions.groupby("target_taxon_id")["interaction_count"].sum()
    all_load = pd.concat([source_load, target_load])
    return {
        "dependency_gini": gini(all_load),
        "top10_interaction_share": top_share(all_load, 0.10),
        "effective_taxa_load": effective_number(all_load),
    }
