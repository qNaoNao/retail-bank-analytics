-- Grain: one row per account and observed transaction month.
CREATE OR REPLACE TABLE mart.account_month AS
WITH ranked AS (
    SELECT
        t.*,
        date_trunc('month', transaction_date)::DATE AS month_start,
        row_number() OVER (
            PARTITION BY account_id, date_trunc('month', transaction_date)
            ORDER BY transaction_date DESC, transaction_id DESC
        ) AS month_end_rank
    FROM mart.fct_transaction t
)
SELECT
    r.account_id,
    r.month_start,
    date_diff('month', date_trunc('month', a.opened_date), r.month_start) AS months_since_open,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (WHERE operation_code IS NOT NULL) AS customer_transaction_count,
    COUNT(DISTINCT transaction_date) FILTER (WHERE operation_code IS NOT NULL)
        AS customer_active_days,
    SUM(amount) FILTER (WHERE direction = 'inflow') AS inflow_amount,
    SUM(amount) FILTER (WHERE direction = 'outflow') AS outflow_amount,
    SUM(signed_amount) AS net_cash_flow,
    AVG(balance_after_transaction) AS average_transaction_balance,
    MAX(balance_after_transaction) FILTER (WHERE month_end_rank = 1) AS month_end_balance,
    MIN(balance_after_transaction) AS minimum_balance,
    COUNT(*) FILTER (WHERE operation = 'card_withdrawal') AS card_transaction_count,
    SUM(amount) FILTER (WHERE operation = 'cash_withdrawal') AS cash_withdrawal_amount,
    SUM(amount) FILTER (WHERE operation = 'bank_transfer_out') AS transfer_out_amount,
    SUM(amount) FILTER (WHERE purpose = 'loan_payment') AS loan_payment_amount
FROM ranked r
JOIN mart.dim_account a USING (account_id)
GROUP BY r.account_id, r.month_start, a.opened_date;

CREATE OR REPLACE TABLE mart.monthly_portfolio AS
SELECT
    month_start,
    COUNT(*) AS transacting_accounts,
    COUNT(*) FILTER (WHERE customer_transaction_count > 0) AS active_accounts,
    SUM(transaction_count) AS transaction_count,
    SUM(inflow_amount) AS inflow_amount,
    SUM(outflow_amount) AS outflow_amount,
    SUM(net_cash_flow) AS net_cash_flow,
    AVG(month_end_balance) AS average_month_end_balance,
    MEDIAN(month_end_balance) AS median_month_end_balance,
    SUM(card_transaction_count) AS card_transaction_count
FROM mart.account_month
GROUP BY month_start;
