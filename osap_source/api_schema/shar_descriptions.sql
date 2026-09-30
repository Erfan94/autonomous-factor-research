-- Sharadar table schema: descriptions (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/descriptions?format=postgres

CREATE TABLE IF NOT EXISTS descriptions (
  "table" text NOT NULL,
  indicator text NOT NULL,
  isfilter text,
  isprimarykey text,
  title text,
  description text,
  unittype text,
  PRIMARY KEY ("table", indicator)
);

CREATE INDEX IF NOT EXISTS descriptions_indicator_idx ON public.descriptions USING btree (indicator);
