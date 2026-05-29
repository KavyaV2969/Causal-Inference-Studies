# main.py

import json
from pathlib import Path

from src.config import (
    RAW_DATA_PATH,
    TREATMENT_HIGH_TEST_COVERAGE,
    OUTCOME,
    CATEGORICAL_COLUMNS,
    BASE_CONFOUNDERS,
    RANDOM_SEED,
)

from src.synthetic_data import save_synthetic_data
from src.feature_engineering import build_analysis_dataset
from src.data_validation import check_data_sufficiency
from src.dag import build_backdoor_dot_graph
from src.estimators import (
    run_dowhy_estimators,
    logistic_ate,
    bootstrap_logistic_ate,
)
from src.diagnostics import (
    add_propensity_scores,
    summarize_overlap,
    add_ipw_weights,
    balance_report,
    summarize_balance,
)
from src.refuters import run_dowhy_refuters
from src.reporting import build_result_object, generate_text_summary


def main():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("outputs/results").mkdir(parents=True, exist_ok=True)
    Path("outputs/reports").mkdir(parents=True, exist_ok=True)

    # 1. Generate synthetic data
    df = save_synthetic_data(
        path=RAW_DATA_PATH,
        n=5000,
        seed=RANDOM_SEED,
    )

    treatment = TREATMENT_HIGH_TEST_COVERAGE
    outcome = OUTCOME

    # 2. Build modeling dataset
    analysis_df, adjustment_set = build_analysis_dataset(
        df=df,
        treatment_col=treatment,
        outcome_col=outcome,
        base_confounders=BASE_CONFOUNDERS,
        categorical_cols=CATEGORICAL_COLUMNS,
    )

    # 3. Data checks
    sufficiency = check_data_sufficiency(
        analysis_df,
        treatment,
        outcome,
    )

    # 4. DAG
    graph = build_backdoor_dot_graph(
        treatment_col=treatment,
        outcome_col=outcome,
        confounders=adjustment_set,
    )

    # 5. DoWhy estimation
    model, identified_estimand, dowhy_estimates = run_dowhy_estimators(
        df=analysis_df,
        treatment_col=treatment,
        outcome_col=outcome,
        graph=graph,
    )

    # Use linear regression estimate object for refuters
    lr_estimate_object = dowhy_estimates["linear_regression"]["object"]

    # 6. Logistic marginal effect
    logistic_result = logistic_ate(
        df=analysis_df,
        treatment_col=treatment,
        outcome_col=outcome,
        covariate_cols=adjustment_set,
    )

    # 7. Bootstrap CI
    ci_result = bootstrap_logistic_ate(
        df=analysis_df,
        treatment_col=treatment,
        outcome_col=outcome,
        covariate_cols=adjustment_set,
        n_bootstrap=300,
        seed=RANDOM_SEED,
    )

    # 8. Diagnostics
    ps_df, _ = add_propensity_scores(
        df=analysis_df,
        treatment_col=treatment,
        covariate_cols=adjustment_set,
    )

    overlap_summary = summarize_overlap(ps_df, treatment)

    weighted_df = add_ipw_weights(ps_df, treatment)

    balance_df = balance_report(
        df=analysis_df,
        weighted_df=weighted_df,
        treatment_col=treatment,
        covariate_cols=adjustment_set,
    )

    balance_summary = summarize_balance(balance_df)

    # 9. Refuters
    refuter_results = run_dowhy_refuters(
        model=model,
        identified_estimand=identified_estimand,
        estimate_object=lr_estimate_object,
    )

    # 10. Result object
    result = build_result_object(
        treatment_col=treatment,
        outcome_col=outcome,
        adjustment_set=adjustment_set,
        data_sufficiency=sufficiency,
        dowhy_estimates=dowhy_estimates,
        logistic_result=logistic_result,
        ci_result=ci_result,
        overlap_summary=overlap_summary,
        balance_summary=balance_summary,
        refuter_results=refuter_results,
    )

    summary = generate_text_summary(result)

    # 11. Save outputs
    with open("outputs/results/high_test_coverage_result.json", "w") as f:
        json.dump(result, f, indent=2)

    with open("outputs/reports/high_test_coverage_summary.txt", "w") as f:
        f.write(summary)

    balance_df.to_csv("outputs/results/high_test_coverage_balance.csv", index=False)

    print(summary)


if __name__ == "__main__":
    main()