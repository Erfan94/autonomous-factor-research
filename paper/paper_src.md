<!-- SOURCE of paper/paper.md. Do not edit paper.md: run `python3 paper/build_tables.py --check`.
     A double-braced key is a value from paper/tables/00_facts.md (each with its record source);
     a double-braced table:NN_name pastes paper/tables/NN_name.md. No decimal is typed here by hand;
     `--check` lists every remaining typed integer. -->

# A pre-registered factor search on Sharadar with a sector-relative, market-hedged family blend: the full record

Alpha Model Auto Research V4. Every number below is generated from the project's record files by
`paper/build_tables.py`; Appendix A7 (`paper/tables/00_facts.md`) gives the source of each number in the prose.

## Headline

All holdout figures cover {{ho_n}} months, {{oos_start}} to {{oos_end}}; the canonical read is run 054 `cut_holdout_*`.

- **The declared headline fell to about half of its expectation, without significance.** The hedged D10−D1, the
  pre-registered headline, earned {{ho_h_ret}}%/yr at Sharpe {{ho_h_sh}}, NW t {{ho_h_t}} (run 054). The expectation
  written before the spend was {{iw_h_ret}}%/yr, Sharpe {{iw_h_sh}}, NW t {{iw_h_t}} (run 053). Beside it: the raw spread
  earned {{ho_raw_ret}}%/yr, Sharpe {{ho_raw_sh}} (run 054). The hedge's ex-ante β averaged {{ho_beta_exante}} (run 054),
  and the raw spread's realised β was {{ho_beta_real}} (run 055, the holdout-only cross-check).
- **The ranking information persisted at about its late in-window level, also without significance.** The composite's
  mean rank IC was {{ho_ic}}, NW t {{ho_ic_t}} (run 054): one-sided p ≈ {{ho_p1}}, two-sided p ≈ {{ho_p2}}, and below
  the {{bar_s1_t}} bar a single predictor needed at Stage 1. The benchmark written before the spend was the second-half
  in-window IC, {{ho_benchmark_h2}} (run 053). The IC was concentrated in {{ho_top_ic_year}} ({{ho_2022_ic}}; table 08b).
- **Out of sample, most of the hedged return was the hedge term.** The hedge term is hedged − raw = −12·mean(β_t·M_t),
  the long market position the hedge adds to a net-short book. It was {{hedge_term_ho}} of the {{ho_h_ret}} pp/yr out of
  sample (run 054), against {{hedge_term_iw}} of {{iw_h_ret}} pp/yr in-window (run 053). Part of it is mechanical: M is a
  total return, so the hedge credits |β|·rf, which the excess-of-rf diagnostic removes ({{ho_rf_credit}} pp/yr out of
  sample, {{iw_rf_credit}} in-window). The lag ran the other way. The ex-ante β was about {{ho_beta_gap2}} less negative
  than the realised one, so the "hedged" series stayed net short that much market in a mostly rising market
  ({{ho_bull_m}} of {{ho_n}} months had a positive trailing {{mkt_state_lb}}-month market return; manifest, run 054). That residual short
  exposure depressed the hedged return.
