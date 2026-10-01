# RUN 013 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE cbeb16455bf4 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v1: Size, Value, Profitability, Investment, Momentum, PctAcc

## BASELINE_v1  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0169  ic_tstat_nw=3.0165  icir=0.2085  ic_half1_mean=0.0304  ic_half2_mean=0.0033  ls_sharpe=0.6139  ls_ann_return_pct=7.3826  ls_ann_vol_pct=12.0247  ls_maxdd_pct=-41.2812  ls_hit_rate_pct=56.5217  turnover_d10_pct=27.6281  turnover_d1_pct=24.0838  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=91.3598  ls_raw_sharpe=0.7371  ls_beta_mean=-0.0742  ls_beta_fullwindow=-0.1210  ls_sharpe_ex_top_years=0.2017  ls_top_years=2000,2001,2003  ls_sharpe_bear=0.8526  ls_sharpe_bull=0.5544
deciles D1..D10 avg %/mo: 0.488,0.677,0.740,0.919,0.993,0.992,1.044,1.178,1.382,1.256
hedge/regime (diagnostics): beta ex-ante -0.0742 full-window -0.1210  raw Sharpe 0.7371  Sharpe ex top years 0.2017 (2000,2001,2003)  bear/bull 0.8526/0.5544
ic decay: h1=0.0113  h2=0.0097  h3=0.0116  h6=0.0097  h12=0.0120
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0159 0.1557 0.2760 5.6600 393; MID 0.0147 0.1671 0.7350 11.7900 589; SMALL 0.0193 0.2748 0.7060 8.1000 981; ALL 0.0169 0.2085 0.7370 9.2200 1964
annual IC: 1999:+0.015 2000:+0.064 2001:+0.091 2002:+0.075 2003:+0.021 2004:+0.035 2005:+0.038 2006:+0.004 2007:-0.036 2008:+0.047 2009:-0.021 2010:+0.029 2011:+0.000 2012:+0.018 2013:+0.032 2014:+0.004 2015:+0.001 2016:+0.029 2017:-0.024 2018:-0.016 2019:-0.027 2020:-0.041 2021:+0.049
