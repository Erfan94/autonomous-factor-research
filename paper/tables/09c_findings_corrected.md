*Table 09c_findings_corrected. Every finding_corrected (append-only corrections). Source: events `finding_corrected` (text truncated at 200 characters).*

| events line | date | subject / id | correction (record text) |
|---|---|---|---|
| 7 | 2026-09-30 | bootstrap_stamps | the stamps of the first commit |
| 30 | 2026-09-30 | v0_early_leg_coverage | a data property of Sharadar's early ART, not a harness defect; affects 3 of 276 signal months. Every ART-flow or 12m-lag candidate inherits it |
| 81 | 2026-09-30 | events_line77_missing_ts | append-only log; this row carries the timestamp |
| 98 | 2026-09-30 | AnnouncementReturn_batch02_review_minors | {"a_carry": "_CARRY_MONTHS 6->7 (ages 0-6, matches OSAP), _EVENT_MONTHS 7->8", "b_history_months": "7->1 (window needs ~4 SEP rows; OSAP has no listing-age gate), lookback_months 7->8", "c_dedupe": "1 … |
| 99 | 2026-09-30 | BPEBM | alpha_review MAJOR: EV floor M+T>=0.05M inverted rationale (M+T<0 = net debt > mcap) and dropped net debt >= 0.95M, the leverage tail; rank scoring makes magnitude moot -> ev.where(ev>0); *usd docstri … |
| 100 | 2026-09-30 | BMdec | alpha_review MAJOR: BE was latest ART quarter vs ME Dec Y-1 (up to 17m mismatch); OSAP pairs FY Y-1 BE; data_layer.py:628-635 convention -> ARY, reportperiod calendar year = Dec ME year, datekey<=sign … |
| 165 | 2026-09-30 | batch04: ChInv, ChAssetTurnover, ChEQ, ChInvIA | ["ChInv docstring null-vs-0 rule aligned to code (zero-fill then both-zero->NaN)", "ChInv spurious one-date-null share measured: 0.00% at 1999-12/2008-12/2020-12 (0/1488, 0/1162, 0/1124 scored); Shara … |
| 420 | 2026-09-30 | events_ts_estimated | rows are not edited (append-only); the true time bound of each of those rows is the author time of the commit that first carries it (git log research/events.jsonl); row order is correct |
| 421 | 2026-09-30 | events_ts_estimated_row | the estimated-ts range in the previous row starts at row 219 (DelCOL preflight_passed), not row 230 |
| 757 | 2026-10-01 | research/registry/BidAskSpread.yaml caveat 2 (run 003) | conclusion stands, reason wrong: raw LS is annualised arithmetically (analytics.py:706); the inexactness is the D3 within-sector rank-reversal offset 1/n_s plus qcut ties. Row not edited. |
| 988 | 2026-10-01 | batch_declared stage2_l3 note: IdioVol3F/MaxRet annual-IC corr | IdioVol3F/MaxRet Stage 1 annual-IC corr is 0.94 (20/23 same sign), not 0.97 (0.97 is IdioVolAHT/MaxRet); NetEquityFinance/XFIN 0.948, ShareIss5Y 0.913 |
| 1083 | 2026-10-01 | run_049_character_lines | ratio 0.106 (decile) / 0.113 (layer) but buffered 0.145, layer_no_buffer 0.070: gross return concave in turnover, buffer raises return per turnover; spread and borrow scale with leverage, impact (\|dw\| … |
| 1130 | 2026-10-02 | paper_headline_brief | only the declared `layer` row is negative at every AUM in 049 and 057; nine in-window rows are net positive (4 fixed-tier, 5 $100M measured-spread sensitivities, max 0.058), none out of sample (paper … |
| 1131 | 2026-10-02 | record_internal_inconsistencies | run_completed runtimes sum to 6.17 h for Phase B; 20 alpha_review events before Phase A closed; run 051 block 0.034550 / -3.064867 (rounding); the paper uses the event fields |
