# RewireScope Notion Figure Exports

Generated from local processed real-data tables. No simulated or placeholder data are used.

## Figure 1 — Observed weekly rewiring in an RMBL plant-pollinator network

PNG: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_1.png`  
HTML: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_1.html`

**Legend:** Adjacent weekly RMBL plant-pollinator transition for `shady_point`, `2015-W10` to `2015-W11`, showing observed edge persistence, births, and deaths. Plants are left, pollinators right; line color marks transition status and line weight reflects observed visitation count. This supports the claim that ecological risk can emerge as moving interaction architecture before species inventories visibly fail. Evidence boundary: observed RMBL rewiring only; source table: `rmbl_transition_edge_status.csv`.

## Figure 2 — Dependency concentration as fragile compensation

PNG: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_2.png`  
HTML: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_2.html`

**Legend:** Weekly RMBL structural diagnostics for `shady_point` in `2015` show dependency Gini, top-10 interaction share, effective taxa load, connectance, nestedness, and specialization, with `2015-W11` summarized as a radar profile. The figure supports the claim that rewiring is not automatically resilience: apparent continuity can mask compensatory-but-fragile concentration into fewer taxa or pathways. Evidence boundary: real RMBL network metrics; source table: `rmbl_network_snapshots.csv`.

## Figure 3 — Temporal execution and candidate silent-edge failure

PNG: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_3.png`  
HTML: `/Users/jaygut/Documents/Side_Projects/rewirescope-dynamic-dependency/outputs/notion_figures/rewirescope_figure_3.html`

**Legend:** RMBL flowering windows and pollinator activity windows are paired with candidate silent-edge flags: historically observed plant-pollinator pairs absent in a site-week despite plant flowering and pollinator activity elsewhere. The figure supports the timing claim that species co-presence is insufficient; an edge must execute within the right phenological window to remain functional. Evidence boundary: candidate screening signal only, not proof of causal interaction extinction; source tables: `rmbl_phenology_windows.csv` and `rmbl_silent_edge_candidates.csv`.
