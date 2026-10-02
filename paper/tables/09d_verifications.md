*Table 09d_verifications. Every verification_completed. Source: events `verification_completed` (text truncated at 200 characters).*

| events line | date | subject | detail (record text) |
|---|---|---|---|
| 8 | 2026-09-30 | bootstrap | snapshot not pulled (key file placed after the last commit; snapshot.py probe: key OK, 13 tables entitled) [1 clause(s) omitted: refer to another project; events.jsonl line 8] |
| 573 | 2026-09-30 | stray post-BME rows in the monthly panel | scratch count over SEP (37.6M rows) and DAILY (33.1M rows) 1997-12..2021-12: 0 rows dated after their calendar month's business month-end; build_monthly_panel's tail(1) therefore always takes a row on … |
| 704 | 2026-10-01 | hedge_gap_check_before_phase_d | independent rebuild of AM, BMdec, BookLeverage, CBOperProf hedged LS matches run 003 blocks to ~1e-15; beta_t on t-36..t-1 only (look-ahead and stale windows do not match); market proxy = cap-weighted … |
| 877 | 2026-10-01 | stage2_new_family_blend | drive_stage2 builds trial = cur_meta + [candidate meta]; family_members/blend_family_ranks derive families from the trial metas; tests/test_composite.py::test_a_candidate_opening_a_new_family_gets_a_f … |
| 1057 | 2026-10-01 | phase_d_close_checks | 15 tags v0..v14; v2..v14 each on its 'ratchet: vN' commit; v1 mis-pointed (open, owner); families.yaml accepted members == composite.families() on all 9 families (19 legs); every passer's registry fam … |
| 1085 | 2026-10-01 | weekend_print_after_signal_asof | cached monthly panel fb86ececd100, me 1998-12..2021-12: 1,711,671 ID-months, 0 with last SEP date > me; the alpha_review minor does not bite in-window; no logged row affected |
