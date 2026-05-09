# RewireScope

**Dynamic dependency intelligence for ecological networks under change.**

RewireScope is an end-to-end proof of concept for **Rewiring Intelligence**:
detecting, classifying, and communicating changes in ecological interaction
architecture through time.

The motivating claim is simple:

> Nature is not declining in place. It is changing shape.

Conventional nature-risk tools often summarize species presence, habitat extent,
or static biodiversity state. RewireScope asks a more operational question:
which ecological dependencies are being born, lost, concentrated, delayed, or
silently failing as environmental and phenological conditions change?

The current proof of concept centers on plant-pollinator systems because they
make the core thesis visible: an ecosystem can retain many of the same species
while its dependency graph changes underneath.

## What the POC Demonstrates

RewireScope turns temporal ecological data into decision signals:

- `adaptive`
- `compensatory-but-fragile`
- `degradative`
- `candidate-silent-edge-failure`
- `unresolved`

The Streamlit terminal shows observed weekly rewiring in the RMBL / CaraDonna
plant-pollinator data, partial historical contrast from Burkle, Marlin, and
Knight, and evidence-gated source modules for datasets that do not yet support
full observed network reconstruction.

## Evidence Boundary

The project is deliberately conservative about scientific claims:

- **Observed temporal rewiring** requires raw pairwise interaction edges across
  repeated time bins.
- **Partial historical contrast** can compare historical and contemporary
  network structure, but does not imply dense temporal animation.
- **Inferred dynamic dependency** can be built from abundance, phenology,
  environmental, or occurrence series, but inferred links are never labeled as
  observed rewiring.
- **Metrics-only sources** support validation and interpretation, not full
  network reconstruction.

This boundary is encoded in
[`data/metadata/source_buildability.yml`](data/metadata/source_buildability.yml)
and surfaced directly in the dashboard.

## Current Data Modules

| Module | Dataset | Claim level | Current role |
| --- | --- | --- | --- |
| `moving_pollination_graph` | RMBL / CaraDonna weekly plant-pollinator interactions | Observed rewiring | Weekly bipartite networks, transition status, rewiring decomposition, phenology, silent-edge candidates |
| `interaction_extinction_archive` | Burkle, Marlin & Knight 120-year plant-pollinator disruption | Partial historical contrast | Historical/contemporary contrast and phenological overlap loss |
| `disturbance_rewiring_gradient` | Lázaro & Gómez-Martínez habitat-loss seasonal rewiring | Pending / partial contrast | Source-gated until workbook inspection supports raw edge-level claims |
| `trophic_timing_engine` | NOAA EcoMon plankton | Inferred dependency only | Source-gated marine timing expansion, no fake association graph |
| `plankton_network_shift` | Helgoland Roads plankton | Inferred dependency only | Source-gated long-term plankton expansion, no fake association graph |

## Repository Layout

```text
app/                 Streamlit intelligence terminal
app/pages/           Interactive evidence-gated dashboard pages
data/metadata/       Dataset registry and claim-level gates
data/raw/            Small public raw/source files available without credentials
docs/                Scientific rationale, dataset inventory, validation notes
scripts/             Data audit, processed-data build, exports
src/rewirescope/     Rewiring, evidence, ingest, metrics, viz, and UI modules
tests/               Unit and smoke tests for data products and terminal loading
outputs/             Reproducible demo/Notion artifacts where intentionally kept
```

Generated processed tables are written to `data/processed/` and are ignored by
git. The app rebuilds them automatically if they are missing.

## Quick Start

Use Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"

python3 scripts/audit_datasets.py
python3 scripts/build_processed_data.py
pytest
streamlit run app/Overview.py
```

The terminal opens at:

```text
http://localhost:8501
```

## Reproducible Figure Exports

The Notion-ready figure exports are generated from local processed data:

```bash
python3 scripts/export_notion_figures.py
```

The current exports live in
[`outputs/notion_figures/`](outputs/notion_figures/) and include the figure
manifest and short scientific legends.

## Data Policy

Raw public data are stored locally only when access is available without
credentials. Derived processed tables are reproducible and ignored by git.
Source-gated modules remain visible in the terminal, but they do not render
analytic charts until real inspected data are available.

No simulated ecological network, fake metric panel, or placeholder analytic
chart is used to support a scientific claim.

## Key Sources

- RMBL / CaraDonna EDI package:
  <https://doi.org/10.6073/pasta/27dc02fe1655e3896f20326fed5cb95f>
- Lázaro and Gómez-Martínez Dryad package:
  <https://doi.org/10.5061/dryad.1ns1rn8x3>
- Burkle, Marlin, and Knight Dryad package:
  <https://doi.org/10.5061/dryad.rp321>
- Burkle Zenodo mirror:
  <https://zenodo.org/records/4948856>
- NOAA EcoMon:
  <https://www.ncei.noaa.gov/archive/accession/0187513>
- Helgoland Roads COPEPOD page:
  <https://www.st.nmfs.noaa.gov/copepod/time-series/de-30201/>

## Status

This is a scientific-demo POC, not a production risk model. The current build is
designed to make the evidence boundary explicit while demonstrating how temporal
interaction data can become an operational rewiring intelligence terminal.
