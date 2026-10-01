# CHANGELOG — one entry per iteration, decision first, ≤ 8 lines

## 2026-09-30 — bootstrap
- Project created from the predecessor's (V3) skeleton by allow-list; no factor outcome, registry row, result, spec, translation or verdict carried over (docs/DECISIONS.md D1, leakage audit there).
- Construction changed, selection rules unchanged: ranks within sector (D3); the long-short hedged to the universe's cap-weighted return with an ex-ante 36-month beta (D4); β and a date-free ex-regime Sharpe on every block and rung, never bars (D5); everything else as pre-registered by the predecessor (D6).
- Windows: decisions 1999-01..2021-12; holdout 2022-01..2026-09, spent once under the refresh protocol D8; D2 states what it can and cannot test.
- Version control local only (D9). Snapshot: pending the owner's key file.

## 2026-09-30 — D11: the Stage 1 spread bar reads the raw D10−D1; the Stage 2 guard reads the hedged blend
- Owner's decision after verifying the bootstrap (stop-and-ask 6: D4 hedged both bars, D6/LESSONS 28 listed a hedged guard as not adopted). Confirmed in chat; no run existed.
- Config schema 5 → 6: `stage1_standalone.ls_spread_series: raw`; `stage1_checks` names the bar row after the series it read; `ls_raw_ann_return_pct` required on every Stage 1 block; index carries `raw_ret`.
- No decile-monotonicity statistic, by the owner's instruction. D4, D6, LESSONS 28, CLAUDE.md, METHODOLOGY, the evaluator agent and RECORDS amended.
- HARNESS_SHA e2e0b18a0115 → 73a95d352942; CONFIG_SHA 1cef53e19e16 → 0d88328d5b10. Snapshot still pending (key file now in place; probe OK, 13 tables).

## 2026-09-30 — v0 measured and constructed (runs 001, 002); manifest block written, tag v0-baseline owed
- v0 = Size, Value, Profitability, Investment, Momentum, one seed family each; stamps 73a95d352942 / 0d88328d5b10 / f9d9d9d95731 / 198b281de1a0; provenance verified on both runs, no validation warnings.
- Run 001: mean IC 0.0145, NW t 2.62, halves 0.0275 / 0.0016; hedged LS Sharpe 0.600, 7.32%/yr, MaxDD -45.6% (raw Sharpe 0.719, beta -0.14); turnover 28.0% D10.
- Caveats: 79% of summed LS return in 2000/2001/2003 (ex-top-years Sharpe 0.16); Profitability/Investment coverage 56%/48% at 1998-12; the hedge cost 0.12 Sharpe on a negative-beta LS.
- Run 002 (Stage 3, never a gate): icir_weighted 0.643 hedged but raw 0.441 at beta -0.45; tier_neutral 0.639; buffered 0.555 at half the turnover; vol_targeted 0.306.
- Five baseline registry rows; two records.py defects found (phase gate, frontier filename match), being fixed by the coordinator (scripts/, outside HARNESS_SHA).

## 2026-09-30 — Stage 1 batch 1 (run 003): CBOperProf passes, 11 rejected, 0 inconclusive
- PASS CBOperProf: IC 0.0209, NW t 3.74, halves 0.0290 / 0.0127, raw LS 7.24%/yr (Sharpe 0.48), coverage 73.4%. The spread is in D1 (the short leg), tiers are uniform, beta is -0.57, so the hedge lifts the Sharpe to 0.90. The top 3 years hold 54% of the summed LS; ex-top-years Sharpe 0.64. Financials/Real Estate are excluded by today's SIC. Status stage2_pending; family owed in Phase C.
- Rejected on ic_tstat_nw (every one also fails ic_mean): AM 1.26, Accruals 1.84, AnnouncementReturn 2.28 (208 m), BMdec 0.82, BPEBM -2.06, Beta -0.97, BetaFP -1.28, BetaLiquidityPS -0.27, BetaTailRisk -0.06, BidAskSpread -2.77, BookLeverage -2.59.
- Flip: BidAskSpread |t| 2.77 >= 2.74 qualifies BidAskSpreadFlip as a second hypothesis (flipped LS beta about -0.97, raw Sharpe about 0.04). BookLeverage (2.59) and BPEBM (2.06) do not qualify.
- Provenance verified on 12 blocks with 0 validation warnings. process_finding: docs/CONSTRUCTION.md already names f_bidaskspreadflip as the construction-layer spread source (bootstrap).
- Hedge reading: for AM and BMdec, hedged return is 7.9 and 3.1 pp below raw at mean beta 0.25 and -0.05. That gap comes from ex-ante beta timing and matters for the hedged Stage 2 guard.

