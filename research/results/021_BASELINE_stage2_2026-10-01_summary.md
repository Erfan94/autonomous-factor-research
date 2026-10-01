# RUN 021 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE d27916e567f2 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v5: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN

## BASELINE_v5  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0245  ic_tstat_nw=4.2703  icir=0.3091  ic_half1_mean=0.0380  ic_half2_mean=0.0110  ls_sharpe=0.9141  ls_ann_return_pct=11.5584  ls_ann_vol_pct=12.6443  ls_maxdd_pct=-47.7533  ls_hit_rate_pct=64.4928  turnover_d10_pct=25.0179  turnover_d1_pct=22.3389  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5459  ls_raw_sharpe=0.8082  ls_beta_mean=-0.2975  ls_beta_fullwindow=-0.3445  ls_sharpe_ex_top_years=0.4789  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1271  ls_sharpe_bull=0.8731
deciles D1..D10 avg %/mo: 0.330,0.664,0.692,0.843,1.050,1.107,1.166,1.226,1.305,1.287
hedge/regime (diagnostics): beta ex-ante -0.2975 full-window -0.3445  raw Sharpe 0.8082  Sharpe ex top years 0.4789 (2000,2001,2021)  bear/bull 1.1271/0.8731
ic decay: h1=0.0183  h2=0.0170  h3=0.0185  h6=0.0162  h12=0.0178
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2360 0.3480 7.1900 393; MID 0.0228 0.2560 0.8420 14.4200 589; SMALL 0.0239 0.3191 0.7630 9.9500 981; ALL 0.0245 0.3091 0.8080 11.4900 1964
annual IC: 1999:+0.024 2000:+0.088 2001:+0.084 2002:+0.090 2003:+0.012 2004:+0.035 2005:+0.042 2006:+0.012 2007:-0.019 2008:+0.064 2009:-0.018 2010:+0.027 2011:+0.023 2012:+0.012 2013:+0.028 2014:+0.023 2015:+0.012 2016:+0.024 2017:-0.012 2018:+0.012 2019:-0.033 2020:-0.050 2021:+0.085
