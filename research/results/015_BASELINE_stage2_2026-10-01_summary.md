# RUN 015 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 8b444636f0a1 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v2: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf

## BASELINE_v2  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0169  ic_tstat_nw=3.0237  icir=0.2099  ic_half1_mean=0.0312  ic_half2_mean=0.0025  ls_sharpe=0.6606  ls_ann_return_pct=7.8213  ls_ann_vol_pct=11.8406  ls_maxdd_pct=-37.0655  ls_hit_rate_pct=55.7971  turnover_d10_pct=27.9507  turnover_d1_pct=24.4075  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=72.7197  ls_raw_sharpe=0.7770  ls_beta_mean=-0.0631  ls_beta_fullwindow=-0.1220  ls_sharpe_ex_top_years=0.2490  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9231  ls_sharpe_bull=0.5730
deciles D1..D10 avg %/mo: 0.470,0.624,0.767,0.890,0.941,1.040,1.049,1.212,1.414,1.264
hedge/regime (diagnostics): beta ex-ante -0.0631 full-window -0.1220  raw Sharpe 0.7770  Sharpe ex top years 0.2490 (2000,2001,2021)  bear/bull 0.9231/0.5730
ic decay: h1=0.0110  h2=0.0095  h3=0.0113  h6=0.0093  h12=0.0116
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0162 0.1660 0.3490 6.7500 393; MID 0.0144 0.1641 0.7430 11.4800 589; SMALL 0.0194 0.2781 0.7810 8.7100 981; ALL 0.0169 0.2099 0.7770 9.5300 1964
annual IC: 1999:+0.022 2000:+0.065 2001:+0.092 2002:+0.076 2003:+0.022 2004:+0.035 2005:+0.038 2006:+0.003 2007:-0.040 2008:+0.050 2009:-0.020 2010:+0.031 2011:-0.000 2012:+0.014 2013:+0.027 2014:+0.002 2015:+0.000 2016:+0.028 2017:-0.024 2018:-0.009 2019:-0.032 2020:-0.039 2021:+0.048
