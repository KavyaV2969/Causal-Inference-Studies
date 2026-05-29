# src/feature_engineering.py

import pandas as pd


def encode_categorical_variables(df, categorical_cols):
    return pd.get_dummies(
        df,
        columns=categorical_cols,
        drop_first=True,
        dummy_na=True,
        dtype=int,
    )


def get_encoded_confounders(df):
    encoded = [
        col for col in df.columns
        if col.startswith("priority_")
        or col.startswith("environment_")
        or col.startswith("change_type_")
        or col.startswith("deployment_window_")
    ]

    return encoded


def build_analysis_dataset(
    df,
    treatment_col,
    outcome_col,
    base_confounders,
    categorical_cols,
):
    df_encoded = encode_categorical_variables(df, categorical_cols)

    encoded_confounders = get_encoded_confounders(df_encoded)

    # Avoid including the treatment itself as a confounder.
    adjustment_set = [
        col for col in base_confounders + encoded_confounders
        if col != treatment_col
    ]

    model_cols = [treatment_col, outcome_col] + adjustment_set

    analysis_df = df_encoded[model_cols].dropna().copy()

    return analysis_df, adjustment_set