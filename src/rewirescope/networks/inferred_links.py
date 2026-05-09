"""Inferred association network helpers.

These helpers are intentionally labeled as inference utilities and are not used
to make observed rewiring claims.
"""

from __future__ import annotations

import pandas as pd


def rolling_correlation_edges(
    table: pd.DataFrame,
    *,
    time_column: str,
    value_columns: list[str],
    window: int,
    min_abs_correlation: float = 0.6,
) -> pd.DataFrame:
    rows = []
    ordered = table.sort_values(time_column)
    for end_idx in range(window, len(ordered) + 1):
        chunk = ordered.iloc[end_idx - window : end_idx]
        corr = chunk[value_columns].corr()
        time_bin = str(chunk[time_column].iloc[-1])
        for i, source in enumerate(value_columns):
            for target in value_columns[i + 1 :]:
                value = corr.loc[source, target]
                if pd.notna(value) and abs(value) >= min_abs_correlation:
                    rows.append(
                        {
                            "time_bin": time_bin,
                            "source_taxon_id": source,
                            "target_taxon_id": target,
                            "interaction_strength": float(value),
                            "evidence_type": "statistical_association",
                            "confidence": "low",
                            "allowed_claim_level": "inferred_dependency",
                        }
                    )
    return pd.DataFrame(rows)
