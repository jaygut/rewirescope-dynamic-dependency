"""Human-readable uncertainty labels."""

from __future__ import annotations


def uncertainty_label(allowed_claim_level: str, confidence: str) -> str:
    if allowed_claim_level == "observed_rewiring":
        return f"Observed edge evidence, {confidence} confidence"
    if allowed_claim_level == "partial_contrast":
        return f"Partial contrast evidence, {confidence} confidence"
    if allowed_claim_level == "inferred_dependency":
        return f"Inferred dependency only, {confidence} confidence"
    return f"Metrics-only evidence, {confidence} confidence"
