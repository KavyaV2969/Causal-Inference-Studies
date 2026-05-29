# src/data_validation.py

def validate_required_columns(df, required_columns):
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return True


def data_quality_report(df, treatment_col, outcome_col):
    return {
        "n_rows": len(df),
        "n_columns": df.shape[1],
        "missing_rate": df.isna().mean().sort_values(ascending=False).to_dict(),
        "treatment_counts": df[treatment_col].value_counts(dropna=False).to_dict(),
        "outcome_counts": df[outcome_col].value_counts(dropna=False).to_dict(),
        "outcome_rate": float(df[outcome_col].mean()),
    }


def check_data_sufficiency(df, treatment_col, outcome_col):
    treated = df[df[treatment_col] == 1]
    control = df[df[treatment_col] == 0]

    return {
        "n": len(df),
        "treated_count": len(treated),
        "control_count": len(control),
        "treated_failures": int(treated[outcome_col].sum()),
        "control_failures": int(control[outcome_col].sum()),
        "overall_failure_rate": float(df[outcome_col].mean()),
    }