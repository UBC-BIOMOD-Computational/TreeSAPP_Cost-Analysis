import pytest

from cost_model import break_even_n, cost_per_test, dominance_note, total_cost, total_time_days
from units import amount_in_volume_to_nM, concentration_to_nM


def test_total_cost_formula():
    n = 1000
    fixed_sample, fixed_read = 100.0, 400.0
    var_sample, var_read = 2.0, 3.0
    qc = 0.10
    expected = 100 + 400 + 1000 * (2 + 3) * 1.10
    assert total_cost(n, fixed_sample, fixed_read, var_sample, var_read, qc) == expected
    assert cost_per_test(n, fixed_sample, fixed_read, var_sample, var_read, qc) == expected / n


def test_break_even_hand_computed():
    # A: fixed 1000, var 5; B: fixed 100, var 6
    # 1000 + 5N = 100 + 6N -> N = 900
    assert break_even_n(1000, 5, 100, 6) == 900


def test_one_option_dominates_all_n():
    # A cheaper fixed and cheaper variable
    assert break_even_n(100, 2, 200, 3) is None
    note = dominance_note(100, 2, 200, 3)
    assert "A dominates at all N" in note


def test_total_time_parallel_capacity():
    # 2 days fixed + (100 * 1440 min = 100 days of serial work) / 10 capacity = 10 days
    elapsed = total_time_days(100, 1.0, 1.0, 720, 720, 10)
    assert elapsed == 12.0


def test_literature_concentration_conversion():
    # 0.5 pmol in 10 uL = 50 nM
    assert amount_in_volume_to_nM(0.5, "pmol", 10, "uL") == pytest.approx(50.0)
    assert concentration_to_nM(50, "nM") == 50.0
    assert concentration_to_nM(0.1, "pM") == 0.0001
