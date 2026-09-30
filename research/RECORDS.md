# Records — formats, and why each file is small

An earlier search's registry reached 321 KB, its event log 327 KB and its
session state 38 KB, and the loop re-read them every batch. This project keeps
what the loop READS small and derived, and what it KEEPS complete but out of
the way.

| file | read by | size rule |
|---|---|---|
| `session_state.yaml` | every session start | the CURRENT state only; ≤ 40 lines; one-line digests of past states go to `session_history.md` |
| `registry_index.yaml` | loop step 2, evaluator | derived (`scripts/records.py index`); one line per factor |
| `registry/<Name>.yaml` | on demand | the full row; ≤ 60 lines; prose fields one paragraph each |
| `events.jsonl` | evaluator (tail), audits | append-only; numbers and ids; a `note` ≤ 200 chars |
| `results/NNN_*_summary.md` | evaluator first | written by the harness; a few KB per member |
| `results/NNN_*.txt` | on demand | the full report + blocks; immutable once committed |
| `stage1_diagnostics.yaml` | evaluator, every Phase B batch | diagnostics owed per factor (never bars); written at the Phase A close, appended only when a later finding adds one |
| `CHANGELOG.md` | humans | one entry per iteration, decision first, ≤ 8 lines |
| `MODEL_MANIFEST.yaml` | every reply (Block 1) | one block per composite version, ≤ 60 lines each |

## Registry row (`research/registry/<Name>.yaml`)

```yaml
name: ExampleFactor
osap_acronym: ExampleFactor
status: accepted | rejected | inconclusive | infeasible | preflight_failed | dropped | stage2_pending | baseline
family: null                 # Phase C: the family the passer joined; null until assigned, never changed after
batch: BATCH-01
declaration_order: 3
date_tested: "2026-09-22"
run: "003"                      # Stage 1 run seq; stage2_run below for the ladder
stage2_run: "004"
stage1_decision: PASS | FAIL        # the stamped Stage 1 verdict; records.py phase_gate reads it (a PASS row needs a family before Stage 2)
decided_by: "resid_ic_tstat_nw"   # the bar that decided, or "all bars" for an acceptance
source: "Novy-Marx 2013 (JFE); SignalDoc sign +1"
orientation: "high gross profit / assets = attractive"
provenance: {harness_sha: ..., config_sha: ..., composite_sha: ..., data_sha: ..., spec: osap_source/cache/b4e911e6/ExampleFactor/spec.md}
dimension_override: null
history_gate_months: null
preflight: {masspoint_max_pct: 0.3, qcut_min_bins: 10, coverage_min_pct: 71.2}
stage1:   # from the block, verbatim
  ic_mean: ..., ic_tstat_nw: ..., ic_half1_mean: ..., ic_half2_mean: ..., ls_sharpe: ...,
  ls_ann_return_pct: ..., ls_raw_ann_return_pct: ..., ls_maxdd_pct: ..., turnover_d10_pct: ..., coverage_pct: ..., avg_names_per_decile: ...,
  n_months: ..., ls_n_months: ..., ic_decay_h1: ..., ic_decay_h6: ..., tier_MEGA_ic_mean: ..., tier_SMALL_ic_mean: ...
  ls_raw_sharpe: ..., ls_beta_mean: ..., ls_beta_fullwindow: ..., ls_sharpe_ex_top_years: ..., ls_top_years: "...",
  ls_sharpe_bear: ..., ls_sharpe_bull: ...      # D5 diagnostics, verbatim from the block; never bars
stage1_failed: [bar, ...]        # empty when passed
stage2:   # from the rung's block, verbatim; absent when no rung ran
  base_legs: "Size,Value,Profitability,Investment,Momentum"
  resid_ic_mean: ..., resid_ic_tstat_nw: ..., solo_ic_mean: ..., resid_ic_share: ...,  # share = resid / solo_ic_mean (HD-001, HD-002); cand_* = WITH arm
  spanning_alpha_ann_pct: ..., spanning_alpha_tstat_nw: ...,
  spanning_r2: ..., corr_to_composite: ..., paired_delta_ic_mean: ..., paired_delta_ic_tstat: ..., delta_ls_sharpe: ...,
  maxdd_worsening_pct: ..., paired_delta_ls_mean: ..., paired_delta_ls_tstat: ...
  base_ls_beta_fullwindow: ..., cand_ls_beta_fullwindow: ..., cand_ls_raw_sharpe: ..., cand_ls_sharpe_ex_top_years: ...
stage2_failed: [bar, ...]
character: >   # ONE paragraph: where the return comes from (deciles, halves, tiers, decay, delisting share)
caveats: [one clause each]
decision: >    # ONE paragraph: the verdict and the bar; how it reads against v0, the live composite and prior rows
```

