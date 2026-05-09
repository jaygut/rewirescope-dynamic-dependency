# Scientific Library Landscape

This POC uses a conservative Python runtime and documents R libraries as methodological references where they remain the strongest ecological-network tools.

## Runtime Choices

| Need | Primary library | Why it is used |
| --- | --- | --- |
| Tabular data | `pandas` | Mature DataFrame operations, CSV/Excel ingestion, time-series grouping. |
| Numeric methods | `numpy`, `scipy` | Stable numerical substrate for concentration, entropy, and matrix calculations. |
| Graph construction | `networkx` | Direct support for bipartite graph algorithms and transparent graph objects. |
| Visualization | `plotly`, `streamlit` | Interactive graphs and a lightweight data-app runtime in pure Python. |
| Excel audit | `openpyxl` | Workbook inspection for Dryad XLSX sources when downloadable. |
| YAML metadata | `pyyaml` | Evidence gates and source registries stay machine-readable. |

## Method Benchmarks and Optional Extensions

| Method area | Library | Evidence from source search | RewireScope stance |
| --- | --- | --- | --- |
| Ecological bipartite metrics | R `bipartite` | CRAN describes it as visualizing bipartite networks and calculating ecological web indices, especially pollination webs and predator-prey webs. | Benchmark for H2, nestedness, and ecological-web conventions. Python POC implements transparent proxies and flags them as proxies. |
| Community ecology | R `vegan` | CRAN `bipartite` docs explicitly connect bipartite web vectors to community ecology methods such as those in `vegan`. | Useful for future validation, ordination, and null models. |
| General graph analytics | `networkx`, `igraph` | NetworkX official docs include bipartite algorithms; igraph remains a high-performance graph option across Python/R. | NetworkX is used now for clarity; igraph is a future performance path. |
| Time-series models | `statsmodels` | Official docs expose ARIMA and comprehensive state-space tools. | Candidate for forecasting network metrics and phenological drift. |
| Change-point detection | `ruptures` | Official docs position it for change-point detection in Python. | Candidate for regime-shift detection in transition metrics. |
| Causal time series | `tigramite` | Official docs describe PCMCI/PCMCIplus causal discovery for lagged and contemporaneous time-series graphs. | Candidate for inferred dynamic dependency modules; never for observed rewiring claims. |
| Empirical dynamic modeling | `pyEDM` / `rEDM` | Sugihara Lab docs describe EDM as non-parametric nonlinear dynamic-systems modeling based on attractor reconstruction. | Candidate for plankton/fisheries inference when time series are dense enough. |
| Anomaly detection | `scikit-learn` | Official docs include novelty and outlier detection. | Candidate for flagging candidate rewiring anomalies; not used as causal evidence by itself. |

## Sources Consulted

- NetworkX bipartite documentation: https://networkx.org/documentation/stable/reference/algorithms/bipartite.html
- CRAN `bipartite`: https://cran.r-project.org/web/packages/bipartite/
- CRAN `vegan`: https://cran.r-project.org/web/packages/vegan/
- statsmodels time-series documentation: https://www.statsmodels.org/stable/tsa.html
- ruptures documentation: https://centre-for-evaluation-and-monitoring.github.io/ruptures-docs/
- Tigramite documentation: https://jakobrunge.github.io/tigramite/
- pyEDM/rEDM documentation: https://sugiharalab.github.io/EDM_Documentation/
- scikit-learn outlier detection documentation: https://scikit-learn.org/stable/modules/outlier_detection.html
- Streamlit documentation: https://docs.streamlit.io/

## Implementation Boundary

The first version avoids opaque model complexity. It implements directly auditable metrics for edge turnover, species-turnover decomposition, dependency concentration, phenological overlap, silent-edge candidates, and rules-based decision signals. More advanced libraries should enter only when they improve inference while preserving evidence labels and falsification conditions.
