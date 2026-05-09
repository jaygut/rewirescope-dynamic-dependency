"""Rules-based rewiring classification with explicit claim boundaries."""

from __future__ import annotations

import pandas as pd


VALID_CLASSES = {
    "adaptive",
    "compensatory-but-fragile",
    "degradative",
    "silent-edge-failure",
    "unresolved",
}


def classify_transition(row: pd.Series | dict) -> dict:
    r = dict(row)
    allowed = r.get("allowed_claim_level", "observed_rewiring")
    if allowed not in {"observed_rewiring", "partial_contrast"}:
        return {
            "classification": "unresolved",
            "confidence": "low",
            "evidence_summary": "Source does not contain observed pairwise temporal edges; only inferred dependency claims are allowed.",
            "falsification_condition": "Add repeated direct interaction observations for the same taxa and time bins.",
        }

    silent_count = float(r.get("silent_edge_candidates", 0) or 0)
    rewiring_ratio = float(r.get("rewiring_ratio", 0) or 0)
    edge_delta = float(r.get("edges_delta", 0) or 0)
    concentration_delta = float(r.get("dependency_gini_delta", 0) or 0)
    effective_delta = float(r.get("effective_taxa_load_delta", 0) or 0)
    connectance_delta = float(r.get("connectance_delta", 0) or 0)

    if silent_count > 0 and edge_delta <= 0:
        return {
            "classification": "silent-edge-failure",
            "confidence": "medium",
            "evidence_summary": f"{int(silent_count)} expected interactions were absent while endpoint taxa remained active.",
            "falsification_condition": "Targeted observation detects the missing edges during the same phenological window.",
        }

    if edge_delta < 0 and (connectance_delta < 0 or effective_delta < 0) and concentration_delta > 0:
        return {
            "classification": "degradative",
            "confidence": "medium",
            "evidence_summary": "Edges or connectance declined while dependency concentration increased.",
            "falsification_condition": "Sampling-corrected networks show stable redundancy and no concentration increase.",
        }

    if abs(edge_delta) <= 2 and (concentration_delta > 0.02 or effective_delta < -1):
        return {
            "classification": "compensatory-but-fragile",
            "confidence": "medium",
            "evidence_summary": "Interaction volume appears roughly stable but load is concentrating into fewer taxa.",
            "falsification_condition": "Additional observations show stable or broader partner diversity.",
        }

    if rewiring_ratio >= 0.35 and concentration_delta <= 0.02 and effective_delta >= -1:
        return {
            "classification": "adaptive",
            "confidence": "low",
            "evidence_summary": "Partner switching occurred without a material increase in dependency concentration.",
            "falsification_condition": "Substitute partners fail to carry comparable interaction load or function.",
        }

    return {
        "classification": "unresolved",
        "confidence": "low",
        "evidence_summary": "Metrics are mixed or below classification thresholds.",
        "falsification_condition": "Additional repeated observations clarify redundancy, concentration, and missing-edge status.",
    }


def classify_transitions(transitions: pd.DataFrame, snapshots: pd.DataFrame, silent: pd.DataFrame) -> pd.DataFrame:
    if transitions.empty:
        return pd.DataFrame()
    snap = snapshots.set_index(["site_id", "time_bin"])
    silent_counts = (
        silent.groupby(["site_id", "time_bin"]).size().rename("silent_edge_candidates")
        if not silent.empty
        else pd.Series(dtype=int, name="silent_edge_candidates")
    )
    rows = []
    for row in transitions.to_dict(orient="records"):
        site_id = row["site_id"]
        from_key = (site_id, row["from_time_bin"])
        to_key = (site_id, row["to_time_bin"])
        before = snap.loc[from_key]
        after = snap.loc[to_key]
        features = {
            **row,
            "allowed_claim_level": "observed_rewiring",
            "edges_delta": float(after["edges_n"] - before["edges_n"]),
            "connectance_delta": float(after["connectance"] - before["connectance"]),
            "dependency_gini_delta": float(after["dependency_gini"] - before["dependency_gini"]),
            "effective_taxa_load_delta": float(after["effective_taxa_load"] - before["effective_taxa_load"]),
            "silent_edge_candidates": int(silent_counts.get(to_key, 0)),
        }
        signal = classify_transition(features)
        rows.append(
            {
                "signal_id": f"{row['dataset_id']}:{site_id}:{row['from_time_bin']}->{row['to_time_bin']}",
                "dataset_id": row["dataset_id"],
                "site_id": site_id,
                "time_window": f"{row['from_time_bin']} to {row['to_time_bin']}",
                "from_time_bin": row["from_time_bin"],
                "to_time_bin": row["to_time_bin"],
                "function": "pollination_visit_network",
                "allowed_claim_level": "observed_rewiring",
                **features,
                **signal,
            }
        )
    return pd.DataFrame(rows)
