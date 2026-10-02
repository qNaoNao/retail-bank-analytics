-- Origination-time features use only transactions strictly before loan_date.
CREATE OR REPLACE TABLE mart.loan_risk_features AS
WITH owner AS (
    SELECT account_id, client_id
    FROM mart.bridge_account_client
    WHERE relationship_type = 'owner'
), preloan AS (
    SELECT
        l.loan_id,
        COUNT(t.transaction_id) AS preloan_transaction_count,
        SUM(t.amount) FILTER (WHERE t.direction = 'inflow') AS preloan_total_inflow,
        SUM(t.amount) FILTER (WHERE t.direction = 'outflow') AS preloan_total_outflow,
        AVG(t.balance_after_transaction) AS preloan_average_balance,
        MIN(t.balance_after_transaction) AS preloan_minimum_balance,
        stddev_samp(t.balance_after_transaction) AS preloan_balance_volatility,
        COUNT(DISTINCT date_trunc('month', t.transaction_date)) AS preloan_observed_months,
        MAX(t.transaction_date) AS feature_window_end
    FROM mart.fct_loan l
    LEFT JOIN mart.fct_transaction t
        ON l.account_id = t.account_id
        AND t.transaction_date < l.loan_date
    GROUP BY l.loan_id
)
SELECT
    l.loan_id,
    l.account_id,
    o.client_id,
    l.loan_date,
    l.loan_amount,
    l.duration_months,
    l.monthly_payment,
    l.loan_status_code,
    l.loan_status,
    l.is_mature,
    l.is_problem,
    a.opened_date,
    date_diff('month', a.opened_date, l.loan_date) AS account_tenure_months_at_loan,
    c.gender,
    date_diff('year', c.birth_date, l.loan_date) AS age_at_loan,
    c.district_id,
    d.region_name,
    d.average_salary AS district_average_salary,
    d.unemployment_rate_1996,
    p.preloan_transaction_count,
    p.preloan_total_inflow,
    p.preloan_total_outflow,
    p.preloan_average_balance,
    p.preloan_minimum_balance,
    p.preloan_balance_volatility,
    p.preloan_observed_months,
    p.feature_window_end,
    l.monthly_payment / NULLIF(p.preloan_total_inflow / NULLIF(p.preloan_observed_months, 0), 0)
        AS payment_to_monthly_inflow
FROM mart.fct_loan l
JOIN mart.dim_account a USING (account_id)
JOIN owner o USING (account_id)
JOIN mart.dim_client c USING (client_id)
JOIN mart.dim_district d ON c.district_id = d.district_id
LEFT JOIN preloan p USING (loan_id);

CREATE OR REPLACE TABLE mart.loan_portfolio_summary AS
SELECT
    CASE WHEN is_mature THEN 'mature' ELSE 'running' END AS portfolio_state,
    loan_status,
    COUNT(*) AS loan_count,
    SUM(loan_amount) AS original_loan_amount,
    AVG(loan_amount) AS average_loan_amount,
    AVG(monthly_payment) AS average_monthly_payment,
    AVG(is_problem::INTEGER) AS problem_share
FROM mart.fct_loan
GROUP BY 1, 2;
