"""Reproducible decision memo and offline HTML report from governed growth marts."""

from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px

from retail_bank_analytics.experiments import plan_experiment, wilson_interval


def memo_html(lines: list[str]) -> str:
    """Render the generated memo's small Markdown subset as safe, readable HTML."""

    def inline(text: str) -> str:
        safe = escape(text)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", safe)

    html: list[str] = []
    table: list[list[str]] = []
    in_list = False

    def flush_table() -> None:
        if not table:
            return
        html.append('<div class="table-scroll"><table>')
        for index, row in enumerate(table):
            if index == 1 and all(set(cell) <= set("-: ") for cell in row):
                continue
            tag = "th" if index == 0 else "td"
            html.append(
                "<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in row) + "</tr>"
            )
        html.append("</table></div>")
        table.clear()

    for line in lines:
        if line.startswith("|"):
            table.append([part.strip() for part in line.strip("|").split("|")])
            continue
        flush_table()
        if in_list and not line.startswith("- "):
            html.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("- "):
            if not in_list:
                html.append("<ul>")
                in_list = True
            html.append(f"<li>{inline(line[2:])}</li>")
        elif line.startswith("#"):
            level = min(6, len(line) - len(line.lstrip("#")))
            html.append(f"<h{level}>{inline(line.lstrip('# '))}</h{level}>")
        else:
            html.append(f"<p>{inline(line)}</p>")
    flush_table()
    if in_list:
        html.append("</ul>")
    return "\n".join(html)


def standardize_by_opening_year(cohort: pd.DataFrame) -> pd.DataFrame:
    """Reweight each observed behavior group to the same common-year composition.

    Only years with every compared group are included; weights are pooled eligible
    accounts in those years. This addresses opening-year mix, not unmeasured confounding.
    """
    groups = cohort.pre180_segment.unique()
    common = cohort.groupby("opening_year").pre180_segment.nunique()
    years = common[common == len(groups)].index
    usable = cohort[cohort.opening_year.isin(years)].copy()
    if usable.empty:
        return pd.DataFrame(columns=["pre180_segment", "standardized_rate", "common_years"])
    weights = usable.groupby("opening_year").eligible_accounts.sum()
    weights /= weights.sum()
    usable["weighted_rate"] = usable.adoption_rate * usable.opening_year.map(weights)
    result = usable.groupby("pre180_segment", as_index=False).weighted_rate.sum()
    result = result.rename(columns={"weighted_rate": "standardized_rate"})
    result["common_years"] = len(years)
    return result


