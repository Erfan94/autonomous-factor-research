<!-- SOURCE of paper/paper.md. Do not edit paper.md: run `python3 paper/build_tables.py --check`.
     A double-braced key is a value from paper/tables/00_facts.md (each with its record source);
     a double-braced table:NN_name pastes paper/tables/NN_name.md. No decimal is typed here by hand;
     `--check` lists every remaining typed integer. -->

# A pre-registered factor search on Sharadar with a sector-relative, market-hedged family blend: the full record

Alpha Model Auto Research V4. Every number below is generated from the project's record files by
`paper/build_tables.py`; Appendix A7 (`paper/tables/00_facts.md`) gives the source of each number in the prose.

## Headline

All holdout figures cover 57 months, 2022-01-01 to 2026-09-30; the canonical read is run 054 `cut_holdout_*`.

- **The declared headline fell to about half of its expectation, without significance.** The hedged D10−D1, the
  pre-registered headline, earned 10.81%/yr at Sharpe 0.523, NW t 1.18 (run 054). The expectation
  written before the spend was 16.34%/yr, Sharpe 0.996, NW t 3.96 (run 053). Beside it: the raw spread
  earned 3.01%/yr, Sharpe 0.124 (run 054). The hedge's ex-ante β averaged -0.549 (run 054),
  and the raw spread's realised β was -0.836 (run 055, the holdout-only cross-check).
- **The ranking information persisted at about its late in-window level, also without significance.** The composite's
  mean rank IC was 0.0300, NW t 1.87 (run 054): one-sided p ≈ 0.030, two-sided p ≈ 0.061, and below
  the 2.5 bar a single predictor needed at Stage 1. The benchmark written before the spend was the second-half
  in-window IC, 0.0283 (run 053). The IC was concentrated in 2022 (+0.105; table 08b).
- **Out of sample, most of the hedged return was the hedge term.** The hedge term is hedged − raw = −12·mean(β_t·M_t),
  the long market position the hedge adds to a net-short book. It was 7.79 of the 10.81 pp/yr out of
  sample (run 054), against 1.43 of 16.34 pp/yr in-window (run 053). Part of it is mechanical: M is a
  total return, so the hedge credits |β|·rf, which the excess-of-rf diagnostic removes (-2.26 pp/yr out of
  sample, -1.25 in-window). The lag ran the other way. The ex-ante β was about 0.29 less negative
  than the realised one, so the "hedged" series stayed net short that much market in a mostly rising market
  (45 of 57 months had a positive trailing 12-month market return; manifest, run 054). That residual short
  exposure depressed the hedged return.
