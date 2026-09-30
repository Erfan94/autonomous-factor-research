-- Sharadar table schema: daily (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/daily?format=postgres

CREATE TABLE IF NOT EXISTS daily (
  ticker text NOT NULL,
  date date NOT NULL,
  lastupdated date,
  ev double precision,
  evebit double precision,
  evebitda double precision,
  marketcap double precision,
  pb double precision,
  pe double precision,
  ps double precision,
  PRIMARY KEY (ticker, date)
);

CREATE INDEX IF NOT EXISTS daily_date_idx ON public.daily USING btree (date);

CREATE INDEX IF NOT EXISTS daily_lastupdated_idx ON public.daily USING btree (lastupdated);
