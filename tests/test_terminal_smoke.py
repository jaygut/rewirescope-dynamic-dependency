import py_compile
from pathlib import Path

import pandas as pd

from rewirescope.terminal_data import load_terminal_summary, load_terminal_tables
from rewirescope.viz import figures


def test_app_pages_compile():
    for path in [Path("app/Overview.py"), *Path("app/pages").glob("*.py")]:
        py_compile.compile(str(path), doraise=True)


def test_terminal_data_loader_has_required_tables():
    tables = load_terminal_tables()
    summary = load_terminal_summary()

    for key in [
        "interactions",
        "snapshots",
        "transition_edges",
        "taxon_load",
        "phenology_windows",
        "signals",
        "silent",
        "burkle_contrast",
    ]:
        assert key in tables
        assert not tables[key].empty
    assert summary["rmbl"]["observed_visit_records"] == len(tables["interactions"])


def test_chart_functions_handle_empty_data():
    empty = pd.DataFrame()

    assert figures.empty_figure()
    assert figures.burkle_contrast_bars(empty)
    assert figures.evidence_gate_matrix(empty)
