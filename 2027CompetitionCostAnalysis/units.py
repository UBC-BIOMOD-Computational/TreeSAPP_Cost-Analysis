"""Concentration and volume unit conversions used by the Gel amplification gate."""

from __future__ import annotations

VOLUME_TO_L = {
    "l": 1.0,
    "liter": 1.0,
    "litre": 1.0,
    "ml": 1e-3,
    "ul": 1e-6,
    "µl": 1e-6,
    "μl": 1e-6,
    "nl": 1e-9,
}

# Factor to convert a molar concentration unit into nM.
CONC_TO_NM = {
    "fm": 1e-6,
    "pm": 1e-3,
    "nm": 1.0,
    "um": 1e3,
    "µm": 1e3,
    "μm": 1e3,
    "mm": 1e6,
    "m": 1e9,
}

AMOUNT_TO_MOL = {
    "mol": 1.0,
    "mmol": 1e-3,
    "umol": 1e-6,
    "µmol": 1e-6,
    "μmol": 1e-6,
    "nmol": 1e-9,
    "pmol": 1e-12,
    "fmol": 1e-15,
}


def _norm(unit: str) -> str:
    return unit.strip().lower().replace(" ", "")


def volume_to_liters(value: float, unit: str) -> float:
    key = _norm(unit)
    if key not in VOLUME_TO_L:
        raise ValueError(f"Unsupported volume unit {unit!r}. Expected one of {sorted(VOLUME_TO_L)}")
    return value * VOLUME_TO_L[key]


def amount_to_moles(value: float, unit: str) -> float:
    key = _norm(unit)
    if key not in AMOUNT_TO_MOL:
        raise ValueError(f"Unsupported amount unit {unit!r}. Expected one of {sorted(AMOUNT_TO_MOL)}")
    return value * AMOUNT_TO_MOL[key]


def concentration_to_nM(value: float, unit: str) -> float:
    key = _norm(unit)
    if key not in CONC_TO_NM:
        raise ValueError(f"Unsupported concentration unit {unit!r}. Expected one of {sorted(CONC_TO_NM)}")
    return value * CONC_TO_NM[key]


def amount_in_volume_to_nM(amount: float, amount_unit: str, volume: float, volume_unit: str) -> float:
    """Convert an absolute quantity in a reaction volume to nM."""
    moles = amount_to_moles(amount, amount_unit)
    liters = volume_to_liters(volume, volume_unit)
    if liters <= 0:
        raise ValueError("Reaction volume must be positive")
    mol_per_l = moles / liters
    return mol_per_l * 1e9
