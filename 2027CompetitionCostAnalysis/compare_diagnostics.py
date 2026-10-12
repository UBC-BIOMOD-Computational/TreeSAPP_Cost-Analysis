#!/usr/bin/env python3
"""Compare Gel, Protein, Sequencing (outsourced and in-house), and SNP diagnostics."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from chemistry import amplification_gate
from inputs_loader import (
    inflate_cost_frame,
    load_config,
    load_cost_assumptions,
    load_performance,
    select_case,
)
from plots import write_all_figures
from report import write_report
from uncertainty import evaluate_options, monte_carlo, pairwise_breakeven, tornado_sensitivity

ROOT = Path(__file__).resolve().parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Diagnostic cost and effectiveness comparison")
    p.add_argument("--costs", type=Path, default=ROOT / "inputs" / "cost_assumptions.csv")
    p.add_argument("--performance", type=Path, default=ROOT / "inputs" / "performance_assumptions.csv")
    p.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    p.add_argument("--scenario", choices=["base", "low", "high", "all"], default="all")
    p.add_argument("--output", type=Path, default=ROOT / "outputs")
    p.add_argument("--scales", nargs="+", type=int, default=None)
    p.add_argument("--no-montecarlo", action="store_true")
    p.add_argument("--export-xlsx", action="store_true", default=True)
    p.add_argument("--exclude", nargs="+", default=[], help="Diagnostic names to drop, e.g. Sequencing")
    return p.parse_args(argv)


def _filter_excludes(costs: pd.DataFrame, performance: pd.DataFrame, exclude: list[str]):
    drop = {e.lower() for e in exclude}
    costs = costs[~costs["diagnostic"].str.lower().isin(drop)].copy()
    performance = performance[~performance["diagnostic"].str.lower().isin(drop)].copy()
    if costs.empty:
        raise ValueError("All diagnostics were excluded")
    return costs, performance


def cost_table_view(scored: pd.DataFrame) -> pd.DataFrame:
    table = scored.rename(
        columns={
            "option": "Type",
            "scale": "Scale",
            "sample_time_fixed_days": "Time to get sample (fixed, days)",
            "sample_time_var_min": "Time to get sample (variable, min)",
            "read_time_fixed_days": "Time to read diagnostic (fixed, days)",
            "read_time_var_min": "Time to read diagnostic (variable, min)",
            "sample_cost_fixed": "Cost to get sample (fixed, 2026 USD)",
            "sample_cost_var": "Cost to get sample (variable, 2026 USD)",
            "read_cost_fixed": "Cost to read diagnostic (fixed, 2026 USD)",
            "read_cost_var": "Cost to read diagnostic (variable, 2026 USD)",
            "total_fixed": "Total fixed (2026 USD)",
            "var_per_test": "Variable cost per test incl. QC (2026 USD)",
            "total_cost": "Total cost (2026 USD)",
            "cost_per_test": "Cost per test (2026 USD)",
            "total_time_days": "Total elapsed time (days)",
        }
    )
    cols = [
        "Type",
        "Scale",
        "scenario",
        "sample_type",
        "Time to get sample (fixed, days)",
        "Time to get sample (variable, min)",
        "Time to read diagnostic (fixed, days)",
        "Time to read diagnostic (variable, min)",
        "Cost to get sample (fixed, 2026 USD)",
        "Cost to get sample (variable, 2026 USD)",
        "Cost to read diagnostic (fixed, 2026 USD)",
        "Cost to read diagnostic (variable, 2026 USD)",
        "Total fixed (2026 USD)",
        "Variable cost per test incl. QC (2026 USD)",
        "Total cost (2026 USD)",
        "Cost per test (2026 USD)",
        "Total elapsed time (days)",
        "feasibility_gate",
        "placeholder",
        "confidence",
        "source",
    ]
    return table[cols]


def comparison_summary_view(scored: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "option",
        "scale",
        "scenario",
        "cost_per_test",
        "total_cost",
        "total_time_days",
        "accuracy",
        "cost_per_correct_result",
        "cost_per_true_positive",
        "effectiveness_score",
        "overall_score",
        "rank_cost",
        "rank_effectiveness",
        "rank_overall",
        "feasibility_gate",
        "eligible_best_overall",
        "placeholder",
        "confidence",
    ]
    return scored[cols].sort_values(["scenario", "scale", "rank_cost"])


def run(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    costs_raw = load_cost_assumptions(args.costs)
    performance = load_performance(args.performance)
    costs_raw, performance = _filter_excludes(costs_raw, performance, args.exclude)
    costs = inflate_cost_frame(costs_raw, config)
    scales = args.scales if args.scales else list(config.scales)
    missing = [s for s in scales if s not in set(costs["scale"].astype(int))]
    if missing:
        raise ValueError(f"No cost rows for scales {missing}")

    scenarios = ["low", "base", "high"] if args.scenario == "all" else [args.scenario]
    gel_gates = [amplification_gate(config.gel_chemistry, case) for case in scenarios]
    gel_by_case = {g["case"]: g for g in gel_gates}
    excluded_gates = list(config.exclude_from_best_overall_gates)
    eff_w = config.effectiveness_weights.model_dump()
    over_w = config.overall_weights.model_dump()

    frames = []
    for case in scenarios:
        prev = getattr(config.prevalence, case)
        frames.append(
            evaluate_options(
                select_case(costs, case),
                performance,
                scales,
                config.volume_basis,
                config.amortization_years,
                prev,
                case,
                gel_by_case.get(case),
                excluded_gates,
                eff_w,
                over_w,
            )
        )
    scored = pd.concat(frames, ignore_index=True)
    breakeven = pairwise_breakeven(scored)

    out = Path(args.output)
    fig_dir = out / "figures"
    out.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    cost_table = cost_table_view(scored)
    summary = comparison_summary_view(scored)
    cost_table.to_csv(out / "cost_table.csv", index=False)
    summary.to_csv(out / "comparison_summary.csv", index=False)
    breakeven.to_csv(out / "breakeven.csv", index=False)

    if args.export_xlsx:
        with pd.ExcelWriter(out / "cost_table.xlsx", engine="openpyxl") as writer:
            cost_table.to_excel(writer, sheet_name="cost_table", index=False)
            summary.to_excel(writer, sheet_name="comparison_summary", index=False)
            breakeven.to_excel(writer, sheet_name="breakeven", index=False)

    option_filter = [
        (d, m)
        for d, m in costs[["diagnostic", "method"]].drop_duplicates().itertuples(index=False)
    ]
    mc_df = None
    if not args.no_montecarlo:
        mc_cfg = config.monte_carlo
        mc_df = monte_carlo(
            costs,
            performance,
            scales,
            config.volume_basis,
            config.amortization_years,
            config.prevalence.model_dump(),
            int(mc_cfg.get("n_draws", 10000)),
            int(mc_cfg.get("seed", 42)),
            lambda case: amplification_gate(config.gel_chemistry, case),
            excluded_gates,
            eff_w,
            over_w,
            option_filter,
        )
        mc_df.to_csv(out / "monte_carlo_results.csv", index=False)
    else:
        pd.DataFrame(
            columns=[
                "scale",
                "option",
                "cost_per_test_p5",
                "cost_per_test_p50",
                "cost_per_test_p95",
                "prob_cheapest",
                "prob_best_overall",
                "n_draws",
                "seed",
            ]
        ).to_csv(out / "monte_carlo_results.csv", index=False)

    tornado = tornado_sensitivity(
        costs,
        performance,
        scales,
        config.volume_basis,
        config.amortization_years,
        config.prevalence.model_dump(),
        lambda case: amplification_gate(config.gel_chemistry, case),
        excluded_gates,
        eff_w,
        over_w,
    )
    tornado.to_csv(out / "tornado_sensitivity.csv", index=False)

    write_all_figures(scored, tornado, mc_df, out)
    write_report(
        out / "report.md",
        scored,
        breakeven,
        gel_gates,
        mc_df,
        {
            "currency": config.currency,
            "target_price_year": config.target_price_year,
            "volume_basis": config.volume_basis,
            "amortization_years": config.amortization_years,
        },
    )
    print(f"Wrote outputs to {out}")
    for option in sorted(scored["option"].unique()):
        print(f"  option: {option}")


def main() -> None:
    try:
        run(parse_args())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