- **The corrected readings are small.** The excess-of-rf hedged series earned {{ho_ex_ret}}%/yr, Sharpe {{ho_ex_sh}},
  NW t {{ho_ex_t}} (run 054). The β-neutral investable book (the construction layer at $100M) earned
  {{layer_ho_gross_ret}}%/yr gross, Sharpe {{layer_ho_gross_sh}} (run 057). Its in-window gross Sharpe was
  {{layer_iw057_gross_sh3}} (run 057 `cut_inwindow_*`, equal to run 049's to three places). Net of measured costs the
  declared layer row is negative at every size in both windows; some sensitivity rows are not (Section 7).
- **The contribution is the record, not the model.** It accounts for every one of {{n_osap}} OSAP predictors: screened,
  excluded with a measured reason, or held as a seed leg. It also holds the bars and verdicts of {{n_screened}} screens,
  rejections included, the decision log, and the orchestration that produced them.

**Convention.** Main-text in-window figures use the spend snapshot: run 053, DATA {{data_sha_2}}, the bytes the holdout
was read on. Acceptance-time figures come from runs 001–052 on DATA {{data_sha_1}}, before the snapshot refresh. They
appear in the version history (table 05e), the ratchet tables and the appendices, labelled "acceptance-time, pre-refresh
bytes". All returns are gross unless labelled net. "Hedged" is the declared D4 series, "raw" is the unhedged D10−D1, and
"excess" is the rf-corrected diagnostic (Section 2). There are no charts; every table caption names its run or record
file. Sharpe ratios are printed to three places.

The project was built from a predecessor's skeleton, methodology only (D1).

## 1. Pre-registration

The search ran under one configuration file, `config/test_config.yaml`, at CONFIG_SHA {{config_sha}}. All
{{n_runs_started}} `run_started` events carry this one CONFIG_SHA ({{n_cfg_shas}} distinct value), so the
pre-registration did not move during the search. The decision window is {{eval_start}} to {{eval_end}} ({{iw_n}} months).
The out-of-sample block is {{oos_start}} to {{oos_end}}. Newey-West t-statistics use {{nw_lags}} lags throughout.

The four construction changes were fixed before any candidate was screened:

1. **Within-sector ranks (D3).** Every signal is percentile-ranked within its sector each month. A sector-month with
   fewer than {{min_names_group}} scored names falls back to the cross-section rank. The family blend averages these ranks.
2. **A market hedge by construction (D4).** The headline long-short is D10−D1 minus β_t × M_t. M is the universe's own
   cap-weighted total return. β_t is estimated on months t−{{beta_window}}..t−1 only, and is 0 before {{beta_min}} months
   of history. Under D11 the hedge reaches exactly one bar, the Stage 2 return guard. The Stage 1 spread bar reads the raw
   D10−D1. Both series are annualised as the monthly mean × 12, so hedged − raw = −12·mean(β_t·M_t) exactly (verification
   hedge_gap_check_before_phase_d); this paper calls that difference the hedge term.
3. **β and a date-free ex-regime Sharpe on every block (D5).** These are the Sharpe after removing the {{top_years_k}} best
   calendar years, and a bear/bull split on the sign of the trailing {{mkt_state_lb}}-month market return. They are
   diagnostics, never bars.
4. **Everything else unchanged (D6).** This covers the bars and their levels, the family blend, the broad universe,
   and the Stage 2 order and ladders.

The bars, verbatim:

{{table:01_bars_verbatim}}

The family cap of {{families_max}} is in the configuration (`search.families_max`). The flip rule sits outside it, in
`CLAUDE.md`: a screen in the reversed sign is a second hypothesis and needs an absolute t of at least
{{flip_bar}}. Orientation is OSAP's published sign. The OSAP source is pinned to tag {{osap_tag}}, commit
{{osap_ref}}.

The design decisions:

{{table:01c_decisions}}

The runner had to stop and ask the owner only in these cases:

{{table:01b_stop_and_ask}}

## 2. Data

All data come from direct pulls of the Sharadar API, recorded twice. The first recording (DATA {{data_sha_1}}) held
{{n_sharadar_tables}} Sharadar tables with full history; FUNDS is mapped in the field map but not held. Every run up to
052, and so every decision of the search, used these bytes.

**The first snapshot already held the holdout months.** It was a full-history pull, recorded {{snap1_recorded}}, and its
SEP table runs to {{snap1_sep_max}} (the frozen manifest before the refresh). The holdout was isolated by rule, not by
absent bytes. Every result block of runs 001–053 ({{eval_end_runs}} runs with blocks) has eval_end {{eval_end_set}}, and
`CLAUDE.md` makes a block whose eval_end reaches 2022 a hard stop, which the harness's validation flags as an
out-of-sample breach. The refresh was needed because the block ends on {{oos_end}}, after that pull.

D8 required that refresh (stop-and-ask 3). The second recording (DATA {{data_sha_2}}) re-pulled the same
{{n_sharadar_tables}} tables, and added one external table, the three-month Treasury bill rate TB3MS from FRED. The
owner approved both in one message: "{{owner_sa3}}".

{{table:02_snapshots}}

{{table:02b_tables}}

**The rf correction is a diagnostic, not a replacement.** The declared hedge (D4) subtracts β_t times the universe's
*total* return, so a negative-β book is credited |β_t| × rf_t as if it were return (decision
hedge_guard_negative_beta_property, logged during Phase D). Replacing the hedge proxy would move CONFIG_SHA, which is
stop-and-ask 2, and that was not asked. So the correction is reported beside the declared hedge:
excess_t = hedged_t + β_t × rf_t, with rf = TB3MS/1200 paired with the holding month. The bars are unchanged. In-window
on the spend snapshot the rf credit (`ls_rf_credit_pp`, excess minus hedged) is {{iw_rf_credit}} pp/yr. The excess-of-rf
Sharpe is {{iw_ex_sh}} against the hedged {{iw_h_sh}} (run 053).

**The refresh restated the in-window block.** Run 052 used the frozen bytes and run 053 the refreshed bytes, with the
same harness, config and composite. Of their shared result-block fields, {{restate_same}} are identical and
{{restate_moved}} differ (including data_sha). Run 053 adds {{restate_new}} excess-of-rf fields. The mean IC moved by
{{restate_dic}}, and the hedged Sharpe from {{sh052}} to {{iw_h_sh}}. No Stage 2 verdict is expected to move (decision
d8_step2_restatement_within_margin). That expectation is inferred from the composite-IC deltas against the thinnest
residual-t margins; the rungs were not re-run on the new bytes. No rejection rested on the guard. The monthly series is
not stored, so the restated months are not itemised.

{{table:02c_restatement}}

## 3. Inventory and the Stage 1 screen

Every OSAP predictor at the pinned commit was inventoried: {{n_osap}} in all. {{n_seed}} are the v0 seed legs. Of the
rest, {{n_feasible}} were constructible from Sharadar and {{n_infeasible}} were not. Of the constructible ones,
{{n_translated}} were translated and passed preflight, and {{n_pf_failed}} failed preflight. Every excluded predictor has
a frontier row with its measured reason (Appendix A2): {{n_fr_data_unavailable}} need data Sharadar does not publish
(analyst forecasts, options, short interest, some Compustat items), {{n_fr_preflight_failed}} failed preflight (mass
points, discrete flags, coverage), and {{n_fr_data_start}} start too late for the {{min_months}}-month minimum.

{{table:03_inventory}}

The Stage 1 screen ran in batches of {{s1_batch}} in alphabetical order. It covered {{n_screened}} signals: the
{{n_translated}} candidates and one declared flip. {{n_s1_pass}} passed, {{n_s1_fail}} were rejected and {{n_s1_incon}}
were inconclusive. Most rejections fell on the t bar ({{n_fail_by_t}} decided by `ic_tstat_nw`).
{{n_t_pass_other_fail}} signals cleared the t bar but had a mean IC below {{bar_s1_ic}}.

{{table:03b_stage1_fail_bars}}

{{table:03c_t_pass_other_fail}}

**How many passes would chance alone produce?** The Stage 1 t bar is one-sided: t ≥ {{bar_s1_t}} in the published sign.
Under a global null where no predictor carries information, each of the {{null_n}} screens in the published sign passes
the t bar with probability P(Z ≥ {{bar_s1_t}}) = {{null_p25}}. The expected number of false passes is {{null_n}} ×
{{null_p25}} = {{null_e1}}.

The flip rule adds a second path. A predictor qualifies for a reversed-sign screen when t ≤ −{{flip_bar}}, with
probability P(Z ≥ {{flip_bar}}) = {{null_p274}} per predictor, or {{null_e2}} expected. Both paths together give
{{null_etot}} expected false passes, against {{n_s1_pass}} observed. A screen must pass every bar, not only the t bar, so
these t-bar counts are upper bounds on the null passes of all bars.

Stage 2 is one-sided too (t > {{bar_s2_t}}). Over {{n_s2}} rungs the null expectation is {{n_s2}} × {{null_p20}} =
{{null_e3}}, against {{n_s2_acc}} acceptances. These expectations hold whatever the dependence between tests; correlated
signals widen the spread around them, not their mean. The normal tail approximates the Newey-West t, which is computed on
a few hundred monthly observations.

{{table:03d_null_fp}}

**Flip hypotheses.** Two predictors qualified for a flip, both at an absolute t of at least {{flip_bar}} in the OSAP sign.
BidAskSpread (absolute t {{bas_parent_t}}) was declared as BidAskSpreadFlip and screened in the last batch. It passed at
t {{bas_flip_t}}, clearing the {{flip_bar}} bar, and was later rejected at Stage 2. GrLTNOA (absolute t {{grl_parent_t}})
qualified but was not screened. Its reversed mean IC, {{grl_rev_ic}}, fails the {{bar_s1_ic}} IC bar by a margin the
rank-reversal offset cannot close (decision flip_not_screened_when_deterministic_fail).

{{table:03e_flips}}

## 4. Families and the Stage 2 order

The {{n_s1_pass}} passers and the five seeds carry {{n_labels}} distinct SignalDoc `Cat.Economic` labels. The cap is
{{families_max}} families. A single decision (phase_c_family_partition) fixed the label-to-family map before any
assignment. Two labels were absorbed where an existing definition covers the construction: volume into liquidity, and
accruals into investment. Four new families were opened. The decision names the rejected alternatives. It also records
that every Stage 1 number was visible when the partition was chosen.

{{table:04_label_map}}

{{table:04b_families}}

Phase C closed before any Stage 2 number existed. The {{n_family_assigned}} assignments, the declared order and the
phase close all precede the first Stage 2 run.

{{table:04c_phase_c_timeline}}

The ninth family was opened in Phase C, by {{fmax_opened_by}}'s assignment ({{fmax_opened_ts}}), which reached
`families_max`. The composite first held nine families at {{fmax_held}}. The remaining passers fell into existing
families. The order (Appendix A4) sorts all {{n_s2}} passers by full-precision Stage 1 NW t and was never re-sorted.

## 5. The ratchet

{{n_ladders}} ladders (runs {{ladder_runs}}) were cut from the declared order, five rungs at a time; the last had four.
Rung i faced the base plus every earlier passing rung. Of {{n_s2}} rungs, {{n_s2_acc}} were accepted, {{n_s2_rej}}
rejected and {{n_s2_incon}} inconclusive. Every rejection was decided by `{{s2_rej_bars}}`. None was decided by the guard:
no rung had a guard t below {{bar_s2_guard}} ({{n_guard_fail}} rows). The lowest guard t was {{min_guard_t}}
({{min_guard_f}}, accepted).

{{table:05_rungs}}

{{table:05b_ladders}}

**Margins.** The two thinnest acceptances were {{thin0}} at {{thin0_t}} and {{thin1}} at {{thin1_t}}. For scale, the
snapshot refresh moved the composite IC t by {{restate_dt}} (table 02c). The two nearest misses were {{miss0}} at
{{miss0_t}} and {{miss1}} at {{miss1_t}}. In every case the rule decided; no rung was re-litigated.

{{table:05c_margins}}

**The guard has a disclosed bias toward negative-β legs** (decision hedge_guard_negative_beta_property). A rung that
moves the blend's ex-ante β is credited through the hedge term, whatever its information. MaxRet is the clearest case
(run 023). Its raw spread delta was {{mr_raw_dls}} pp/yr, the hedge part {{mr_hedge_part}} and the hedged delta
{{mr_hedged_dls}}. Its residual IC t of {{mr_resid_t}} carried the acceptance. For a negative-β new family the guard is
close to non-binding, and the residual IC is the operative gate. The split was recorded from ladder 2 on:

{{table:05d_hedge_part}}

**Every acceptance was reproduced.** After each acceptance the evaluator rebuilt the composite and ran
`--baseline --stage 2`. Each baseline reproduced its rung's with-candidate arm on {{repro_fields}} fields to six places
(phase_completed D). Stage 3 then ran per version. One annotated tag per version was created. The v1 tag points at the
wrong commit and was not moved (Section 9).

The version history, acceptance-time, pre-refresh bytes:

{{table:05e_versions}}

At acceptance time, on the pre-refresh bytes, the composite's mean IC rose between v0 and v14 from {{v0_ic}} to
{{v14a_ic}}, and its NW t from {{v0_ic_t}} to {{v14a_ic_t}}. The hedged Sharpe rose from {{v0_sh}} to {{v14a_sh}}. The
full-window β of the raw spread went from {{v0_beta}} to {{v14a_beta}}, and D10 turnover from {{v0_to}}% to {{v14a_to}}%
a month (runs 001 and 042). The guard's hedge part was largest for three accepted legs: MaxRet ({{mr_hedge_part}} pp/yr),
zerotrade6M ({{zt6_hedge_part}}) and roaq ({{roaq_hedge_part}}) (table 05d). IdioVol3F's was {{ivol_hedge_part}}, and the
hedged Sharpe fell when it joined ({{v9_sh}} at v9, {{v10_sh}} at v10). The acceptance-time hedged Sharpe peaked at
{{best_sh_ver}} ({{best_sh}}); later acceptances raised the IC and its t, not the hedged Sharpe.

## 6. The in-window composite (v14, run 053)

v14 has {{v14_legs}} legs in {{v14_fams}} families (COMPOSITE {{v14_sha}}). On the spend snapshot, {{eval_start}} to
{{eval_end}} (run 053), its mean IC is {{iw_ic}}, NW t {{iw_ic_t}} (plain t {{iw_ic_plain_t}}). The hedged long-short
earns {{iw_h_ret}}%/yr at Sharpe {{iw_h_sh}}, and the raw spread {{iw_raw_ret}}%/yr at Sharpe {{iw_raw_sh}}. The hedge
term is {{hedge_term_iw}} pp/yr at a full-window β of {{iw_beta_fw}}.

{{table:06_v14_inwindow}}

**The information is front-loaded.** The IC halves are {{iw_ic_h1}} and {{iw_ic_h2}}. The years {{iw_top_years}} carry
{{iw_top_share}}% of the summed long-short return. The Sharpe without those years is {{iw_top3}}. Annual IC is negative in
{{n_neg_ic_years}} of {{n_ic_years}} years: {{neg_ic_years}}, as printed in the run 053 summary.

{{table:06d_annual_ic}}

{{table:06b_deciles}}

{{table:06c_tiers}}

**The legs do not all start in 1999.** The early years run on fewer legs. In the first year all nine families are
present, but {{legs_1999}} of the {{v14_legs}} legs score in January. IdioVol3F starts in {{start_IdioVol3F}}: its FF3
factors are built from June 1999 formations, so its first signal is {{sig_IdioVol3F}}. VolumeTrend and TrendFactor start
in {{start_TrendFactor}} (signal month-end {{sig_TrendFactor}}). ShareIss5Y starts in {{start_ShareIss5Y}} (signal
{{sig_ShareIss5Y}}) because of its {{gate_ShareIss5Y}}-month history gate. The family blend renormalises over the legs
present.

{{table:06e_leg_starts}}

{{table:06f_legs_by_year}}

**The rf correction** (run 053) lowers the headline from {{iw_h_sh}} to {{iw_ex_sh}} (Sharpe) and from {{iw_h_ret}} to
{{iw_ex_ret}}%/yr. The rf credit is {{iw_rf_credit}} pp/yr. The Sharpe without the top-3 years is {{iw_ex_top3}} on the
excess series.

**Return-start sensitivity** (runs 050 and 051, pre-refresh bytes; figures from the run 051 block; finding_confirmed
skip1_return_start_sensitivity). The whole-model alpha review flagged one risk: several legs end on the same close that
starts the forward return. That could carry untradeable bid-ask bounce into the IC. A diagnostic run started the forward
return at the first trade of month t+1 instead. The composite IC fell from {{skip1_close_ic}} to {{skip1_ic}} (paired
ΔIC {{skip1_dic}}, NW t {{skip1_dic_t}}), about {{skip1_share}}% of the IC. The hedged Sharpe fell from {{close_sh}} to
{{skip1_sh}}. The second-half IC barely moved ({{close_h2}} to {{skip1_h2}}). The loss sits in the value, investment and
financing legs, not in the short-horizon legs the bounce hypothesis named (table 06h). The signal-close convention was
declared in advance; no verdict is affected.

{{table:06g_skip1}}

{{table:06h_skip1_legs}}

**Stage 3** (run 043; run 048 reproduced it under the layer harness). Stage 3 is acceptance-time, pre-refresh bytes. No
in-window Stage 3 was run on the spend snapshot.

{{table:06i_stage3}}

## 7. The construction layer

D7 required three changes before the layer's first number. The book must be neutral to market β as well as sector
(implemented as a hard constraint). The half-spread must come from a harness-built Corwin-Schultz series rather than a
composite leg. The regime cuts must follow the D5 rule. The alpha review of that change asked for fixes first: one major
(a passage in the design notes cited another project's outcome; removed), one medium (the ex-years cut) and several
lows. They landed in a second harness move. Runs 045, 047 and 048 reproduced the measuring path (docs/JOURNAL.md).

{{table:07d_d7_changes}}

**In-window result** (run 049, book {{l49_book}} to {{l49_book_end}}, pre-refresh bytes). At $100M the layer earns
{{l49_gross}}%/yr gross, Sharpe {{layer_iw_gross_sh3}}, NW t {{l49_gross_t}}. Measured costs are {{l49_cost}}%/yr:
spread {{l49_spread}}, impact {{l49_impact}}, borrow {{l49_borrow}}. Net, it earns {{l49_net}}%/yr at Sharpe
{{l49_net_sh}}; the net Sharpe is {{l49_net_1b}} at $1B and {{l49_net_5b}} at $5B. One-way turnover is {{l49_to}}% a
month. Ex-post net β on M is {{l49_beta}} against an ex-ante target of zero. Without the β constraint, net β is
{{l49_nbc_beta}} and gross return is {{l49_nbc_gross}}%/yr at Sharpe {{l49_nbc_gross_sh}}. All {{n_layer_rows}} rows are in
Appendix B1.

{{table:07a_layer_summary}}

**The regime cuts (D7 item 3; manifest v14 `construction_layer.cuts`, run 049).** The D5 rule gave the declared ex-years;
the first precedes the book, so the effective cut removes {{cut_ex_eff}}. Without them the layer's net Sharpe is
{{cut_ex_net_sh}} (gross {{cut_ex_gross_sh}}). In 2011–2020 it earned {{cut_1120_gross}}%/yr gross, Sharpe
{{cut_1120_gross_sh}}, and net Sharpe {{cut_1120_net_sh}}. **The gross return also faded after 2002.** It was
{{l49_g2001}}% in 2001 and {{l49_g2002}}% in 2002 (net {{l49_n2001}} and {{l49_n2002}}). Over 2003–2020 it compounds to
{{comp_gross}}% gross, about {{comp_gross_geo}}%/yr geometric ({{comp_gross_arith}}%/yr arithmetic), and {{comp_net}}%
net (run 049 annual returns). The manifest's character line reads: "{{man_comp_text}}".

**Costs exceed the information, and the identity shows by how much.** Net and gross vol are close, so net Sharpe equals
gross Sharpe × (1 − cost/gross) to within {{identity_maxgap}} on every $100M row (table 07b). The layer is negative net
whenever measured costs exceed the gross return. The equal-weight decile book earns more gross return
({{l49_erd_gross}}%/yr, Sharpe {{l49_erd_gross_sh}}) at {{l49_erd_to}}% one-way turnover a month, and loses more net.

{{table:07b_identity}}

**Risk model.** Ex-ante vol averages {{l49_exante_vol}}% a year against {{l49_real_vol}}% realised. The bias statistic is
{{l49_bias}}, inside the band in {{l49_bias_band}}% of windows (run 049). Over run 057's book ({{l57_book}},
{{l57_book_n}} months) it is {{l57_bias_full}}. The risk model underpredicts by more than a factor of two.

**Spread.** The measured Corwin-Schultz half-spread implies {{half_spread_bp}} bp per unit traded. The fixed-tier
alternative implies {{fixed_half_spread_bp}} bp (manifest v14 `construction_layer.trading`), with spread coverage
{{spread_measured}}% (run 049). *Judgment, not measurement:* the daily Corwin-Schultz estimate is floored at zero before
averaging. That biases measured spreads up for liquid names, so the true cost likely lies between the measured and the
fixed-tier rows (manifest v14 `construction_layer.character`). The fixed-tier row is net positive in-window at $100M
(Sharpe {{l49_fts_net_sh}}). No run measures which spread is right.

**"Negative net of measured costs" holds for the declared layer row, not for every row.** The `layer` row is net
negative at $100M, $1B and $5B in run 049 and in both windows of run 057; the build asserts it. {{n_pos_layer_rows}}
other rows are net positive: {{n_pos_fixed}} use the fixed-tier spread, and {{n_pos_measured}} are $100M sensitivity
rows with measured spreads and net Sharpe of at most {{pos_measured_max}}. None is positive out of sample
({{n_pos_layer_rows_ho}} rows).

{{table:07e_layer_positive_net_rows}}

On the spend snapshot the in-window book restates mildly: gross {{l57iw_gross}}%/yr, net Sharpe {{l57iw_net_sh}} at
$100M (run 057 `cut_inwindow_*`).

{{table:07c_layer_restated}}

## 8. Out of sample

The holdout was spent once, on {{spent_on}}, on v14 with DATA {{data_sha_2}} and the frozen layer (runs 054–057). The
owner answered stop-and-ask 5 with "{{owner_sa5}}". The canonical read is run 054 `cut_holdout_*`. In that run the hedge
β is estimated continuously across the 2021-12/2022-01 boundary. Run 055 (`--holdout-only`) is the cross-check. Its
first months run unhedged (β = 0; {{ho055_hedged_m}} hedged months), and it reports the deciles, tiers and ex-top-3
rows that 054's cut does not print. Run 054's in-window cut equals run 053 on {{cont_same}} of {{cont_n}} shared fields.

**The expectations, verbatim** (decision holdout_expectations_v14_spend_snapshot, logged {{hx_ts}}; the first holdout
run started {{ho_first_ts}}):

> {{hx_text}}

{{table:08_vs_expectation}}

**What held.** The mean IC, {{ho_ic}}, is {{ho_ic_share_full}}% of the full in-window mean and above the second-half
benchmark {{ho_benchmark_h2}}. At NW t {{ho_ic_t}} on {{ho_n}} months the one-sided p is about {{ho_p1}}: not significant
two-sided (p ≈ {{ho_p2}}), and below the {{bar_s1_t}} Stage 1 bar.

**What did not.**

- *The declared headline.* The hedged D10−D1 earned {{ho_h_ret}}%/yr, Sharpe {{ho_h_sh}}, NW t {{ho_h_t}} (run 054),
  against an expected {{iw_h_ret}}%/yr, Sharpe {{iw_h_sh}}, NW t {{iw_h_t}} (run 053). Beside it, the raw spread earned
  {{ho_raw_ret}}%/yr (Sharpe {{ho_raw_sh}}) and the excess series {{ho_ex_ret}}%/yr (Sharpe {{ho_ex_sh}}).
- *Concentration.* {{ho_top_ic_year}} alone has IC {{ho_2022_ic}} (run 054) and a hedged return of {{ho_2022_h}}% (run 056
  equal_rank_decile, the same series as run 054's cut). The holdout-only IC halves are {{ho_ic_h1_055}} and
  {{ho_ic_h2_055}} (run 055).
- *Decile shape.* In the holdout D1 earns {{ho_d1}}%/mo, and D2 to D10 sit flat between {{ho_d2_d10_min}} and
  {{ho_d2_d10_max}} (run 055; table 06b). The spread is the short bottom decile only.
- *Drawdown.* The raw maximum drawdown of the whole 1999–2026 record, {{full054_raw_mdd}}% (run 054), falls in the
  holdout.
- *The ex-top-3 diagnostic is mechanical here.* The holdout spans {{n_ho_years}} calendar years. Removing the top
  {{top_years_k}} ({{ho_top_years}}) leaves {{n_ho_years_left}}, both negative. The resulting Sharpes ({{ho_ex3_h}}
  hedged, run 055; {{ho_ex3_x}} excess, run 054) carry no regime information.

{{table:08b_holdout_years}}

{{table:08c_holdout_tiers}}

**The hedge lagged, and the lag cost return.** The ex-ante β averaged {{ho_beta_exante}} over the holdout (run 054). The
raw spread's realised β was {{ho_beta_real}} (run 055), and the last ex-ante estimate was {{ho_beta_last}}. In-window the
two agreed ({{iw_beta_exante}} and {{iw_beta_fw}}, run 053). The trailing {{beta_window}}-month estimate under-hedged by
about {{ho_beta_gap2}} of market, so the hedged series stayed net short in a mostly rising market (bull months
{{ho_bull_m}}, bear months {{ho_bear_m}}; manifest, run 054). That depressed the hedged return; it is neither the raw book
nor a neutral one. What flattered the hedged return mechanically is the rf credit, {{ho_rf_credit}} pp/yr (in-window
{{iw_rf_credit}}). The excess series, which removes it, earned {{ho_ex_ret}}%/yr at Sharpe {{ho_ex_sh}}, NW t
{{ho_ex_t}} (run 054). The cross-check (run 055) left the first year unhedged. It shows a hedged Sharpe of {{ho055_sh}},
with the same IC and raw return.

{{table:08d_beta}}

**The investable book.** At $100M the layer earned {{layer_ho_gross_ret}}%/yr gross, Sharpe {{layer_ho_gross_sh}}. Costs
of {{l57ho_cost}}%/yr left {{layer_ho_net_ret}}%/yr net, Sharpe {{layer_ho_net_sh}} (run 057).

{{table:08e_layer_holdout}}

**Gaps in the spend, disclosed rather than repaired.** D8 step 4 asked for Stage 3 to be read from its holdout cuts.
Run 056's Stage 3 blocks carry none (process_finding stage3_holdout_cuts_absent). The only Stage 3 evidence for the
holdout is therefore the calendar-year returns below and the 1999–2026 full-window statistics. Run 055 is flagged by the
harness's own minimum-sample rule: "{{floor_warn}}" Its decile-collapse warning is the same floor applied to a
{{ho_n}}-month window, with the long-short present in every month.

{{table:08f_stage3_holdout}}

**What the holdout can and cannot test (D2).** The block is a clean test of factor selection. Every candidate was
screened fresh on this snapshot, and no month after {{eval_end}} entered any decision. It is not an unbiased test of the
construction changes (within-sector ranks, the hedge, the diagnostics). Those were motivated by a study, made before this
project, that read 2023–2026 data. The owner chose this overlap knowingly. The holdout can confirm or refute the
selected composite. It cannot say whether the hedge and the sector ranking would have been chosen without seeing those
years.

## 9. Integrity

**Alpha reviews.** There were {{n_alpha_reviews}} adversarial audits: {{n_alpha_phaseA}} on translated batches in
Phase A, then the STreversal residual-share trigger, the D7 layer and the whole model before the holdout. They found
{{n_alpha_critical}} critical issue, a missing history gate on PriceDelayRsq, fixed before any screen. The Phase A
majors were fixed before any screen, and the D7 review's major before the first layer number. The whole-model review's
two majors were answered by a diagnostic (the skip1 run 051) and by the choice of the holdout IC benchmark (the second
half).

{{table:09_alpha_reviews}}

**Process findings.** There are {{n_process_findings}} process findings (Appendix B2). {{n_leak_findings}} of them
concern text that refers to another project: {{leak_ids}}. Their record text is not reproduced; the clauses that name
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
- The session permission classifier refused one subagent action, the v12 apply. The record reads: "{{deny_text}}".
  The coordinator did not route around the refusal and waited for the owner, who then authorised the coordinator to
  make the moves and composite edits (docs/JOURNAL.md, research/CHANGELOG.md; table 10f).

**Corrections.** {{n_finding_corrected}} findings were corrected append-only (Appendix B3). Among them, the timestamps of
events rows {{ts_est_rows}} were estimates rather than clock readings; their true bound is the commit that carries them.
Verifications and confirmed findings are in Appendices B4 and B5.

## 10. Orchestration

**Who did what.** The runner was the session model: {{model_bootstrap}} at bootstrap, {{model_runner}} from the snapshot
recording on, with {{model_advisor}} as the advisor (docs/JOURNAL.md). Five subagents did the repeated work. In event
counts:

- osap-fetcher wrote the predictor specs ({{cnt_spec_written}} `spec_written`, one per non-seed predictor);
- sharadar-field-checker verified fields on this snapshot ({{cnt_fields_verified}} `fields_verified`);
- sharadar-translator wrote the factor files ({{cnt_factor_translated}} `factor_translated`: the {{n_translated}}
  candidates plus {{translated_unscreened}}, translated and then failed preflight);
- alpha-reviewer audited code ({{cnt_alpha_review}});
- factor-evaluator checked provenance and wrote every record ({{cnt_factor_evaluated}} `factor_evaluated`).

Preflight passes reconcile as follows. There are {{pp_events}} `preflight_passed` events: {{pp_single}} single-factor
events and one for {{pp_multi}}. The preflights of {{pp_implied}} are recorded inside their `factor_translated` events,
which RECORDS.md treats as an implied pass. The runner logged {{cnt_decision}} judgment calls as `decision` events. The
event log has {{n_events}} rows (Appendix B8).

**Runs.** {{n_runs_started}} runs were started and {{n_runs_completed}} completed (Appendix B6). Run {{aborted_seq}} was
aborted as superseded, with no result. The completed runs total {{wall_hours}} hours of wall time (`runtime_seconds`).
The runtimes of runs 003–011 sum to {{phaseB_h}} h, while docs/JOURNAL.md states {{journal_phaseB_h}} h for Phase B; the
paper uses the event field.

{{table:10b_runtime_by_phase}}

**Stamp moves** (Appendix B7). CONFIG moved once, before any run ({{n_config_moves}} `config_changed` with a SHA).
HARNESS moved {{n_harness_moves}} times: once for D11 before any run, twice for D7 and its fixes, once for the skip1
diagnostic and once for the rf diagnostic. None of these moves fell inside a declared ladder. DATA was recorded twice,
{{n_snapshot_moves}} `snapshot_recorded` events: the first pull and the D8 refresh. COMPOSITE took
{{n_composite_versions}} values (v0–v14), so it moved {{n_composite_moves}} times.

**Advisor and owner.** The event log records {{n_advisor}} advisor consultations: four ladder acceptances, the Phase D
to E boundary, and the D8 step-2 verdict. `docs/ORCHESTRATION.md` asks for more (every phase boundary); consultations not
logged cannot be verified from the record. The owner's inputs on record are:

- two verbatim answers to stop-and-ask questions, in events;
- one paraphrased resolution of a rule conflict (D11), in events;
- the v12 authorisation, recorded only as a paraphrase in docs/JOURNAL.md and research/CHANGELOG.md. The chat message
  itself is in no record file, so it is not quoted.

{{table:10e_advisor}}

{{table:10f_owner}}

## 11. Limitations, and what a next pre-registration would change

These limitations follow from the record. The proposals describe what would be declared differently; none was run.

**Limitations.**

- *The hedged headline is not a market-neutral return.* Its hedge term includes the rf credit, which flatters it
  ({{ho_rf_credit}} pp/yr out of sample). Its trailing β lagged the holdout's realised β by about {{ho_beta_gap2}}, which
  left residual short exposure in a rising market. The raw spread is not neutral either: its realised holdout β is
  {{ho_beta_real}} (run 055). The corrected readings are the excess-of-rf series ({{ho_ex_ret}}%/yr, Sharpe
  {{ho_ex_sh}}, NW t {{ho_ex_t}}; run 054) and the β-neutral layer ({{layer_ho_gross_ret}}%/yr gross; run 057).
- *The holdout is short and concentrated.* At {{ho_n}} months it is below the harness's own {{min_months}}-month floor.
  One year carries the IC, and the ex-top-3 diagnostic is mechanical on {{n_ho_years}} calendar years.
- *The holdout does not test the construction changes* (D2, Section 8).
- *The holdout was isolated by rule, not by data* (Section 2). The first snapshot held those months.
- *Sector labels are current, not point in time* (D3). This touches every leg's rank, and the industry-built predictors
  through current SIC (decision current_sic_signal_values).
- *The seed legs were never screened.* Their in-window standalone ICs (run 051, signal-close base, pre-refresh bytes) are:
  Size {{seed_ic_Size}} (t {{seed_t_Size}}), Value {{seed_ic_Value}} (t {{seed_t_Value}}), Investment
  {{seed_ic_Investment}} (t {{seed_t_Investment}}) and Momentum {{seed_ic_Momentum}} (t {{seed_t_Momentum}}). Only
  Profitability ({{seed_ic_Profitability}}, t {{seed_t_Profitability}}) would clear the Stage 1 t bar. By
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
- *About {{skip1_share}}% of the in-window IC arrives on the first trading day* of the holding month (run 051,
  pre-refresh bytes).
- *Record defects, disclosed:*
  - estimated event timestamps on rows {{ts_est_rows}};
  - the mis-pointed v1 tag;
  - the missing Stage 3 holdout cuts;
  - the missing tiers and deciles in run 054's holdout cut;
  - the Phase B runtime, stated differently in the journal and the events;
  - the skip1 finding text's rounding (Appendix B5).

**Not tested.**

- The {{n_frontier}} frontier predictors (Appendix A2).
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

{{table:A1_registry}}

## Appendix A2. The frontier

{{table:A2_frontier}}

## Appendix A3. Families

{{table:A3_families_yaml}}

## Appendix A4. The Stage 2 order

{{table:A4_stage2_order}}

## Appendix A5. Manifest headlines v0–v14 (acceptance-time), with v14 on the spend snapshot and in the holdout

{{table:A5_manifest_headlines}}

## Appendix A6. Tags and commits

{{table:A6_tags}}

## Appendix A7. The source of every number in the prose

{{table:00_facts}}

## Appendix B. Record dumps

### B1. The construction layer, all rows (run 049)

{{table:07_layer049}}

### B2. Process findings

{{table:09b_process_findings}}

### B3. Findings corrected

{{table:09c_findings_corrected}}

### B4. Verifications

{{table:09d_verifications}}

### B5. Findings confirmed

{{table:09e_findings_confirmed}}

### B6. Every run

{{table:10_runs}}

### B7. Every stamp move

{{table:10c_stamp_moves}}

### B8. Event counts

{{table:10d_event_counts}}
