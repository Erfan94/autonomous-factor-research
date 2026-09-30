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
