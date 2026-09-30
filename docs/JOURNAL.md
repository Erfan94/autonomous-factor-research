# Journal — dated step log

Append one entry per step: what ran, what was decided, what it cost. Numbers
and ids, not essays; the reasoning lives in DECISIONS.md and events.jsonl.

## 2026-09-30 — bootstrap (session: Fable 5.1, run from the predecessor's directory)
- Owner's instruction: a fresh project from V3's skeleton, the four construction changes (D3–D6), decisions 1999–2021, holdout 2022-01..2026-09 spent after September closes, a fresh Sharadar pull, local git only.
- Copied 762 tracked files by allow-list (no specs, translations, records, results, manifest blocks or paper); leakage grep logged in D1; 109 field verifications reset to `probed_on_prior_snapshot`; composite reduced to v0; layer config pin and regime years reset.
- Harness: within-group ranking (`rank_one_factor(group_col)`), `universe_market_return`, `trailing_beta` / `hedge_long_short`, `regime_diagnostics`, `_cut_stats` and the cut fields under `--include-holdout`, the β/regime rows on every Stage 2 rung, hedged Stage 3 variants, the layer's family scores on the same ranks, `include_holdout` set under `--holdout-only` (the predecessor's HD-HOLDOUT-FLAG), `stamp_block.py` reading the manifest's real holdout state.
- Config schema 5: `ranking`, `market_hedge`, `diagnostics`; dates moved.
- Tests: 429 passing (`pytest tests/`), including `tests/test_v4_construction.py` (within-sector ranks and the thin-group fallback; β at t uses only months < t; the hedged series has ~zero ex-post β; the regime rule is date-free; the report's hedge, regime and cut sections; the baseline emits `cut_holdout_*` under `--include-holdout`; every block carries β).
- Snapshot: pending the API key file (the owner copies it into the project root; the bootstrap session may not read the predecessor's).

## 2026-09-30 — verification of the bootstrap and D11 (session: Fable 5.1, run from the predecessor's directory)
- Owner asked for a verification of the bootstrap against their instruction. Verified: allow-list transfer (762 files, no outcomes), windows 1999-01..2021-12 / 2022-01..2026-09, D3–D6 in code with tests, local git only, siblings denied, 429 tests. Not done: the snapshot pull (the key file arrived after the last commit; `snapshot.py probe` now reports key OK and all 13 tables entitled).
- Found a self-contradiction: D4 hedged the Stage 1 spread bar and the Stage 2 guard; D6 and LESSONS 28 listed a hedged guard as not adopted. Owner chose the hybrid (Stage 1 raw, Stage 2 guard hedged) and declined any decile-monotonicity diagnostic. Written as D11; config schema 6; five new tests.
- Cost: one harness + config move with no run behind it; the stamps are in CHANGELOG.

## 2026-09-30 — snapshot recorded (session: Opus 5.5 runner, Fable 5.1 advisor)
- `snapshot.py download`: 13 tables in ~16 min (SEP 991 MB zip, 45.4m rows; SF1 3.2m; DAILY 39.8m; SF3 81.2m). FUNDS mapped, not held.
- `verify` OK: config vocabularies match the bytes string-for-string (NYSE/NASDAQ/NYSEMKT; two Domestic Common categories; all 10 delisting actions; ART); TICKERS.table carries legacy codes SEP/SF1, both accepted by TICKERS_SCOPE; marketcap median $712m; SEP starts 1997-12-31, exactly the first momentum window.
- `manifest`: DATA_SHA nodata -> 198b281de1a0. `live`: 14 tables checked, column-complete, full history.
- `records.py check` DRIFTed on two unregistered bootstrap event types; registered them (scripts/, not harness). Check OK.

## 2026-09-30 — v0 baseline (runs 001, 002) and records.py fixes
- Run 001 `--baseline --stage 2`: 137 s wall (panel build 61 s, then cached). v0 IC 0.0145, NW t 2.62, halves 0.0275/0.0016; hedged LS Sharpe 0.60, 7.32%/yr, MaxDD −45.6%, β −0.14 fw; raw Sharpe 0.72; ex-top-3-years (2000, 2001, 2003) Sharpe 0.16.
- Run 002 `--baseline --stage 3`: 60 s. icir_weighted 0.64 hedged (raw 0.44, β −0.45: the hedge adds market exposure to a net-short book); buffered halves turnover for −0.045 Sharpe; vol_targeted 0.31.
- Cost: both runs far under the ORCHESTRATION estimates (25 min baseline) on a cached panel; Phase B planning should re-time the first 12-factor batch rather than assume an hour.
- factor-evaluator: provenance verified on both; five baseline registry rows; v0 manifest block. It found two scripts/records.py defects (baseline stage-2 run opened the phase gate; leg row Investment.yaml masked OSAP's Investment predictor). Fixed; UNACCOUNTED 207. The OSAP Investment candidate will be named InvestmentTWX.
- Measured two open items: 21 in-universe performance delistings is sound (unknown reasons default to performance); thin early Profitability/Investment coverage is Sharadar ART lacking TTM flows for calendardate 1998Q1–Q3, confined to signals 1998-12..1999-02 (finding_corrected supersedes the manifest's unmeasured explanation).

## 2026-09-30 — Phase A inventory (fetch batches 01-26)
- 212 OSAP predictors specced at ref b4e911e6 in 26 fetch batches of eight (osap-fetcher, pairs of four), field-checked where unverified (eps, opinc/oibdp, revtq/cshprq), translated (sharadar-translator), preflighted serially in one process, and audited by alpha-reviewer in 17 review passes.
- Outcome: 106 candidate files preflight-passed; 101 frontier rows (64 data_unavailable, 28 preflight_failed, 9 data_start); 5 baseline rows. UNACCOUNTED 0.
- Rulings taken on the way (decision events): debt gate on SF1.debt users (and its exemption where OSAP zero-fills dltt/dlc: dNoa); current-SIC signal values under D3/HX-2; full windows for return and volume windows; capex sign ruling; EP/NetPayoutYield flows lagged to the t-6 price; OrgCap fiscal-year handling; history gates on every price-window factor; tie rule applied literally.
- Records defects found and corrected append-only: event timestamps estimated rather than read from the clock (rows 219-419; finding_corrected); stale field_map ib/ibq entries remapped; one commit swept in in-flight specs.
- Cost: every preflight 1-3 minutes on the cached panel; the reviews found one critical (PriceDelayRsq history gate) and ~20 major issues, all fixed before any screen.
