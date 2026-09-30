-- Sharadar table schema: sp500 (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/sp500?format=postgres

CREATE TABLE IF NOT EXISTS sp500 (
  date date NOT NULL,
  action text NOT NULL,
  ticker text NOT NULL,
  name text,
  contraticker text,
  contraname text,
  note text,
  PRIMARY KEY (date, action, ticker)
);

CREATE INDEX IF NOT EXISTS sp500_action_idx ON public.sp500 USING btree (action);

CREATE INDEX IF NOT EXISTS sp500_contraticker_idx ON public.sp500 USING btree (contraticker);

CREATE INDEX IF NOT EXISTS sp500_ticker_idx ON public.sp500 USING btree (ticker);
