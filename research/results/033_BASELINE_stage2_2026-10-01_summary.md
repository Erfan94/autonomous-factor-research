# RUN 033 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 1b4195ff18b4 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v10: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F

## BASELINE_v10  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0326  ic_tstat_nw=4.4757  icir=0.3120  ic_half1_mean=0.0457  ic_half2_mean=0.0195  ls_sharpe=0.9193  ls_ann_return_pct=15.2529  ls_ann_vol_pct=16.5916  ls_maxdd_pct=-45.7772  ls_hit_rate_pct=63.4058  turnover_d10_pct=39.7994  turnover_d1_pct=35.3912  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3884  ls_raw_sharpe=0.5785  ls_beta_mean=-0.6803  ls_beta_fullwindow=-0.7519  ls_sharpe_ex_top_years=0.5749  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8423  ls_sharpe_bull=1.0930
deciles D1..D10 avg %/mo: 0.272,0.560,0.813,0.936,1.037,1.125,1.130,1.233,1.296,1.267
hedge/regime (diagnostics): beta ex-ante -0.6803 full-window -0.7519  raw Sharpe 0.5785  Sharpe ex top years 0.5749 (2000,2001,2021)  bear/bull 0.8423/1.0930
ic decay: h1=0.0251  h2=0.0225  h3=0.0235  h6=0.0206  h12=0.0228
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0305 0.2220 0.3890 9.5500 393; MID 0.0292 0.2569 0.5400 12.0100 589; SMALL 0.0338 0.3352 0.5310 10.9200 981; ALL 0.0326 0.3120 0.5780 11.9400 1964
annual IC: 1999:+0.026 2000:+0.127 2001:+0.098 2002:+0.106 2003:-0.004 2004:+0.035 2005:+0.037 2006:+0.025 2007:-0.004 2008:+0.083 2009:-0.035 2010:+0.021 2011:+0.051 2012:+0.012 2013:+0.023 2014:+0.033 2015:+0.037 2016:+0.017 2017:-0.003 2018:+0.039 2019:-0.029 2020:-0.060 2021:+0.114
