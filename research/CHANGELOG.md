# CHANGELOG — one entry per iteration, decision first, ≤ 8 lines

## 2026-09-30 — bootstrap
- Project created from the predecessor's (V3) skeleton by allow-list; no factor outcome, registry row, result, spec, translation or verdict carried over (docs/DECISIONS.md D1, leakage audit there).
- Construction changed, selection rules unchanged: ranks within sector (D3); the long-short hedged to the universe's cap-weighted return with an ex-ante 36-month beta (D4); β and a date-free ex-regime Sharpe on every block and rung, never bars (D5); everything else as pre-registered by the predecessor (D6).
- Windows: decisions 1999-01..2021-12; holdout 2022-01..2026-09, spent once under the refresh protocol D8; D2 states what it can and cannot test.
- Version control local only (D9). Snapshot: pending the owner's key file.

## 2026-09-30 — D11: the Stage 1 spread bar reads the raw D10−D1; the Stage 2 guard reads the hedged blend
- Owner's decision after verifying the bootstrap (stop-and-ask 6: D4 hedged both bars, D6/LESSONS 28 listed a hedged guard as not adopted). Confirmed in chat; no run existed.
- Config schema 5 → 6: `stage1_standalone.ls_spread_series: raw`; `stage1_checks` names the bar row after the series it read; `ls_raw_ann_return_pct` required on every Stage 1 block; index carries `raw_ret`.
- No decile-monotonicity statistic, by the owner's instruction. D4, D6, LESSONS 28, CLAUDE.md, METHODOLOGY, the evaluator agent and RECORDS amended.
- HARNESS_SHA e2e0b18a0115 → 73a95d352942; CONFIG_SHA 1cef53e19e16 → 0d88328d5b10. Snapshot still pending (key file now in place; probe OK, 13 tables).

## 2026-09-30 — v0 measured and constructed (runs 001, 002); manifest block written, tag v0-baseline owed
- v0 = Size, Value, Profitability, Investment, Momentum, one seed family each; stamps 73a95d352942 / 0d88328d5b10 / f9d9d9d95731 / 198b281de1a0; provenance verified on both runs, no validation warnings.
- Run 001: mean IC 0.0145, NW t 2.62, halves 0.0275 / 0.0016; hedged LS Sharpe 0.600, 7.32%/yr, MaxDD -45.6% (raw Sharpe 0.719, beta -0.14); turnover 28.0% D10.
- Caveats: 79% of summed LS return in 2000/2001/2003 (ex-top-years Sharpe 0.16); Profitability/Investment coverage 56%/48% at 1998-12; the hedge cost 0.12 Sharpe on a negative-beta LS.
- Run 002 (Stage 3, never a gate): icir_weighted 0.643 hedged but raw 0.441 at beta -0.45; tier_neutral 0.639; buffered 0.555 at half the turnover; vol_targeted 0.306.
- Five baseline registry rows; two records.py defects found (phase gate, frontier filename match), being fixed by the coordinator (scripts/, outside HARNESS_SHA).
