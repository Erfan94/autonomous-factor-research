*Table 09b_process_findings. Every process_finding. Source: events `process_finding` (text truncated at 200 characters; ids with the other project's name have that word masked as `other-project`; text that refers to another project is omitted and pointed to by line).*

| events line | date | subject / id | note or action (record text) |
|---|---|---|---|
| 2 | 2026-09-30 | field_map_verification_reset | a verification from another snapshot is a mapping, not a proof (LESSONS 25) |
| 14 | 2026-09-30 | unregistered_event_types | added both to KNOWN_EVENTS and RECORDS.md; scripts/ is outside HARNESS_SHA; check OK |
| 23 | 2026-09-30 | phase_gate_baseline_stage2 | latent: once candidate files exist before Stage 1 rows (Phase A/B) check will DRIFT falsely; gate should skip baseline runs. scripts/ outside HARNESS_SHA; not fixed here |
| 24 | 2026-09-30 | frontier_masks_osap_Investment | osap_frontier counts rows by filename; should use osap_acronym for status baseline. Phase A would skip Investment; its candidate file would also collide with the leg row name |
| 48 | 2026-09-30 | missing_item_rule_applied | rule applied as written: infeasible unless OSAP zero-fills; no per-predictor substitution (ppnenet for ppegt) adopted |
| 62 | 2026-09-30 | book_equity_preferred_terms | adopted here: a missing preferred term that only adjusts book equity -> approx (equity (+taxliabilities), preferred not removed), consistent with the v0 Value leg; a signal that IS preferred stock sta … |
| 63 | 2026-09-30 | AnnouncementReturn_date_source | option B: code-22 8-K dates only, no datekey fallback (a filing-date return is a different event); 67 of 276 months null, all in the first half |
| 64 | 2026-09-30 | field_map_dc_gloss | zero-fill applies either way; gloss correction owed to the field-checker at batch 02 |
| 80 | 2026-09-30 | BPEBM_orientation_fixed_before_preflight | set ascending=False before any preflight or screen; no number existed |
| 115 | 2026-09-30 | sf1_netincdis_sign_inverted | known_trap added to field_map.yaml; CF ib = netinc + netincdis |
| 132 | 2026-09-30 | ChAssetTurnover_route | route A (terms dropped, as the logged missing-item rule prescribes); route B (identity reconstruction) not adopted: would null ~20% (financials/REITs) and carry txp inside lco |
| 184 | 2026-09-30 | tie_rule_change_in_level_signals | standing rule: for a change-in-level signal, names whose level is exactly 0 (or null, where OSAP zero-fills) at BOTH ends are NaN - the zero change is structural, not information; one-end-zero kept. A … |
| 193 | 2026-09-30 | CoskewACX_truncated_early_windows | nulled: a window opening before the market series is truncated, not OSAP construct; first signal 1999-12 (11 of 276 months) |
| 235 | 2026-09-30 | debt_gate_unapplied | gate added to all five (debtc notna at every date read); inputs list SF1.debtc; re-preflight |
| 240 | 2026-09-30 | dolvol_history_gate | history_months=2 (price at the month t-2 end), docstring updated |
| 269 | 2026-09-30 | fieldmap_ib_stale | ib entry remapped to netinc + netincdis, status approx; index rebuilt |
| 352 | 2026-10-01 | scratchpad_glob_other-project_names | fetcher prompts name their own scratchpad subfolder explicitly; no content reached any record |
| 448 | 2026-09-30 | asc842_tie_rule_reach | declared in NetDebtFinance; factor-evaluator to read 2019-21 decile bins and within-sector mass for debt-flow candidates at Stage 1 |
| 469 | 2026-09-30 | commit_swept_inflight_specs | commits stage named spec paths only while fetchers run |
| 627 | 2026-09-30 | fieldmap_ibq_stale | ibq remapped to netinc + netincdis (approx); index rebuilt; no translated file read ibq as netinccmn |
| 693 | 2026-09-30 | docs/CONSTRUCTION.md f_bidaskspreadflip | construction layer names f_bidaskspreadflip as its spread source before any V4 screen; BidAskSpread flip qualified in run 003 (\|t\| 2.77). Pre-registration/D7 review owed; not edited |
| 700 | 2026-09-30 | records_index_raw_ret | fixed in scripts/records.py (outside HARNESS_SHA); RECORDS.md notes ls_top_years_share_pct is undefined when the summed LS is near zero or negative |
| 833 | 2026-10-01 | shareiss5y_stale_docstring | docstring corrected; no number affected (comment only) |
| 881 | 2026-10-01 | records_phase_gate_acronym_keys | scripts/records.py passes row file names to phase_gate (outside HARNESS_SHA); no harness or record change |
| 900 | 2026-10-01 | tag_v1_mispointed | tag not moved or deleted (CLAUDE.md: tags are never moved); manifest v1 git_tag annotated; owner decides whether to delete and recreate it on 0d52a33. Fix: tag only after `git rev-parse HEAD` shows th … |
| 1020 | 2026-10-01 | v12_apply_permission_denied | not retried by another route; the coordinator does not perform a subagent-denied action; awaiting the owner |
| 1056 | 2026-10-01 | leak_sweep_phase_d_close | none required |
| 1064 | 2026-10-01 | construction_md_other-project_caveat | [text omitted: refers to another project; events.jsonl line 1064] |
| 1070 | 2026-10-01 | d7_other-project_outcome_clause | CONSTRUCTION.md sentence replaced by the design reason; D7 annotated with a dated governing note (decision text not rewritten); docs are unstamped, no SHA moves |
| 1087 | 2026-10-01 | d8_other-project_restatement_figure | dated governing note added under D8; decision text not rewritten |
| 1129 | 2026-10-02 | stage3_holdout_cuts_absent | not re-run: the block is spent once (D8); the gap is disclosed in the manifest and the paper |
