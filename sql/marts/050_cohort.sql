-- Activity retention uses customer-initiated operations, not bank-generated fees/interest.
CREATE OR REPLACE TABLE mart.cohort_activity_retention AS
WITH limits AS (
    SELECT MAX(month_start) AS final_month FROM mart.account_month
), account_cohorts AS (
    SELECT
        account_id,
        date_trunc('quarter', opened_date)::DATE AS cohort_quarter,
        date_trunc('month', opened_date)::DATE AS opened_month
    FROM mart.dim_account
), cohort_sizes AS (
    SELECT cohort_quarter, COUNT(*) AS cohort_accounts
    FROM account_cohorts
    GROUP BY cohort_quarter
), eligible_grid AS (
    SELECT
        c.account_id,
        c.cohort_quarter,
        n.months_since_open,
        (c.opened_month + n.months_since_open * INTERVAL 1 MONTH)::DATE AS activity_month
    FROM account_cohorts c
    CROSS JOIN range(0, 73) n(months_since_open)
    CROSS JOIN limits l
    WHERE c.opened_month + n.months_since_open * INTERVAL 1 MONTH <= l.final_month
), activity AS (
    SELECT account_id, month_start
    FROM mart.account_month
    WHERE customer_transaction_count > 0
)
SELECT
    g.cohort_quarter,
    g.months_since_open,
    s.cohort_accounts,
    COUNT(*) AS observable_accounts,
    COUNT(a.account_id) AS active_accounts,
    COUNT(a.account_id)::DOUBLE / NULLIF(COUNT(*), 0) AS activity_retention_rate
FROM eligible_grid g
JOIN cohort_sizes s USING (cohort_quarter)
LEFT JOIN activity a
    ON g.account_id = a.account_id AND g.activity_month = a.month_start
GROUP BY g.cohort_quarter, g.months_since_open, s.cohort_accounts;

CREATE OR REPLACE TABLE mart.cohort_engagement AS
SELECT
    date_trunc('quarter', a.opened_date)::DATE AS cohort_quarter,
    m.months_since_open,
    COUNT(*) AS observed_accounts,
    AVG(m.customer_transaction_count) AS average_customer_transactions,
    MEDIAN(m.customer_transaction_count) AS median_customer_transactions,
    AVG(m.month_end_balance) AS average_month_end_balance,
    MEDIAN(m.month_end_balance) AS median_month_end_balance,
    AVG((m.customer_transaction_count > 0)::INTEGER) AS active_account_share
FROM mart.account_month m
JOIN mart.dim_account a USING (account_id)
GROUP BY 1, 2;

-- A conjunctive onboarding funnel. Later stages are strict subsets of earlier stages.
CREATE OR REPLACE TABLE mart.onboarding_funnel_account AS
WITH observation AS (
    SELECT MAX(transaction_date) AS final_date FROM mart.fct_transaction
), activity AS (
    SELECT
        a.account_id,
        a.opened_date,
        MIN(t.transaction_date) FILTER (WHERE t.operation_code IS NOT NULL)
            AS first_customer_transaction_date,
        COUNT(DISTINCT date_trunc('month', t.transaction_date)) FILTER (
            WHERE t.operation_code IS NOT NULL
              AND t.transaction_date >= a.opened_date
              AND t.transaction_date < a.opened_date + INTERVAL 6 MONTH
        ) AS active_months_first_6
    FROM mart.dim_account a
    LEFT JOIN mart.fct_transaction t USING (account_id)
    GROUP BY a.account_id, a.opened_date
), products AS (
    SELECT
        a.account_id,
        least(MIN(c.issued_date), MIN(l.loan_date)) AS first_product_date
    FROM mart.dim_account a
    LEFT JOIN mart.fct_card c USING (account_id)
    LEFT JOIN mart.fct_loan l USING (account_id)
    GROUP BY a.account_id
), eligible AS (
    SELECT
        x.*,
        p.first_product_date,
        x.first_customer_transaction_date <= x.opened_date + INTERVAL 30 DAY
            AS activated_within_30d
    FROM activity x
    CROSS JOIN observation o
    LEFT JOIN products p USING (account_id)
    WHERE x.opened_date + INTERVAL 12 MONTH <= o.final_date
)
SELECT
    *,
    activated_within_30d AND active_months_first_6 >= 3 AS engaged_first_6m,
    activated_within_30d
        AND active_months_first_6 >= 3
        AND first_product_date <= opened_date + INTERVAL 12 MONTH AS product_adopted_within_12m
FROM eligible;

CREATE OR REPLACE TABLE mart.onboarding_funnel AS
WITH stages AS (
    SELECT 1 AS stage_order, 'Eligible accounts' AS stage, COUNT(*) AS accounts
    FROM mart.onboarding_funnel_account
    UNION ALL
    SELECT 2, 'Activated within 30 days', COUNT(*)
    FROM mart.onboarding_funnel_account WHERE activated_within_30d
    UNION ALL
    SELECT 3, 'Engaged in first 6 months', COUNT(*)
    FROM mart.onboarding_funnel_account WHERE engaged_first_6m
    UNION ALL
    SELECT 4, 'Card or loan within 12 months', COUNT(*)
    FROM mart.onboarding_funnel_account WHERE product_adopted_within_12m
)
SELECT
    stage_order,
    stage,
    accounts,
    first_value(accounts) OVER (ORDER BY stage_order) AS eligible_accounts,
    accounts::DOUBLE / first_value(accounts) OVER (ORDER BY stage_order) AS conversion_from_eligible,
    accounts::DOUBLE / lag(accounts) OVER (ORDER BY stage_order) AS conversion_from_prior_stage
FROM stages;
