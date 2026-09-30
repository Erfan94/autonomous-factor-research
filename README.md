# Alpha Model Auto Research V4

An automated, pre-registered search for a multi-factor equity alpha model on
Sharadar data, run by an agentic research loop. Every predictor in Open
Source Asset Pricing (Chen & Zimmermann) is inventoried and translated to a
frozen Sharadar snapshot, screened alone, grouped into fewer than ten
economic families, and admitted to its family when it carries information
the model does not already have. Every run is stamped with the hashes of
the harness, the config, the composite and the data snapshot, so every
number in the records is reproducible from the repo plus the frozen
snapshot.

What this project changes against its predecessor (docs/DECISIONS.md D3–D6):
ranks are formed within sector before the family blend; the long-short is
hedged to the market by construction with an ex-ante trailing beta; every
block and every ratchet rung prints the long-short's beta and a date-free
ex-regime Sharpe as diagnostics; the selection rules, the family blend and
the broad universe are unchanged.

- Baseline v0: Size, Value, Profitability, Investment, Momentum, one family each.
- Universe: US common stock, price ≥ $1, NYSE-20th-percentile size and 20th-percentile ADV entry cuts with a 15th-percentile exit band, month by month.
- Decisions on 1999-01 .. 2021-12; 2022-01 .. 2026-09 held out for one final validation (docs/DECISIONS.md D2, D8).
- Selection on information only: Stage 1 standalone screen; Stage 2 residual IC t > 2 with a hedged-return guard; composite = family blend of within-sector ranks. No transaction cost anywhere.

Layout: `harness/` (data layer, analytics, runner, portfolio construction),
`factors/` (composite + candidates + accepted), `config/`, `research/`
(records and results), `osap_source/` (pinned OSAP source and field maps),
`docs/` (decisions, methodology, orchestration, journal), `paper/`, `tests/`.

Start here: `CLAUDE.md` (the loop and the rules), `docs/DECISIONS.md` (why),
`research/LESSONS.md` (the evidence behind the rules), `research/RECORDS.md`
(record formats).

Setup: `pip install -r requirements.txt`; put the Sharadar API key in the
gitignored key file at the project root (`data/README.md`, first-time
setup); then `python3 harness/snapshot.py probe`, `download`, `verify`,
`manifest`, `live`.

The repository is local until the owner publishes it (D9).
