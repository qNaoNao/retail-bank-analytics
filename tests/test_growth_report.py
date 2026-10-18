"""Composition effects must remain visible in observational segment comparisons."""

import pandas as pd
import pytest

from retail_bank_analytics.growth_report import standardize_by_opening_year


def test_year_standardization_exposes_simpsons_paradox():
    cohort = pd.DataFrame(
        [
            {
                "opening_year": 1996,
                "pre180_segment": "A",
                "eligible_accounts": 90,
                "adoption_rate": 0.8,
            },
            {
                "opening_year": 1996,
                "pre180_segment": "B",
                "eligible_accounts": 10,
                "adoption_rate": 0.9,
            },
            {
                "opening_year": 1997,
                "pre180_segment": "A",
                "eligible_accounts": 10,
                "adoption_rate": 0.1,
            },
            {
                "opening_year": 1997,
                "pre180_segment": "B",
                "eligible_accounts": 90,
                "adoption_rate": 0.2,
            },
        ]
    )
    rates = standardize_by_opening_year(cohort).set_index("pre180_segment")
    # Raw A=73%, B=27%; each group gets the same 50/50 year weights instead.
    assert rates.loc["A", "standardized_rate"] == pytest.approx(0.45)
    assert rates.loc["B", "standardized_rate"] == pytest.approx(0.55)
    assert rates.common_years.tolist() == [2, 2]


def test_composition_check_excludes_years_without_both_groups():
    cohort = pd.DataFrame(
        [
            {
                "opening_year": 1996,
                "pre180_segment": "A",
                "eligible_accounts": 10,
                "adoption_rate": 0.2,
            },
            {
                "opening_year": 1996,
                "pre180_segment": "B",
                "eligible_accounts": 10,
                "adoption_rate": 0.3,
            },
            {
                "opening_year": 1997,
                "pre180_segment": "A",
                "eligible_accounts": 999,
                "adoption_rate": 0.9,
            },
        ]
    )
    rates = standardize_by_opening_year(cohort).set_index("pre180_segment")
    assert rates.loc["A", "standardized_rate"] == pytest.approx(0.2)
    assert rates.common_years.tolist() == [1, 1]
