import pandas as pd

from rewirescope.rewiring.dependency_concentration import concentration_summary, effective_number, gini, top_share


def test_concentration_metrics_for_even_loads():
    values = pd.Series([1, 1, 1, 1])

    assert gini(values) == 0
    assert top_share(values, 0.25) == 0.25
    assert round(effective_number(values), 6) == 4


def test_concentration_summary_detects_uneven_load():
    df = pd.DataFrame(
        [
            {"source_taxon_id": "p1", "target_taxon_id": "a", "interaction_count": 100},
            {"source_taxon_id": "p1", "target_taxon_id": "b", "interaction_count": 1},
            {"source_taxon_id": "p2", "target_taxon_id": "a", "interaction_count": 1},
        ]
    )

    summary = concentration_summary(df)

    assert summary["dependency_gini"] > 0
    assert summary["top10_interaction_share"] > 0.49
