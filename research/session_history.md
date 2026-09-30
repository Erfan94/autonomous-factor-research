# Session history — one line per state change (date | step | digest)

2026-09-30 | bootstrap_awaiting_api_key | skeleton from V3 by allow-list; four construction changes in harness+config; 429 tests; no snapshot yet
2026-09-30 | bootstrap_awaiting_snapshot | bootstrap verified; D11 (Stage 1 bar raw, Stage 2 guard hedged) in config+harness; 434 tests; key file in place, probe OK; no snapshot yet
- 2026-09-30 bootstrap_awaiting_snapshot -> snapshot recorded: 13 tables, DATA_SHA 198b281de1a0, verify + live OK; two bootstrap event types registered.
2026-09-30 | bootstrap_v0_baseline_stage2 | snapshot DATA_SHA 198b281de1a0 live OK; v0 --baseline --stage 2 (run 001) launched
2026-09-30 | bootstrap_v0_stage3_running | run 001 evaluated (v0 IC 0.0145, t 2.62, hedged Sharpe 0.600); five baseline rows; two records.py defects logged
