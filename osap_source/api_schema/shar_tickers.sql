-- Sharadar table schema: tickers (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/tickers?format=postgres

CREATE TABLE IF NOT EXISTS tickers (
  "table" text NOT NULL,
  permaticker bigint NOT NULL,
  ticker text NOT NULL,
  name text,
  exchange text,
  isdelisted text,
  category text,
  cusips text,
  siccode bigint,
  sicsector text,
  sicindustry text,
  figi text,
  famaindustry text,
  sector text,
  industry text,
  scalemarketcap text,
  scalerevenue text,
  relatedtickers text,
  currency text,
  location text,
  lastupdated date,
  firstadded date,
  firstpricedate date,
  lastpricedate date,
  firstquarter text,
  lastquarter text,
  secfilings text,
  companysite text,
  PRIMARY KEY ("table", permaticker, ticker)
);

CREATE INDEX IF NOT EXISTS tickers_lastupdated_idx ON public.tickers USING btree (lastupdated);

CREATE INDEX IF NOT EXISTS tickers_permaticker_idx ON public.tickers USING btree (permaticker);

CREATE INDEX IF NOT EXISTS tickers_table_idx ON public.tickers USING btree ("table");

CREATE INDEX IF NOT EXISTS tickers_ticker_idx ON public.tickers USING btree (ticker);
