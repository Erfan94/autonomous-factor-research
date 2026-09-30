-- Sharadar table schema: metrics (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/metrics?format=postgres

CREATE TABLE IF NOT EXISTS metrics (
  ticker text NOT NULL,
  date date NOT NULL,
  lastupdated date,
  beta1y double precision,
  beta5y double precision,
  dividendyieldforward double precision,
  dividendyieldtrailing double precision,
  high52w double precision,
  high5y double precision,
  low52w double precision,
  low5y double precision,
  ma200d double precision,
  ma200w double precision,
  ma50d double precision,
  ma50w double precision,
  price double precision,
  return1y double precision,
  return5y double precision,
  returnytd double precision,
  volume bigint,
  volumeavg1m bigint,
  volumeavg3m bigint,
  PRIMARY KEY (ticker, date)
);

CREATE INDEX IF NOT EXISTS metrics_date_idx ON public.metrics USING btree (date);

CREATE INDEX IF NOT EXISTS metrics_lastupdated_idx ON public.metrics USING btree (lastupdated);
