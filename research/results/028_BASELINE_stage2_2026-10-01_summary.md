# RUN 028 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE a12e87c5fb36 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v8: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq

## BASELINE_v8  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0320  ic_tstat_nw=4.5036  icir=0.3156  ic_half1_mean=0.0460  ic_half2_mean=0.0180  ls_sharpe=0.9673  ls_ann_return_pct=15.1807  ls_ann_vol_pct=15.6937  ls_maxdd_pct=-43.3632  ls_hit_rate_pct=64.1304  turnover_d10_pct=44.0720  turnover_d1_pct=39.5197  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3893  ls_raw_sharpe=0.6127  ls_beta_mean=-0.6497  ls_beta_fullwindow=-0.7212  ls_sharpe_ex_top_years=0.6039  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9605  ls_sharpe_bull=1.1220
deciles D1..D10 avg %/mo: 0.313,0.519,0.823,0.960,0.976,1.141,1.152,1.171,1.304,1.311
hedge/regime (diagnostics): beta ex-ante -0.6497 full-window -0.7212  raw Sharpe 0.6127  Sharpe ex top years 0.6039 (2000,2001,2021)  bear/bull 0.9605/1.1220
ic decay: h1=0.0246  h2=0.0216  h3=0.0224  h6=0.0197  h12=0.0222
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0299 0.2190 0.4130 9.9300 393; MID 0.0281 0.2521 0.5890 12.7000 589; SMALL 0.0337 0.3467 0.6080 11.8400 981; ALL 0.0320 0.3156 0.6130 11.9800 1964
annual IC: 1999:+0.026 2000:+0.123 2001:+0.101 2002:+0.108 2003:-0.002 2004:+0.036 2005:+0.038 2006:+0.025 2007:-0.008 2008:+0.081 2009:-0.031 2010:+0.022 2011:+0.045 2012:+0.013 2013:+0.021 2014:+0.033 2015:+0.033 2016:+0.015 2017:-0.004 2018:+0.037 2019:-0.029 2020:-0.058 2021:+0.110
