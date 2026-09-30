-- Sharadar table schema: actions (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/actions?format=postgres

CREATE TABLE IF NOT EXISTS actions (
  date date NOT NULL,
  action text NOT NULL,
  ticker text NOT NULL,
  name text NOT NULL,
  value double precision,
  contraticker text NOT NULL,
  contraname text NOT NULL,
  PRIMARY KEY (date, action, ticker, name, contraticker, contraname)
);

CREATE INDEX IF NOT EXISTS actions_action_idx ON public.actions USING btree (action);

CREATE INDEX IF NOT EXISTS actions_contraticker_idx ON public.actions USING btree (contraticker);

CREATE INDEX IF NOT EXISTS actions_ticker_idx ON public.actions USING btree (ticker);
