-- Core dimensional model. Money facts remain at source-event grain.
CREATE SCHEMA IF NOT EXISTS mart;

CREATE OR REPLACE TABLE mart.dim_district AS SELECT * FROM staging.district;
CREATE OR REPLACE TABLE mart.dim_account AS SELECT * FROM staging.account;
CREATE OR REPLACE TABLE mart.dim_client AS SELECT * FROM staging.client;

CREATE OR REPLACE TABLE mart.bridge_account_client AS
SELECT disp_id, account_id, client_id, relationship_type, relationship_type_code
FROM staging.disposition;

CREATE OR REPLACE TABLE mart.dim_date AS
SELECT
    day::DATE AS date_day,
    date_trunc('month', day)::DATE AS month_start,
    year(day) AS calendar_year,
    quarter(day) AS calendar_quarter,
    month(day) AS calendar_month,
    monthname(day) AS month_name,
    dayofweek(day) AS day_of_week,
    dayname(day) AS day_name
FROM range(DATE '1993-01-01', DATE '1999-01-01', INTERVAL 1 DAY) dates(day);

CREATE OR REPLACE TABLE mart.fct_transaction AS
SELECT * FROM staging.transactions;

CREATE OR REPLACE TABLE mart.fct_loan AS
SELECT * FROM staging.loan;

CREATE OR REPLACE TABLE mart.fct_card AS
SELECT
    c.card_id,
    d.account_id,
    d.client_id,
    d.relationship_type,
    c.disp_id,
    c.card_type,
    c.issued_date
FROM staging.card c
JOIN staging.disposition d USING (disp_id);

CREATE OR REPLACE TABLE mart.fct_order AS
SELECT * FROM staging.orders;
