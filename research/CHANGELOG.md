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
