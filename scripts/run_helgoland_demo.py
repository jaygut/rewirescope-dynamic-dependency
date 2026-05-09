#!/usr/bin/env python3
"""Print Helgoland Roads source boundary."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rewirescope.ingest.helgoland import SOURCE


def main() -> None:
    print(SOURCE)


if __name__ == "__main__":
    main()
