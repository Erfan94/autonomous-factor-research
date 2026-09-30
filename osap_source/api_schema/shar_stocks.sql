-- Sharadar table schema: stocks (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/stocks?format=postgres

CREATE TABLE IF NOT EXISTS stocks (
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

CREATE INDEX IF NOT EXISTS stocks_date_idx ON public.stocks USING btree (date);

CREATE INDEX IF NOT EXISTS stocks_lastupdated_idx ON public.stocks USING btree (lastupdated);
