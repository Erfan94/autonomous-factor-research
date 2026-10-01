# RUN 051 BASELINE_SKIP1 stage 2

stamps: HARNESS aef490297071 CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## BASELINE_v14  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0345  ic_tstat_nw=5.1597  icir=0.3437  ic_half1_mean=0.0421  ic_half2_mean=0.0270  ls_sharpe=0.7767  ls_ann_return_pct=12.2624  ls_ann_vol_pct=15.7882  ls_maxdd_pct=-44.0830  ls_hit_rate_pct=60.1449  turnover_d10_pct=58.1350  turnover_d1_pct=54.4051  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  ls_raw_sharpe=0.6548  ls_beta_mean=-0.5547  ls_beta_fullwindow=-0.5261  ls_sharpe_ex_top_years=0.4759  ls_top_years=2000,2002,2021  ls_sharpe_bear=1.3166  ls_sharpe_bull=0.8206
deciles D1..D10 avg %/mo: 0.296,0.521,0.676,0.728,0.917,0.943,1.004,1.101,1.215,1.314
hedge/regime (diagnostics): beta ex-ante -0.5547 full-window -0.5261  raw Sharpe 0.6548  Sharpe ex top years 0.4759 (2000,2002,2021)  bear/bull 1.3166/0.8206
ic decay: h1=0.0255  h2=0.0200  h3=0.0223  h6=0.0173  h12=0.0215
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0304 0.2088 0.2220 5.5400 393; MID 0.0317 0.2895 0.5350 10.9800 589; SMALL 0.0349 0.3778 0.7130 12.3400 981; ALL 0.0345 0.3437 0.6550 12.2100 1964
annual IC: 1999:+0.001 2000:+0.124 2001:+0.088 2002:+0.100 2003:-0.009 2004:+0.039 2005:+0.022 2006:+0.029 2007:-0.024 2008:+0.079 2009:-0.002 2010:+0.042 2011:+0.052 2012:+0.016 2013:+0.024 2014:+0.037 2015:+0.036 2016:+0.037 2017:-0.001 2018:+0.047 2019:+0.000 2020:-0.044 2021:+0.101
