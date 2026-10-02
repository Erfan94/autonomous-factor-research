# Journal — dated step log

Append one entry per step: what ran, what was decided, what it cost. Numbers
and ids, not essays; the reasoning lives in DECISIONS.md and events.jsonl.

## 2026-09-30 — bootstrap (session: Fable 5.1, run from the predecessor's directory)
- Owner's instruction: a fresh project from V3's skeleton, the four construction changes (D3–D6), decisions 1999–2021, holdout 2022-01..2026-09 spent after September closes, a fresh Sharadar pull, local git only.
- Copied 762 tracked files by allow-list (no specs, translations, records, results, manifest blocks or paper); leakage grep logged in D1; 109 field verifications reset to `probed_on_prior_snapshot`; composite reduced to v0; layer config pin and regime years reset.
- Harness: within-group ranking (`rank_one_factor(group_col)`), `universe_market_return`, `trailing_beta` / `hedge_long_short`, `regime_diagnostics`, `_cut_stats` and the cut fields under `--include-holdout`, the β/regime rows on every Stage 2 rung, hedged Stage 3 variants, the layer's family scores on the same ranks, `include_holdout` set under `--holdout-only` (the predecessor's HD-HOLDOUT-FLAG), `stamp_block.py` reading the manifest's real holdout state.
- Config schema 5: `ranking`, `market_hedge`, `diagnostics`; dates moved.
- Tests: 429 passing (`pytest tests/`), including `tests/test_v4_construction.py` (within-sector ranks and the thin-group fallback; β at t uses only months < t; the hedged series has ~zero ex-post β; the regime rule is date-free; the report's hedge, regime and cut sections; the baseline emits `cut_holdout_*` under `--include-holdout`; every block carries β).
- Snapshot: pending the API key file (the owner copies it into the project root; the bootstrap session may not read the predecessor's).

## 2026-09-30 — verification of the bootstrap and D11 (session: Fable 5.1, run from the predecessor's directory)
- Owner asked for a verification of the bootstrap against their instruction. Verified: allow-list transfer (762 files, no outcomes), windows 1999-01..2021-12 / 2022-01..2026-09, D3–D6 in code with tests, local git only, siblings denied, 429 tests. Not done: the snapshot pull (the key file arrived after the last commit; `snapshot.py probe` now reports key OK and all 13 tables entitled).
- Found a self-contradiction: D4 hedged the Stage 1 spread bar and the Stage 2 guard; D6 and LESSONS 28 listed a hedged guard as not adopted. Owner chose the hybrid (Stage 1 raw, Stage 2 guard hedged) and declined any decile-monotonicity diagnostic. Written as D11; config schema 6; five new tests.
- Cost: one harness + config move with no run behind it; the stamps are in CHANGELOG.

## 2026-09-30 — snapshot recorded (session: Opus 5.5 runner, Fable 5.1 advisor)
- `snapshot.py download`: 13 tables in ~16 min (SEP 991 MB zip, 45.4m rows; SF1 3.2m; DAILY 39.8m; SF3 81.2m). FUNDS mapped, not held.
- `verify` OK: config vocabularies match the bytes string-for-string (NYSE/NASDAQ/NYSEMKT; two Domestic Common categories; all 10 delisting actions; ART); TICKERS.table carries legacy codes SEP/SF1, both accepted by TICKERS_SCOPE; marketcap median $712m; SEP starts 1997-12-31, exactly the first momentum window.
- `manifest`: DATA_SHA nodata -> 198b281de1a0. `live`: 14 tables checked, column-complete, full history.
- `records.py check` DRIFTed on two unregistered bootstrap event types; registered them (scripts/, not harness). Check OK.

## 2026-09-30 — v0 baseline (runs 001, 002) and records.py fixes
- Run 001 `--baseline --stage 2`: 137 s wall (panel build 61 s, then cached). v0 IC 0.0145, NW t 2.62, halves 0.0275/0.0016; hedged LS Sharpe 0.60, 7.32%/yr, MaxDD −45.6%, β −0.14 fw; raw Sharpe 0.72; ex-top-3-years (2000, 2001, 2003) Sharpe 0.16.
- Run 002 `--baseline --stage 3`: 60 s. icir_weighted 0.64 hedged (raw 0.44, β −0.45: the hedge adds market exposure to a net-short book); buffered halves turnover for −0.045 Sharpe; vol_targeted 0.31.
- Cost: both runs far under the ORCHESTRATION estimates (25 min baseline) on a cached panel; Phase B planning should re-time the first 12-factor batch rather than assume an hour.
- factor-evaluator: provenance verified on both; five baseline registry rows; v0 manifest block. It found two scripts/records.py defects (baseline stage-2 run opened the phase gate; leg row Investment.yaml masked OSAP's Investment predictor). Fixed; UNACCOUNTED 207. The OSAP Investment candidate will be named InvestmentTWX.
- Measured two open items: 21 in-universe performance delistings is sound (unknown reasons default to performance); thin early Profitability/Investment coverage is Sharadar ART lacking TTM flows for calendardate 1998Q1–Q3, confined to signals 1998-12..1999-02 (finding_corrected supersedes the manifest's unmeasured explanation).

## 2026-09-30 — Phase A inventory (fetch batches 01-26)
- 212 OSAP predictors specced at ref b4e911e6 in 26 fetch batches of eight (osap-fetcher, pairs of four), field-checked where unverified (eps, opinc/oibdp, revtq/cshprq), translated (sharadar-translator), preflighted serially in one process, and audited by alpha-reviewer in 17 review passes.
- Outcome: 106 candidate files preflight-passed; 101 frontier rows (64 data_unavailable, 28 preflight_failed, 9 data_start); 5 baseline rows. UNACCOUNTED 0.
- Rulings taken on the way (decision events): debt gate on SF1.debt users (and its exemption where OSAP zero-fills dltt/dlc: dNoa); current-SIC signal values under D3/HX-2; full windows for return and volume windows; capex sign ruling; EP/NetPayoutYield flows lagged to the t-6 price; OrgCap fiscal-year handling; history gates on every price-window factor; tie rule applied literally.
- Records defects found and corrected append-only: event timestamps estimated rather than read from the clock (rows 219-419; finding_corrected); stale field_map ib/ibq entries remapped; one commit swept in in-flight specs.
- Cost: every preflight 1-3 minutes on the cached panel; the reviews found one critical (PriceDelayRsq history gate) and ~20 major issues, all fixed before any screen.

## 2026-10-01 — Phase B: Stage 1 screen (runs 003-011)
- 107 screens (106 candidates + BidAskSpreadFlip) in 9 alphabetical batches fixed before run 1 (research/stage1_batches.yaml); factor-evaluator wrote every row; check_stage1 agreed with the stamped decision on all 107.
- Outcome: 24 pass, 83 rejected, 0 inconclusive. Passers cluster into volatility/liquidity (IdioVol3F, IdioVolAHT, MaxRet, RealizedVol, zerotrade x3, BidAskSpreadFlip; beta -0.7 to -1.2, hedge 53-88% of the hedged return), profitability (CBOperProf, GP, OperProfRD, RoE, roaq, PctAcc), cash-flow value (CF, cfp), net issuance/payout (NetEquityFinance, NetPayoutYield, ShareIss1Y, ShareIss5Y, XFIN), and STreversal, TrendFactor, VolumeTrend.
- Rejections dominated by small within-sector IC after 1999: five signals fail ic_mean alone at NW t > 2.5 (ChNNCOA 4.15, OPLeverage 2.89, RevenueSurprise 2.78, EarningsConsistency 2.60, plus SP at t 2.4968); tail-driven spreads (NOA raw Sharpe 1.01, dNoa 0.95) fail the rank-IC bars by design.
- Flips: BidAskSpread qualified (|t| 2.77) and its declared Flip passed at the 2.74 bar (t 2.7628); GrLTNOA qualified (|t| 2.75) but not screened (reversed IC 0.0059 < 0.010; decision flip_not_screened_when_deterministic_fail). Within-sector rank reversal offset measured at 1e-4 in IC.
- Checks: hedge arithmetic independently reproduced to 1e-15 (gaps are the trailing-beta regime-lag covariance, a D4 design property; the Stage 2 guard inherits it); BidAskSpreadFlip named in the construction-layer template before any screen, removed by D7.2 in Phase E.
- Cost: 4.9 h of screening wall time (19-92 min per batch; daily-price batches slowest), evaluation overlapped with the next screen; 0 stamps moved.

## 2026-10-01 — Phase C: families and the Stage 2 order
- The 24 passers carry 11 SignalDoc Cat.Economic labels against a cap of 9 families. One decision (phase_c_family_partition) fixed the label->family map before any assignment: two absorptions where an existing definition literally covers the construction (volume->liquidity; accruals->investment, as Hou-Xue-Zhang classify it); four new families (volatility, liquidity, external_financing, short_term_reversal). Rejected alternatives named in the event; Stage 1 numbers were visible and that is disclosed.
- Families (members incl. seed): size 1, value 4, profitability 6, investment 2, momentum 2, volatility 4, liquidity 5, external_financing 4, short_term_reversal 1. Written to families.yaml, every passer's FactorDef.family and registry row, 24 family_assigned events in Stage 1 order.
- research/stage2_order.yaml declared: full-precision Stage 1 NW t descending (PctAcc 4.03 first, NetPayoutYield 2.60 last); tie-break mean IC then name. No Stage 2 number exists.

## 2026-10-01 — Phase D: Stage 2 ratchet (runs 012-044)
- Five ladders cut from stage2_order.yaml (5/5/5/5/4 rungs), each against the composite at its declaration; rung i faced the base plus every earlier passer.
- Outcome: 24 tested, 14 accepted, 10 rejected (every one on residual IC NW t, none on the guard), 0 inconclusive. Ladder tallies 5/0, 4/1, 2/3, 3/2, 0/4.
- Composite v0 -> v14: 19 legs in 9 families; IC 0.0145 -> 0.0389, NW t 2.62 -> 5.68, hedged Sharpe 0.60 -> 0.98, raw Sharpe 0.773, beta -0.14 -> -0.56, MaxDD -45.6 -> -43.2, D10 turnover 28% -> 58%.
- Every acceptance applied one version at a time; each baseline reproduced its rung's WITH arm on 66/66 fields to six places; Stage 3 per version; one annotated tag per version (v1's tag mis-pointed, logged, not moved, owner to decide).
- Character: much of the hedged gain from v7 on is hedge-carried (negative-beta legs: MaxRet, IdioVol3F, zerotrade6M; decision hedge_guard_negative_beta_property, rf correction deferred to E). Closest misses: IdioVolAHT 1.92, ShareIss1Y 1.88; thinnest passes IdioVol3F 2.03, VolumeTrend 2.04.
- Audits: STreversal residual share 1.06 reviewed clean (alpha-reviewer). Close checks: tags, families vs composite, leak sweep (process_finding leak_sweep_phase_d_close), records check OK.
- Cost: 33 runs, 7.2 h wall (ladders 2.4 h; baseline+Stage 3 pairs 18-40 min each, rising with leg count); 0 harness/config/data stamp moves. One permission denial on the v12 apply; owner authorised the coordinator to do moves and composite edits.

## 2026-10-01 — Phase E: the construction layer (D7; runs 045-049)
- 41edba9 (HARNESS 73a95d352942 -> 471f70782486; pytest 441): D7's three changes — sector + market-beta neutral optimiser (`[S | beta]'w = 0`, beta trailing 36m on D4's M), a harness-built Corwin-Schultz half-spread that reads no composite leg, regime ex_years [2000, 2001, 2021] from the D5 rule on run 042; layer pinned to v14 (7fe6f001e708). Run 045 (Stage 2, 2430 s) reproduced run 042 except harness_sha.
- alpha-reviewer on 41edba9: fix first. One major (CONSTRUCTION.md and D7 cited a sibling outcome; removed in 4ca9bd5, process_finding d7_predecessor_outcome_clause), one medium (ex-year 2000 precedes the book), lows (name-cap excess unreported, beta-drop and spread-join guards data-dependent, a vacuous CS PIT test). Run 046 (Stage 3 under 471f) aborted mid-run as superseded; partial log kept untracked.
- 5d57746 (HARNESS -> 3561590b660a; pytest 445): declared vs effective ex-years (effective 2001, 2021), name-cap excess reported, LayerRefused below 95% spread coverage or on a beta-less book month, non-vacuous CS PIT test. Runs 047 (Stage 2, 2421.7 s) and 048 (Stage 3, 2428.6 s) reproduced 042 and 043 on every field except harness_sha.
- Run 049 (`--baseline --construction-layer`, 2473.6 s, 33 blocks, in-window): stamps and layer pin verified, 0 validation warnings, every guard held. layer@$100M gross 4.08%/yr (Sharpe 0.86, t 3.27), costs 4.36 (spread 3.39), net -0.29 (Sharpe -0.06); -0.41 at $1B, -0.87 at $5B; fixed tier spreads +0.50 / +0.16 / -0.32. Ex-post beta -0.10 against ex-ante 0; risk model underpredicts about 2.4x; return front-loaded (2003-2020 net -36% compounded).
- Decided: nothing is gated; the layer is frozen as run and recorded in the manifest's v14 `construction_layer` block. Next: the advisor, then stop-and-ask 3 (snapshot refresh) and 5 (holdout).
- Cost: about 2.8 h of run wall time (045, 047, 048, 049 at 40-41 min each; 046 stopped after 7 min), 2 HARNESS_SHA moves, 0 config/composite/data moves.

## 2026-10-01 — D8 refresh and step 2 (owner approved stop-and-ask 3: "approve both, use TB3MS for rf")
- rf as a diagnostic beside the declared hedge (moving market_hedge would be stop-and-ask 2): harness 8d1895a, run 052 reproduced 042 on the old bytes.
- Refresh: DATA_SHA 198b281de1a0 -> 42587e08609a (d477021); SEP to 2026-10-01 incl. 2026-09-30; TB3MS 1934-01..2026-09.
- Step 2 (run 053): 54 fields restated, IC -9e-6, hedged Sharpe +0.014; no Stage 2 verdict can move against the thinnest margins. Excess-of-rf Sharpe 0.928 vs hedged 0.996 (rf credit 1.25 pp/yr). Holdout expectations restated on the spend snapshot before any OOS number.
- Earlier the same day: skip1 diagnostic (run 051) and the whole-model audit; stop-and-ask 5 is next.

## 2026-10-02 — The holdout spend (owner approved stop-and-ask 5: "Yes"; D8 steps 3-4; runs 054-057)
- Ran, on HARNESS 1271266472a9 / CONFIG 0d88328d5b10 / COMPOSITE 7fe6f001e708 (v14, 19 legs, 9 families) / DATA 42587e08609a: 054 `--baseline --stage 2 --include-holdout` (3004 s, the canonical read), 055 `--holdout-only` (637 s, cross-check, beta = 0 through 2022-12), 056 Stage 3 `--include-holdout` (3003 s), 057 `--construction-layer --include-holdout` (3088 s, 33 blocks). The block is now spent; nothing re-run.
- Provenance: every stamp and the layer pin (4b279fc317cd, composite pin 7fe6f001e708) match on all 40 blocks; eval_end 2026-09-30 on all; validate_results raises only the expected out-of-sample breach, plus on 055 the 120-month floor (thin sample / decile-collapse text: INCONCLUSIVE by the harness's own rule; LS present 57/57). 054's in-window cut equals run 053 on 20/20 fields to six places.
- Read against decision holdout_expectations_v14_spend_snapshot: hedged Sharpe 0.52 (expected 0.996), excess-of-rf 0.41 (0.93), raw 0.12 (0.79), IC 0.0300 at NW t 1.87 (0.0389 full / 0.0283 second half), ex-top-3 negative on both series, layer@$100M net Sharpe -0.37 (-0.06).
- What it means: the selection carried rank information into 2022 (IC +0.105, hedged +60%) and very little after (IC halves 0.057 / 0.004; 2023-26 hedged -7.9, +3.5, -16.2, +18.4). The hedged headline is mostly the hedge term (raw 3.0%/yr, hedged 10.8%/yr) and the trailing beta lagged the book's realised -0.84; the beta-neutral layer earned 0.74%/yr gross. The paper reads the composite's IC as holding its level out of sample (0.030, 77% of the full in-window mean, above the second half) but concentrated in 2022 and not significant; the hedged Sharpe as about half; any beta-neutral return as close to zero.
- Gaps reported, not repaired: 056 Stage 3 blocks carry no holdout cut (D8 step 4 asks to read them), and 054's holdout cut carries no hedged ex-top-years, bear/bull, tier or decile rows (taken from 055 and labelled).
- Records: MODEL_MANIFEST holdout {status: spent, 2026-10-02} and v14 `holdout` block; events run_completed x4, provenance_verified x4, validation_warning x4, construction_reported (056, 057), holdout_spent (new type, added to KNOWN_EVENTS and RECORDS.md, a scripts/ change); CHANGELOG. Session state left to the coordinator.
- Cost: 9,732 s (2.7 h) of run wall time (054 3004 s, 055 637 s, 056 3003 s, 057 3088 s); 0 stamp moves.

## 2026-10-02 — Holdout spend and the paper (owner: "Yes" to stop-and-ask 5)
- Runs 054-057 under D8 steps 3-4 on v14: holdout IC 0.0300 (NW t 1.87, one-sided p ~0.03) vs 0.0283 benchmark; hedged Sharpe 0.523 vs 0.996; excess-of-rf 0.413; raw 0.124; layer net Sharpe -0.367 @100M. Stage 3 holdout cuts absent (process_finding).
- Paper: paper/paper.md generated by paper/build_tables.py from the records (57 tables, 349 sourced facts, deterministic); a read-only review traced ~120 numbers (all matched) and asked for headline framing fixes (hedged OOS headline, hedge-term direction, regime cuts, holdout isolation wording), all applied.
- Search finished. Open for the owner: publication choice and GitHub link (D9); the v1 tag.
