"""Fixed/variable cost, time, break-even, and cost-effectiveness formulas."""

from __future__ import annotations

from typing import Optional

import numpy as np

EPS = 1e-12


def total_cost(
    n: float,
    fixed_sample: float,
    fixed_read: float,
    var_sample: float,
    var_read: float,
    qc_overhead: float,
) -> float:
    """total_cost(N) = fixed_sample + fixed_read + N * (var_sample + var_read) * (1 + qc_overhead)."""
    if n < 0:
        raise ValueError("N must be non-negative")
    return fixed_sample + fixed_read + n * (var_sample + var_read) * (1.0 + qc_overhead)


def cost_per_test(
    n: float,
    fixed_sample: float,
    fixed_read: float,
    var_sample: float,
    var_read: float,
    qc_overhead: float,
) -> float:
    if n <= 0:
        raise ValueError("N must be positive to compute cost per test")
    return total_cost(n, fixed_sample, fixed_read, var_sample, var_read, qc_overhead) / n


def variable_cost_per_test(var_sample: float, var_read: float, qc_overhead: float) -> float:
    return (var_sample + var_read) * (1.0 + qc_overhead)


def effective_fixed_cost(fixed_sample: float, fixed_read: float, volume_basis: str, amortization_years: float) -> float:
    """Apply annual amortization when volume is treated as yearly throughput."""
    total_fixed = fixed_sample + fixed_read
    if volume_basis == "annual":
        if amortization_years <= 0:
            raise ValueError("amortization_years must be positive when volume_basis is annual")
        return total_fixed / amortization_years
    if volume_basis == "one_time":
        return total_fixed
    raise ValueError(f"Unknown volume_basis {volume_basis!r}; expected 'annual' or 'one_time'")


def amortize_factor(volume_basis: str, amortization_years: float) -> float:
    if volume_basis == "annual":
        if amortization_years <= 0:
            raise ValueError("amortization_years must be positive when volume_basis is annual")
        return 1.0 / amortization_years
    if volume_basis == "one_time":
        return 1.0
    raise ValueError(f"Unknown volume_basis {volume_basis!r}; expected 'annual' or 'one_time'")


def split_amortized_fixed(
    fixed_sample,
    fixed_read,
    volume_basis: str,
    amortization_years: float,
):
    """Return amortized (fixed_sample, fixed_read). Accepts scalars or numpy arrays."""
    factor = amortize_factor(volume_basis, amortization_years)
    return fixed_sample * factor, fixed_read * factor


def minutes_to_days(minutes: float) -> float:
    return minutes / (60.0 * 24.0)


def total_time_days(
    n: float,
    sample_time_fixed_days: float,
    read_time_fixed_days: float,
    sample_time_var_min: float,
    read_time_var_min: float,
    parallel_capacity: float,
) -> float:
    """total_time(N) = fixed_time + (N * var_time) / parallel_capacity, in days."""
    if np.any(np.asarray(parallel_capacity) <= 0):
        raise ValueError("parallel_capacity must be positive")
    fixed_time = sample_time_fixed_days + read_time_fixed_days
    var_days = minutes_to_days(sample_time_var_min + read_time_var_min)
    return fixed_time + (n * var_days) / parallel_capacity


def accuracy(sensitivity: float, specificity: float, prevalence: float) -> float:
    return sensitivity * prevalence + specificity * (1.0 - prevalence)


def cost_per_correct_result(cost_per_test_value: float, accuracy_value: float) -> float:
    if accuracy_value <= 0:
        return float("inf")
    return cost_per_test_value / accuracy_value


def cost_per_true_positive(cost_per_test_value: float, sensitivity: float, prevalence: float) -> float:
    denom = sensitivity * prevalence
    if denom <= 0:
        return float("inf")
    return cost_per_test_value / denom


def break_even_n(
    fixed_a: float,
    var_a: float,
    fixed_b: float,
    var_b: float,
) -> Optional[float]:
    """N where total costs are equal: (fixed_A - fixed_B) / (var_B - var_A).

    `var_*` must already include QC overhead. Returns None when there is no
    positive crossover (one option dominates at all N, or variable costs are equal).
    """
    denom = var_b - var_a
    if abs(denom) < EPS:
        return None
    n = (fixed_a - fixed_b) / denom
    if n > 0:
        return n
    return None


def dominance_note(fixed_a: float, var_a: float, fixed_b: float, var_b: float) -> str:
    """Describe the relationship when there is no positive break-even."""
    if abs(var_a - var_b) < EPS:
        if abs(fixed_a - fixed_b) < EPS:
            return "identical cost structure"
        cheaper = "A" if fixed_a < fixed_b else "B"
        return f"{cheaper} has lower fixed cost and the same variable cost, so {cheaper} dominates at all N"
    n = break_even_n(fixed_a, var_a, fixed_b, var_b)
    if n is not None:
        return f"crossover at N={n:.1f}"
    if var_a < var_b and fixed_a <= fixed_b:
        return "A dominates at all N (lower or equal fixed cost and lower variable cost)"
    if var_b < var_a and fixed_b <= fixed_a:
        return "B dominates at all N (lower or equal fixed cost and lower variable cost)"
    if var_a < var_b:
        return "A is cheaper for all positive N (crossover is not positive)"
    return "B is cheaper for all positive N (crossover is not positive)"
