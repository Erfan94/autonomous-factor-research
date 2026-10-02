# RUN 055 BASELINE stage 2

stamps: HARNESS 1271266472a9 CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 42587e08609a
window: 2022-01-01 .. 2026-09-30  holdout_included: True
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## BASELINE_v14  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0300  ic_tstat_nw=1.8743  icir=0.2394  ic_half1_mean=0.0567  ic_half2_mean=0.0043  ls_sharpe=0.5844  ls_ann_return_pct=12.2013  ls_ann_vol_pct=20.8779  ls_maxdd_pct=-35.5187  ls_hit_rate_pct=61.4035  turnover_d10_pct=54.3382  turnover_d1_pct=44.9509  coverage_pct=100.0  avg_names_per_decile=192.8  n_months=57  ls_n_months=57  delisting_adjusted_pct=0.3686  leg_coverage_pct_full=57.1309  ls_raw_sharpe=0.1239  ls_beta_mean=-0.5044  ls_beta_fullwindow=-0.8358  ls_sharpe_ex_top_years=-0.5717  ls_top_years=2022,2024,2026  ls_sharpe_bear=NA  ls_sharpe_bull=0.0635  cut_inwindow_n_months=0  cut_inwindow_ic_mean=NA  cut_inwindow_ic_tstat_nw=NA  cut_inwindow_ls_sharpe=NA  cut_inwindow_ls_ann_return_pct=NA  cut_inwindow_ls_maxdd_pct=NA  cut_inwindow_ls_raw_sharpe=NA  cut_inwindow_ls_beta_mean=NA  cut_holdout_n_months=57  cut_holdout_ic_mean=0.0300  cut_holdout_ic_tstat_nw=1.8743  cut_holdout_ls_sharpe=0.5844  cut_holdout_ls_ann_return_pct=12.2013  cut_holdout_ls_maxdd_pct=-35.5187  cut_holdout_ls_raw_sharpe=0.1239  cut_holdout_ls_beta_mean=-0.5044  ls_excess_sharpe=0.4771  ls_excess_ann_return_pct=9.9895  ls_excess_maxdd_pct=-37.3336  ls_excess_tstat_nw=1.0539  ls_excess_sharpe_ex_top_years=-0.7034  ls_excess_top_years=2022,2024,2026  ls_rf_credit_pp=-2.2118
deciles D1..D10 avg %/mo: 0.406,0.632,0.712,0.669,0.630,0.686,0.629,0.649,0.695,0.657
hedge/regime (diagnostics): beta ex-ante -0.5044 full-window -0.8358  raw Sharpe 0.1239  Sharpe ex top years -0.5717 (2022,2024,2026)  bear/bull NA/0.0635
cut_inwindow: n_months=0  ic_mean=NA  ic_tstat_nw=NA  ls_sharpe=NA  ls_ann_return_pct=NA  ls_maxdd_pct=NA  ls_raw_sharpe=NA  ls_beta_mean=NA
cut_inwindow excess: ls_excess_sharpe=NA  ls_excess_ann_return_pct=NA  ls_excess_maxdd_pct=NA  ls_excess_tstat_nw=NA  ls_excess_sharpe_ex_top_years=NA  ls_excess_top_years=  ls_rf_credit_pp=NA
cut_holdout: n_months=57  ic_mean=0.0300  ic_tstat_nw=1.8743  ls_sharpe=0.5844  ls_ann_return_pct=12.2013  ls_maxdd_pct=-35.5187  ls_raw_sharpe=0.1239  ls_beta_mean=-0.5044
cut_holdout excess: ls_excess_sharpe=0.4771  ls_excess_ann_return_pct=9.9895  ls_excess_maxdd_pct=-37.3336  ls_excess_tstat_nw=1.0539  ls_excess_sharpe_ex_top_years=-0.7034  ls_excess_top_years=2022,2024,2026  ls_rf_credit_pp=-2.2118
ic decay: h1=0.0288  h2=0.0317  h3=0.0235  h6=0.0067  h12=0.0087
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0202 0.0967 -0.1310 -5.2000 386; MID 0.0404 0.2893 0.1260 3.4300 578; SMALL 0.0331 0.2968 0.2090 4.0700 963; ALL 0.0300 0.2394 0.1240 3.0100 1927
annual IC: 2022:+0.105 2023:-0.002 2024:+0.031 2025:-0.021 2026:+0.040
