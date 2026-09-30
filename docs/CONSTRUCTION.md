# Phase E — the institutional construction layer (carried design; re-declared at Phase E)

Status: TEMPLATE, carried from the predecessor's final design (its r2), with
its parameters in `config/construction_layer.yaml`. It is re-frozen at
Phase E, before the first layer number, with the three changes
`docs/DECISIONS.md` D7 owes it:

1. **A market-beta constraint.** The predecessor's book was sector- and
   dollar-neutral but not beta-neutral; its holdout loss sat in the beta the
   optimiser never saw. Phase E adds a market factor (the universe's
   cap-weighted return, `analytics.universe_market_return`) to the risk
   model and a zero-beta constraint to the projection (§5), or an
   equivalent ex-ante hedge of the book.
2. **A spread source that is not a composite leg.** §6 reads the measured
   half-spread from a column a composite leg happens to carry; the layer
   refuses to run without that leg. Phase E builds the spread series in the
   harness (`data_layer`, cached like the market series) so the cost model
   does not depend on which factors were accepted.
3. **Regime cuts from the D5 rule.** `report.regime_cuts.ex_years` is empty
   until Phase E sets it to the finished composite's top-3 long-short
   calendar years in the decision window (config `diagnostics`), never to a
   year learned on another window.

Every dated declaration below is the predecessor's; the dates say when its
design was fixed, not when this project's is. §9's resolutions carry over
where the code is unchanged.

## 1. What this phase is, and what it is not

- It takes the FINISHED composite (pinned in `config/construction_layer.yaml`
  at Phase E). It describes how an institutional desk would trade it: a risk
  model, a cost model, an optimiser and buffered trading, gross and net, by
  liquidity tier and across AUM levels.
- It judges nothing. No leg is added, dropped or reweighted by a Phase E
  number. The composite score that enters is exactly the Stage 2 family
  blend (`blend_family_ranks`). D8 set this scope.
- **Selection bias.** The composite is chosen on the same 1999–2021 window the layer
  runs on. So in-window layer figures describe the composite's
  *tradability*, not its expected return. Only the holdout figure (final
  validation, stop-and-ask 5, with the composite and the layer both frozen)
  is an estimate.
- Its parameters live in `config/construction_layer.yaml`, NOT in
  `config/test_config.yaml`. CONFIG_SHA pre-registers how a factor is judged,
  and Phase E judges nothing. Every layer block records the file's hash as
  LAYER_SHA beside the four stamps. LAYER_SHA is informational, not a fifth
  gate stamp.
- The code lives in a new harness module, `harness/construction_layer.py`,
  added to `provenance.HARNESS_FILES` (its reverse-coverage test requires
  it), with tests. HARNESS_SHA moves once, outside any ladder. The finished
  composite's Stage 2 and Stage 3 numbers must then reproduce under the new
  HARNESS_SHA (a cascade proof).
- There are no new data or new tables (DATA_SHA unmoved) and no new Python
  dependencies. It uses numpy, pandas and scipy only.

## 2. Inputs (all already in the audit frame, point-in-time)

Per (ID, month t):
- COMPOSITE_SCORE
- monthly_ret, the forward return realised AFTER signal t
- RET_END and SIGNAL_ASOF
- liq_tier, sector, industry_group
- mkt_cap_usd and adv_usd, as of the signal date
- `f_bidaskspreadflip`: the raw Corwin-Schultz spread, the signal-month mean,
  with ≥ 12 valid days

Point-in-time rule: every estimate used at month t is built from months s
whose RET_END(s) ≤ SIGNAL_ASOF(t), in practice s ≤ t−1. The spread is as of
the signal date. A test asserts this on a synthetic panel whose future
returns are poisoned.

## 3. Alpha and book size

The alpha is the Grinold forecast α_i,t = z_i,t × σ_i,t, where:
- **z_i,t** is the cross-sectional normal score of COMPOSITE_SCORE.
- **σ_i,t** is the name's predicted total monthly volatility (§4).

There is no IC multiplier inside α: under a fixed gross it would cancel
exactly, which was the r1 defect.