## 2026-10-01 — Stage 1 batch 2 (run 004): CF passes, 11 rejected, 0 inconclusive
- PASS CF (cash flow / market equity, Cat.Economic valuation): IC 0.0201, NW t 3.03, halves 0.0331 / 0.0070, raw LS 3.32%/yr (Sharpe 0.20, LS NW t 0.75), coverage 96.1%. The spread is in D9/D10; D1 beats D2-D5. Outside 2000-2002 the annual LS sums to -29 pp (ex-top-years Sharpe -0.17), and the 2011-2020 ICs average about zero. Beta -0.29. Status stage2_pending; family owed in Phase C.
- Rejected on ic_tstat_nw: Cash -1.86, CashProd 0.47, ChAssetTurnover 2.24, ChEQ 1.40, ChInv 1.51, ChInvIA 0.36, ChNWC 2.04, ChTax 1.42, CompositeDebtIssuance 1.49 (each also fails ic_mean), CompEquIss 2.44 (its only failed bar; 2003-2021, 228 m).
- Rejected on ic_mean alone: ChNNCOA 0.0094 < 0.010, with NW t 4.15, the highest of the 24 screened so far.
- No flip qualifies (Cash |t| 1.86 < 2.74). CompositeDebtIssuance passes coverage (46.2%) and names (91.2), so it is not inconclusive. Its 1999-2000 cross-sections are thin (0.3% at the 1998-12 probe) and are its best LS years.
- Provenance verified on 12 blocks, 0 validation warnings. Hedge-gap facts for the open check: CashProd hedged -5.5 pp vs raw at beta 0.22; ChEQ -2.5 pp at beta ~0; CF -0.6 pp at beta -0.29.

## 2026-10-01 — Stage 1 batch 3 (run 005): 0 pass, 12 rejected, 0 inconclusive
- Rejected on ic_tstat_nw (each also fails ic_mean): CoskewACX 1.65, Coskewness 1.65, DelCOA 0.26, DelCOL -0.92, DelEqu 1.25, DelFINL 1.36, DelNetFin 1.08, DolVol -0.18, EBM 0.42, EP 0.96, EarningsSurprise 1.63. All but DelEqu and EarningsSurprise also fail ic_half_min.
- Rejected on ic_mean: EarningsConsistency 0.0090 < 0.010 with NW t 2.60. The raw spread also fails (-0.13%/yr; D1 is the top decile). decision stage1_decided_by_convention_fallback: the first failed bar in check order.
- Not inconclusive: EarningsConsistency coverage 43.3% >= 40 with 85.2 names; CoskewACX/Coskewness 264 LS months >= the 237 floor (first signal 1999-12). No flip qualifies (DelCOL |t| 0.92).
- Halves change sign: CoskewACX -0.0011/0.0135, Coskewness -0.0001/0.0137, EBM 0.0125/-0.0088, EP 0.0135/-0.0026, DolVol 0.0056/-0.0073, DelCOA 0.0074/-0.0055, DelFINL 0.0104/-0.0026, DelNetFin 0.0074/-0.0024, DelCOL 0.0025/-0.0095.
- Provenance verified on 12 blocks, 0 validation warnings. Counters: 36 screened, 2 passed, 34 rejected; composite v0.

## 2026-10-01 — Stage 1 batch 4 (run 006): GP, IdioVol3F, IdioVolAHT pass; 9 rejected, 0 inconclusive
- PASS GP (profitability): IC 0.0155, NW t 3.52, halves 0.0206 / 0.0105, raw LS 8.64%/yr (Sharpe 0.69); the spread is D1 (0.419 %/mo); MEGA has the highest IC (0.0210). Beta -0.45; the hedge adds 2.70 pp (hedged Sharpe 1.09); ex-top-years Sharpe 0.92. Financials and Real Estate are excluded by current SIC, as for CBOperProf.
- PASS IdioVol3F (IC 0.0229, t 3.15, 269 m) and IdioVolAHT (IC 0.0238, t 2.63, 272 m), both volatility: D1-driven, halves level, raw Sharpe 0.14. At beta -0.98 / -1.07 the hedge supplies 68% / 67% of the hedged return (10.10 / 11.68%/yr). The pair are near-duplicates (same construct, top years, annual IC sign in 20 of 23 years) with turnover 64% vs 11%. Each LS-months floor (242 / 244) scales to its own data-start months.
- Rejected on ic_tstat_nw: EntMult 1.96, EquityDuration 1.86 (both valuation; IC halves 0.0320/-0.0052 and 0.0203/0.0004), GrSaleToGrInv 1.58, GrSaleToGrOverhead -0.75, Herf -1.15, HerfAsset -2.00, HerfBE -1.21, High52 0.77. High52's hedged 9.38%/yr is all hedge (beta -1.01, raw -0.13%/yr).
- GrLTNOA rejected (t -2.75): the flip qualifies by |t| but is not screened, because its reversed mean IC (0.0059) misses 0.010 by 0.0041. Under decision flip_not_screened_when_deterministic_fail, the reversal is exact up to the D3 rank offset 1/n_s and qcut ties, not compounding. finding_corrected covers BidAskSpread's run-003 caveat wording.
- Provenance verified on 12 blocks, 0 validation warnings; check_stage1 matches 12/12. Counters: 48 screened, 5 passed, 43 rejected, 2 flips qualified; composite v0.