## Events (`research/events.jsonl`)

One JSON object per line, `ts` (ISO 8601 UTC) and `event`, plus the fields
below. Never edit or delete a line; correct with `finding_corrected`.

| event | fields |
|---|---|
| `project_initialized` | `detail` |
| `snapshot_recorded` | `data_sha`, `tables`, `recorded_on`, `reason` |
| `factor_suggested` | `factor`, `osap_acronym`, `batch`, `rationale` (≤ 120 chars) |
| `factor_fetched` | `factor`, `spec_path`, `data_available` (bool); `cached: true` when the spec pre-existed |
| `factor_infeasible` / `factor_dropped` / `factor_deferred` | `factor`, `reason` |
| `factor_translated` | `factor`, `factor_def_path`, `inputs`; `cached: true` when the file pre-existed |
| `fields_verified` | `factor`, `fields` |
| `batch_declared` | `batch`, `members` (= Stage 2 order), `harness_sha`, `composite_sha`, `data_sha` |
| `batch_amended` | `batch`, `members_final`, `replaced` |
| `preflight_failed` | `factor`, `batch`, `failures` |
| `run_started` | `seq`, `label`, `stage`, `factors`, the four stamps. A `--baseline` run carries `factors: "baseline"` and a label containing `baseline`, so `records.py` phase_gate does not read it as the ratchet starting |
| `run_completed` | `seq`, `result_path`, `n_blocks`, `runtime_seconds` |
| `run_failed` | `seq`, `factors`, `failure_class` |
| `provenance_verified` / `provenance_mismatch` | `seq`, the stamps (and `kind`, `expected_sha`, `got_sha`) |
| `validation_warning` | `factor`, `stage`, `warnings` |
| `factor_evaluated` | `factor`, `stage`, `decision`, `decided_by`, `stats` (the bar values only) |
| `batch_closed` | `batch`, `tally` (`{pass: n, fail: n, inconclusive: n}`), `composite_after` |
| `registry_rows_written` | `batch`, `stage`, `rows`, `counters` |
| `spec_written` | `factor`, `spec_path`, `availability` (feasible / infeasible / approx) — Phase A |
| `inventory_classified` | `n_predictors`, `n_feasible`, `n_infeasible`, `n_translated`, `n_preflight_failed`, `by_reason` — closes Phase A |
| `family_assigned` | `factor`, `family`, `cat_economic`, `new_family` (bool), `n_families_after` — Phase C, before any Stage 2 number |
| `stage2_order_declared` | `order` (every Stage 1 passer, descending Stage 1 NW t), `rule`, `n` — closes Phase C |
| `phase_completed` | `phase` (A/B/C/D/E), `digest` |
| `composite_updated` | `model_version`, `factors_included`, `composite_sha`, `git_tag` |
| `construction_reported` | `model_version`, `seq`, `best_variant`, `sharpe` |
| `config_changed` / `harness_changed` | `old_sha`, `new_sha`, `reason`, `tests_passed` |
| `harness_defect_found` | `defect_id`, `severity`, `location`, `fix_landed` |
| `finding_confirmed` / `finding_corrected` / `process_finding` | `subject`, `evidence` / `supersedes`, `note` |
| `open_question_updated` | `id`, `status`, `tally` (numbers, not an essay) |
| `decision_reversed` | `factor`, `from_decision`, `to_decision`, `reason`, `commit` |
| `repository_initialized` / `repository_committed` / `repository_pushed` | `remote` (`none` while local-only, D9), `branch`, `commit`, `tags` |
| `alpha_review` | `target`, `findings` (count by severity), `critical` (list) |
| `flip_hypothesis_qualified` | `factor`, `flipped_name`, `seq`, `osap_sign`, `stats_osap_sign`, `stats_flipped`, `bar` (\|t\| ≥ 2.74), `caveat` |
| `frontier_classified` | `n_open_before`, `n_excluded`, `n_testable`, `by_reason` (counts; each excluded name is a row in `osap_source/osap_frontier.yaml`) |
| `preflight_passed` | `factor`, `batch`, the probe coverage/mode shares (optional; a pass is also implied by `factor_translated` with no `preflight_failed`) |
| `preflight_remeasured` | `harness_sha`, `n_factors`, `hard_failures`, `rows` (factor → probe → cover/mode/distinct/qcut), `note` — a whole-pool dry run after a harness change; supersedes earlier probe readings |
| `error` | `factor`, `step`, `message` |
| `verification_completed` | `subject`, `detail` — an owner-requested audit of a step against its instruction |
| `rule_conflict_found` | `subject`, `stop_and_ask` (6), `detail`, `resolved_by`, `decision` — a rule contradicting itself, and how the owner resolved it |
| `decision` | `id`, `decision` — a judgment call the rules leave to the runner (a translation choice, a tie-break between two readings of a spec), taken without a stop-and-ask |