**The gross budget.** Confidence sizes the book; this is the institutional
reading.
- The book's gross is G_t = 2.0 × clip(IC_t / IC_ref, 0, 1), with
  IC_ref = 0.02 declared: 100% long and 100% short at full confidence, less
  when the trailing IC is weaker.
- IC_t is the trailing 36-month mean of the composite's realised monthly rank
  IC over months s ≤ t−1, needing at least 12 months.
- Ex-ante volatility is REPORTED, not targeted.
- In months where IC_t ≤ 0, the book is flat. Those months are counted and
  reported, not skipped.
- IC_ref and the gross of 2.0 are declared, not fitted. The in-sample IC
  (0.047) is never used.

*Amendment, 2026-09-27, before any real number.* r2 targeted an ex-ante
volatility of 10% × clip(IC_t/IC_ref, 0, 1), with the gross capped at 2.0.
- On the synthetic 2000-name panel (σ ≈ 9%/month), a sector-neutral MV book
  needs a gross of about 10× (median 10.1) to reach 10%.
- So the cap bound in 100% of months and the confidence scaling never acted:
  the r1 "dead parameter" defect in a new form.
- A cap of about 10× is not an institutional book, so confidence now scales
  the gross directly.
- This was calibrated on synthetic data only; no real return was seen.

## 4. Risk model (monthly fundamental factor model)

- **Factors:**
  - one dummy per Sharadar `sector`, plus an explicit 12th group
    `Unclassified` for names with no sector. The sector dummies span the
    market, so there is no separate intercept, which avoids the r1
    collinearity.
  - size: the normal score of log mkt_cap_usd;
  - trailing volatility: the normal score of the 12-month std of monthly_ret,
    over s ≤ t−1, needing at least 6 obs, otherwise the sector median.

  The alpha families are deliberately NOT risk factors: that would neutralise
  the alpha the model holds. Size and volatility overlap the Size leg and the
  low-vol tilt, and the optimiser prices that overlap rather than forbidding
  it.
- **Factor returns:** a cross-sectional WLS of monthly_ret(s) on the
  exposures at s, with weights √mkt_cap.
- **Factor covariance** at t: an EWMA over s ≤ t−1, with a half-life of 24
  months, a 60-month window, and at least 24 months.
- **Specific variance:** an EWMA of squared residuals (half-life 24), shrunk
  50% toward the sector median. Fewer than 12 residuals means the sector
  median is used.
- **The book starts at 2001-01**, once the 24 months of factor returns
  (1999-01..2000-12) exist. Every reference row is re-reported over
  2001-01..2021-12.
- **Reported:** the bias statistic (realised / predicted book volatility,
  12-month rolling) and ex-ante against realised tracking.

## 5. Optimiser (closed form, then constraints by projection; no QP solver)

**Target:** w* = argmax α'w − (λ/2) w'Σw s.t. S'w = 0, where S holds the 12
sector-group columns.
- Every name belongs to exactly one group, so S'w = 0 implies 1'w = 0
  (dollar neutrality). There is no separate dollar row, which keeps the KKT
  system non-singular (the r1 defect).
- Σ = XFX' + D, inverted by Woodbury.
- w* is then scaled to the month's gross budget G_t (§3), so λ drops out.

**Pipeline, in this order, every month:**
1. **Target** w* (above).
2. **Name cap:** |w_i| ≤ max(1%, 5/N_side). Clip, re-project onto S'w = 0,
   iterate to 1e-10 (at most 50 iterations).
3. **Buffer (no-trade region)** against the HELD book w_held. For
   |w*_i − w_held,i| ≤ 0.25·|w*_i| + 2 bp, keep w_held,i. Otherwise move a
   fraction κ = 0.5 toward w*_i.
4. **Participation cap:** |Δw_i| × AUM ≤ 5% × adv_usd_i × 21. A trade above
   the cap is cut to it.
5. **Final re-projection** onto S'w = 0 and the gross budget G_t. This step changes
   other names' trades. Those trades are counted and charged like any other,
   and the block reports the share of turnover the re-projection causes.

