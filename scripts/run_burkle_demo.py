#!/usr/bin/env python3
"""Build and summarize the Burkle partial historical contrast demo."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.demo import build_burkle, write_outputs


def main() -> None:
    tables = build_burkle()
    write_outputs(tables)
    for name, table in tables.items():
        print(f"{name}: {len(table):,} rows")


if __name__ == "__main__":
    main()
