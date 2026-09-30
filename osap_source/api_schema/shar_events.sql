-- Sharadar table schema: events (PostgreSQL)
-- As of 2026-08-18
-- https://api.sharadar.com/v1.0/schema/events?format=postgres

CREATE TABLE IF NOT EXISTS events (
  ticker text NOT NULL,
  date date NOT NULL,
  eventcodes text,
  PRIMARY KEY (date, ticker)
);

CREATE INDEX IF NOT EXISTS events_ticker_idx ON public.events USING btree (ticker);
