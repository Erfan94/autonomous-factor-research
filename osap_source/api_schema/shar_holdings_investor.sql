-- Sharadar table schema: holdings_investor (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/holdings_investor?format=postgres

CREATE TABLE IF NOT EXISTS holdings_investor (
  date text,
  investorid text,
  investorname text,
  shrholdings bigint,
  cllholdings bigint,
  putholdings bigint,
  wntholdings bigint,
  dbtholdings bigint,
  prfholdings bigint,
  fndholdings bigint,
  undholdings bigint,
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
  percentoftotal double precision
);

CREATE UNIQUE INDEX IF NOT EXISTS holdings_investor_date_investorid_idx ON public.holdings_investor USING btree (date, investorid);

CREATE INDEX IF NOT EXISTS holdings_investor_investorid_idx ON public.holdings_investor USING btree (investorid);
