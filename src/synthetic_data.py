import numpy as np
import pandas as pd


def generate_synthetic_crp_data(n=5000, seed=42):
    rng = np.random.default_rng(seed)

    change_complexity = rng.normal(0, 1, n)
    group_quality = rng.normal(0, 1, n)

    priority = rng.choice(
        ["Low", "Medium", "High", "Critical"],
        size=n,
        p=[0.25, 0.45, 0.22, 0.08],
    )

    environment = rng.choice(
        ["Dev", "QA", "Staging", "Production"],
        size=n,
        p=[0.20, 0.25, 0.25, 0.30],
    )

    change_type = rng.choice(
        ["Standard", "Normal", "Emergency"],
        size=n,
        p=[0.45, 0.45, 0.10],
    )

    priority_risk = pd.Series(priority).map({
        "Low": -0.5,
        "Medium": 0.0,
        "High": 0.7,
        "Critical": 1.2,
    }).to_numpy()

    env_risk = pd.Series(environment).map({
        "Dev": -0.8,
        "QA": -0.4,
        "Staging": 0.0,
        "Production": 0.8,
    }).to_numpy()

    type_risk = pd.Series(change_type).map({
        "Standard": -0.4,
        "Normal": 0.2,
        "Emergency": 1.0,
    }).to_numpy()

    assignment_group_failure_rate_90d = np.clip(
        0.08 + 0.04 * change_complexity - 0.03 * group_quality + rng.normal(0, 0.02, n),
        0.01,
        0.35,
    )

    change_frequency_90d = np.clip(
        20 + 8 * group_quality + rng.normal(0, 5, n),
        1,
        None,
    )

    test_coverage = np.clip(
        65
        - 8 * change_complexity
        + 7 * group_quality
        - 10 * (change_type == "Emergency")
        + rng.normal(0, 12, n),
        0,
        100,
    )

    high_test_coverage = (test_coverage >= 80).astype(int)

    rollback_logit = (
        -0.2
        + 0.9 * change_complexity
        + 0.6 * priority_risk
        + 0.5 * env_risk
        + rng.normal(0, 0.4, n)
    )

    p_rollback = 1 / (1 + np.exp(-rollback_logit))
    rollback_plan_present = rng.binomial(1, p_rollback)

    approval_count = np.clip(
        np.round(2 + 1.5 * priority_risk + 1.0 * change_complexity + rng.normal(0, 1, n)),
        1,
        8,
    ).astype(int)

    cab_involvement = (
        (environment == "Production")
        & (
            (priority == "High")
            | (priority == "Critical")
            | (change_type == "Emergency")
        )
    ).astype(int)

    deployment_window = rng.choice(
        ["BusinessHours", "OffHours", "Weekend"],
        size=n,
        p=[0.55, 0.30, 0.15],
    )

    off_hours_deployment = (deployment_window != "BusinessHours").astype(int)

    failure_logit = (
        -2.2
        + 0.9 * change_complexity
        - 0.7 * group_quality
        + 0.6 * priority_risk
        + 0.5 * env_risk
        + 0.7 * type_risk
        - 0.75 * high_test_coverage
        - 0.45 * rollback_plan_present
        + 0.25 * off_hours_deployment
        + rng.normal(0, 0.3, n)
    )

    p_failure = 1 / (1 + np.exp(-failure_logit))
    failure = rng.binomial(1, p_failure)

    return pd.DataFrame({
        "change_id": [f"CHG{i:06d}" for i in range(n)],
        "priority": priority,
        "change_type": change_type,
        "environment": environment,
        "change_complexity": change_complexity,
        "assignment_group_failure_rate_90d": assignment_group_failure_rate_90d,
        "change_frequency_90d": change_frequency_90d,
        "test_coverage": test_coverage,
        "high_test_coverage": high_test_coverage,
        "rollback_plan_present": rollback_plan_present,
        "approval_count": approval_count,
        "cab_involvement": cab_involvement,
        "deployment_window": deployment_window,
        "off_hours_deployment": off_hours_deployment,
        "failure": failure,
        "true_failure_probability": p_failure,
    })


def save_synthetic_data(path, n=5000, seed=42):
    df = generate_synthetic_crp_data(n=n, seed=seed)
    df.to_csv(path, index=False)
    return df