`python3 scripts/records.py check` refuses an unknown event type.

## Session state (`research/session_state.yaml`)

```yaml
updated: "2026-09-25T10:00:00Z"
step: phase_B_batch01_stage1_running  # one token: what is happening now
phase: phase_B_screen                 # bootstrap | phase_A_inventory | phase_B_screen | phase_C_families | phase_D_ratchet | phase_E_construct | final_validation | paper
composite: {version: v0, legs: 5, families: 5, sha: ..., legs_list: [...]}
batch: {id: BATCH-01, members: [...], order_fixed: true, stage1_run: "003", passers: [], stage2_run: null}
versions: {v0: "<composite_sha> v0-baseline"}
stamps: {harness_sha: ..., config_sha: ..., composite_sha: ..., data_sha: ...}
counters: {inventoried: 0, infeasible: 0, translated: 0, preflight_failed: 0, screened: 0, passed: 0, families: 5, ratcheted: 0, accepted: 0, rejected: 0, inconclusive: 0}
open: [one line per open question or owed item, e.g. "tag v1-add-<name> owed"]
next: "one sentence: what Claude does next"
```

When the state changes, replace the file and append one line
(`date | step | digest`) to `research/session_history.md`.

## Manifest block (`MODEL_MANIFEST.yaml`)

legs (each with its `family`), `families` (the family table string), `construction_rule`, stamps,
`ratchet` (the two bars of the accepting rung plus the paired dIC diagnostic and the rung's
β / ex-regime rows), `baseline` (the version's own `--baseline --stage 2` block: IC, NW t,
hedged Sharpe, ann ret, vol, MaxDD, hit, turnover, coverage, tiers — all GROSS — plus
`ls_raw_sharpe`, `ls_beta_mean`, `ls_beta_fullwindow`, `ls_sharpe_ex_top_years`,
`ls_top_years`, `ls_sharpe_bear`, `ls_sharpe_bull`), `construction` (the Stage 3 table: per
variant hedged Sharpe, LS t, ann ret, vol, MaxDD, worst 12m, turnover, raw Sharpe, β),
three lines of `character`. Never edit a past block.

The manifest's top-level `holdout` block is `{status: unspent}` until the one spend, then
`{status: spent, spent_on: YYYY-MM-DD, data_sha: ..., runs: [...]}`; `stamp_block.py` reads it.


## Families (`research/families.yaml`)

`families:` maps each family to `{definition, members}` (seeds first, passers
appended in assignment order); `assignments:` is the ordered log of every
Phase C decision: `{factor, family, cat_economic, assigned, event_ts}`. A
family is assigned once, after the factor's Stage 1 row exists and before
any Stage 2 number, and is copied into the candidate file's `FactorDef`
(`family="..."`). The composite's family table is what
`factors/composite.py` `families()` returns and what every baseline block
records as `composite_families`.

## Stage 2 order (`research/stage2_order.yaml`)

Written once when Phase C closes: every Stage 1 passer in descending Stage 1
Newey-West IC t, with the t values, the rule name from config
(`search.stage2_order`) and the timestamp. Ladders are cut from this list in
order, five rungs at a time, and the list is never re-sorted on a Stage 2
result.