def generate_growth_report(database: Path, markdown: Path, output_dir: Path) -> dict:
    """Write facts, planning assumptions and limitations together, never inferred uplift."""
    with duckdb.connect(str(database), read_only=True) as connection:
        kind = connection.execute("SELECT dataset_kind FROM analytics.dataset_metadata").fetchone()[
            0
        ]
        if kind != "historical":
            raise ValueError(
                "The historical findings report cannot be generated from synthetic data"
            )
        growth = connection.execute(
            "SELECT * FROM analytics.monthly_growth ORDER BY month_start"
        ).fetchdf()
        segment = connection.execute(
            "SELECT * FROM analytics.card_adoption_segments ORDER BY pre180_segment"
        ).fetchdf()
        cohort = connection.execute(
            "SELECT * FROM analytics.card_adoption_by_cohort ORDER BY opening_year,pre180_segment"
        ).fetchdf()
        as_of, complete = connection.execute(
            "SELECT as_of_date,last_complete_month FROM analytics.observation_window"
        ).fetchone()
        candidates, adopted, censored, prior_card = connection.execute("""
            SELECT COUNT(*) FILTER(WHERE card_free_at_landmark AND outcome_observable),
                COUNT(*) FILTER(WHERE card_free_at_landmark AND outcome_observable AND card_adopted_next180d),
                COUNT(*) FILTER(WHERE NOT outcome_observable),
                COUNT(*) FILTER(WHERE NOT card_free_at_landmark)
            FROM mart.card_adoption_landmark
        """).fetchone()
        saturation = connection.execute(
            "SELECT accounts FROM mart.onboarding_funnel WHERE stage_order=2"
        ).fetchone()[0]
        total = connection.execute("SELECT count(*) FROM mart.dim_account").fetchone()[0]
    lower, upper = wilson_interval(adopted, candidates)
    baseline = adopted / candidates
    standardized = standardize_by_opening_year(cohort)
    intervals = [
        wilson_interval(int(r.adopted_accounts), int(r.eligible_accounts))
        for r in segment.itertuples()
    ]
    segment["ci_low"] = [i[0] for i in intervals]
    segment["ci_high"] = [i[1] for i in intervals]
    segment = segment.merge(standardized, on="pre180_segment", how="left")
    plans = [
        plan_experiment(baseline, delta, candidates, 50).to_dict() for delta in (0.005, 0.01, 0.02)
    ]
    last = growth.iloc[-1]
    last_year = growth[growth.month_start.dt.year == growth.month_start.dt.year.max()]
    first_active = int(last_year.new_active_accounts.sum())
    reactivated = int(last_year.reactivated_accounts.sum())
    lost = int(last_year.newly_inactive_accounts.sum())
    evidence = {
        "dataset_kind": kind,
        "as_of_date": str(as_of),
        "last_complete_month": str(complete),
        "card_eligible_accounts": candidates,
        "card_adopted_accounts": adopted,
        "card_adoption_rate": baseline,
        "card_adoption_wilson95": [lower, upper],
        "incomplete_followup_accounts": censored,
        "prior_card_accounts": prior_card,
        "latest_active_accounts": int(last.active_accounts),
        "latest_net_change": int(last.net_active_change),
        "last_year_first_active_events": first_active,
        "last_year_reactivation_events": reactivated,
        "last_year_newly_inactive_events": lost,
        "planning_scenarios": plans,
    }
    lines = [
        "# Growth Decision Memo",
        "",
        f"Rebuilt from the historical warehouse through **{as_of}**. Last complete month: {complete:%Y-%m}.",
        "",
        "## Decision",
        "",
        "Prioritize measurement and a scoped card-offer experiment design. Do not recommend a broad retention campaign from this source: transaction activity is almost universal, closures are absent, and offers / consent are unobserved.",
        "",
        "## 1. Explain the active-account change before calling it growth",
        "",
        f"In {last.month_start:%Y-%m}, {int(last.previous_active_accounts):,} prior active + {int(last.new_active_accounts):,} first active + {int(last.reactivated_accounts):,} reactivated − {int(last.newly_inactive_accounts):,} newly inactive = **{int(last.active_accounts):,} active** (net {int(last.net_active_change):+,}).",
        f"Across {last_year.month_start.dt.year.max()}, there were {first_active:,} first-active, {reactivated:,} reactivation and {lost:,} newly-inactive **events**. The same account can reactivate more than once; annual sums are not unique customers.",
        "",
        "The spine includes account-months with no transaction. Only complete calendar months enter the bridge. 'First active' is the first observed customer operation, not necessarily the account-opening month; 'newly inactive' is a monthly transition, not churn.",
        "",
        "## 2. Choose a metric that has room to move",
        "",
        f"The existing 30-day activation stage reaches {saturation:,}/{total:,} accounts ({saturation / total:.1%}). It is a poor primary experiment endpoint in this sample.",
        "Use a narrower prospective endpoint: first card issuance in days **[180, 360)**, among accounts with no card before day 180. Build behavior features only in **[opening, day 180)**. The cutoff is account-specific, and immature labels stay NULL.",
        f"Fully observed candidates: **{candidates:,}**; first-card issuances: **{adopted:,}**; rate **{baseline:.2%}** (95% Wilson interval **{lower:.2%}–{upper:.2%}**). Excluded for incomplete follow-up: {censored:,}; card already issued before landmark: {prior_card:,}. Exclusions can overlap.",
        "",
        "| Prior behavior | Candidates | Issued | Rate | 95% Wilson interval | Common-year standardized rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in segment.itertuples():
        standardized_rate = (
            "n/a" if pd.isna(row.standardized_rate) else f"{row.standardized_rate:.2%}"
        )
        lines.append(
            f"| {row.pre180_segment} | {row.eligible_accounts:,} | {row.adopted_accounts:,} | {row.adoption_rate:.2%} | {row.ci_low:.2%}–{row.ci_high:.2%} | {standardized_rate} |"
        )
    lines += [
        "",
        "The standardized comparison uses the same pooled opening-year weights and only years containing every compared group. This checks composition effects; neither the raw nor standardized rate establishes treatment uplift. Card issuance also does not establish card use or revenue. Confidence intervals do not correct selection bias.",
        "",
        "## 3. Check whether an experiment could finish",
        "",
        "Planning assumptions: account-level 1:1 randomization, two-sided α=5%, 80% power; independent-proportion normal approximation, no continuity correction or attrition allowance. Traffic of **50 newly eligible accounts/day is an assumption**, not an observed channel metric. The target change is a planning MDE, not an estimated campaign effect.",
        "",
        "| Assumed absolute increase | Per arm | Total required | Fits historical pool? | Recruitment + 180-day outcome |",
        "|---|---:|---:|---|---:|",
    ]
    for plan in plans:
        lines.append(
            f"| {plan['absolute_mde'] * 100:.1f} pp | {plan['per_arm']:,} | {plan['total_accounts']:,} | {'Yes' if plan['fits_available_population'] else 'No'} | ≥{plan['minimum_calendar_days']:,} days |"
        )
    lines += [
        "",
        "Historical eligibility is an upper bound: consent, suitability, contactability and current product rules can reduce it. This pool contains cohorts from several years, not simultaneously recruitable traffic. Even 'fits' is only an arithmetic check, not launch approval.",
        "",
        "## 4. Pre-register a real test before sending offers",
        "",
        "- **Hypothesis:** a consented educational card offer at the landmark increases first-card issuance within the next 180 days by at least the selected MDE.",
        "- **Assignment:** randomize by owner account before exposure; preserve the same assignment on repeat visits; stratify by opening cohort / region if appropriate. Deduplicate owners if future data contains multiple accounts per person.",
        "- **Primary analysis:** intention-to-treat difference in proportions with a two-sided 95% interval after all assigned accounts mature. Include unexposed assigned accounts; report exposure separately.",
        "- **Diagnostics:** check allocation counts / sample-ratio mismatch, cross-arm contamination, event deduplication and missing outcomes before effect estimation. Stop a broken test rather than interpreting its p-value.",
        "- **Guardrails:** complaints / opt-outs, unsuitable offers, operational cost and later credit stress. Current source cannot measure these; instrument them before launch. Issuance alone is insufficient to claim revenue or ROI.",
        "- **Decision:** ship only if the pre-registered practical-effect criterion and guardrails pass; otherwise iterate or stop. No repeated significance peeking or causal claim from observational segments.",
        "",
        "## Deliverables",
        "",
        "SQL: `sql/marts/080_growth.sql`; dashboard: Growth & experiments; local exports: monthly bridge CSV, cohort/segment CSV, planning JSON and `outputs/growth_report.html`. Regenerate with `make growth-report`.",
        "",
    ]
    markdown.parent.mkdir(parents=True, exist_ok=True)
    markdown.write_text("\n".join(lines), encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "growth_summary.json").write_text(json.dumps(evidence, indent=2) + "\n")
    growth.to_csv(output_dir / "monthly_growth.csv", index=False)
    segment.to_csv(output_dir / "card_adoption_segments.csv", index=False)
    cohort.to_csv(output_dir / "card_adoption_by_cohort.csv", index=False)
    chart = px.line(
        growth,
        x="month_start",
        y=[
            "active_accounts",
            "new_active_accounts",
            "reactivated_accounts",
            "newly_inactive_accounts",
        ],
        title="Monthly growth components · complete months",
    )
    chart.update_layout(template="plotly_white", legend_title_text="Metric")
    figure = chart.to_html(full_html=False, include_plotlyjs=True)
    html = f"""<!doctype html><html lang="en"><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Retail Bank Growth Decision Report</title><style>
    body{{max-width:1120px;margin:40px auto;padding:0 24px;font:16px/1.65 system-ui;color:#17324d}}
    table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{padding:9px;border:1px solid #dce3ea;text-align:left}}
    th{{background:#eef3fb}}.table-scroll{{overflow-x:auto}}h2{{margin-top:40px}}
    .memo{{background:#f5f8fc;padding:24px;border-radius:12px}}code{{font-size:.85em;overflow-wrap:anywhere}}
    @media print{{body{{max-width:none;margin:0}}.modebar{{display:none}}}}
    </style><h1>Retail Bank · Growth Decision Report</h1>
    <p>Historical source through {as_of}. Generated from tested SQL; no treatment effects are claimed.</p>
    {figure}<div class="memo">{memo_html(lines)}</div>
    <p>Offline report: charts and data are embedded; no external script host is required.</p></html>"""
    (output_dir / "growth_report.html").write_text(html, encoding="utf-8")
    return evidence
