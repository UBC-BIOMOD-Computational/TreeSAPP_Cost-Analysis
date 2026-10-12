"""Gel assay chemistry constraints: units, amplification gate, literature vs device gap."""

from __future__ import annotations

from typing import Any

from units import amount_in_volume_to_nM, concentration_to_nM


def _qty(node: dict[str, Any], default_unit: str | None = None) -> tuple[float, str]:
    return float(node["value"]), str(node.get("unit", default_unit))


def literature_target_nM(gel: dict[str, Any]) -> tuple[float, str]:
    lit = gel["literature_proven"]
    nM = amount_in_volume_to_nM(lit["quantity"], lit["unit"], lit["volume"], lit["volume_unit"])
    entered = f"{lit['quantity']} {lit['unit']} in {lit['volume']} {lit['volume_unit']}"
    return nM, entered


def device_target_nM(gel: dict[str, Any]) -> tuple[float, str]:
    device = gel["device_proven"]
    well = gel["well_volume"]
    nM = amount_in_volume_to_nM(device["quantity"], device["unit"], well["value"], well["unit"])
    entered = f"{device['quantity']} {device['unit']} per well ({well['value']} {well['unit']})"
    return nM, entered


def expected_input_nM(gel: dict[str, Any], case: str) -> tuple[float, str]:
    node = gel["expected_input_conc"][case]
    value, unit = _qty(node)
    return concentration_to_nM(value, unit), f"{value} {unit}"


def target_nM_for_basis(gel: dict[str, Any]) -> tuple[float, str, str]:
    basis = gel.get("detection_basis", "literature")
    if basis == "literature":
        nM, entered = literature_target_nM(gel)
        return nM, entered, basis
    if basis == "device":
        nM, entered = device_target_nM(gel)
        return nM, entered, basis
    raise ValueError(f"Unknown detection_basis {basis!r}")


def amplification_gate(gel: dict[str, Any], case: str) -> dict[str, Any]:
    """If required_fold exceeds achievable gain, Gel fails the feasibility gate."""
    target, target_entered, basis = target_nM_for_basis(gel)
    expected, expected_entered = expected_input_nM(gel, case)
    amp = gel["amplification"]
    max_fold = float(amp["max_fold_gain"])
    efficiency = float(amp["efficiency"])
    achievable = max_fold * efficiency
    if expected <= 0:
        required_fold = float("inf")
    else:
        required_fold = target / expected
    passed = required_fold <= achievable
    lit_nM, lit_entered = literature_target_nM(gel)
    device_nM, device_entered = device_target_nM(gel)
    gap = device_nM / lit_nM if lit_nM else float("inf")
    return {
        "diagnostic": "Gel",
        "case": case,
        "detection_basis": basis,
        "target_nM": target,
        "target_entered": target_entered,
        "expected_input_nM": expected,
        "expected_entered": expected_entered,
        "required_fold": required_fold,
        "achievable_fold": achievable,
        "amplification_chemistry": amp.get("chemistry"),
        "amplification_efficiency": efficiency,
        "max_fold_gain": max_fold,
        "passed": passed,
        "feasibility_gate": "pass" if passed else "fail",
        "rna_purification_required": bool(gel.get("rna_purification_required", False)),
        "background_rna_tolerance_ng_per_uL": gel.get("background_rna_tolerance_ng_per_uL"),
        "literature_nM": lit_nM,
        "literature_entered": lit_entered,
        "device_nM": device_nM,
        "device_entered": device_entered,
        "device_vs_literature_fold": gap,
        "probe_purity_critical": bool(gel.get("probe_purity_critical", False)),
    }
