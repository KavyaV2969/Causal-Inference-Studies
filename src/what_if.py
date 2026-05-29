# src/what_if.py

def simulate_binary_intervention_logit(
    fitted_model,
    row_df,
    treatment_col,
    treatment_value,
):
    row_cf = row_df.copy()
    row_cf[treatment_col] = treatment_value

    return float(fitted_model.predict(row_cf)[0])


def compute_risk_reduction(baseline_prob, simulated_prob):
    absolute_reduction = baseline_prob - simulated_prob

    if baseline_prob > 0:
        relative_reduction = absolute_reduction / baseline_prob
    else:
        relative_reduction = None

    return {
        "absolute_reduction": absolute_reduction,
        "absolute_reduction_pp": absolute_reduction * 100,
        "relative_reduction": relative_reduction,
        "relative_reduction_percent": (
            relative_reduction * 100 if relative_reduction is not None else None
        ),
    }