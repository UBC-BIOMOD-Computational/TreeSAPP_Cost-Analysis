"""Plain-language report.md generation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def _md_table(df: pd.DataFrame, floatfmt: str = ".2f") -> str:
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = []
    for rec in df.to_dict(orient="records"):
        cells = []
        for c in cols:
            v = rec[c]
            if isinstance(v, float):
                cells.append(format(v, floatfmt))
            else:
                cells.append(str(v))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *body])


def _pick(df: pd.DataFrame, scale: int, scenario: str = "base") -> pd.DataFrame:
    sub = df[(df["scale"] == scale) & (df["scenario"] == scenario)]
    return sub.sort_values("option")


def _cheapest(sub: pd.DataFrame) -> pd.Series:
    return sub.loc[sub["cost_per_test"].idxmin()]


def _most_effective(sub: pd.DataFrame) -> pd.Series:
    return sub.loc[sub["effectiveness_score"].idxmax()]


def _best_overall(sub: pd.DataFrame) -> pd.Series | None:
    eligible = sub[sub["eligible_best_overall"]]
    if eligible.empty:
        return None
    return eligible.loc[eligible["overall_score"].idxmax()]


def _placeholder_lines(scored: pd.DataFrame) -> list[str]:
    flagged = scored[scored["placeholder"]]
    if flagged.empty:
        return ["No inputs were tagged `placeholder`."]
    lines = [
        "The following options use **placeholder** numbers. Replace each with a vendor quote before treating rankings as final:"
    ]
    seen = set()
    for _, rec in flagged.iterrows():
        key = (rec["option"], rec["scale"], rec["confidence"])
        if key in seen:
            continue
        seen.add(key)
        lines.append(
            f"- {rec['option']} at N={int(rec['scale'])} (confidence={rec['confidence']}, source={rec['source']}): replace with vendor quote"
        )
    return lines


def write_report(
    path: Path,
    scored: pd.DataFrame,
    breakeven: pd.DataFrame,
    gel_gates: list[dict],
    mc: pd.DataFrame | None,
    config_notes: dict,
) -> None:
    scenarios = sorted(scored["scenario"].unique())
    scales = sorted(scored["scale"].unique())
    lines: list[str] = []
    lines.append("# Diagnostic Cost and Effectiveness Comparison")
    lines.append("")
    lines.append(
        f"All money is **{config_notes.get('currency', 'USD')} {config_notes.get('target_price_year', 2026)}**. "
        f"Volume basis is **{config_notes.get('volume_basis')}**"
        + (
            f" with a {config_notes.get('amortization_years')}-year amortization of fixed costs."
            if config_notes.get("volume_basis") == "annual"
            else " (full fixed cost assigned to the batch)."
        )
    )
    lines.append("")
    lines.append("## Answers")
    lines.append("")

    base = scored[scored["scenario"] == "base"] if "base" in scenarios else scored
    for scale in scales:
        sub = _pick(base, int(scale), sub_scenario(base))
        cheap = _cheapest(sub)
        effective = _most_effective(sub)
        best = _best_overall(sub)
        lines.append(f"### N = {int(scale):,}")
        lines.append("")
        lines.append(
            f"1. **Cheapest:** {cheap['option']} at {_fmt_money(cheap['cost_per_test'])} per test "
            f"(total {_fmt_money(cheap['total_cost'])})."
        )
        lines.append(
            f"2. **Most effective:** {effective['option']} "
            f"(effectiveness score {effective['effectiveness_score']:.3f}, "
            f"accuracy {effective['accuracy']:.3f}, turnaround {effective['total_time_days']:.1f} days)."
        )
        if best is None:
            lines.append("3. **Best overall:** no option passed the feasibility gate.")
        else:
            depends = " **This ranking uses placeholder and/or low-confidence inputs.**" if (
                best["placeholder"] or best["confidence"] == "low"
            ) else ""
            lines.append(
                f"3. **Best overall:** {best['option']} "
                f"(overall score {best['overall_score']:.3f}).{depends}"
            )
        gated = sub[~sub["eligible_best_overall"]]
        if not gated.empty:
            names = ", ".join(f"{r.option} ({r.feasibility_gate})" for r in gated.itertuples())
            lines.append(f"   Excluded from best-overall: {names}.")
        lines.append("")

    lines.append("## Cost table (base case)")
    lines.append("")
    show = base[
        [
            "option",
            "scale",
            "sample_type",
            "sample_time_fixed_days",
            "sample_time_var_min",
            "read_time_fixed_days",
            "read_time_var_min",
            "sample_cost_fixed",
            "sample_cost_var",
            "read_cost_fixed",
            "read_cost_var",
            "total_fixed",
            "var_per_test",
            "total_cost",
            "cost_per_test",
            "feasibility_gate",
        ]
    ].copy()
    lines.append(_md_table(show))
    lines.append("")

    lines.append("## Sequencing in-house vs. outsourced")
    lines.append("")
    seq = breakeven[
        breakeven["option_a"].str.contains("Sequencing") & breakeven["option_b"].str.contains("Sequencing")
    ]
    if seq.empty:
        lines.append("Sequencing pair was not in the comparison (excluded).")
    else:
        for _, rec in seq.iterrows():
            n_star = rec["break_even_n"]
            n_txt = "no positive crossover" if pd.isna(n_star) else f"N = {n_star:,.0f}"
            lines.append(
                f"- Scenario {rec.get('scenario', 'base')}, reference scale {int(rec['scale'])}: "
                f"break-even {n_txt}. {rec['note']}."
            )
    lines.append("")

    lines.append("## Gel assay chemistry")
    lines.append("")
    for gate in gel_gates:
        status = "PASS" if gate["passed"] else "FAIL"
        lines.append(
            f"- Case **{gate['case']}** ({status}): required fold {gate['required_fold']:.3g} vs "
            f"achievable {gate['achievable_fold']:.3g} using {gate['amplification_chemistry']}. "
            f"Target entered as {gate['target_entered']} → {gate['target_nM']:.4g} nM "
            f"(basis={gate['detection_basis']}). Expected input entered as {gate['expected_entered']} "
            f"→ {gate['expected_input_nM']:.4g} nM."
        )
    if gel_gates:
        g0 = gel_gates[0]
        lines.append("")
        lines.append(
            f"Literature proven quantity was entered as {g0['literature_entered']} ({g0['literature_nM']:.4g} nM). "
            f"Device proven quantity was entered as {g0['device_entered']} ({g0['device_nM']:.4g} nM). "
            f"The device requirement is {g0['device_vs_literature_fold']:.3g}× the literature figure; "
            "this gap is flagged and both remain separate inputs."
        )
        if not g0["rna_purification_required"]:
            lines.append(
                "RNA purification is **not** required (background RNA tolerance "
                f"{g0['background_rna_tolerance_ng_per_uL']} ng/µL); extraction kits are omitted from Gel costs. "
                "Whole-blood sampling skips centrifugation relative to plasma/serum options."
            )
        if g0["probe_purity_critical"]:
            lines.append("Probe purity is treated as critical; probe purification/QC is included in Gel read costs.")
    lines.append("")

    lines.append("## Placeholder and low-confidence inputs")
    lines.append("")
    lines.extend(_placeholder_lines(scored))
    low_conf = scored[scored["confidence"] == "low"]
    if not low_conf.empty:
        lines.append("")
        lines.append("Low-confidence rows (even if sourced) also make the ranking sensitive:")
        for option in sorted(low_conf["option"].unique()):
            lines.append(f"- {option}")
    lines.append("")

    if mc is not None and not mc.empty:
        lines.append("## Uncertainty (Monte Carlo)")
        lines.append("")
        lines.append(
            "Triangular draws on low/base/high inputs. Probabilities are the fraction of draws in which "
            "an option is cheapest or best overall among feasibility-passing options."
        )
        lines.append("")
        lines.append(_md_table(mc, floatfmt=".3f"))
        lines.append("")

    lines.append("## Scenario analysis")
    lines.append("")
    for scenario in scenarios:
        lines.append(f"### {scenario}")
        lines.append("")
        for scale in scales:
            sub = _pick(scored, int(scale), scenario)
            cheap = _cheapest(sub)
            best = _best_overall(sub)
            best_txt = "none eligible" if best is None else best["option"]
            lines.append(
                f"- N={int(scale):,}: cheapest {cheap['option']} ({_fmt_money(cheap['cost_per_test'])}/test); "
                f"best overall {best_txt}."
            )
        lines.append("")

    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "- Prevalence, sensitivity, and specificity are currently placeholder or literature-style values; "
        "they drive accuracy and cost-per-correct-result."
    )
    lines.append(
        "- Protein remains gated until VIM/CDH1 detectability in plasma/serum is shown."
    )
    lines.append(
        "- Expected circulating VIM/CDH1 concentration is a required user input and is still a placeholder; "
        "it controls whether Gel passes the amplification feasibility gate."
    )
    lines.append(
        "- Effectiveness weights (accuracy, turnaround, feasibility, invasiveness, regulatory burden) "
        "and the cost/effectiveness blend are user-set in config.yaml."
    )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sub_scenario(df: pd.DataFrame) -> str:
    if "base" in set(df["scenario"]):
        return "base"
    return str(df["scenario"].iloc[0])
