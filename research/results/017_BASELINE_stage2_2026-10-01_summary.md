# RUN 017 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 73ee92fe0723 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v3: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y

## BASELINE_v3  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0215  ic_tstat_nw=3.9766  icir=0.2843  ic_half1_mean=0.0336  ic_half2_mean=0.0095  ls_sharpe=0.8479  ls_ann_return_pct=10.2876  ls_ann_vol_pct=12.1324  ls_maxdd_pct=-41.9210  ls_hit_rate_pct=59.4203  turnover_d10_pct=26.3407  turnover_d1_pct=22.9657  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5778  ls_raw_sharpe=0.8738  ls_beta_mean=-0.1575  ls_beta_fullwindow=-0.1917  ls_sharpe_ex_top_years=0.4646  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0370  ls_sharpe_bull=0.8064
deciles D1..D10 avg %/mo: 0.444,0.553,0.775,0.850,0.955,1.046,1.174,1.199,1.314,1.359
hedge/regime (diagnostics): beta ex-ante -0.1575 full-window -0.1917  raw Sharpe 0.8738  Sharpe ex top years 0.4646 (2000,2001,2021)  bear/bull 1.0370/0.8064
ic decay: h1=0.0155  h2=0.0141  h3=0.0159  h6=0.0141  h12=0.0153
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0229 0.2289 0.4360 8.5500 393; MID 0.0204 0.2436 0.8490 13.3100 589; SMALL 0.0216 0.3171 0.8870 10.1200 981; ALL 0.0215 0.2843 0.8740 10.9900 1964
annual IC: 1999:+0.022 2000:+0.065 2001:+0.092 2002:+0.076 2003:+0.020 2004:+0.036 2005:+0.037 2006:+0.008 2007:-0.037 2008:+0.063 2009:-0.020 2010:+0.033 2011:+0.020 2012:+0.015 2013:+0.027 2014:+0.014 2015:+0.012 2016:+0.024 2017:-0.011 2018:+0.010 2019:-0.031 2020:-0.044 2021:+0.065
