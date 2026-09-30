-- Sharadar table schema: insiders (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/insiders?format=postgres

CREATE TABLE IF NOT EXISTS insiders (
  ticker text NOT NULL,
  date date NOT NULL,
  formtype text NOT NULL,
  ownername text NOT NULL,
  officertitle text,
  isdirector text,
  isofficer text,
  istenpercentowner text,
  transactiondate date,
  securityadcode text,
  transactioncode text,
  sharesownedbeforetransaction bigint,
  transactionshares bigint,
  sharesownedfollowingtransaction bigint,
  transactionpricepershare double precision,
  transactionvalue bigint,
  securitytitle text,
  directorindirect text,
  natureofownership text,
  dateexercisable date,
  priceexercisable double precision,
  expirationdate date,
  rownum bigint NOT NULL,
  PRIMARY KEY (ticker, date, formtype, ownername, rownum)
);

CREATE INDEX IF NOT EXISTS insiders_date_idx ON public.insiders USING btree (date);

CREATE INDEX IF NOT EXISTS insiders_ownername_idx ON public.insiders USING btree (ownername);

CREATE INDEX IF NOT EXISTS insiders_securityadcode_idx ON public.insiders USING btree (securityadcode);

CREATE INDEX IF NOT EXISTS insiders_transactionvalue_idx ON public.insiders USING btree (transactionvalue);
