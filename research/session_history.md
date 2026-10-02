# Session history — one line per state change (date | step | digest)

2026-09-30 | bootstrap_awaiting_api_key | skeleton from V3 by allow-list; four construction changes in harness+config; 429 tests; no snapshot yet
2026-09-30 | bootstrap_awaiting_snapshot | bootstrap verified; D11 (Stage 1 bar raw, Stage 2 guard hedged) in config+harness; 434 tests; key file in place, probe OK; no snapshot yet
- 2026-09-30 bootstrap_awaiting_snapshot -> snapshot recorded: 13 tables, DATA_SHA 198b281de1a0, verify + live OK; two bootstrap event types registered.
2026-09-30 | bootstrap_v0_baseline_stage2 | snapshot DATA_SHA 198b281de1a0 live OK; v0 --baseline --stage 2 (run 001) launched
2026-09-30 | bootstrap_v0_stage3_running | run 001 evaluated (v0 IC 0.0145, t 2.62, hedged Sharpe 0.600); five baseline rows; two records.py defects logged

## 2026-09-30 21:40 — Phase A through fetch batch 10
- Batches 07-10 classified; review fixes applied to batches 05-09 (CoskewACX market-calendar lag, debtc gate on 5 debt readers, EP earnings lagged to t-6).
- field_map: SF1.eps, opinc, oibdp verified; compustat.ib remapped to netinc + netincdis.
- Commits dbbad83 .. cd5bc3d. UNACCOUNTED 128 of 212.
2026-10-01 | phase_D_closed | ladders 1-5 (runs 012/023/032/037/044): 24 tested, 14 accepted (v1-v14), 10 rejected; v14 19 legs 9 families; baselines+Stage 3 runs 013-043; tag v1 mis-pointed open
2026-10-01 | phase_E_layer | D7 layer changes (41edba9, 5d57746), alpha-review fixes, reproductions 045/047/048, run 049 layer: gross Sharpe 0.86, net -0.06 @100M measured CS, +0.50 fixed-tier; whole-model audit clean; stop-and-ask 3 put to owner
2026-10-02 | holdout_spent | owner yes to stop-and-ask 5; runs 054-057 on DATA 42587e08609a: IC 0.030 (t 1.87) vs 0.028 expected; hedged Sharpe 0.52 vs 1.00; raw 0.12; excess 0.41; layer net -0.37 @100M; Stage 3 holdout cuts absent (process_finding)
2026-10-02 | finished | paper generated from records, reviewed and revised; phase_completed E; awaiting owner on publication and the v1 tag
