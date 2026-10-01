# RUN 030 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE c961f5791816 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v9: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE

## BASELINE_v9  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0323  ic_tstat_nw=4.5007  icir=0.3146  ic_half1_mean=0.0462  ic_half2_mean=0.0183  ls_sharpe=0.9316  ls_ann_return_pct=14.8709  ls_ann_vol_pct=15.9633  ls_maxdd_pct=-43.6667  ls_hit_rate_pct=62.3188  turnover_d10_pct=44.3025  turnover_d1_pct=39.5813  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3893  ls_raw_sharpe=0.5790  ls_beta_mean=-0.6626  ls_beta_fullwindow=-0.7338  ls_sharpe_ex_top_years=0.5814  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9337  ls_sharpe_bull=1.0696
deciles D1..D10 avg %/mo: 0.344,0.482,0.825,0.983,0.976,1.130,1.153,1.190,1.282,1.304
hedge/regime (diagnostics): beta ex-ante -0.6626 full-window -0.7338  raw Sharpe 0.5790  Sharpe ex top years 0.5814 (2000,2001,2021)  bear/bull 0.9337/1.0696
ic decay: h1=0.0246  h2=0.0216  h3=0.0224  h6=0.0199  h12=0.0225
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0303 0.2202 0.3980 9.6600 393; MID 0.0284 0.2521 0.5610 12.2200 589; SMALL 0.0337 0.3436 0.5660 11.1900 981; ALL 0.0323 0.3146 0.5790 11.5300 1964
annual IC: 1999:+0.026 2000:+0.124 2001:+0.102 2002:+0.109 2003:-0.002 2004:+0.037 2005:+0.037 2006:+0.026 2007:-0.007 2008:+0.081 2009:-0.033 2010:+0.022 2011:+0.046 2012:+0.013 2013:+0.021 2014:+0.034 2015:+0.034 2016:+0.016 2017:-0.003 2018:+0.037 2019:-0.028 2020:-0.058 2021:+0.110
