-- Sharadar table schema: funds (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/funds?format=postgres

CREATE TABLE IF NOT EXISTS funds (
  ticker text NOT NULL,
  date date NOT NULL,
  open double precision,
  high double precision,
  low double precision,
  close double precision,
  volume double precision,
  closeadj double precision,
  closeunadj double precision,
  lastupdated date,
  PRIMARY KEY (ticker, date)
);

CREATE INDEX IF NOT EXISTS funds_date_idx ON public.funds USING btree (date);

CREATE INDEX IF NOT EXISTS funds_lastupdated_idx ON public.funds USING btree (lastupdated);
