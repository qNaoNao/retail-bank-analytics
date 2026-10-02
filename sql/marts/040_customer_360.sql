-- Grain: one row per owned account. Owner-only attribution prevents double counting.
CREATE OR REPLACE TABLE mart.account_360 AS
WITH transaction_metrics AS (
    SELECT
        account_id,
        MIN(month_start) AS first_transaction_month,
        MAX(month_start) AS last_transaction_month,
        COUNT(*) AS observed_months,
        COUNT(*) FILTER (WHERE customer_transaction_count > 0) AS active_months,
        SUM(transaction_count) AS lifetime_transaction_count,
        SUM(customer_transaction_count) AS lifetime_customer_transaction_count,
        SUM(inflow_amount) AS lifetime_inflow,
        SUM(outflow_amount) AS lifetime_outflow,
        SUM(net_cash_flow) AS lifetime_net_cash_flow,
        AVG(month_end_balance) AS average_month_end_balance,
        MEDIAN(month_end_balance) AS median_month_end_balance,
        stddev_samp(month_end_balance) AS balance_volatility,
        MIN(minimum_balance) AS minimum_observed_balance,
        MAX(month_end_balance) AS maximum_month_end_balance,
        SUM(card_transaction_count) AS card_transaction_count
    FROM mart.account_month
    GROUP BY account_id
), product_metrics AS (
    SELECT
        a.account_id,
        COUNT(DISTINCT c.card_id) AS card_count,
        COUNT(DISTINCT l.loan_id) AS loan_count,
        MAX(c.issued_date) AS latest_card_issue_date,
        MAX(l.loan_date) AS latest_loan_date,
        MAX(l.is_problem::INTEGER) AS has_problem_loan
    FROM mart.dim_account a
    LEFT JOIN mart.fct_card c USING (account_id)
    LEFT JOIN mart.fct_loan l USING (account_id)
    GROUP BY a.account_id
), scored AS (
    SELECT
        a.*,
        t.* EXCLUDE (account_id),
        p.* EXCLUDE (account_id),
        ntile(4) OVER (ORDER BY t.average_month_end_balance NULLS FIRST) AS balance_quartile,
        ntile(4) OVER (ORDER BY t.lifetime_customer_transaction_count NULLS FIRST)
            AS activity_quartile
    FROM mart.dim_account a
    LEFT JOIN transaction_metrics t USING (account_id)
    LEFT JOIN product_metrics p USING (account_id)
)
SELECT
    *,
    CASE
        WHEN balance_quartile = 4 AND activity_quartile = 4 THEN 'high_value_engaged'
        WHEN balance_quartile = 4 AND activity_quartile <= 2 THEN 'high_value_low_engagement'
        WHEN activity_quartile = 4 THEN 'high_activity_mass'
        WHEN balance_quartile = 1 AND activity_quartile = 1 THEN 'low_activity_low_balance'
        ELSE 'core'
    END AS behavior_segment
FROM scored;

CREATE OR REPLACE TABLE mart.customer_360 AS
SELECT
    b.client_id,
    a.account_id,
    c.birth_date,
    date_diff('year', c.birth_date, DATE '1998-12-31') AS age_at_dataset_end,
    c.gender,
    c.district_id,
    d.district_name,
    d.region_name,
    d.average_salary AS district_average_salary,
    a.opened_date,
    a.statement_frequency,
    a.first_transaction_month,
    a.last_transaction_month,
    a.observed_months,
    a.active_months,
    a.lifetime_transaction_count,
    a.lifetime_customer_transaction_count,
    a.lifetime_inflow,
    a.lifetime_outflow,
    a.lifetime_net_cash_flow,
    a.average_month_end_balance,
    a.median_month_end_balance,
    a.balance_volatility,
    a.minimum_observed_balance,
    a.maximum_month_end_balance,
    a.card_transaction_count,
    a.card_count,
    a.loan_count,
    a.has_problem_loan,
    a.balance_quartile,
    a.activity_quartile,
    a.behavior_segment
FROM mart.account_360 a
JOIN mart.bridge_account_client b
    ON a.account_id = b.account_id AND b.relationship_type = 'owner'
JOIN mart.dim_client c USING (client_id)
JOIN mart.dim_district d ON c.district_id = d.district_id;
