# Dataset Inventory

## Green: Observed Rewiring Core

### RMBL / CaraDonna

The EDI metadata and local raw CSV audit confirm the required columns: `date`, `week_num`, `site`, `transect`, `plant`, `pollinator`, and `interactions`. A separate phenology file provides weekly flower counts by site, transect, and plant.

Allowed claim: observed temporal rewiring.

Implemented outputs:

- normalized interaction table;
- weekly bipartite network snapshots;
- transition-level edge turnover;
- species-turnover versus rewiring decomposition;
- dependency concentration;
- phenology-derived silent-edge candidates;
- weekly decision signals.

## Yellow: Disturbance Classification Pending Workbook Inspection

### Lázaro and Gómez-Martínez

Dryad metadata confirms the workbook names and source abstract, but command-line download of the XLSX files was blocked by WAF in this environment. The module remains a build target, but no direct raw-edge reconstruction is claimed until the workbook is inspected.

Allowed claim in current repo: provisional source metadata and planned disturbance-classification workflow only.

## Yellow: Partial Historical Contrast

### Burkle, Marlin, and Knight

Zenodo mirrors the Dryad files and provides contemporary interactions, plant phenology, and bee phenology. The historical edge list used here is a paper-figure reconstruction from Dai Shizuka's worked example, not a raw Dryad historical edge table.

Allowed claim: partial historical contrast. It can show contemporary versus reconstructed historical architecture and phenological overlap loss, but not dense 120-year temporal rewiring.

## Red for Observed Rewiring: Inferred Dynamic Dependency Only

### NOAA EcoMon and Helgoland Roads

Both datasets are valuable long-term plankton and environmental time series. Neither is an observed pairwise interaction network dataset. Any edges built from these sources must be inferred through co-occurrence, lagged association, diet priors, traits, or dynamic models and must carry uncertainty labels.
