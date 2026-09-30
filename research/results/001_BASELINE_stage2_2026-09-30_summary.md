# RUN 001 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## BASELINE_v0  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0145  ic_tstat_nw=2.6226  icir=0.1821  ic_half1_mean=0.0275  ic_half2_mean=0.0016  ls_sharpe=0.5999  ls_ann_return_pct=7.3218  ls_ann_vol_pct=12.2043  ls_maxdd_pct=-45.5599  ls_hit_rate_pct=55.0725  turnover_d10_pct=28.0020  turnover_d1_pct=23.6973  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=91.6333  ls_raw_sharpe=0.7191  ls_beta_mean=-0.0846  ls_beta_fullwindow=-0.1399  ls_sharpe_ex_top_years=0.1590  ls_top_years=2000,2001,2003  ls_sharpe_bear=1.0745  ls_sharpe_bull=0.4561
deciles D1..D10 avg %/mo: 0.483,0.739,0.771,0.874,0.886,1.070,1.124,1.215,1.256,1.252
hedge/regime (diagnostics): beta ex-ante -0.0846 full-window -0.1399  raw Sharpe 0.7191  Sharpe ex top years 0.1590 (2000,2001,2003)  bear/bull 1.0745/0.4561
ic decay: h1=0.0096  h2=0.0085  h3=0.0103  h6=0.0096  h12=0.0115
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0154 0.1388 0.3190 6.5100 393; MID 0.0118 0.1344 0.6330 10.2300 589; SMALL 0.0155 0.2304 0.7550 8.6200 981; ALL 0.0145 0.1821 0.7190 9.2300 1964
annual IC: 1999:+0.011 2000:+0.062 2001:+0.091 2002:+0.066 2003:+0.019 2004:+0.029 2005:+0.028 2006:+0.009 2007:-0.044 2008:+0.048 2009:-0.018 2010:+0.026 2011:-0.001 2012:+0.020 2013:+0.025 2014:+0.003 2015:+0.001 2016:+0.029 2017:-0.029 2018:-0.015 2019:-0.024 2020:-0.047 2021:+0.047
