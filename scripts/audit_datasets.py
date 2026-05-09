#!/usr/bin/env python3
"""Audit local source files and evidence gates."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.audit import audit_csv, load_source_registry, registry_rows
from rewirescope.ingest import lazaro


def main() -> None:
    registry = load_source_registry()
    print(registry_rows(registry).to_string(index=False))
    print()
    print(audit_csv("data/raw/rmbl_caradonna/caradonna_rmbl_interaction_networks_data_EDI.csv", [
        "date", "week_num", "site", "plant", "pollinator", "interactions"
    ]))
    print(audit_csv("data/raw/rmbl_caradonna/caradonna_rmbl_flowering_phenology_data_EDI.csv", [
        "week_num", "site", "plant", "flower_count"
    ]))
    print(audit_csv("data/raw/burkle_120yr/dryad - interactions now.csv", ["plant", "bee", "#sum.ints"]))
    print(lazaro.workbook_audit())


if __name__ == "__main__":
    main()
