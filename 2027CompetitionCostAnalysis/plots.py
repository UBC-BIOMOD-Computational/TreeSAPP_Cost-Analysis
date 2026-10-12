"""Figures written to outputs/figures/."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from cost_model import total_cost

sns.set_theme(style="whitegrid", context="talk")


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_cost_vs_n(scored: pd.DataFrame, path: Path, n_grid: np.ndarray | None = None) -> None:
    base = scored[scored["scenario"] == "base"] if "scenario" in scored.columns else scored
    if n_grid is None:
        n_grid = np.unique(np.round(np.geomspace(100, 100_000, 60)).astype(int))
    fig, ax = plt.subplots(figsize=(10, 6))
    for option, grp in base.groupby("option"):
        row = grp.sort_values("scale").iloc[0]
        costs = [
            total_cost(
                int(n),
                row["sample_cost_fixed"],
                row["read_cost_fixed"],
                row["sample_cost_var"],
                row["read_cost_var"],
                row["qc_overhead_pct"],
            )
            / n
            for n in n_grid
        ]
        ax.plot(n_grid, costs, label=option, linewidth=2)
    ax.set_xscale("log")
    ax.set_xlabel("Number of tests (N)")
    ax.set_ylabel("Cost per test (2026 USD)")
    ax.set_title("Cost per test vs. volume")
    ax.legend(fontsize=9)
    _save(fig, path)


def plot_stacked_bars(scored: pd.DataFrame, path: Path) -> None:
    base = scored[scored["scenario"] == "base"] if "scenario" in scored.columns else scored
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)
    for ax, (scale, grp) in zip(axes, base.groupby("scale")):
        labels = grp["option"].tolist()
        fixed = grp["total_fixed"].to_numpy()
        variable = (grp["var_per_test"] * grp["scale"]).to_numpy()
        x = np.arange(len(labels))
        ax.bar(x, fixed, label="Fixed (amortized)")
        ax.bar(x, variable, bottom=fixed, label="Variable × N")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
        ax.set_title(f"Total cost at N={int(scale)}")
        ax.set_ylabel("USD (2026)")
        ax.legend(fontsize=8)
    fig.suptitle("Stacked fixed and variable cost")
    _save(fig, path)


def plot_cost_per_test_by_scale(scored: pd.DataFrame, path: Path) -> None:
    base = scored[scored["scenario"] == "base"] if "scenario" in scored.columns else scored
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=base, x="option", y="cost_per_test", hue="scale", ax=ax)
    ax.set_xlabel("Diagnostic")
    ax.set_ylabel("Cost per test (2026 USD)")
    ax.set_title("Cost per test by scale")
    ax.tick_params(axis="x", rotation=30)
    _save(fig, path)


def plot_tornado(tornado: pd.DataFrame, path: Path, scale: int) -> None:
    sub = tornado[(tornado["scale"] == scale) & (tornado["option"] == tornado["base_winner"])]
    if sub.empty:
        return
    rows = []
    for param, grp in sub.groupby("parameter"):
        low = grp.loc[grp["side"] == "low", "delta_overall_score"]
        high = grp.loc[grp["side"] == "high", "delta_overall_score"]
        rows.append(
            {
                "parameter": param,
                "low": float(low.iloc[0]) if not low.empty else 0.0,
                "high": float(high.iloc[0]) if not high.empty else 0.0,
            }
        )
    frame = pd.DataFrame(rows)
    frame["span"] = (frame["high"] - frame["low"]).abs()
    frame = frame.sort_values("span").tail(15)
    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(frame))
    ax.barh(y, frame["low"], color="#4c72b0", label="low")
    ax.barh(y, frame["high"], color="#dd8452", label="high")
    ax.set_yticks(y)
    ax.set_yticklabels(frame["parameter"], fontsize=8)
    ax.set_xlabel("Change in overall score of base-case winner")
    ax.set_title(f"One-at-a-time sensitivity (N={scale})")
    ax.legend()
    _save(fig, path)


def plot_cost_vs_effectiveness(scored: pd.DataFrame, path: Path) -> None:
    base = scored[scored["scenario"] == "base"] if "scenario" in scored.columns else scored
    fig, ax = plt.subplots(figsize=(10, 6))
    for scale, grp in base.groupby("scale"):
        ax.scatter(grp["cost_per_test"], grp["effectiveness_score"], s=80, label=f"N={int(scale)}")
        for _, rec in grp.iterrows():
            ax.annotate(rec["option"], (rec["cost_per_test"], rec["effectiveness_score"]), fontsize=8)
    ax.set_xlabel("Cost per test (2026 USD)")
    ax.set_ylabel("Effectiveness score (0-1)")
    ax.set_title("Cost vs. effectiveness")
    ax.legend()
    _save(fig, path)


def plot_win_probabilities(mc: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    melted = mc.melt(
        id_vars=["scale", "option"],
        value_vars=["prob_cheapest", "prob_best_overall"],
        var_name="metric",
        value_name="probability",
    )
    titles = {"prob_cheapest": "P(cheapest)", "prob_best_overall": "P(best overall)"}
    for ax, metric in zip(axes, ["prob_cheapest", "prob_best_overall"]):
        sub = melted[melted["metric"] == metric]
        sns.barplot(data=sub, x="option", y="probability", hue="scale", ax=ax)
        ax.set_title(titles[metric])
        ax.set_ylabel("Probability")
        ax.tick_params(axis="x", rotation=30)
        ax.set_ylim(0, 1)
    fig.suptitle("Monte Carlo win probabilities")
    _save(fig, path)


def write_all_figures(scored: pd.DataFrame, tornado: pd.DataFrame, mc: pd.DataFrame | None, out_dir: Path) -> list[Path]:
    figures = out_dir / "figures"
    paths = [
        figures / "cost_vs_n.png",
        figures / "stacked_fixed_variable.png",
        figures / "cost_per_test_by_scale.png",
        figures / "cost_vs_effectiveness.png",
    ]
    plot_cost_vs_n(scored, paths[0])
    plot_stacked_bars(scored, paths[1])
    plot_cost_per_test_by_scale(scored, paths[2])
    plot_cost_vs_effectiveness(scored, paths[3])
    for scale in sorted(scored["scale"].unique()):
        p = figures / f"tornado_N{int(scale)}.png"
        plot_tornado(tornado, p, int(scale))
        paths.append(p)
    if mc is not None and not mc.empty:
        p = figures / "monte_carlo_win_probabilities.png"
        plot_win_probabilities(mc, p)
        paths.append(p)
    return paths
