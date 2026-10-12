"""Monte Carlo and one-at-a-time sensitivity analysis."""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from cost_model import (
    break_even_n,
    cost_per_test,
    dominance_note,
    split_amortized_fixed,
    total_cost,
    total_time_days,
    variable_cost_per_test,
)
from inputs_loader import COST_NUMERIC_FIELDS, option_label
from scoring import add_scores


def triangular_sample(rng: np.random.Generator, low: float, base: float, high: float, size: int) -> np.ndarray:
    if high < low:
        raise ValueError(f"triangular high < low: {low}, {high}")
    if np.isclose(low, high):
        return np.full(size, low)
    mode = min(max(base, low), high)
    return rng.triangular(low, mode, high, size=size)


def build_lookup(costs: pd.DataFrame) -> dict:
    lookup: dict[tuple, dict[str, dict[str, float]]] = {}
    for rec in costs.to_dict(orient="records"):
        key = (rec["diagnostic"], rec["method"], int(rec["scale"]))
        lookup.setdefault(key, {})[rec["case"]] = rec
    return lookup


def pairwise_breakeven(scored: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = [c for c in ["scenario", "scale"] if c in scored.columns]
    for keys, grp in scored.groupby(group_cols, sort=False):
        records = grp.to_dict(orient="records")
        if not isinstance(keys, tuple):
            keys = (keys,)
        meta = dict(zip(group_cols, keys))
        for i, a in enumerate(records):
            for b in records[i + 1 :]:
                n_star = break_even_n(a["total_fixed"], a["var_per_test"], b["total_fixed"], b["var_per_test"])
                rows.append(
                    {
                        **meta,
                        "option_a": a["option"],
                        "option_b": b["option"],
                        "break_even_n": n_star,
                        "note": dominance_note(
                            a["total_fixed"], a["var_per_test"], b["total_fixed"], b["var_per_test"]
                        ),
                    }
                )
    return pd.DataFrame(rows)


def evaluate_options(
    case_rows: pd.DataFrame,
    performance: pd.DataFrame,
    scales: list[int],
    volume_basis: str,
    amortization_years: float,
    prevalence: float,
    scenario: str,
    gel_gate: dict | None,
    excluded_gates: list[str],
    effectiveness_weights: dict[str, float],
    overall_weights: dict[str, float],
) -> pd.DataFrame:
    perf = performance.set_index("diagnostic")
    rows = []
    for rec in case_rows.to_dict(orient="records"):
        if int(rec["scale"]) not in scales:
            continue
        diagnostic = rec["diagnostic"]
        if diagnostic not in perf.index:
            raise ValueError(f"No performance row for diagnostic {diagnostic}")
        p = perf.loc[diagnostic]
        gate = str(p["feasibility_gate"])
        if diagnostic == "Gel" and gel_gate is not None:
            gate = gel_gate["feasibility_gate"]
        fs, fr_raw = rec["sample_cost_fixed"], rec["read_cost_fixed"] + rec["prep_cost_fixed"]
        fs, fr = split_amortized_fixed(fs, fr_raw, volume_basis, amortization_years)
        vs = rec["sample_cost_var"]
        vr = rec["read_cost_var"] + rec["prep_cost_var"]
        qc = rec["qc_overhead_pct"]
        n = int(rec["scale"])
        read_time_var = rec["read_time_var_min"] + rec["prep_time_var_min"]
        rows.append(
            {
                "scenario": scenario,
                "option": option_label(diagnostic, rec["method"]),
                "diagnostic": diagnostic,
                "method": rec["method"],
                "scale": n,
                "sample_type": rec["sample_type"],
                "sample_time_fixed_days": rec["sample_time_fixed_days"],
                "sample_time_var_min": rec["sample_time_var_min"],
                "read_time_fixed_days": rec["read_time_fixed_days"],
                "read_time_var_min": read_time_var,
                "sample_cost_fixed": fs,
                "sample_cost_var": vs,
                "read_cost_fixed": fr,
                "read_cost_var": vr,
                "qc_overhead_pct": qc,
                "parallel_capacity": rec["parallel_capacity"],
                "total_fixed": fs + fr,
                "var_per_test": variable_cost_per_test(vs, vr, qc),
                "total_cost": total_cost(n, fs, fr, vs, vr, qc),
                "cost_per_test": cost_per_test(n, fs, fr, vs, vr, qc),
                "total_time_days": total_time_days(
                    n,
                    rec["sample_time_fixed_days"],
                    rec["read_time_fixed_days"],
                    rec["sample_time_var_min"],
                    read_time_var,
                    rec["parallel_capacity"],
                ),
                "sensitivity": float(p["sensitivity"]),
                "specificity": float(p["specificity"]),
                "invasiveness_score": float(p["invasiveness_score"]),
                "technical_feasibility_score": float(p["technical_feasibility_score"]),
                "readiness_level": float(p["readiness_level"]),
                "regulatory_burden_score": float(p["regulatory_burden_score"]),
                "feasibility_gate": gate,
                "source": rec["source"],
                "confidence": rec["confidence"],
                "placeholder": str(rec["source"]).lower() == "placeholder",
                "price_year": rec["price_year"],
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("No cost rows matched the requested scales")
    return add_scores(frame, effectiveness_weights, overall_weights, prevalence, excluded_gates)


def monte_carlo(
    costs: pd.DataFrame,
    performance: pd.DataFrame,
    scales: list[int],
    volume_basis: str,
    amortization_years: float,
    prevalence_triple: dict[str, float],
    n_draws: int,
    seed: int,
    gel_gate_fn: Callable[[str], dict],
    excluded_gates: list[str],
    effectiveness_weights: dict[str, float],
    overall_weights: dict[str, float],
    option_filter: list[tuple[str, str]] | None = None,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    lookup = build_lookup(costs)
    keys = [k for k in lookup if k[2] in scales]
    if option_filter:
        allowed = set(option_filter)
        keys = [k for k in keys if (k[0], k[1]) in allowed]
    perf = performance.set_index("diagnostic")

    samples: dict[tuple, dict[str, np.ndarray]] = {}
    for key in keys:
        by_case = lookup[key]
        samples[key] = {
            field: triangular_sample(
                rng, by_case["low"][field], by_case["base"][field], by_case["high"][field], n_draws
            )
            for field in COST_NUMERIC_FIELDS
        }

    prev = triangular_sample(
        rng, prevalence_triple["low"], prevalence_triple["base"], prevalence_triple["high"], n_draws
    )
    gel_gate = gel_gate_fn("base")

    def _minmax(arr: np.ndarray, higher_is_better: bool) -> np.ndarray:
        lo = arr.min(axis=1, keepdims=True)
        hi = arr.max(axis=1, keepdims=True)
        tied = np.isclose(hi, lo)
        denom = np.where(tied, 1.0, hi - lo)
        norm = np.where(tied, 1.0, (arr - lo) / denom)
        return norm if higher_is_better else 1.0 - norm

    records = []
    w_eff = effectiveness_weights
    w_over = overall_weights
    for scale in scales:
        scale_keys = [k for k in keys if k[2] == scale]
        options = []
        cpt_cols = []
        time_cols = []
        acc_cols = []
        feas_cols = []
        inv_cols = []
        reg_cols = []
        eligible_mask = []
        for diagnostic, method, sc in scale_keys:
            key = (diagnostic, method, sc)
            s = samples[key]
            p = perf.loc[diagnostic]
            feasibility = str(p["feasibility_gate"])
            if diagnostic == "Gel":
                feasibility = gel_gate["feasibility_gate"]
            fs_raw = s["sample_cost_fixed"]
            fr_raw = s["read_cost_fixed"] + s["prep_cost_fixed"]
            fs, fr = split_amortized_fixed(fs_raw, fr_raw, volume_basis, amortization_years)
            vs = s["sample_cost_var"]
            vr = s["read_cost_var"] + s["prep_cost_var"]
            qc = s["qc_overhead_pct"]
            cpt = (fs + fr) / sc + (vs + vr) * (1.0 + qc)
            read_var = s["read_time_var_min"] + s["prep_time_var_min"]
            time = total_time_days(
                sc,
                s["sample_time_fixed_days"],
                s["read_time_fixed_days"],
                s["sample_time_var_min"],
                read_var,
                s["parallel_capacity"],
            )
            acc = float(p["sensitivity"]) * prev + float(p["specificity"]) * (1.0 - prev)
            options.append(option_label(diagnostic, method))
            cpt_cols.append(cpt)
            time_cols.append(time)
            acc_cols.append(acc)
            feas_cols.append(np.full(n_draws, float(p["technical_feasibility_score"])))
            inv_cols.append(np.full(n_draws, float(p["invasiveness_score"])))
            reg_cols.append(np.full(n_draws, float(p["regulatory_burden_score"])))
            eligible_mask.append(feasibility not in excluded_gates)

        cpt_mat = np.column_stack(cpt_cols)
        time_mat = np.column_stack(time_cols)
        acc_mat = np.column_stack(acc_cols)
        feas_mat = np.column_stack(feas_cols)
        inv_mat = np.column_stack(inv_cols)
        reg_mat = np.column_stack(reg_cols)
        eligible = np.array(eligible_mask, dtype=bool)

        effectiveness = (
            w_eff["accuracy"] * _minmax(acc_mat, True)
            + w_eff["turnaround"] * _minmax(time_mat, False)
            + w_eff["feasibility"] * _minmax(feas_mat, True)
            + w_eff["invasiveness"] * _minmax(inv_mat, False)
            + w_eff["regulatory_burden"] * _minmax(reg_mat, False)
        )
        overall = w_over["cost"] * _minmax(cpt_mat, False) + w_over["effectiveness"] * effectiveness
        cheap_idx = np.argmin(cpt_mat, axis=1)
        overall_masked = np.where(eligible[None, :], overall, -np.inf)
        best_idx = np.argmax(overall_masked, axis=1)
        any_eligible = eligible.any()

        for i, option in enumerate(options):
            series = cpt_mat[:, i]
            records.append(
                {
                    "scale": scale,
                    "option": option,
                    "cost_per_test_p5": float(np.percentile(series, 5)),
                    "cost_per_test_p50": float(np.percentile(series, 50)),
                    "cost_per_test_p95": float(np.percentile(series, 95)),
                    "prob_cheapest": float(np.mean(cheap_idx == i)),
                    "prob_best_overall": float(np.mean(best_idx == i)) if any_eligible and eligible[i] else 0.0,
                    "n_draws": n_draws,
                    "seed": seed,
                }
            )
    return pd.DataFrame(records)


def tornado_sensitivity(
    costs: pd.DataFrame,
    performance: pd.DataFrame,
    scales: list[int],
    volume_basis: str,
    amortization_years: float,
    prevalence_triple: dict[str, float],
    gel_gate_fn: Callable[[str], dict],
    excluded_gates: list[str],
    effectiveness_weights: dict[str, float],
    overall_weights: dict[str, float],
) -> pd.DataFrame:
    """One-at-a-time: each numeric input to low/high, others at base. Tracks winner movement."""
    lookup = build_lookup(costs)
    rows = []
    for scale in scales:
        base_costs = costs[(costs["case"] == "base") & (costs["scale"] == scale)]
        base_eval = evaluate_options(
            base_costs,
            performance,
            [scale],
            volume_basis,
            amortization_years,
            prevalence_triple["base"],
            "base",
            gel_gate_fn("base"),
            excluded_gates,
            effectiveness_weights,
            overall_weights,
        )
        eligible = base_eval[base_eval["eligible_best_overall"]]
        base_winner = eligible.loc[eligible["overall_score"].idxmax(), "option"] if not eligible.empty else None
        base_scores = dict(zip(base_eval["option"], base_eval["overall_score"]))
        base_cpt = dict(zip(base_eval["option"], base_eval["cost_per_test"]))

        params: list[tuple[str, str, str, str]] = []
        for diagnostic, method, sc in lookup:
            if sc != scale:
                continue
            for field in COST_NUMERIC_FIELDS:
                params.append((diagnostic, method, field, option_label(diagnostic, method)))
        params.append(("__global__", "", "prevalence", "all"))

        for diagnostic, method, field, option in params:
            for side, case in (("low", "low"), ("high", "high")):
                tweaked = base_costs.copy()
                prev = prevalence_triple["base"]
                gate_case = "base"
                if field == "prevalence":
                    prev = prevalence_triple[case]
                else:
                    mask = (tweaked["diagnostic"] == diagnostic) & (tweaked["method"] == method)
                    source = lookup[(diagnostic, method, scale)][case]
                    tweaked.loc[mask, field] = source[field]
                    if diagnostic == "Gel":
                        gate_case = case
                scored = evaluate_options(
                    tweaked,
                    performance,
                    [scale],
                    volume_basis,
                    amortization_years,
                    prev,
                    case,
                    gel_gate_fn(gate_case),
                    excluded_gates,
                    effectiveness_weights,
                    overall_weights,
                )
                eligible_s = scored[scored["eligible_best_overall"]]
                winner = (
                    eligible_s.loc[eligible_s["overall_score"].idxmax(), "option"]
                    if not eligible_s.empty
                    else None
                )
                for _, rec in scored.iterrows():
                    rows.append(
                        {
                            "scale": scale,
                            "parameter": f"{option}:{field}" if field != "prevalence" else "prevalence",
                            "side": side,
                            "option": rec["option"],
                            "cost_per_test": rec["cost_per_test"],
                            "overall_score": rec["overall_score"],
                            "delta_cost_per_test": rec["cost_per_test"] - base_cpt[rec["option"]],
                            "delta_overall_score": rec["overall_score"] - base_scores[rec["option"]],
                            "base_winner": base_winner,
                            "perturbed_winner": winner,
                            "winner_changed": winner != base_winner,
                        }
                    )
    return pd.DataFrame(rows)
