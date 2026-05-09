# Classification Schema

Each decision signal contains:

- `classification`: adaptive, compensatory-but-fragile, degradative, silent-edge-failure, or unresolved;
- `confidence`: low, medium, or high;
- `allowed_claim_level`: observed_rewiring, partial_contrast, inferred_dependency, or metrics_only;
- `evidence_summary`: the quantitative reason for the classification;
- `falsification_condition`: what observation would weaken the claim.

Evidence gates override metric confidence. For example, NOAA EcoMon can produce an inferred dependency signal, but it cannot produce an observed rewiring signal unless direct pairwise interactions are added.