- **The corrected readings are small.** The excess-of-rf hedged series earned 8.54%/yr, Sharpe 0.413,
  NW t 0.93 (run 054). The β-neutral investable book (the construction layer at $100M) earned
  0.74%/yr gross, Sharpe 0.101 (run 057). Its in-window gross Sharpe was
  0.856 (run 057 `cut_inwindow_*`, equal to run 049's to three places). Net of measured costs the
  declared layer row is negative at every size in both windows; some sensitivity rows are not (Section 7).
- **The contribution is the record, not the model.** It accounts for every one of 212 OSAP predictors: screened,
  excluded with a measured reason, or held as a seed leg. It also holds the bars and verdicts of 107 screens,
  rejections included, the decision log, and the orchestration that produced them.

**Convention.** Main-text in-window figures use the spend snapshot: run 053, DATA 42587e08609a, the bytes the holdout
was read on. Acceptance-time figures come from runs 001–052 on DATA 198b281de1a0, before the snapshot refresh. They
appear in the version history (table 05e), the ratchet tables and the appendices, labelled "acceptance-time, pre-refresh
bytes". All returns are gross unless labelled net. "Hedged" is the declared D4 series, "raw" is the unhedged D10−D1, and
"excess" is the rf-corrected diagnostic (Section 2). There are no charts; every table caption names its run or record
file. Sharpe ratios are printed to three places.

The project was built from a predecessor's skeleton, methodology only (D1).

## 1. Pre-registration

The search ran under one configuration file, `config/test_config.yaml`, at CONFIG_SHA 0d88328d5b10. All
57 `run_started` events carry this one CONFIG_SHA (1 distinct value), so the
pre-registration did not move during the search. The decision window is 1999-01-01 to 2021-12-31 (276 months).
The out-of-sample block is 2022-01-01 to 2026-09-30. Newey-West t-statistics use 3 lags throughout.

The four construction changes were fixed before any candidate was screened:

1. **Within-sector ranks (D3).** Every signal is percentile-ranked within its sector each month. A sector-month with
   fewer than 10 scored names falls back to the cross-section rank. The family blend averages these ranks.
2. **A market hedge by construction (D4).** The headline long-short is D10−D1 minus β_t × M_t. M is the universe's own
   cap-weighted total return. β_t is estimated on months t−36..t−1 only, and is 0 before 12 months
   of history. Under D11 the hedge reaches exactly one bar, the Stage 2 return guard. The Stage 1 spread bar reads the raw
   D10−D1. Both series are annualised as the monthly mean × 12, so hedged − raw = −12·mean(β_t·M_t) exactly (verification
   hedge_gap_check_before_phase_d); this paper calls that difference the hedge term.
3. **β and a date-free ex-regime Sharpe on every block (D5).** These are the Sharpe after removing the 3 best
   calendar years, and a bear/bull split on the sign of the trailing 12-month market return. They are
   diagnostics, never bars.
4. **Everything else unchanged (D6).** This covers the bars and their levels, the family blend, the broad universe,
   and the Stage 2 order and ladders.

The bars, verbatim:

*Table 01_bars_verbatim. The bars and the search rules, verbatim. Source: config/test_config.yaml lines 209-233 (CONFIG_SHA 0d88328d5b10).*

```yaml
acceptance_thresholds:

  stage1_standalone:
    min_ic_mean: 0.010
    min_ic_tstat_nw: 2.50            # Newey-West t of the monthly rank IC
    min_ic_half_mean: 0.0            # mean IC > 0 in BOTH halves of the window
    min_ls_ann_return_pct: 0.0       # D10-D1 GROSS annual return must be positive, on the series named below
    ls_spread_series: "raw"          # D11: the bar reads the RAW D10-D1 (ls_raw_ann_return_pct); "hedged" = the hedged headline
    min_coverage_pct: 40.0
    min_avg_names_per_decile: 30

  stage2_marginal:
    min_resid_ic_tstat_nw: 2.00      # residual IC after projecting on the base legs; STRICTLY GREATER THAN
    min_paired_delta_ls_tstat: -2.00 # guard: the family blend's hedged gross LS return must not fall significantly
    # The paired composite-dIC is a DIAGNOSTIC, not a bar: one leg added to a
    # many-family blend moves its IC by less than a paired test can resolve
    # on 276 months, so a dIC bar rejects on power rather than information.
search:
  composite_construction: "family_blend"   # 1/F across families, 1/n within; two-level, renormalised
  families_max: 9                          # fewer than ten families, assigned after Stage 1, before Stage 2
  stage1_batch_size: 12                    # candidates per Stage 1 run (one frame build per batch)
  stage1_order: "alphabetical_acronym"     # Stage 1 batches are formed in this order, never by any number
  stage2_order: "descending_stage1_ic_tstat_nw"  # over ALL Stage 1 passers, declared before any Stage 2 number
  stage2_ladder_max_rungs: 5
```

The family cap of 9 is in the configuration (`search.families_max`). The flip rule sits outside it, in
`CLAUDE.md`: a screen in the reversed sign is a second hypothesis and needs an absolute t of at least
2.74. Orientation is OSAP's published sign. The OSAP source is pinned to tag v2.0.0, commit
b4e911e6.

The design decisions:

*Table 01c_decisions. Design decisions D1-D11. Source: docs/DECISIONS.md headings (id, date, owner); the right-hand column is a paraphrase. Dated governing notes were added under D7 and D8 on 2026-10-01 (process_findings d7_other-project_outcome_clause, d8_other-project_restatement_figure).*

| id | date | decided by | what it fixes (paraphrase) |
|---|---|---|---|
| D1 | 2026-09-30 | Erfan Sadeghi | Fresh project from an earlier project's skeleton: methodology and code by allow-list; no outcome carried; fresh data pull. |
| D2 | 2026-09-30 | Erfan | Windows: decisions 1999-01..2021-12, holdout 2022-01..2026-09; the holdout tests selection, not the construction change. |
| D3 | 2026-09-30 | Erfan | Ranks formed within sector before the family blend; thin sector-months fall back to the cross-section; current sector label disclosed. |
| D4 | 2026-09-30 | Erfan | Long-short hedged to the universe's own cap-weighted return with an ex-ante 36-month beta; raw series and beta printed beside. |
| D5 | 2026-09-30 | Erfan | Beta and a date-free ex-regime Sharpe (ex top-3 years; bear/bull by trailing 12-month market) on every block and rung; never bars. |
| D6 | 2026-09-30 | Erfan | Every other rule kept as pre-registered: bars, levels, family blend, universe, Stage 2 order and ladders, flip rule. |
| D7 | 2026-09-30 | loop | What the construction layer must change before its first number: beta neutrality, a harness-built spread, regime cuts from the D5 rule. |
| D8 | 2026-09-30 | loop | The holdout spend protocol: refresh, in-window reproduction, then one spend, read from cut_holdout_* fields. |
| D9 | 2026-09-30 | Erfan | Version control local only until the owner publishes. |
| D10 | 2026-09-30 | Erfan | Runner and advisor roles. |
| D11 | 2026-09-30 | Erfan | The hedge reaches the Stage 2 guard only; the Stage 1 spread bar reads the raw D10-D1; no decile-monotonicity statistic. |

The runner had to stop and ask the owner only in these cases:

*Table 01b_stop_and_ask. The stop-and-ask list. Source: CLAUDE.md lines 132-139.*

| # | stop and ask (verbatim) |
|---|---|
| 1 | Spending the out-of-sample block (`--include-holdout` / `--holdout-only`, once, ever). |
| 2 | Anything that moves CONFIG_SHA (a re-baseline). |
| 3 | Anything that moves DATA_SHA (refreshing the snapshot, adding a table) — including the refresh the holdout spend needs (D8). |
| 4 | Bumping `osap_source.ref`. |
| 5 | Declaring the search finished and running the final validation. |
| 6 | A rule contradicting itself, or a result implying already-logged rows are wrong. |
| 7 | A tenth family (config `search.families_max`). |

## 2. Data

All data come from direct pulls of the Sharadar API, recorded twice. The first recording (DATA 198b281de1a0) held
13 Sharadar tables with full history; FUNDS is mapped in the field map but not held. Every run up to
052, and so every decision of the search, used these bytes.

**The first snapshot already held the holdout months.** It was a full-history pull, recorded 2026-09-30T16:39:10Z, and its
SEP table runs to 2026-09-29 (the frozen manifest before the refresh). The holdout was isolated by rule, not by
absent bytes. Every result block of runs 001–053 (52 runs with blocks) has eval_end 2021-12-31, and
`CLAUDE.md` makes a block whose eval_end reaches 2022 a hard stop, which the harness's validation flags as an
out-of-sample breach. The refresh was needed because the block ends on 2026-09-30, after that pull.

D8 required that refresh (stop-and-ask 3). The second recording (DATA 42587e08609a) re-pulled the same
13 tables, and added one external table, the three-month Treasury bill rate TB3MS from FRED. The
owner approved both in one message: "approve both, use TB3MS for rf".

*Table 02_snapshots. The two snapshot recordings. Source: research/events.jsonl `snapshot_recorded` (record text truncated at 260 characters).*

| events line | ts (UTC) | old DATA_SHA | new DATA_SHA | tables | reason (record text) |
|---|---|---|---|---|---|
| 13 | 2026-09-30T16:41:44Z | (none) | 198b281de1a0 | 13 | first pull, full history, 13 tables; verify OK (vocabularies match config: exchanges, categories, 10 delisting actions, ART; marketcap median 712m); live OK column-complete; FUNDS mapped, not held |
| 1104 | 2026-10-01T23:27:07Z | 198b281de1a0 | 42587e08609a | 13 Sharadar + TB3MS (detail) | D8 step 1 refresh (owner-approved stop-and-ask 3): 13 Sharadar tables re-pulled full history (SEP 45,393,854 rows to 2026-10-01; 2026-09-30 present with 6,262 names vs 6,324 on 09-29) + TB3MS external (FRED, 1,113 rows 1934-01..2026-09, 2026-09 = 3.94, no fill … |

*Table 02b_tables. Tables held in the spend snapshot. Source: data/SNAPSHOT_MANIFEST.yaml (status FROZEN, recorded_on 2026-10-01T23:26:28Z); DATA_SHA is derived from the per-table sha256 values listed there.*

| table | kind | rows | min date | max date |
|---|---|---|---|---|
| ACTIONS | sharadar | 714,029 | 1997-12-31 | 2026-10-05 |
| DAILY | sharadar | 39,855,506 | 1998-12-01 | 2026-10-01 |
| DESCRIPTIONS | sharadar | 386 |  |  |
| EVENTS | sharadar | 2,532,960 | 1993-11-08 | 2026-10-01 |
| METRICS | sharadar | 30,939 | 1997-12-31 | 2026-10-01 |
| SEP | sharadar | 45,393,854 | 1997-12-31 | 2026-10-01 |
| SF1 | sharadar | 3,218,127 | 1990-06-06 | 2026-10-01 |
| SF2 | sharadar | 11,559,783 | 2008-01-02 | 2026-09-30 |
| SF3 | sharadar | 81,210,476 | 2013-06-30 | 2026-06-30 |
| SF3A | sharadar | 670,115 |  |  |
| SF3B | sharadar | 306,512 |  |  |
| SP500 | sharadar | 60,185 | 1957-03-04 | 2026-10-01 |
| TB3MS | external | 1,113 | 1934-01-01 | 2026-09-01 |
| TICKERS | sharadar | 74,282 |  |  |

**The rf correction is a diagnostic, not a replacement.** The declared hedge (D4) subtracts β_t times the universe's
*total* return, so a negative-β book is credited |β_t| × rf_t as if it were return (decision
hedge_guard_negative_beta_property, logged during Phase D). Replacing the hedge proxy would move CONFIG_SHA, which is
stop-and-ask 2, and that was not asked. So the correction is reported beside the declared hedge:
excess_t = hedged_t + β_t × rf_t, with rf = TB3MS/1200 paired with the holding month. The bars are unchanged. In-window
on the spend snapshot the rf credit (`ls_rf_credit_pp`, excess minus hedged) is -1.25 pp/yr. The excess-of-rf
Sharpe is 0.928 against the hedged 0.996 (run 053).

**The refresh restated the in-window block.** Run 052 used the frozen bytes and run 053 the refreshed bytes, with the
same harness, config and composite. Of their shared result-block fields, 28 are identical and
54 differ (including data_sha). Run 053 adds 8 excess-of-rf fields. The mean IC moved by
-0.000009, and the hedged Sharpe from 0.983 to 0.996. No Stage 2 verdict is expected to move (decision
d8_step2_restatement_within_margin). That expectation is inferred from the composite-IC deltas against the thinnest
residual-t margins; the rungs were not re-run on the new bytes. No rejection rested on the guard. The monthly series is
not stored, so the restated months are not itemised.

*Table 02c_restatement. D8 step 2: the same harness, config and composite on the frozen and the refreshed bytes, in-window. Source: result blocks of runs 052 and 053; 28 fields identical, 54 different (including data_sha), 8 new in 053.*

| field | run 052 (DATA 198b281de1a0) | run 053 (DATA 42587e08609a) | difference |
|---|---|---|---|
| ic_mean | 0.038944 | 0.038935 | -0.000009 |
| ic_tstat_nw | 5.683053 | 5.681156 | -0.001897 |
| ic_half1_mean | 0.049774 | 0.049594 | -0.000180 |
| ic_half2_mean | 0.028114 | 0.028275 | +0.000161 |
| ls_sharpe | 0.982552 | 0.996435 | +0.013883 |
| ls_ann_return_pct | 16.122152 | 16.344422 | +0.222270 |
| ls_tstat_nw | 3.906882 | 3.960060 | +0.053178 |
| ls_raw_sharpe | 0.773385 | 0.790230 | +0.016845 |
| ls_raw_ann_return_pct | 14.619309 | 14.910787 | +0.291478 |
| ls_beta_fullwindow | -0.559560 | -0.555989 | +0.003571 |
| ls_beta_mean | -0.543694 | -0.539829 | +0.003865 |
| ls_sharpe_ex_top_years | 0.649801 | 0.666471 | +0.016670 |
| ls_maxdd_pct | -43.214321 | -43.233708 | -0.019387 |
| turnover_d10_pct | 58.135039 | 58.093391 | -0.041648 |

## 3. Inventory and the Stage 1 screen

Every OSAP predictor at the pinned commit was inventoried: 212 in all. 5 are the v0 seed legs. Of the
rest, 134 were constructible from Sharadar and 73 were not. Of the constructible ones,
106 were translated and passed preflight, and 28 failed preflight. Every excluded predictor has
a frontier row with its measured reason (Appendix A2): 64 need data Sharadar does not publish
(analyst forecasts, options, short interest, some Compustat items), 28 failed preflight (mass
points, discrete flags, coverage), and 9 start too late for the 120-month minimum.

*Table 03_inventory. Inventory accounting. Sources: research/events.jsonl `inventory_classified`; osap_source/osap_frontier.yaml; research/registry/*.yaml; research/registry_index.yaml `search_accounting`.*

| class | count | source |
|---|---|---|
| OSAP predictors (SignalDoc Cat.Signal = Predictor, ref b4e911e6) | 212 | inventory_classified |
| seed legs (v0, never screened) | 5 | inventory_classified |
| constructible: translated and preflight-passed | 106 | inventory_classified |
| constructible: preflight failed (frontier class preflight_failed) | 28 | osap_frontier.yaml |
| not constructible: data unavailable in Sharadar (frontier class data_unavailable) | 64 | osap_frontier.yaml |
| not constructible: data start too late (frontier class data_start) | 9 | osap_frontier.yaml |
| Stage 1 screens (translated candidates plus one declared flip) | 107 | registry rows |
| Stage 1 passes | 24 | registry rows |
| Stage 1 rejections | 83 | registry rows |
| Stage 1 inconclusive | 0 | registry_index |

The Stage 1 screen ran in batches of 12 in alphabetical order. It covered 107 signals: the
106 candidates and one declared flip. 24 passed, 83 were rejected and 0
were inconclusive. Most rejections fell on the t bar (79 decided by `ic_tstat_nw`).
4 signals cleared the t bar but had a mean IC below 0.010.

*Table 03b_stage1_fail_bars. Stage 1 rejections by bar. Source: research/registry/*.yaml `decided_by` and `stage1_failed` on the FAIL rows (decided_by names ic_tstat_nw when it fails, else the first failed bar in check order: decisions stage1_decided_by_convention, _fallback).*

| bar | decided the rejection | failed (any position) |
|---|---|---|
| ic_half_min | 0 | 49 |
| ic_mean | 4 | 76 |
| ic_tstat_nw | 79 | 79 |
| ls_raw_ann_return_pct | 0 | 17 |

*Table 03c_t_pass_other_fail. Screens that cleared the t bar and failed another. Source: research/registry/<name>.yaml stage1.ic_tstat_nw, stage1.ic_mean, decided_by.*

| factor | Stage 1 NW t | mean IC | decided by |
|---|---|---|---|
| ChNNCOA | 4.1486 | 0.0094 | ic_mean |
| OPLeverage | 2.8949 | 0.0087 | ic_mean |
| RevenueSurprise | 2.7821 | 0.0094 | ic_mean |
| EarningsConsistency | 2.5958 | 0.0090 | ic_mean |

**How many passes would chance alone produce?** The Stage 1 t bar is one-sided: t ≥ 2.5 in the published sign.
Under a global null where no predictor carries information, each of the 106 screens in the published sign passes
the t bar with probability P(Z ≥ 2.5) = 0.006210. The expected number of false passes is 106 ×
0.006210 = 0.658.

The flip rule adds a second path. A predictor qualifies for a reversed-sign screen when t ≤ −2.74, with
probability P(Z ≥ 2.74) = 0.003072 per predictor, or 0.326 expected. Both paths together give
0.984 expected false passes, against 24 observed. A screen must pass every bar, not only the t bar, so
these t-bar counts are upper bounds on the null passes of all bars.

Stage 2 is one-sided too (t > 2.0). Over 24 rungs the null expectation is 24 × 0.022750 =
0.546, against 14 acceptances. These expectations hold whatever the dependence between tests; correlated
signals widen the spread around them, not their mean. The normal tail approximates the Newey-West t, which is computed on
a few hundred monthly observations.

*Table 03d_null_fp. Expected false positives under the global null. Normal tail, p = 0.5 erfc(z / sqrt 2); counts from research/registry/*.yaml and research/registry_index.yaml `search_accounting`; bars from config/test_config.yaml; the 2.74 flip bar from CLAUDE.md and events `flip_hypothesis_qualified`. The expectation n x p holds under any dependence between tests; dependence widens its spread.*

| test family | tests n | bar | tail | p = P(Z beyond bar) | expected false positives n x p | observed |
|---|---|---|---|---|---|---|
| Stage 1, published sign | 106 | NW t >= 2.50 | one-sided (upper) | 0.006210 | 0.658 | 27 with t >= bar; 23 passed every bar |
| Stage 1, flip qualification (reversed sign) | 106 | NW t <= -2.74 | one-sided (lower) | 0.003072 | 0.326 | 2 qualified, 1 screened and passed |
| Stage 1, both paths | 106 |  |  | 0.009282 | 0.984 | 24 passed |
| Stage 2, residual IC | 24 | NW t > 2.00 | one-sided (upper) | 0.022750 | 0.546 | 14 accepted |

**Flip hypotheses.** Two predictors qualified for a flip, both at an absolute t of at least 2.74 in the OSAP sign.
BidAskSpread (absolute t 2.77) was declared as BidAskSpreadFlip and screened in the last batch. It passed at
t 2.7628, clearing the 2.74 bar, and was later rejected at Stage 2. GrLTNOA (absolute t 2.75)
qualified but was not screened. Its reversed mean IC, 0.0059, fails the 0.010 IC bar by a margin the
rank-reversal offset cannot close (decision flip_not_screened_when_deterministic_fail).

*Table 03e_flips. Flip hypotheses. Source: events `flip_hypothesis_qualified` (parent statistics), research/registry/<flip>.yaml (screen), decision flip_not_screened_when_deterministic_fail.*

| events line | parent | parent NW t | parent mean IC | flip | screened | flip Stage 1 NW t | outcome |
|---|---|---|---|---|---|---|---|
| 691 | BidAskSpread | -2.7705 | -0.020478 | BidAskSpreadFlip | yes (run 011) | 2.7628 | PASS / rejected |
| 755 | GrLTNOA | -2.7546 | -0.005898 | GrLTNOAFlip | no |  | not screened (decision flip_not_screened_when_deterministic_fail: reversed IC below the 0.010 bar) |

## 4. Families and the Stage 2 order

The 24 passers and the five seeds carry 11 distinct SignalDoc `Cat.Economic` labels. The cap is
9 families. A single decision (phase_c_family_partition) fixed the label-to-family map before any
assignment. Two labels were absorbed where an existing definition covers the construction: volume into liquidity, and
accruals into investment. Four new families were opened. The decision names the rejected alternatives. It also records
that every Stage 1 number was visible when the partition was chosen.

*Table 04_label_map. Label-to-family map fixed before any assignment. Source: events decision phase_c_family_partition (map text, parsed), research/families.yaml `assignments` (passers per label). The size row is the v0 seed; no passer carries that label.*

| SignalDoc Cat.Economic label | family | family kind | Stage 1 passers carrying the label |
|---|---|---|---|
| size | size | seed (v0 Size) |  |
| profitability | profitability | seed family | CBOperProf, GP, OperProfRD, RoE, roaq |
| valuation | value | seed family | CF, NetPayoutYield, cfp |
| momentum | momentum | seed family | TrendFactor |
| investment | investment | seed family |  |
| accruals | investment | seed family | PctAcc |
| volatility | volatility | new family | IdioVol3F, IdioVolAHT, MaxRet, RealizedVol |
| liquidity | liquidity | new family | zerotrade12M, zerotrade1M, zerotrade6M, BidAskSpreadFlip |
| volume | liquidity | new family | VolumeTrend |
| external financing | external_financing | new family | NetEquityFinance, ShareIss1Y, ShareIss5Y, XFIN |
| short-term reversal | short_term_reversal | new family | STreversal |

*Table 04b_families. The nine families. Source: research/families.yaml `families`; the v14 column from MODEL_MANIFEST.yaml v14 `families`.*

| family | definition | members | members (seeds first, passers in assignment order) | in v14 |
|---|---|---|---|---|
| size | market capitalisation (small = attractive) | 1 | Size | Size |
| value | price relative to a fundamental anchor | 4 | Value, CF, NetPayoutYield, cfp | Value, cfp |
| profitability | earning power relative to capital | 6 | Profitability, CBOperProf, GP, OperProfRD, RoE, roaq | Profitability, CBOperProf, GP, roaq, RoE |
| investment | growth of the asset base or of investment | 2 | Investment, PctAcc | Investment, PctAcc |
| momentum | continuation of past returns | 2 | Momentum, TrendFactor | Momentum, TrendFactor |
| volatility | dispersion or tail size of a stock's own returns (total, idiosyncratic, extreme daily); low = attractive | 4 | IdioVol3F, IdioVolAHT, MaxRet, RealizedVol | MaxRet, IdioVol3F |
| external_financing | net capital raised from or returned to investors (share issuance, net equity and debt financing) | 4 | NetEquityFinance, ShareIss1Y, ShareIss5Y, XFIN | ShareIss5Y, XFIN |
| short_term_reversal | reversal of the most recent month's return | 1 | STreversal | STreversal |
| liquidity | trading activity and trading cost (turnover, zero-volume days, bid-ask spread, volume trend) | 5 | VolumeTrend, zerotrade12M, zerotrade1M, zerotrade6M, BidAskSpreadFlip | zerotrade6M, VolumeTrend |

Phase C closed before any Stage 2 number existed. The 24 assignments, the declared order and the
phase close all precede the first Stage 2 run.

*Table 04c_phase_c_timeline. Phase C closed before any Stage 2 number. Source: research/events.jsonl, research/stage2_order.yaml.*

| event | events line | ts (UTC) |
|---|---|---|
| last Stage 1 run completed (run 011) | 834 | 2026-10-01T05:30:42Z |
| phase B closed | 849 | 2026-10-01T05:41:09Z |
| first and last of 24 family_assigned | 851-874 | 2026-10-01T05:45:32Z / 2026-10-01T05:45:32Z |
| stage2_order_declared | 875 | 2026-10-01T05:45:32Z |
| research/stage2_order.yaml `declared` |  | 2026-10-01T05:45:32Z |
| phase C closed | 876 | 2026-10-01T05:46:26Z |
| first Stage 2 run started (run 012) | 880 | 2026-10-01T05:52:14Z |
| first Stage 2 number evaluated (factor_evaluated, run 012) | 884 | 2026-10-01T06:02:03Z |

The ninth family was opened in Phase C, by VolumeTrend's assignment (2026-10-01T05:45:32Z), which reached
`families_max`. The composite first held nine families at v12. The remaining passers fell into existing
families. The order (Appendix A4) sorts all 24 passers by full-precision Stage 1 NW t and was never re-sorted.

## 5. The ratchet

5 ladders (runs 012, 023, 032, 037, 044) were cut from the declared order, five rungs at a time; the last had four.
Rung i faced the base plus every earlier passing rung. Of 24 rungs, 14 were accepted, 10
rejected and 0 inconclusive. Every rejection was decided by `resid_ic_tstat_nw`. None was decided by the guard:
no rung had a guard t below -2.0 (0 rows). The lowest guard t was -1.26
(RoE, accepted).

*Table 05_rungs. Every Stage 2 rung. Source: research/registry/<name>.yaml `stage2_run`, `stage2` (verbatim from the rung's block), `decided_by`; version from MODEL_MANIFEST.yaml `ratchet`. Acceptance-time, pre-refresh bytes (DATA 198b281de1a0).*

| run | rung | order rank | factor | family | base legs | resid IC | resid IC NW t (bar > 2.0) | resid months | guard t (bar >= -2.0) | paired dIC t (diag.) | verdict | decided by | version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 012 | 1 | 1 | PctAcc | investment | 5 | 0.0098 | 4.673595 | 276 | 0.0874 | 2.81 | PASS | all bars | v1 |
| 012 | 2 | 2 | CBOperProf | profitability | 6 | 0.0104 | 3.020413 | 276 | 0.9458 | -0.01 | PASS | all bars | v2 |
| 012 | 3 | 3 | ShareIss5Y | external_financing | 7 | 0.0120 | 3.608529 | 223 | 2.8334 | 3.03 | PASS | all bars | v3 |
| 012 | 4 | 4 | cfp | value | 8 | 0.0104 | 2.974093 | 276 | 2.1869 | 3.10 | PASS | all bars | v4 |
| 012 | 5 | 5 | XFIN | external_financing | 9 | 0.0069 | 3.273460 | 276 | -0.6374 | -0.62 | PASS | all bars | v5 |
| 023 | 1 | 6 | GP | profitability | 10 | 0.0073 | 2.741182 | 276 | 0.4291 | -0.79 | PASS | all bars | v6 |
| 023 | 2 | 7 | ShareIss1Y | external_financing | 11 | 0.0044 | 1.879334 | 270 | 0.1724 | 1.76 | FAIL | resid_ic_tstat_nw |  |
| 023 | 3 | 8 | MaxRet | volatility | 11 | 0.0179 | 4.007615 | 276 | 1.7489 | 2.61 | PASS | all bars | v7 |
| 023 | 4 | 9 | roaq | profitability | 12 | 0.0119 | 3.727830 | 276 | 1.9515 | 2.66 | PASS | all bars | v8 |
| 023 | 5 | 10 | RoE | profitability | 13 | 0.0045 | 2.412780 | 276 | -1.2571 | 1.44 | PASS | all bars | v9 |
| 032 | 1 | 11 | OperProfRD | profitability | 14 | -0.0011 | -0.424080 | 276 | 0.9243 | -0.20 | FAIL | resid_ic_tstat_nw |  |
| 032 | 2 | 12 | IdioVol3F | volatility | 14 | 0.0065 | 2.030731 | 269 | 0.8872 | 0.81 | PASS | all bars | v10 |
| 032 | 3 | 13 | NetEquityFinance | external_financing | 15 | 0.0035 | 1.395688 | 276 | 0.4727 | 1.86 | FAIL | resid_ic_tstat_nw |  |
| 032 | 4 | 14 | CF | value | 15 | 0.0023 | 1.020438 | 276 | -0.7610 | 0.72 | FAIL | resid_ic_tstat_nw |  |
| 032 | 5 | 15 | STreversal | short_term_reversal | 15 | 0.0153 | 3.808913 | 276 | -0.5362 | 1.50 | PASS | all bars | v11 |
| 037 | 1 | 16 | zerotrade6M | liquidity | 16 | 0.0099 | 2.686514 | 276 | 1.7206 | 0.99 | PASS | all bars | v12 |
| 037 | 2 | 17 | VolumeTrend | liquidity | 17 | 0.0047 | 2.043637 | 228 | -0.0866 | -0.19 | PASS | all bars | v13 |
| 037 | 3 | 18 | zerotrade12M | liquidity | 18 | 0.0010 | 0.490011 | 275 | 0.1364 | 0.10 | FAIL | resid_ic_tstat_nw |  |
| 037 | 4 | 19 | RealizedVol | volatility | 18 | 0.0055 | 1.730033 | 276 | -0.6125 | 0.37 | FAIL | resid_ic_tstat_nw |  |
| 037 | 5 | 20 | TrendFactor | momentum | 18 | 0.0078 | 2.140869 | 228 | -0.0051 | 1.36 | PASS | all bars | v14 |
| 044 | 1 | 21 | BidAskSpreadFlip | liquidity | 19 | 0.0051 | 1.769160 | 276 | 0.4268 | 1.83 | FAIL | resid_ic_tstat_nw |  |
| 044 | 2 | 22 | IdioVolAHT | volatility | 19 | 0.0073 | 1.923537 | 272 | 0.0617 | 0.71 | FAIL | resid_ic_tstat_nw |  |
| 044 | 3 | 23 | zerotrade1M | liquidity | 19 | -0.0025 | -1.278064 | 276 | 0.1143 | -0.36 | FAIL | resid_ic_tstat_nw |  |
| 044 | 4 | 24 | NetPayoutYield | value | 19 | 0.0003 | 0.116485 | 264 | 0.0604 | -0.56 | FAIL | resid_ic_tstat_nw |  |

*Table 05b_ladders. Ladder tallies. Source: research/registry/*.yaml stage2 rows grouped by `stage2_run`.*

| run | rungs | legs in base at rung 1 | accepted | rejected | accepted factors | rejected factors |
|---|---|---|---|---|---|---|
| 012 | 5 | 5 | 5 | 0 | PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN |  |
| 023 | 5 | 10 | 4 | 1 | GP, MaxRet, roaq, RoE | ShareIss1Y |
| 032 | 5 | 14 | 2 | 3 | IdioVol3F, STreversal | OperProfRD, NetEquityFinance, CF |
| 037 | 5 | 16 | 3 | 2 | zerotrade6M, VolumeTrend, TrendFactor | zerotrade12M, RealizedVol |
| 044 | 4 | 19 | 0 | 4 |  | BidAskSpreadFlip, IdioVolAHT, zerotrade1M, NetPayoutYield |

**Margins.** The two thinnest acceptances were IdioVol3F at 2.03 and VolumeTrend at 2.04. For scale, the
snapshot refresh moved the composite IC t by -0.0019 (table 02c). The two nearest misses were IdioVolAHT at
1.92 and ShareIss1Y at 1.88. In every case the rule decided; no rung was re-litigated.

*Table 05c_margins. Thinnest passes and nearest misses on the residual-IC bar. Source: research/registry/<name>.yaml stage2.resid_ic_tstat_nw.*

| kind | factor | resid IC NW t | margin to 2.0 |
|---|---|---|---|
| thinnest pass | IdioVol3F | 2.030731 | +0.030731 |
| thinnest pass | VolumeTrend | 2.043637 | +0.043637 |
| thinnest pass | TrendFactor | 2.140869 | +0.140869 |
| nearest miss | IdioVolAHT | 1.923537 | -0.076463 |
| nearest miss | ShareIss1Y | 1.879334 | -0.120666 |
| nearest miss | BidAskSpreadFlip | 1.769160 | -0.230840 |

**The guard has a disclosed bias toward negative-β legs** (decision hedge_guard_negative_beta_property). A rung that
moves the blend's ex-ante β is credited through the hedge term, whatever its information. MaxRet is the clearest case
(run 023). Its raw spread delta was -0.59 pp/yr, the hedge part 2.82 and the hedged delta
2.23. Its residual IC t of 4.01 carried the acceptance. For a negative-β new family the guard is
close to non-binding, and the residual IC is the operative gate. The split was recorded from ladder 2 on:

*Table 05d_hedge_part. The guard's delta split into raw spread and hedge term, as recorded from ladder 2 on. Source: events `factor_evaluated` (stage 2) field raw_vs_hedged_dls_pp; ladder 1 rows predate the field.*

| run | factor | raw dLS pp/yr | hedge part pp/yr | hedged dLS pp/yr | guard t | verdict |
|---|---|---|---|---|---|---|
| 023 | GP | +0.35 | -0.20 | +0.16 | 0.43 | PASS |
| 023 | ShareIss1Y | +0.04 | +0.03 | +0.07 | 0.17 | FAIL |
| 023 | MaxRet | -0.59 | +2.82 | +2.23 | 1.75 | PASS |
| 023 | roaq | +0.72 | +0.51 | +1.23 | 1.95 | PASS |
| 023 | RoE | -0.45 | +0.14 | -0.31 | -1.26 | PASS |
| 032 | OperProfRD | +0.19 | -0.02 | +0.17 | 0.92 | FAIL |
| 032 | IdioVol3F | +0.41 | -0.03 | +0.38 | 0.89 | PASS |
| 032 | NetEquityFinance | +0.01 | +0.18 | +0.19 | 0.47 | FAIL |
| 032 | CF | -0.67 | +0.28 | -0.40 | -0.76 | FAIL |
| 032 | STreversal | +1.09 | -1.73 | -0.64 | -0.54 | PASS |
| 037 | zerotrade6M | +0.64 | +0.90 | +1.55 | 1.72 | PASS |
| 037 | VolumeTrend | +0.18 | -0.21 | -0.03 | -0.09 | PASS |
| 037 | zerotrade12M | -0.06 | +0.11 | +0.04 | 0.14 | FAIL |
| 037 | RealizedVol | -0.38 | +0.25 | -0.13 | -0.61 | FAIL |
| 037 | TrendFactor | +0.77 | -0.77 | +0.00 | -0.01 | PASS |
| 044 | BidAskSpreadFlip | -0.20 | +0.40 | +0.20 | 0.43 | FAIL |
| 044 | IdioVolAHT | +0.02 | +0.00 | +0.02 | 0.06 | FAIL |
| 044 | zerotrade1M | -0.03 | +0.08 | +0.05 | 0.11 | FAIL |
| 044 | NetPayoutYield | -0.43 | +0.45 | +0.03 | 0.06 | FAIL |

**Every acceptance was reproduced.** After each acceptance the evaluator rebuilt the composite and ran
`--baseline --stage 2`. Each baseline reproduced its rung's with-candidate arm on 66/66 fields to six places
(phase_completed D). Stage 3 then ran per version. One annotated tag per version was created. The v1 tag points at the
wrong commit and was not moved (Section 9).

The version history, acceptance-time, pre-refresh bytes:

*Table 05e_versions. Version history v0-v14, acceptance-time, pre-refresh bytes (DATA 198b281de1a0). Source: MODEL_MANIFEST.yaml `versions[*]` (`legs`, `families`, `ratchet.bars`, `baseline`, `construction.run`, `stamps`). Gross; LS hedged unless labelled raw.*

| version | leg added | family | legs | families | ratchet run/rung | resid t | guard t | baseline run | IC | IC NW t | hedged Sharpe | hedged ann % | hedged MaxDD % | beta (full window) | raw Sharpe | Sharpe ex top-3 yrs | D10 turnover % | Stage 3 run | COMPOSITE_SHA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v0 | (seed: Size, Value, Profitability, Investment, Momentum) |  | 5 | 5 |  |  |  | 001 | 0.0145 | 2.62 | 0.600 | 7.32 | -45.56 | -0.140 | 0.719 | 0.159 | 28.0 | 002 | f9d9d9d95731 |
| v1 | PctAcc | investment | 6 | 5 | 012/1 | 4.67 | 0.09 | 013 | 0.0169 | 3.02 | 0.614 | 7.38 | -41.28 | -0.121 | 0.737 | 0.202 | 27.6 | 014 | cbeb16455bf4 |
| v2 | CBOperProf | profitability | 7 | 5 | 012/2 | 3.02 | 0.95 | 015 | 0.0169 | 3.02 | 0.661 | 7.82 | -37.07 | -0.122 | 0.777 | 0.249 | 28.0 | 016 | 8b444636f0a1 |
| v3 | ShareIss5Y | external_financing | 8 | 6 | 012/3 | 3.61 | 2.83 | 017 | 0.0215 | 3.98 | 0.848 | 10.29 | -41.92 | -0.192 | 0.874 | 0.465 | 26.3 | 018 | 73ee92fe0723 |
| v4 | cfp | value | 9 | 6 | 012/4 | 2.97 | 2.19 | 019 | 0.0249 | 4.51 | 0.996 | 12.02 | -40.63 | -0.263 | 0.913 | 0.614 | 25.2 | 020 | 3329679c69fb |
| v5 | XFIN | external_financing | 10 | 6 | 012/5 | 3.27 | -0.64 | 021 | 0.0245 | 4.27 | 0.914 | 11.56 | -47.75 | -0.344 | 0.808 | 0.479 | 25.0 | 022 | d27916e567f2 |
| v6 | GP | profitability | 11 | 6 | 023/1 | 2.74 | 0.43 | 024 | 0.0242 | 4.23 | 0.925 | 11.72 | -49.42 | -0.323 | 0.843 | 0.490 | 25.2 | 025 | 21a6688ae5d1 |
| v7 | MaxRet | volatility | 12 | 7 | 023/3 | 4.01 | 1.75 | 026 | 0.0305 | 4.49 | 0.951 | 13.95 | -41.68 | -0.649 | 0.622 | 0.623 | 43.4 | 027 | 43c92213ae73 |
| v8 | roaq | profitability | 13 | 7 | 023/4 | 3.73 | 1.95 | 028 | 0.0320 | 4.50 | 0.967 | 15.18 | -43.36 | -0.721 | 0.613 | 0.604 | 44.1 | 029 | a12e87c5fb36 |
| v9 | RoE | profitability | 14 | 7 | 023/5 | 2.41 | -1.26 | 030 | 0.0323 | 4.50 | 0.932 | 14.87 | -43.67 | -0.734 | 0.579 | 0.581 | 44.3 | 031 | c961f5791816 |
| v10 | IdioVol3F | volatility | 15 | 7 | 032/2 | 2.03 | 0.89 | 033 | 0.0326 | 4.48 | 0.919 | 15.25 | -45.78 | -0.752 | 0.578 | 0.575 | 39.8 | 034 | 1b4195ff18b4 |
| v11 | STreversal | short_term_reversal | 16 | 8 | 032/5 | 3.81 | -0.54 | 035 | 0.0355 | 5.36 | 0.942 | 14.61 | -39.53 | -0.512 | 0.737 | 0.565 | 59.1 | 036 | 335b06e3d608 |
| v12 | zerotrade6M | liquidity | 17 | 9 | 037/1 | 2.69 | 1.72 | 038 | 0.0373 | 5.15 | 0.985 | 16.16 | -41.11 | -0.635 | 0.708 | 0.646 | 56.8 | 039 | 612e59349f40 |
| v13 | VolumeTrend | liquidity | 18 | 9 | 037/2 | 2.04 | -0.09 | 040 | 0.0372 | 5.24 | 0.979 | 16.13 | -41.60 | -0.619 | 0.719 | 0.635 | 56.6 | 041 | fa17bd1cd37e |
| v14 | TrendFactor | momentum | 19 | 9 | 037/5 | 2.14 | -0.01 | 042 | 0.0389 | 5.68 | 0.983 | 16.12 | -43.21 | -0.560 | 0.773 | 0.650 | 58.1 | 043 | 7fe6f001e708 |

At acceptance time, on the pre-refresh bytes, the composite's mean IC rose between v0 and v14 from 0.0145 to
0.0389, and its NW t from 2.62 to 5.68. The hedged Sharpe rose from 0.600 to 0.983. The
full-window β of the raw spread went from -0.140 to -0.560, and D10 turnover from 28.0% to 58.1%
a month (runs 001 and 042). The guard's hedge part was largest for three accepted legs: MaxRet (2.82 pp/yr),
zerotrade6M (+0.90) and roaq (+0.51) (table 05d). IdioVol3F's was -0.03, and the
hedged Sharpe fell when it joined (0.932 at v9, 0.919 at v10). The acceptance-time hedged Sharpe peaked at
v4 (0.996); later acceptances raised the IC and its t, not the hedged Sharpe.

## 6. The in-window composite (v14, run 053)

v14 has 19 legs in 9 families (COMPOSITE 7fe6f001e708). On the spend snapshot, 1999-01-01 to
2021-12-31 (run 053), its mean IC is 0.0389, NW t 5.68 (plain t 6.43). The hedged long-short
earns 16.34%/yr at Sharpe 0.996, and the raw spread 14.91%/yr at Sharpe 0.790. The hedge
term is 1.43 pp/yr at a full-window β of -0.556.

*Table 06_v14_inwindow. v14 in-window, 1999-01..2021-12, on the spend snapshot. Source: run 053 result block (HARNESS 1271266472a9, CONFIG 0d88328d5b10, COMPOSITE 7fe6f001e708, DATA 42587e08609a). Gross; LS hedged unless labelled raw.*

| statistic | value |
|---|---|
| mean IC | 0.0389 |
| IC NW t (plain t) | 5.68 (6.43) |
| ICIR | 0.387 |
| IC halves | 0.0496 / 0.0283 |
| IC > 0 months % | 62.3 |
| hedged LS ann % / vol % / Sharpe / NW t | 16.34 / 16.40 / 0.996 / 3.96 |
| hedged MaxDD % | -43.23 |
| hit rate % | 62.7 |
| raw LS ann % / vol % / Sharpe / MaxDD % | 14.91 / 18.87 / 0.790 / -44.93 |
| excess-of-rf hedged ann % / Sharpe / NW t (diagnostic) | 15.09 / 0.928 / 3.75 |
| rf credit pp/yr | -1.254 |
| beta ex ante (mean) / full window | -0.540 / -0.556 |
| hedged months | 264 |
| Sharpe ex top-3 years (years) | 0.666 (2000,2001,2021) |
| top-3 years' share of summed LS % | 53.6 |
| Sharpe bear / bull (months) | 1.257 / 1.115 (64 / 200) |
| IC decay h1 / h3 / h6 / h12 | 0.0269 / 0.0247 / 0.0197 / 0.0235 |
| D10 / D1 turnover % per month | 58.1 / 54.5 |
| names per decile | 195.8 |
| names with all legs scored % | 45.4 |
| delisting-adjusted returns % | 0.44 |

**The information is front-loaded.** The IC halves are 0.0496 and 0.0283. The years 2000,2001,2021 carry
53.6% of the summed long-short return. The Sharpe without those years is 0.666. Annual IC is negative in
3 of 23 years: 2003 (-0.000), 2007 (-0.016), 2020 (-0.049), as printed in the run 053 summary.

*Table 06d_annual_ic. Annual mean IC, in-window, part 1. Source: research/results/053_*_summary.md `annual IC`.*

| year | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IC | +0.018 | +0.122 | +0.109 | +0.118 | -0.000 | +0.041 | +0.026 | +0.040 | -0.016 | +0.081 | +0.003 | +0.032 |

*Annual mean IC, in-window, part 2. Source: as above; values as printed there (a sign with 0.000 is a value smaller than 0.0005 in size).*

| year | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| IC | +0.059 | +0.019 | +0.019 | +0.041 | +0.040 | +0.030 | +0.001 | +0.039 | +0.009 | -0.049 | +0.114 |

*Table 06b_deciles. Decile mean monthly returns, equal weight, raw. Source: `decile_avg_ret_pct` in the run 053 block (1999-2021) and the run 055 block (holdout-only, 2022-01..2026-09; run 054's holdout cut prints no deciles).*

| decile | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
|---|---|---|---|---|---|---|---|---|---|---|
| in-window raw %/mo (run 053) | 0.261 | 0.562 | 0.761 | 0.782 | 1.022 | 1.067 | 1.114 | 1.259 | 1.350 | 1.504 |
| holdout raw %/mo (run 055) | 0.406 | 0.632 | 0.712 | 0.669 | 0.630 | 0.686 | 0.629 | 0.649 | 0.695 | 0.657 |

*Table 06c_tiers. Liquidity tiers in-window (diagnostic). Source: run 053 `tier_*` fields.*

| tier | IC | raw LS Sharpe | avg names |
|---|---|---|---|
| MEGA | 0.033500 | 0.275000 | 392 |
| MID | 0.034700 | 0.629000 | 587 |
| SMALL | 0.041200 | 0.922000 | 978 |

**The legs do not all start in 1999.** The early years run on fewer legs. In the first year all nine families are
present, but 15 of the 19 legs score in January. IdioVol3F starts in 1999-08: its FF3
factors are built from June 1999 formations, so its first signal is 1999-07. VolumeTrend and TrendFactor start
in 2003-01 (signal month-end 2002-12). ShareIss5Y starts in 2003-06 (signal
2003-05) because of its 65-month history gate. The family blend renormalises over the legs
present.

*Table 06e_leg_starts. When each v14 leg starts. Source: research/registry/<leg>.yaml stage1.n_months (candidates) and the run 053 preflight table (1998-12-31 probe); seed legs have no Stage 1 row and score from the first month. First month = 1999-01 plus (276 - scored months), i.e. unscored months are leading; registry caveats give the reasons (IdioVol3F: FF3 factors from 1999-07; ShareIss5Y: 65-month history gate; VolumeTrend: 60-month window; TrendFactor: uncensored coefficients from 2002-12).*

| leg | family | scored months | first holding month | first signal month-end | coverage at the 1998-12-31 probe % |
|---|---|---|---|---|---|
| Size | size | 276 | 1999-01 | 1998-12 | 100.0 |
| Value | value | 276 | 1999-01 | 1998-12 | 96.1 |
| Profitability | profitability | 276 | 1999-01 | 1998-12 | 56.0 |
| Investment | investment | 276 | 1999-01 | 1998-12 | 47.9 |
| Momentum | momentum | 276 | 1999-01 | 1998-12 | 94.6 |
| PctAcc | investment | 276 | 1999-01 | 1998-12 | 51.5 |
| CBOperProf | profitability | 276 | 1999-01 | 1998-12 | 37.7 |
| ShareIss5Y | external_financing | 223 | 2003-06 | 2003-05 | 0.0 |
| cfp | value | 276 | 1999-01 | 1998-12 | 51.9 |
| XFIN | external_financing | 276 | 1999-01 | 1998-12 | 51.9 |
| GP | profitability | 276 | 1999-01 | 1998-12 | 46.1 |
| MaxRet | volatility | 276 | 1999-01 | 1998-12 | 99.6 |
| roaq | profitability | 276 | 1999-01 | 1998-12 | 96.3 |
| RoE | profitability | 276 | 1999-01 | 1998-12 | 56.0 |
| IdioVol3F | volatility | 269 | 1999-08 | 1999-07 | 0.0 |
| STreversal | short_term_reversal | 276 | 1999-01 | 1998-12 | 99.6 |
| zerotrade6M | liquidity | 276 | 1999-01 | 1998-12 | 96.2 |
| VolumeTrend | liquidity | 228 | 2003-01 | 2002-12 | 0.0 |
| TrendFactor | momentum | 228 | 2003-01 | 2002-12 | 0.0 |

*Table 06f_legs_by_year. Legs active by year (years where the count changes; unchanged from the last row to 2021). Derived from table 06e.*

| year | legs in January | legs in December | families in December | legs starting that year |
|---|---|---|---|---|
| 1999 | 15 | 16 | 9 | IdioVol3F (1999-08) |
| 2003 | 18 | 19 | 9 | ShareIss5Y (2003-06), VolumeTrend (2003-01), TrendFactor (2003-01) |

**The rf correction** (run 053) lowers the headline from 0.996 to 0.928 (Sharpe) and from 16.34 to
15.09%/yr. The rf credit is -1.25 pp/yr. The Sharpe without the top-3 years is 0.605 on the
excess series.

**Return-start sensitivity** (runs 050 and 051, pre-refresh bytes; figures from the run 051 block; finding_confirmed
skip1_return_start_sensitivity). The whole-model alpha review flagged one risk: several legs end on the same close that
starts the forward return. That could carry untradeable bid-ask bounce into the IC. A diagnostic run started the forward
return at the first trade of month t+1 instead. The composite IC fell from 0.0389 to 0.0346 (paired
ΔIC -0.0044, NW t -3.06), about 11% of the IC. The hedged Sharpe fell from 0.983 to
0.777. The second-half IC barely moved (0.0281 to 0.0270). The loss sits in the value, investment and
financing legs, not in the short-horizon legs the bounce hypothesis named (table 06h). The signal-close convention was
declared in advance; no verdict is affected.

*Table 06g_skip1. Return-start sensitivity, diagnostic only. Source: result blocks of runs 050 and 051 (HARNESS aef490297071, DATA 198b281de1a0: pre-refresh bytes); finding_confirmed skip1_return_start_sensitivity.*

| field | run 050 (signal-close base) | run 051 (skip1 base) |
|---|---|---|
| ic_mean | 0.0389 | 0.0346 |
| ic_tstat_nw | 5.68 | 5.16 |
| ic_half1_mean | 0.0498 | 0.0421 |
| ic_half2_mean | 0.0281 | 0.0270 |
| ls_sharpe | 0.983 | 0.777 |
| ls_ann_return_pct | 16.12 | 12.26 |
| ls_raw_sharpe | 0.773 | 0.655 |
| ls_sharpe_ex_top_years | 0.650 | 0.476 |
| paired composite dIC (NW t) |  | -0.0044 (-3.06) |

*Table 06h_skip1_legs. Per-leg standalone IC (within-sector rank, published sign), signal-close vs skip1 base, sorted by delta t. Source: run 051 `legic_*` fields (pre-refresh bytes).*

| leg column | IC close | t | IC skip1 | t | delta | delta t |
|---|---|---|---|---|---|---|
| f_cfp | 0.0246 | 3.65 | 0.0200 | 3.00 | -0.0047 | -4.15 |
| f_inv | 0.0054 | 1.21 | 0.0023 | 0.53 | -0.0031 | -3.48 |
| f_xfin | 0.0170 | 3.57 | 0.0143 | 3.03 | -0.0027 | -2.91 |
| f_value | 0.0058 | 0.85 | 0.0028 | 0.42 | -0.0030 | -2.16 |
| f_pctacc | 0.0112 | 4.03 | 0.0099 | 3.81 | -0.0012 | -1.97 |
| f_mom | 0.0096 | 1.27 | 0.0064 | 0.85 | -0.0031 | -1.74 |
| f_cbop | 0.0209 | 3.74 | 0.0196 | 3.57 | -0.0013 | -1.42 |
| f_ivol3f | 0.0229 | 3.15 | 0.0207 | 2.86 | -0.0022 | -1.34 |
| f_voltrend | 0.0114 | 2.87 | 0.0103 | 2.55 | -0.0011 | -1.16 |
| f_maxret | 0.0233 | 3.42 | 0.0215 | 3.25 | -0.0018 | -0.94 |
| f_roaq | 0.0208 | 3.37 | 0.0199 | 3.28 | -0.0009 | -0.91 |
| f_streversal | 0.0145 | 2.96 | 0.0130 | 2.83 | -0.0015 | -0.91 |
| f_prof | 0.0205 | 3.78 | 0.0197 | 3.72 | -0.0008 | -0.88 |
| f_zt6m | 0.0185 | 2.93 | 0.0174 | 2.76 | -0.0012 | -0.78 |
| f_trendfactor | 0.0171 | 2.79 | 0.0159 | 2.55 | -0.0013 | -0.70 |
| f_roe | 0.0192 | 3.34 | 0.0185 | 3.34 | -0.0007 | -0.64 |
| f_shareiss5y | 0.0158 | 3.67 | 0.0153 | 3.50 | -0.0005 | -0.47 |
| f_size | -0.0093 | -1.53 | -0.0070 | -1.14 | +0.0023 | 1.32 |
| f_gp | 0.0155 | 3.52 | 0.0178 | 4.15 | +0.0022 | 2.64 |

**Stage 3** (run 043; run 048 reproduced it under the layer harness). Stage 3 is acceptance-time, pre-refresh bytes. No
in-window Stage 3 was run on the spend snapshot.

*Table 06i_stage3. Stage 3 on v14, in-window, acceptance-time, pre-refresh bytes. Source: MODEL_MANIFEST.yaml v14 `construction` (run 043); run 048 reproduced run 043 on every field but harness_sha (docs/JOURNAL.md, Phase E). Gross, hedged; raw Sharpe and full-window beta beside.*

| variant | sharpe | ls_t_nw | ann_ret_pct | vol_pct | maxdd_pct | worst_12m_pct | turnover_long_pct | turnover_short_pct | raw_sharpe | beta_fullwindow | sharpe_ex_top_years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| equal_rank_decile | 0.983 | 3.91 | 16.12 | 16.41 | -43.2 | -41.4 | 58.1 | 54.4 | 0.773 | -0.56 | 0.65 |
| tier_neutral | 0.858 | 3.55 | 14.59 | 17.0 | -44.0 | -41.0 | 59.5 | 55.7 | 0.617 | -0.64 | 0.54 |
| icir_weighted | 0.902 | 4.2 | 15.54 | 17.23 | -33.1 | -27.7 | 39.1 | 37.7 | 0.464 | -0.93 | 0.64 |
| buffered | 0.954 | 3.81 | 15.01 | 15.73 | -42.0 | -38.6 | 38.5 | 32.6 | 0.72 | -0.57 | 0.65 |
| vol_targeted | 0.901 | 3.95 | 10.94 | 12.14 | -30.6 | -29.2 | 58.1 | 54.4 | 0.711 | -0.31 | 0.61 |

## 7. The construction layer

D7 required three changes before the layer's first number. The book must be neutral to market β as well as sector
(implemented as a hard constraint). The half-spread must come from a harness-built Corwin-Schultz series rather than a
composite leg. The regime cuts must follow the D5 rule. The alpha review of that change asked for fixes first: one major
(a passage in the design notes cited another project's outcome; removed), one medium (the ex-years cut) and several
lows. They landed in a second harness move. Runs 045, 047 and 048 reproduced the measuring path (docs/JOURNAL.md).

*Table 07d_d7_changes. The D7 layer changes and the alpha-review fixes. Source: events `harness_changed` (text truncated at 420 characters).*

| events line | ts | old HARNESS | new HARNESS | tests | reason (record text) |
|---|---|---|---|---|---|
| 1060 | 2026-10-01T17:04:10Z | 73a95d352942 | 471f70782486 | 441 passed (434 - 1 replaced + 8 new) | D7 construction layer: (1) sector+market-beta neutrality via a constraint matrix [sector dummies \| beta_i], beta_i trailing 36m on D4's M (min 12, sector-month median fill), held by steps 1,2,5 per CONSTRUCTION.md 9.5, final book \|beta'w\|<=1e-10; reference row layer_no_beta_constraint; (2) Corwin-Schultz spread built in harness/data_layer.py (bit-exact vs BidAskSpread candidate raw on 1984 real name-months), no leg c … |
| 1071 | 2026-10-01T18:44:13Z | 471f70782486 | 3561590b660a | 445 passed | alpha_review fixes to the D7 layer (layer path only): declared vs effective ex-years fields (2000 precedes book_start; effective 2001,2021); name_cap_excess carried to summary; LayerRefused if spread join < costs.spread_measured_min_pct 95 (real 99.938% in-window, worst 99.58% 2021-02) or a sector_beta_neutral book month lacks beta; CS PIT test replaced with a non-vacuous one; _cs_builder_sha hashes Snapshot.table/ti … |

**In-window result** (run 049, book 2001-01 to 2021-12, pre-refresh bytes). At $100M the layer earns
4.08%/yr gross, Sharpe 0.856, NW t 3.27. Measured costs are 4.36%/yr:
spread 3.39, impact 0.79, borrow 0.19. Net, it earns -0.29%/yr at Sharpe
-0.060; the net Sharpe is -0.409 at $1B and -0.870 at $5B. One-way turnover is 36.0% a
month. Ex-post net β on M is -0.101 against an ex-ante target of zero. Without the β constraint, net β is
-0.135 and gross return is 4.39%/yr at Sharpe 0.805. All 33 rows are in
Appendix B1.

*Table 07a_layer_summary. The construction layer in-window (book 2001-01..2021-12), selected rows; all 33 rows are in Appendix B1 (table 07_layer049). Source: run 049 result blocks (pre-refresh bytes).*

| row | gross ann % | gross Sharpe | total cost %/yr | net ann % | net Sharpe | one-way turnover % | net beta on M |
|---|---|---|---|---|---|---|---|
| layer @ $100M | 4.08 | 0.856 | 4.36 | -0.29 | -0.060 | 36.0 | -0.101 |
| layer @ $1000M | 4.08 | 0.857 | 6.01 | -1.93 | -0.409 | 35.9 | -0.101 |
| layer @ $5000M | 3.79 | 0.819 | 7.81 | -4.02 | -0.870 | 34.1 | -0.097 |
| layer_fixed_tier_spread @ $100M | 4.06 | 0.854 | 1.69 | 2.37 | 0.502 | 36.0 | -0.101 |
| layer_no_beta_constraint @ $100M | 4.39 | 0.805 | 4.29 | 0.10 | 0.018 | 35.5 | -0.135 |
| equal_rank_decile @ $100M | 12.52 | 0.793 | 20.47 | -7.95 | -0.507 | 117.7 | -0.454 |

**The regime cuts (D7 item 3; manifest v14 `construction_layer.cuts`, run 049).** The D5 rule gave the declared ex-years;
the first precedes the book, so the effective cut removes 2001, 2021. Without them the layer's net Sharpe is
-0.370 (gross 0.647). In 2011–2020 it earned 0.95%/yr gross, Sharpe
0.222, and net Sharpe -0.559. **The gross return also faded after 2002.** It was
+23.6% in 2001 and +20.3% in 2002 (net +15.8 and +14.0). Over 2003–2020 it compounds to
+37.7% gross, about 1.79%/yr geometric (1.96%/yr arithmetic), and -36.1%
net (run 049 annual returns). The manifest's character line reads: "2003-2020 compounds to -36% net (+38% gross, 1.9%/yr)".

**Costs exceed the information, and the identity shows by how much.** Net and gross vol are close, so net Sharpe equals
gross Sharpe × (1 − cost/gross) to within 0.005 on every $100M row (table 07b). The layer is negative net
whenever measured costs exceed the gross return. The equal-weight decile book earns more gross return
(12.52%/yr, Sharpe 0.793) at 117.7% one-way turnover a month, and loses more net.

*Table 07b_identity. The gross-versus-cost identity: with net vol close to gross vol, net Sharpe = gross Sharpe x (1 - cost/gross). Source: run 049 result blocks, computed here.*

| variant @ $100M | gross Sharpe | cost / gross | gross Sharpe x (1 - cost/gross) | net Sharpe | difference | gross vol % | net vol % |
|---|---|---|---|---|---|---|---|
| layer | 0.856 | 1.070 | -0.060 | -0.060 | +0.000 | 4.76 | 4.74 |
| layer_eta_0.25 | 0.857 | 0.973 | 0.023 | 0.023 | +0.000 | 4.76 | 4.75 |
| layer_eta_1 | 0.857 | 1.264 | -0.226 | -0.227 | -0.001 | 4.76 | 4.73 |
| layer_fixed_tier_spread | 0.854 | 0.416 | 0.499 | 0.502 | +0.003 | 4.76 | 4.73 |
| layer_exec_half_month | 0.662 | 1.464 | -0.307 | -0.308 | -0.001 | 4.50 | 4.49 |
| layer_tiered_borrow | 0.856 | 1.242 | -0.207 | -0.208 | -0.001 | 4.76 | 4.74 |
| layer_no_buffer | 1.068 | 1.794 | -0.848 | -0.843 | +0.005 | 5.98 | 6.01 |
| layer_no_beta_constraint | 0.805 | 0.978 | 0.018 | 0.018 | +0.000 | 5.45 | 5.44 |
| layer_dollar_neutral_only | 0.820 | 0.959 | 0.034 | 0.034 | +0.000 | 5.41 | 5.45 |
| equal_rank_decile | 0.793 | 1.635 | -0.503 | -0.507 | -0.004 | 15.80 | 15.66 |
| buffered | 0.736 | 1.157 | -0.116 | -0.116 | +0.000 | 15.30 | 15.24 |

**Risk model.** Ex-ante vol averages 1.97% a year against 4.78% realised. The bias statistic is
2.58, inside the band in 20.5% of windows (run 049). Over run 057's book (2001-01..2026-09,
309 months) it is 3.12. The risk model underpredicts by more than a factor of two.

**Spread.** The measured Corwin-Schultz half-spread implies 39.2 bp per unit traded. The fixed-tier
alternative implies 8.3 bp (manifest v14 `construction_layer.trading`), with spread coverage
99.95% (run 049). *Judgment, not measurement:* the daily Corwin-Schultz estimate is floored at zero before
averaging. That biases measured spreads up for liquid names, so the true cost likely lies between the measured and the
fixed-tier rows (manifest v14 `construction_layer.character`). The fixed-tier row is net positive in-window at $100M
(Sharpe 0.502). No run measures which spread is right.

**"Negative net of measured costs" holds for the declared layer row, not for every row.** The `layer` row is net
negative at $100M, $1B and $5B in run 049 and in both windows of run 057; the build asserts it. 9
other rows are net positive: 4 use the fixed-tier spread, and 5 are $100M sensitivity
rows with measured spreads and net Sharpe of at most 0.058. None is positive out of sample
(0 rows).

*Table 07e_layer_positive_net_rows. Every construction-layer row with a positive net Sharpe. Source: runs 049 (`net_sharpe`), 057 (`cut_inwindow_net_sharpe`, `cut_holdout_net_sharpe`), all 33 variants each; `half_spread_mode` from the block.*

| run / window | variant | net Sharpe | half-spread mode |
|---|---|---|---|
| 049 | layer_dollar_neutral_only@100M | 0.034 | measured |
| 049 | layer_eta_0.25@100M | 0.023 | measured |
| 049 | layer_fixed_tier_spread@1000M | 0.156 | fixed |
| 049 | layer_fixed_tier_spread@100M | 0.502 | fixed |
| 049 | layer_no_beta_constraint@100M | 0.018 | measured |
| 057 in-window | layer_dollar_neutral_only@100M | 0.054 | measured |
| 057 in-window | layer_eta_0.25@100M | 0.058 | measured |
| 057 in-window | layer_fixed_tier_spread@1000M | 0.189 | fixed |
| 057 in-window | layer_fixed_tier_spread@100M | 0.519 | fixed |

On the spend snapshot the in-window book restates mildly: gross 4.15%/yr, net Sharpe -0.022 at
$100M (run 057 `cut_inwindow_*`).

*Table 07c_layer_restated. The layer's in-window book (2001-01..2021-12) on the frozen bytes (run 049, DATA 198b281de1a0) and on the spend snapshot (run 057 `cut_inwindow_*`, DATA 42587e08609a). Same layer config 4b279fc317cd.*

| AUM | gross ann % (049) | gross ann % (057 in-window) | gross Sharpe (049) | gross Sharpe (057 in-window) | cost (049) | cost (057 in-window) | net Sharpe (049) | net Sharpe (057 in-window) |
|---|---|---|---|---|---|---|---|---|
| $100M | 4.08 | 4.15 | 0.856 | 0.856 | 4.36 | 4.25 | -0.060 | -0.022 |
| $1000M | 4.08 | 4.16 | 0.857 | 0.859 | 6.01 | 5.86 | -0.409 | -0.356 |
| $5000M | 3.79 | 3.95 | 0.819 | 0.837 | 7.81 | 7.65 | -0.870 | -0.799 |

## 8. Out of sample

The holdout was spent once, on 2026-10-02, on v14 with DATA 42587e08609a and the frozen layer (runs 054–057). The
owner answered stop-and-ask 5 with "Yes". The canonical read is run 054 `cut_holdout_*`. In that run the hedge
β is estimated continuously across the 2021-12/2022-01 boundary. Run 055 (`--holdout-only`) is the cross-check. Its
first months run unhedged (β = 0; 45 hedged months), and it reports the deciles, tiers and ex-top-3
rows that 054's cut does not print. Run 054's in-window cut equals run 053 on 20 of 20 shared fields.

**The expectations, verbatim** (decision holdout_expectations_v14_spend_snapshot, logged 2026-10-02T00:14:32Z; the first holdout
run started 2026-10-02T01:09:09Z):

> Rule: D8 reads the holdout against the live version's in-window figures on the spend snapshot. On DATA 42587e08609a (run 053, in-window 1999-2021, v14): hedged LS Sharpe 0.9964 (ann 16.34%); ex-top-3-years Sharpe 0.6665 (2000, 2001, 2021); excess-of-rf hedged Sharpe 0.9285 (ann 15.09%); excess ex-top-3-years Sharpe 0.6045; mean IC 0.0389 full window, 0.0283 second half (benchmark the holdout IC against the second half); raw Sharpe 0.7902; layer run 049 net Sharpe -0.06 @100M (old bytes, measured CS). The run-042 expectations stay as history. Written before any out-of-sample number; no bar.

*Table 08_vs_expectation. The holdout against the expectations written before it. Metrics and sources from MODEL_MANIFEST.yaml v14 `holdout.vs_expectation` (= events `holdout_spent`); values re-read from the named run blocks (run 053; run 054 `cut_holdout_*`; run 055; runs 049 and 057 for the layer) at the paper's precision, and checked against the manifest's rounded values. Expectations from decision holdout_expectations_v14_spend_snapshot.*

| metric | in-window expectation (run 053 unless noted) | holdout | holdout source |
|---|---|---|---|
| hedged_sharpe | 0.996 | 0.523 | 054 |
| hedged_ann_return_pct | 16.34 | 10.81 | 054 |
| hedged_ls_t_nw | 3.96 | 1.18 | 054 |
| ex_top3_hedged_sharpe | 0.666 | -0.572 | 055 only (054 cut prints none); top years 2022,2024,2026 = 3 of 5 calendar years |
| excess_sharpe | 0.928 | 0.413 | 054 |
| excess_ann_return_pct | 15.09 | 8.54 | 054 |
| excess_ex_top3_sharpe | 0.605 | -0.708 | 054; top years 2022,2024,2026 |
| rf_credit_pp | -1.25 | -2.26 | 054 |
| ic_mean | 0.0389 | 0.0300 | 054; vs second-half benchmark 0.0283 |
| ic_t_nw | 5.68 | 1.87 | 054 |
| raw_sharpe | 0.790 | 0.124 | 054 (= 055) |
| raw_ann_return_pct | 14.91 | 3.01 | 054 (= 055) |
| hedged_maxdd_pct | -43.23 | -35.65 | 054 |
| layer_net_sharpe_100M | -0.060 | -0.367 | 057 layer@100M; expectation is run 049 on the old bytes (057 in-window restates it to -0.022) |

**What held.** The mean IC, 0.0300, is 77% of the full in-window mean and above the second-half
benchmark 0.0283. At NW t 1.87 on 57 months the one-sided p is about 0.030: not significant
two-sided (p ≈ 0.061), and below the 2.5 Stage 1 bar.

**What did not.**

- *The declared headline.* The hedged D10−D1 earned 10.81%/yr, Sharpe 0.523, NW t 1.18 (run 054),
  against an expected 16.34%/yr, Sharpe 0.996, NW t 3.96 (run 053). Beside it, the raw spread earned
  3.01%/yr (Sharpe 0.124) and the excess series 8.54%/yr (Sharpe 0.413).
- *Concentration.* 2022 alone has IC +0.105 (run 054) and a hedged return of +60.0% (run 056
  equal_rank_decile, the same series as run 054's cut). The holdout-only IC halves are 0.0567 and
  0.0043 (run 055).
- *Decile shape.* In the holdout D1 earns 0.406%/mo, and D2 to D10 sit flat between 0.629 and
  0.712 (run 055; table 06b). The spread is the short bottom decile only.
- *Drawdown.* The raw maximum drawdown of the whole 1999–2026 record, -51.84% (run 054), falls in the
  holdout.
- *The ex-top-3 diagnostic is mechanical here.* The holdout spans 5 calendar years. Removing the top
  3 (2022,2024,2026) leaves 2, both negative. The resulting Sharpes (-0.572
  hedged, run 055; -0.708 excess, run 054) carry no regime information.

*Table 08b_holdout_years. The holdout by calendar year (2026 is January-September). Sources: research/results/054_*_summary.md `annual IC`; run 056 equal_rank_decile `annual_returns_pct`; run 057 layer@100M `annual_gross_returns_pct`, `annual_net_returns_pct`.*

| year | composite IC (054) | hedged D10-D1 % (056 equal_rank_decile) | layer@$100M gross % (057) | layer@$100M net % (057) |
|---|---|---|---|---|
| 2022 | +0.105 | +60.0 | +20.8 | +15.9 |
| 2023 | -0.002 | -7.9 | -0.3 | -3.9 |
| 2024 | +0.031 | +3.5 | -7.4 | -10.6 |
| 2025 | -0.021 | -16.2 | -8.8 | -12.0 |
| 2026 | +0.040 | +18.4 | +0.6 | -0.7 |

*Table 08c_holdout_tiers. Liquidity tiers in the holdout (diagnostic). Source: run 055 `tier_*` fields (run 054's holdout cut prints no tiers).*

| tier | IC | raw LS Sharpe |
|---|---|---|
| MEGA | 0.020200 | -0.131000 |
| MID | 0.040400 | 0.126000 |
| SMALL | 0.033100 | 0.209000 |

**The hedge lagged, and the lag cost return.** The ex-ante β averaged -0.549 over the holdout (run 054). The
raw spread's realised β was -0.836 (run 055), and the last ex-ante estimate was -1.108. In-window the
two agreed (-0.540 and -0.556, run 053). The trailing 36-month estimate under-hedged by
about 0.29 of market, so the hedged series stayed net short in a mostly rising market (bull months
45, bear months 12; manifest, run 054). That depressed the hedged return; it is neither the raw book
nor a neutral one. What flattered the hedged return mechanically is the rf credit, -2.26 pp/yr (in-window
-1.25). The excess series, which removes it, earned 8.54%/yr at Sharpe 0.413, NW t
0.93 (run 054). The cross-check (run 055) left the first year unhedged. It shows a hedged Sharpe of 0.584,
with the same IC and raw return.

*Table 08d_beta. The hedge beta against the realised beta. Sources as named per row.*

| quantity | source field | value |
|---|---|---|
| ex-ante beta, mean over holdout months | run 054 cut_holdout_ls_beta_mean | -0.549 |
| ex-ante beta, mean over the 45 hedged months of the holdout-only run | run 055 ls_beta_mean | -0.504 |
| realised beta of the raw LS, holdout | run 055 ls_beta_fullwindow | -0.836 |
| ex-ante beta, last month | run 054 ls_beta_last | -1.108 |
| ex-ante beta, mean in-window | run 053 ls_beta_mean | -0.540 |
| realised beta of the raw LS, in-window | run 053 ls_beta_fullwindow | -0.556 |
| layer@$100M net beta on M, holdout | run 057 cut_holdout_net_beta_on_market | -0.186 |
| layer@$100M net beta on M, in-window | run 057 cut_inwindow_net_beta_on_market | -0.098 |

**The investable book.** At $100M the layer earned 0.74%/yr gross, Sharpe 0.101. Costs
of 3.40%/yr left -2.66%/yr net, Sharpe -0.367 (run 057).

*Table 08e_layer_holdout. The construction layer in the holdout (57 months). Source: run 057 `cut_holdout_*` fields.*

| AUM | variant | gross ann % | gross Sharpe | total cost % | net ann % | net Sharpe | net beta on M |
|---|---|---|---|---|---|---|---|
| $100M | layer | 0.74 | 0.101 | 3.40 | -2.66 | -0.367 | -0.186 |
| $100M | layer_fixed_tier_spread | 0.75 | 0.103 | 1.15 | -0.40 | -0.055 | -0.187 |
| $100M | layer_no_beta_constraint | 0.70 | 0.095 | 3.40 | -2.70 | -0.369 | -0.192 |
| $100M | equal_rank_decile | 3.01 | 0.124 | 17.47 | -14.45 | -0.597 | -0.829 |
| $1000M | layer | 0.74 | 0.101 | 4.26 | -3.52 | -0.485 | -0.186 |
| $1000M | layer_fixed_tier_spread | 0.74 | 0.102 | 2.00 | -1.26 | -0.174 | -0.187 |
| $1000M | layer_no_beta_constraint | 0.72 | 0.099 | 4.25 | -3.53 | -0.482 | -0.192 |
| $1000M | equal_rank_decile | 3.01 | 0.124 | 27.39 | -24.38 | -1.007 | -0.826 |
| $5000M | layer | 0.70 | 0.097 | 5.77 | -5.07 | -0.701 | -0.185 |
| $5000M | layer_fixed_tier_spread | 0.73 | 0.100 | 3.52 | -2.79 | -0.386 | -0.186 |
| $5000M | layer_no_beta_constraint | 0.67 | 0.091 | 5.77 | -5.10 | -0.697 | -0.191 |
| $5000M | equal_rank_decile | 3.01 | 0.124 | 45.75 | -42.73 | -1.759 | -0.822 |

**Gaps in the spend, disclosed rather than repaired.** D8 step 4 asked for Stage 3 to be read from its holdout cuts.
Run 056's Stage 3 blocks carry none (process_finding stage3_holdout_cuts_absent). The only Stage 3 evidence for the
holdout is therefore the calendar-year returns below and the 1999–2026 full-window statistics. Run 055 is flagged by the
harness's own minimum-sample rule: "Only 57 usable months (minimum 120). INCONCLUSIVE, not a rejection — a thin sample is a coverage problem." Its decile-collapse warning is the same floor applied to a
57-month window, with the long-short present in every month.

*Table 08f_stage3_holdout. Stage 3 variants in the spend run. Run 056 printed no holdout cut (process_finding stage3_holdout_cuts_absent), so only the 1999-2026 full-window statistics and the printed calendar-year hedged returns exist. Source: run 056 result blocks.*

| variant | Sharpe 1999-2026 | raw Sharpe 1999-2026 | beta 1999-2026 | 2022 % | 2023 % | 2024 % | 2025 % | 2026 % (Jan-Sep) |
|---|---|---|---|---|---|---|---|---|
| equal_rank_decile | 0.896 | 0.647 | -0.61 | +60.0 | -7.9 | +3.5 | -16.2 | +18.4 |
| tier_neutral | 0.764 | 0.482 | -0.70 | +61.3 | -10.2 | +1.3 | -17.1 | +16.9 |
| icir_weighted | 0.800 | 0.369 | -0.94 | +34.7 | -2.9 | +9.0 | -11.0 | +15.7 |
| buffered | 0.869 | 0.604 | -0.61 | +53.3 | -4.0 | +4.7 | -16.7 | +16.3 |
| vol_targeted | 0.822 | 0.599 | -0.33 | +21.5 | -4.9 | -0.2 | -8.0 | +7.9 |

**What the holdout can and cannot test (D2).** The block is a clean test of factor selection. Every candidate was
screened fresh on this snapshot, and no month after 2021-12-31 entered any decision. It is not an unbiased test of the
construction changes (within-sector ranks, the hedge, the diagnostics). Those were motivated by a study, made before this
project, that read 2023–2026 data. The owner chose this overlap knowingly. The holdout can confirm or refute the
selected composite. It cannot say whether the hedge and the sector ranking would have been chosen without seeing those
years.

## 9. Integrity

**Alpha reviews.** There were 23 adversarial audits: 20 on translated batches in
Phase A, then the STreversal residual-share trigger, the D7 layer and the whole model before the holdout. They found
1 critical issue, a missing history gate on PriceDelayRsq, fixed before any screen. The Phase A
majors were fixed before any screen, and the D7 review's major before the first layer number. The whole-model review's
two majors were answered by a diagnostic (the skip1 run 051) and by the choice of the holdout IC benchmark (the second
half).

*Table 09_alpha_reviews. Every alpha-reviewer audit. Source: events `alpha_review` (finding lists counted). Timestamps on events rows 219-419 are sequence estimates, not clock readings (finding_corrected events_ts_estimated, events_ts_estimated_row); their true bound is the commit that first carries them.*

| events line | ts | target | findings by severity | verdict |
|---|---|---|---|---|
| 67 | 2026-09-30T17:16:42Z | batch01: AM, Accruals | critical 0, major 0, minor 5 |  |
| 97 | 2026-09-30T17:34:33Z | batch02: AnnouncementReturn, BMdec, BPEBM, Beta, BetaFP | critical 0, major 2, minor 5 |  |
| 151 | 2026-09-30T17:57:42Z | batch03: BetaLiquidityPS, BetaTailRisk, BidAskSpread, BookLeverage, CBOperProf, CF | critical 0, major 0, minor 3 |  |
| 164 | 2026-09-30T18:05:10Z | batch04: Cash, CashProd, ChAssetTurnover, ChEQ, ChInv, ChInvIA | critical 0, major 0, minor 5 |  |
| 224 | 2026-09-30T18:40:00Z | batch05-06: ChNNCOA, ChNWC, ChTax, CompEquIss, CompositeDebtIssuance, CoskewACX, Coskewness, DelCOA | critical 0, major 1, minor 4 |  |
| 234 | 2026-09-30T18:55:00Z | batch07: DelCOL, DelEqu, DelFINL, DelNetFin | critical 0, major 1, medium 1, minor 4 |  |
| 274 | 2026-09-30T20:45:00Z | batch08: DolVol, EBM, EP, EarningsConsistency | critical 0, major 0, medium 1, minor 4 |  |
| 293 | 2026-09-30T21:35:00Z | batch09: EquityDuration, EarningsSurprise, EntMult | critical 0, high 0, medium 2, low 8 |  |
| 321 | 2026-09-30T23:10:00Z | fetch10-11: GP, GrLTNOA, GrSaleToGrInv, GrSaleToGrOverhead, Herf, HerfAsset, HerfBE, High52 | critical 0, high 0, medium 1, low 6 |  |
| 359 | 2026-10-01T01:20:00Z | batch12: IdioVol3F, IdioVolAHT, Illiquidity, IntMom, IntanBM | critical 0, major 1, minor 5 |  |
| 387 | 2026-10-01T02:55:00Z | batch13: InvestmentTWX, LRreversal, Leverage, InvGrowth, IntanSP, IntanEP, IntanCFP | critical 0, major 0, minor 4 |  |
| 410 | 2026-10-01T04:25:00Z | batch14: Mom6m, Mom12mOffSeason, MomOffSeason, MRreversal, MaxRet, MeanRankRevGrowth | critical 0, major 1, minor 4 |  |
| 447 | 2026-09-30T21:19:00Z | batch15-16: MomOffSeason06YrPlus, MomSeason, MomSeason06YrPlus, MomSeasonShort, NOA, NetDebtFinance, NetEquityFinance, N … | critical 0, high 0, medium 1, low 5 |  |
| 484 | 2026-09-30T21:43:50Z | batch17: OPLeverage, OperProfRD, OrgCap | critical 0, major 2, minor 5 |  |
| 496 | 2026-09-30T21:54:22Z | batch18: PctAcc, PctTotAcc, Price, PriceDelayRsq | critical 1, major 0, minor 3 |  |
| 516 | 2026-09-30T22:05:06Z | batch19: PriceDelaySlope, PriceDelayTstat | critical 0, major 0, minor 3 |  |
| 572 | 2026-09-30T22:34:37Z | batch20-21: RealizedVol, RoE, SP, STreversal, ShareIss1Y | critical 0, major 0, medium 1, minor 5 |  |
| 633 | 2026-09-30T22:56:02Z | batch21-23: ResidualMomentum, ReturnSkew, ReturnSkew3F, RevenueSurprise, ShareIss5Y, VolMkt, VolSD, VolumeTrend, XFIN | critical 0, major 2, minor 5 |  |
| 666 | 2026-09-30T23:04:47Z | batch24-25: grcapx, grcapx3y, cfp, dNoa, roaq | critical 0, major 2, minor 2, low 2 |  |
| 669 | 2026-09-30T23:12:47Z | final batch: TotalAccruals, TrendFactor, VarCF, zerotrade1M, zerotrade6M, zerotrade12M | critical 0, major 0, minor 2, low 3 | clear_to_screen |
| 992 | 2026-10-01T09:05:04Z | STreversal@run032_rung5 (trigger: residual IC share 1.06) | critical 0, major 0, minor 0, low 2 | clear_to_apply |
| 1069 | 2026-10-01T17:14:30Z | 41edba9 D7 construction layer | major 1, medium 1, low 5 | fix first |
| 1084 | 2026-10-01T19:44:00Z | whole model v14 (19 legs, composite.py) before stop-and-ask 3/5 | critical 0, major 2, minor 4 | clean to take to the owner |

**Process findings.** There are 31 process findings (Appendix B2). 6 of them
concern text that refers to another project: book_equity_preferred_terms, scratchpad_glob_other-project_names, leak_sweep_phase_d_close, construction_md_other-project_caveat, d7_other-project_outcome_clause, d8_other-project_restatement_figure. Their record text is not reproduced; the clauses that name
the other project are omitted and pointed to by events line.

- book_equity_preferred_terms: field-map notes cited a ruling logged only in another project's event log; the ruling was
  re-made here on its own terms.
- scratchpad_glob_other-project_names: a fetcher's directory listing showed another project's scratch folder names.
  Nothing was opened or cited, and later prompts named their own folder.
- leak_sweep_phase_d_close: the grep sweep at the D-to-E boundary. Its hits were project provenance and one
  data-construction parity note; no predictor's outcome elsewhere was cited, and no action was needed.
- construction_md_other-project_caveat, d7_other-project_outcome_clause and d8_other-project_restatement_figure: three
  passages in design documents (`docs/CONSTRUCTION.md`, D7, D8) that carried another project's outcome or measurement.
  The first was removed; the D7 and D8 decisions were annotated with dated governing notes, and their text was left
  as dated.

The only CONFIG move (events line 10, Appendix B7) has one clause omitted for the same reason. It records D11: the Stage 1
spread bar reads the raw series, the config schema moved, bars and levels were unchanged, and no run existed.

Other entries:

- The v1 tag is mis-pointed (tag_v1_mispointed): `v1-add-PctAcc` annotates 2e37d4b, not the v1 commit 0d52a33. Tags
  are never moved, so the owner decides (Appendix A6).
- Two of the whole-model review's minors: current SIC, sector and exchange labels are used historically (a declared D3
  limitation), and a weekend print after the signal date was possible. The weekend print was then checked
  (verification_completed weekend_print_after_signal_asof), and no in-window month was affected.
- The session permission classifier refused one subagent action, the v12 apply. The record reads: "factor-evaluator step 1 for v12 (git mv factors/candidates/zerotrade6M.py -> factors/accepted/ plus the factors/composite.py edit) was refused by the session permission classifier; repo unchanged, no stamp moved, no run started".
  The coordinator did not route around the refusal and waited for the owner, who then authorised the coordinator to
  make the moves and composite edits (docs/JOURNAL.md, research/CHANGELOG.md; table 10f).

**Corrections.** 15 findings were corrected append-only (Appendix B3). Among them, the timestamps of
events rows 219-419 were estimates rather than clock readings; their true bound is the commit that carries them.
Verifications and confirmed findings are in Appendices B4 and B5.

## 10. Orchestration

**Who did what.** The runner was the session model: Claude Fable 5.1 at bootstrap, Claude Opus 5.5 from the snapshot
recording on, with Claude Fable 5.1 as the advisor (docs/JOURNAL.md). Five subagents did the repeated work. In event
counts:

- osap-fetcher wrote the predictor specs (207 `spec_written`, one per non-seed predictor);
- sharadar-field-checker verified fields on this snapshot (27 `fields_verified`);
- sharadar-translator wrote the factor files (108 `factor_translated`: the 106
  candidates plus DelDRC, EarnSupBig, translated and then failed preflight);
- alpha-reviewer audited code (23);
- factor-evaluator checked provenance and wrote every record (132 `factor_evaluated`).

Preflight passes reconcile as follows. There are 105 `preflight_passed` events: 104 single-factor
events and one for BidAskSpreadFlip. The preflights of AM, Accruals are recorded inside their `factor_translated` events,
which RECORDS.md treats as an implied pass. The runner logged 51 judgment calls as `decision` events. The
event log has 1134 rows (Appendix B8).

**Runs.** 57 runs were started and 56 completed (Appendix B6). Run 046 was
aborted as superseded, with no result. The completed runs total 21.9 hours of wall time (`runtime_seconds`).
The runtimes of runs 003–011 sum to 6.17 h, while docs/JOURNAL.md states 4.9 h for Phase B; the
paper uses the event field.

*Table 10b_runtime_by_phase. Run wall time by phase (runs 001-002 bootstrap, 003-011 Phase B, 012-044 Phase D, 045-053 Phase E and D8, 054-057 holdout). Source: events `run_completed` runtime_seconds.*

| phase | runs completed | runtime h |
|---|---|---|
| 0 | 2 | 0.05 |
| B | 9 | 6.17 |
| D | 33 | 7.19 |
| E (D7, D8) | 8 | 5.80 |
| E (holdout) | 4 | 2.70 |

**Stamp moves** (Appendix B7). CONFIG moved once, before any run (1 `config_changed` with a SHA).
HARNESS moved 5 times: once for D11 before any run, twice for D7 and its fixes, once for the skip1
diagnostic and once for the rf diagnostic. None of these moves fell inside a declared ladder. DATA was recorded twice,
2 `snapshot_recorded` events: the first pull and the D8 refresh. COMPOSITE took
15 values (v0–v14), so it moved 14 times.

**Advisor and owner.** The event log records 6 advisor consultations: four ladder acceptances, the Phase D
to E boundary, and the D8 step-2 verdict. `docs/ORCHESTRATION.md` asks for more (every phase boundary); consultations not
logged cannot be verified from the record. The owner's inputs on record are:

- two verbatim answers to stop-and-ask questions, in events;
- one paraphrased resolution of a rule conflict (D11), in events;
- the v12 authorisation, recorded only as a paraphrase in docs/JOURNAL.md and research/CHANGELOG.md. The chat message
  itself is in no record file, so it is not quoted.

*Table 10e_advisor. Advisor consultations recorded in the event log. Source: events with an `advisor` field or 'Advisor consulted' in the decision text.*

| events line | ts | decision | record |
|---|---|---|---|
| 890 | 2026-10-01T06:07:17Z | ladder1_acceptance | decision text: 'Advisor consulted' |
| 945 | 2026-10-01T07:23:38Z | ladder2_acceptance | decision text: 'Advisor consulted' |
| 990 | 2026-10-01T09:01:52Z | ladder3_acceptance | decision text: 'Advisor consulted' |
| 1019 | 2026-10-01T11:06:45Z | ladder4_acceptance | decision text: 'Advisor consulted' |
| 1058 | 2026-10-01T15:57:46Z | phase_e_stage3_is_run_043 | consulted at D->E |
| 1107 | 2026-10-02T00:14:32Z | d8_step2_restatement_within_margin | consulted |

*Table 10f_owner. The owner's inputs as recorded. Source: events with a `verbatim` field, rule_conflict_found (resolved_by), and the docs/JOURNAL.md and research/CHANGELOG.md lines that record the v12 authorisation.*

| record | ts | subject | owner's input | form |
|---|---|---|---|---|
| 9 | 2026-09-30T16:11:08Z | rule_conflict_found D4_vs_D6_hedged_bars | owner in chat, 2026-09-30: Stage 1 bar reads the raw D10-D1, Stage 2 guard reads the hedged blend; no decile-monotonicity statistic | paraphrase in the record |
| 1097 | 2026-10-01T21:47:56Z | owner_stop_and_ask_3_approved | "approve both, use TB3MS for rf" | verbatim |
| 1109 | 2026-10-02T01:09:05Z | owner_stop_and_ask_5_approved | "Yes" | verbatim |
| docs/JOURNAL.md line 59 | 2026-10-01 (Phase D entry) | v12 apply after the permission denial | owner authorised the coordinator to do moves and composite edits | paraphrase; the chat message is not in any record file |
| research/CHANGELOG.md line 201 |  | v12 apply | Applied by the coordinator (owner-authorised) | paraphrase |

## 11. Limitations, and what a next pre-registration would change

These limitations follow from the record. The proposals describe what would be declared differently; none was run.

**Limitations.**

- *The hedged headline is not a market-neutral return.* Its hedge term includes the rf credit, which flatters it
  (-2.26 pp/yr out of sample). Its trailing β lagged the holdout's realised β by about 0.29, which
  left residual short exposure in a rising market. The raw spread is not neutral either: its realised holdout β is
  -0.836 (run 055). The corrected readings are the excess-of-rf series (8.54%/yr, Sharpe
  0.413, NW t 0.93; run 054) and the β-neutral layer (0.74%/yr gross; run 057).
- *The holdout is short and concentrated.* At 57 months it is below the harness's own 120-month floor.
  One year carries the IC, and the ex-top-3 diagnostic is mechanical on 5 calendar years.
- *The holdout does not test the construction changes* (D2, Section 8).
- *The holdout was isolated by rule, not by data* (Section 2). The first snapshot held those months.
- *Sector labels are current, not point in time* (D3). This touches every leg's rank, and the industry-built predictors
  through current SIC (decision current_sic_signal_values).
- *The seed legs were never screened.* Their in-window standalone ICs (run 051, signal-close base, pre-refresh bytes) are:
  Size -0.0093 (t -1.53), Value 0.0058 (t 0.85), Investment
  0.0054 (t 1.21) and Momentum 0.0096 (t 1.27). Only
  Profitability (0.0205, t 3.78) would clear the Stage 1 t bar. By
  pre-registration the seeds anchor five of the nine families, and Size alone is the size family.
- *The family partition was chosen with Stage 1 numbers visible* (decision phase_c_family_partition, disclosed). It was
  fixed before any Stage 2 number.
- *Multiple testing is controlled only by the bar levels.* Under the global null about one Stage 1 false pass and about
  half a Stage 2 false acceptance are expected (table 03d). No family-wise or false-discovery correction was
  pre-registered.
- *Acceptance-time and spend-snapshot figures differ slightly* (table 02c). Every verdict was taken on the frozen bytes;
  the rungs were not re-run on the refreshed bytes.
- *Costs.* No cost enters selection. Measured costs exceed the layer's gross return, and the spread measure may overstate
  costs for liquid names (a judgment, Section 7). The risk model underpredicts by more than a factor of two, and the
  layer's gross return faded after 2002.
- *About 11% of the in-window IC arrives on the first trading day* of the holding month (run 051,
  pre-refresh bytes).
- *Record defects, disclosed:*
  - estimated event timestamps on rows 219-419;
  - the mis-pointed v1 tag;
  - the missing Stage 3 holdout cuts;
  - the missing tiers and deciles in run 054's holdout cut;
  - the Phase B runtime, stated differently in the journal and the events;
  - the skip1 finding text's rounding (Appendix B5).

**Not tested.**

- The 101 frontier predictors (Appendix A2).
- Any screen of GrLTNOAFlip.
- Any decile-monotonicity statistic (declined by the owner, D11).
- Any alternative hedge proxy, stock-level β, or excess-of-rf guard as a bar.
- Any holding period other than one month.
- Any universe outside US common stock on NYSE, NASDAQ and NYSEMKT.
- Any walk-forward of the selection rules on this snapshot.
- Any Stage 3 variant's holdout Sharpe.
- Any re-run of the Stage 2 rungs on the refreshed bytes.
- Any tuning of the layer after the spend.

**What a next pre-registration would change, described not tuned.**

- Declare the hedge as excess of rf, with a β estimate whose tracking error is itself reported.
- Require every holdout-reading run (Stage 3 and the layer) to emit holdout cuts, and test that before the spend.
- Hold the holdout months out of the decision snapshot, or record their isolation as a tested property.
- Use point-in-time sector labels.
- Screen the seed legs, or justify each.
- Fix the family partition rule before Stage 1 runs.
- Declare the return-start convention, with the skip1 base as a reported sensitivity.
- Pre-register a spread measure without the zero floor, and a risk-model calibration check.
- State the holdout's power before choosing its length.
- Tag a version only after `git rev-parse HEAD` shows the version commit.

## Appendix A1. The full registry

*Table A1_registry. The full registry, 112 rows (five seed legs carry no screen). Source: research/registry_index.yaml (derived from research/registry/*.yaml) and `stage2_run` from the rows. Acceptance-time, pre-refresh bytes.*

| name | status | batch | Stage 1 run | Stage 2 run | family | IC | IC NW t | raw LS %/yr | hedged LS %/yr | hedged Sharpe | coverage % | beta | Sharpe ex top-3 | resid t | guard t | decided by |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Accruals | rejected | stage1_b1 | 003 |  |  | 0.0048 | 1.84 | 2.92 | 2.49 | 0.329 | 76.7 | 0.04 | 0.107 |  |  | ic_tstat_nw |
| AM | rejected | stage1_b1 | 003 |  |  | 0.0098 | 1.26 | 4.72 | -3.17 | -0.149 | 99.6 | 0.34 | -0.449 |  |  | ic_tstat_nw |
| AnnouncementReturn | rejected | stage1_b1 | 003 |  |  | 0.0092 | 2.28 | 2.51 | 5.19 | 0.643 | 66.5 | -0.21 | 0.342 |  |  | ic_tstat_nw |
| Beta | rejected | stage1_b1 | 003 |  |  | -0.0091 | -0.97 | 1.12 | -10.31 | -0.608 | 85.4 | 1.11 | -0.974 |  |  | ic_tstat_nw |
| BetaFP | rejected | stage1_b1 | 003 |  |  | -0.0123 | -1.28 | 1.13 | -11.48 | -0.655 | 83.1 | 1.22 | -1.03 |  |  | ic_tstat_nw |
| BetaLiquidityPS | rejected | stage1_b1 | 003 |  |  | -0.0008 | -0.27 | -0.57 | -1.3 | -0.173 | 67.2 | 0.11 | -0.621 |  |  | ic_tstat_nw |
| BetaTailRisk | rejected | stage1_b1 | 003 |  |  | -0.0006 | -0.06 | 1.09 | -8.79 | -0.766 | 60.2 | 0.78 | -1.236 |  |  | ic_tstat_nw |
| BidAskSpread | rejected | stage1_b1 | 003 |  |  | -0.0205 | -2.77 | -0.94 | -8.63 | -0.482 | 99.1 | 0.97 | -0.889 |  |  | ic_tstat_nw |
| BidAskSpreadFlip | rejected | stage1_b9 | 011 | 044 | liquidity | 0.0206 | 2.76 | 1.07 | 8.72 | 0.485 | 99.1 | -0.98 | 0.295 | 1.77 | 0.43 | resid_ic_tstat_nw |
| BMdec | rejected | stage1_b1 | 003 |  |  | 0.0045 | 0.82 | 3.68 | 0.61 | 0.054 | 92.1 | -0.03 | -0.423 |  |  | ic_tstat_nw |
| BookLeverage | rejected | stage1_b1 | 003 |  |  | -0.0096 | -2.59 | -3.63 | -1.29 | -0.13 | 99.6 | -0.04 | -0.398 |  |  | ic_tstat_nw |
| BPEBM | rejected | stage1_b1 | 003 |  |  | -0.0092 | -2.06 | 0.39 | -0.38 | -0.036 | 75.6 | 0.23 | -0.448 |  |  | ic_tstat_nw |
| Cash | rejected | stage1_b2 | 004 |  |  | -0.0091 | -1.86 | -0.57 | -0.24 | -0.017 | 99.6 | 0.33 | -0.426 |  |  | ic_tstat_nw |
| CashProd | rejected | stage1_b2 | 004 |  |  | 0.003 | 0.47 | 3.74 | -1.75 | -0.127 | 99.2 | 0.26 | -0.483 |  |  | ic_tstat_nw |
| CBOperProf | accepted | stage1_b1 | 003 | 012 | profitability | 0.0209 | 3.74 | 7.24 | 11.24 | 0.901 | 73.4 | -0.57 | 0.638 | 3.02 | 0.95 | all bars |
| CF | rejected | stage1_b2 | 004 | 032 | value | 0.0201 | 3.03 | 3.32 | 2.75 | 0.179 | 96.1 | -0.29 | -0.169 | 1.02 | -0.76 | resid_ic_tstat_nw |
| cfp | accepted | stage1_b9 | 011 | 012 | value | 0.0246 | 3.65 | 9.45 | 7.47 | 0.51 | 95.7 | -0.13 | 0.246 | 2.97 | 2.19 | all bars |
| ChAssetTurnover | rejected | stage1_b2 | 004 |  |  | 0.0058 | 2.24 | 2.37 | 2.39 | 0.376 | 83.4 | -0.06 | 0.136 |  |  | ic_tstat_nw |
| ChEQ | rejected | stage1_b2 | 004 |  |  | 0.0057 | 1.4 | 7.66 | 5.17 | 0.455 | 91.2 | 0.02 | 0.092 |  |  | ic_tstat_nw |
| ChInv | rejected | stage1_b2 | 004 |  |  | 0.0052 | 1.51 | 5.14 | 5.65 | 0.649 | 60.3 | -0.1 | 0.359 |  |  | ic_tstat_nw |
| ChInvIA | rejected | stage1_b2 | 004 |  |  | 0.0009 | 0.36 | 4.04 | 3.69 | 0.564 | 87.2 | -0.11 | 0.331 |  |  | ic_tstat_nw |
| ChNNCOA | rejected | stage1_b2 | 004 |  |  | 0.0094 | 4.15 | 4.81 | 4.49 | 0.656 | 77.2 | -0.07 | 0.233 |  |  | ic_mean |
| ChNWC | rejected | stage1_b2 | 004 |  |  | 0.0042 | 2.04 | 1.15 | 1.35 | 0.221 | 77.0 | -0.02 | 0.035 |  |  | ic_tstat_nw |
| ChTax | rejected | stage1_b2 | 004 |  |  | 0.0048 | 1.42 | 0.09 | 1.02 | 0.128 | 87.1 | -0.03 | -0.161 |  |  | ic_tstat_nw |
| CompEquIss | rejected | stage1_b2 | 004 |  |  | 0.0119 | 2.44 | 3.62 | 5.25 | 0.614 | 65.1 | -0.06 | 0.375 |  |  | ic_tstat_nw |
| CompositeDebtIssuance | rejected | stage1_b2 | 004 |  |  | 0.0046 | 1.49 | 1.33 | 2.81 | 0.319 | 46.2 | -0.11 | -0.018 |  |  | ic_tstat_nw |
| CoskewACX | rejected | stage1_b3 | 005 |  |  | 0.0062 | 1.65 | 2.78 | 1.25 | 0.11 | 91.1 | 0.22 | -0.118 |  |  | ic_tstat_nw |
| Coskewness | rejected | stage1_b3 | 005 |  |  | 0.0068 | 1.65 | 1.61 | -0.52 | -0.045 | 91.1 | 0.33 | -0.229 |  |  | ic_tstat_nw |
| DelCOA | rejected | stage1_b3 | 005 |  |  | 0.0009 | 0.26 | 4.97 | 4.91 | 0.583 | 77.3 | -0.07 | 0.195 |  |  | ic_tstat_nw |
| DelCOL | rejected | stage1_b3 | 005 |  |  | -0.0035 | -0.92 | 0.81 | 0.36 | 0.04 | 77.1 | -0.06 | -0.287 |  |  | ic_tstat_nw |
| DelEqu | rejected | stage1_b3 | 005 |  |  | 0.0052 | 1.25 | 6.06 | 3.53 | 0.333 | 95.2 | 0.0 | 0.008 |  |  | ic_tstat_nw |
| DelFINL | rejected | stage1_b3 | 005 |  |  | 0.0039 | 1.36 | 2.26 | 3.53 | 0.451 | 69.6 | -0.18 | 0.112 |  |  | ic_tstat_nw |
| DelNetFin | rejected | stage1_b3 | 005 |  |  | 0.0025 | 1.08 | 1.07 | 2.22 | 0.317 | 77.2 | -0.0 | -0.237 |  |  | ic_tstat_nw |
| dNoa | rejected | stage1_b9 | 011 |  |  | 0.0077 | 2.19 | 7.74 | 6.62 | 0.817 | 95.2 | -0.07 | 0.395 |  |  | ic_tstat_nw |
| DolVol | rejected | stage1_b3 | 005 |  |  | -0.0008 | -0.18 | 3.69 | 1.65 | 0.165 | 99.5 | -0.01 | -0.119 |  |  | ic_tstat_nw |
| EarningsConsistency | rejected | stage1_b3 | 005 |  |  | 0.009 | 2.6 | -0.13 | 2.92 | 0.338 | 43.3 | -0.18 | 0.183 |  |  | ic_mean |
| EarningsSurprise | rejected | stage1_b3 | 005 |  |  | 0.0048 | 1.63 | 1.33 | 2.32 | 0.324 | 86.2 | -0.09 | 0.051 |  |  | ic_tstat_nw |
| EBM | rejected | stage1_b3 | 005 |  |  | 0.0018 | 0.42 | 3.22 | 0.3 | 0.032 | 75.6 | 0.24 | -0.331 |  |  | ic_tstat_nw |
| EntMult | rejected | stage1_b4 | 006 |  |  | 0.0134 | 1.96 | 5.55 | 2.85 | 0.194 | 65.9 | -0.08 | -0.127 |  |  | ic_tstat_nw |
| EP | rejected | stage1_b3 | 005 |  |  | 0.0055 | 0.96 | 3.53 | 1.76 | 0.17 | 75.1 | -0.05 | -0.12 |  |  | ic_tstat_nw |
| EquityDuration | rejected | stage1_b4 | 006 |  |  | 0.0104 | 1.86 | 2.33 | 2.98 | 0.253 | 94.7 | -0.3 | -0.061 |  |  | ic_tstat_nw |
| GP | accepted | stage1_b4 | 006 | 023 | profitability | 0.0155 | 3.52 | 8.64 | 11.34 | 1.091 | 74.4 | -0.45 | 0.921 | 2.74 | 0.43 | all bars |
| grcapx | rejected | stage1_b9 | 011 |  |  | 0.0041 | 1.37 | 4.02 | 3.4 | 0.488 | 81.0 | -0.08 | 0.263 |  |  | ic_tstat_nw |
| grcapx3y | rejected | stage1_b9 | 011 |  |  | 0.0028 | 0.89 | 3.97 | 3.42 | 0.446 | 72.3 | -0.04 | 0.233 |  |  | ic_tstat_nw |
| GrLTNOA | rejected | stage1_b4 | 006 |  |  | -0.0059 | -2.75 | -0.08 | -0.76 | -0.114 | 76.8 | 0.04 | -0.491 |  |  | ic_tstat_nw |
| GrSaleToGrInv | rejected | stage1_b4 | 006 |  |  | 0.0035 | 1.58 | 1.62 | 1.59 | 0.217 | 57.1 | -0.01 | -0.167 |  |  | ic_tstat_nw |
| GrSaleToGrOverhead | rejected | stage1_b4 | 006 |  |  | -0.002 | -0.75 | -3.04 | -2.73 | -0.394 | 85.1 | -0.04 | -0.549 |  |  | ic_tstat_nw |
| Herf | rejected | stage1_b4 | 006 |  |  | -0.0028 | -1.15 | 0.03 | -0.79 | -0.106 | 91.5 | 0.04 | -0.326 |  |  | ic_tstat_nw |
| HerfAsset | rejected | stage1_b4 | 006 |  |  | -0.0049 | -2.0 | -0.59 | -1.45 | -0.182 | 91.6 | 0.06 | -0.432 |  |  | ic_tstat_nw |
| HerfBE | rejected | stage1_b4 | 006 |  |  | -0.003 | -1.21 | 0.28 | -0.44 | -0.061 | 91.6 | -0.03 | -0.33 |  |  | ic_tstat_nw |
| High52 | rejected | stage1_b4 | 006 |  |  | 0.0065 | 0.77 | -0.13 | 9.38 | 0.448 | 96.1 | -1.01 | 0.255 |  |  | ic_tstat_nw |
| IdioVol3F | accepted | stage1_b4 | 006 | 032 | volatility | 0.0229 | 3.15 | 3.28 | 10.1 | 0.536 | 96.7 | -0.98 | 0.374 | 2.03 | 0.89 | all bars |
| IdioVolAHT | rejected | stage1_b4 | 006 | 044 | volatility | 0.0238 | 2.63 | 3.89 | 11.68 | 0.545 | 96.8 | -1.07 | 0.389 | 1.92 | 0.06 | resid_ic_tstat_nw |
| Illiquidity | rejected | stage1_b5 | 007 |  |  | -0.0064 | -1.19 | 4.31 | 1.13 | 0.078 | 96.4 | 0.29 | -0.137 |  |  | ic_tstat_nw |
| IntanBM | rejected | stage1_b5 | 007 |  |  | -0.0003 | -0.04 | 4.34 | -3.54 | -0.228 | 61.1 | 0.56 | -0.837 |  |  | ic_tstat_nw |
| IntanCFP | rejected | stage1_b5 | 007 |  |  | -0.0033 | -0.4 | 4.67 | -4.35 | -0.263 | 62.9 | 0.65 | -0.798 |  |  | ic_tstat_nw |
| IntanEP | rejected | stage1_b5 | 007 |  |  | -0.0045 | -0.55 | 4.58 | -4.31 | -0.258 | 62.9 | 0.64 | -0.798 |  |  | ic_tstat_nw |
| IntanSP | rejected | stage1_b5 | 007 |  |  | -0.0052 | -0.62 | 5.2 | -3.97 | -0.233 | 62.9 | 0.67 | -0.772 |  |  | ic_tstat_nw |
| IntMom | rejected | stage1_b5 | 007 |  |  | 0.0031 | 0.5 | -1.12 | 2.24 | 0.151 | 95.4 | -0.18 | -0.117 |  |  | ic_tstat_nw |
| Investment | baseline | BASELINE | 001 |  | investment |  |  |  |  |  |  |  |  |  |  |  |
| InvestmentTWX | rejected | stage1_b5 | 007 |  |  | 0.0003 | 0.15 | 2.68 | 1.98 | 0.342 | 78.7 | 0.03 | 0.097 |  |  | ic_tstat_nw |
| InvGrowth | rejected | stage1_b5 | 007 |  |  | 0.0055 | 1.56 | 3.5 | 3.82 | 0.386 | 51.7 | -0.14 | 0.009 |  |  | ic_tstat_nw |
| Leverage | rejected | stage1_b5 | 007 |  |  | 0.0125 | 1.71 | 7.09 | -0.5 | -0.025 | 99.6 | 0.3 | -0.342 |  |  | ic_tstat_nw |
| LRreversal | rejected | stage1_b5 | 007 |  |  | -0.008 | -1.29 | 2.84 | -0.97 | -0.068 | 78.9 | 0.09 | -0.381 |  |  | ic_tstat_nw |
| MaxRet | accepted | stage1_b5 | 007 | 023 | volatility | 0.0233 | 3.42 | 4.17 | 10.57 | 0.611 | 99.8 | -0.86 | 0.544 | 4.01 | 1.75 | all bars |
| MeanRankRevGrowth | rejected | stage1_b6 | 008 |  |  | -0.0005 | -0.12 | 2.23 | 0.76 | 0.093 | 46.6 | 0.1 | -0.225 |  |  | ic_tstat_nw |
| Mom12mOffSeason | rejected | stage1_b6 | 008 |  |  | 0.0084 | 1.24 | 7.08 | 13.34 | 0.583 | 96.4 | -0.35 | 0.418 |  |  | ic_tstat_nw |
| Mom6m | rejected | stage1_b6 | 008 |  |  | 0.0077 | 1.24 | 6.47 | 12.93 | 0.616 | 98.2 | -0.47 | 0.449 |  |  | ic_tstat_nw |
| Momentum | baseline | BASELINE | 001 |  | momentum |  |  |  |  |  |  |  |  |  |  |  |
| MomOffSeason | rejected | stage1_b6 | 008 |  |  | -0.0052 | -0.97 | 2.23 | 1.19 | 0.113 | 66.6 | 0.05 | -0.208 |  |  | ic_tstat_nw |
| MomOffSeason06YrPlus | rejected | stage1_b6 | 008 |  |  | 0.0065 | 1.76 | 1.45 | 1.64 | 0.268 | 40.6 | 0.01 | -0.063 |  |  | ic_tstat_nw |
| MomSeason | rejected | stage1_b6 | 008 |  |  | 0.002 | 0.58 | -0.27 | 0.17 | 0.022 | 66.1 | 0.0 | -0.221 |  |  | ic_tstat_nw |
| MomSeason06YrPlus | rejected | stage1_b6 | 008 |  |  | 0.0069 | 1.9 | 0.21 | 0.12 | 0.018 | 40.3 | -0.0 | -0.287 |  |  | ic_tstat_nw |
| MomSeasonShort | rejected | stage1_b6 | 008 |  |  | 0.0013 | 0.28 | -0.44 | 1.02 | 0.096 | 96.1 | 0.02 | -0.345 |  |  | ic_tstat_nw |
| MRreversal | rejected | stage1_b5 | 007 |  |  | -0.0043 | -0.96 | 3.69 | 0.62 | 0.051 | 91.0 | 0.09 | -0.2 |  |  | ic_tstat_nw |
| NetDebtFinance | rejected | stage1_b6 | 008 |  |  | 0.0034 | 1.38 | 2.25 | 2.95 | 0.455 | 88.1 | -0.16 | 0.163 |  |  | ic_tstat_nw |
| NetEquityFinance | rejected | stage1_b6 | 008 | 032 | external_financing | 0.0166 | 3.03 | 4.54 | 7.02 | 0.601 | 93.9 | -0.52 | 0.434 | 1.4 | 0.47 | resid_ic_tstat_nw |
| NetPayoutYield | rejected | stage1_b6 | 008 | 044 | value | 0.0145 | 2.6 | 4.92 | 6.87 | 0.542 | 65.5 | -0.41 | 0.302 | 0.12 | 0.06 | resid_ic_tstat_nw |
| NOA | rejected | stage1_b6 | 008 |  |  | 0.0016 | 0.62 | 8.64 | 7.92 | 0.907 | 77.3 | -0.02 | 0.605 |  |  | ic_tstat_nw |
| OperProfRD | rejected | stage1_b7 | 009 | 032 | profitability | 0.0192 | 3.18 | 6.44 | 10.94 | 0.733 | 70.7 | -0.6 | 0.452 | -0.42 | 0.92 | resid_ic_tstat_nw |
| OPLeverage | rejected | stage1_b7 | 009 |  |  | 0.0087 | 2.89 | 4.09 | 3.46 | 0.429 | 85.4 | -0.1 | 0.153 |  |  | ic_mean |
| OrgCap | rejected | stage1_b7 | 009 |  |  | 0.0054 | 1.7 | 4.21 | 4.36 | 0.401 | 50.4 | 0.08 | 0.194 |  |  | ic_tstat_nw |
| PctAcc | accepted | stage1_b7 | 009 | 012 | investment | 0.0112 | 4.03 | 4.74 | 4.15 | 0.672 | 95.6 | -0.04 | 0.462 | 4.67 | 0.09 | all bars |
| PctTotAcc | rejected | stage1_b7 | 009 |  |  | 0.0022 | 0.91 | 2.48 | 2.16 | 0.377 | 95.6 | -0.08 | 0.187 |  |  | ic_tstat_nw |
| Price | rejected | stage1_b7 | 009 |  |  | -0.01 | -1.41 | 2.98 | -5.89 | -0.315 | 100.0 | 0.77 | -0.766 |  |  | ic_tstat_nw |
| PriceDelayRsq | rejected | stage1_b7 | 009 |  |  | -0.007 | -2.12 | -1.09 | 0.01 | 0.001 | 87.8 | -0.17 | -0.232 |  |  | ic_tstat_nw |
| PriceDelaySlope | rejected | stage1_b7 | 009 |  |  | -0.0055 | -1.69 | -0.6 | -2.93 | -0.42 | 87.8 | 0.23 | -0.816 |  |  | ic_tstat_nw |
| PriceDelayTstat | rejected | stage1_b7 | 009 |  |  | -0.0055 | -1.68 | -0.59 | -2.93 | -0.419 | 87.8 | 0.23 | -0.809 |  |  | ic_tstat_nw |
| Profitability | baseline | BASELINE | 001 |  | profitability |  |  |  |  |  |  |  |  |  |  |  |
| RealizedVol | rejected | stage1_b7 | 009 | 037 | volatility | 0.0234 | 2.81 | 3.39 | 12.13 | 0.607 | 99.8 | -1.16 | 0.479 | 1.73 | -0.61 | resid_ic_tstat_nw |
| ResidualMomentum | rejected | stage1_b7 | 009 |  |  | 0.0035 | 0.72 | 1.76 | 4.92 | 0.466 | 67.4 | -0.24 | 0.187 |  |  | ic_tstat_nw |
| ReturnSkew | rejected | stage1_b7 | 009 |  |  | 0.005 | 2.22 | 0.4 | 0.45 | 0.066 | 99.8 | -0.03 | -0.269 |  |  | ic_tstat_nw |
| ReturnSkew3F | rejected | stage1_b8 | 010 |  |  | 0.0007 | 0.35 | -1.34 | -1.93 | -0.307 | 96.7 | 0.02 | -0.679 |  |  | ic_tstat_nw |
| RevenueSurprise | rejected | stage1_b8 | 010 |  |  | 0.0094 | 2.78 | 1.82 | 2.59 | 0.347 | 86.6 | -0.05 | 0.093 |  |  | ic_mean |
| roaq | accepted | stage1_b9 | 011 | 023 | profitability | 0.0208 | 3.37 | 5.28 | 9.95 | 0.705 | 96.3 | -0.58 | 0.386 | 3.73 | 1.95 | all bars |
| RoE | accepted | stage1_b8 | 010 | 023 | profitability | 0.0192 | 3.34 | 2.95 | 7.38 | 0.532 | 93.1 | -0.59 | 0.372 | 2.41 | -1.26 | all bars |
| ShareIss1Y | rejected | stage1_b8 | 010 | 023 | external_financing | 0.0165 | 3.52 | 7.12 | 9.06 | 0.909 | 90.5 | -0.38 | 0.742 | 1.88 | 0.17 | resid_ic_tstat_nw |
| ShareIss5Y | accepted | stage1_b8 | 010 | 012 | external_financing | 0.0158 | 3.67 | 4.88 | 8.23 | 1.085 | 62.6 | -0.24 | 0.749 | 3.61 | 2.83 | all bars |
| Size | baseline | BASELINE | 001 |  | size |  |  |  |  |  |  |  |  |  |  |  |
| SP | rejected | stage1_b8 | 010 |  |  | 0.0182 | 2.5 | 9.21 | 2.79 | 0.145 | 96.1 | 0.18 | -0.201 |  |  | ic_tstat_nw |
| STreversal | accepted | stage1_b8 | 010 | 032 | short_term_reversal | 0.0145 | 2.96 | 3.37 | -0.48 | -0.029 | 99.8 | 0.44 | -0.369 | 3.81 | -0.54 | all bars |
| TotalAccruals | rejected | stage1_b8 | 010 |  |  | -0.0 | -0.01 | 1.47 | -0.7 | -0.093 | 94.6 | 0.12 | -0.361 |  |  | ic_tstat_nw |
| TrendFactor | accepted | stage1_b8 | 010 | 037 | momentum | 0.0171 | 2.79 | 10.12 | 8.94 | 0.523 | 68.7 | 0.05 | 0.276 | 2.14 | -0.01 | all bars |
| Value | baseline | BASELINE | 001 |  | value |  |  |  |  |  |  |  |  |  |  |  |
| VarCF | rejected | stage1_b8 | 010 |  |  | 0.0064 | 0.76 | -3.97 | 5.59 | 0.406 | 60.7 | -0.79 | 0.174 |  |  | ic_tstat_nw |
| VolMkt | rejected | stage1_b8 | 010 |  |  | 0.0161 | 2.25 | 2.38 | 9.55 | 0.551 | 97.1 | -0.94 | 0.32 |  |  | ic_tstat_nw |
| VolSD | rejected | stage1_b8 | 010 |  |  | 0.0112 | 2.36 | 1.95 | 6.05 | 0.534 | 79.8 | -0.47 | 0.398 |  |  | ic_tstat_nw |
| VolumeTrend | accepted | stage1_b9 | 011 | 037 | liquidity | 0.0114 | 2.87 | 2.4 | 5.05 | 0.661 | 66.3 | -0.23 | 0.331 | 2.04 | -0.09 | all bars |
| XFIN | accepted | stage1_b9 | 011 | 012 | external_financing | 0.017 | 3.57 | 6.57 | 8.61 | 0.734 | 95.6 | -0.47 | 0.484 | 3.27 | -0.64 | all bars |
| zerotrade12M | rejected | stage1_b9 | 011 | 037 | liquidity | 0.018 | 2.83 | 3.69 | 8.97 | 0.692 | 94.7 | -0.7 | 0.449 | 0.49 | 0.14 | resid_ic_tstat_nw |
| zerotrade1M | rejected | stage1_b9 | 011 | 044 | liquidity | 0.0155 | 2.63 | 2.56 | 6.89 | 0.441 | 99.4 | -0.73 | 0.281 | -1.28 | 0.11 | resid_ic_tstat_nw |
| zerotrade6M | accepted | stage1_b9 | 011 | 037 | liquidity | 0.0185 | 2.93 | 4.19 | 8.92 | 0.602 | 97.6 | -0.73 | 0.427 | 2.69 | 1.72 | all bars |

## Appendix A2. The frontier

*Table A2_frontier. The frontier: every OSAP predictor not tested, 101 rows. Source: osap_source/osap_frontier.yaml `excluded`.*

| OSAP acronym | class | date | reason (record text) |
|---|---|---|---|
| AbnormalAccruals | data_unavailable | 2026-09-30 | needs compustat.ppegt (gross PP&E) as a Jones-model regressor; SF1 has only ppnenet; OSAP does not zero-fill ppegt, so the rule makes it infeasible (net-for-gross substitution not adopted) |
| AccrualsBM | data_unavailable | 2026-09-30 | needs compustat.txp (income taxes payable); no SF1 column (112 checked; taxliabilities is total tax liabilities); AccrualsBM uses raw txp and txp is not in OSAP zero_fill_vars, so the rule makes it infeasible |
| Activism1 | data_unavailable | 2026-09-30 | GIM governance index G (external spreadsheet, ends 2007-01, no Sharadar source) and 13F maxinstown_perc (SF3 from 2013-06-30): supports disjoint, zero scoreable months |
| Activism2 | data_unavailable | 2026-09-30 | GIM governance index G (external, ends 2007-01, no Sharadar source) and 13F largest-holder share (SF3 from 2013-06-30): supports disjoint, zero scoreable months |
| AdExp | data_unavailable | 2026-09-30 | needs compustat.xad (advertising expense); no SF1 column among 112 (sgna/opex are aggregates); AdExp uses raw xad, not zero-filled, so no approx route |
| AgeIPO | data_unavailable | 2026-09-30 | needs FoundingYear and IPO dates from Ritter's external IPO-age file (PERMNO-keyed); no Sharadar field or crosswalk; not zero-filled. TICKERS.firstpricedate would measure listing recency, a different signal |
| AnalystRevision | data_unavailable | 2026-09-30 | only input is IBES consensus meanest (fpi 1); no Sharadar table carries estimates; not a Compustat item, no zero-fill |
| AnalystValue | data_unavailable | 2026-09-30 | requires IBES analyst forecasts (feps1, feps2, LTG); no Sharadar table carries estimates; the source drops firms without forecasts (no zero-fill) |
| AOP | data_unavailable | 2026-09-30 | requires IBES analyst forecasts (feps1, feps2, LTG); no Sharadar table carries estimates; the source drops firms without forecasts (no zero-fill) |
| betaVIX | data_unavailable | 2026-09-30 | needs daily VIX (or VXO) changes; ^VIX exists only under Sharadar table SFP, which is mapped but not held (adding it moves DATA_SHA, stop-and-ask 3); no held table carries a volatility index; OSAP inner-joins the VIX series (no zero-fill) |
| BrandInvest | data_unavailable | 2026-09-30 | needs compustat.xad (advertising) for BrandCapital; no SF1 column; xad is not in OSAP zero_fill_vars and BrandCapital is NaN where xad is NaN (xad0 zero-fill does not reach the denominator) |
| ChangeInRecommendation | data_unavailable | 2026-09-30 | IBES analyst recommendation code (ireccd); no Sharadar recommendations/estimates table; no zero-fill; no proxy |
| ChForecastAccrual | data_unavailable | 2026-09-30 | sign of the monthly change in IBES consensus EPS (meanest, fpi 1); no Sharadar estimates table; not zero-filled (NaN without it); the accruals gate also needs txp (unavailable) |
| ChNAnalyst | data_unavailable | 2026-09-30 | change in IBES analyst count (numest, fpi 1); no Sharadar estimates table; NaN when numest or its lag is missing (no zero-fill) |
| CitationsRD | data_unavailable | 2026-09-30 | numerator is NBER patent citations (ncitscale), not published by Sharadar; OSAP's fillna(0) fills gaps in that panel, so dropping it makes the signal a constant; the panel ends 2006 |
| ConsRecomm | data_unavailable | 2026-09-30 | mean IBES recommendation code (ireccd); no Sharadar recommendations table; no zero-fill or optional term |
| ConvDebt | data_unavailable | 2026-09-30 | needs convertible debt (dc from dcvt/dcpstk) and cshrc; neither in any held table; OSAP zero-fills dc but not cshrc; dropping both leaves a constant 0 |
| CPVolSpread | data_unavailable | 2026-09-30 | OptionMetrics call minus put implied volatility; Sharadar publishes no options data; OSAP drops missing rows (no zero-fill) |
| CredRatDG | data_unavailable | 2026-09-30 | needs S&P credrat / Capital IQ downgrade history; Sharadar has no ratings column or EVENTS proxy; OSAP's fillna(0) fills no-downgrade months, not an input term, so dropping ratings leaves a constant 0 |
| CustomerMomentum | data_unavailable | 2026-09-30 | needs Compustat Segment customer names and the CCM link; the customer link is the signal; not in Sharadar |
| dCPVolSpread | data_unavailable | 2026-09-30 | needs OptionMetrics call and put implied volatility; no held Sharadar table carries option data; OSAP leaves NaN (no zero-fill) |
| DebtIssuance | data_unavailable | 2026-09-30 | needs gross long-term debt issuance (dltis); SF1 has only net ncfdebt (a different event: net borrower incl. commercial paper); dltis not in OSAP zero_fill_vars |
| DelBreadth | data_start | 2026-09-30 | constructible from 13F (SF3 investor-level or SF3A shrholders) but 13F starts 2013-06-30: 97 decision months with a 45-day point-in-time lag (2013-12..2021-12), below rebalance.min_months 120, so Stage 1 is inconclusive by construction; would also need a new 13F MonthContext accessor and field_map keys |
| DelDRC | preflight_failed | 2026-09-30 | coverage: 9.7% / 27.4% / 28.0% of the universe at the 1998-12 / 2010-06 / 2021-11 probes, under the 40% Stage 1 bar at every probe; structural, from OSAP's own filters kept unweakened (non-financial by SIC, equity > 0, revenue >= $5M, deferred revenue non-zero at one end at least); file kept at factors/preflight_failed/DelDRC.py |
| DelLTI | preflight_failed | 2026-09-30 | mass point: change in long-term investments (investmentsnc) is exactly 0 for 50.7-59.9% of scored names (40-46% of the universe; OSAP's ivao zero-fill makes the same block), far above the 10% cliff; the standing tie rule (level 0 at both ends -> NaN) leaves 30.7-39.5% coverage, under the 40% Stage 1 bar |
| DivInit | preflight_failed | 2026-09-30 | binary dividend-initiation flag: 98.7% of the universe is 0 (24.7 ones per month on average; 181 of 263 usable months have < 30 ones), so qcut gives 2 bins and the mode breaches the 10% cliff; a rare-event signal needs an event-study harness the pre-registered design does not have. Also: CRSP distcd filter not reproducible (ACTIONS 'dividend' rows would substitute) |
| DivOmit | preflight_failed | 2026-09-30 | binary dividend-omission flag: 99.6% of the universe is 0 (7.2 ones per month on average, 206 of 265 months < 10, 3 months with none); mode breaches the 10% cliff, qcut collapses; same distcd caveat as DivInit |
| DivSeason | preflight_failed | 2026-09-30 | binary seasonal-dividend flag: 71.5-78.7% of scored names are 0 (scored = payers within 12 months, ~52% of the universe), so qcut gives 2 bins and the mode breaches the 10% cliff; measured on 46 of 276 decision months (every 6th) by osap-fetcher. Also approx data: CRSP distribution codes cd1-cd3 have no Sharadar field (ACTIONS 'dividend' rows substitute) |
| DivYieldST | preflight_failed | 2026-09-30 | predicted-dividend-yield tercile code in {0,1,2,3}: 76.0-83.5% of scored names are 0, so qcut gives at most 4 bins and the mode breaches the 10% cliff; measured on 46 of 276 decision months by osap-fetcher. Same ACTIONS-for-CRSP-distcd substitution as DivSeason |
| DownRecomm | data_unavailable | 2026-09-30 | needs IBES recommendation history (downgrades); no Sharadar table carries analyst recommendations; not an OSAP zero-fill item; 0 of 276 months constructible |
| dVolCall | data_unavailable | 2026-09-30 | needs OptionMetrics 30-day 50-delta call implied volatility; no held Sharadar table carries option data (SF3A call holdings are 13F positions); OSAP does not zero-fill it |
| dVolPut | data_unavailable | 2026-09-30 | needs OptionMetrics 30-day 50-delta put implied volatility; not in Sharadar; OSAP does not zero-fill it |
| EarningsForecastDisparity | data_unavailable | 2026-09-30 | every input is IBES (meanest FY1, long-term growth fgr5yr, fy0a); no analyst data in Sharadar; not zero-filled by OSAP |
| EarningsStreak | data_unavailable | 2026-09-30 | inputs actual, meanest, price, anndats_act, statpers from IBES_EPS_Adj (analyst surprise streak); not in Sharadar; not zero-filled by OSAP; an SF1 eps-change streak would be a different signal |
| EarnSupBig | preflight_failed | 2026-09-30 | mass point by construction: every non-big firm in an FF48 industry-month receives the same value (the big firms' mean surprise), so each cross-section holds <= 48 distinct values; the modal share is 12.8% / 9.1% / 15.1% at the 1998-12 / 2010-06 / 2021-11 probes and > 10% in 14 of 23 yearly probe months (1999-06..2021-06, max 17.5%, qcut 9 bins in 3); no tie handling exists without replacing the signal; file kept at factors/preflight_failed/EarnSupBig.py |
| ExchSwitch | preflight_failed | 2026-09-30 | binary exchange-switch flag: buildable from ACTIONS exchangeto/exchangefrom (TICKERS.exchange is current-only), but it fires on 0.50% of universe name-months (upper bound; 2,701 of 542,282); median 7 flagged names per month, < 30 in 267 of 276 months; the zero block is 98.5-99.96% of each cross-section, qcut 2 bins; measured by osap-fetcher over all 276 decision months |
| ExclExp | data_unavailable | 2026-09-30 | signal is int0a - epspiq; int0a is the IBES unadjusted actual EPS, not in Sharadar and not zero-filled by OSAP (missing -> row dropped); epspiq alone is a different signal |
| FEPS | data_unavailable | 2026-09-30 | signal is IBES meanest (mean unadjusted FY1 EPS forecast); no analyst forecasts in Sharadar; not zero-filled by OSAP |
| fgr5yrLag | data_unavailable | 2026-09-30 | needs the IBES long-term growth forecast (meanest, fpi 0); no analyst data in Sharadar; OSAP requires it non-missing |
| FirmAge | data_start | 2026-09-30 | age = months since first trade is censored at the snapshot start (SEP and TICKERS.firstpricedate begin 1997-12; OSAP censors at 1926 and nulls censored firms), so only post-1997 listers score: 5.4% of the universe at 1998-12 rising to 61.6% at 2021-11, pooled 34.7% over 276 months, 170 of 276 months under the 40% bar; the first probe also breaches the 10% mass-point cliff (14.5% at 6 months, 11 distinct values). Measured by osap-fetcher on the harness universe, all 276 decision months |
| FirmAgeMom | preflight_failed | 2026-09-30 | defined only in the youngest age quintile (OSAP), so coverage cannot exceed ~20%: 18.3-20.0% of the universe in the 205 months where the quintile is identifiable (from 2004-11, age censored at the 1997-12 snapshot start), 0 names in 71 months; pooled 13.7% over 276 months, never reaching the 40% Stage 1 bar. Measured by osap-fetcher on the harness universe |
| ForecastDispersion | data_unavailable | 2026-09-30 | signal is IBES stdev / \|meanest\| (FY1 forecast dispersion); no analyst data in Sharadar; OSAP does not zero-fill it |
| FR | data_unavailable | 2026-09-30 | needs Compustat pension items (pbnaa, pplao, pplau, pbnvv, pbpro, pbpru; COMP.ACO_PNFNDA); SF1 has no pension field; OSAP inner-merges (no zero-fill), so infeasible under the missing-item rule |
| Frontier | preflight_failed | 2026-09-30 | coverage: OSAP does not zero-fill xrd, so rnd non-reporters and rnd == 0 (67% of non-null rnd in the universe) drop out; with the faithful gates (rnd != 0, sale, at, equity > 0, debtc/debtnc non-null, capex, opinc+depamor, ppnenet) pooled coverage is 30.1% over 276 months, 14.5-38.5% per month, 0 of 276 months at or above the 40% bar; xad (unavailable) is zero-filled by OSAP itself so it is not the obstacle. Measured by osap-fetcher on the harness universe |
| Governance | data_unavailable | 2026-09-30 | G-index (Gompers-Ishii-Metrick, Yale spreadsheet) is in no Sharadar table; OSAP drops rows without G (no default); OSAP's own series also ends 2007-01 (at most 97 decision months) |
| GrAdExp | data_unavailable | 2026-09-30 | advertising expense xad is the signal itself; no Sharadar field; OSAP reads raw xad (not zero-filled) and nulls xad < 0.1, so no zero-fill rescue |
| hire | data_unavailable | 2026-09-30 | employee counts (Compustat emp) are in no held Sharadar table; OSAP sets hire = 0 where emp is missing, so without emp the signal is the constant 0 for every firm (the missing-item rule's constant case) |
| IndIPO | preflight_failed | 2026-09-30 | binary recent-IPO flag: 89.9% of the universe is 0 on average (78.8-95.4%), 2 distinct values, qcut 1 bin at all three probes; the modal share exceeds the 10% cliff in all 276 months, so no tie handling can fill ten deciles. Also approx data: the Ritter IPO file is unavailable; TICKERS.firstpricedate (= ACTIONS listed) is floored at 1997-12-31 for 37.5% of IDs and also marks spin-offs, SPACs and uplistings. Measured by osap-fetcher on the harness universe, all 276 decision months |
| IndMom | preflight_failed | 2026-09-30 | mass point by construction: the 2-digit-SIC cap-weighted past return is assigned to every industry member, so each cross-section holds 63-68 distinct values on ~1,960 names; modal share 8.4-20.3% (mean 10.7%), >= 10% in 144 of 276 months and at 2 of 3 preflight probes (12.3% 1998-12, 14.5% 2021-11), qcut < 10 bins in 33 months; within sector 65% of names tie with >= 10% of their peers (Utilities 98% one value). Measured by osap-fetcher on the harness universe, all 276 months |
| IndRetBig | preflight_failed | 2026-09-30 | mass point and coverage by construction: the big firms' FF48 mean return is assigned to the non-big members and the big firms are NaN; coverage 20.4-36.9% (mean 28.9%), under 40% in every month; modal share 10.2-26.1%, >= 10% in all 276 months, qcut < 10 bins in 126; a universe-scope big/small cut still breaches the cliff at 2 of 3 probes. Measured by osap-fetcher on the harness universe, all 276 months |
| InvestPPEInv | data_unavailable | 2026-10-01 | needs gross PP&E (ppegt), which SF1 does not carry (only ppnenet) and OSAP does not zero-fill; substituting net PP&E is a different signal and is not adopted (as for AbnormalAccruals) |
| IO_ShortInterest | data_unavailable | 2026-09-30 | short interest is in no held Sharadar table (13 checked), and OSAP uses it as the sample filter (top 1% of shortint/shrout), so without it every row is null, not neutral (the fillna(0) on tempshortratio/instown_perc does not rescue a filter); 13F institutional ownership (SF3/SF3A) starts 2013-06 (at most 102 of 276 months); the top-1% sample would also be ~20 names, ~2 per decile against the 30-per-decile bar |
| iomom_cust | data_unavailable | 2026-09-30 | needs BEA Make input-output tables and Compustat NAICS to map firms to BEA industries; neither is in the snapshot; OSAP has no fallback and does not zero-fill |
| iomom_supp | data_unavailable | 2026-09-30 | needs BEA Use input-output tables and Compustat NAICS; neither is in the snapshot; OSAP has no fallback and does not zero-fill |
| Mom6mJunk | data_unavailable | 2026-10-01 | needs an S&P/CIQ credit rating (splticrm, comp.adsprate, CIQ fallback) to select junk-rated firms; no held Sharadar table carries ratings (EVENTS code 63 is credit enhancement, not a rating); OSAP does not zero-fill it (missing rating -> observation dropped) |
| MomOffSeason11YrPlus | data_start | 2026-10-01 | data start: 55 off-season returns at lags 120..178 need the close at BME(t-179); with SEP from 1997-12 the first full-window signal is 2012-11-30, so only 109 of 276 decision months can score, under rebalance.min_months 120 (history_months equals the full window, the hard rule for return-window factors; OSAP's partial-window skipna scoring is not reproduced, decision momentum_partial_windows) |
| MomOffSeason16YrPlus | data_start | 2026-10-01 | data start: 55 off-season returns at lags 180..238 need the close at BME(t-239); first full-window signal 2017-11-30, so only 49 of 276 decision months can score, under rebalance.min_months 120 (decision momentum_partial_windows) |
| MomRev | preflight_failed | 2026-10-01 | two-valued flag (1 = top Mom6m and bottom Mom36m quintile, 0 = the reverse, NaN otherwise): coverage 4.2-16.7% of the universe (mean 9.0%, pooled 8.0%), under 40% in every month; modal share 50.0-73.4% among scored names, at most 2 of 10 deciles fillable. Measured by osap-fetcher on the harness universe, 251 scorable months |
| MomSeason11YrPlus | data_start | 2026-10-01 | data start: 5 same-month returns at lags 131..179 need the close at BME(t-180); first full-window signal 2012-12-31, so only 108 of 276 decision months can score, under rebalance.min_months 120 (decision momentum_partial_windows; OSAP-literal partial windows would give 156) |
| MomSeason16YrPlus | data_start | 2026-10-01 | data start: 5 same-month returns at lags 191..239 need the close at BME(t-240); first full-window signal 2017-12-29, so only 48 of 276 decision months can score (96 even with OSAP-literal partial windows), under rebalance.min_months 120 |
| MomVol | preflight_failed | 2026-09-30 | categorical label 1..10 scored only in the top volume tercile: coverage 26.5-33.0% of the universe (ceiling 33.3%), under 40% in all 265 scorable months; modal share 11.0-21.4%, >= 10% in 265 of 265 months, qcut < 10 bins in 264. Measured by osap-fetcher on the harness universe |
| MS | preflight_failed | 2026-10-01 | six-valued score (MS in 1..6): 6 distinct values in every measured month, modal share 20.8-52.9% (mean 25.0%), >= 10% cliff in all 269 measured months, qcut cannot give 10 bins; and coverage by construction (lowest book-to-market quintile, >= 3 firms per SIC2): mean 25.3% of the universe, under 40% in every month. xad is zero-filled by OSAP itself (so not infeasible on data). Measured by osap-fetcher on the harness universe, 269 of 276 months |
| NetDebtPrice | data_unavailable | 2026-09-30 | numerator (dltt + dlc + pstk + dvpa - tstkp) - che needs preferred stock pstk: no SF1 field, and neither OSAP's zero_fill_vars nor NetDebtPrice's predictor fills it (unlike DelFINL/DelNetFin, whose predictors fillna(0) pstk themselves), so infeasible under the missing-item rule; book_equity_preferred_terms covers book equity only. Also, with pstk omitted, coverage is under 40% in 128 of 276 months |
| NumEarnIncrease | preflight_failed | 2026-09-30 | integer count 0..8 of consecutive quarterly earnings increases: 9 distinct values, modal value 0 at 34.9-84.6% of scored names (median 52.1%), >= 10% cliff in all 276 months; probes 84.3% / 37.5% / 44.4% with qcut 2 / 5 / 6 bins; nulling the zeros leaves value 1 at a median 15.0%. Measured by osap-fetcher on the harness universe, all 276 months |
| OptionVolume1 | data_unavailable | 2026-09-30 | numerator is OptionMetrics option volume (optvolume); no held Sharadar table carries option volume (SF3A/SF3B put/call are quarterly 13F holdings from 2013-06); OSAP does not zero-fill it |
| OptionVolume2 | data_unavailable | 2026-09-30 | OptionMetrics option volume (optvolume) and its 6-month average; no held Sharadar table carries option data; OSAP does not zero-fill it |
| OrderBacklog | data_unavailable | 2026-09-30 | order backlog (Compustat ob) has no SF1 field; OSAP zero-fills ob but its predictor then sets the signal NaN wherever ob == 0, so with ob absent the signal is undefined for every firm (the missing-item rule's constant/undefined case) |
| OrderBacklogChg | data_unavailable | 2026-09-30 | needs non-zero order backlog (Compustat ob) at t and t-12; ob has no SF1 field and OSAP's zero-fill-then-null logic makes the signal undefined for every firm |
| OScore | preflight_failed | 2026-09-30 | OSAP's published predictor is a binary flag (1 = top O-Score decile, 0 = deciles 1-7, deciles 8-9 dropped): 2 distinct values, 87.3-87.5% of scored names at 0 in every month, qcut 2 bins; coverage 37.8% pooled, under 40% in 179 of 276 months. The continuous O-Score is a different signal (the published test is non-monotonic) and is not substituted, as for EarnSupBig. Measured by osap-fetcher on the harness universe, all 276 months |
| PatentsRD | data_unavailable | 2026-09-30 | numerator npat comes from a patent panel Sharadar does not publish; the predictor's fillna(0) fills gaps inside that panel, so without it npat is 0 for every firm and the signal is constant (as CitationsRD) |
| PayoutYield | data_unavailable | 2026-09-30 | numerator needs preferred redemption value pstkrv (no SF1 field, not zero-filled by OSAP or the predictor) and gross repurchases prstkc (Sharadar has only net ncfcommon; gross buybacks of the ~46% net issuers are unobservable); the net-flow NetPayoutYield formula is a different signal and is not substituted |
| PredictedFE | data_unavailable | 2026-09-30 | needs IBES forecasts (feps1, feps2, long-term growth) and AOP (itself built from IBES) as regressors; no analyst data in Sharadar; the source screen drops firms without them (no zero-fill); same script and reason as the AOP and AnalystValue rows |
| ProbInformedTrading | data_unavailable | 2026-09-30 | PIN parameters (a, u, es, eb) come from a third-party file estimated on intraday buy/sell trade counts; no held Sharadar table carries trade counts or quotes; OSAP drops unmatched rows (no zero-fill) |
| PS | preflight_failed | 2026-09-30 | Piotroski F-score, an integer 0..9 scored in OSAP's top book-to-market quintile: 6-9 distinct values, modal share 20.0-40.7% (median 26.8%) >= 10% in all 276 months; coverage 1.4-6.1% of the universe (never >= 40%); even with no book-to-market restriction (a different signal, not substituted) the modal share is 23.2-31.7% in every month. Measured by osap-fetcher on the harness universe, all 276 months |
| RD | preflight_failed | 2026-09-30 | coverage: OSAP does not zero-fill xrd and scores only R&D reporters; SF1.rnd is vendor-zero for non-reporters, so rnd == 0 is NaN (faithful reading): pooled coverage 31.9% of the universe, >= 40% in only 4 of 276 months (0 of 276 with OSAP's 6-month lag); keeping zeros instead puts 56.6-70.7% of scored names at 0 (qcut 3-6 bins every month). Same ground as the Frontier row. Measured by osap-fetcher on the harness universe, all 276 months |
| RDAbility | preflight_failed | 2026-09-30 | coverage by construction: scored only in the top tercile of R&D/sales with R&D > 0 (6.9% of the universe) and after 8 fiscal-year rows with >= 6 valid pairs; mean coverage 3.0% (max 5.5%), 0 of 276 months >= 40% and 0 with >= 300 scored names. Measured by osap-fetcher on the harness universe, all 276 months |
| RDcap | preflight_failed | 2026-09-30 | OSAP keeps only the bottom market-cap tercile of all listed stocks, which contains 0 harness-universe names in all 276 months (coverage 0%); and without that cut the value is exactly 0 (xrd.fillna(0), zeros not nulled) for 63.2-74.0% of names, >= 10% cliff in every month, qcut 3-5 bins. Measured by osap-fetcher on the harness universe and market scope |
| RDIPO | preflight_failed | 2026-09-30 | binary flag (recent IPO with zero R&D): modal zero share 92.5-98.4% in every month, qcut 1 bin; also approx IPO dates (TICKERS.firstpricedate floored at 1997-12-31, marks spin-offs/SPACs; as IndIPO). Measured by osap-fetcher, all 276 months |
| RDS | data_unavailable | 2026-09-30 | OSAP zero-fills recta, msa and pension terms but then sets RDS NaN wherever recta and msa were originally missing (both_missing_mask); SF1 carries neither, so OSAP's own code nulls every row; forcing the dirty-surplus term to 0 would be a different signal |
| realestate | data_unavailable | 2026-09-30 | needs Compustat fatb and fatl (buildings and land at cost) and ppegt, with a ppenb/ppenls fallback; none is in SF1 and OSAP zero-fills none (a missing term drops the row); a ppnenet/assets proxy would be a different signal |
| Recomm_ShortInterest | data_unavailable | 2026-09-30 | needs IBES analyst recommendations and Compustat short interest; neither in Sharadar; OSAP inner-joins both (no zero-fill); also a binary flag in two extreme cells |
| retConglomerate | data_unavailable | 2026-09-30 | needs Compustat business-segment data (segment SICs and sales) and the CCM link; no held Sharadar table carries segments; OSAP inner-merges (no fill) |
| REV6 | data_unavailable | 2026-09-30 | needs IBES mean-estimate revisions (meanest, statpers, fpedats); no analyst data in Sharadar; NaN if any of the 7 monthly changes is missing (no zero-fill) |
| RIO_Disp | data_unavailable | 2026-09-30 | needs IBES forecast dispersion (stdev, not in Sharadar, no zero-fill) and 13F ownership from 2013-06 (94 scorable months < 120); 5-valued output |
| RIO_MB | data_start | 2026-09-30 | data start: 13F institutional ownership (SF3A) from 2013-06-30 gives 94 scorable decision months with the 45-day filing lag (95 without), under rebalance.min_months 120; OSAP's zero-fill of missing ownership before 2013 makes lagged RIO a size proxy (Spearman with log cap -0.96 vs -0.38 on real 13F months), not accepted; also a 5-valued output (modal share ~27.5%) scored only in the top market-to-book quintile (~18% coverage) |
| RIO_Turnover | data_start | 2026-09-30 | data start: as RIO_MB, 94 scorable months with 13F data < 120; 5-valued output (modal share ~28.9%), ~19.6% coverage (top turnover quintile only) |
| RIO_Volatility | data_start | 2026-09-30 | data start: defined by 13F institutional ownership (Sharadar SF3/SF3A from 2013-06-30): 96 scorable decision months with OSAP timing, 94 with a 45-day point-in-time lag, under rebalance.min_months 120 (as DelBreadth); OSAP's zero-fill of missing ownership before 2013 would make it a pure size sort, not accepted; also scored only in the top-volatility quintile (~19.7% coverage) as an ordinal 1..5 |
| RIVolSpread | data_unavailable | 2026-09-30 | needs at-the-money implied volatility (OptionMetrics); no held Sharadar table carries option data; OSAP keeps only rows with implied vol (no zero-fill) |
| sfe | data_unavailable | 2026-09-30 | needs the IBES median next-year EPS forecast and analyst count; no analyst data in Sharadar; OSAP inner-merges (no fill) |
| ShareRepurchase | preflight_failed | 2026-09-30 | binary repurchase flag (prstkc > 0): 2 distinct values, modal share 50.0-72.3% every month, qcut 1-2 bins; also approx data (gross prstkc not in Sharadar; net ncfcommon < 0 would stand in). Measured by osap-fetcher, all 276 months |
| ShareVol | preflight_failed | 2026-09-30 | OSAP's published signal is {0,1} at 5% and 10% share-turnover thresholds with the middle dropped: under the plain-percent reading 95.3% of names are 1, under the literal CRSP-units reading 99.85-100%, qcut 0-2 bins; its drop rule (no share change in 3 months) cannot survive filing-stepped sharesbas (leaves ~8% of the universe); a continuous turnover would be a different signal. Measured by osap-fetcher, all 276 months |
| ShortInterest | data_unavailable | 2026-09-30 | short interest (shortint) is the signal itself and is in no held Sharadar table; OSAP inner-merges on the short-interest file (no zero-fill) |
| sinAlgo | data_unavailable | 2026-09-30 | needs Compustat segments and historical NAICS (neither in Sharadar; OSAP does not zero-fill them); a SIC-only build is a binary flag scored only in a small comparison group: 3.9-6.2% coverage, modal share 83.9-90.0%, 2 qcut bins. Measured by osap-fetcher, all 276 months |
| skew1 | data_unavailable | 2026-09-30 | built from OptionMetrics option-level implied volatility; no held Sharadar table carries option data; OSAP does not zero-fill it |
| SmileSlope | data_unavailable | 2026-09-30 | needs OptionMetrics implied-volatility surface (30-day, delta 50 put minus call); no held Sharadar table carries option data; OSAP keeps only non-null rows (no zero-fill) |
| Spinoff | preflight_failed | 2026-09-30 | binary spin-off child flag (ACTIONS spunofffrom, 24-month window): 1.06% of the universe flagged on average (20.5 names a month; < 30 in 237 of 276 months), zero block 98.9%, 2 distinct values, cannot form ten deciles. Measured by osap-fetcher on the harness universe, all 276 months |
| std_turn | preflight_failed | 2026-09-30 | OSAP nulls std_turn for market-cap quintiles 4-5 of all listed stocks; the harness universe sits almost entirely above the 60th percentile, so coverage after OSAP's null is 2.5-11.3% (54-262 names, at most 26 per decile) at all probes; dropping the null would change what OSAP emits, not adopted (as RDcap). Measured by osap-fetcher, 13 probe months |
| SurpriseRD | preflight_failed | 2026-09-30 | binary R&D-surprise flag: 2 distinct values, qcut 1 bin in >= 272 of 276 months under either reading; with rnd == 0 as missing (OSAP does not zero-fill xrd) coverage is 29.0% pooled, 0 of 276 months >= 40%, modal share 51.9-84.6%; keeping zeros gives modal share 83.4-95.1%. Measured by osap-fetcher, all 276 months |
| tang | data_unavailable | 2026-09-30 | the pinned code uses gross PP&E (ppegt), not in SF1 and dropped by OSAP when missing (ppnenet is a substitution, not adopted); and the manufacturers-only sample (SIC 2000-3999) is 35.1-38.5% of the universe before any value, under the 40% bar |
| Tax | data_unavailable | 2026-09-30 | needs Compustat txfo, txfed, txdi (no SF1 fields, not zero-filled by OSAP); the fallback txt - txdi is NaN without txdi, so every ib > 0 row is NaN and every ib <= 0 row is the single value 1.0 (coverage 9.0-39.5%, 100% mass point); a taxexp-only numerator would be a different signal |
| UpRecomm | data_unavailable | 2026-09-30 | needs IBES analyst recommendations (ireccd); no analyst data in Sharadar; also a binary upgrade flag |

## Appendix A3. Families

*Table A3_families_yaml. research/families.yaml, verbatim.*

```yaml
# Family assignments — Phase C. Written ONCE per Stage 1 passer, after its
# screen and before ANY Stage 2 number exists, by economic definition (the
# OSAP SignalDoc Cat.Economic label is the reference; the predictor's own
# construction decides when the label is "other"). Fewer than ten families
# in total (config search.families_max). Never changed after assignment:
# a wrong family is a logged limitation, not an edit.
#
# The five seed families are fixed by v0: size, value, profitability,
# investment, momentum. A passer joins one of them or opens a new one.
#
# families:
#   value:
#     definition: "price relative to a fundamental anchor"
#     members: [Value]                 # seeds first, passers appended in assignment order
#   <new_family>:
#     definition: "..."
#     members: [...]
# assignments:
#   - {factor: <Name>, family: <family>, cat_economic: "<SignalDoc label>", assigned: "YYYY-MM-DD", event_ts: "..."}
families:
  size:
    definition: market capitalisation (small = attractive)
    members: [Size]
  value:
    definition: price relative to a fundamental anchor
    members: [Value, CF, NetPayoutYield, cfp]
  profitability:
    definition: earning power relative to capital
    members: [Profitability, CBOperProf, GP, OperProfRD, RoE, roaq]
  investment:
    definition: growth of the asset base or of investment
    members: [Investment, PctAcc]
  momentum:
    definition: continuation of past returns
    members: [Momentum, TrendFactor]
  volatility:
    definition: dispersion or tail size of a stock's own returns (total, idiosyncratic, extreme daily); low = attractive
    members: [IdioVol3F, IdioVolAHT, MaxRet, RealizedVol]
  external_financing:
    definition: net capital raised from or returned to investors (share issuance, net equity and debt financing)
    members: [NetEquityFinance, ShareIss1Y, ShareIss5Y, XFIN]
  short_term_reversal:
    definition: reversal of the most recent month's return
    members: [STreversal]
  liquidity:
    definition: trading activity and trading cost (turnover, zero-volume days, bid-ask spread, volume trend)
    members: [VolumeTrend, zerotrade12M, zerotrade1M, zerotrade6M, BidAskSpreadFlip]
assignments:
  - {"factor": "CBOperProf", "family": "profitability", "cat_economic": "profitability", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "CF", "family": "value", "cat_economic": "valuation", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "GP", "family": "profitability", "cat_economic": "profitability", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "IdioVol3F", "family": "volatility", "cat_economic": "volatility", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "IdioVolAHT", "family": "volatility", "cat_economic": "volatility", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "MaxRet", "family": "volatility", "cat_economic": "volatility", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "NetEquityFinance", "family": "external_financing", "cat_economic": "external financing", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "NetPayoutYield", "family": "value", "cat_economic": "valuation", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "OperProfRD", "family": "profitability", "cat_economic": "profitability", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "PctAcc", "family": "investment", "cat_economic": "accruals", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "RealizedVol", "family": "volatility", "cat_economic": "volatility", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "RoE", "family": "profitability", "cat_economic": "profitability", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "STreversal", "family": "short_term_reversal", "cat_economic": "short-term reversal", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "ShareIss1Y", "family": "external_financing", "cat_economic": "external financing", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "ShareIss5Y", "family": "external_financing", "cat_economic": "external financing", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "TrendFactor", "family": "momentum", "cat_economic": "momentum", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "VolumeTrend", "family": "liquidity", "cat_economic": "volume", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "XFIN", "family": "external_financing", "cat_economic": "external financing", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "cfp", "family": "value", "cat_economic": "valuation", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "roaq", "family": "profitability", "cat_economic": "profitability", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "zerotrade12M", "family": "liquidity", "cat_economic": "liquidity", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "zerotrade1M", "family": "liquidity", "cat_economic": "liquidity", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "zerotrade6M", "family": "liquidity", "cat_economic": "liquidity", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
  - {"factor": "BidAskSpreadFlip", "family": "liquidity", "cat_economic": "liquidity", "assigned": "2026-10-01", "event_ts": "2026-10-01T05:45:32Z"}
```

## Appendix A4. The Stage 2 order

*Table A4_stage2_order. The pre-declared Stage 2 order (rule descending_stage1_ic_tstat_nw, declared 2026-10-01T05:45:32Z). Source: research/stage2_order.yaml.*

| rank | factor | Stage 1 NW t | Stage 1 mean IC | family |
|---|---|---|---|---|
| 1 | PctAcc | 4.032033 | 0.011159 | investment |
| 2 | CBOperProf | 3.735701 | 0.020856 | profitability |
| 3 | ShareIss5Y | 3.667119 | 0.015791 | external_financing |
| 4 | cfp | 3.651526 | 0.024642 | value |
| 5 | XFIN | 3.570243 | 0.017006 | external_financing |
| 6 | GP | 3.520387 | 0.015533 | profitability |
| 7 | ShareIss1Y | 3.516353 | 0.016467 | external_financing |
| 8 | MaxRet | 3.423890 | 0.023275 | volatility |
| 9 | roaq | 3.366138 | 0.020781 | profitability |
| 10 | RoE | 3.337252 | 0.019194 | profitability |
| 11 | OperProfRD | 3.183514 | 0.019224 | profitability |
| 12 | IdioVol3F | 3.147216 | 0.022882 | volatility |
| 13 | NetEquityFinance | 3.027885 | 0.016576 | external_financing |
| 14 | CF | 3.027856 | 0.020063 | value |
| 15 | STreversal | 2.963026 | 0.014466 | short_term_reversal |
| 16 | zerotrade6M | 2.927305 | 0.018548 | liquidity |
| 17 | VolumeTrend | 2.869779 | 0.011364 | liquidity |
| 18 | zerotrade12M | 2.831524 | 0.017979 | liquidity |
| 19 | RealizedVol | 2.809589 | 0.023399 | volatility |
| 20 | TrendFactor | 2.787353 | 0.017142 | momentum |
| 21 | BidAskSpreadFlip | 2.762832 | 0.020576 | liquidity |
| 22 | IdioVolAHT | 2.628065 | 0.023776 | volatility |
| 23 | zerotrade1M | 2.626066 | 0.015549 | liquidity |
| 24 | NetPayoutYield | 2.604558 | 0.014492 | value |

## Appendix A5. Manifest headlines v0–v14 (acceptance-time), with v14 on the spend snapshot and in the holdout

*Table A5_manifest_headlines. Manifest headlines v0-v14 in the project's summary format (Sharpe, return and MaxDD hedged; beta the full-window beta of the raw LS; turnover D10 per month). Sources: MODEL_MANIFEST.yaml `versions[*].baseline`; run 053; run 054 `cut_holdout_*` and run 055 (`ls_beta_fullwindow`, `turnover_d10_pct`) for the holdout row.*

| version | run | window and bytes | legs | families | mean IC | IC t (NW) | LS Sharpe | ann ret % | MaxDD % | beta | turnover % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v0 | 001 | acceptance-time (DATA 198b281de1a0) | 5 | 5 | 0.0145 | 2.62 | 0.600 | 7.32 | -45.56 | -0.140 | 28.0 |
| v1 | 013 | acceptance-time (DATA 198b281de1a0) | 6 | 5 | 0.0169 | 3.02 | 0.614 | 7.38 | -41.28 | -0.121 | 27.6 |
| v2 | 015 | acceptance-time (DATA 198b281de1a0) | 7 | 5 | 0.0169 | 3.02 | 0.661 | 7.82 | -37.07 | -0.122 | 28.0 |
| v3 | 017 | acceptance-time (DATA 198b281de1a0) | 8 | 6 | 0.0215 | 3.98 | 0.848 | 10.29 | -41.92 | -0.192 | 26.3 |
| v4 | 019 | acceptance-time (DATA 198b281de1a0) | 9 | 6 | 0.0249 | 4.51 | 0.996 | 12.02 | -40.63 | -0.263 | 25.2 |
| v5 | 021 | acceptance-time (DATA 198b281de1a0) | 10 | 6 | 0.0245 | 4.27 | 0.914 | 11.56 | -47.75 | -0.344 | 25.0 |
| v6 | 024 | acceptance-time (DATA 198b281de1a0) | 11 | 6 | 0.0242 | 4.23 | 0.925 | 11.72 | -49.42 | -0.323 | 25.2 |
| v7 | 026 | acceptance-time (DATA 198b281de1a0) | 12 | 7 | 0.0305 | 4.49 | 0.951 | 13.95 | -41.68 | -0.649 | 43.4 |
| v8 | 028 | acceptance-time (DATA 198b281de1a0) | 13 | 7 | 0.0320 | 4.50 | 0.967 | 15.18 | -43.36 | -0.721 | 44.1 |
| v9 | 030 | acceptance-time (DATA 198b281de1a0) | 14 | 7 | 0.0323 | 4.50 | 0.932 | 14.87 | -43.67 | -0.734 | 44.3 |
| v10 | 033 | acceptance-time (DATA 198b281de1a0) | 15 | 7 | 0.0326 | 4.48 | 0.919 | 15.25 | -45.78 | -0.752 | 39.8 |
| v11 | 035 | acceptance-time (DATA 198b281de1a0) | 16 | 8 | 0.0355 | 5.36 | 0.942 | 14.61 | -39.53 | -0.512 | 59.1 |
| v12 | 038 | acceptance-time (DATA 198b281de1a0) | 17 | 9 | 0.0373 | 5.15 | 0.985 | 16.16 | -41.11 | -0.635 | 56.8 |
| v13 | 040 | acceptance-time (DATA 198b281de1a0) | 18 | 9 | 0.0372 | 5.24 | 0.979 | 16.13 | -41.60 | -0.619 | 56.6 |
| v14 | 042 | acceptance-time (DATA 198b281de1a0) | 19 | 9 | 0.0389 | 5.68 | 0.983 | 16.12 | -43.21 | -0.560 | 58.1 |
| v14 | 053 | in-window, spend snapshot (DATA 42587e08609a) | 19 | 9 | 0.0389 | 5.68 | 0.996 | 16.34 | -43.23 | -0.556 | 58.1 |
| v14 | 054 (055 for beta, turnover) | holdout 2022-01..2026-09 | 19 | 9 | 0.0300 | 1.87 | 0.523 | 10.81 | -35.65 | -0.836 | 54.3 |

## Appendix A6. Tags and commits

*Table A6_tags. Tag-to-commit map. Source: MODEL_MANIFEST.yaml `tags` (built from `git tag -l 'v*'` and `git rev-parse <tag>^{commit}`).*

| version | tag | tag commit | version commit (if different) | note |
|---|---|---|---|---|
| v0 | v0-baseline | de3f3b6102c10c7deb5e99d6557cb064afc44073 |  |  |
| v1 | v1-add-PctAcc | 2e37d4bbcea9e0228aade37e9037a07d504f0340 | 0d52a33dea348a16760d38517432970980ee9849 | MIS-POINTED (owner decides) |
| v2 | v2-add-CBOperProf | b892fd8b64e49682d94694640db6b6bb2a40b726 |  |  |
| v3 | v3-add-ShareIss5Y | 9f95f366732933235bf3bd368c5500302a52ab8c |  |  |
| v4 | v4-add-cfp | ba822a37081ad806b6ceb7b82feead0a21f5e9df |  |  |
| v5 | v5-add-XFIN | 7fb7fcbc79c5be3f656c75951fdf532536a82999 |  |  |
| v6 | v6-add-GP | 78e1ad357a58e5f281a58d1cc8f4a81c6fe767c2 |  |  |
| v7 | v7-add-MaxRet | 9ca72f2c5113ffcd7b559ef0cda52cf435d511ea |  |  |
| v8 | v8-add-roaq | 9d80c1ef82ba4f14e7663bce65ef783a0254af9d |  |  |
| v9 | v9-add-RoE | aa12f9c87e979e8b9abc34c18a4f67b48498581d |  |  |
| v10 | v10-add-IdioVol3F | 74eaad843573d2ba0f643941d487ecd0a5b95d2c |  |  |
| v11 | v11-add-STreversal | 2e4e543b4f16fd5b77ea296e35005162fa78fa42 |  |  |
| v12 | v12-add-zerotrade6M | bf17998008c0e298d7a7171f84d3aca7d9039462 |  |  |
| v13 | v13-add-VolumeTrend | 986de788e33ee4b0708e87cfbe81e563fd54edc0 |  |  |
| v14 | v14-add-TrendFactor | 4a6ade91b454a4a48148fdbbe4f487bafdacf440 |  |  |

## Appendix A7. The source of every number in the prose

*Every scalar the prose uses, with its record source. Generated by paper/build_tables.py.*

| key | value | source |
|---|---|---|
| aborted_seq | 046 | events run_aborted seq |
| bar_s1_ic | 0.010 | config stage1_standalone.min_ic_mean |
| bar_s1_t | 2.5 | config stage1_standalone.min_ic_tstat_nw |
| bar_s2_guard | -2.0 | config stage2_marginal.min_paired_delta_ls_tstat |
| bar_s2_t | 2.0 | config stage2_marginal.min_resid_ic_tstat_nw |
| bas_flip_t | 2.7628 | registry BidAskSpreadFlip stage1.ic_tstat_nw |
| bas_flip_t2 | 2.76 | registry BidAskSpreadFlip stage1.ic_tstat_nw |
| bas_parent_t | 2.77 | events flip_hypothesis_qualified BidAskSpread \|ic_tstat_nw\| |
| best_sh | 0.996 | manifest v4 baseline.ls_hedged.ls_sharpe |
| best_sh_ver | v4 | manifest version with the highest baseline.ls_hedged.ls_sharpe |
| beta_min | 12 | config market_hedge.beta_min_months |
| beta_window | 36 | config market_hedge.beta_window_months |
| close_h2 | 0.0281 | run 050 ic_half2_mean |
| close_sh | 0.983 | run 050 ls_sharpe |
| cnt_alpha_review | 23 | events alpha_review count |
| cnt_decision | 51 | events decision count |
| cnt_factor_evaluated | 132 | events factor_evaluated count |
| cnt_factor_translated | 108 | events factor_translated count |
| cnt_fields_verified | 27 | events fields_verified count |
| cnt_preflight_failed | 29 | events preflight_failed count |
| cnt_preflight_passed | 105 | events preflight_passed count |
| cnt_spec_written | 207 | events spec_written count |
| comp_gross | +37.7 | compounded run 049 layer@100M annual_gross_returns_pct 2003-2020 |
| comp_gross_arith | 1.96 | mean of run 049 annual_gross_returns_pct 2003-2020 |
| comp_gross_geo | 1.79 | geometric annual rate of comp_gross over 18 years |
| comp_net | -36.1 | compounded run 049 layer@100M annual_net_returns_pct 2003-2020 |
| config_sha | 0d88328d5b10 | run 053 block config_sha |
| cont_n | 20 | run 054 cut_inwindow_* fields with a same-named run 053 field |
| cont_same | 20 | run 054 cut_inwindow_* fields equal to the run 053 field of the same name |
| cut_1120_gross | 0.95 | run 049 layer@100M cut_2011_2020_gross_ann_return_pct |
| cut_1120_gross_sh | 0.222 | run 049 layer@100M cut_2011_2020_gross_sharpe |
| cut_1120_net_sh | -0.559 | run 049 layer@100M cut_2011_2020_net_sharpe |
| cut_ex_eff | 2001, 2021 | run 049 layer@100M cut_exyears_effective |
| cut_ex_gross_sh | 0.647 | run 049 layer@100M cut_exyears_gross_sharpe |
| cut_ex_net_sh | -0.370 | run 049 layer@100M cut_exyears_net_sharpe |
| data_sha_1 | 198b281de1a0 | events snapshot_recorded #1 data_sha |
| data_sha_2 | 42587e08609a | events snapshot_recorded #2 new_data_sha |
| deny_text | factor-evaluator step 1 for v12 (git mv factors/candidates/zerotrade6M.py -> factors/accepted/ plus the factors/composite.py edit) was refused by the session permission classifier; repo unchanged, no stamp moved, no run started | events process_finding v12_apply_permission_denied evidence |
| eval_end | 2021-12-31 | config dates.eval_end |
| eval_end_runs | 52 | runs 001-053 with result blocks |
| eval_end_set | 2021-12-31 | eval_end over every result block of runs 001-053 |
| eval_start | 1999-01-01 | config dates.eval_start |
| families_max | 9 | config search.families_max |
| fixed_half_spread_bp | 8.3 | manifest v14 construction_layer.trading.fixed_tier_half_spread_bp |
| flip_bar | 2.74 | CLAUDE.md flip rule \|t\| >= 2.74 |
| floor_warn | Only 57 usable months (minimum 120). INCONCLUSIVE, not a rejection — a thin sample is a coverage problem. | events validation_warning seq 055 warnings[1] |
| fmax_held | v12 | first MODEL_MANIFEST version whose composite holds families_max families |
| fmax_opened_by | VolumeTrend | events line 867 family_assigned (first with n_families_after = families_max and new_family) |
| fmax_opened_ts | 2026-10-01T05:45:32Z | events line 867 family_assigned ts |
| full054_raw_mdd | -51.84 | run 054 ls_raw_maxdd_pct (1999-2026) |
| gate_ShareIss5Y | 65 | registry ShareIss5Y history_gate_months |
| grl_parent_t | 2.75 | events flip_hypothesis_qualified GrLTNOA \|ic_tstat_nw\| |
| grl_rev_ic | 0.0059 | events flip_hypothesis_qualified GrLTNOA \|ic_mean\| |
| half_spread_bp | 39.2 | manifest v14 construction_layer.trading.implied_half_spread_bp |
| hedge_term_ho | 7.79 | run 054 cut_holdout_ls_ann_return_pct - cut_holdout_ls_raw_ann_return_pct |
| hedge_term_iw | 1.43 | run 053 ls_ann_return_pct - ls_raw_ann_return_pct |
| ho055_hedged_m | 45 | run 055 ls_hedged_months |
| ho055_ic | 0.0300 | run 055 ic_mean |
| ho055_raw | 3.01 | run 055 ls_raw_ann_return_pct |
| ho055_raw_mdd | -51.84 | run 055 ls_raw_maxdd_pct |
| ho055_ret | 12.20 | run 055 ls_ann_return_pct |
| ho055_sh | 0.584 | run 055 ls_sharpe |
| ho_2022_h | +60.0 | 056 equal_rank_decile annual 2022 |
| ho_2022_ic | +0.105 | 054 summary annual IC 2022 |
| ho_bear_m | 12 | manifest v14 holdout.holdout_detail.bear_bull.holdout_months_bear_bull_054[0] (trailing-12m market down) |
| ho_benchmark_h2 | 0.0283 | run 053 ic_half2_mean (decision holdout_expectations_v14_spend_snapshot) |
| ho_beta_exante | -0.549 | run 054 cut_holdout_ls_beta_mean |
| ho_beta_exante2 | -0.55 | run 054 cut_holdout_ls_beta_mean |
| ho_beta_exante_055 | -0.504 | run 055 ls_beta_mean |
| ho_beta_gap | 0.287 | run 054 cut_holdout_ls_beta_mean - run 055 ls_beta_fullwindow |
| ho_beta_gap2 | 0.29 | run 054 cut_holdout_ls_beta_mean - run 055 ls_beta_fullwindow |
| ho_beta_last | -1.108 | run 054 ls_beta_last |
| ho_beta_real | -0.836 | run 055 ls_beta_fullwindow (holdout-only run, 57 months) |
| ho_beta_real2 | -0.84 | run 055 ls_beta_fullwindow |
| ho_bull_m | 45 | manifest v14 holdout.holdout_detail.bear_bull.holdout_months_bear_bull_054[1] (trailing-12m market up) |
| ho_d1 | 0.406 | run 055 decile_avg_ret_pct D1 |
| ho_d2_d10_max | 0.712 | run 055 decile_avg_ret_pct max of D2..D10 |
| ho_d2_d10_min | 0.629 | run 055 decile_avg_ret_pct min of D2..D10 |
| ho_ex3_h | -0.572 | run 055 ls_sharpe_ex_top_years |
| ho_ex3_x | -0.708 | run 054 cut_holdout_ls_excess_sharpe_ex_top_years |
| ho_ex_ret | 8.54 | run 054 cut_holdout_ls_excess_ann_return_pct |
| ho_ex_sh | 0.413 | run 054 cut_holdout_ls_excess_sharpe |
| ho_ex_t | 0.93 | run 054 cut_holdout_ls_excess_tstat_nw |
| ho_first_ts | 2026-10-02T01:09:09Z | events run_started 054 ts |
| ho_h_mdd | -35.65 | run 054 cut_holdout_ls_maxdd_pct |
| ho_h_ret | 10.81 | run 054 cut_holdout_ls_ann_return_pct |
| ho_h_sh | 0.523 | run 054 cut_holdout_ls_sharpe |
| ho_h_t | 1.18 | run 054 cut_holdout_ls_tstat_nw |
| ho_ic | 0.0300 | run 054 cut_holdout_ic_mean |
| ho_ic3 | 0.030 | run 054 cut_holdout_ic_mean |
| ho_ic_h1_055 | 0.0567 | run 055 ic_half1_mean |
| ho_ic_h2_055 | 0.0043 | run 055 ic_half2_mean |
| ho_ic_share_full | 77 | 100 x run 054 cut_holdout_ic_mean / run 053 ic_mean |
| ho_ic_t | 1.87 | run 054 cut_holdout_ic_tstat_nw |
| ho_n | 57 | run 054 cut_holdout_n_months |
| ho_p1 | 0.030 | one-sided normal p of run 054 cut_holdout_ic_tstat_nw |
| ho_p2 | 0.061 | two-sided normal p of run 054 cut_holdout_ic_tstat_nw |
| ho_raw_ret | 3.01 | run 054 cut_holdout_ls_raw_ann_return_pct |
| ho_raw_ret1 | 3.0 | run 054 cut_holdout_ls_raw_ann_return_pct |
| ho_raw_sh | 0.124 | run 054 cut_holdout_ls_raw_sharpe |
| ho_rf_credit | -2.26 | run 054 cut_holdout_ls_rf_credit_pp |
| ho_top_ic_year | 2022 | year of the largest holdout annual IC (054 summary) |
| ho_top_years | 2022,2024,2026 | run 054 cut_holdout_ls_excess_top_years |
| hx_text | Rule: D8 reads the holdout against the live version's in-window figures on the spend snapshot. On DATA 42587e08609a (run 053, in-window 1999-2021, v14): hedged LS Sharpe 0.9964 (ann 16.34%); ex-top-3-years Sharpe 0.6665 (2000, 2001, 2021); excess-of-rf hedged Sharpe 0.9285 (ann 15.09%); excess ex-top-3-years Sharpe 0.6045; mean IC 0.0389 full window, 0.0283 second half (benchmark the holdout IC against the second half); raw Sharpe 0.7902; layer run 049 net Sharpe -0.06 @100M (old bytes, measured CS). The run-042 expectations stay as history. Written before any out-of-sample number; no bar. | events decision holdout_expectations_v14_spend_snapshot (verbatim) |
| hx_ts | 2026-10-02T00:14:32Z | events decision holdout_expectations_v14_spend_snapshot ts |
| identity_maxgap | 0.005 | max \|difference\| in table 07b |
| ivol_hedge_part | -0.03 | events factor_evaluated IdioVol3F stage 2 raw_vs_hedged_dls_pp.hedge_part |
| iw_bear | 1.257 | run 053 ls_sharpe_bear |
| iw_beta_exante | -0.540 | run 053 ls_beta_mean |
| iw_beta_fw | -0.556 | run 053 ls_beta_fullwindow |
| iw_beta_fw2 | -0.56 | run 053 ls_beta_fullwindow |
| iw_bull | 1.115 | run 053 ls_sharpe_bull |
| iw_ex_ret | 15.09 | run 053 ls_excess_ann_return_pct |
| iw_ex_sh | 0.928 | run 053 ls_excess_sharpe |
| iw_ex_t | 3.75 | run 053 ls_excess_tstat_nw |
| iw_ex_top3 | 0.605 | run 053 ls_excess_sharpe_ex_top_years |
| iw_h_mdd | -43.23 | run 053 ls_maxdd_pct |
| iw_h_ret | 16.34 | run 053 ls_ann_return_pct |
| iw_h_sh | 0.996 | run 053 ls_sharpe |
| iw_h_t | 3.96 | run 053 ls_tstat_nw |
| iw_ic | 0.0389 | run 053 ic_mean |
| iw_ic_h1 | 0.0496 | run 053 ic_half1_mean |
| iw_ic_h2 | 0.0283 | run 053 ic_half2_mean |
| iw_ic_plain_t | 6.43 | run 053 ic_tstat |
| iw_ic_t | 5.68 | run 053 ic_tstat_nw |
| iw_mdd | -43.23 | run 053 ls_maxdd_pct |
| iw_n | 276 | run 053 n_months |
| iw_raw_mdd | -44.93 | run 053 ls_raw_maxdd_pct |
| iw_raw_ret | 14.91 | run 053 ls_raw_ann_return_pct |
| iw_raw_sh | 0.790 | run 053 ls_raw_sharpe |
| iw_rf_credit | -1.25 | run 053 ls_rf_credit_pp |
| iw_to | 58.1 | run 053 turnover_d10_pct |
| iw_top3 | 0.666 | run 053 ls_sharpe_ex_top_years |
| iw_top_share | 53.6 | run 053 ls_top_years_share_pct |
| iw_top_years | 2000,2001,2021 | run 053 ls_top_years |
| journal_phaseB_h | 4.9 | docs/JOURNAL.md Phase B entry |
| l49_beta | -0.101 | run 049 layer@100M net_beta_on_market |
| l49_bias | 2.58 | run 049 layer@100M bias_stat_mean |
| l49_bias_band | 20.5 | run 049 layer@100M bias_stat_in_band_pct |
| l49_book | 2001-01 | run 049 layer@100M book_start |
| l49_book_end | 2021-12 | run 049 layer@100M book_end |
| l49_borrow | 0.19 | run 049 layer@100M cost_borrow_ann_pct |
| l49_cost | 4.36 | run 049 layer@100M cost_total_ann_pct |
| l49_erd_gross | 12.52 | run 049 equal_rank_decile@100M gross_ann_return_pct |
| l49_erd_gross_sh | 0.793 | run 049 equal_rank_decile@100M gross_sharpe |
| l49_erd_to | 117.7 | run 049 equal_rank_decile@100M turnover_oneway_pct |
| l49_exante_vol | 1.97 | run 049 layer@100M exante_vol_ann_pct_mean |
| l49_fts_net_sh | 0.502 | run 049 layer_fixed_tier_spread@100M net_sharpe |
| l49_g2001 | +23.6 | run 049 layer@100M annual_gross_returns_pct 2001 |
| l49_g2002 | +20.3 | run 049 layer@100M annual_gross_returns_pct 2002 |
| l49_gross | 4.08 | run 049 layer@100M gross_ann_return_pct |
| l49_gross_t | 3.27 | run 049 layer@100M gross_tstat_nw |
| l49_impact | 0.79 | run 049 layer@100M cost_impact_ann_pct |
| l49_n2001 | +15.8 | run 049 layer@100M annual_net_returns_pct 2001 |
| l49_n2002 | +14.0 | run 049 layer@100M annual_net_returns_pct 2002 |
| l49_nbc_beta | -0.135 | run 049 layer_no_beta_constraint@100M net_beta_on_market |
| l49_nbc_gross | 4.39 | run 049 layer_no_beta_constraint@100M gross_ann_return_pct |
| l49_nbc_gross_sh | 0.805 | run 049 layer_no_beta_constraint@100M gross_sharpe |
| l49_net | -0.29 | run 049 layer@100M net_ann_return_pct |
| l49_net_1b | -0.409 | run 049 layer@1000M net_sharpe |
| l49_net_5b | -0.870 | run 049 layer@5000M net_sharpe |
| l49_net_sh | -0.060 | run 049 layer@100M net_sharpe |
| l49_real_vol | 4.78 | run 049 layer@100M realised_vol_ann_pct_live |
| l49_spread | 3.39 | run 049 layer@100M cost_spread_ann_pct |
| l49_to | 36.0 | run 049 layer@100M turnover_oneway_pct |
| l57_bias_full | 3.12 | run 057 layer@100M bias_stat_mean (book 2001-01..2026-09) |
| l57_book | 2001-01..2026-09 | run 057 layer@100M book_start, book_end |
| l57_book_n | 309 | run 057 layer@100M n_months |
| l57ho_cost | 3.40 | run 057 layer@100M cut_holdout_cost_total_ann_pct |
| l57iw_gross | 4.15 | run 057 layer@100M cut_inwindow_gross_ann_return_pct |
| l57iw_net_sh | -0.022 | run 057 layer@100M cut_inwindow_net_sharpe |
| ladder_max | 5 | config search.stage2_ladder_max_rungs |
| ladder_runs | 012, 023, 032, 037, 044 | registry stage2_run over the 24 Stage 2 rows |
| layer_canon_neg_all | yes | runs 049 net_sharpe, 057 cut_inwindow_net_sharpe and cut_holdout_net_sharpe for layer@100M/1000M/5000M |
| layer_ho_gross_ret | 0.74 | run 057 layer@100M cut_holdout_gross_ann_return_pct |
| layer_ho_gross_sh | 0.101 | run 057 layer@100M cut_holdout_gross_sharpe |
| layer_ho_net_ret | -2.66 | run 057 layer@100M cut_holdout_net_ann_return_pct |
| layer_ho_net_sh | -0.367 | run 057 layer@100M cut_holdout_net_sharpe |
| layer_iw057_gross_sh3 | 0.856 | run 057 layer@100M cut_inwindow_gross_sharpe |
| layer_iw_gross_sh | 0.86 | run 049 layer@100M gross_sharpe |
| layer_iw_gross_sh3 | 0.856 | run 049 layer@100M gross_sharpe |
| leak_ids | book_equity_preferred_terms, scratchpad_glob_other-project_names, leak_sweep_phase_d_close, construction_md_other-project_caveat, d7_other-project_outcome_clause, d8_other-project_restatement_figure | process_findings whose record text refers to another project (ids masked) |
| legs_1999 | 15 | table 06f 1999 January |
| man_comp_text | 2003-2020 compounds to -36% net (+38% gross, 1.9%/yr) | manifest v14 construction_layer.character (verbatim) |
| min_guard_f | RoE | factor with the lowest guard t |
| min_guard_t | -1.26 | registry RoE stage2.paired_delta_ls_tstat (lowest guard t) |
| min_months | 120 | config rebalance.min_months |
| min_names_group | 10 | config ranking.min_names_per_group |
| miss0 | IdioVolAHT | table 05c |
| miss0_t | 1.92 | registry IdioVolAHT stage2.resid_ic_tstat_nw |
| miss1 | ShareIss1Y | table 05c |
| miss1_t | 1.88 | registry ShareIss1Y stage2.resid_ic_tstat_nw |
| mkt_state_lb | 12 | config diagnostics.market_state_lookback_months |
| model_advisor | Claude Fable 5.1 | docs/JOURNAL.md 'snapshot recorded' entry |
| model_bootstrap | Claude Fable 5.1 | docs/JOURNAL.md bootstrap entry |
| model_runner | Claude Opus 5.5 | docs/JOURNAL.md 'snapshot recorded' entry |
| mr_hedge_part | 2.82 | events factor_evaluated MaxRet raw_vs_hedged_dls_pp.hedge_part |
| mr_hedged_dls | 2.23 | events factor_evaluated MaxRet stage 2 raw_vs_hedged_dls_pp.hedged |
| mr_raw_dls | -0.59 | events factor_evaluated MaxRet raw_vs_hedged_dls_pp.raw |
| mr_resid_t | 4.01 | registry MaxRet stage2.resid_ic_tstat_nw |
| n_advisor | 6 | rows of table 10e |
| n_alpha_critical | 1 | sum of critical findings over events alpha_review |
| n_alpha_phaseA | 20 | events alpha_review before phase_completed A |
| n_alpha_reviews | 23 | events alpha_review |
| n_cfg_shas | 1 | distinct config_sha over every run_started event |
| n_composite_moves | 14 | events composite_updated minus the v0 recording |
| n_composite_versions | 15 | events composite_updated (one per version v0-v14) |
| n_config_moves | 1 | events config_changed with a SHA |
| n_decisions | 11 | docs/DECISIONS.md D headings |
| n_events | 1134 | research/events.jsonl rows |
| n_fail_by_t | 79 | registry FAIL rows decided_by ic_tstat_nw |
| n_families | 9 | distinct families in table 04 |
| n_family_assigned | 24 | events family_assigned |
| n_feasible | 134 | events inventory_classified n_feasible |
| n_finding_corrected | 15 | events finding_corrected |
| n_flip_qualified | 2 | events flip_hypothesis_qualified |
| n_flip_screens | 1 | registry Stage 1 rows named *Flip |
| n_fr_data_start | 9 | osap_frontier.yaml rows with class data_start |
| n_fr_data_unavailable | 64 | osap_frontier.yaml rows with class data_unavailable |
| n_fr_preflight_failed | 28 | osap_frontier.yaml rows with class preflight_failed |
| n_frontier | 101 | osap_source/osap_frontier.yaml excluded rows |
| n_guard_fail | 0 | Stage 2 rows with paired_delta_ls_tstat < -2.0 |
| n_harness_moves | 5 | events harness_changed with a SHA |
| n_ho_years | 5 | 054 summary annual IC years >= 2022 |
| n_ho_years_left | 2 | holdout calendar years minus top_years_k |
| n_ic_years | 23 | run 053 summary annual IC years |
| n_index_gaps | 0 | Stage 2 rows of registry_index missing resid_t/dls_t/beta/sh_exreg/family/decided_by |
| n_index_s2 | 24 | registry_index rows with a stage2_run |
| n_infeasible | 73 | events inventory_classified n_infeasible |
| n_labels | 11 | distinct SignalDoc Cat.Economic labels in table 04 (seed labels plus passer labels) |
| n_ladders | 5 | distinct stage2_run |
| n_layer_rows | 33 | run 049 result blocks |
| n_leak_findings | 6 | process_findings whose record text refers to another project |
| n_neg_ic_years | 3 | run 053 summary annual IC printed with a minus sign |
| n_osap | 212 | events inventory_classified n_predictors |
| n_pf_failed | 28 | events inventory_classified n_preflight_failed |
| n_pos_fixed | 4 | rows of table 07e with half_spread_mode fixed |
| n_pos_layer_rows | 9 | count of rows in table 07e |
| n_pos_layer_rows_ho | 0 | count of 057 holdout rows in table 07e |
| n_pos_measured | 5 | rows of table 07e with half_spread_mode measured |
| n_process_findings | 31 | events process_finding |
| n_runs_completed | 56 | events run_completed |
| n_runs_started | 57 | run_started events |
| n_s1_fail | 83 | registry rows with stage1_decision FAIL |
| n_s1_incon | 0 | registry_index search_accounting n_inconclusive |
| n_s1_pass | 24 | registry rows with stage1_decision PASS |
| n_s2 | 24 | Stage 2 rows |
| n_s2_acc | 14 | Stage 2 rows ratchet_decision PASS |
| n_s2_incon | 0 | registry_index n_inconclusive |
| n_s2_rej | 10 | Stage 2 rows ratchet_decision FAIL |
| n_screened | 107 | registry rows with stage1_decision PASS/FAIL (= registry_index n_stage1_tested) |
| n_seed | 5 | events inventory_classified n_baseline_legs |
| n_sharadar_tables | 13 | events snapshot_recorded #1 tables |
| n_snapshot_moves | 2 | events snapshot_recorded |
| n_spec_distinct | 207 | distinct factors over events spec_written |
| n_t_pass_other_fail | 4 | rows in table 03c |
| n_translated | 106 | events inventory_classified n_translated |
| n_translated_distinct | 108 | distinct factors over events factor_translated |
| neg_ic_years | 2003 (-0.000), 2007 (-0.016), 2020 (-0.049) | run 053 summary annual IC printed with a minus sign |
| null_e1 | 0.658 | null_n x null_p25 |
| null_e2 | 0.326 | null_n x null_p274 |
| null_e3 | 0.546 | n_stage2_tested x null_p20 |
| null_etot | 0.984 | null_e1 + null_e2 |
| null_n | 106 | registry Stage 1 rows in the published sign |
| null_obs_t25 | 27 | registry Stage 1 rows (published sign) with ic_tstat_nw >= 2.5 |
| null_p20 | 0.022750 | 0.5 erfc(2.0/sqrt 2) |
| null_p25 | 0.006210 | 0.5 erfc(2.5/sqrt 2) |
| null_p274 | 0.003072 | 0.5 erfc(2.74/sqrt 2) |
| nw_lags | 3 | config statistics.newey_west_lags |
| oos_end | 2026-09-30 | config dates.out_of_sample_end |
| oos_start | 2022-01-01 | config dates.out_of_sample_start |
| osap_ref | b4e911e6 | config osap_source.ref |
| osap_tag | v2.0.0 | config osap_source.tag |
| owner_sa3 | approve both, use TB3MS for rf | events decision owner_stop_and_ask_3_approved verbatim |
| owner_sa5 | Yes | events decision owner_stop_and_ask_5_approved verbatim |
| phaseB_h | 6.17 | sum of run_completed runtime_seconds, runs 003-011 / 3600 |
| phaseD_h | 7.19 | sum of run_completed runtime_seconds, runs 012-044 / 3600 |
| pos_measured_max | 0.058 | max net Sharpe over measured-spread rows of table 07e |
| pp_events | 105 | events preflight_passed |
| pp_implied | AM, Accruals | screened candidates whose preflight is recorded inside factor_translated (RECORDS.md: a pass is implied) |
| pp_multi | BidAskSpreadFlip | events preflight_passed with a factors list |
| pp_single | 104 | events preflight_passed with a single factor |
| repro_fields | 66/66 | events phase_completed D digest |
| restate_dic | -0.000009 | run 053 ic_mean - run 052 ic_mean |
| restate_dt | -0.0019 | run 053 ic_tstat_nw - run 052 ic_tstat_nw |
| restate_moved | 54 | run 052 vs 053 result-block fields, different (includes data_sha) |
| restate_new | 8 | run 053 fields absent from 052 (the excess-of-rf diagnostic) |
| restate_same | 28 | run 052 vs 053 result-block fields, identical |
| roaq_hedge_part | +0.51 | events factor_evaluated roaq stage 2 raw_vs_hedged_dls_pp.hedge_part |
| s1_batch | 12 | config search.stage1_batch_size |
| s2_rej_bars | resid_ic_tstat_nw | decided_by over Stage 2 FAIL rows |
| seed_ic_Investment | 0.0054 | run 051 legic_f_inv_close |
| seed_ic_Momentum | 0.0096 | run 051 legic_f_mom_close |
| seed_ic_Profitability | 0.0205 | run 051 legic_f_prof_close |
| seed_ic_Size | -0.0093 | run 051 legic_f_size_close |
| seed_ic_Value | 0.0058 | run 051 legic_f_value_close |
| seed_t_Investment | 1.21 | run 051 legic_f_inv_close_t |
| seed_t_Momentum | 1.27 | run 051 legic_f_mom_close_t |
| seed_t_Profitability | 3.78 | run 051 legic_f_prof_close_t |
| seed_t_Size | -1.53 | run 051 legic_f_size_close_t |
| seed_t_Value | 0.85 | run 051 legic_f_value_close_t |
| sh052 | 0.983 | run 052 ls_sharpe |
| sig_IdioVol3F | 1999-07 | table 06e first signal month-end of IdioVol3F |
| sig_ShareIss5Y | 2003-05 | table 06e first signal month-end of ShareIss5Y |
| sig_TrendFactor | 2002-12 | table 06e first signal month-end of TrendFactor |
| sig_VolumeTrend | 2002-12 | table 06e first signal month-end of VolumeTrend |
| skip1_close_ic | 0.0389 | run 050 ic_mean |
| skip1_dic | -0.0044 | run 051 paired_dic_mean |
| skip1_dic_t | -3.06 | run 051 paired_dic_tstat_nw |
| skip1_h2 | 0.0270 | run 051 ic_half2_mean |
| skip1_ic | 0.0346 | run 051 ic_mean |
| skip1_sh | 0.777 | run 051 ls_sharpe |
| skip1_share | 11 | 100 x -run 051 paired_dic_mean / run 050 ic_mean |
| snap1_recorded | 2026-09-30T16:39:10Z | git d477021^:data/SNAPSHOT_MANIFEST.yaml recorded_on |
| snap1_sep_max | 2026-09-29 | git d477021^:data/SNAPSHOT_MANIFEST.yaml tables.SEP.max_date (the frozen manifest before the refresh) |
| snap2_recorded | 2026-10-01T23:26:28Z | data/SNAPSHOT_MANIFEST.yaml recorded_on |
| spent_on | 2026-10-02 | MODEL_MANIFEST.yaml holdout.spent_on |
| spread_measured | 99.95 | run 049 layer@100M spread_measured_pct |
| start_IdioVol3F | 1999-08 | table 06e first holding month of IdioVol3F |
| start_ShareIss5Y | 2003-06 | table 06e first holding month of ShareIss5Y |
| start_TrendFactor | 2003-01 | table 06e first holding month of TrendFactor |
| start_VolumeTrend | 2003-01 | table 06e first holding month of VolumeTrend |
| str_hedge_part | -1.73 | events factor_evaluated STreversal stage 2 raw_vs_hedged_dls_pp.hedge_part |
| tf_hedge_part | -0.77 | events factor_evaluated TrendFactor stage 2 raw_vs_hedged_dls_pp.hedge_part |
| thin0 | IdioVol3F | table 05c |
| thin0_t | 2.03 | registry IdioVol3F stage2.resid_ic_tstat_nw |
| thin1 | VolumeTrend | table 05c |
| thin1_t | 2.04 | registry VolumeTrend stage2.resid_ic_tstat_nw |
| top_years_k | 3 | config diagnostics.ex_regime_top_years |
| translated_unscreened | DelDRC, EarnSupBig | factor_translated factors without a registry row (failed preflight; frontier) |
| ts_est_rows | 219-419 | finding_corrected events_ts_estimated and events_ts_estimated_row |
| v0_beta | -0.140 | manifest v0 baseline.beta.ls_beta_fullwindow (run 001) |
| v0_ic | 0.0145 | manifest v0 baseline.ic.ic_mean (run 001) |
| v0_ic_t | 2.62 | manifest v0 baseline.ic.ic_tstat_nw (run 001) |
| v0_sh | 0.600 | manifest v0 baseline.ls_hedged.ls_sharpe (run 001) |
| v0_to | 28.0 | manifest v0 baseline.breadth.turnover_d10_pct (run 001) |
| v10_sh | 0.919 | manifest v10 baseline.ls_hedged.ls_sharpe (run 033) |
| v14_fams | 9 | manifest v14 families |
| v14_legs | 19 | manifest v14 legs |
| v14_sha | 7fe6f001e708 | manifest v14 stamps.composite_sha |
| v14a_beta | -0.560 | manifest v14 baseline.beta.ls_beta_fullwindow (run 042) |
| v14a_ic | 0.0389 | manifest v14 baseline.ic.ic_mean (run 042) |
| v14a_ic_t | 5.68 | manifest v14 baseline.ic.ic_tstat_nw (run 042) |
| v14a_sh | 0.983 | manifest v14 baseline.ls_hedged.ls_sharpe (run 042) |
| v14a_to | 58.1 | manifest v14 baseline.breadth.turnover_d10_pct (run 042) |
| v9_sh | 0.932 | manifest v9 baseline.ls_hedged.ls_sharpe (run 030) |
| wall_hours | 21.9 | sum of run_completed runtime_seconds / 3600 |
| wall_seconds | 78885.2 | sum of run_completed runtime_seconds |
| zt6_hedge_part | +0.90 | events factor_evaluated zerotrade6M stage 2 raw_vs_hedged_dls_pp.hedge_part |

## Appendix B. Record dumps

### B1. The construction layer, all rows (run 049)

*Table 07_layer049. Construction layer on v14, in-window book 2001-01..2021-12 (252 months), pre-refresh bytes. Source: run 049 result blocks (HARNESS 3561590b660a, LAYER 4b279fc317cd). Costs in %/yr; equal_rank_decile and buffered are the Stage 3 books unhedged under the same cost model.*

| AUM | variant | gross ann % | gross Sharpe | spread | impact | borrow | total cost | net ann % | net Sharpe | net NW t | one-way turnover % | net beta on M |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| $100M | layer | 4.08 | 0.856 | 3.39 | 0.79 | 0.19 | 4.36 | -0.29 | -0.060 | -0.24 | 36.0 | -0.101 |
| $100M | layer_eta_0.25 | 4.08 | 0.857 | 3.39 | 0.40 | 0.19 | 3.97 | 0.11 | 0.023 | 0.09 | 36.0 | -0.101 |
| $100M | layer_eta_1 | 4.08 | 0.857 | 3.39 | 1.58 | 0.19 | 5.16 | -1.08 | -0.227 | -0.90 | 36.0 | -0.101 |
| $100M | layer_fixed_tier_spread | 4.06 | 0.854 | 0.71 | 0.79 | 0.19 | 1.69 | 2.37 | 0.502 | 1.94 | 36.0 | -0.101 |
| $100M | layer_exec_half_month | 2.98 | 0.662 | 3.39 | 0.79 | 0.19 | 4.36 | -1.38 | -0.308 | -1.22 | 36.0 | -0.099 |
| $100M | layer_tiered_borrow | 4.08 | 0.856 | 3.39 | 0.79 | 0.89 | 5.06 | -0.99 | -0.208 | -0.82 | 36.0 | -0.101 |
| $100M | layer_no_buffer | 6.38 | 1.068 | 8.42 | 2.79 | 0.24 | 11.45 | -5.07 | -0.843 | -3.39 | 90.7 | -0.114 |
| $100M | layer_no_beta_constraint | 4.39 | 0.805 | 3.33 | 0.77 | 0.19 | 4.29 | 0.10 | 0.018 | 0.07 | 35.5 | -0.135 |
| $100M | layer_dollar_neutral_only | 4.43 | 0.820 | 3.31 | 0.75 | 0.19 | 4.25 | 0.18 | 0.034 | 0.13 | 34.9 | -0.127 |
| $100M | equal_rank_decile | 12.52 | 0.793 | 12.65 | 7.56 | 0.25 | 20.47 | -7.95 | -0.507 | -2.02 | 117.7 | -0.454 |
| $100M | buffered | 11.27 | 0.736 | 8.40 | 4.38 | 0.25 | 13.04 | -1.77 | -0.116 | -0.47 | 77.9 | -0.474 |
| $1000M | layer | 4.08 | 0.857 | 3.38 | 2.45 | 0.19 | 6.01 | -1.93 | -0.409 | -1.63 | 35.9 | -0.101 |
| $1000M | layer_eta_0.25 | 4.08 | 0.857 | 3.38 | 1.22 | 0.19 | 4.79 | -0.71 | -0.150 | -0.59 | 35.9 | -0.101 |
| $1000M | layer_eta_1 | 4.09 | 0.857 | 3.38 | 4.91 | 0.19 | 8.47 | -4.39 | -0.927 | -3.73 | 36.0 | -0.101 |
| $1000M | layer_fixed_tier_spread | 4.07 | 0.856 | 0.71 | 2.45 | 0.19 | 3.34 | 0.73 | 0.156 | 0.61 | 35.9 | -0.101 |
| $1000M | layer_exec_half_month | 2.98 | 0.662 | 3.38 | 2.45 | 0.19 | 6.01 | -3.03 | -0.678 | -2.72 | 35.9 | -0.098 |
| $1000M | layer_tiered_borrow | 4.08 | 0.856 | 3.38 | 2.45 | 0.89 | 6.72 | -2.64 | -0.559 | -2.23 | 35.9 | -0.101 |
| $1000M | layer_no_buffer | 6.23 | 1.046 | 8.30 | 8.10 | 0.23 | 16.63 | -10.40 | -1.705 | -6.83 | 89.2 | -0.113 |
| $1000M | layer_no_beta_constraint | 4.39 | 0.804 | 3.33 | 2.40 | 0.19 | 5.91 | -1.52 | -0.280 | -1.14 | 35.4 | -0.136 |
| $1000M | layer_dollar_neutral_only | 4.43 | 0.820 | 3.30 | 2.34 | 0.19 | 5.83 | -1.40 | -0.257 | -0.99 | 34.8 | -0.126 |
| $1000M | equal_rank_decile | 12.52 | 0.793 | 12.77 | 24.28 | 0.25 | 37.30 | -24.78 | -1.587 | -6.37 | 118.7 | -0.446 |
| $1000M | buffered | 11.27 | 0.736 | 8.45 | 13.98 | 0.25 | 22.68 | -11.41 | -0.754 | -3.08 | 78.4 | -0.470 |
| $5000M | layer | 3.79 | 0.819 | 3.20 | 4.43 | 0.18 | 7.81 | -4.02 | -0.870 | -3.49 | 34.1 | -0.097 |
| $5000M | layer_eta_0.25 | 3.78 | 0.818 | 3.20 | 2.21 | 0.18 | 5.59 | -1.81 | -0.393 | -1.56 | 34.1 | -0.097 |
| $5000M | layer_eta_1 | 3.82 | 0.822 | 3.21 | 8.88 | 0.18 | 12.27 | -8.46 | -1.800 | -7.22 | 34.2 | -0.098 |
| $5000M | layer_fixed_tier_spread | 3.78 | 0.818 | 0.66 | 4.42 | 0.18 | 5.26 | -1.48 | -0.324 | -1.29 | 34.1 | -0.097 |
| $5000M | layer_exec_half_month | 2.78 | 0.630 | 3.20 | 4.43 | 0.18 | 7.81 | -5.04 | -1.144 | -4.64 | 34.1 | -0.094 |
| $5000M | layer_tiered_borrow | 3.79 | 0.820 | 3.20 | 4.43 | 0.86 | 8.49 | -4.70 | -1.017 | -4.08 | 34.1 | -0.097 |
| $5000M | layer_no_buffer | 5.37 | 0.985 | 7.18 | 11.85 | 0.22 | 19.25 | -13.89 | -2.473 | -9.91 | 77.6 | -0.103 |
| $5000M | layer_no_beta_constraint | 4.17 | 0.783 | 3.16 | 4.38 | 0.18 | 7.72 | -3.55 | -0.667 | -2.73 | 33.7 | -0.133 |
| $5000M | layer_dollar_neutral_only | 4.25 | 0.816 | 3.16 | 4.33 | 0.19 | 7.68 | -3.43 | -0.652 | -2.53 | 33.3 | -0.119 |
| $5000M | equal_rank_decile | 12.52 | 0.793 | 13.02 | 56.14 | 0.25 | 69.42 | -56.90 | -3.345 | -11.87 | 121.0 | -0.428 |
| $5000M | buffered | 11.27 | 0.736 | 8.55 | 31.83 | 0.25 | 40.63 | -29.36 | -1.908 | -7.65 | 79.3 | -0.463 |

### B2. Process findings

*Table 09b_process_findings. Every process_finding. Source: events `process_finding` (text truncated at 200 characters; ids with the other project's name have that word masked as `other-project`; clauses that refer to another project are omitted and pointed to by line). 'LESSONS n' in a note refers to research/LESSONS.md, the project's methodology file; it is cited there for method, not for any predictor's outcome.*

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
| 1064 | 2026-10-01 | construction_md_other-project_caveat | contradicted here (run 042 ls_sharpe_ex_top_years 0.65); removed in the D7 edit [1 clause(s) omitted: refer to another project; events.jsonl line 1064] |
| 1070 | 2026-10-01 | d7_other-project_outcome_clause | CONSTRUCTION.md sentence replaced by the design reason; D7 annotated with a dated governing note (decision text not rewritten); docs are unstamped, no SHA moves |
| 1087 | 2026-10-01 | d8_other-project_restatement_figure | dated governing note added under D8; decision text not rewritten |
| 1129 | 2026-10-02 | stage3_holdout_cuts_absent | not re-run: the block is spent once (D8); the gap is disclosed in the manifest and the paper |

### B3. Findings corrected

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
| 1133 | 2026-10-02 | manuscript_draft_audit | five questions (1, 2, 3, 5, 6) in three owner answers (events 9-10, 1097, 1109); hedge term = long market position at ex-ante beta -0.549 in a rising market, the lag to realised -0.836 under-hedged; r … |

### B4. Verifications

*Table 09d_verifications. Every verification_completed. Source: events `verification_completed` (text truncated at 200 characters).*

| events line | date | subject | detail (record text) |
|---|---|---|---|
| 8 | 2026-09-30 | bootstrap | snapshot not pulled (key file placed after the last commit; snapshot.py probe: key OK, 13 tables entitled) [1 clause(s) omitted: refer to another project; events.jsonl line 8] |
| 573 | 2026-09-30 | stray post-BME rows in the monthly panel | scratch count over SEP (37.6M rows) and DAILY (33.1M rows) 1997-12..2021-12: 0 rows dated after their calendar month's business month-end; build_monthly_panel's tail(1) therefore always takes a row on … |
| 704 | 2026-10-01 | hedge_gap_check_before_phase_d | independent rebuild of AM, BMdec, BookLeverage, CBOperProf hedged LS matches run 003 blocks to ~1e-15; beta_t on t-36..t-1 only (look-ahead and stale windows do not match); market proxy = cap-weighted … |
| 877 | 2026-10-01 | stage2_new_family_blend | drive_stage2 builds trial = cur_meta + [candidate meta]; family_members/blend_family_ranks derive families from the trial metas; tests/test_composite.py::test_a_candidate_opening_a_new_family_gets_a_f … |
| 1057 | 2026-10-01 | phase_d_close_checks | 15 tags v0..v14; v2..v14 each on its 'ratchet: vN' commit; v1 mis-pointed (open, owner); families.yaml accepted members == composite.families() on all 9 families (19 legs); every passer's registry fam … |
| 1085 | 2026-10-01 | weekend_print_after_signal_asof | cached monthly panel fb86ececd100, me 1998-12..2021-12: 1,711,671 ID-months, 0 with last SEP date > me; the alpha_review minor does not bite in-window; no logged row affected |

### B5. Findings confirmed

*Table 09e_findings_confirmed. Every finding_confirmed. Source: events `finding_confirmed` (text truncated at 200 characters). The skip1 row's text rounds the composite IC and the paired t as 0.0346 and -3.07; the run 051 block gives 0.034550 and -3.064867 (0.0346 and -3.06, half-up), which the paper uses.*

| events line | date | subject | evidence (record text) |
|---|---|---|---|
| 28 | 2026-09-30 | records_py_phase_gate_and_frontier | phase_gate now skips run_started rows with factors/label 'baseline'; osap_frontier matches registry rows on osap_acronym (leg Investment.yaml = AssetGrowth). frontier UNACCOUNTED 206 -> 207, Investmen … |
| 29 | 2026-09-30 | performance_delisting_count | ACTIONS 1999-01..2022-01: bankruptcyliquidation 2448, regulatorydelisting 507, delisted 13289; run 001 in-universe performance delistings 21. classify_delistings defaults unknown reasons to performanc … |
| 68 | 2026-09-30 | fundamentals_latest_datekey_staleness | alpha_review batch01 minors 1-2 measured at signals 1999-12, 2003-12, 2008-12, 2013-12, 2018-12, 2021-11: fundamentals() row older than fundamentals_history q_back0 reportperiod 0 of 1790-2610 names e … |
| 1096 | 2026-10-01 | skip1_return_start_sensitivity | diagnostic, never a bar. v14 close->skip1: IC 0.0389->0.0346 (paired delta -0.0044, NW t -3.07), NW t 5.68->5.16, halves 0.0498/0.0281->0.0421/0.0270, hedged Sharpe 0.983->0.777, raw 0.773->0.655, hed … |

### B6. Every run

*Table 10_runs. Every run. Source: events `run_started` and `run_completed` (runtime_seconds); run 046 has a `run_aborted` event and no runtime.*

| run | label | stage | started (UTC) | runtime s | HARNESS | CONFIG | COMPOSITE | DATA | factors |
|---|---|---|---|---|---|---|---|---|---|
| 001 | v0_baseline_stage2 | 2 | 2026-09-30T16:41:59Z | 121.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | baseline |
| 002 | v0_baseline_stage3 | 3 | 2026-09-30T16:44:54Z | 60.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | baseline |
| 003 | stage1_b1 | 1 | 2026-09-30T23:16:12Z | 1719.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 004 | stage1_b2 | 1 | 2026-09-30T23:45:20Z | 1161.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 005 | stage1_b3 | 1 | 2026-10-01T00:05:13Z | 1219.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 006 | stage1_b4 | 1 | 2026-10-01T00:25:50Z | 1780.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 007 | stage1_b5 | 1 | 2026-10-01T00:56:00Z | 5523.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 008 | stage1_b6 | 1 | 2026-10-01T02:28:31Z | 4016.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 009 | stage1_b7 | 1 | 2026-10-01T03:35:52Z | 1884.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 010 | stage1_b8 | 1 | 2026-10-01T04:07:40Z | 2872.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 12 factors |
| 011 | stage1_b9 | 1 | 2026-10-01T04:55:59Z | 2044.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | 11 factors |
| 012 | stage2_l1 | 2 | 2026-10-01T05:52:14Z | 224.0 | 73a95d352942 | 0d88328d5b10 | f9d9d9d95731 | 198b281de1a0 | PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN |
| 013 | v1_baseline_stage2 | 2 | 2026-10-01T06:09:17Z | 87.0 | 73a95d352942 | 0d88328d5b10 | cbeb16455bf4 | 198b281de1a0 | baseline |
| 014 | v1_baseline_stage3 | 3 | 2026-10-01T06:11:00Z | 90.0 | 73a95d352942 | 0d88328d5b10 | cbeb16455bf4 | 198b281de1a0 | baseline |
| 015 | v2_baseline_stage2 | 2 | 2026-10-01T06:20:47Z | 118.0 | 73a95d352942 | 0d88328d5b10 | 8b444636f0a1 | 198b281de1a0 | baseline |
| 016 | v2_baseline_stage3 | 3 | 2026-10-01T06:22:56Z | 123.0 | 73a95d352942 | 0d88328d5b10 | 8b444636f0a1 | 198b281de1a0 | baseline |
| 017 | v3_baseline_stage2 | 2 | 2026-10-01T06:30:54Z | 134.0 | 73a95d352942 | 0d88328d5b10 | 73ee92fe0723 | 198b281de1a0 | baseline |
| 018 | v3_baseline_stage3 | 3 | 2026-10-01T06:33:19Z | 133.0 | 73a95d352942 | 0d88328d5b10 | 73ee92fe0723 | 198b281de1a0 | baseline |
| 019 | v4_baseline_stage2 | 2 | 2026-10-01T06:41:25Z | 142.0 | 73a95d352942 | 0d88328d5b10 | 3329679c69fb | 198b281de1a0 | baseline |
| 020 | v4_baseline_stage3 | 3 | 2026-10-01T06:43:58Z | 147.0 | 73a95d352942 | 0d88328d5b10 | 3329679c69fb | 198b281de1a0 | baseline |
| 021 | v5_baseline_stage2 | 2 | 2026-10-01T06:52:15Z | 154.0 | 73a95d352942 | 0d88328d5b10 | d27916e567f2 | 198b281de1a0 | baseline |
| 022 | v5_baseline_stage3 | 3 | 2026-10-01T06:55:00Z | 159.0 | 73a95d352942 | 0d88328d5b10 | d27916e567f2 | 198b281de1a0 | baseline |
| 023 | stage2_l2 | 2 | 2026-10-01T07:03:31Z | 510.0 | 73a95d352942 | 0d88328d5b10 | d27916e567f2 | 198b281de1a0 | GP,ShareIss1Y,MaxRet,roaq,RoE |
| 024 | v6_baseline_stage2 | 2 | 2026-10-01T07:25:39Z | 163.0 | 73a95d352942 | 0d88328d5b10 | 21a6688ae5d1 | 198b281de1a0 | baseline |
| 025 | v6_baseline_stage3 | 3 | 2026-10-01T07:28:43Z | 167.0 | 73a95d352942 | 0d88328d5b10 | 21a6688ae5d1 | 198b281de1a0 | baseline |
| 026 | v7_baseline_stage2 | 2 | 2026-10-01T07:37:50Z | 366.0 | 73a95d352942 | 0d88328d5b10 | 43c92213ae73 | 198b281de1a0 | baseline |
| 027 | v7_baseline_stage3 | 3 | 2026-10-01T07:44:21Z | 370.0 | 73a95d352942 | 0d88328d5b10 | 43c92213ae73 | 198b281de1a0 | baseline |
| 028 | v8_baseline_stage2 | 2 | 2026-10-01T07:56:20Z | 391.0 | 73a95d352942 | 0d88328d5b10 | a12e87c5fb36 | 198b281de1a0 | baseline |
| 029 | v8_baseline_stage3 | 3 | 2026-10-01T08:03:02Z | 399.0 | 73a95d352942 | 0d88328d5b10 | a12e87c5fb36 | 198b281de1a0 | baseline |
| 030 | v9_baseline_stage2 | 2 | 2026-10-01T08:15:23Z | 405.0 | 73a95d352942 | 0d88328d5b10 | c961f5791816 | 198b281de1a0 | baseline |
| 031 | v9_baseline_stage3 | 3 | 2026-10-01T08:22:20Z | 411.0 | 73a95d352942 | 0d88328d5b10 | c961f5791816 | 198b281de1a0 | baseline |
| 032 | stage2_l3 | 2 | 2026-10-01T08:33:18Z | 944.0 | 73a95d352942 | 0d88328d5b10 | c961f5791816 | 198b281de1a0 | OperProfRD,IdioVol3F,NetEquityFinance,CF,STreversal |
| 033 | v10_baseline_stage2 | 2 | 2026-10-01T09:03:50Z | 603.0 | 73a95d352942 | 0d88328d5b10 | 1b4195ff18b4 | 198b281de1a0 | baseline |
| 034 | v10_baseline_stage3 | 3 | 2026-10-01T09:14:16Z | 609.0 | 73a95d352942 | 0d88328d5b10 | 1b4195ff18b4 | 198b281de1a0 | baseline |
| 035 | v11_baseline_stage2 | 2 | 2026-10-01T09:30:29Z | 793.0 | 73a95d352942 | 0d88328d5b10 | 335b06e3d608 | 198b281de1a0 | baseline |
| 036 | v11_baseline_stage3 | 3 | 2026-10-01T09:44:00Z | 799.0 | 73a95d352942 | 0d88328d5b10 | 335b06e3d608 | 198b281de1a0 | baseline |
| 037 | stage2_l4 | 2 | 2026-10-01T10:01:37Z | 3081.0 | 73a95d352942 | 0d88328d5b10 | 335b06e3d608 | 198b281de1a0 | 5 factors |
| 038 | v12_baseline_stage2 | 2 | 2026-10-01T11:25:18Z | 1088.0 | 73a95d352942 | 0d88328d5b10 | 612e59349f40 | 198b281de1a0 | baseline |
| 039 | v12_baseline_stage3 | 3 | 2026-10-01T11:44:20Z | 1073.0 | 73a95d352942 | 0d88328d5b10 | 612e59349f40 | 198b281de1a0 | baseline |
| 040 | v13_baseline_stage2 | 2 | 2026-10-01T12:09:19Z | 1805.0 | 73a95d352942 | 0d88328d5b10 | fa17bd1cd37e | 198b281de1a0 | baseline |
| 041 | v13_baseline_stage3 | 3 | 2026-10-01T12:40:00Z | 1816.0 | 73a95d352942 | 0d88328d5b10 | fa17bd1cd37e | 198b281de1a0 | baseline |
| 042 | v14_baseline_stage2 | 2 | 2026-10-01T13:16:33Z | 2407.0 | 73a95d352942 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 043 | v14_baseline_stage3 | 3 | 2026-10-01T13:57:21Z | 2405.0 | 73a95d352942 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 044 | stage2_l5 | 2 | 2026-10-01T14:43:48Z | 3757.9 | 73a95d352942 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | BidAskSpreadFlip,IdioVolAHT,zerotrade1M,NetPayoutYield |
| 045 | v14_baseline_stage2_harness_471f | 2 | 2026-10-01T17:04:10Z | 2430.0 | 471f70782486 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 046 | v14_baseline_stage3_harness_471f | 3 | 2026-10-01T17:07:15Z | aborted | 471f70782486 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 047 | v14_baseline_stage2_harness_3561 | 2 | 2026-10-01T18:44:13Z | 2421.7 | 3561590b660a | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 048 | v14_baseline_stage3_harness_3561 | 3 | 2026-10-01T18:44:13Z | 2428.6 | 3561590b660a | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 049 | v14_baseline_construction_layer | layer | 2026-10-01T18:47:31Z | 2473.6 | 3561590b660a | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 050 | v14_baseline_stage2_harness_aef4 | 2 | 2026-10-01T21:21:35Z | 2410.4 | aef490297071 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 051 | v14_baseline_skip1_diagnostic | 2 | 2026-10-01T21:21:35Z | 2418.7 | aef490297071 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 052 | v14_baseline_stage2_harness_1271 | 2 | 2026-10-01T23:07:10Z | 3597.4 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 198b281de1a0 | baseline |
| 053 | v14_baseline_stage2_d8_refresh | 2 | 2026-10-01T23:27:07Z | 2699.9 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 42587e08609a | baseline |
| 054 | v14_baseline_stage2_holdout_include | 2 | 2026-10-02T01:09:09Z | 3004.2 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 42587e08609a | baseline |
| 055 | v14_baseline_stage2_holdout_only | 2 | 2026-10-02T01:59:29Z | 637.0 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 42587e08609a | baseline |
| 056 | v14_baseline_stage3_holdout_include | 3 | 2026-10-02T02:10:24Z | 3002.5 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 42587e08609a | baseline |
| 057 | v14_baseline_layer_holdout_include | layer | 2026-10-02T03:00:42Z | 3088.3 | 1271266472a9 | 0d88328d5b10 | 7fe6f001e708 | 42587e08609a | baseline |

### B7. Every stamp move

*Table 10c_stamp_moves. Every stamp move. Source: events `harness_changed`, `config_changed`, `snapshot_recorded`, `composite_updated`, and finding_corrected bootstrap_stamps for the first commit (the two bootstrap rows that preceded it carry no SHA).*

| events line | ts (UTC) | event | old | new | reason (record text, truncated at 160) |
|---|---|---|---|---|---|
| 7 | 2026-09-30T13:05:45Z | first commit 705d9f9 | HARNESS / CONFIG / COMPOSITE / DATA | e2e0b18a0115 / 1cef53e19e16 / f9d9d9d95731 / nodata | stamps of the first commit (finding_corrected bootstrap_stamps) |
| 10 | 2026-09-30T16:11:08Z | config_changed | 1cef53e19e16 | 0d88328d5b10 | D11: stage1_standalone.ls_spread_series: raw; schema 5 -> 6; comments; bars and levels unchanged; no run existed [1 clause(s) omitted: refer to another project; events.jsonl line 10] |
| 11 | 2026-09-30T16:11:08Z | harness_changed | e2e0b18a0115 | 73a95d352942 | D11: stage1_checks reads ls_spread_series (default raw) and names the bar row after the series; ls_raw_ann_return_pct required on Stage 1 blocks; records.py ind … |
| 13 | 2026-09-30T16:41:44Z | snapshot_recorded | nodata | 198b281de1a0 | first pull, full history, 13 tables; verify OK (vocabularies match config: exchanges, categories, 10 delisting actions, ART; marketcap median 712m); live OK col … |
| 27 | 2026-09-30T16:53:36Z | composite_updated v0 |  | f9d9d9d95731 | runs 001,002 |
| 899 | 2026-10-01T06:13:22Z | composite_updated v1 |  | cbeb16455bf4 | runs 012,013,014 |
| 908 | 2026-10-01T06:25:38Z | composite_updated v2 |  | 8b444636f0a1 | runs 012,015,016 |
| 916 | 2026-10-01T06:36:15Z | composite_updated v3 |  | 73ee92fe0723 | runs 012,017,018 |
| 924 | 2026-10-01T06:47:03Z | composite_updated v4 |  | 3329679c69fb | runs 012,019,020 |
| 932 | 2026-10-01T06:58:27Z | composite_updated v5 |  | d27916e567f2 | runs 012,021,022 |
| 953 | 2026-10-01T07:32:25Z | composite_updated v6 |  | 21a6688ae5d1 | runs 023,024,025 |
| 961 | 2026-10-01T07:51:16Z | composite_updated v7 |  | 43c92213ae73 | runs 023,026,027 |
| 969 | 2026-10-01T08:10:20Z | composite_updated v8 |  | a12e87c5fb36 | runs 023,028,029 |
| 977 | 2026-10-01T08:29:53Z | composite_updated v9 |  | c961f5791816 | runs 023,030,031 |
| 999 | 2026-10-01T09:25:17Z | composite_updated v10 |  | 1b4195ff18b4 | runs 032,033,034 |
| 1007 | 2026-10-01T09:58:12Z | composite_updated v11 |  | 335b06e3d608 | runs 032,035,036 |
| 1028 | 2026-10-01T12:02:46Z | composite_updated v12 |  | 612e59349f40 | runs 037,038,039 |
| 1036 | 2026-10-01T13:11:19Z | composite_updated v13 |  | fa17bd1cd37e | runs 037,040,041 |
| 1044 | 2026-10-01T14:38:34Z | composite_updated v14 |  | 7fe6f001e708 | runs 037,042,043 |
| 1060 | 2026-10-01T17:04:10Z | harness_changed | 73a95d352942 | 471f70782486 | D7 construction layer: (1) sector+market-beta neutrality via a constraint matrix [sector dummies \| beta_i], beta_i trailing 36m on D4's M (min 12, sector-month … |
| 1071 | 2026-10-01T18:44:13Z | harness_changed | 471f70782486 | 3561590b660a | alpha_review fixes to the D7 layer (layer path only): declared vs effective ex-years fields (2000 precedes book_start; effective 2001,2021); name_cap_excess car … |
| 1089 | 2026-10-01T21:21:35Z | harness_changed | 3561590b660a | aef490297071 | diagnostic --return-start skip1 (alpha_review major 1): forward return of t+1 based at the first SEP trade of t+1 (within 7 days of the market's first trading d … |
| 1098 | 2026-10-01T23:07:10Z | harness_changed | aef490297071 | 1271266472a9 | rf diagnostic (owner_stop_and_ask_3_approved): external-table kind in snapshot.py (TB3MS from FRED fredgraph.csv, keyless, frozen in data/sharadar/TB3MS.parquet … |
| 1104 | 2026-10-01T23:27:07Z | snapshot_recorded | 198b281de1a0 | 42587e08609a | D8 step 1 refresh (owner-approved stop-and-ask 3): 13 Sharadar tables re-pulled full history (SEP 45,393,854 rows to 2026-10-01; 2026-09-30 present with 6,262 n … |

### B8. Event counts

*Table 10d_event_counts. research/events.jsonl by event type (1134 rows).*

| event | count |
|---|---|
| spec_written | 207 |
| factor_evaluated | 132 |
| factor_translated | 108 |
| preflight_passed | 105 |
| factor_infeasible | 71 |
| run_started | 57 |
| provenance_verified | 56 |
| run_completed | 56 |
| decision | 51 |
| process_finding | 31 |
| preflight_failed | 29 |
| fields_verified | 27 |
| family_assigned | 24 |
| alpha_review | 23 |
| construction_reported | 18 |
| composite_updated | 15 |
| finding_corrected | 15 |
| registry_rows_written | 15 |
| batch_closed | 14 |
| batch_declared | 14 |
| preflight_remeasured | 14 |
| repository_committed | 10 |
| harness_changed | 6 |
| verification_completed | 6 |
| phase_completed | 5 |
| validation_warning | 5 |
| finding_confirmed | 4 |
| config_changed | 2 |
| flip_hypothesis_qualified | 2 |
| snapshot_recorded | 2 |
| batch_amended | 1 |
| factor_dropped | 1 |
| holdout_spent | 1 |
| inventory_classified | 1 |
| project_initialized | 1 |
| repo_published | 1 |
| repository_initialized | 1 |
| rule_conflict_found | 1 |
| run_aborted | 1 |
| stage2_order_declared | 1 |
