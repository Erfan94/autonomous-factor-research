# Lessons — what three earlier searches taught, and what this project does about it

Two predecessor projects (one on Bloomberg data, one on Sharadar, 2026-08 ..
2026-09) ran the same kind of loop: a fixed baseline, eight OSAP candidates
per batch, a standalone screen, a sequential ratchet. Each screened around
70–90 predictors and accepted three or four. Their factor-level outcomes are
NOT carried here on purpose — this search judges every candidate fresh — but
the methodological findings are, because the rules in `config/test_config.yaml`
are the consequences. Numbers below are from the second predecessor unless
noted.

| # | lesson (evidence) | consequence here |
|---|---|---|
| 1 | **A return-based spanning test was the binding bar and contradicted the stated philosophy.** The predecessor said it selected on information, but its accept rule required the candidate's solo decile long-short to earn alpha (NW t ≥ 1.65) on the composite's long-short. 31 of 36 ratcheted candidates passed the residual-IC information test; 5 of 36 passed spanning. 19 rejected rows had raised the composite's own IC with t > 2. The hurdle rose with every acceptance because alpha = solo return − β × base return and the base return grew from 12.8 to 17.9 %/yr. | **Stage 2 accepts on information**: residual IC t ≥ 2.0 AND paired composite-ΔIC t ≥ 2.0, with a guard that the blend's gross return does not fall significantly (t ≥ −2.0). Spanning alpha is printed as a diagnostic on every rung, never a bar. |
| 2 | **Charging a flat transaction cost on a standalone monthly decile portfolio rejected the highest-IC signals.** Eight rows with IC 0.015–0.051 failed only the after-cost bar; four had positive gross spreads eaten by 40 bp round-trip on 100 %+ monthly turnover. A leg in a 1/N blend contributes a fraction of its standalone turnover, and construction (buffers, holding periods) is where turnover is engineered. | **No cost anywhere.** Stage 1 requires a positive GROSS D10−D1; turnover is printed on every block and in the Stage 3 table so a reader can price it. Implementability is reported, never decided. |
| 3 | **Fixed dollar screens ($100 mm cap, $250 k ADV) are not the same screen in 1999 and 2025.** | **Relative screens, month by month**: NYSE 20th-percentile size breakpoint (the Fama-French microcap cut), bottom-20 % ADV dropped, price ≥ $1. |
| 4 | **The out-of-sample tail was eight months.** All decisions used 1999–2025 and the holdout began 2026-01, so the final validation would have had no power. | **Decisions on 1999-01 .. 2021-12; 2022-01 .. 2026-09 reserved** (57 months), spent once on the finished composite under D8, read from the `cut_holdout_*` fields of a continuous `--include-holdout` run. |
| 5 | **Stage 2 once tested a portfolio construction, not a signal** (first predecessor: five point bars on the deltas of an equal-weight blend's D10−D1; 9 of 19 rejections had every information bar passing and were killed by Sharpe/MaxDD alone). | Sharpe, MaxDD of the 1/N blend stay diagnostics. Weighting is Stage 3's question, answered on the accepted composite with five declared variants. |
| 6 | **Mechanical dilution**: a new leg enters at 1/(N+1) and absolute delta bars stall as N grows. | Every bar is a t-statistic on a paired or residual series; none is an absolute delta. |
| 7 | **No significance test** on the first search: SE of the mean IC (~0.005) was ten times the delta bar. | Newey-West t everywhere (3 lags, config). Levels: standalone 2.5, marginal 2.0 / 2.0, guard −2.0. |
| 8 | **Decile IC discards within-decile order** and a hit-rate bar rejected factors for a property of the extreme portfolio. | IC is Spearman on the continuous score; no hit-rate or Sharpe bar at Stage 1. |
| 9 | **One regime carried some factors** (value in 2000–02 and 2021–22). | Stage 1 requires mean IC > 0 in both halves; annual IC is on every summary. |
| 10 | **Lowering the standalone t bar does not raise the count.** At 2.0 instead of 2.5 four more rows would have reached Stage 2, all near-duplicates of an existing leg. The wall was downstream. | The standalone bar stays at 2.5, which is already below the Harvey-Liu-Zhu 3.0 for a new anomaly. |
| 11 | **Half the universe was scored on a different blend** once legs with history gates and financial nulls accumulated. | `leg_coverage_pct_full` on every block; the residual test is computed on the names that carry the candidate. |
| 12 | **The frontier was file-based, not source-based**: seven batches ran off a pool of translated files while over 100 of OSAP's 212 predictors went unaccounted, and the legs, indexed under project names, could have been re-suggested under their OSAP acronyms. | `scripts/records.py check` reconciles SignalDoc against rows + leg acronyms + files + `osap_frontier.yaml` and prints the open frontier; a design-time exclusion is a logged, measured reason. |
| 13 | **Moving any of the four stamps while a completed run was unevaluated stranded the run** — twice, once per stamp, because the rule had been written for one stamp. | `records.py check` DRIFTs on an unevaluated run whose stamps moved; the rule is stated for the class (any stamp). |
| 14 | **Design-time coverage was computed as the wrong statistic**: months-with-any-signal ÷ months is an upper bound on the pooled name-month coverage the harness measures, off by 25 pp for long-lookback signals. | A coverage claim is the pooled share × 0.95 (a measured bias) or is measured by preflight. |
| 15 | **Flipping a sign after seeing the number doubles the hypotheses.** | A flipped screen needs \|t\| ≥ 2.74 and the row carries the caveat. |
| 16 | **A "frozen" snapshot that nobody re-reads can silently lack columns the vendor publishes**: four unmapped tables sat unnoticed for a whole search. | `snapshot.py live` proves the parquet equals the API's schema and history; `records.py check` DRIFTs when the proof is stale. |
| 17 | **Binary events and group-constant signals cannot fill ten deciles.** Binary events, group-constant signals and heavily zero-filled items are structural exclusions under a 10-decile / 10 %-mass-point screen. | Kept as a known limitation; each is logged in `osap_frontier.yaml` with the measured mass point so the paper can list them. |


## Lessons from the third search (2026-09, the predecessor of this project)

Measured on the predecessor's frozen snapshot, 1999–2022, 288 months. No
factor is named; the numbers are what the rules below answer to.

| # | lesson (evidence) | consequence here |
|---|---|---|
| 18 | **A one-at-a-time paired ΔIC bar on an equal-weight blend is underpowered, not wrong.** 24 of 27 ratcheted candidates failed only that bar; 17 of them carried significant residual information (NW t ≥ 2). Each added ~0.001 of blend IC at weight 1/9 while a paired test resolves ~0.003 on 288 months. Added jointly, the 15 residual-passers raised blend IC by 0.0079 (t 3.37). | **Stage 2 accepts on residual IC (t > 2) with a gross-return guard.** The paired ΔIC is a diagnostic. |
| 19 | **Equal weight across every leg dilutes families unevenly**: a fourth volatility measure took a full 1/N vote from value. A blend of all 32 Stage 1 passers grouped into 8 declared families (1/F across, equal within) beat the 8-leg composite on IC (0.046 vs 0.040, paired t 2.58), Sharpe (0.52 vs 0.48) and drawdown, in both halves. | **The search construction is a family blend.** Families assigned after Stage 1, before Stage 2, fewer than ten. |
| 20 | **Unshrunk trailing-ICIR weights hurt every blend tested**, including the live composite alone (IC 0.040 → 0.032). | No learned weight in the search construction; the ICIR variant stays a Stage 3 diagnostic. |
| 21 | **Relative cuts recomputed monthly flicker at the boundary**: ~5% of names left the universe each month, 90% of them still trading, 94% small-tier, a third back within a month. Turnover was partly universe churn. | **Membership hysteresis**: enter at the 20th percentile, leave below the 15th, chain started cold at the first panel month so membership is a function of (config, data, month). |
| 22 | **The screens remove distressed names before they fail**: 22 performance-delisting name-months in 288 months against 2,387 mergers; the Shumway convention is effectively never triggered. | Kept, and stated: the model carries no distress exposure; distress-type signals are muted on this universe. The paper says so. |
| 23 | **Half-sample fades are partly composition**: the universe held ~2,500 names in 1999–2001 and ~1,750 after, so early years are small-name heavy. | The halves bar stays; universe size by year is on every baseline block's diagnostics and in the paper. |
| 24 | **Specs that carry verdicts leak.** Specs written during a search cited which siblings were accepted, which failed and at what t. | Specs are regenerated from the cached OSAP source; fetcher and translator are forbidden from citing any outcome. |
| 25 | **Field verification is snapshot-specific.** A `verified` status from another pull is a mapping, not a proof. | Every inherited status was reset to `mapped` with `probed_on_prior_snapshot`; the checker re-verifies on this snapshot before first use. |
| 26 | **Ratchet order decides which duplicate represents a family.** Alphabetical order lets a weak variant enter before its stronger sibling. | Stage 2 order is descending Stage 1 NW t over ALL passers, declared once when Phase C closes, never re-sorted. |

## Lessons from the third search's post-holdout study (2026-09-30, the direct predecessor of this project)

Measured on the predecessor's frozen snapshot: its decision window 1999–2022,
its spent holdout 2023-01..2026-08 (44 months), and a six-fold nested
walk-forward inside 1999–2022 (select on 1999..T, evaluate T+1..T+3, pooled
2005–2022). No factor or family is named.

| # | lesson (evidence) | consequence here |
|---|---|---|
| 27 | **Information bars accumulate exposures they do not measure.** The predecessor's ratchet accepted on residual IC and guarded only the raw D10−D1. Its long-short's beta to the cap-weighted market went from −0.12 at the baseline to −0.77 at the final version; in-window that bet paid in the bear years (the two carried regimes) and out of sample, with the market up 17 %/yr, it cost about −10 %/yr (holdout Sharpe −0.42 raw, +0.11 hedged ex ante with a trailing 36-month beta; in-window Sharpe outside the carried years −0.14 raw, +0.74 hedged). Its construction layer was sector- and dollar-neutral, not beta-neutral. | **The long-short is hedged by construction** (D4) and the beta is printed on every block and every rung (D5). |
| 28 | **Tuning the selection rule did not separate from noise.** In the walk-forward, the as-run rules beat a fixed baseline (pooled IC 0.025 vs 0.006, Sharpe 0.45 vs 0.27, five of six blocks) while tighter t bars, stability-in-thirds screens, family caps and a hedged Stage 2 guard all landed within noise of each other. | **The bars, the family blend and the order stay as they were** (D6); no pre-registration is spent on tightening. |
| 29 | **Construction is where the gain was.** Sector-neutral ranks and the ex-ante hedge took the walk-forward's selected composite from Sharpe 0.45 to 0.71, positive in all six three-year blocks, MaxDD −62 % → −41 %; the Sharpe outside the best long-short years ranked the predecessor's versions in their holdout order when the full-window Sharpe did not; restricting to the top half by market cap was worse (0.41 vs 0.45, hedged 0.37 vs 0.56) and the top 500 worse still. On 44 holdout months a Sharpe carries a standard error near 0.5, so the holdout confirms direction only. | **Ranks within sector** (D3), **the hedge** (D4), **a date-free ex-regime Sharpe on every block** (D5), **the broad universe kept** (D6). The block 2022-01..2026-09 is a clean test of selection, not of these changes (D2). |

## Token cost — what the loop reads

Read `session_state.yaml`, then the run's `_summary.md`; open the full `.txt`
only where the summary leaves a question open. The registry index is one line
per factor; a full row is read on demand. Events are numbers and ids.
