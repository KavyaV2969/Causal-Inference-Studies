# src/estimators.py

import numpy as np
import pandas as pd
import statsmodels.api as sm


def clean_model_matrix(df, treatment_col, outcome_col, covariate_cols):
    covariate_cols = [
        c for c in covariate_cols
        if c not in [treatment_col, outcome_col]
    ]

    cols = [treatment_col, outcome_col] + covariate_cols
    data = df[cols].copy()

    data = data.apply(pd.to_numeric, errors="coerce").dropna()

    usable_covariates = []
    for col in covariate_cols:
        if data[col].nunique() > 1:
            usable_covariates.append(col)

    data = data[[treatment_col, outcome_col] + usable_covariates]

    # Remove duplicate columns
    data = data.loc[:, ~data.T.duplicated()]

    final_covariates = [
        c for c in data.columns
        if c not in [treatment_col, outcome_col]
    ]

    return data, final_covariates


def logistic_ate(df, treatment_col, outcome_col, covariate_cols):
    data, clean_covariates = clean_model_matrix(
        df=df,
        treatment_col=treatment_col,
        outcome_col=outcome_col,
        covariate_cols=covariate_cols,
    )

    y = data[outcome_col]

    X = sm.add_constant(
        data[[treatment_col] + clean_covariates],
        has_constant="add",
    )

    try:
        model = sm.Logit(y, X).fit(disp=False, maxiter=200)
    except np.linalg.LinAlgError:
        # Fallback: regularized logistic regression handles singularity better
        model = sm.Logit(y, X).fit_regularized(
            alpha=1.0,
            disp=False,
            maxiter=500,
        )

    X1 = X.copy()
    X1[treatment_col] = 1

    X0 = X.copy()
    X0[treatment_col] = 0

    p1 = model.predict(X1)
    p0 = model.predict(X0)

    ate = float(np.mean(p1 - p0))

    return {
        "ate": ate,
        "ate_pp": ate * 100,
        "p_treated": float(p1.mean()),
        "p_untreated": float(p0.mean()),
        "model": model,
        "used_covariates": clean_covariates,
        "n": len(data),
    }


def bootstrap_logistic_ate(
    df,
    treatment_col,
    outcome_col,
    covariate_cols,
    n_bootstrap=300,
    seed=42,
):
    rng = np.random.default_rng(seed)

    data, clean_covariates = clean_model_matrix(
        df=df,
        treatment_col=treatment_col,
        outcome_col=outcome_col,
        covariate_cols=covariate_cols,
    )

    effects = []
    failures = 0

    for _ in range(n_bootstrap):
        sample_idx = rng.choice(data.index, size=len(data), replace=True)
        sample = data.loc[sample_idx]

        try:
            effect = logistic_ate(
                sample,
                treatment_col,
                outcome_col,
                clean_covariates,
            )["ate"]

            effects.append(effect)

        except Exception:
            failures += 1

    effects = np.array(effects)

    point = logistic_ate(
        data,
        treatment_col,
        outcome_col,
        clean_covariates,
    )["ate"]

    return {
        "point_estimate": point,
        "point_estimate_pp": point * 100,
        "lower_95": float(np.percentile(effects, 2.5)),
        "upper_95": float(np.percentile(effects, 97.5)),
        "lower_95_pp": float(np.percentile(effects, 2.5) * 100),
        "upper_95_pp": float(np.percentile(effects, 97.5) * 100),
        "successful_bootstraps": len(effects),
        "failed_bootstraps": failures,
    }

def clean_model_matrix(df, treatment_col, outcome_col, covariate_cols):
    data = df[[treatment_col, outcome_col] + covariate_cols].dropna().copy()

    # Never allow treatment/outcome inside covariates
    covariate_cols = [
        c for c in covariate_cols
        if c not in [treatment_col, outcome_col]
    ]

    # Keep only numeric columns
    cols = [treatment_col, outcome_col] + covariate_cols
    data = data[cols].apply(pd.to_numeric, errors="coerce").dropna()

    # Remove zero-variance covariates
    usable_covariates = []
    for col in covariate_cols:
        if data[col].nunique() > 1:
            usable_covariates.append(col)

    data = data[[treatment_col, outcome_col] + usable_covariates]

    # Remove duplicate columns
    data = data.loc[:, ~data.T.duplicated()]

    final_covariates = [
        c for c in data.columns
        if c not in [treatment_col, outcome_col]
    ]

    return data, final_covariates