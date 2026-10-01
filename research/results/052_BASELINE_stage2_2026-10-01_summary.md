# RUN 052 BASELINE stage 2

stamps: HARNESS 1271266472a9 CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## BASELINE_v14  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0389  ic_tstat_nw=5.6831  icir=0.3870  ic_half1_mean=0.0498  ic_half2_mean=0.0281  ls_sharpe=0.9826  ls_ann_return_pct=16.1222  ls_ann_vol_pct=16.4084  ls_maxdd_pct=-43.2143  ls_hit_rate_pct=63.7681  turnover_d10_pct=58.1350  turnover_d1_pct=54.4051  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  ls_raw_sharpe=0.7734  ls_beta_mean=-0.5437  ls_beta_fullwindow=-0.5596  ls_sharpe_ex_top_years=0.6498  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2192  ls_sharpe_bull=1.1146
deciles D1..D10 avg %/mo: 0.275,0.539,0.757,0.802,1.006,1.061,1.132,1.249,1.355,1.493
hedge/regime (diagnostics): beta ex-ante -0.5437 full-window -0.5596  raw Sharpe 0.7734  Sharpe ex top years 0.6498 (2000,2001,2021)  bear/bull 1.2192/1.1146
ic decay: h1=0.0269  h2=0.0226  h3=0.0247  h6=0.0197  h12=0.0234
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0335 0.2307 0.2840 7.3000 393; MID 0.0348 0.3193 0.6370 13.1600 589; SMALL 0.0412 0.4404 0.9050 16.2100 981; ALL 0.0389 0.3870 0.7730 14.6200 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.000 2004:+0.042 2005:+0.027 2006:+0.040 2007:-0.016 2008:+0.081 2009:+0.003 2010:+0.032 2011:+0.058 2012:+0.019 2013:+0.019 2014:+0.040 2015:+0.040 2016:+0.031 2017:+0.001 2018:+0.039 2019:+0.009 2020:-0.049 2021:+0.114
