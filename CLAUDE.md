# Alpha Model Auto Research V4: a pre-registered family-blend factor search on Sharadar, with a market-neutral, sector-relative construction

Build a multi-factor alpha model by inventorying every predictor in Chen &
Zimmermann's Open Source Asset Pricing (OSAP), translating each to a frozen
Sharadar snapshot, screening each alone, grouping the passers into fewer
than ten economic families, and admitting a signal to its family when it
carries information the model does not already have. A fixed, deterministic
harness; everything a paper needs left behind. Baseline v0: the five
Fama-French characteristics plus momentum, one family each. **Nothing else
is inherited.** The predecessor (V3, a sibling directory) taught the
methodology in `research/LESSONS.md`; its factor outcomes are deliberately
NOT here, and every candidate is judged fresh on this snapshot.

## What is different from the predecessor (docs/DECISIONS.md D3–D6)

Four construction changes, pre-registered in `config/test_config.yaml`
before any candidate was screened. The selection rules are unchanged.

1. **Ranks are formed within sector** (`ranking`): every signal is
   percentile-ranked among its sector peers each month, then the family
   blend averages those ranks. A sector-month with fewer than 10 scored
   names falls back to the cross-section rank.
2. **The long-short is hedged to the market by construction**
   (`market_hedge`): D10−D1 minus β_t × the universe's own cap-weighted
   return, β_t estimated on months t−36..t−1 only (β = 0 before 12 months of
   history). Every LS number a bar reads is the hedged one; the raw series
   and the β are printed and recorded beside it.
3. **Every block and every Stage 2 rung prints the long-short's β (full-window
   and ex-ante), the raw Sharpe, and a date-free ex-regime Sharpe**
   (`diagnostics`: Sharpe after removing the 3 best LS calendar years, plus
   a bull/bear split on the ex-ante trailing-12-month market return). These
   are diagnostics, never bars.
4. **Everything else is kept**: the bars and their levels, the family blend,
   the broad universe, the Stage 2 order and ladders. Tighter bars, stability
   screens, family caps and a large-cap universe were all tried on the
   predecessor's walk-forward and did not help (LESSONS 28–29).

## The end product is a paper, and a profile

The search finishes (stop-and-ask 5) with a composite, a registry of every
candidate ever inventoried with its bars and verdict, a family table with
timestamps, a manifest of every version, and one spend of the out-of-sample
block. `paper/README.md` lists what the write-up reads. `docs/` records how
the project was designed and run (`DECISIONS.md`, `METHODOLOGY.md`,
`ORCHESTRATION.md`, `JOURNAL.md`): the author's research profile is the
orchestration as much as the model. Log rejections and inconclusives with
the same detail as acceptances; the paper's honesty is the rejection table.

## The constraint that shapes everything

