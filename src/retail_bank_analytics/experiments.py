"""Uncertainty and fixed-horizon planning for a future randomized card offer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, isfinite, sqrt
from statistics import NormalDist


def wilson_interval(successes: int, total: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval; handles zero/all successes without zero-width intervals."""
    if total <= 0 or not 0 <= successes <= total or not 0 < confidence < 1:
        raise ValueError("Require total > 0, 0 <= successes <= total, and 0 < confidence < 1")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    rate = successes / total
    divisor = 1 + z * z / total
    centre = (rate + z * z / (2 * total)) / divisor
    half = z * sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / divisor
    return max(0.0, centre - half), min(1.0, centre + half)


def sample_size_per_arm(
    baseline: float, absolute_mde: float, alpha: float = 0.05, power: float = 0.8
) -> int:
    """Normal approximation for independent proportions, equal allocation, two-sided test.

    MDE is an absolute probability change (0.02 means two percentage points).
    No continuity correction, sequential peeking, clustering or attrition adjustment.
    """
    if not all(isfinite(x) for x in (baseline, absolute_mde, alpha, power)):
        raise ValueError("Inputs must be finite")
    if not 0 < baseline < 1 or not 0 < absolute_mde < 1 - baseline:
        raise ValueError("Require 0 < baseline < baseline + absolute_mde < 1")
    if not 0 < alpha < 1 or not 0.5 < power < 1:
        raise ValueError("Require 0 < alpha < 1 and 0.5 < power < 1")
    treatment = baseline + absolute_mde
    pooled = (baseline + treatment) / 2
    z_alpha = NormalDist().inv_cdf(1 - alpha / 2)
    z_power = NormalDist().inv_cdf(power)
    numerator = z_alpha * sqrt(2 * pooled * (1 - pooled)) + z_power * sqrt(
        baseline * (1 - baseline) + treatment * (1 - treatment)
    )
    return ceil(numerator * numerator / (absolute_mde * absolute_mde))


@dataclass(frozen=True)
class ExperimentPlan:
    baseline: float
    absolute_mde: float
    per_arm: int
    total_accounts: int
    recruitment_days: int
    outcome_days: int
    minimum_calendar_days: int
    fits_available_population: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def plan_experiment(
    baseline: float,
    absolute_mde: float,
    available_accounts: int,
    eligible_accounts_per_day: int,
    outcome_days: int = 180,
) -> ExperimentPlan:
    """Hypothetical traffic and MDE are explicit; source contains no experiment log."""
    if available_accounts < 0 or eligible_accounts_per_day <= 0 or outcome_days <= 0:
        raise ValueError("Require a nonnegative population and positive traffic/outcome days")
    per_arm = sample_size_per_arm(baseline, absolute_mde)
    recruitment = ceil(2 * per_arm / eligible_accounts_per_day)
    return ExperimentPlan(
        baseline,
        absolute_mde,
        per_arm,
        2 * per_arm,
        recruitment,
        outcome_days,
        recruitment + outcome_days,
        2 * per_arm <= available_accounts,
    )
