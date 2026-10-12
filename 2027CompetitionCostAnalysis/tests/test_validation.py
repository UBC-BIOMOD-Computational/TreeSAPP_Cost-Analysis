from pathlib import Path

import pandas as pd
import pytest

from inputs_loader import load_cost_assumptions, load_performance


def test_missing_cost_columns(tmp_path):
    path = tmp_path / "costs.csv"
    pd.DataFrame({"diagnostic": ["Gel"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="case|missing columns"):
        load_cost_assumptions(path)


def test_negative_cost_rejected(tmp_path):
    src = Path(__file__).resolve().parents[1] / "inputs" / "cost_assumptions.csv"
    df = pd.read_csv(src)
    df.loc[0, "sample_cost_var"] = -1
    path = tmp_path / "costs.csv"
    df.to_csv(path, index=False)
    with pytest.raises(Exception, match="negative"):
        load_cost_assumptions(path)


def test_low_base_high_order(tmp_path):
    src = Path(__file__).resolve().parents[1] / "inputs" / "cost_assumptions.csv"
    df = pd.read_csv(src)
    mask = (df["diagnostic"] == "Gel") & (df["scale"] == 1000) & (df["case"] == "low")
    df.loc[mask, "sample_cost_var"] = 999
    path = tmp_path / "costs.csv"
    df.to_csv(path, index=False)
    with pytest.raises(ValueError, match="out of order"):
        load_cost_assumptions(path)


def test_performance_missing_columns(tmp_path):
    path = tmp_path / "perf.csv"
    pd.DataFrame({"diagnostic": ["Gel"]}).to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_performance(path)