## 2026-10-01 — Stage 1 batch 5 (run 007): MaxRet passes, 11 rejected, 0 inconclusive
- PASS MaxRet (volatility; IC 0.0233, NW t 3.42, halves 0.0287 / 0.0178, raw LS 4.17%/yr, Sharpe 0.19). D1 anchors the spread and D8-D10 are graded. Beta -0.86, so the hedge supplies 61% of the hedged 10.57%/yr. Ex-top-years Sharpe 0.54. Likely overlap with IdioVol3F / IdioVolAHT: annual IC same sign 20/23 and 19/23 years, correlation 0.94 / 0.97, same loss years 1999/2009/2020. stage2_pending; family owed in Phase C.
- Rejected on ic_tstat_nw: Illiquidity -1.19, IntMom 0.50, IntanBM -0.04, IntanCFP -0.40, IntanEP -0.55, IntanSP -0.62, InvGrowth 1.56, InvestmentTWX 0.15, LRreversal -1.29, MRreversal -0.96 (each also fails ic_mean), and Leverage 1.71 (its only failed bar; IC 0.0125).
- Every long-term-reversal signal has non-positive IC. The Intan quartet's raw 4.3-5.2%/yr is beta (0.56-0.67): hedged -3.5 to -4.3%/yr, same top years 2003/2009/2016. The quartet shares Ret60, and LRreversal's window lies inside it.
- Not inconclusive: Intan 228 LS months >= 205, coverage 61-63%; LRreversal 251 >= 225, MRreversal 269 >= 242, IntMom 275 >= 247. No flip qualifies (largest |t| LRreversal 1.29 < 2.74).
- Provenance verified on 12 blocks, 0 validation warnings, check_stage1 matches 12/12. InvestmentTWX D10 (negative-x0 names) read: nothing visible. Counters: 60 screened, 6 passed, 54 rejected; composite v0.

## 2026-10-01 — Stage 1 batch 6 (run 008): NetEquityFinance and NetPayoutYield pass, 10 rejected, 0 inconclusive
- PASS NetEquityFinance (external financing; IC 0.0166, NW t 3.03, halves 0.0199 / 0.0132, raw 4.54%/yr, Sharpe 0.32). D1 (heaviest issuers) anchors the spread; beta -0.52, so the hedge adds 2.48 pp (35%). Ex-top-years Sharpe 0.43. PASS NetPayoutYield (valuation; IC 0.0145, NW t 2.60 on a thin margin, halves 0.0142 / 0.0148, raw 4.92%/yr). Its spread is graded in the long leg; beta -0.41; 2021 alone +62.3% hedged; ex-top-years Sharpe 0.30. Both stage2_pending.
- The two passers use the same net equity flow with opposite sign: annual IC correlation 0.90, same sign in 15 of 22 years, both lose about 21% in 2020. Against CompEquIss (b2) the annual IC correlation is 0.06 / -0.12. There is a mechanical link to v0 Investment. No Stage 2 number exists.
- Rejected on ic_tstat_nw (each also fails ic_mean): MeanRankRevGrowth -0.12, Mom12mOffSeason 1.24, Mom6m 1.24, MomOffSeason -0.97, MomOffSeason06YrPlus 1.76, MomSeason 0.58, MomSeason06YrPlus 1.90, MomSeasonShort 0.28, NOA 0.62, NetDebtFinance 1.38. Mom6m and Mom12mOffSeason use windows inside v0 Momentum's.
- The 06YrPlus pair are rejected, not inconclusive: 169 / 168 months >= 120, LS floors 152 / 151 met, coverage 40.62 / 40.27% >= 40. That coverage is pooled over 276 months with 107 / 108 leading null months.
- NOA: raw Sharpe 1.01 on IC 0.0016. 67% of the D10-D1 spread lies in D1-D3 and the interior is flat; 1999-2001 carry 49% of the return. No flip qualifies (largest |t| 1.90).
- Provenance verified on 12 blocks, 0 validation warnings, check_stage1 matches 12/12. Counters: 72 screened, 8 passed, 64 rejected; composite v0.

## 2026-10-01 — Stage 1 batch 7 (run 009): OperProfRD, PctAcc and RealizedVol pass, 9 rejected, 0 inconclusive
- PASS PctAcc (accruals; IC 0.0112 on a 0.0012 margin, NW t 4.03, the highest passer t; halves 0.0152 / 0.0071; raw 4.74%/yr, Sharpe 0.76, beta -0.04, so the hedge subtracts 0.59 pp). MEGA IC -0.0009: a SMALL/MID effect. Annual IC correlation 0.69 with Accruals (b1, rejected) and 0.15 with PctTotAcc. TotalAccruals (b8) shares PctTotAcc's numerator.
- PASS OperProfRD (profitability; IC 0.0192, NW t 3.18, raw 6.44%/yr, beta -0.60, the hedge supplying 41% of 10.94%/yr). Annual IC correlation 0.97 with CBOperProf and 0.85 with GP; it shares the revenue - cor - sgna core with v0 Profitability. 2000 hedged +120.2%. Ex-top-years Sharpe 0.45.
- PASS RealizedVol (volatility; IC 0.0234, NW t 2.81, raw 3.39%/yr, Sharpe 0.13). Its beta of -1.16 is the most negative of the passers; the hedge supplies 72% of 12.13%/yr. Annual IC correlation 0.97 with each of IdioVol3F, IdioVolAHT and MaxRet. All three passers are stage2_pending.
- Rejected on ic_tstat_nw (each also fails ic_mean): OrgCap 1.70, PctTotAcc 0.91, Price -1.41, PriceDelayRsq -2.12, PriceDelaySlope -1.69, PriceDelayTstat -1.68, ResidualMomentum 0.72, ReturnSkew 2.22. OPLeverage fails on ic_mean alone (0.0087; NW t 2.89; fallback convention).
- PriceDelaySlope and PriceDelayTstat are near-identical (annual IC correlation 1.00). Price has beta 0.77: raw +2.98%/yr becomes -5.89%/yr hedged on a negative IC. No flip qualifies (largest |t| 2.12 < 2.74).
- Provenance verified on 12 blocks; check_stage1 matches 12/12. One validation warning: Price coverage is 100%, which follows from the universe's own price floor; there is no mass point. Counters: 84 screened, 11 passed, 73 rejected; composite v0.

