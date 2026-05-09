import pandas as pd

from rewirescope.rewiring.edge_turnover import compare_snapshots


def frame(edges):
    return pd.DataFrame(
        [
            {"source_taxon_id": s, "target_taxon_id": t, "interaction_count": 1}
            for s, t in edges
        ]
    )


def test_turnover_separates_rewiring_from_species_turnover():
    current = frame([("p1", "a"), ("p2", "b"), ("p3", "c")])
    following = frame([("p1", "b"), ("p2", "a"), ("p4", "d")])

    result = compare_snapshots(current, following)

    assert result["births"] == 3
    assert result["deaths"] == 3
    assert result["rewiring_edges"] == 4
    assert result["species_turnover_edges"] == 2
    assert result["rewiring_ratio"] == 4 / 6
