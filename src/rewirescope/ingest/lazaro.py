"""Audit-only ingestion path for Lázaro and Gómez-Martínez until workbook inspection."""

from __future__ import annotations

from pathlib import Path

from rewirescope.audit import audit_excel


WORKBOOK = Path("data/raw/lazaro_gomez_martinez/Lazaro_Gomez-Martinez_DryadData.xlsx")


def workbook_audit() -> dict:
    audit = audit_excel(WORKBOOK)
    return {
        "dataset_id": "lazaro_gomez_martinez",
        "workbook": str(WORKBOOK),
        "exists": audit.exists,
        "size_bytes": audit.size_bytes,
        "sheets": list(audit.columns),
        "problem": audit.problem,
        "allowed_claim_level": "partial_contrast",
    }
