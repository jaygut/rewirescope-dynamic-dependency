"""Evidence gates and allowed claim levels."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ClaimLevel(StrEnum):
    OBSERVED_REWIRING = "observed_rewiring"
    PARTIAL_CONTRAST = "partial_contrast"
    INFERRED_DEPENDENCY = "inferred_dependency"
    METRICS_ONLY = "metrics_only"


class EvidenceType(StrEnum):
    DIRECT_OBSERVATION = "direct_observation"
    PAPER_FIGURE_RECONSTRUCTION = "paper_figure_reconstruction"
    TRAIT_OR_ASSOCIATION_INFERENCE = "trait_or_association_inference"
    DERIVED_METRIC = "derived_metric"


@dataclass(frozen=True)
class EvidenceGate:
    dataset_id: str
    allowed_claim_level: ClaimLevel
    evidence_type: EvidenceType
    observed_pairwise_edges: bool
    repeated_time_bins: bool
    raw_interaction_counts: bool
    notes: str = ""

    @property
    def can_visualize_observed_rewiring(self) -> bool:
        return (
            self.allowed_claim_level == ClaimLevel.OBSERVED_REWIRING
            and self.observed_pairwise_edges
            and self.repeated_time_bins
            and self.raw_interaction_counts
        )

    @property
    def edge_label(self) -> str:
        if self.allowed_claim_level == ClaimLevel.OBSERVED_REWIRING:
            return "observed"
        if self.allowed_claim_level == ClaimLevel.PARTIAL_CONTRAST:
            return "observed/partially reconstructed"
        if self.allowed_claim_level == ClaimLevel.INFERRED_DEPENDENCY:
            return "inferred"
        return "metrics-only"


def enforce_observed_rewiring(gate: EvidenceGate) -> None:
    """Raise if a dataset is not allowed to make observed rewiring claims."""

    if not gate.can_visualize_observed_rewiring:
        raise ValueError(
            f"{gate.dataset_id} is {gate.allowed_claim_level}; "
            "it cannot be described as observed temporal rewiring."
        )
