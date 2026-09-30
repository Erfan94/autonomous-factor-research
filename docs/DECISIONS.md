# Design decisions — dated, with rationale and evidence

Every entry says what was decided, by whom, on what evidence, and what it
rules out. "Principle" means the decision follows from the pre-registration
philosophy; "measured" means it follows from a numbered lesson in
`research/LESSONS.md`, which carries the predecessors' numbers without their
factor names.

## D1 — 2026-09-30 — Fresh project from the predecessor's skeleton, methodology only (owner: Erfan Sadeghi)

Carried from the predecessor (V3), by an explicit allow-list, never by
copy-then-delete: harness code and tests, scripts, the config template, agent
and skill definitions, the git hooks, the Sharadar API contract
(`data/sharadar_llms.txt`, `osap_source/api_schema/`), the OSAP source
cached at the pinned commit (`predictor.py`, `signaldoc_row.csv`, upstream
excerpts, `.sas`/`.do` sources, `SignalDoc.csv`, `tree.txt`), and the
Compustat-to-Sharadar field map as MAPPING knowledge.

Not carried: any registry row, result, manifest block, event, changelog,
session state, frontier verdict, **candidate translation**, project-authored
`spec.md`, Stage 1 diagnostics file, family assignment, Stage 2 order,
design-study output, paper file, or snapshot-specific field verification.
The composite was reduced to v0; the construction-layer config's composite
pin and regime years were reset; a layer test fixture that imported an
accepted leg now builds a synthetic one. The data is downloaded from scratch
(`DATA_SHA` differs from any prior pull by construction).

Leakage audit before the first commit (a grep over the V4 tree for the
predecessor's accepted-factor names, batch labels, run numbers, version tags,
stamps and verdict words): hits remain only in OSAP's own cache files (where
those strings are predictor acronyms), in `osap_source/field_map.yaml`
notes that name predictors as *users* of a field (mapping knowledge; every
one of its 109 `verified_on` dates was moved to `probed_on_prior_snapshot`),
in `harness/data_layer.py` comments that record measurements made on the
predecessor's DATA_SHA (kept as documented harness-design evidence), in the
format placeholders of `research/RECORDS.md`, in this project's own
`harness_changed` / `config_changed` events (which cite the predecessor's
stamps as the `old_sha` they replaced), in one test fixture label, and in
`.claude/agents/osap-fetcher.md`, where an acronym is an example of a
predictor emitted by a differently named upstream script. `research/LESSONS.md`
carries the predecessors' numbers and names no factor.
`.claude/settings.json` denies reading or shelling into every sibling project.

Cost accepted: Phase A re-fetches every spec and re-translates every
constructible predictor with subagents, as the predecessor did.

## D2 — 2026-09-30 — Windows: decisions 1999-01..2021-12, holdout 2022-01..2026-09, and what that holdout can and cannot test (owner: Erfan)

Decisions use 276 months; the reserved block is 57 months, spent once on the
finished composite after September 2026 closes (D8). The block is a clean
test of **factor selection**: every candidate is screened fresh on this
snapshot and no 2022+ month enters any decision.

