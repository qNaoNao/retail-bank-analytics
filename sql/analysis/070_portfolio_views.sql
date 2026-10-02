-- Business-facing views consumed by the dashboard. Metric logic stays in SQL.
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.executive_kpis AS
SELECT
    (SELECT COUNT(*) FROM mart.customer_360) AS customers,
    (SELECT COUNT(*) FROM mart.dim_account) AS accounts,
    (SELECT COUNT(*) FROM mart.fct_transaction) AS transactions,
    (SELECT SUM(amount) FROM mart.fct_transaction WHERE direction = 'inflow') AS total_inflow,
    (SELECT SUM(amount) FROM mart.fct_transaction WHERE direction = 'outflow') AS total_outflow,
    (SELECT AVG(month_end_balance) FROM mart.account_month) AS average_month_end_balance,
    (SELECT AVG((card_count > 0)::INTEGER) FROM mart.account_360) AS card_penetration,
    (SELECT AVG((loan_count > 0)::INTEGER) FROM mart.account_360) AS loan_penetration,
    (SELECT AVG(is_problem::INTEGER) FROM mart.fct_loan WHERE is_mature) AS mature_loan_problem_rate;

CREATE OR REPLACE VIEW analytics.segment_summary AS
SELECT
    behavior_segment,
    COUNT(*) AS customer_count,
    COUNT(*) FILTER (WHERE loan_count > 0) AS loan_customer_count,
    COUNT(*) FILTER (WHERE has_problem_loan = 1) AS problem_loan_customer_count,
    AVG(average_month_end_balance) AS average_month_end_balance,
    AVG(lifetime_customer_transaction_count) AS average_customer_transactions,
    AVG((card_count > 0)::INTEGER) AS card_penetration,
    AVG((loan_count > 0)::INTEGER) AS loan_penetration,
    AVG(has_problem_loan) FILTER (WHERE loan_count > 0) AS problem_loan_share
FROM mart.customer_360
GROUP BY behavior_segment;

CREATE OR REPLACE VIEW analytics.risk_by_region AS
SELECT
    region_name,
    COUNT(*) FILTER (WHERE is_mature) AS mature_loans,
    COUNT(*) FILTER (WHERE is_mature AND is_problem) AS mature_problem_loans,
    AVG(is_problem::INTEGER) FILTER (WHERE is_mature) AS mature_problem_rate,
    SUM(loan_amount) FILTER (WHERE is_mature) AS mature_loan_amount,
    SUM(loan_amount) FILTER (WHERE is_mature AND is_problem) AS mature_problem_amount
FROM mart.loan_risk_features
GROUP BY region_name;
