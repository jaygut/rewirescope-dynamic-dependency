#!/usr/bin/env python3
"""Report the current Lázaro source gate."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.ingest.lazaro import workbook_audit


def main() -> None:
    print(workbook_audit())


if __name__ == "__main__":
    main()