It is **not an unbiased test of the construction change** (D3–D5). Those
changes were motivated by a post-holdout study of the predecessor that read
2023–2026 (and 2022 was inside the predecessor's decision window). The owner
chose this overlap knowingly, excluding the alternative of waiting for data
after 2026-08. The paper states it in the limitations: the holdout can
confirm or refute the selected composite; whether the hedge and the sector
ranking would have been chosen without seeing those years it cannot say.

## D3 — 2026-09-30 — Ranks are formed within sector before the family blend (owner: Erfan; measured: LESSONS 29)

Every signal is percentile-ranked within its sector-month (the universe
frame's `sector`, TICKERS.sector), after winsorising on the whole
cross-section; the family blend averages those ranks. A sector-month with
fewer than 10 scored names falls back to the cross-section rank for its
names; a missing sector label is its own group. The rule applies wherever a
rank is formed: Stage 1, the residual-IC projection and the composite in
Stage 2, the baseline, Stage 3 and the layer's family scores
(`config ranking`, `harness/analytics.rank_one_factor`).

Known limitation, declared: TICKERS.sector is the vendor's CURRENT
classification, so a reclassified firm carries today's sector in 1999.
The predecessor accepted the same look-ahead for industry-adjusted
predictors and its construction layer; here it touches every leg. The
paper says so.

## D4 — 2026-09-30 — The long-short is hedged to the market by construction (owner: Erfan; measured: LESSONS 27, 29)

Headline LS_t = (D10−D1)_t − β_t × M_t, where M is the universe's own
cap-weighted holding-month return (never an index, so no series the
snapshot does not hold) and β_t is the OLS slope of the raw LS on M over
months t−36..t−1 only. Fewer than 12 prior months → β = 0 (unhedged), never
a two-month estimate. The hedged series is the headline of every block: the
standalone screens, the Stage 2 arms, the baseline, the Stage 3 variants.
Which BARS read it is D11: the Stage 2 return guard does; the Stage 1
positive-spread bar reads the raw D10−D1. (As first written on 2026-09-30
this entry hedged both bars; D11 records the owner's correction, made
before any run existed.) The raw series, the ex-ante β and the full-window β of the raw LS
are printed and recorded beside every hedged number, so the choice is
auditable on every block. Gross: no cost is charged on the hedge or
anywhere else. Parameters in `config market_hedge`.

Why portfolio-level rather than stock-level neutralisation: it is the
construction the predecessor's study measured (LESSONS 29); stock-level
betas would add a second estimated quantity to every name-month.

## D5 — 2026-09-30 — β and a date-free ex-regime Sharpe on every block and every rung; never bars (owner: Erfan; measured: LESSONS 27–29)

Every block carries `ls_beta_fullwindow`, `ls_beta_mean` (ex ante),
`ls_raw_sharpe`, `ls_sharpe_ex_top_years`, `ls_top_years`,
`ls_sharpe_bear`, `ls_sharpe_bull`; every Stage 2 rung prints them
WITHOUT/WITH. "Ex-regime" in this project means **Sharpe after removing the
k = 3 calendar years with the highest long-short return** (config
`diagnostics.ex_regime_top_years`), and the market state is the sign of the
trailing 12-month market return ending at t−1. Both rules name no date, so
no year learned on the predecessor's window is written into the rule that
reads this one. `records.py index` carries β and the ex-regime Sharpe per
row. The evaluator reads them and says what they did; nothing rejects on them.

## D6 — 2026-09-30 — Everything else stays as pre-registered by the predecessor (owner: Erfan; measured: LESSONS 28)

Stage 1 bars and levels; Stage 2 = residual IC t > 2.0 (strict) + the
return guard at −2.0; the family blend (1/F across, equal within,
two-level, renormalised); fewer than ten families assigned after Stage 1;
Stage 2 order descending Stage 1 t, ladders of five; the broad relative
universe with the 20/15 membership band; batches of 12 in alphabetical
order; the flip rule at |t| ≥ 2.74. Tighter t bars, stability-in-thirds
screens and family caps all sat within noise of the as-run rules in the
predecessor's six-fold walk-forward, and a large-cap universe was worse, so
no pre-registration is spent on them. A hedged Stage 2 guard also sat within
noise there; it is adopted anyway (D11), for consistency with the hedged
construction rather than for any measured gain, and the Stage 1 spread bar
stays raw.

## D7 — 2026-09-30 — What Phase E must change in the construction layer, declared now (owner: loop)

The layer's design (`docs/CONSTRUCTION.md`, `config/construction_layer.yaml`)
is carried as a template. Before its first number, Phase E must:
1. add a market-beta neutrality constraint (or a market factor with a
   zero-exposure target) — the predecessor's layer was sector- and
   dollar-neutral but not beta-neutral, which is where its loss sat;
2. take the half-spread from a harness-built series, not from a composite
   leg's column (the layer refused to run without a specific leg);
3. set `report.regime_cuts.ex_years` from the D5 rule on the finished
   composite's in-window LS, and pin `composite.composite_sha`.
Each moves LAYER_SHA, which is outside CONFIG_SHA; each is logged.

## D8 — 2026-09-30 — The holdout spend protocol, declared before any out-of-sample number (owner: loop)

The block ends 2026-09-30, after the search's snapshot was pulled, so the
spend requires a refreshed snapshot (stop-and-ask 3). The order, as one
spend, on the finished composite and the frozen layer:
1. Owner says September has closed → `snapshot.py download`, `verify`,
   `manifest`, `live` → a new DATA_SHA. Nothing else moves.
2. `run_test.py --baseline --stage 2` on the new snapshot, in-window only.
   Its block must reproduce the live version's manifest block; every
   difference is logged (vendor restatements; the earlier search measured
   ~0.03% on composite statistics). A difference that flips a Stage 2
   verdict is stop-and-ask 6.
3. Stop-and-ask 5, then `--baseline --stage 2 --include-holdout`: the
   canonical read is the `cut_holdout_*` fields (the hedge β estimated
   continuously across 2021-12/2022-01). `--holdout-only` is the cross-check;
   its first 12 months run at β = 0 and it says so.
4. `--baseline --stage 3 --include-holdout` and
   `--baseline --construction-layer --include-holdout`, read from their
   holdout cuts.
No bar. Two expectations are written before the spend: the live version's
in-window hedged Sharpe, and its in-window ex-top-3-years Sharpe. The paper
reads the holdout against both. After the spend: no composite change, no
re-baseline, no further Stage 2 on this snapshot, no layer retuning.

## D9 — 2026-09-30 — Version control is local only until the owner publishes (owner: Erfan)

A local git repository with hooks and no remote. Commits at every logical
step keep the provenance chain (stamp lines, tags, commit ids in events);
nothing is pushed. When the search is done the owner provides the GitHub
link and chooses the files.

## D10 — 2026-09-30 — Runner and advisor (owner: Erfan)

The runner is the session model (Claude Fable 5.1 at bootstrap); the advisor
is Claude Fable through the advisor tool, consulted at every phase boundary,
before every acceptance and whenever a result looks too good. Subagents as
in `docs/ORCHESTRATION.md`. The bootstrap session ran with knowledge of the
predecessor's outcomes; nothing it wrote into V4 names a predictor's
verdict, and the family list it left is the five seeds only.

## D11 — 2026-09-30 — Which bars the hedge reaches: the Stage 2 guard, not the Stage 1 spread (owner: Erfan; principle)

As bootstrapped, D4 hedged every long-short a bar reads, while D6 and
LESSONS 28 listed "a hedged Stage 2 guard" among the tuning ideas not
adopted: a rule contradicting itself (stop-and-ask 6), surfaced by the
owner's verification of the bootstrap on 2026-09-30, before the snapshot
was pulled and before any run existed. The owner's instructions had pulled
in two directions: item 1 (hedge market beta) and item 4 (keep the
selection process). The owner's decision, given in chat:

* **Stage 1**: the positive-spread bar reads the **raw** D10−D1 annual
  return (`ls_raw_ann_return_pct`; config
  `stage1_standalone.ls_spread_series: raw`). A standalone signal is judged
  on its own spread, exactly as the predecessor judged it, so the Stage 1
  screen is unchanged in every bar and every level.
* **Stage 2**: the return guard reads the **hedged** family blend (paired
  Δ of the hedged LS, NW t ≥ −2.0). A leg is judged on what it does to the
  strategy that will be held, which is the hedged one. LESSONS 28 measured
  this guard as within noise of the raw one; it is adopted for consistency
  with the construction, not for gain.
* Everything reported stays hedged with the raw series and β beside it; the
  spanning diagnostic hedges the candidate's solo LS the same way (like
  with like); Stage 3 and the layer are unchanged.

Implementation: one switch in the Stage 1 threshold block, read by the
shared `stage1_checks`, so the runner and the evaluator cannot drift; the
bar row is named after the series it read; `ls_raw_ann_return_pct` is a
required Stage 1 block key. The switch defaults to `raw` in code so an
absent key can never reinstate the rejected rule. Config schema 5 → 6.
HARNESS_SHA and CONFIG_SHA move with no run behind them; the change was
written from the predecessor's session under the owner's authorisation
(this file sits in V4's `ask` tier). D4 and D6 are amended in place with a
pointer here; the original wording is in the first commit.

Not decided, and not to be revisited: a decile-monotonicity statistic. The
owner declined to add one, even as a diagnostic; the decile table is read,
as before, and IC plus the positive spread remain the only monotonicity
proxies.