**Execution (declared 2026-09-27, before any real number).** Trades execute
at the signal-date close, the same convention as Stages 1–3, so the whole
final book earns monthly_ret(t). This is optimistic for a book whose
participation cap assumes about 21 days of trading, so a sensitivity row
(`layer_exec_half_month`, §6) lets the traded Δw earn only half of the month.

**The gross budget is a hard bound (declared 2026-09-27).** After step 5's last
re-projection, a uniform scale brings the gross to at most G_t. A uniform
scale keeps every group sum at zero. The block reports
`gross_budget_max_excess` and `months_gross_exceeds_budget`, and both must
be 0.

**w_held is the drifted book:** last month's final dollar positions grown by
each name's realised return, divided by the book's capital. Names that
leave the universe are sold at the signal date (charged). Delisted names
close at the Shumway return with no trading cost.

**Tests:**
- the KKT solution against a dense solve on n = 50;
- sector and dollar neutrality hold to 1e-10;
- the caps hold;
- drift accounting on a hand-built three-month example.

## 6. Cost model (charged ex post on the realised trades)

One-way cost of trading $Q in name i is c_i(Q) = hs_i + η σ_d,i √(Q / ADV_i).

- **hs_i:** HALF the measured Corwin-Schultz spread, `f_bidaskspreadflip`/2,
  floored at 1 bp.
  - A name without a valid spread (fewer than 12 valid days) takes that
    month's median hs of its liquidity tier.
  - This is measured per name and per month, so it carries the 1999–2002
    pre-decimalisation spreads. A fixed schedule would understate costs in
    exactly the years where the composite earns (the r1 defect).
  - Using a leg's input as an ex-post cost selects nothing.
  - **Sensitivity row:** a fixed tier schedule (MEGA 2, MID 5, SMALL 12 bp),
    labelled as understating 1999–2007.
- **η = 0.5.** A square-root impact coefficient in the range the literature
  reports for US equities; declared, not fitted. Sensitivity rows use η = 0.25
  and η = 1.0.
- **σ_d,i** is §4's monthly σ divided by √21. **ADV_i** is adv_usd.
- **Short borrow:** 25 bp/yr on the short book, flat (Sharadar has no borrow
  data).
- **σ_d where the risk model has none** (declared 2026-09-27): the month's
  tier median, then the month's median. In a month with no risk model, the
  trailing 12-month realised std is used the same way. It is never 0.
- **Sensitivity rows added 2026-09-27, before any real number** (alpha-review
  of bd5c486; parameters in `costs.sensitivity`):
  - `layer_exec_half_month`: traded Δw earns `trade_return_fraction` = 0.5
    of monthly_ret(t). The realised book return is Σ (h + 0.5·Δw)·r, where h
    is the drifted held weight and Δw = w_final − h. Each name ends the month
    at w + (h + 0.5·Δw)·r. Costs are unchanged.
  - `layer_tiered_borrow`: borrow by liq_tier (`borrow_bp_per_year_by_tier`):
    MEGA 25, MID 75, SMALL 200 bp/yr, any other tier at the largest. The flat
    25 bp is general-collateral borrow, which understates small-cap shorts.

## 7. What is reported (one block per AUM level, overall and by tier)

- **AUM levels:** $100M, $1B, $5B of capital (the gross is up to 2×).
- **Metrics:**
  - gross and net annual return, vol, Sharpe and NW t;
  - MaxDD, naming the episode;
  - worst 12 months;
  - one-way turnover per month, with its re-projection share;
  - cost drag split into spread, impact and borrow;
  - the share of trades hitting the participation cap;
  - the mean gross budget, how many months confidence scaled the book below
    2.0, and how many months are flat (IC_t ≤ 0, or no history);
  - the average number of names long and short;
  - realised exposures to size, volatility and each family;
  - the risk-model bias statistic.
