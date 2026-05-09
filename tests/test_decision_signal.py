from rewirescope.classify.decision_signal import classify_transition


def test_inferred_sources_cannot_make_observed_rewiring_claims():
    result = classify_transition({"allowed_claim_level": "inferred_dependency", "rewiring_ratio": 1})

    assert result["classification"] == "unresolved"
    assert "observed pairwise temporal edges" in result["evidence_summary"]


def test_degradative_rule():
    result = classify_transition(
        {
            "allowed_claim_level": "observed_rewiring",
            "edges_delta": -5,
            "connectance_delta": -0.1,
            "dependency_gini_delta": 0.1,
            "effective_taxa_load_delta": -2,
        }
    )

    assert result["classification"] == "degradative"


def test_compensatory_fragile_rule():
    result = classify_transition(
        {
            "allowed_claim_level": "observed_rewiring",
            "edges_delta": 0,
            "connectance_delta": 0,
            "dependency_gini_delta": 0.05,
            "effective_taxa_load_delta": -2,
        }
    )

    assert result["classification"] == "compensatory-but-fragile"