Every test runs locally on the same bytes. Four stamps go on every result
block and `factor-evaluator` refuses a result whose stamps do not match the
repo: `HARNESS_SHA` (harness/*.py), `CONFIG_SHA` (config/test_config.yaml),
`COMPOSITE_SHA` (factors/composite.py + accepted files), `DATA_SHA`
(data/SNAPSHOT_MANIFEST.yaml). The snapshot is THIS project's own pull from
the Sharadar API (`harness/snapshot.py download`, full history, 13 tables
held; FUNDS mapped but not held), frozen by manifest. No bytes were copied
from another project.

`run_test.py --source` defaults to `recorded`: measure on the frozen snapshot
after the live API authorises its schema and history at run start.
`python3 harness/snapshot.py live` writes `research/live_check.yaml`;
`records.py check` DRIFTs when that proof is missing, on another DATA_SHA, or
over 14 days old. Adding a table or refreshing the snapshot moves DATA_SHA
(stop-and-ask 3).

## How a factor is judged — pre-registered in `config/test_config.yaml`

Signals are selected on **information**, with significance tests. **No
transaction cost is charged anywhere.** Turnover is reported, never decides.

- **Universe** (relative, month by month, with a membership band): US common
  stock on NYSE / NASDAQ / NYSEMKT; price ≥ $1; a name ENTERS at market cap
  ≥ the NYSE 20th percentile and dollar volume ≥ the 20th percentile of the
  cap-screened names, and a current member LEAVES only below the 15th
  percentiles. The chain starts cold at the first panel month, so a month's
  universe depends on (config, data, month) only. Tiers MEGA/MID/SMALL by
  ADV percentile are diagnostics.
- **Window**: decisions on 1999-01-01 .. 2021-12-31 (276 months). The
  out-of-sample block 2022-01-01 .. 2026-09-30 (57 months) is spent once, at
  the end, on the finished composite, after September 2026 has closed and the
  snapshot has been refreshed under the protocol in `docs/DECISIONS.md` D8
  (`--include-holdout`, read from the `cut_holdout_*` fields; `--holdout-only`
  as the cross-check). D2 states why this block is a clean test of the
  selection but not an unbiased test of the construction change.
- **Stage 1, standalone screen** (unchanged): mean IC ≥ 0.010; Newey-West IC
  t ≥ 2.5; mean IC > 0 in both halves; hedged D10−D1 GROSS annual return > 0;
  coverage ≥ 40%; ≥ 30 names per decile; LS months ≥ floor.
- **Families** (Phase C): every Stage 1 passer is assigned to one of fewer
  than ten families by economic definition (SignalDoc `Cat.Economic` is the
  reference), after its screen and before any Stage 2 number, logged in
  `research/families.yaml` and written into its `FactorDef.family`. Never
  changed afterwards.
- **The composite is a family blend**: equal weight across families, equal
  within, two-level and renormalised (`harness.analytics.blend_family_ranks`)
  over within-sector ranks. A new leg dilutes only its own family.
- **Stage 2, the ratchet (accept/reject)**, both: residual IC after
  projecting the candidate's normal score on every current leg's score, NW t
  **strictly greater than 2.0**; guard: paired Δ of the family blend's hedged
  gross long-short return, NW t ≥ −2.0. The paired composite-ΔIC, spanning
  alpha, R², Sharpe and MaxDD deltas, the β rows and the ex-regime Sharpe are
  diagnostics printed on every rung, never bars (LESSONS 18, 27).
- **Stage 2 order**: descending Stage 1 NW IC t over ALL passers, declared
  once when Phase C closes (`research/stage2_order.yaml`), never re-sorted.
  Ladders of at most five rungs are cut from that list in order; rung i
  faces the base plus every earlier rung that passed.
- **Stage 3, construction** (`--baseline --stage 3`): five declared variants
  on the accepted composite, gross, hedged, by tier. On the manifest. Never a
  gate.
- Orientation is OSAP's published sign. A flipped-sign screen is a second
  hypothesis: |t| ≥ 2.74 at Stage 1 and a caveat in its row.

## Autonomy — this project runs itself

The human supplies the API key, the answers to the stop-and-ask list, and
occasional steering. Everything else is yours. **A turn ends with a run
executed and a decision logged, not with a question.** If you are about to
ask, apply the rule, say which in one sentence, keep going. The runner is
the session model (Claude Fable 5.1 at bootstrap); the advisor is Fable
through the advisor tool: consult it at every phase boundary, before every
acceptance is committed, and whenever a result looks too good
(`docs/ORCHESTRATION.md`).

Invoking `osap-fetcher`, `sharadar-field-checker`, `sharadar-translator`,
`factor-evaluator`, `alpha-reviewer` is part of the loop and overrides any
general instruction to avoid subagents.

### Stop and ask — only these

1. Spending the out-of-sample block (`--include-holdout` / `--holdout-only`, once, ever).
2. Anything that moves CONFIG_SHA (a re-baseline).
3. Anything that moves DATA_SHA (refreshing the snapshot, adding a table) — including the refresh the holdout spend needs (D8).
4. Bumping `osap_source.ref`.
5. Declaring the search finished and running the final validation.
6. A rule contradicting itself, or a result implying already-logged rows are wrong.
7. A tenth family (config `search.families_max`).

Everything else: decide, log the reasoning in `research/events.jsonl`, proceed.

## The loop — five phases, in order, no phase started before the previous closes

0. **First session only**: record the snapshot (`snapshot.py probe|download|
   verify|manifest|live`), then `python3 harness/run_test.py --baseline
   --stage 2` and `--baseline --stage 3`; evaluate; write the v0 manifest
   block; tag `v0-baseline` (locally). v0 is measured before any candidate is screened.
1. **Read** `research/session_state.yaml` (the current state only). Finish
   any unfinished item first.

**Phase A — inventory (every OSAP predictor).** `python3 scripts/records.py
frontier` prints the open names. For each: `osap-fetcher` (the source is
cached for many acronyms; the spec is always written fresh), then
`sharadar-field-checker` for every field not `verified` on THIS snapshot
(every inherited status was reset: `probed_on_prior_snapshot` is a mapping,
not a proof), then `sharadar-translator` into `factors/candidates/<Name>.py`,
then `python3 harness/preflight.py --factors ...`. A predictor needing data
Sharadar does not publish, or failing preflight (mass point, coverage,
data start), gets a row in `osap_source/osap_frontier.yaml` with the
measured reason. Work in fetch batches of eight, in alphabetical acronym
order. Log `spec_written`, `fields_verified`, `factor_translated`,
`preflight_failed`. Phase A closes with `inventory_classified` when
UNACCOUNTED is 0 and every constructible predictor has a preflight-passed
file. `alpha-reviewer` audits every translated batch before it is screened.

**Phase B — Stage 1 screen (every constructible predictor).** Batches of
`search.stage1_batch_size` (12) in alphabetical acronym order:
`python3 harness/run_test.py --factors A,...,L --stage 1`. Log
`batch_declared`, `run_started`, `run_completed`; `factor-evaluator` writes
every row. Phase B closes with `phase_completed` when every constructible
predictor has a Stage 1 row.

**Phase C — families.** For every Stage 1 passer, in Stage 1 order: read
its spec and SignalDoc `Cat.Economic`, assign a family by economic
definition (join a seed family or open a new one; fewer than ten in total),
write it into `research/families.yaml` and the candidate's `FactorDef`
(`family="..."`), log `family_assigned`. Then sort ALL passers by Stage 1
NW t descending into `research/stage2_order.yaml`, log
`stage2_order_declared`. No Stage 2 number exists yet; `records.py check`
DRIFTs on a Stage 2 run that precedes the close of Phases A–C.

**Phase D — Stage 2 ratchet.** Cut ladders of at most five from the declared
order: `--factors A,B,C,D,E --stage 2` (or `--factor A --stage 2` for one).
Rung i faces the base plus every earlier accepted rung. If accepted, the
evaluator moves the file, edits the composite, adds the manifest block, runs
`--baseline --stage 2` then `--baseline --stage 3` for the new version, names
the tag owed. Continue down the list until every passer has a Stage 2 row.
Read the β and ex-regime rows on every rung and say what they did; they
never decide.

**Phase E — construction, final validation, paper.** Stage 3 on the final
composite; the institutional construction layer (risk model, cost model,
optimiser, buffered trading) is designed and reported as a separate,
documented phase on the finished composite, with the three changes D7 owes
it (a market-beta constraint, a spread source that is not a composite leg,
regime cuts from the D5 rule); then stop-and-ask 3 (the snapshot refresh),
stop-and-ask 5 and the holdout under D8; then the paper.

Pre-committed: never move ANY of the four stamps while a completed run is
unevaluated; never move HARNESS_SHA inside a declared ladder; fix a harness
defect before the next decision depends on it (`pytest tests/`, re-run the
affected candidate). Inconclusive (thin sample, decile collapse, coverage
floor) is a verdict distinct from rejected.

## Hard rules

- A factor file reads data only through `MonthContext`; no universe filters,
  dates, rebalance logic, sector ranking, hedging or IC/decile maths in a
  factor. Extend `harness/` instead. `FactorDef.dimension` is the one
  sanctioned per-factor deviation.
- Every return-window factor declares `history_months`.
- A candidate's `family` is None until Phase C and never changes after.
- Never write under `data/` except the cache. Never fetch OSAP from `master`.
- Every bar passing is not evidence a result is sound: read the decile shape,
  the halves, the tiers, the decay, the β, the ex-regime Sharpe and the
  `ret_kind` mix before a verdict.
- Decisions use 1999-01-01 .. 2021-12-31 only. A block whose `eval_end`
  reaches 2022 is a hard stop unless it is the final validation.
- `pytest tests/` after any harness change.
- Never read, copy or cite the sibling projects under `../` (the earlier
  searches, V3 included). Their outcomes are not evidence here.
  `.claude/settings.json` denies them. A spec, a factor docstring or a record
  that cites how a predictor fared elsewhere is a leak: remove it and log
  `process_finding`.
- The API key lives in the gitignored key file at the project root
  (`data/README.md`) and is read only by `harness/snapshot.py` /
  `run_test.py`. Never print it, never cat that file.

## Records (small by design — see `research/RECORDS.md` for formats)

| path | what |
|---|---|
| `research/session_state.yaml` | the current state only, ≤ 25 lines; history in `session_history.md` |
| `research/registry_index.yaml` | one line per factor: outcome, key numbers, β, ex-regime Sharpe, family, decisive bar |
| `research/registry/<Name>.yaml` | the full row, read on demand |
| `research/families.yaml` | every family, its definition and members; the ordered assignment log |
| `research/stage2_order.yaml` | the pre-declared ratchet order, written once |
| `research/events.jsonl` | append-only, numbers and ids, no prose essays |
| `research/results/` | full report, `_summary.md`, blocks, meta — tracked |
| `MODEL_MANIFEST.yaml` | one block per composite version + its Stage 3 table; the holdout state |
| `research/CHANGELOG.md` | one entry per iteration, decision first, ≤ 8 lines |
| `osap_source/osap_frontier.yaml` | every OSAP predictor not tested, with the reason |
| `docs/JOURNAL.md` | dated step log: what ran, what was decided, what it cost |

## Every reply ends with two blocks

**Best model so far** — a table of every version in `MODEL_MANIFEST.yaml`,
live one marked, columns exactly:
`| version | legs | families | mean IC | IC t (NW) | LS Sharpe | ann ret | MaxDD | beta | turnover |`
(Sharpe, return and MaxDD hedged; `beta` the full-window β of the raw LS),
then one line: live legs by family and the last change; one line of caveat:
in-window 1999–2021, holdout unspent or SPENT date, and
`N accepted of M screened, K inventoried, phase X`.

**Next step** — one sentence: **Running:** …, **Yours:** …, or **Blocked:** ….
Never end on a question the rules already answer.

A run's body, above the blocks, in order: verdict per member and the bar
that decided it; provenance in one line; what the numbers mean (deciles,
halves, tiers, decay, turnover, delisting share, β, ex-regime Sharpe, family
joined and weight); against v0, the live composite and prior rows including
rejections; integrity anomalies; records written and tag owed. Bullets and
tables; every number once.

## Version control — LOCAL ONLY until the owner says otherwise

The repository is a local git repository with **no remote**. Commit after
every completed run and at every logical step (an inventory batch with its
specs and files, a screen with its rows and results, a family assignment
batch, a ratchet with its manifest block, a harness change with its tests);
never push, never add a remote. When the search is done the owner provides
the GitHub link and chooses the files to publish. The `/commit-step` skill
has the message format and the hooks' rules; `python3 scripts/stamp_block.py`
prints the stamp lines every message carries. One annotated tag per
composite version (`v0-baseline`, then `vN-add-<name>`); tags are never
moved. Revert with `git revert`, never reset or force.

## Commands

```bash
pytest tests/                                            # after any harness change
python3 harness/provenance.py                            # the four stamps
python3 harness/snapshot.py probe|download|verify|manifest   # pull, check, freeze the snapshot (data step)
python3 harness/snapshot.py live                         # prove the snapshot still equals the API
python3 harness/preflight.py --factors A,B               # checks, no backtest
python3 harness/run_test.py --baseline --stage 2         # measure the composite
python3 harness/run_test.py --baseline --stage 3         # construct the composite
python3 harness/run_test.py --factors A,...,L --stage 1  # screen a batch (Phase B)
python3 harness/run_test.py --factors A,B,C,D,E --stage 2  # ladder, max 5 (Phase D)
python3 harness/run_test.py --factor A --stage 2         # one rung
python3 scripts/records.py index|state|check             # rebuild the index, show state, drift check
python3 scripts/records.py frontier                      # check, printing all open OSAP names (Phase A)
```
