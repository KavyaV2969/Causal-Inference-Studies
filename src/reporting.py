# src/reporting.py

def assign_recommendation_status(effect_pp, lower_pp, upper_pp, overlap_summary, balance_summary):
    if overlap_summary["share_outside_common_support"] > 0.2:
        return "not_estimable_due_to_poor_overlap"

    if balance_summary["share_weighted_smd_below_0_1"] < 0.8:
        return "inconclusive_due_to_poor_balance"

    if effect_pp < 0 and upper_pp < 0:
        return "recommend"

    if effect_pp < 0 and lower_pp < 0 < upper_pp:
        return "recommend_with_caution"

    if lower_pp <= 0 <= upper_pp:
        return "inconclusive"

    if effect_pp > 0 and lower_pp > 0:
        return "do_not_recommend_potential_harm"

    return "inconclusive"


def build_result_object(
    treatment_col,
    outcome_col,
    adjustment_set,
    data_sufficiency,
    dowhy_estimates,
    logistic_result,
    ci_result,
    overlap_summary,
    balance_summary,
    refuter_results,
):
    status = assign_recommendation_status(
        effect_pp=logistic_result["ate_pp"],
        lower_pp=ci_result["lower_95_pp"],
        upper_pp=ci_result["upper_95_pp"],
        overlap_summary=overlap_summary,
        balance_summary=balance_summary,
    )

    return {
        "treatment": treatment_col,
        "outcome": outcome_col,
        "estimand": "ATE",
        "adjustment_set": adjustment_set,
        "data_sufficiency": data_sufficiency,
        "dowhy_estimates": {
            key: value.get("value")
            for key, value in dowhy_estimates.items()
        },
        "main_estimate": {
            "method": "logistic_average_marginal_effect",
            "ate": logistic_result["ate"],
            "ate_pp": logistic_result["ate_pp"],
            "p_failure_if_treated": logistic_result["p_treated"],
            "p_failure_if_untreated": logistic_result["p_untreated"],
            "ci_95_pp": [
                ci_result["lower_95_pp"],
                ci_result["upper_95_pp"],
            ],
        },
        "diagnostics": {
            "overlap": overlap_summary,
            "balance": balance_summary,
            "refuters": refuter_results,
        },
        "recommendation_status": status,
    }


def generate_text_summary(result):
    effect = result["main_estimate"]["ate_pp"]
    lower, upper = result["main_estimate"]["ci_95_pp"]

    p1 = result["main_estimate"]["p_failure_if_treated"] * 100
    p0 = result["main_estimate"]["p_failure_if_untreated"] * 100

    return f"""
Treatment:
{result["treatment"]}

Outcome:
{result["outcome"]}

Estimated effect:
{effect:.2f} percentage points

95% CI:
{lower:.2f} to {upper:.2f} percentage points

Predicted failure probability:
If treated: {p1:.2f}%
If untreated: {p0:.2f}%

Recommendation status:
{result["recommendation_status"]}

Interpretation:
Under the stated DAG assumptions and observed data, {result["treatment"]} is estimated to change failure probability by {effect:.2f} percentage points.

Adjustment set:
{", ".join(result["adjustment_set"])}
"""