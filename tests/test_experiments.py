"""Known score-interval values and planning behavior, independent of historical files."""

import math

import pytest

from retail_bank_analytics.experiments import plan_experiment, sample_size_per_arm, wilson_interval


def test_wilson_known_values_and_boundary_successes():
    assert wilson_interval(31, 234) == pytest.approx((0.0949234721, 0.1819057197), abs=1e-9)
    lower, upper = wilson_interval(0, 100)
    assert lower == pytest.approx(0, abs=1e-12)
    assert upper == pytest.approx(0.0369935, abs=1e-7)
    assert wilson_interval(100, 100)[0] == pytest.approx(1 - upper)


@pytest.mark.parametrize("successes,total", [(0, 0), (-1, 20), (21, 20)])
def test_wilson_rejects_invalid_counts(successes, total):
    with pytest.raises(ValueError):
        wilson_interval(successes, total)


def test_sample_size_has_expected_scale_and_direction():
    # A 10% -> 12% two-proportion fixed-horizon design needs about 3,841 per arm.
    assert 3800 < sample_size_per_arm(0.10, 0.02) < 3900
    assert sample_size_per_arm(0.10, 0.01) > sample_size_per_arm(0.10, 0.02)
    assert sample_size_per_arm(0.10, 0.02, power=0.9) > sample_size_per_arm(0.10, 0.02)


@pytest.mark.parametrize(
    "p,delta", [(0, 0.02), (1, 0.02), (0.99, 0.02), (0.1, 0), (math.nan, 0.02)]
)
def test_invalid_planning_inputs_do_not_produce_a_fake_sample_size(p, delta):
    with pytest.raises(ValueError):
        sample_size_per_arm(p, delta)


def test_duration_includes_outcome_maturation_and_population_gate():
    plan = plan_experiment(0.1, 0.02, 100, 50)
    assert not plan.fits_available_population
    assert plan.total_accounts == 2 * plan.per_arm
    assert plan.minimum_calendar_days == plan.recruitment_days + 180
