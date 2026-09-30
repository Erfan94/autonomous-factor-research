# Paper — what the loop must leave behind for the write-up

The end product of this search is a paper describing an automated,
pre-registered factor search on Sharadar data with a market-neutral,
sector-relative construction. Nothing in this directory is written until the
search is declared finished (stop-and-ask 5). Until then, the loop leaves the
paper its evidence:

- `config/test_config.yaml` at the commit that measured v0 — the pre-registration, including the four construction changes.
- `research/registry/*.yaml` — every candidate, every bar, every verdict, rejections included, with β and the ex-regime Sharpe on every row.
- `research/results/` — the run reports the numbers came from, stamped.
- `MODEL_MANIFEST.yaml` — every composite version with its Stage 3 table and its hedge summary.
- `osap_source/osap_frontier.yaml` — every OSAP predictor NOT tested, with the reason.
- `research/families.yaml` and `research/stage2_order.yaml` — the family assignments and the pre-declared ratchet order, with timestamps that precede every Stage 2 number.
- `docs/DECISIONS.md` — every design decision with its date, rationale and evidence; the leakage audit; D2's statement of what the holdout can and cannot test.
- `docs/JOURNAL.md` — the dated step log of how the search actually ran (for the orchestration section).
- `research/events.jsonl` — the ordered decision log, for the "how the search ran" section.
- The out-of-sample block 2022-01..2026-09, spent once under D8 and read from the `cut_holdout_*` fields.
