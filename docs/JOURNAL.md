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
