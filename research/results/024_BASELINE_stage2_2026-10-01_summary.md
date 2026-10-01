# RUN 024 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 21a6688ae5d1 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v6: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP

## BASELINE_v6  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0242  ic_tstat_nw=4.2330  icir=0.3058  ic_half1_mean=0.0377  ic_half2_mean=0.0107  ls_sharpe=0.9255  ls_ann_return_pct=11.7157  ls_ann_vol_pct=12.6589  ls_maxdd_pct=-49.4236  ls_hit_rate_pct=61.9565  turnover_d10_pct=25.2323  turnover_d1_pct=22.2917  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=46.5243  ls_raw_sharpe=0.8434  ls_beta_mean=-0.2766  ls_beta_fullwindow=-0.3225  ls_sharpe_ex_top_years=0.4897  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2686  ls_sharpe_bull=0.8422
deciles D1..D10 avg %/mo: 0.301,0.690,0.661,0.861,1.046,1.143,1.151,1.280,1.248,1.288
hedge/regime (diagnostics): beta ex-ante -0.2766 full-window -0.3225  raw Sharpe 0.8434  Sharpe ex top years 0.4897 (2000,2001,2021)  bear/bull 1.2686/0.8422
ic decay: h1=0.0181  h2=0.0169  h3=0.0184  h6=0.0162  h12=0.0177
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2375 0.3560 7.3200 393; MID 0.0221 0.2498 0.8560 14.4600 589; SMALL 0.0239 0.3198 0.8130 10.3300 981; ALL 0.0242 0.3058 0.8430 11.8500 1964
annual IC: 1999:+0.023 2000:+0.085 2001:+0.085 2002:+0.089 2003:+0.013 2004:+0.034 2005:+0.042 2006:+0.013 2007:-0.023 2008:+0.065 2009:-0.017 2010:+0.029 2011:+0.024 2012:+0.012 2013:+0.027 2014:+0.020 2015:+0.012 2016:+0.022 2017:-0.013 2018:+0.015 2019:-0.035 2020:-0.049 2021:+0.083
