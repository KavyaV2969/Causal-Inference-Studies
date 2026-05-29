# src/refuters.py

def run_dowhy_refuters(model, identified_estimand, estimate_object):
    results = {}

    refuters = [
        "placebo_treatment_refuter",
        "random_common_cause",
        "data_subset_refuter",
    ]

    for refuter in refuters:
        try:
            result = model.refute_estimate(
                identified_estimand,
                estimate_object,
                method_name=refuter,
            )

            results[refuter] = str(result)

        except Exception as e:
            results[refuter] = f"FAILED: {e}"

    return results