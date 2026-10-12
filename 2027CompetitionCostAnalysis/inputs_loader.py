"""Load and validate config, cost, and performance inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

COST_NUMERIC_FIELDS = [
    "sample_time_fixed_days",
    "sample_time_var_min",
    "read_time_fixed_days",
    "read_time_var_min",
    "sample_cost_fixed",
    "sample_cost_var",
    "prep_cost_fixed",
    "prep_cost_var",
    "prep_time_var_min",
    "read_cost_fixed",
    "read_cost_var",
    "qc_overhead_pct",
    "parallel_capacity",
]

REQUIRED_COST_COLUMNS = [
    "diagnostic",
    "method",
    "scale",
    "sample_type",
    "price_year",
    "source",
    "confidence",
] + COST_NUMERIC_FIELDS

REQUIRED_PERFORMANCE_COLUMNS = [
    "diagnostic",
    "sensitivity",
    "specificity",
    "sample_type",
    "invasiveness_score",
    "technical_feasibility_score",
    "readiness_level",
    "regulatory_burden_score",
    "feasibility_gate",
    "notes",
]

VALID_SAMPLE_TYPES = {"whole_blood", "plasma", "serum"}
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_GATES = {"pass", "fail", "unknown"}
VALID_CASES = {"low", "base", "high"}


class CostRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    diagnostic: str
    method: str
    scale: int
    case: str = "base"
    sample_type: str
    sample_time_fixed_days: float
    sample_time_var_min: float
    read_time_fixed_days: float
    read_time_var_min: float
    sample_cost_fixed: float
    sample_cost_var: float
    prep_cost_fixed: float
    prep_cost_var: float
    prep_time_var_min: float
    read_cost_fixed: float
    read_cost_var: float
    qc_overhead_pct: float
    parallel_capacity: float
    price_year: int
    source: str
    confidence: str

    @field_validator("sample_type")
    @classmethod
    def sample_type_ok(cls, v: str) -> str:
        if v not in VALID_SAMPLE_TYPES:
            raise ValueError(f"sample_type must be one of {sorted(VALID_SAMPLE_TYPES)}")
        return v

    @field_validator("confidence")
    @classmethod
    def confidence_ok(cls, v: str) -> str:
        if v not in VALID_CONFIDENCE:
            raise ValueError(f"confidence must be one of {sorted(VALID_CONFIDENCE)}")
        return v

    @field_validator("case")
    @classmethod
    def case_ok(cls, v: str) -> str:
        if v not in VALID_CASES:
            raise ValueError(f"case must be one of {sorted(VALID_CASES)}")
        return v

    @field_validator("qc_overhead_pct")
    @classmethod
    def qc_ok(cls, v: float) -> float:
        if v < 0:
            raise ValueError("qc_overhead_pct cannot be negative")
        return v

    @field_validator("parallel_capacity")
    @classmethod
    def cap_ok(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("parallel_capacity must be positive")
        return v

    @model_validator(mode="after")
    def non_negative_numeric(self) -> "CostRow":
        for field in COST_NUMERIC_FIELDS:
            value = getattr(self, field)
            if field == "parallel_capacity":
                continue
            if value < 0:
                raise ValueError(f"{field} cannot be negative (got {value})")
        return self


class PerformanceRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    diagnostic: str
    sensitivity: float
    specificity: float
    sample_type: str
    invasiveness_score: float
    technical_feasibility_score: float
    readiness_level: float
    regulatory_burden_score: float
    feasibility_gate: str
    notes: str = ""

    @field_validator("sample_type")
    @classmethod
    def sample_type_ok(cls, v: str) -> str:
        if v not in VALID_SAMPLE_TYPES:
            raise ValueError(f"sample_type must be one of {sorted(VALID_SAMPLE_TYPES)}")
        return v

    @field_validator("feasibility_gate")
    @classmethod
    def gate_ok(cls, v: str) -> str:
        if v not in VALID_GATES:
            raise ValueError(f"feasibility_gate must be one of {sorted(VALID_GATES)}")
        return v

    @field_validator("sensitivity", "specificity")
    @classmethod
    def rate_ok(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("sensitivity and specificity must be in [0, 1]")
        return v

    @field_validator(
        "invasiveness_score",
        "technical_feasibility_score",
        "readiness_level",
        "regulatory_burden_score",
    )
    @classmethod
    def score_ok(cls, v: float) -> float:
        if v < 0:
            raise ValueError("scores cannot be negative")
        return v


class EffectivenessWeights(BaseModel):
    accuracy: float
    turnaround: float
    feasibility: float
    invasiveness: float
    regulatory_burden: float

    @model_validator(mode="after")
    def sum_to_one(self) -> "EffectivenessWeights":
        total = (
            self.accuracy
            + self.turnaround
            + self.feasibility
            + self.invasiveness
            + self.regulatory_burden
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"effectiveness_weights must sum to 1 (got {total})")
        for name, value in self.model_dump().items():
            if value < 0:
                raise ValueError(f"effectiveness weight {name} cannot be negative")
        return self


class OverallWeights(BaseModel):
    cost: float
    effectiveness: float

    @model_validator(mode="after")
    def sum_to_one(self) -> "OverallWeights":
        total = self.cost + self.effectiveness
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"overall_weights must sum to 1 (got {total})")
        return self


class RangeTriple(BaseModel):
    low: float
    base: float
    high: float

    @model_validator(mode="after")
    def ordered(self) -> "RangeTriple":
        if self.low > self.base or self.base > self.high:
            raise ValueError(f"low/base/high out of order: {self.low}, {self.base}, {self.high}")
        return self


class AppConfig(BaseModel):
    currency: str = "USD"
    target_price_year: int = 2026
    scales: list[int]
    volume_basis: str
    amortization_years: float = 5.0
    discount_rate: float = 0.0
    prevalence: RangeTriple
    cpi: dict[int, float]
    effectiveness_weights: EffectivenessWeights
    overall_weights: OverallWeights
    sequencing: dict[str, Any] = Field(default_factory=dict)
    gel_chemistry: dict[str, Any]
    monte_carlo: dict[str, Any]
    exclude_from_best_overall_gates: list[str] = Field(default_factory=lambda: ["fail", "unknown"])

    @field_validator("volume_basis")
    @classmethod
    def basis_ok(cls, v: str) -> str:
        if v not in {"annual", "one_time"}:
            raise ValueError("volume_basis must be 'annual' or 'one_time'")
        return v

    @field_validator("cpi")
    @classmethod
    def cpi_keys(cls, v: dict[Any, float]) -> dict[int, float]:
        return {int(k): float(val) for k, val in v.items()}


def load_config(path: Path) -> AppConfig:
    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return AppConfig.model_validate(raw)


def cpi_factor(price_year: int, target_year: int, cpi: dict[int, float]) -> float:
    if price_year not in cpi:
        raise ValueError(f"No CPI entry for price_year {price_year}")
    if target_year not in cpi:
        raise ValueError(f"No CPI entry for target_year {target_year}")
    return cpi[target_year] / cpi[price_year]


def _require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing columns: {missing}")


def load_cost_assumptions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "case" not in df.columns:
        raise ValueError("cost_assumptions.csv must be long-format with a 'case' column (low/base/high)")
    _require_columns(df, REQUIRED_COST_COLUMNS + ["case"], "cost_assumptions.csv")
    rows = [CostRow.model_validate(rec).model_dump() for rec in df.to_dict(orient="records")]
    out = pd.DataFrame(rows)
    _validate_low_base_high(out)
    return out


def _validate_low_base_high(df: pd.DataFrame) -> None:
    keys = ["diagnostic", "method", "scale"]
    for key, grp in df.groupby(keys, sort=False):
        cases = set(grp["case"])
        if cases != VALID_CASES:
            raise ValueError(f"Expected low/base/high rows for {key}, found {sorted(cases)}")
        by_case = {row["case"]: row for row in grp.to_dict(orient="records")}
        for field in COST_NUMERIC_FIELDS:
            low, base, high = by_case["low"][field], by_case["base"][field], by_case["high"][field]
            if low > base or base > high:
                raise ValueError(
                    f"low/base/high out of order for {field} at {key}: {low}, {base}, {high}"
                )


def load_performance(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    _require_columns(df, REQUIRED_PERFORMANCE_COLUMNS, "performance_assumptions.csv")
    rows = [PerformanceRow.model_validate(rec).model_dump() for rec in df.to_dict(orient="records")]
    return pd.DataFrame(rows)


def inflate_cost_frame(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    out = df.copy()
    money_fields = [
        "sample_cost_fixed",
        "sample_cost_var",
        "prep_cost_fixed",
        "prep_cost_var",
        "read_cost_fixed",
        "read_cost_var",
    ]
    factors = out["price_year"].map(lambda y: cpi_factor(int(y), config.target_price_year, config.cpi))
    for field in money_fields:
        out[field] = out[field] * factors
    out["cpi_factor"] = factors
    out["currency"] = config.currency
    out["price_year_adjusted"] = config.target_price_year
    return out


def option_label(diagnostic: str, method: str) -> str:
    if diagnostic.lower() == "sequencing" and method == "outsourced":
        return "Sequencing-Outsourced"
    if diagnostic.lower() == "sequencing" and method == "in_house":
        return "Sequencing-InHouse"
    if method in {"standard", "", None}:
        return diagnostic
    return f"{diagnostic}-{method}"


def select_case(df: pd.DataFrame, case: str) -> pd.DataFrame:
    if case not in VALID_CASES:
        raise ValueError(f"Unknown case {case!r}")
    return df.loc[df["case"] == case].copy()


def placeholder_flags(df: pd.DataFrame) -> pd.Series:
    return df["source"].astype(str).str.lower().eq("placeholder")
