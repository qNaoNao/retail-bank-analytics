"""Interactive decision dashboard for the Retail Bank Customer 360 project."""

from __future__ import annotations

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from retail_bank_analytics.paths import PROJECT_ROOT

DATABASE = PROJECT_ROOT / "data" / "processed" / "retail_bank.duckdb"
NAVY = "#17324D"
BLUE = "#2F6BFF"
TEAL = "#16A39A"
AMBER = "#F2A93B"
RED = "#D95C5C"

st.set_page_config(
    page_title="Retail Bank Customer 360",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1450px;}
    [data-testid="stMetric"] {background:#F7F9FC; border:1px solid #E5EAF0; border-radius:12px; padding:14px;}
    h1, h2, h3 {color:#17324D;}
    .context-note {background:#F2F6FA; border-left:4px solid #2F6BFF; padding:12px 14px; border-radius:6px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    connection = duckdb.connect(str(DATABASE), read_only=True)
    try:
        return connection.execute(sql).fetchdf()
    finally:
        connection.close()


def percent(value: float) -> str:
    return f"{value:.1%}"


def money(value: float) -> str:
    return f"CZK {value:,.0f}"


if not DATABASE.exists():
    st.error("The local analytical database is missing. Run `make warehouse` first.")
    st.stop()

customers = query("SELECT * FROM mart.customer_360")
monthly = query("SELECT * FROM mart.monthly_portfolio ORDER BY month_start")
kpis = query("SELECT * FROM analytics.executive_kpis").iloc[0]

st.sidebar.title("Portfolio filters")
regions = sorted(customers["region_name"].dropna().unique())
segments = sorted(customers["behavior_segment"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
selected_segments = st.sidebar.multiselect("Behaviour segment", segments, default=segments)
selected_gender = st.sidebar.multiselect(
    "Gender", sorted(customers["gender"].unique()), default=sorted(customers["gender"].unique())
)
product_filter = st.sidebar.selectbox(
    "Product holding", ["All", "Card holder", "Loan holder", "Card and loan", "Neither"]
)

filtered = customers[
    customers["region_name"].isin(selected_regions)
    & customers["behavior_segment"].isin(selected_segments)
    & customers["gender"].isin(selected_gender)
].copy()
if product_filter == "Card holder":
    filtered = filtered[filtered["card_count"] > 0]
elif product_filter == "Loan holder":
    filtered = filtered[filtered["loan_count"] > 0]
elif product_filter == "Card and loan":
    filtered = filtered[(filtered["card_count"] > 0) & (filtered["loan_count"] > 0)]
elif product_filter == "Neither":
    filtered = filtered[(filtered["card_count"] == 0) & (filtered["loan_count"] == 0)]

st.sidebar.caption(f"{len(filtered):,} of {len(customers):,} owner accounts selected")

st.title("Retail Bank Customer 360")
st.caption("Growth, engagement and credit-risk analytics · PKDD'99 Czech Financial Dataset")
st.markdown(
    '<div class="context-note"><b>Decision lens:</b> All amounts are historical CZK. '
    "Results are descriptive; filters do not imply product eligibility or causal uplift.</div>",
    unsafe_allow_html=True,
)

overview_tab, customer_tab, engagement_tab, risk_tab, definitions_tab = st.tabs(
    ["Executive overview", "Customer 360", "Cohort & funnel", "Lending risk", "Definitions"]
)

with overview_tab:
    st.subheader("Portfolio at a glance")
    columns = st.columns(5)
    columns[0].metric("Customers", f"{int(kpis.customers):,}")
    columns[1].metric("Transactions", f"{int(kpis.transactions):,}")
    columns[2].metric("Avg. month-end balance", money(kpis.average_month_end_balance))
    columns[3].metric("Card penetration", percent(kpis.card_penetration))
    columns[4].metric("Mature-loan problem rate", percent(kpis.mature_loan_problem_rate))

    left, right = st.columns((1.15, 1))
    with left:
        active_chart = px.line(
            monthly,
            x="month_start",
            y="active_accounts",
            title="Monthly active accounts",
            labels={"month_start": "Month", "active_accounts": "Accounts"},
        )
        active_chart.update_traces(line_color=BLUE, line_width=3)
        active_chart.update_layout(hovermode="x unified")
        st.plotly_chart(active_chart, width="stretch")
    with right:
        flows = monthly.melt(
            id_vars="month_start",
            value_vars=["inflow_amount", "outflow_amount"],
            var_name="flow",
            value_name="amount",
        )
        flow_chart = px.line(
            flows,
            x="month_start",
            y="amount",
            color="flow",
            title="Monthly inflow and outflow",
            labels={"month_start": "Month", "amount": "CZK", "flow": "Flow"},
            color_discrete_map={"inflow_amount": TEAL, "outflow_amount": AMBER},
        )
        flow_chart.update_layout(hovermode="x unified")
        st.plotly_chart(flow_chart, width="stretch")
    st.info(
        "Active-account growth largely reflects the bank portfolio expanding toward its final "
        "4,500 accounts; it should not be presented as same-customer engagement uplift."
    )

with customer_tab:
    st.subheader("Filtered customer and account view")
    if filtered.empty:
        st.warning("No accounts match the selected filters.")
    else:
        cols = st.columns(4)
        cols[0].metric("Selected accounts", f"{len(filtered):,}")
        cols[1].metric("Avg. balance", money(filtered["average_month_end_balance"].mean()))
        cols[2].metric("Card penetration", percent((filtered["card_count"] > 0).mean()))
        cols[3].metric("Loan penetration", percent((filtered["loan_count"] > 0).mean()))

        segment = (
            filtered.groupby("behavior_segment", as_index=False)
            .agg(
                accounts=("account_id", "count"),
                average_balance=("average_month_end_balance", "mean"),
                card_penetration=("card_count", lambda values: (values > 0).mean()),
            )
            .sort_values("accounts", ascending=False)
        )
        left, right = st.columns((0.9, 1.3))
        with left:
            segment_chart = px.bar(
                segment,
                x="accounts",
                y="behavior_segment",
                orientation="h",
                title="Behaviour segments",
                color="average_balance",
                color_continuous_scale=["#DCE8FF", BLUE],
            )
            st.plotly_chart(segment_chart, width="stretch")
        with right:
            scatter = px.scatter(
                filtered,
                x="lifetime_customer_transaction_count",
                y="average_month_end_balance",
                color="behavior_segment",
                size="card_count",
                hover_data=["account_id", "region_name", "loan_count"],
                title="Balance and customer-operated activity",
                labels={
                    "lifetime_customer_transaction_count": "Customer-operated transactions",
                    "average_month_end_balance": "Average month-end balance (CZK)",
                },
            )
            st.plotly_chart(scatter, width="stretch")

        st.markdown("#### Account drill-down")
        account_id = st.selectbox("Account ID", sorted(filtered["account_id"].astype(int).tolist()))
        profile = filtered[filtered["account_id"] == account_id].iloc[0]
        detail_cols = st.columns(5)
        detail_cols[0].metric("Segment", profile.behavior_segment.replace("_", " ").title())
        detail_cols[1].metric("Region", profile.region_name)
        detail_cols[2].metric("Cards", int(profile.card_count))
        detail_cols[3].metric("Loans", int(profile.loan_count))
        detail_cols[4].metric("Minimum balance", money(profile.minimum_observed_balance))
        account_month = query(
            f"SELECT * FROM mart.account_month WHERE account_id={int(account_id)} ORDER BY month_start"
        )
        account_chart = px.line(
            account_month,
            x="month_start",
            y="month_end_balance",
            title=f"Account {int(account_id)} month-end balance",
            labels={"month_start": "Month", "month_end_balance": "CZK"},
        )
        account_chart.update_traces(line_color=NAVY, line_width=2.5)
        st.plotly_chart(account_chart, width="stretch")

with engagement_tab:
    st.subheader("Opening cohorts and onboarding funnel")
    cohort = query(
        """
        SELECT * FROM mart.cohort_engagement
        WHERE months_since_open BETWEEN 0 AND 24
        ORDER BY cohort_quarter, months_since_open
        """
    )
    pivot = cohort.pivot(
        index="cohort_quarter", columns="months_since_open", values="average_month_end_balance"
    )
    heatmap = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Average month-end balance by opening cohort and account age",
        labels={"x": "Months since opening", "y": "Opening cohort", "color": "CZK"},
    )
    st.plotly_chart(heatmap, width="stretch")

    funnel = query("SELECT * FROM mart.onboarding_funnel ORDER BY stage_order")
    funnel_chart = go.Figure(
        go.Funnel(
            y=funnel["stage"],
            x=funnel["accounts"],
            textinfo="value+percent initial",
            marker={"color": [NAVY, BLUE, TEAL, AMBER]},
        )
    )
    funnel_chart.update_layout(title="Conjunctive 12-month onboarding funnel")
    st.plotly_chart(funnel_chart, width="stretch")

    retention = query(
        """
        SELECT months_since_open,
               SUM(active_accounts)::DOUBLE / SUM(observable_accounts) AS retention_rate
        FROM mart.cohort_activity_retention
        WHERE months_since_open <= 36
        GROUP BY months_since_open ORDER BY months_since_open
        """
    )
    retention_chart = px.line(
        retention,
        x="months_since_open",
        y="retention_rate",
        title="Customer-operation activity retention proxy",
        labels={"months_since_open": "Months since opening", "retention_rate": "Active share"},
    )
    retention_chart.update_yaxes(tickformat=".0%", range=[0.9, 1.005])
    retention_chart.update_traces(line_color=TEAL, line_width=3)
    st.plotly_chart(retention_chart, width="stretch")
    st.warning(
        "The proxy remains close to 100%. It is useful as a data-suitability test, but not as "
        "evidence of true customer retention because closures and churn labels are absent."
    )

with risk_tab:
    st.subheader("Loan outcomes and pre-origination indicators")
    loans = query("SELECT * FROM mart.loan_risk_features")
    if not filtered.empty:
        loans = loans[loans["account_id"].isin(set(filtered["account_id"]))]

    risk_cols = st.columns(4)
    mature = loans[loans["is_mature"]]
    risk_cols[0].metric("Selected loans", f"{len(loans):,}")
    risk_cols[1].metric("Finished loans", f"{len(mature):,}")
    risk_cols[2].metric(
        "Finished-loan problem rate",
        percent(mature["is_problem"].mean()) if len(mature) else "n/a",
    )
    risk_cols[3].metric("Running delinquent", f"{(loans['loan_status']=='running_delinquent').sum():,}")

    left, right = st.columns(2)
    with left:
        status = loans.groupby("loan_status", as_index=False).agg(loans=("loan_id", "count"))
        status_chart = px.bar(
            status,
            x="loan_status",
            y="loans",
            color="loan_status",
            title="Loan status mix",
            color_discrete_sequence=[TEAL, BLUE, AMBER, RED],
        )
        st.plotly_chart(status_chart, width="stretch")
    with right:
        mature_chart = px.box(
            mature,
            x="loan_status",
            y="payment_to_monthly_inflow",
            color="loan_status",
            points="outliers",
            title="Scheduled payment burden before origination",
            labels={"payment_to_monthly_inflow": "Payment / average monthly inflow"},
            color_discrete_map={"repaid": TEAL, "defaulted": RED},
        )
        mature_chart.update_yaxes(tickformat=".0%")
        st.plotly_chart(mature_chart, width="stretch")

    region = (
        mature.groupby("region_name", as_index=False)
        .agg(
            mature_loans=("loan_id", "count"),
            problem_loans=("is_problem", "sum"),
            problem_rate=("is_problem", "mean"),
            loan_amount=("loan_amount", "sum"),
        )
        .sort_values("problem_rate", ascending=False)
    )
    region_chart = px.scatter(
        region,
        x="mature_loans",
        y="problem_rate",
        size="loan_amount",
        color="problem_rate",
        text="region_name",
        color_continuous_scale=[TEAL, AMBER, RED],
        title="Regional mature-loan rate with sample size",
        labels={"mature_loans": "Finished loans", "problem_rate": "Problem rate"},
    )
    region_chart.update_yaxes(tickformat=".0%")
    st.plotly_chart(region_chart, width="stretch")
    st.info(
        "Use the bubble size and loan count before interpreting a rate. Small regional samples "
        "are monitoring signals, not sufficient evidence for policy changes."
    )

with definitions_tab:
    st.subheader("Definitions and interpretation guardrails")
    st.markdown(
        """
        - **Monthly active account:** at least one transaction with a recorded customer operation.
        - **Activity retention:** share of observable cohort accounts with a customer-operation transaction in a relative month; not confirmed customer retention.
        - **Mature-loan problem rate:** defaulted finished loans divided by all finished loans. Running loans are excluded from final outcomes.
        - **Payment burden:** scheduled monthly payment divided by average monthly inflow observed before loan origination.
        - **Customer 360:** one row per account owner. Authorized users do not receive account money metrics, preventing double counting.
        - **Behaviour segment:** transparent balance/activity quartiles; a descriptive portfolio label, not a credit or sales decision.
        """
    )
    st.markdown("#### Source limitations")
    st.markdown(
        "Historical 1990s Czech banking data is useful for demonstrating analytical methods. "
        "It is not current market sizing, contains no verified churn label, and has no randomized "
        "campaign treatment. Raw data remains local because no explicit modern redistribution "
        "license was found."
    )
