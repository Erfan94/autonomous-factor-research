# RUN 019 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 3329679c69fb DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v4: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp

## BASELINE_v4  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0249  ic_tstat_nw=4.5109  icir=0.3273  ic_half1_mean=0.0375  ic_half2_mean=0.0124  ls_sharpe=0.9960  ls_ann_return_pct=12.0191  ls_ann_vol_pct=12.0674  ls_maxdd_pct=-40.6324  ls_hit_rate_pct=62.6812  turnover_d10_pct=25.1677  turnover_d1_pct=22.3010  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5701  ls_raw_sharpe=0.9134  ls_beta_mean=-0.2295  ls_beta_fullwindow=-0.2627  ls_sharpe_ex_top_years=0.6135  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2300  ls_sharpe_bull=0.9550
deciles D1..D10 avg %/mo: 0.354,0.615,0.704,0.854,0.979,1.126,1.122,1.250,1.319,1.346
hedge/regime (diagnostics): beta ex-ante -0.2295 full-window -0.2627  raw Sharpe 0.9134  Sharpe ex top years 0.6135 (2000,2001,2021)  bear/bull 1.2300/0.9550
ic decay: h1=0.0183  h2=0.0169  h3=0.0185  h6=0.0160  h12=0.0175
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2567 0.4900 9.6500 393; MID 0.0236 0.2756 0.8000 12.9900 589; SMALL 0.0248 0.3458 0.9310 11.1500 981; ALL 0.0249 0.3273 0.9130 11.9000 1964
annual IC: 1999:+0.025 2000:+0.079 2001:+0.088 2002:+0.090 2003:+0.015 2004:+0.038 2005:+0.041 2006:+0.009 2007:-0.023 2008:+0.063 2009:-0.017 2010:+0.027 2011:+0.026 2012:+0.013 2013:+0.032 2014:+0.024 2015:+0.013 2016:+0.023 2017:-0.007 2018:+0.013 2019:-0.033 2020:-0.046 2021:+0.079
