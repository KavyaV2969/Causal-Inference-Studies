# src/diagnostics.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


def add_propensity_scores(df, treatment_col, covariate_cols):
    data = df[[treatment_col] + covariate_cols].dropna().copy()

    X = data[covariate_cols]
    T = data[treatment_col]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, T)

    data["propensity_score"] = model.predict_proba(X)[:, 1]

    return data, model


def summarize_overlap(ps_df, treatment_col):
    treated = ps_df[ps_df[treatment_col] == 1]["propensity_score"]
    control = ps_df[ps_df[treatment_col] == 0]["propensity_score"]

    common_min = max(treated.min(), control.min())
    common_max = min(treated.max(), control.max())

    outside_common_support = (
        (ps_df["propensity_score"] < common_min)
        | (ps_df["propensity_score"] > common_max)
    ).mean()

    return {
        "treated_min": float(treated.min()),
        "treated_max": float(treated.max()),
        "control_min": float(control.min()),
        "control_max": float(control.max()),
        "common_support_min": float(common_min),
        "common_support_max": float(common_max),
        "share_outside_common_support": float(outside_common_support),
    }


def add_ipw_weights(ps_df, treatment_col):
    df = ps_df.copy()

    eps = 1e-6
    ps = df["propensity_score"].clip(eps, 1 - eps)

    df["ipw_weight"] = np.where(
        df[treatment_col] == 1,
        1 / ps,
        1 / (1 - ps),
    )

    return df


def standardized_mean_difference(
    df,
    treatment_col,
    covariate_col,
    weight_col=None,
):
    treated = df[df[treatment_col] == 1]
    control = df[df[treatment_col] == 0]

    if weight_col is None:
        mean_t = treated[covariate_col].mean()
        mean_c = control[covariate_col].mean()
        var_t = treated[covariate_col].var()
        var_c = control[covariate_col].var()
    else:
        mean_t = np.average(treated[covariate_col], weights=treated[weight_col])
        mean_c = np.average(control[covariate_col], weights=control[weight_col])

        var_t = np.average(
            (treated[covariate_col] - mean_t) ** 2,
            weights=treated[weight_col],
        )

        var_c = np.average(
            (control[covariate_col] - mean_c) ** 2,
            weights=control[weight_col],
        )

    pooled_sd = np.sqrt((var_t + var_c) / 2)

    if pooled_sd == 0 or np.isnan(pooled_sd):
        return 0.0

    return float((mean_t - mean_c) / pooled_sd)


def balance_report(df, weighted_df, treatment_col, covariate_cols):
    rows = []

    for col in covariate_cols:
        rows.append({
            "covariate": col,
            "smd_unweighted": standardized_mean_difference(
                df,
                treatment_col,
                col,
            ),
            "smd_weighted": standardized_mean_difference(
                weighted_df,
                treatment_col,
                col,
                weight_col="ipw_weight",
            ),
        })

    return pd.DataFrame(rows)


def summarize_balance(balance_df):
    return {
        "max_abs_smd_unweighted": float(balance_df["smd_unweighted"].abs().max()),
        "max_abs_smd_weighted": float(balance_df["smd_weighted"].abs().max()),
        "share_weighted_smd_below_0_1": float(
            (balance_df["smd_weighted"].abs() < 0.1).mean()
        ),
    }