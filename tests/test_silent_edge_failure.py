import pandas as pd

from rewirescope.rewiring.silent_edge_failure import detect_candidates


def test_detects_expected_edge_absent_when_taxa_active():
    interactions = pd.DataFrame(
        [
            {
                "site_id": "s1",
                "time_bin": "2020-W01",
                "sequence": 1,
                "source_taxon_id": "plant_a",
                "target_taxon_id": "poll_x",
                "interaction_count": 1,
            },
            {
                "site_id": "s1",
                "time_bin": "2020-W02",
                "sequence": 2,
                "source_taxon_id": "plant_b",
                "target_taxon_id": "poll_x",
                "interaction_count": 1,
            },
        ]
    )
    plant_presence = pd.DataFrame(
        [
            {"site_id": "s1", "time_bin": "2020-W02", "sequence": 2, "taxon_id": "plant_a", "present": True},
            {"site_id": "s1", "time_bin": "2020-W02", "sequence": 2, "taxon_id": "plant_b", "present": True},
        ]
    )

    candidates = detect_candidates(interactions, plant_presence, {("plant_a", "poll_x")})

    assert len(candidates) == 1
    assert candidates.iloc[0]["source_taxon_id"] == "plant_a"
