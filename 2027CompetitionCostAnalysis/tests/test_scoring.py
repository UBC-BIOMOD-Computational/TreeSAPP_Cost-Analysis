import pandas as pd

from scoring import score_group


def test_weights_applied_and_rank():
    df = pd.DataFrame(
        [
            {
                "option": "A",
                "cost_per_test": 10.0,
                "total_time_days": 5.0,
                "sensitivity": 0.9,
                "specificity": 0.9,
                "technical_feasibility_score": 1.0,
                "invasiveness_score": 0.2,
                "regulatory_burden_score": 0.2,
                "feasibility_gate": "pass",
            },
            {
                "option": "B",
                "cost_per_test": 50.0,
                "total_time_days": 50.0,
                "sensitivity": 0.5,
                "specificity": 0.5,
                "technical_feasibility_score": 0.1,
                "invasiveness_score": 1.0,
                "regulatory_burden_score": 1.0,
                "feasibility_gate": "pass",
            },
        ]
    )
    weights = {
        "accuracy": 0.35,
        "turnaround": 0.20,
        "feasibility": 0.20,
        "invasiveness": 0.10,
        "regulatory_burden": 0.15,
    }
    overall = {"cost": 0.5, "effectiveness": 0.5}
    scored = score_group(df, weights, overall, prevalence=0.05, excluded_gates=["fail", "unknown"])
    assert scored.loc[scored["option"] == "A", "rank_overall"].iloc[0] == 1
    assert scored["effectiveness_score"].between(0, 1).all()


def test_failed_gate_excluded_from_best_overall():
    df = pd.DataFrame(
        [
            {
                "option": "CheapFail",
                "cost_per_test": 1.0,
                "total_time_days": 1.0,
                "sensitivity": 1.0,
                "specificity": 1.0,
                "technical_feasibility_score": 1.0,
                "invasiveness_score": 0.1,
                "regulatory_burden_score": 0.1,
                "feasibility_gate": "fail",
            },
            {
                "option": "Ok",
                "cost_per_test": 20.0,
                "total_time_days": 10.0,
                "sensitivity": 0.8,
                "specificity": 0.8,
                "technical_feasibility_score": 0.5,
                "invasiveness_score": 0.5,
                "regulatory_burden_score": 0.5,
                "feasibility_gate": "pass",
            },
        ]
    )
    weights = {
        "accuracy": 0.2,
        "turnaround": 0.2,
        "feasibility": 0.2,
        "invasiveness": 0.2,
        "regulatory_burden": 0.2,
    }
    scored = score_group(df, weights, {"cost": 0.5, "effectiveness": 0.5}, 0.05, ["fail", "unknown"])
    assert bool(scored.loc[scored["option"] == "CheapFail", "eligible_best_overall"].iloc[0]) is False
    assert scored.loc[scored["option"] == "Ok", "rank_overall"].iloc[0] == 1
