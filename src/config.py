RANDOM_SEED = 42

RAW_DATA_PATH = "data/raw/synthetic_crp_data.csv"
PROCESSED_DATA_PATH = "data/processed/analysis_dataset.csv"

TREATMENT_HIGH_TEST_COVERAGE = "high_test_coverage"
TREATMENT_ROLLBACK_PLAN = "rollback_plan_present"

OUTCOME = "failure"

TEST_COVERAGE_THRESHOLD = 80

CATEGORICAL_COLUMNS = [
    "priority",
    "change_type",
    "environment",
    "deployment_window",
]

BASE_CONFOUNDERS = [
    "change_complexity",
    "assignment_group_failure_rate_90d",
    "change_frequency_90d",
    "off_hours_deployment",
    "approval_count",
    "cab_involvement",
    "rollback_plan_present",
]