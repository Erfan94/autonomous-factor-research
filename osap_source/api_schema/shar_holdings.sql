-- Sharadar table schema: holdings (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/holdings?format=postgres

CREATE TABLE IF NOT EXISTS holdings (
  ticker text NOT NULL,
  investorid text NOT NULL,
  securitytype text NOT NULL,
  date date NOT NULL,
  value double precision,
  units double precision,
  PRIMARY KEY (ticker, investorid, securitytype, date)
);

CREATE INDEX IF NOT EXISTS holdings_date_idx ON public.holdings USING btree (date);

CREATE INDEX IF NOT EXISTS holdings_investorid_idx ON public.holdings USING btree (investorid);

CREATE INDEX IF NOT EXISTS holdings_securitytype_idx ON public.holdings USING btree (securitytype);
