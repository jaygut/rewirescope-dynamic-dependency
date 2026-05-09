"""Decision memo helpers."""

from __future__ import annotations

import pandas as pd


def summarize_signals(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return pd.DataFrame(columns=["classification", "n", "mean_edge_turnover", "mean_rewiring_ratio"])
    return (
        signals.groupby("classification")
        .agg(
            n=("classification", "size"),
            mean_edge_turnover=("edge_turnover", "mean"),
            mean_rewiring_ratio=("rewiring_ratio", "mean"),
        )
        .reset_index()
        .sort_values("n", ascending=False)
    )