- **Reference rows over 2001-01..2021-12:**
  - the Stage 3 equal_rank_decile and buffered variants, gross and with the
    same cost model applied to their trades;
  - the layer book with the buffer off;
  - the layer book with sector neutrality off (dollar-neutral only), so the
    paper can show what the constraint costs;
  - the sensitivity rows in §6 (η, fixed tier spread, execution fraction,
    tiered borrow), at every AUM.
- **Diagnostics added 2026-09-27, before any real number** (config
  `report.diagnostics`; reported, never a gate):
  - `new_positions_delisting_n` and `new_positions_delisting_pnl_pct`: names
    opened or increased (|w_final| > |h|) in a month whose ret_kind is
    partial_delisted_*, and their summed contribution to the annualised gross
    return. This is reported per row and AUM.
  - the sector leak: the Unclassified share of universe name-months (overall,
    and its min and max by year), and the partial_delisted share of
    name-months inside against outside Unclassified. This is reported in
    every block.
  - `gross_budget_max_excess` and `months_gross_exceeds_budget` (§5).
- **The regime cut on every row:** ex the D5 top-3 LS years and 2011–2020. The finished composite's
  decile LS is negative there, and that is the paper's headline caveat.

## 8. Order of work (one logical change per commit)

1. Run 044 (the HD-PRINT-BARS reproduction) is evaluated against 041 on every
   field and committed. If it differs: `git revert 209ad84`.
2. This draft is final, then D15, then `config/construction_layer.yaml`
   frozen.
3. `harness/construction_layer.py` + tests + HARNESS_FILES, then pytest,
   then alpha-reviewer (point-in-time audit of §2–§6). Then the finished composite's Stage 2
   and Stage 3 reproduction under the new HARNESS_SHA.
4. One run: `run_test.py --baseline --construction-layer`, a new flag with
   its own run label `LAYER` (records.py and parse_result_blocks are checked
   to accept it). It composes with `--include-holdout`. **The holdout is
   spent with `--include-holdout`** and read from the `cut_holdout_*`
   fields. `--holdout-only` gives the risk model no history (24 flat months,
   then about 20 live ones), so the runner refuses it with the layer
   (2026-09-27). Then factor-evaluator
   writes the manifest `construction_layer` block, and the JOURNAL.
5. Advisor. Then stop-and-ask 5: the holdout, with the frozen composite and
   the frozen layer.

## 9. Implementation declarations (how the code resolves what §2–§7 left open)

Recorded from the implementation report before any real run. Each point is
tested or stated in the layer block.

**Risk model**
1. **Vol factor start.** The trailing-vol factor is first estimable in
   1999-07 (six prior months). The factor covariance is a pairwise EWMA
   with a PSD floor, and the 24-month minimum counts months with any factor
   return. The book starts in 2001-01 (asserted).
2. **WLS weighting.** The √mktcap weight applies to squared residuals, so
   rows are scaled by mktcap^¼.
3. **Specific variance** uses the 60-month window. Each factor-return column
   is demeaned by its own EWMA mean.
4. **Sector groups** are derived from the data, with `Unclassified` always
   appended. Missing, empty or "UNKNOWN" sectors map to `Unclassified`. The
   real group count is stamped in every block.

**Optimiser**

5. **Neutrality tolerance.** Neutrality to 1e-10 is asserted after steps 1,
   2 and 5. The buffer and the participation cap move names individually,
   and step 5 re-projects after them.
6. **Name cap.** It applies to the target (step 2). A held weight may sit up
   to 1.25 × cap + 2 bp inside the no-trade band.
7. **Step 5.** It repeats three moves: a water-fill re-projection that
   respects participation headroom, then scaling to G_t, then the
   participation clip. Neutrality wins where headroom runs out, and
   `participation_overrides` counts those names.
8. **Who is moved.** Only scored names in the month's universe are moved.
   Unscored held names unwind through the buffer. Sector groups with no
   names that month are dropped from S.
9. **Flat months.** A month is flat when IC_t ≤ 0, when IC_t is undefined,
   or when the risk model is not ready. The book is then exactly flat: the
   buffer and the participation cap are bypassed, the liquidation is
   charged, and the reason is counted.

**Accounting**

