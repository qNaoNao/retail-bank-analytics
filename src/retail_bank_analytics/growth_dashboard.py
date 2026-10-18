"""Business-facing growth diagnostics and a prospective experiment planning panel."""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from retail_bank_analytics.experiments import plan_experiment, wilson_interval


def with_intervals(frame: pd.DataFrame, successes: str, total: str) -> pd.DataFrame:
    result = frame.copy()
    intervals = [wilson_interval(int(k), int(n)) for k, n in zip(result[successes], result[total])]
    result["ci_low"] = [interval[0] for interval in intervals]
    result["ci_high"] = [interval[1] for interval in intervals]
    return result


def render_growth(query: Callable[[str], pd.DataFrame], *, synthetic: bool = False) -> None:
    st.subheader("Growth diagnostics & experiment planning")
    st.caption(
        "Scope: all accounts. Region, lifetime-segment and product filters apply only to "
        "Customer 360 / Lending risk. This page uses its own opening-year filter."
    )
    growth = query("SELECT * FROM analytics.monthly_growth ORDER BY month_start")
    if growth.empty:
        st.info("No complete calendar month is observable yet.")
        return
    selected_month = st.selectbox(
        "Growth month (complete months only)",
        growth.month_start.tolist(),
        index=len(growth) - 1,
        format_func=lambda value: value.strftime("%Y-%m"),
    )
    month = growth[growth.month_start == selected_month].iloc[0]
    cols = st.columns(4)
    cols[0].metric(
        "Active accounts this month",
        f"{int(month.active_accounts):,}",
        f"{int(month.net_active_change):+,} vs prior month",
    )
    cols[1].metric("First active", f"{int(month.new_active_accounts):,}")
    cols[2].metric("Reactivated", f"{int(month.reactivated_accounts):,}")
    cols[3].metric("Became inactive", f"{int(month.newly_inactive_accounts):,}")
    bridge = go.Figure(
        go.Waterfall(
            x=[
                "Previous<br>active",
                "First<br>active",
                "Reactivated",
                "Became<br>inactive",
                "Current<br>active",
            ],
            y=[
                int(month.previous_active_accounts),
                int(month.new_active_accounts),
                int(month.reactivated_accounts),
                -int(month.newly_inactive_accounts),
                0,
            ],
            measure=["absolute", "relative", "relative", "relative", "total"],
            increasing={"marker": {"color": "#16A39A"}},
            decreasing={"marker": {"color": "#D95C5C"}},
            totals={"marker": {"color": "#17324D"}},
        )
    )
    bridge.update_layout(title="Monthly activity bridge", yaxis_title="Accounts")
    st.plotly_chart(bridge, width="stretch")
    st.caption(
        "Reconciliation: current active = prior active + first active + reactivated − newly inactive. "
        "Inactivity means no recorded customer operation in that month, not account closure. "
        "Months containing only fees or interest do not count as activity."
    )
    st.download_button(
        "Download monthly growth bridge",
        growth.to_csv(index=False),
        "monthly_growth.csv",
        "text/csv",
    )

    st.markdown("#### Is the card-adoption gap measurable?")
    landmark = query("SELECT * FROM mart.card_adoption_landmark")
    years = sorted(landmark.opening_year.dt.year.unique().tolist())
    chosen_years = st.multiselect("Opening years", years, default=years)
    selected = landmark[landmark.opening_year.dt.year.isin(chosen_years)]
    eligible = selected[selected.card_free_at_landmark & selected.outcome_observable]
    cols = st.columns(3)
    cols[0].metric("Observed card-free accounts", f"{len(eligible):,}")
    cols[1].metric(
        "Excluded: incomplete follow-up", f"{int((~selected.outcome_observable).sum()):,}"
    )
    cols[2].metric(
        "Excluded: card before landmark", f"{int((~selected.card_free_at_landmark).sum()):,}"
    )
    st.caption(
        "Features: [opening, day 180). Eligible: card-free at day 180. Outcome: first card "
        "issued in [day 180, day 360). Only fully observed outcomes enter rates. Exclusion "
        "counts can overlap. Issuance does not establish card use, revenue or offer eligibility."
    )
    if eligible.empty:
        st.info("No fully observed, card-free accounts in these opening years.")
        return
    summary = eligible.groupby("pre180_segment", as_index=False).agg(
        eligible_accounts=("account_id", "size"), adopted_accounts=("card_adopted_next180d", "sum")
    )
    summary["adoption_rate"] = summary.adopted_accounts / summary.eligible_accounts
    summary = with_intervals(summary, "adopted_accounts", "eligible_accounts")
    summary["chart_label"] = summary.pre180_segment.map(
        {
            "Transfer used before day 180": "Prior outgoing<br>transfer",
            "No outgoing transfer before day 180": "No prior outgoing<br>transfer",
            "No observed transactions": "No observed<br>transactions",
        }
    )
    figure = px.bar(
        summary,
        x="adoption_rate",
        y="chart_label",
        orientation="h",
        error_x=(summary.ci_high - summary.adoption_rate).clip(lower=0),
        error_x_minus=(summary.adoption_rate - summary.ci_low).clip(lower=0),
        hover_data=["eligible_accounts", "adopted_accounts"],
        title="First-card issuance · 95% CI",
        labels={
            "chart_label": "Prior behavior",
            "adoption_rate": "First-card issuance rate",
        },
    )
    figure.update_xaxes(tickformat=".1%")
    st.plotly_chart(figure, width="stretch")
    st.dataframe(summary.drop(columns="chart_label"), hide_index=True, width="stretch")
    with st.expander("Check opening-year composition before comparing groups"):
        cohort = eligible.groupby(["opening_year", "pre180_segment"], as_index=False).agg(
            eligible_accounts=("account_id", "size"),
            adopted_accounts=("card_adopted_next180d", "sum"),
        )
        cohort["adoption_rate"] = cohort.adopted_accounts / cohort.eligible_accounts
        st.dataframe(cohort, hide_index=True, width="stretch")
    st.info(
        "These are observational groups. Confidence intervals describe sampling uncertainty, "
        "not selection bias; timing, branch policy and customer differences can explain the gap. "
        "A larger descriptive rate does not establish incremental campaign benefit."
    )

    st.markdown("#### Plan a future randomized offer")
    successes = int(eligible.card_adopted_next180d.sum())
    baseline = successes / len(eligible)
    lower, upper = wilson_interval(successes, len(eligible))
    st.markdown(
        f"{'Illustrative synthetic' if synthetic else 'Historical planning'} baseline: "
        f"**{successes:,}/{len(eligible):,} = {baseline:.2%}** "
        f"(95% Wilson interval {lower:.2%}–{upper:.2%}). Re-estimate on a current population "
        "before running an experiment. No treatment/control results exist in this dataset."
    )
    if not 0 < baseline < 1:
        st.warning(
            "This selection has a zero or saturated baseline; sample-size planning is unavailable."
        )
        return
    left, right = st.columns(2)
    maximum_mde_pp = float(min(20, (1 - baseline) * 99))
    mde_pp = left.number_input(
        "Assumed minimum detectable increase (percentage points)",
        min_value=min(0.1, maximum_mde_pp / 10),
        max_value=maximum_mde_pp,
        value=min(2.0, maximum_mde_pp / 2),
        step=min(0.1, maximum_mde_pp / 10),
    )
    traffic = right.number_input(
        "Assumed newly eligible accounts per day", min_value=1, max_value=100000, value=50, step=10
    )
    plan = plan_experiment(baseline, mde_pp / 100, len(eligible), int(traffic))
    cols = st.columns(3)
    cols[0].metric("Required per arm", f"{plan.per_arm:,}")
    cols[1].metric("Required total", f"{plan.total_accounts:,}")
    cols[2].metric("Recruit + mature outcomes", f"≥ {plan.minimum_calendar_days:,} days")
    if plan.fits_available_population:
        st.success(
            "The displayed candidate count meets this illustrative sample-size requirement. Current consent, suitability and traffic remain unmeasured."
        )
    else:
        st.warning(
            "This candidate pool is too small for the assumed effect. Acquire more comparable traffic, or reconsider the metric / detectable effect before launching."
        )
    st.caption(
        "Two-sided α=5%, power=80%, 1:1 account randomization; independent-proportion normal "
        "approximation, no continuity correction or attrition allowance. Calendar lower bound = "
        "recruitment at assumed traffic + 180-day follow-up. No repeated peeking."
    )
    st.download_button(
        "Download prospective experiment plan",
        pd.Series(plan.to_dict()).to_json(indent=2),
        "experiment_plan.json",
        "application/json",
    )
