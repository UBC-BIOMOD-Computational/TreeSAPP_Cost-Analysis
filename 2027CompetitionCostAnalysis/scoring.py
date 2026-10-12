"""Effectiveness scoring, ranking, and overall (cost + effectiveness) score."""

from __future__ import annotations

import numpy as np
import pandas as pd

from cost_model import accuracy, cost_per_correct_result, cost_per_true_positive


def _minmax(series: pd.Series, higher_is_better: bool) -> pd.Series:
    values = series.astype(float)
    lo, hi = values.min(), values.max()
    if np.isclose(hi, lo):
        return pd.Series(np.ones(len(values)), index=values.index)
    norm = (values - lo) / (hi - lo)
    return norm if higher_is_better else 1.0 - norm


def score_group(
    df: pd.DataFrame,
    effectiveness_weights: dict[str, float],
    overall_weights: dict[str, float],
    prevalence: float,
    excluded_gates: list[str],
) -> pd.DataFrame:
    """Normalize criteria within a scale (and scenario) and rank options."""
    out = df.copy()
    out["accuracy"] = [
        accuracy(s, p, prevalence) for s, p in zip(out["sensitivity"], out["specificity"])
    ]
    out["cost_per_correct_result"] = [
        cost_per_correct_result(c, a) for c, a in zip(out["cost_per_test"], out["accuracy"])
    ]
    out["cost_per_true_positive"] = [
        cost_per_true_positive(c, s, prevalence)
        for c, s in zip(out["cost_per_test"], out["sensitivity"])
    ]
    out["eligible_best_overall"] = ~out["feasibility_gate"].isin(excluded_gates)

    out["score_accuracy"] = _minmax(out["accuracy"], True)
    out["score_turnaround"] = _minmax(out["total_time_days"], False)
    out["score_feasibility"] = _minmax(out["technical_feasibility_score"], True)
    out["score_invasiveness"] = _minmax(out["invasiveness_score"], False)
    out["score_regulatory"] = _minmax(out["regulatory_burden_score"], False)

    w = effectiveness_weights
    out["effectiveness_score"] = (
        w["accuracy"] * out["score_accuracy"]
        + w["turnaround"] * out["score_turnaround"]
        + w["feasibility"] * out["score_feasibility"]
        + w["invasiveness"] * out["score_invasiveness"]
        + w["regulatory_burden"] * out["score_regulatory"]
    )
    out["score_cost"] = _minmax(out["cost_per_test"], False)
    out["overall_score"] = (
        overall_weights["cost"] * out["score_cost"]
        + overall_weights["effectiveness"] * out["effectiveness_score"]
    )

    out["rank_cost"] = out["cost_per_test"].rank(method="min").astype(int)
    out["rank_effectiveness"] = out["effectiveness_score"].rank(ascending=False, method="min").astype(int)

    eligible = out["eligible_best_overall"]
    out["rank_overall"] = pd.NA
    if eligible.any():
        ranks = out.loc[eligible, "overall_score"].rank(ascending=False, method="min").astype(int)
        out.loc[eligible, "rank_overall"] = ranks
    return out


def add_scores(
    results: pd.DataFrame,
    effectiveness_weights: dict[str, float],
    overall_weights: dict[str, float],
    prevalence: float,
    excluded_gates: list[str],
) -> pd.DataFrame:
    pieces = []
    group_cols = [c for c in ["scenario", "scale"] if c in results.columns]
    for _, grp in results.groupby(group_cols, sort=False):
        pieces.append(
            score_group(grp, effectiveness_weights, overall_weights, prevalence, excluded_gates)
        )
    return pd.concat(pieces, ignore_index=True)
