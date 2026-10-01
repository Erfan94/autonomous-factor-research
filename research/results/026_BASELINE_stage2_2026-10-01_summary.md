# RUN 026 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 43c92213ae73 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v7: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet

## BASELINE_v7  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0305  ic_tstat_nw=4.4930  icir=0.3160  ic_half1_mean=0.0444  ic_half2_mean=0.0166  ls_sharpe=0.9512  ls_ann_return_pct=13.9480  ls_ann_vol_pct=14.6632  ls_maxdd_pct=-41.6776  ls_hit_rate_pct=62.3188  turnover_d10_pct=43.4076  turnover_d1_pct=39.4165  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=46.5243  ls_raw_sharpe=0.6220  ls_beta_mean=-0.5866  ls_beta_fullwindow=-0.6493  ls_sharpe_ex_top_years=0.6234  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9739  ls_sharpe_bull=1.0454
deciles D1..D10 avg %/mo: 0.332,0.487,0.806,0.995,0.994,1.158,1.151,1.146,1.330,1.270
hedge/regime (diagnostics): beta ex-ante -0.5866 full-window -0.6493  raw Sharpe 0.6220  Sharpe ex top years 0.6234 (2000,2001,2021)  bear/bull 0.9739/1.0454
ic decay: h1=0.0232  h2=0.0203  h3=0.0212  h6=0.0194  h12=0.0219
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0296 0.2199 0.4150 10.1100 393; MID 0.0278 0.2580 0.6250 12.5000 589; SMALL 0.0311 0.3431 0.6530 11.4900 981; ALL 0.0305 0.3160 0.6220 11.2600 1964
annual IC: 1999:+0.027 2000:+0.112 2001:+0.097 2002:+0.104 2003:+0.001 2004:+0.035 2005:+0.038 2006:+0.023 2007:-0.011 2008:+0.080 2009:-0.026 2010:+0.025 2011:+0.040 2012:+0.011 2013:+0.023 2014:+0.033 2015:+0.030 2016:+0.016 2017:-0.005 2018:+0.033 2019:-0.028 2020:-0.058 2021:+0.104
