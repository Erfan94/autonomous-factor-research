# RUN 039 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 612e59349f40 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v12: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9846  ls_ann_return_pct=16.1589  ls_ann_vol_pct=16.4119  ls_maxdd_pct=-41.1079  ls_hit_rate_pct=64.8551  n_months=276  worst_12m_pct=-38.9362  turnover_long_pct=56.7968  turnover_short_pct=52.6024  construction_weights=family blend  ls_raw_sharpe=0.7084  ls_beta_mean=-0.5991  ls_beta_fullwindow=-0.6348  ls_sharpe_ex_top_years=0.6455  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9250  ls_sharpe_bull=1.2290
hedge/regime (diagnostics): beta ex-ante -0.5991 full-window -0.6348  raw Sharpe 0.7084  Sharpe ex top years 0.6455 (2000,2001,2021)  bear/bull 0.9250/1.2290
annual LS %: 1999:-24.4,2000:120.0,2001:65.1,2002:43.1,2003:30.4,2004:27.8,2005:15.4,2006:24.9,2007:-0.6,2008:8.7,2009:-20.3,2010:15.8,2011:21.9,2012:7.3,2013:7.8,2014:8.3,2015:26.1,2016:16.2,2017:7.8,2018:11.6,2019:7.4,2020:-38.6,2021:78.9

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8534  ls_ann_return_pct=14.5511  ls_ann_vol_pct=17.0509  ls_maxdd_pct=-43.8147  ls_hit_rate_pct=65.9420  n_months=276  worst_12m_pct=-41.3763  turnover_long_pct=58.3514  turnover_short_pct=54.4147  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5592  ls_beta_mean=-0.6536  ls_beta_fullwindow=-0.7078  ls_sharpe_ex_top_years=0.5336  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7165  ls_sharpe_bull=1.1259
hedge/regime (diagnostics): beta ex-ante -0.6536 full-window -0.7078  raw Sharpe 0.5592  Sharpe ex top years 0.5336 (2000,2001,2021)  bear/bull 0.7165/1.1259
annual LS %: 1999:-29.9,2000:118.1,2001:46.5,2002:30.8,2003:21.8,2004:21.2,2005:14.0,2006:27.2,2007:-1.5,2008:2.7,2009:-14.6,2010:14.6,2011:25.7,2012:13.7,2013:8.4,2014:8.9,2015:23.6,2016:10.4,2017:12.4,2018:9.5,2019:5.9,2020:-40.4,2021:82.3

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7898  ls_ann_return_pct=13.5101  ls_ann_vol_pct=17.1059  ls_maxdd_pct=-35.5917  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-32.5632  turnover_long_pct=37.1596  turnover_short_pct=35.6667  construction_weights=Size=0.010;Value=0.029;Profitability=0.071;Investment=0.027;Momentum=0.042;PctAcc=0.080;CBOperProf=0.070;ShareIss5Y=0.078;cfp=0.080;XFIN=0.067;GP=0.069;MaxRet=0.062;roaq=0.067;RoE=0.060;IdioVol3F=0.062;STreversal=0.061;zerotrade6M=0.064  ls_raw_sharpe=0.3552  ls_beta_mean=-0.8327  ls_beta_fullwindow=-0.9528  ls_sharpe_ex_top_years=0.5281  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.4961  ls_sharpe_bull=1.1683
hedge/regime (diagnostics): beta ex-ante -0.8327 full-window -0.9528  raw Sharpe 0.3552  Sharpe ex top years 0.5281 (2000,2003,2021)  bear/bull 0.4961/1.1683
annual LS %: 1999:-27.5,2000:84.3,2001:19.7,2002:21.5,2003:30.9,2004:30.6,2005:17.2,2006:17.1,2007:12.5,2008:5.4,2009:-23.2,2010:17.9,2011:14.6,2012:4.2,2013:13.7,2014:9.5,2015:13.2,2016:3.8,2017:12.4,2018:12.8,2019:12.0,2020:-21.0,2021:64.5

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9568  ls_ann_return_pct=15.0833  ls_ann_vol_pct=15.7639  ls_maxdd_pct=-40.9132  ls_hit_rate_pct=66.6667  n_months=276  worst_12m_pct=-38.2163  turnover_long_pct=36.8106  turnover_short_pct=30.9607  construction_weights=buffer 20%  ls_raw_sharpe=0.6555  ls_beta_mean=-0.6134  ls_beta_fullwindow=-0.6495  ls_sharpe_ex_top_years=0.6413  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9736  ls_sharpe_bull=1.1772
hedge/regime (diagnostics): beta ex-ante -0.6134 full-window -0.6495  raw Sharpe 0.6555  Sharpe ex top years 0.6413 (2000,2001,2021)  bear/bull 0.9736/1.1772
annual LS %: 1999:-25.3,2000:113.9,2001:57.2,2002:35.0,2003:30.1,2004:27.2,2005:17.6,2006:23.1,2007:0.2,2008:10.1,2009:-17.9,2010:12.5,2011:21.7,2012:8.6,2013:6.9,2014:7.5,2015:18.8,2016:18.4,2017:8.1,2018:9.1,2019:5.3,2020:-36.3,2021:70.9

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9004  ls_ann_return_pct=10.9483  ls_ann_vol_pct=12.1594  ls_maxdd_pct=-29.3341  ls_hit_rate_pct=61.5942  n_months=276  worst_12m_pct=-28.4859  turnover_long_pct=56.7968  turnover_short_pct=52.6024  construction_weights=target 10% vol, cap 3.0x, mean lev 0.92  ls_raw_sharpe=0.6424  ls_beta_mean=-0.4276  ls_beta_fullwindow=-0.3707  ls_sharpe_ex_top_years=0.6247  ls_top_years=2011,2015,2021  ls_sharpe_bear=0.4951  ls_sharpe_bull=1.2235
hedge/regime (diagnostics): beta ex-ante -0.4276 full-window -0.3707  raw Sharpe 0.6424  Sharpe ex top years 0.6247 (2011,2015,2021)  bear/bull 0.4951/1.2235
annual LS %: 1999:-14.7,2000:19.6,2001:14.1,2002:18.3,2003:8.8,2004:21.0,2005:16.9,2006:30.7,2007:-2.7,2008:2.9,2009:-12.0,2010:8.3,2011:44.2,2012:1.1,2013:12.6,2014:6.1,2015:35.0,2016:18.0,2017:10.4,2018:18.5,2019:8.9,2020:-28.3,2021:38.5
