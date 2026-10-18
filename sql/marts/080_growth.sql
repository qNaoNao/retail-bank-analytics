-- Observation time comes from the source, never from the machine's current date.
CREATE OR REPLACE VIEW analytics.observation_window AS
SELECT
    MAX(transaction_date) AS as_of_date,
    CASE WHEN MAX(transaction_date) = last_day(MAX(transaction_date))
        THEN date_trunc('month', MAX(transaction_date))::DATE
        ELSE (date_trunc('month', MAX(transaction_date)) - INTERVAL 1 MONTH)::DATE
    END AS last_complete_month
FROM mart.fct_transaction;

-- Dense calendar spine: an absent account-month is inactivity, not a missing row.
-- Grain: one account per complete calendar month after opening.
CREATE OR REPLACE TABLE mart.account_month_lifecycle AS
WITH spine AS (
    SELECT a.account_id, m.month_start::DATE AS month_start
    FROM mart.dim_account a
    CROSS JOIN analytics.observation_window o
    CROSS JOIN LATERAL generate_series(
        date_trunc('month', a.opened_date), o.last_complete_month, INTERVAL 1 MONTH
    ) m(month_start)
), activity AS (
    SELECT s.*, coalesce(a.customer_transaction_count, 0) > 0 AS is_active
    FROM spine s
    LEFT JOIN mart.account_month a USING (account_id, month_start)
), history AS (
    SELECT *,
        coalesce(lag(is_active) OVER w, false) AS was_active,
        coalesce(SUM(is_active::INTEGER) OVER (
            PARTITION BY account_id ORDER BY month_start
            ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
        ), 0) AS prior_active_months
    FROM activity
    WINDOW w AS (PARTITION BY account_id ORDER BY month_start)
)
SELECT *,
    CASE
        WHEN is_active AND prior_active_months = 0 THEN 'new'
        WHEN is_active AND was_active THEN 'retained'
        WHEN is_active THEN 'reactivated'
        WHEN prior_active_months > 0 THEN 'inactive'
        ELSE 'never_active'
    END AS lifecycle_state,
    was_active AND NOT is_active AS became_inactive
FROM history;

CREATE OR REPLACE VIEW analytics.monthly_growth AS
WITH counts AS (
    SELECT month_start,
        COUNT(*) FILTER (WHERE is_active) AS active_accounts,
        COUNT(*) FILTER (WHERE was_active) AS previous_active_accounts,
        COUNT(*) FILTER (WHERE lifecycle_state = 'new') AS new_active_accounts,
        COUNT(*) FILTER (WHERE lifecycle_state = 'retained') AS retained_accounts,
        COUNT(*) FILTER (WHERE lifecycle_state = 'reactivated') AS reactivated_accounts,
        COUNT(*) FILTER (WHERE became_inactive) AS newly_inactive_accounts
    FROM mart.account_month_lifecycle GROUP BY month_start
)
SELECT *, active_accounts - previous_active_accounts AS net_active_change,
    (active_accounts - previous_active_accounts)::DOUBLE
        / NULLIF(previous_active_accounts, 0) AS growth_rate,
    (new_active_accounts + reactivated_accounts)::DOUBLE
        / NULLIF(newly_inactive_accounts, 0) AS quick_ratio
FROM counts;

-- Landmark design: observe [opening, day 180), then measure first card issuance
-- in [day 180, day 360). Lifetime segments and future balances are never features.
-- All accounts remain in the mart; immature outcomes are NULL, not failures.
CREATE OR REPLACE TABLE mart.card_adoption_landmark AS
WITH features AS (
    SELECT a.account_id,
        COUNT(t.transaction_id) AS pre180_transaction_count,
        COUNT(t.transaction_id) FILTER (WHERE t.operation_code IS NOT NULL)
            AS pre180_customer_transactions,
        COUNT(t.transaction_id) FILTER (WHERE t.operation = 'bank_transfer_out')
            AS pre180_transfer_out_count,
        MAX(t.transaction_date) AS feature_last_transaction_date,
        arg_max(t.balance_after_transaction, (t.transaction_date, t.transaction_id))
            AS pre180_last_balance
    FROM mart.dim_account a
    LEFT JOIN mart.fct_transaction t ON a.account_id = t.account_id
        AND t.transaction_date >= a.opened_date
        AND t.transaction_date < a.opened_date + INTERVAL 180 DAY
    GROUP BY a.account_id
), first_cards AS (
    SELECT account_id, MIN(issued_date) AS first_card_date
    FROM mart.fct_card GROUP BY account_id
), windows AS (
    SELECT a.account_id, a.opened_date, d.region_name,
        date_trunc('year', a.opened_date)::DATE AS opening_year,
        (a.opened_date + INTERVAL 180 DAY)::DATE AS landmark_date,
        (a.opened_date + INTERVAL 360 DAY)::DATE AS outcome_end_exclusive,
        o.as_of_date, f.* EXCLUDE (account_id), c.first_card_date,
        c.first_card_date IS NULL
            OR c.first_card_date >= a.opened_date + INTERVAL 180 DAY AS card_free_at_landmark,
        a.opened_date + INTERVAL 360 DAY <= o.as_of_date + INTERVAL 1 DAY
            AS outcome_observable,
        CASE
            WHEN f.pre180_transaction_count = 0 THEN 'No observed transactions'
            WHEN f.pre180_transfer_out_count > 0 THEN 'Transfer used before day 180'
            ELSE 'No outgoing transfer before day 180'
        END AS pre180_segment
    FROM mart.dim_account a
    JOIN mart.dim_district d USING (district_id)
    CROSS JOIN analytics.observation_window o
    JOIN features f USING (account_id)
    LEFT JOIN first_cards c USING (account_id)
)
SELECT *, CASE WHEN outcome_observable THEN
    coalesce(first_card_date >= landmark_date AND first_card_date < outcome_end_exclusive, false)
    ELSE NULL END AS card_adopted_next180d
FROM windows;

CREATE OR REPLACE VIEW analytics.card_adoption_segments AS
SELECT pre180_segment, COUNT(*) AS eligible_accounts,
    COUNT(*) FILTER (WHERE card_adopted_next180d) AS adopted_accounts,
    AVG(card_adopted_next180d::INTEGER) AS adoption_rate
FROM mart.card_adoption_landmark
WHERE card_free_at_landmark AND outcome_observable
GROUP BY pre180_segment;

CREATE OR REPLACE VIEW analytics.card_adoption_by_cohort AS
SELECT opening_year, pre180_segment, COUNT(*) AS eligible_accounts,
    COUNT(*) FILTER (WHERE card_adopted_next180d) AS adopted_accounts,
    AVG(card_adopted_next180d::INTEGER) AS adoption_rate
FROM mart.card_adoption_landmark
WHERE card_free_at_landmark AND outcome_observable
GROUP BY opening_year, pre180_segment;
