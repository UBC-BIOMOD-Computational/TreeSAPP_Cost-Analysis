from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chemistry import amplification_gate
from compare_diagnostics import parse_args, run
from inputs_loader import AppConfig, EffectivenessWeights, load_config
from uncertainty import triangular_sample

ROOT = Path(__file__).resolve().parents[1]


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1"):
        EffectivenessWeights(
            accuracy=0.5,
            turnaround=0.5,
            feasibility=0.5,
            invasiveness=0.0,
            regulatory_burden=0.0,
        )


def test_monte_carlo_reproducible_with_seed():
    rng_a = np.random.default_rng(42)
    rng_b = np.random.default_rng(42)
    a = triangular_sample(rng_a, 1.0, 2.0, 4.0, 500)
    b = triangular_sample(rng_b, 1.0, 2.0, 4.0, 500)
    np.testing.assert_array_equal(a, b)


def test_config_loads():
    cfg = load_config(ROOT / "config.yaml")
    assert isinstance(cfg, AppConfig)
    assert cfg.target_price_year == 2026


def test_cli_placeholder_run(tmp_path, monkeypatch):
    out = tmp_path / "outputs"
    args = parse_args(
        [
            "--costs",
            str(ROOT / "inputs" / "cost_assumptions.csv"),
            "--performance",
            str(ROOT / "inputs" / "performance_assumptions.csv"),
            "--config",
            str(ROOT / "config.yaml"),
            "--scenario",
            "all",
            "--output",
            str(out),
        ]
    )
    # Keep the integration test fast.
    monkeypatch.setattr("compare_diagnostics.load_config", lambda path: _fast_config())
    run(args)
    for name in [
        "cost_table.csv",
        "cost_table.xlsx",
        "comparison_summary.csv",
        "breakeven.csv",
        "monte_carlo_results.csv",
        "report.md",
    ]:
        assert (out / name).exists(), name
    figures = [
        "cost_vs_n.png",
        "stacked_fixed_variable.png",
        "cost_per_test_by_scale.png",
        "cost_vs_effectiveness.png",
        "monte_carlo_win_probabilities.png",
        "tornado_N1000.png",
        "tornado_N50000.png",
    ]
    for name in figures:
        assert (out / "figures" / name).exists(), name
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "replace with vendor quote" in report
    table = pd.read_csv(out / "cost_table.csv")
    assert "Type" in table.columns
    assert "Scale" in table.columns
    assert "Cost to get sample (fixed, 2026 USD)" in table.columns


def _fast_config():
    cfg = load_config(ROOT / "config.yaml")
    cfg.monte_carlo["n_draws"] = 200
    return cfg


def test_gel_gate_uses_entered_units():
    cfg = load_config(ROOT / "config.yaml")
    gate = amplification_gate(cfg.gel_chemistry, "base")
    assert "pM" in gate["expected_entered"]
    assert gate["literature_nM"] == pytest.approx(50.0)
    assert gate["device_nM"] > gate["literature_nM"]
