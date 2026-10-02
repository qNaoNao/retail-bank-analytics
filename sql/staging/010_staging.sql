-- Grain: one typed row per source record. Raw source values remain available in raw.*.
CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.account AS
SELECT
    CAST(account_id AS BIGINT) AS account_id,
    CAST(district_id AS INTEGER) AS district_id,
    frequency AS statement_frequency_code,
    CASE frequency
        WHEN 'POPLATEK MESICNE' THEN 'monthly'
        WHEN 'POPLATEK TYDNE' THEN 'weekly'
        WHEN 'POPLATEK PO OBRATU' THEN 'after_transaction'
        ELSE 'unknown'
    END AS statement_frequency,
    strptime('19' || lpad(date, 6, '0'), '%Y%m%d')::DATE AS opened_date
FROM raw.account;

CREATE OR REPLACE TABLE staging.client AS
WITH parsed AS (
    SELECT
        CAST(client_id AS BIGINT) AS client_id,
        lpad(birth_number, 6, '0') AS birth_number,
        CAST(substr(lpad(birth_number, 6, '0'), 1, 2) AS INTEGER) AS birth_year_2d,
        CAST(substr(lpad(birth_number, 6, '0'), 3, 2) AS INTEGER) AS encoded_month,
        CAST(substr(lpad(birth_number, 6, '0'), 5, 2) AS INTEGER) AS birth_day,
        CAST(district_id AS INTEGER) AS district_id
    FROM raw.client
)
SELECT
    client_id,
    birth_number,
    make_date(
        1900 + birth_year_2d,
        CASE WHEN encoded_month > 50 THEN encoded_month - 50 ELSE encoded_month END,
        birth_day
    ) AS birth_date,
    CASE WHEN encoded_month > 50 THEN 'female' ELSE 'male' END AS gender,
    district_id
FROM parsed;

CREATE OR REPLACE TABLE staging.district AS
SELECT
    CAST(A1 AS INTEGER) AS district_id,
    A2 AS district_name,
    A3 AS region_name,
    CAST(A4 AS INTEGER) AS population,
    CAST(A5 AS INTEGER) AS municipalities_lt_500,
    CAST(A6 AS INTEGER) AS municipalities_500_1999,
    CAST(A7 AS INTEGER) AS municipalities_2000_9999,
    CAST(A8 AS INTEGER) AS municipalities_ge_10000,
    CAST(A9 AS INTEGER) AS city_count,
    CAST(A10 AS DOUBLE) AS urban_ratio_pct,
    CAST(A11 AS DOUBLE) AS average_salary,
    try_cast(nullif(trim(A12), '?') AS DOUBLE) AS unemployment_rate_1995,
    try_cast(nullif(trim(A13), '?') AS DOUBLE) AS unemployment_rate_1996,
    CAST(A14 AS DOUBLE) AS entrepreneurs_per_1000,
    try_cast(nullif(trim(A15), '?') AS INTEGER) AS crimes_1995,
    try_cast(nullif(trim(A16), '?') AS INTEGER) AS crimes_1996
FROM raw.district;

CREATE OR REPLACE TABLE staging.disposition AS
SELECT
    CAST(disp_id AS BIGINT) AS disp_id,
    CAST(client_id AS BIGINT) AS client_id,
    CAST(account_id AS BIGINT) AS account_id,
    type AS relationship_type_code,
    CASE type WHEN 'OWNER' THEN 'owner' WHEN 'DISPONENT' THEN 'authorized_user' END
        AS relationship_type
FROM raw.disposition;

CREATE OR REPLACE TABLE staging.card AS
SELECT
    CAST(card_id AS BIGINT) AS card_id,
    CAST(disp_id AS BIGINT) AS disp_id,
    type AS card_type,
    strptime('19' || substr(issued, 1, 6), '%Y%m%d')::DATE AS issued_date
FROM raw.card;

CREATE OR REPLACE TABLE staging.loan AS
SELECT
    CAST(loan_id AS BIGINT) AS loan_id,
    CAST(account_id AS BIGINT) AS account_id,
    strptime('19' || lpad(date, 6, '0'), '%Y%m%d')::DATE AS loan_date,
    CAST(amount AS DECIMAL(18, 2)) AS loan_amount,
    CAST(duration AS INTEGER) AS duration_months,
    CAST(payments AS DECIMAL(18, 2)) AS monthly_payment,
    status AS loan_status_code,
    CASE status
        WHEN 'A' THEN 'repaid'
        WHEN 'B' THEN 'defaulted'
        WHEN 'C' THEN 'running_ok'
        WHEN 'D' THEN 'running_delinquent'
    END AS loan_status,
    status IN ('A', 'B') AS is_mature,
    status IN ('B', 'D') AS is_problem
FROM raw.loan;

CREATE OR REPLACE TABLE staging.orders AS
SELECT
    CAST(order_id AS BIGINT) AS order_id,
    CAST(account_id AS BIGINT) AS account_id,
    nullif(trim(bank_to), '') AS destination_bank,
    nullif(trim(account_to), '') AS destination_account,
    CAST(amount AS DECIMAL(18, 2)) AS order_amount,
    nullif(trim(k_symbol), '') AS purpose_code,
    CASE nullif(trim(k_symbol), '')
        WHEN 'POJISTNE' THEN 'insurance'
        WHEN 'SIPO' THEN 'household'
        WHEN 'LEASING' THEN 'leasing'
        WHEN 'UVER' THEN 'loan_payment'
        ELSE 'unspecified'
    END AS purpose
FROM raw.orders;

CREATE OR REPLACE TABLE staging.transactions AS
SELECT
    CAST(trans_id AS BIGINT) AS transaction_id,
    CAST(account_id AS BIGINT) AS account_id,
    strptime('19' || lpad(date, 6, '0'), '%Y%m%d')::DATE AS transaction_date,
    type AS transaction_type_code,
    CASE WHEN type = 'PRIJEM' THEN 'inflow' ELSE 'outflow' END AS direction,
    nullif(trim(operation), '') AS operation_code,
    CASE nullif(trim(operation), '')
        WHEN 'VYBER KARTOU' THEN 'card_withdrawal'
        WHEN 'VKLAD' THEN 'cash_deposit'
        WHEN 'PREVOD Z UCTU' THEN 'bank_transfer_in'
        WHEN 'VYBER' THEN 'cash_withdrawal'
        WHEN 'PREVOD NA UCET' THEN 'bank_transfer_out'
        ELSE 'bank_generated_or_unspecified'
    END AS operation,
    CAST(amount AS DECIMAL(18, 2)) AS amount,
    CASE WHEN type = 'PRIJEM' THEN CAST(amount AS DECIMAL(18, 2))
        ELSE -CAST(amount AS DECIMAL(18, 2)) END AS signed_amount,
    CAST(balance AS DECIMAL(18, 2)) AS balance_after_transaction,
    nullif(trim(k_symbol), '') AS purpose_code,
    CASE nullif(trim(k_symbol), '')
        WHEN 'POJISTNE' THEN 'insurance'
        WHEN 'SLUZBY' THEN 'statement_fee'
        WHEN 'UROK' THEN 'interest_credit'
        WHEN 'SANKC. UROK' THEN 'penalty_interest'
        WHEN 'SIPO' THEN 'household'
        WHEN 'DUCHOD' THEN 'pension'
        WHEN 'UVER' THEN 'loan_payment'
        ELSE 'unspecified'
    END AS purpose,
    nullif(trim(bank), '') AS counterparty_bank,
    nullif(trim(account), '') AS counterparty_account
FROM raw.transactions;
