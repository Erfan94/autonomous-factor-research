# RUN 041 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE fa17bd1cd37e DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v13: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9786  ls_ann_return_pct=16.1259  ls_ann_vol_pct=16.4788  ls_maxdd_pct=-41.6031  ls_hit_rate_pct=64.4928  n_months=276  worst_12m_pct=-39.2745  turnover_long_pct=56.5533  turnover_short_pct=53.1515  construction_weights=family blend  ls_raw_sharpe=0.7188  ls_beta_mean=-0.5891  ls_beta_fullwindow=-0.6194  ls_sharpe_ex_top_years=0.6349  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9616  ls_sharpe_bull=1.2044
hedge/regime (diagnostics): beta ex-ante -0.5891 full-window -0.6194  raw Sharpe 0.7188  Sharpe ex top years 0.6349 (2000,2001,2021)  bear/bull 0.9616/1.2044
annual LS %: 1999:-24.4,2000:120.0,2001:65.1,2002:43.1,2003:31.4,2004:25.4,2005:16.5,2006:25.4,2007:-1.2,2008:8.0,2009:-16.3,2010:18.7,2011:25.3,2012:9.6,2013:6.9,2014:7.9,2015:22.0,2016:15.4,2017:5.1,2018:10.1,2019:3.1,2020:-38.6,2021:80.4

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8257  ls_ann_return_pct=14.1114  ls_ann_vol_pct=17.0902  ls_maxdd_pct=-46.5010  ls_hit_rate_pct=64.1304  n_months=276  worst_12m_pct=-43.6158  turnover_long_pct=58.0434  turnover_short_pct=54.6385  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5625  ls_beta_mean=-0.6240  ls_beta_fullwindow=-0.6745  ls_sharpe_ex_top_years=0.4917  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7273  ls_sharpe_bull=1.0767
hedge/regime (diagnostics): beta ex-ante -0.6240 full-window -0.6745  raw Sharpe 0.5625  Sharpe ex top years 0.4917 (2000,2001,2021)  bear/bull 0.7273/1.0767
annual LS %: 1999:-29.9,2000:118.1,2001:46.5,2002:30.8,2003:23.5,2004:22.6,2005:16.7,2006:27.4,2007:-2.7,2008:3.5,2009:-15.1,2010:15.1,2011:27.6,2012:12.4,2013:6.6,2014:8.5,2015:18.6,2016:13.6,2017:11.7,2018:6.5,2019:2.5,2020:-43.5,2021:83.4

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8000  ls_ann_return_pct=13.6834  ls_ann_vol_pct=17.1040  ls_maxdd_pct=-33.0623  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-29.1547  turnover_long_pct=35.6296  turnover_short_pct=34.7385  construction_weights=Size=0.009;Value=0.029;Profitability=0.066;Investment=0.026;Momentum=0.039;PctAcc=0.077;CBOperProf=0.066;ShareIss5Y=0.071;cfp=0.077;XFIN=0.062;GP=0.065;MaxRet=0.058;roaq=0.063;RoE=0.057;IdioVol3F=0.057;STreversal=0.058;zerotrade6M=0.058;VolumeTrend=0.063  ls_raw_sharpe=0.3673  ls_beta_mean=-0.8275  ls_beta_fullwindow=-0.9471  ls_sharpe_ex_top_years=0.5399  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.5377  ls_sharpe_bull=1.1611
hedge/regime (diagnostics): beta ex-ante -0.8275 full-window -0.9471  raw Sharpe 0.3673  Sharpe ex top years 0.5399 (2000,2003,2021)  bear/bull 0.5377/1.1611
annual LS %: 1999:-27.5,2000:84.3,2001:19.7,2002:21.5,2003:30.9,2004:30.6,2005:17.2,2006:16.7,2007:10.4,2008:2.1,2009:-19.1,2010:21.1,2011:15.2,2012:3.4,2013:13.8,2014:9.2,2015:13.9,2016:4.9,2017:16.7,2018:12.3,2019:10.5,2020:-23.1,2021:66.2

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9448  ls_ann_return_pct=14.8945  ls_ann_vol_pct=15.7653  ls_maxdd_pct=-42.7689  ls_hit_rate_pct=65.5797  n_months=276  worst_12m_pct=-39.0345  turnover_long_pct=36.7291  turnover_short_pct=31.5679  construction_weights=buffer 20%  ls_raw_sharpe=0.6667  ls_beta_mean=-0.5956  ls_beta_fullwindow=-0.6272  ls_sharpe_ex_top_years=0.6222  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0350  ls_sharpe_bull=1.1356
hedge/regime (diagnostics): beta ex-ante -0.5956 full-window -0.6272  raw Sharpe 0.6667  Sharpe ex top years 0.6222 (2000,2001,2021)  bear/bull 1.0350/1.1356
annual LS %: 1999:-25.3,2000:113.9,2001:57.2,2002:35.0,2003:31.3,2004:24.6,2005:17.4,2006:23.7,2007:-0.3,2008:11.2,2009:-15.2,2010:14.5,2011:23.0,2012:9.6,2013:7.3,2014:7.5,2015:15.4,2016:17.5,2017:5.8,2018:8.3,2019:3.5,2020:-38.5,2021:71.6

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9088  ls_ann_return_pct=11.0221  ls_ann_vol_pct=12.1277  ls_maxdd_pct=-30.1090  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-28.9434  turnover_long_pct=56.5533  turnover_short_pct=53.1515  construction_weights=target 10% vol, cap 3.0x, mean lev 0.90  ls_raw_sharpe=0.6663  ls_beta_mean=-0.4179  ls_beta_fullwindow=-0.3560  ls_sharpe_ex_top_years=0.6311  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.5295  ls_sharpe_bull=1.2239
hedge/regime (diagnostics): beta ex-ante -0.4179 full-window -0.3560  raw Sharpe 0.6663  Sharpe ex top years 0.6311 (2006,2011,2021)  bear/bull 0.5295/1.2239
annual LS %: 1999:-14.7,2000:19.6,2001:14.1,2002:18.3,2003:9.1,2004:21.7,2005:19.3,2006:31.6,2007:-2.4,2008:3.1,2009:-9.2,2010:9.5,2011:46.9,2012:4.6,2013:11.0,2014:5.7,2015:30.6,2016:17.7,2017:7.8,2018:17.8,2019:5.4,2020:-28.4,2021:38.7
