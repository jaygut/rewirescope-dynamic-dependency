# Metric Definitions

## Edge Turnover

For adjacent time bins, edge turnover is:

```text
1 - |E_t intersect E_t+1| / |E_t union E_t+1|
```

The implementation reports births, deaths, persistence, and total union size.

## Rewiring Among Persistent Species

Changed edges are split into:

- species-turnover edges, where at least one endpoint is absent from either adjacent time bin;
- rewiring edges, where both endpoints are present in both bins but the specific interaction appears or disappears.

This prevents species turnover from being mistaken for partner switching.

## Dependency Concentration

Dependency concentration is measured with:

- Gini coefficient of interaction load by taxon;
- share of total interaction load carried by the top 10 percent of taxa;
- effective number of interaction partners based on Shannon entropy.

Higher concentration can indicate compensatory-but-fragile rewiring when function appears stable but fewer taxa carry the interaction load.

## Phenological Overlap

For two taxa with activity windows:

```text
overlap = max(0, min(end_a, end_b) - max(start_a, start_b) + 1)
```

RMBL uses weekly windows. Burkle uses day-of-year windows.

## Silent Edge Failure Candidate

A candidate is flagged when:

- an expected or historical interaction exists;
- both endpoint taxa are present or active in the current period;
- the edge is absent or drops below the configured threshold;
- the allowed claim level is observed rewiring or partial historical contrast.

The label is "candidate" because absence of observed visits can reflect sampling incompleteness.

## Decision Signal

Rules-based first version:

- adaptive: rewiring occurs while redundancy is stable or improving and dependency concentration is stable or lower;
- compensatory-but-fragile: apparent function is stable, but concentration rises or effective partner diversity declines;
- degradative: edge count, connectance, or partner diversity decline while concentration rises;
- candidate-silent-edge-failure: expected interactions are absent while taxa remain active; this is a candidate flag, not proof of causal interaction extinction;
- unresolved: evidence is insufficient or mixed.
