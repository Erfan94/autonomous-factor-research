-- Sharadar table schema: holdings_ticker (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/holdings_ticker?format=postgres

CREATE TABLE IF NOT EXISTS holdings_ticker (
  date text NOT NULL,
  ticker text NOT NULL,
  name text,
  shrholders bigint,
  cllholders bigint,
  putholders bigint,
  wntholders bigint,
  dbtholders bigint,
  prfholders bigint,
  fndholders bigint,
  undholders bigint,
  shrunits double precision,
  cllunits double precision,
  putunits double precision,
  wntunits double precision,
  dbtunits double precision,
  prfunits double precision,
  fndunits double precision,
  undunits double precision,
  shrvalue double precision,
  cllvalue double precision,
  putvalue double precision,
  wntvalue double precision,
  dbtvalue double precision,
  prfvalue double precision,
  fndvalue double precision,
  undvalue double precision,
  totalvalue double precision,
  percentoftotal double precision,
  PRIMARY KEY (date, ticker)
);

CREATE INDEX IF NOT EXISTS holdings_ticker_ticker_idx ON public.holdings_ticker USING btree (ticker);
