"""Dataset audit helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import yaml


@dataclass(frozen=True)
class FileAudit:
    path: str
    exists: bool
    size_bytes: int
    columns: tuple[str, ...] = ()
    rows: int | None = None
    problem: str | None = None


def load_source_registry(path: str | Path = "data/metadata/source_buildability.yml") -> dict:
    with Path(path).open() as handle:
        return yaml.safe_load(handle)


def audit_csv(path: str | Path, required_columns: Iterable[str] = ()) -> FileAudit:
    path = Path(path)
    if not path.exists():
        return FileAudit(str(path), False, 0, problem="missing")
    size = path.stat().st_size
    try:
        df = pd.read_csv(path, nrows=1000)
    except Exception as exc:  # pragma: no cover - defensive audit path
        return FileAudit(str(path), True, size, problem=str(exc))
    missing = [column for column in required_columns if column not in df.columns]
    problem = f"missing columns: {missing}" if missing else None
    rows = sum(1 for _ in path.open(encoding="utf-8", errors="ignore")) - 1
    return FileAudit(str(path), True, size, tuple(df.columns), rows, problem)


def audit_excel(path: str | Path) -> FileAudit:
    path = Path(path)
    if not path.exists():
        return FileAudit(str(path), False, 0, problem="missing")
    size = path.stat().st_size
    try:
        excel = pd.ExcelFile(path)
    except Exception as exc:
        return FileAudit(str(path), True, size, problem=str(exc))
    return FileAudit(str(path), True, size, tuple(excel.sheet_names), None, None)


def registry_rows(registry: dict) -> pd.DataFrame:
    rows = []
    for dataset_id, item in registry.items():
        rows.append(
            {
                "dataset_id": dataset_id,
                "title": item.get("title"),
                "allowed_claim_level": item.get("allowed_claim_level"),
                "rebuild_network_snapshots": item.get("rebuild_network_snapshots"),
                "visualize_rewiring_events": item.get("visualize_rewiring_events"),
                "observed_pairwise_edges": item.get("observed_pairwise_edges"),
                "repeated_time_bins": item.get("repeated_time_bins"),
                "raw_interaction_counts": item.get("raw_interaction_counts"),
                "audit_notes": item.get("audit_notes"),
            }
        )
    return pd.DataFrame(rows)
