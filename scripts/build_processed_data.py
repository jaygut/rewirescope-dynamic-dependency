#!/usr/bin/env python3
"""Build processed RewireScope data products."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.demo import build_all


def main() -> None:
    tables = build_all()
    for name, table in tables.items():
        print(f"{name}: {len(table):,} rows")


if __name__ == "__main__":
    main()
