# RUN 040 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE fa17bd1cd37e DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v13: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend

## BASELINE_v13  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0372  ic_tstat_nw=5.2391  icir=0.3624  ic_half1_mean=0.0467  ic_half2_mean=0.0277  ls_sharpe=0.9786  ls_ann_return_pct=16.1259  ls_ann_vol_pct=16.4788  ls_maxdd_pct=-41.6031  ls_hit_rate_pct=64.4928  turnover_d10_pct=56.5533  turnover_d1_pct=53.1515  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  ls_raw_sharpe=0.7188  ls_beta_mean=-0.5891  ls_beta_fullwindow=-0.6194  ls_sharpe_ex_top_years=0.6349  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9616  ls_sharpe_bull=1.2044
deciles D1..D10 avg %/mo: 0.268,0.621,0.779,0.846,1.000,1.088,1.117,1.190,1.338,1.422
hedge/regime (diagnostics): beta ex-ante -0.5891 full-window -0.6194  raw Sharpe 0.7188  Sharpe ex top years 0.6349 (2000,2001,2021)  bear/bull 0.9616/1.2044
ic decay: h1=0.0263  h2=0.0214  h3=0.0236  h6=0.0209  h12=0.0250
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0323 0.2212 0.2510 6.4500 393; MID 0.0336 0.3013 0.6110 12.8000 589; SMALL 0.0388 0.4049 0.7870 14.6800 981; ALL 0.0372 0.3624 0.7190 13.8500 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.009 2004:+0.039 2005:+0.031 2006:+0.038 2007:-0.015 2008:+0.082 2009:-0.025 2010:+0.029 2011:+0.056 2012:+0.021 2013:+0.021 2014:+0.045 2015:+0.046 2016:+0.020 2017:+0.009 2018:+0.040 2019:+0.001 2020:-0.053 2021:+0.113