## 2026-10-01 — Stage 1 batch 8 (run 010): RoE, STreversal, ShareIss1Y, ShareIss5Y and TrendFactor pass; 7 rejected; 0 inconclusive
- PASS ShareIss5Y (NW t 3.67, hedged Sharpe 1.085, beta -0.24; 223 months, coverage pooled 62.6%) and ShareIss1Y (NW t 3.52, raw 7.12%/yr). Their annual ICs correlate 0.89 with each other and 0.81-0.95 with NetEquityFinance and NetPayoutYield; CompEquIss -0.01 / 0.21. Both lose in 2020 (-26.6 / -15.7%) and gain in 2021.
- PASS RoE (NW t 3.34; beta -0.59, the hedge supplying 60% of 7.38%/yr; SMALL raw Sharpe 0.03). Spearman 0.71 with the v0 Profitability leg (spec). Annual IC correlates 0.93 with OperProfRD and 0.86 with CBOperProf.
- PASS STreversal (NW t 2.96, plain t 2.53). Beta +0.44 is the first material positive beta among passers: raw +3.37%/yr becomes -0.48%/yr hedged. Ex-top-years Sharpe -0.369. The spread is SMALL; turnover 86-89%; lag-1 IC 0.0027. It is the month v0 Momentum skips.
- PASS TrendFactor (NW t 2.79, raw 10.12%/yr). Halves 0.0290 / 0.0053; 2009 hedged +91.6% is 51% of the summed LS; lag-1 IC 0.0030; turnover 63-65%; 228 months.
- Rejected: SP on ic_tstat_nw 2.496817 (short by 0.003183, no rounding; the index shows 2.50); VolMkt 2.25 (annual IC correlation 0.88-0.95 with the four volatility passers); VolSD 2.36; ReturnSkew3F 0.35; TotalAccruals -0.01 (annual IC correlation 0.84 with PctTotAcc, 0.09 with PctAcc); VarCF 0.76. RevenueSurprise fails on ic_mean 0.0094 (NW t 2.78; fallback convention).
- Provenance verified on 12 blocks, 0 validation warnings, check_stage1 12/12. No flips (largest negative OSAP-sign |t| 0.01). Counters: 96 screened, 16 passed, 80 rejected; composite v0.

