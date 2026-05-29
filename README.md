# Causal Change Failure Analysis

This project estimates the causal effect of high test coverage on change failure risk using a synthetic Change Request Process (CRP) dataset.

The main pipeline generates synthetic data, builds an analysis dataset, defines a backdoor-adjustment DAG, estimates treatment effects with DoWhy and logistic regression, runs diagnostics, applies refuters, and writes result artifacts to `outputs/`.

## Question

The primary causal question is:

> What is the average treatment effect of high test coverage on the probability of change failure?

In the current configuration:

- Treatment: `high_test_coverage`
- Outcome: `failure`
- Estimand: Average Treatment Effect (ATE)

## Current Example Result

From the generated output in `outputs/results/high_test_coverage_result.json`:

- Estimated effect: `-7.12` percentage points
- 95% bootstrap CI: `-9.79` to `-3.99` percentage points
- Predicted failure probability if treated: `7.75%`
- Predicted failure probability if untreated: `14.87%`
- Recommendation status: `recommend`

Interpretation: under the stated DAG assumptions and the synthetic observed data, high test coverage is estimated to reduce change failure probability.

## Project Structure

```text
.
├── main.py
├── requirements.txt
├── data/
│   └── raw/
│       └── synthetic_crp_data.csv
├── outputs/
│   ├── reports/
│   │   └── high_test_coverage_summary.txt
│   └── results/
│       ├── high_test_coverage_balance.csv
│       └── high_test_coverage_result.json
├── practice/
│   ├── causal.ipynb
│   ├── ChatGPT-Causal Inference Basics.md
│   └── ChatGPT-Causal Inference Basics.pdf
└── src/
    ├── config.py
    ├── dag.py
    ├── data_validation.py
    ├── diagnostics.py
    ├── estimators.py
    ├── feature_engineering.py
    ├── refuters.py
    ├── reporting.py
    ├── synthetic_data.py
    └── what_if.py
```

## Pipeline

`main.py` performs the following steps:

1. Creates required data and output directories.
2. Generates a synthetic CRP dataset.
3. Encodes categorical variables and builds the analysis dataset.
4. Checks treated/control counts and outcome rates.
5. Builds a DOT-format causal DAG.
6. Estimates causal effects using DoWhy.
7. Estimates a logistic-regression average marginal treatment effect.
8. Bootstraps a 95% confidence interval.
9. Computes propensity scores, overlap diagnostics, IPW weights, and balance diagnostics.
10. Runs DoWhy refuters.
11. Saves JSON, text, and CSV outputs.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

On Windows, `pygraphviz` can require a local Graphviz installation and build tooling. If installation fails, install Graphviz first and make sure its `bin` directory is available on `PATH`.

## Run

```powershell
python main.py
```

The script prints a summary and writes outputs to:

- `outputs/results/high_test_coverage_result.json`
- `outputs/results/high_test_coverage_balance.csv`
- `outputs/reports/high_test_coverage_summary.txt`

## Key Modules

- `src/config.py`: central configuration for treatment, outcome, paths, confounders, and seed.
- `src/synthetic_data.py`: synthetic CRP data generation.
- `src/feature_engineering.py`: categorical encoding and adjustment-set construction.
- `src/dag.py`: backdoor DAG construction.
- `src/estimators.py`: DoWhy estimators, logistic ATE, and bootstrap confidence interval.
- `src/diagnostics.py`: propensity-score overlap and covariate balance checks.
- `src/refuters.py`: DoWhy refutation checks.
- `src/reporting.py`: result object and text summary generation.
- `src/what_if.py`: helper functions for binary intervention simulation.

## Outputs

The JSON output contains:

- treatment and outcome names
- adjustment set
- data sufficiency checks
- DoWhy estimates
- main logistic marginal effect estimate
- bootstrap confidence interval
- overlap diagnostics
- balance diagnostics
- refuter results
- recommendation status

The balance CSV reports standardized mean differences before and after weighting for each covariate.

## Notes

This project uses synthetic data, so the results are useful for learning, workflow validation, and causal-method experimentation. They should not be interpreted as evidence about a real production change-management process unless the synthetic data generation is replaced with validated real-world data and the causal assumptions are reviewed.
