# RUN 038 BASELINE stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 612e59349f40 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v12: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M

## BASELINE_v12  (stage baseline)  → **MEASURED**
stats: ic_mean=0.0373  ic_tstat_nw=5.1535  icir=0.3550  ic_half1_mean=0.0467  ic_half2_mean=0.0279  ls_sharpe=0.9846  ls_ann_return_pct=16.1589  ls_ann_vol_pct=16.4119  ls_maxdd_pct=-41.1079  ls_hit_rate_pct=64.8551  turnover_d10_pct=56.7968  turnover_d1_pct=52.6024  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  ls_raw_sharpe=0.7084  ls_beta_mean=-0.5991  ls_beta_fullwindow=-0.6348  ls_sharpe_ex_top_years=0.6455  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9250  ls_sharpe_bull=1.2290
deciles D1..D10 avg %/mo: 0.312,0.629,0.753,0.829,1.000,1.049,1.138,1.188,1.320,1.451
hedge/regime (diagnostics): beta ex-ante -0.5991 full-window -0.6348  raw Sharpe 0.7084  Sharpe ex top years 0.6455 (2000,2001,2021)  bear/bull 0.9250/1.2290
ic decay: h1=0.0265  h2=0.0215  h3=0.0238  h6=0.0210  h12=0.0249
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0318 0.2077 0.2560 6.6000 393; MID 0.0332 0.2900 0.6020 12.5600 589; SMALL 0.0396 0.4036 0.7800 14.8200 981; ALL 0.0373 0.3550 0.7080 13.6700 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.010 2004:+0.040 2005:+0.027 2006:+0.039 2007:-0.011 2008:+0.086 2009:-0.029 2010:+0.025 2011:+0.058 2012:+0.019 2013:+0.022 2014:+0.044 2015:+0.051 2016:+0.018 2017:+0.008 2018:+0.047 2019:-0.000 2020:-0.054 2021:+0.111