## 2026-10-01 — Stage 1 batch 9 (run 011, the last): 8 pass (incl. BidAskSpreadFlip at the 2.74 flip bar), 3 rejected, 0 inconclusive
- PASS cfp (NW t 3.65; the highest IC of the 24 passers at 0.0246). Its halves are front-loaded (0.0391 / 0.0102); hedged 7.47%/yr is below raw 9.45. Annual IC correlation 0.96 with CF. PASS XFIN (NW t 3.57; beta -0.47, hedge share 24%; 0.95 with NetEquityFinance and ShareIss1Y). PASS roaq (NW t 3.37; beta -0.58, hedge share 47%; 0.97 with RoE, 0.91 with OperProfRD). PASS VolumeTrend (NW t 2.87, IC 0.0114 on a 0.0014 margin, 228 months; a MID effect, bear Sharpe 0.0002).
- PASS zerotrade6M / 12M / 1M (NW t 2.93 / 2.83 / 2.63): one low-turnover sort. Annual IC correlates 0.99 within the trio and 0.90-0.96 with the volatility passers; beta about -0.7, hedge share 53-63%. zerotrade1M carries the off-horizon caveat (a 1-month hold vs OSAP's 12-month).
- PASS BidAskSpreadFlip, a flipped-sign second hypothesis judged at |NW t| >= 2.74: 2.762832 clears it by 0.0228. Its offset from run 003's negation: IC +0.000098, t -0.0076, raw spread +0.13 pp; no bar crossed. The raw Sharpe is 0.046 and beta -0.98, so the hedge is 88% of the hedged 8.72%/yr. D10 adds nothing and bear Sharpe is -0.244. Annual IC correlation with IdioVol3F is 0.98.
- Rejected on ic_tstat_nw: dNoa 2.19 (also ic_mean and h2 -0.0002; raw Sharpe 0.95 from the D1 tail and 1999-2001, the NOA pattern), grcapx 1.37, grcapx3y 0.89 (both also fail ic_mean).
- Provenance verified on 11 blocks, 0 validation warnings, check_stage1 11/11. Counters: 107 screened, 24 passed, 83 rejected; composite v0. Every constructible predictor now has a Stage 1 row.

## 2026-10-01 — Stage 2 ladder 1 (run 012): all five rungs PASS; application pending the advisor
- PASS on both bars, in the declared order (residual NW t > 2.0, paired hedged dLS t >= -2.0): PctAcc 4.67 / 0.09 (investment, weight 0.10), CBOperProf 3.02 / 0.95 (profitability, 0.10), ShareIss5Y 3.61 on 223 m / 2.83 (opens external_financing, 1/6), cfp 2.97 / 2.19 (value, 0.083), XFIN 3.27 / -0.64 (external_financing, 0.083). check_stage2 agrees on all five.
- Provenance: four stamps equal the repo; include_holdout False; eval_end 2021-12-31; 0 validation warnings. The base arm equals run 001 to six places, and each rung's base equals the previous WITH arm.
- Composite path, v0 to rung 5 (hedged): IC 0.0145 -> 0.0245, NW t 2.62 -> 4.27, Sharpe 0.600 -> 0.914 (0.996 after cfp), MaxDD -45.6 -> -47.8, beta -0.14 -> -0.34, ex-top-years Sharpe 0.16 -> 0.48 (0.61 after cfp).
- Raw dLS next to the guard: -0.01 / +0.31 / +1.46 / +0.92 / -0.41 pp/yr, with approximate t -0.02 / 0.67 / 1.67 / 1.16 / -0.57 (hedged paired SE). The hedge adds about 1 pp on rungs 3 and 4.
- XFIN facts: dIC -0.0005 (t -0.62), dSharpe -0.082, MaxDD 7.1 pts worse, beta -0.26 -> -0.34. It halves ShareIss5Y's weight. Both bars pass, and the rules decide on those bars alone.
- Records: five rows carry stage2 fields with status stage2_pending; provenance_verified, 5 factor_evaluated and registry_rows_written are logged. No composite edit, manifest block or tag yet (v1..v5 owed on application).

## 2026-10-01 — v1 = v0 + PctAcc (investment family): accepted and applied (runs 013, 014); tag v1-add-PctAcc owed
- Accepted from run 012 rung 1 on both bars: residual IC NW t 4.67 > 2.0; guard paired hedged dLS t 0.09 >= -2.0. Raw dLS -0.01 pp/yr against hedged +0.06: both about 0, so the raw series does not contradict the guard. Ladder 1 faced a 5-leg base, where residual IC is easiest to find.
- Applied: PctAcc.py moved to factors/accepted/ and appended to COMPOSITE_FACTORS; COMPOSITE_VERSION v1; COMPOSITE_SHA f9d9d9d95731 -> cbeb16455bf4, the other stamps unchanged; pytest 434 passed. Families: investment = Investment, PctAcc (0.10 each).
- Run 013 (--baseline --stage 2) reproduces the rung 1 WITH arm to six places: IC 0.016858 (NW t 3.02), hedged Sharpe 0.61395, 7.382577%/yr, MaxDD -41.28, beta -0.121, raw Sharpe 0.737, ex-top-years Sharpe 0.202, turnover 27.6%.
- Run 014 (Stage 3, never a gate): equal_rank_decile 0.614; icir_weighted 0.709 hedged (raw 0.494, beta -0.39, PctAcc weight 0.29); tier_neutral 0.604; buffered 0.555 at turnover 14.7%; vol_targeted 0.339.
- Records: manifest block v1; provenance_verified (013, 014), construction_reported, composite_updated; PctAcc row accepted; index n_accepted 1. Next: v2 (CBOperProf) on the coordinator's word.

## 2026-10-01 — v2 = v1 + CBOperProf (profitability family): accepted and applied (runs 015, 016); tag v2-add-CBOperProf owed
- Accepted from run 012 rung 2 (base v1) on both bars: residual IC NW t 3.02 > 2.0 (50% of its own IC); guard paired hedged dLS t 0.95 >= -2.0 (hedged +0.44, raw +0.31 pp/yr, same sign). Paired dIC -0.0000 (t -0.01) is a diagnostic.
- Applied: CBOperProf.py moved to factors/accepted/ and appended; COMPOSITE_VERSION v2; COMPOSITE_SHA cbeb16455bf4 -> 8b444636f0a1, the other stamps unchanged; pytest 434 passed. Families: profitability = Profitability, CBOperProf (0.10 each).
- Run 015 reproduces the rung 2 WITH arm to six places: IC 0.016855 (NW t 3.02), hedged Sharpe 0.660554, 7.821336%/yr, MaxDD -37.07, beta -0.122, raw Sharpe 0.777, ex-top-years Sharpe 0.249; full-leg coverage 72.7% (Financials/Real Estate).
- Run 016 (Stage 3, never a gate): equal_rank_decile 0.661; icir_weighted 0.813 hedged (raw 0.499, beta -0.47); tier_neutral 0.692; buffered 0.632 at turnover 15.0%; vol_targeted 0.378.
- Records: manifest block v2 (the v1 git_tag line is left as it reads); provenance_verified (015, 016), construction_reported, composite_updated; CBOperProf row accepted; index n_accepted 2.

## 2026-10-01 — v3 = v2 + ShareIss5Y (opens external_financing, 6 families): accepted and applied (runs 017, 018); tag v3-add-ShareIss5Y owed
- Accepted from run 012 rung 3 (base v2) on both bars. Residual IC NW t 3.61 > 2.0, on 223 months, at 76% of its own IC. Guard paired hedged dLS t 2.83 >= -2.0 over 276 months; for the first 53 the family is absent and the blend renormalises to v2. Raw dLS +1.46 pp/yr agrees in sign with the hedged +2.47.
- Applied: ShareIss5Y.py (ARQ, 65-month history gate) moved to factors/accepted/; COMPOSITE_VERSION v3; COMPOSITE_SHA 8b444636f0a1 -> 73ee92fe0723, the other stamps unchanged; pytest 434 passed. FAMILIES header shows 6 families, external_financing:ShareIss5Y; manifest families match.
- Run 017 reproduces the rung 3 WITH arm to six places: IC 0.021532 (NW t 3.98), hedged Sharpe 0.847944, 10.287625%/yr, MaxDD -41.92, beta -0.192, raw Sharpe 0.874, ex-top-years Sharpe 0.465. Full-leg coverage 47.6%.
- Run 018 (Stage 3, never a gate): equal_rank_decile 0.848; icir_weighted 0.948 hedged (raw 0.580, beta -0.47); tier_neutral 0.909; buffered 0.789 at turnover 13.9%; vol_targeted 0.655.
- Records: manifest block v3; provenance_verified (017, 018), construction_reported, composite_updated; ShareIss5Y row accepted; index n_accepted 3.

## 2026-10-01 — v4 = v3 + cfp (value family): accepted and applied (runs 019, 020); tag v4-add-cfp owed
- Accepted from run 012 rung 4 (base v3) on both bars. Residual IC NW t 2.97 > 2.0, at 42% of its own IC. Guard paired hedged dLS t 2.19 >= -2.0; raw dLS +0.92 pp/yr agrees in sign with the hedged +1.73, so the hedge adds about 0.8 pp. Spanning alpha t 0.40 (R2 0.26) against residual t 2.97 / dIC t 3.10: both reported, not reconciled.
- Applied: cfp.py moved to factors/accepted/; COMPOSITE_VERSION v4; COMPOSITE_SHA 73ee92fe0723 -> 3329679c69fb, the other stamps unchanged; pytest 434 passed. Families: value = Value, cfp (0.083 each); still 6 families.
- Run 019 reproduces the rung 4 WITH arm to six places: IC 0.024946 (NW t 4.51), hedged Sharpe 0.995998, 12.019142%/yr, MaxDD -40.63, beta -0.263, raw Sharpe 0.913, ex-top-years Sharpe 0.614.
- Run 020 (Stage 3, never a gate): equal_rank_decile 0.996; tier_neutral 1.006 (raw 0.834, beta -0.34); icir_weighted 0.934 (raw 0.605, beta -0.47); buffered 0.904 at turnover 13.0%; vol_targeted 0.774.
- Records: manifest block v4; provenance_verified (019, 020), construction_reported, composite_updated; cfp row accepted; index n_accepted 4. CF (rank 14, annual-IC correlation 0.96) will face a base holding cfp.

## 2026-10-01 — v5 = v4 + XFIN (external_financing, 2nd leg): accepted and applied (runs 021, 022); ladder 1 closed 5/5; tag v5-add-XFIN owed
- Accepted from run 012 rung 5 (base v4) on both bars: residual IC NW t 3.27 > 2.0; guard t -0.64 >= -2.0. Every diagnostic worsened: dIC -0.0005 (t -0.62), dSharpe -0.082, MaxDD 7.1 pts worse hedged and 7.8 raw. Raw dLS -0.41 pp/yr is also negative, so the hedge did not rescue it. The -2.0 guard admits it by design (decision ladder1_acceptance).
- Applied: XFIN.py moved to factors/accepted/; COMPOSITE_VERSION v5; COMPOSITE_SHA 3329679c69fb -> d27916e567f2, the other stamps unchanged; pytest 434 passed. external_financing = ShareIss5Y, XFIN (0.083 each; ShareIss5Y halved).
- Run 021 reproduces the rung 5 WITH arm to six places: IC 0.024477 (NW t 4.27), hedged Sharpe 0.91412, 11.558369%/yr, MaxDD -47.75, beta -0.344, raw Sharpe 0.808, ex-top-years Sharpe 0.479.
- Run 022 (Stage 3, never a gate): every variant is below v4. equal_rank_decile 0.914; icir_weighted 0.926 (raw 0.559, beta -0.55); tier_neutral 0.861; buffered 0.830 at turnover 13.2%; vol_targeted 0.653.
- Records: manifest block v5; provenance_verified (021, 022), construction_reported, composite_updated, batch_closed stage2_l1 (5 pass); XFIN row accepted; index n_accepted 5. Next ladder: ranks 6-10 (GP, ShareIss1Y, MaxRet, roaq, RoE) on v5.

## 2026-10-01 — Stage 2 ladder 2 (run 023): GP, MaxRet, roaq, RoE PASS; ShareIss1Y REJECTED; application pending the advisor
- Bars (residual NW t > 2.0, paired hedged dLS t >= -2.0): GP 2.74 / 0.43 (profitability, 0.056); ShareIss1Y 1.88 / 0.17, rejected on resid_ic_tstat_nw (faced ShareIss5Y and XFIN); MaxRet 4.01 / 1.75 (opens volatility, 0.143); roaq 3.73 / 1.95 (profitability, 0.036); RoE 2.41 / -1.26 (profitability, 0.029). check_stage2 agrees 5/5.
- Provenance: four stamps equal the repo, include_holdout False, eval_end 2021-12-31, 0 warnings. The base equals run 021 to six places; each base is the previous PASS rung's WITH arm, and ShareIss1Y is in no later base.
- Path from v5 to rung 5 (hedged): IC 0.0245 -> 0.0323; Sharpe 0.914 -> 0.932 (peak 0.967 after roaq); 11.56 -> 14.87%/yr; MaxDD -47.8 -> -43.7; beta -0.34 -> -0.73; raw Sharpe 0.808 -> 0.579; turnover 25.0 -> 44.3%.
- Raw vs hedged dLS (pp/yr; hedge part = hedged - raw): GP +0.35 / +0.16 (-0.20); ShareIss1Y +0.04 / +0.07; MaxRet -0.59 / +2.23 (+2.82, opposite signs); roaq +0.72 / +1.23 (+0.51); RoE -0.45 / -0.31 (+0.14). Approximate raw t: 0.96 / 0.10 / -0.46 / 1.14 / -1.83.
- RoE: residual share 0.24, dSharpe -0.036, spanning alpha t -0.33. Like XFIN, it is admitted by the -2.0 guard. The rules decide on residual IC and the hedged guard only.
- Records: five rows carry stage2 fields (ShareIss1Y rejected; the other four stage2_pending). Logged provenance_verified, 5 factor_evaluated and registry_rows_written; index rebuilt; check OK. v6-v9 owed on application.

## 2026-10-01 — v6 = v5 + GP (profitability, 3rd leg): accepted and applied (runs 024, 025); tag v6-add-GP owed
- Accepted from run 023 rung 1 (base v5) on both bars: residual IC NW t 2.74 > 2.0, at 47% of its own IC; guard paired hedged dLS t 0.43 >= -2.0. Raw dLS +0.35 pp/yr beats the hedged +0.16, so the hedge subtracts 0.20 pp. dIC -0.0003 (t -0.79) against spanning alpha t 3.62: not reconciled (decision ladder2_acceptance).
- Applied: GP.py moved to factors/accepted/; COMPOSITE_VERSION v6; COMPOSITE_SHA d27916e567f2 -> 21a6688ae5d1, the other stamps unchanged; pytest 434 passed. Profitability = Profitability, CBOperProf, GP at 0.056 each.
- Run 024 reproduces the rung 1 WITH arm on 16 of 16 stats to six places: IC 0.024198 (NW t 4.23), hedged Sharpe 0.92549, 11.715703%/yr, MaxDD -49.42, beta -0.323, raw Sharpe 0.843, ex-top-years Sharpe 0.490.
- Run 025 (Stage 3, never a gate): equal_rank_decile 0.925; icir_weighted 1.026 (raw 0.639, beta -0.55, MaxDD -28.1); tier_neutral 0.905; buffered 0.833 at turnover 13.3%; vol_targeted 0.686.
- Records: manifest block v6; logged provenance_verified (024, 025), construction_reported and composite_updated; GP row set to accepted. Next: v7 = v6 + MaxRet (target IC 0.030522 / Sharpe 0.951223 / 13.947962%).

## 2026-10-01 — v7 = v6 + MaxRet (opens volatility, 7th family): accepted and applied (runs 026, 027); tag v7-add-MaxRet owed
- Accepted from run 023 rung 3 (base v6) on both bars: residual IC NW t 4.01 > 2.0, at 77% of its own IC; guard t 1.75 >= -2.0. Raw dLS is -0.59 pp/yr against hedged +2.23, so the guard's gain is all hedge (+2.82 pp, paired SE about 1.3). Residual IC is the operative gate (decision hedge_guard_negative_beta_property).
- Applied: MaxRet.py moved to factors/accepted/; COMPOSITE_VERSION v7; COMPOSITE_SHA 21a6688ae5d1 -> 43c92213ae73, the other stamps unchanged; pytest 434 passed. Families: 7 at 1/7 each; Size, Momentum and MaxRet carry 0.143 each.
- Run 026 reproduces the rung 3 WITH arm on 16 of 16 stats to six places: IC 0.030522 (NW t 4.49), hedged Sharpe 0.951223, 13.947962%/yr, MaxDD -41.68, beta -0.649, raw Sharpe 0.622, ex-top-years Sharpe 0.623, turnover 43.4%.
- Run 027 (Stage 3, never a gate): tier_neutral 0.968 (beta -0.71); equal_rank_decile 0.951; buffered 0.928 at turnover 24.6%; icir_weighted 0.911 (raw 0.493, beta -0.76); vol_targeted 0.842.
- The total-return proxy credits |dbeta|*rf, about 0.6 pp here; deferred to Phase E. Records: manifest block v7; logged provenance_verified (026, 027), construction_reported and composite_updated; MaxRet row set to accepted.

## 2026-10-01 — v8 = v7 + roaq (profitability, 4th leg): accepted and applied (runs 028, 029); tag v8-add-roaq owed
- Accepted from run 023 rung 4 (base v7) on both bars: residual IC NW t 3.73 > 2.0, at 57% of its own IC; guard t 1.95 >= -2.0. Raw dLS +0.72 and hedged +1.23 pp/yr agree in sign; the hedge part is +0.51 (about 41%). Spanning alpha t 0.39 at R2 0.44 against residual t 3.73 and dIC t 2.66: not reconciled.
- Applied: roaq.py moved to factors/accepted/; COMPOSITE_VERSION v8; COMPOSITE_SHA 43c92213ae73 -> a12e87c5fb36, the other stamps unchanged; pytest 434 passed. Profitability = Profitability, CBOperProf, GP, roaq at 0.036 each; 7 families.
- Run 028 reproduces the rung 4 WITH arm on 16 of 16 stats to six places: IC 0.032018 (NW t 4.50), hedged Sharpe 0.967311, 15.18071%/yr, MaxDD -43.36, beta -0.721, raw Sharpe 0.613, ex-top-years Sharpe 0.604, turnover 44.1%.
- Run 029 (Stage 3, never a gate): equal_rank_decile 0.967 (the best); tier_neutral 0.947; buffered 0.938 at turnover 25.5%; vol_targeted 0.844; icir_weighted 0.817 (raw 0.423, beta -0.83).
- Records: manifest block v8; logged provenance_verified (028, 029), construction_reported and composite_updated; roaq row set to accepted. Next: v9 = v8 + RoE (target IC 0.032255 / Sharpe 0.931566 / 14.870865%).

## 2026-10-01 — v9 = v8 + RoE (profitability, 5th leg): accepted and applied (runs 030, 031); ladder 2 closed 4/5; tag v9-add-RoE owed
- Accepted from run 023 rung 5 (base v8) on both bars: residual IC NW t 2.41 > 2.0; guard t -1.26 >= -2.0. Every LS diagnostic worsened: dSharpe -0.036, spanning alpha -1.00%/yr (t -0.33), raw dLS -0.45 pp/yr (approximate t -1.83, the closest to -2.0 in either ladder). Raw Sharpe, ex-top-years, bear, bull and hit rate all fell. Residual share 0.24, the ladder low. The -2.0 guard admits it by design (decision ladder2_acceptance).
- Applied: RoE.py moved to factors/accepted/; COMPOSITE_VERSION v9; COMPOSITE_SHA a12e87c5fb36 -> c961f5791816, the other stamps unchanged; pytest 434 passed. Profitability now has 5 legs at 1/35 each; 7 families.
- Run 030 reproduces the rung 5 WITH arm on 16 of 16 stats to six places: IC 0.032255 (NW t 4.50), hedged Sharpe 0.931566, 14.870865%/yr, MaxDD -43.67, beta -0.734, raw Sharpe 0.579, ex-top-years Sharpe 0.581.
- Run 031 (Stage 3, never a gate): every variant is below v8. equal_rank_decile 0.932; buffered 0.919 at turnover 25.8%; tier_neutral 0.905; icir_weighted 0.806 (raw 0.415, beta -0.85); vol_targeted 0.777.
- Records: manifest block v9; logged provenance_verified (030, 031), construction_reported, composite_updated and batch_closed stage2_l2 (4 pass, 1 fail); RoE row set to accepted. Next ladder: ranks 11-15 on v9.

## 2026-10-01 — Stage 2 ladder 3 (run 032): IdioVol3F, STreversal PASS; OperProfRD, NetEquityFinance, CF REJECTED; application pending the advisor
- Bars (residual NW t > 2.0, paired hedged dLS t >= -2.0): OperProfRD -0.42 / 0.92 (profitability, 0.024); IdioVol3F 2.030731 / 0.89 (volatility, 0.071; margin 0.031, the thinnest yet); NetEquityFinance 1.40 / 0.47 (external_financing); CF 1.02 / -0.76 (value); STreversal 3.81 / -0.54 (opens short_term_reversal, 0.125). check_stage2 agrees 5/5.
- Provenance: four stamps equal the repo, include_holdout False, eval_end 2021-12-31, 0 warnings. Rungs 1-2 base equals run 030 to six places (66 fields); rungs 3-5 base is IdioVol3F's WITH arm; OperProfRD is in no later base.
- Rejections faced near-twins: OperProfRD vs CBOperProf (annual IC corr 0.97; residual IC negative), NetEquityFinance vs XFIN (0.95) and ShareIss5Y (0.91), CF vs cfp (0.96; spanning alpha t -2.70). The declared order made these expected.
- Path v9 -> rung 5 WITH arm (hedged): IC 0.0323 -> 0.0355 (NW t 4.50 -> 5.36); Sharpe 0.932 -> 0.919 -> 0.942; 14.87 -> 14.61%/yr; MaxDD -43.7 -> -39.5; beta -0.734 -> -0.512; raw Sharpe 0.579 -> 0.737; turnover D10 44.3 -> 59.1%.
- Raw vs hedged dLS (pp/yr; hedge part = hedged - raw): OperProfRD +0.19 / +0.17 (-0.02); IdioVol3F +0.41 / +0.38 (-0.03); NetEquityFinance +0.01 / +0.19 (+0.18); CF -0.67 / -0.40 (+0.28); STreversal +1.09 / -0.64 (-1.73 at dbeta +0.20: opposite signs, implied market mean 8.6%/yr). Approximate raw t: 1.03 / 0.95 / 0.02 / -1.30 / 0.91.
- Records: five rows carry stage2 fields (three rejected, two stage2_pending); logged provenance_verified, 5 factor_evaluated, finding_corrected (IdioVol3F/MaxRet corr 0.94, not 0.97), registry_rows_written; index rebuilt; check OK. v10 and v11 owed on application.
