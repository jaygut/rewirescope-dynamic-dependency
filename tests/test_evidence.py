import pytest

from rewirescope.evidence import ClaimLevel, EvidenceGate, EvidenceType, enforce_observed_rewiring


def test_evidence_gate_blocks_inferred_rewiring_claims():
    gate = EvidenceGate(
        dataset_id="plankton",
        allowed_claim_level=ClaimLevel.INFERRED_DEPENDENCY,
        evidence_type=EvidenceType.TRAIT_OR_ASSOCIATION_INFERENCE,
        observed_pairwise_edges=False,
        repeated_time_bins=True,
        raw_interaction_counts=False,
    )

    with pytest.raises(ValueError):
        enforce_observed_rewiring(gate)
