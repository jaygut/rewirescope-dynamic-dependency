#!/usr/bin/env python3
"""Download public data sources that are accessible without credentials."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.request import urlretrieve

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


DOWNLOADS = {
    "data/raw/rmbl_caradonna/caradonna_rmbl_interaction_networks_data_EDI.csv": "https://pasta.lternet.edu/package/data/eml/edi/512/1/bb87318745d9b83f102aa0a58e9b5386",
    "data/raw/rmbl_caradonna/caradonna_rmbl_flowering_phenology_data_EDI.csv": "https://pasta.lternet.edu/package/data/eml/edi/512/1/c858be23bac4b5f93b830bcbdac6ba2c",
    "data/raw/rmbl_caradonna/edi_512_1_metadata.xml": "https://pasta.lternet.edu/package/metadata/eml/edi/512/1",
    "data/raw/burkle_120yr/dryad - interactions now.csv": "https://zenodo.org/records/4948856/files/dryad%20-%20interactions%20now.csv?download=1",
    "data/raw/burkle_120yr/dryad - bee phen.csv": "https://zenodo.org/records/4948856/files/dryad%20-%20bee%20phen.csv?download=1",
    "data/raw/burkle_120yr/dryad - plant phen.csv": "https://zenodo.org/records/4948856/files/dryad%20-%20plant%20phen.csv?download=1",
    "data/raw/burkle_120yr/old_edgelist_paper_figure_reconstruction.csv": "https://dshizuka.github.io/networkanalysis/SampleData/Burkle2013/old_edgelist.csv",
}


def main() -> None:
    for target, url in DOWNLOADS.items():
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.stat().st_size > 100:
            print(f"exists: {path}")
            continue
        print(f"download: {path}")
        urlretrieve(url, path)


if __name__ == "__main__":
    main()