10. **Capital and drift.** Capital is reset to the AUM level each month, and
    P&L is swept. The drifted weight is w(1+r)/(1+net). A delisted name goes
    to 0 at no cost.
11. **Names leaving the universe** are sold at the signal date, charged at
    their last known hs, σ and ADV, and not participation-capped. When a
    Stage 3 reference variant skips a month, it holds the drifted book.
12. **Turnover and spreads.**
    - One-way turnover is Σ|Δw|/2, as a % of capital.
    - A missing half-spread falls back to the tier-month median, then the
      month median, then the 1 bp floor.
    - Impact is 0 only where σ is unavailable.
    - The fixed-schedule sensitivity row maps any non-MEGA/MID/SMALL tier to
      the largest bp value.

**Reporting**

13. **Reference rows** (equal_rank_decile, buffered) keep their own
    equal-weight gross-2 scale. They are not sized to G_t.
14. **Bias statistic.** It is the rolling 12-month std of the gross return
    divided by the ex-ante σ, over live months. The block reports its mean and
    the % of months inside 1 ± √(2/12), and the mean ex-ante against realised
    annual vol.
15. **MaxDD** is on the compounded series with the start as a peak of 1.0.
    The peak and trough dates are reported, and the peak reads "inception"
    when there was no prior high.

**Declared 2026-09-27, before any real number (alpha-review of bd5c486)**

16. **Execution timing.** The base trades at the signal-date close (§5). The
    `layer_exec_half_month` row is the realistic-execution bound. Names that
    left the universe are sold at the signal close in both rows, and earn
    nothing that month.
17. **Halted names (caveat).** The book is not changed for them. A name whose
    month ends in a delisting may still be opened or increased at the signal
    close, because its halt is not known then. The layer reports how many
    such positions there were and what they contributed. The contribution is
    the whole position's, not only the increment's.
18. **Sector leak (caveat).** TICKERS.sector is the vendor's CURRENT
    classification. A dead name may be unclassified today for reasons tied
    to its fate, so the `Unclassified` group could carry information about
    the future. The layer reports the group's size and its delisting share
    against the classified names'. A large gap is read as a leak in the
    neutrality constraint and the risk model, not as alpha.
19. **Spread column.** A composite without the `f_bidaskspreadflip` leg is
    refused, both by the runner before any result file exists and by the
    layer itself. There is no whole-panel fallback to the 1 bp floor.
20. **`--holdout-only` is refused** with `--construction-layer`. The holdout
    is spent with `--include-holdout` (§8).

**Declared 2026-09-27, before the holdout is spent (alpha-review of the holdout readout; reporting only, no weight, return or cost changes)**

21. **Every cut carries the headline's field set.** The cuts are
    `cut_holdout_`, `cut_inwindow_`, `cut_exyears_` and `cut_2011_2020_`. Each
    one reports:
    - gross and net annual return, vol, Sharpe and NW t;
    - net MaxDD with its peak and trough, and the net worst 12 months;
    - one-way turnover;
    - the cost split;
    - net by liq_tier;
    - flat months, and budget-scaled months counted separately for live and
      flat months;
    - the gross-budget mean over live months;
    - the participation-hit share;
    - `new_positions_delisting_n`.

    Each cut is computed on its own months only. Drawdown and worst-12-month
    figures compound from the cut's first month, with a peak floor of 1.0 at
    the cut start. The ex-years cut compounds over its own months in date
    order and skips the excluded years.
22. **In-window cuts with a holdout present.** `cut_exyears_` and
    `cut_2011_2020_` exclude months at or after out_of_sample_start.
    `cut_inwindow_` (months before out_of_sample_start) is added. A test shows
    that every in-window cut field, and the annual returns before the
    holdout, are identical with and without the holdout.
23. **The monthly path is saved** as `NNN_LAYER_stageE_<date>.paths.csv`
    beside the .txt, with one row per (row, AUM, month). Floats are written at
    %.17g, so they round-trip exactly. Its sha256[:12] is `paths_sha` in every
    block and in the .meta.json.
