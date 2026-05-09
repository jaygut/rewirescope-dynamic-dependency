#!/usr/bin/env python3
"""Print NOAA EcoMon source boundary."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.ingest.ecomon import SOURCE


def main() -> None:
    print(SOURCE)


if __name__ == "__main__":
    main()
