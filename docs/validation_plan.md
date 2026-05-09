# Validation Plan

## Current Verification

- Unit tests validate turnover decomposition, dependency concentration, silent-edge candidates, and decision-signal rules.
- The dataset audit checks local file existence and key columns.
- The processed-data build must produce non-empty RMBL transition metrics and Burkle contrast outputs.

## Scientific Validation Targets

- Compare RMBL turnover and rewiring decomposition against published CaraDonna patterns.
- Inspect Lázaro workbook once available and reproduce the relationship between habitat loss, rewiring frequency, nestedness, and specialization.
- Keep Burkle historical reconstruction labeled as partial contrast unless raw historical edge tables are acquired.
- Use null models before interpreting inferred marine association networks as ecological dependency hypotheses.

## Falsification Discipline

Every decision signal should state what would weaken it. Examples:

- Adaptive claims weaken if substitute partners do not preserve interaction load or function proxies.
- Compensatory claims weaken if redundancy does not decline after sampling correction.
- Degradative claims weaken if null models show the same simplification under sampling effort alone.
- Silent-edge claims weaken if targeted observation detects the supposedly missing edge during the relevant phenological window.
