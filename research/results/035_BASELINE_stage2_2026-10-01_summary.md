# RUN 035 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 335b06e3d608 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v11: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal

## BASELINE_v11  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0355  ic_tstat_nw=5.3630  icir=0.3806  ic_half1_mean=0.0475  ic_half2_mean=0.0236  ls_sharpe=0.9423  ls_ann_return_pct=14.6139  ls_ann_vol_pct=15.5088  ls_maxdd_pct=-39.5291  ls_hit_rate_pct=59.4203  turnover_d10_pct=59.0772  turnover_d1_pct=59.3116  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3884  ls_raw_sharpe=0.7372  ls_beta_mean=-0.4800  ls_beta_fullwindow=-0.5122  ls_sharpe_ex_top_years=0.5653  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0847  ls_sharpe_bull=1.0636
deciles D1..D10 avg %/mo: 0.312,0.562,0.741,0.861,0.933,1.040,1.178,1.255,1.390,1.398
hedge/regime (diagnostics): beta ex-ante -0.4800 full-window -0.5122  raw Sharpe 0.7372  Sharpe ex top years 0.5653 (2000,2001,2021)  bear/bull 1.0847/1.0636
ic decay: h1=0.0235  h2=0.0180  h3=0.0209  h6=0.0181  h12=0.0232
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0322 0.2581 0.4270 9.3700 393; MID 0.0304 0.3005 0.5920 11.5200 589; SMALL 0.0379 0.4182 0.7820 13.8000 981; ALL 0.0355 0.3806 0.7370 13.0300 1964
annual IC: 1999:+0.029 2000:+0.117 2001:+0.112 2002:+0.116 2003:+0.000 2004:+0.045 2005:+0.034 2006:+0.033 2007:-0.023 2008:+0.075 2009:-0.021 2010:+0.030 2011:+0.039 2012:+0.024 2013:+0.024 2014:+0.037 2015:+0.035 2016:+0.022 2017:-0.001 2018:+0.033 2019:-0.001 2020:-0.047 2021:+0.105
