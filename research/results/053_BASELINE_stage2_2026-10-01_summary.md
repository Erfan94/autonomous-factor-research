# RUN 053 BASELINE stage 2

stamps: HARNESS 1271266472a9 CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 42587e08609a
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## BASELINE_v14  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0389  ic_tstat_nw=5.6812  icir=0.3870  ic_half1_mean=0.0496  ic_half2_mean=0.0283  ls_sharpe=0.9964  ls_ann_return_pct=16.3444  ls_ann_vol_pct=16.4029  ls_maxdd_pct=-43.2337  ls_hit_rate_pct=62.6812  turnover_d10_pct=58.0934  turnover_d1_pct=54.4537  coverage_pct=100.0  avg_names_per_decile=195.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4372  leg_coverage_pct_full=45.4155  ls_raw_sharpe=0.7902  ls_beta_mean=-0.5398  ls_beta_fullwindow=-0.5560  ls_sharpe_ex_top_years=0.6665  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2566  ls_sharpe_bull=1.1151  ls_excess_sharpe=0.9285  ls_excess_ann_return_pct=15.0907  ls_excess_maxdd_pct=-43.3352  ls_excess_tstat_nw=3.7491  ls_excess_sharpe_ex_top_years=0.6045  ls_excess_top_years=2000,2001,2021  ls_rf_credit_pp=-1.2537
deciles D1..D10 avg %/mo: 0.261,0.562,0.761,0.782,1.022,1.067,1.114,1.259,1.350,1.504
hedge/regime (diagnostics): beta ex-ante -0.5398 full-window -0.5560  raw Sharpe 0.7902  Sharpe ex top years 0.6665 (2000,2001,2021)  bear/bull 1.2566/1.1151
ic decay: h1=0.0269  h2=0.0226  h3=0.0247  h6=0.0197  h12=0.0235
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0335 0.2305 0.2750 7.1100 392; MID 0.0347 0.3193 0.6290 12.9500 587; SMALL 0.0412 0.4403 0.9220 16.4400 978; ALL 0.0389 0.3870 0.7900 14.9100 1958
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.000 2004:+0.041 2005:+0.026 2006:+0.040 2007:-0.016 2008:+0.081 2009:+0.003 2010:+0.032 2011:+0.059 2012:+0.019 2013:+0.019 2014:+0.041 2015:+0.040 2016:+0.030 2017:+0.001 2018:+0.039 2019:+0.009 2020:-0.049 2021:+0.114
