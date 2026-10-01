# RUN 048 CONSTRUCTION stage 3

stamps: HARNESS 3561590b660a CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9826  ls_ann_return_pct=16.1222  ls_ann_vol_pct=16.4084  ls_maxdd_pct=-43.2143  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-41.3580  turnover_long_pct=58.1350  turnover_short_pct=54.4051  construction_weights=family blend  ls_raw_sharpe=0.7734  ls_beta_mean=-0.5437  ls_beta_fullwindow=-0.5596  ls_sharpe_ex_top_years=0.6498  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2192  ls_sharpe_bull=1.1146
hedge/regime (diagnostics): beta ex-ante -0.5437 full-window -0.5596  raw Sharpe 0.7734  Sharpe ex top years 0.6498 (2000,2001,2021)  bear/bull 1.2192/1.1146
annual LS %: 1999:-24.4,2000:120.0,2001:65.1,2002:43.1,2003:32.6,2004:24.8,2005:14.0,2006:27.2,2007:-3.0,2008:6.4,2009:-2.7,2010:21.4,2011:24.8,2012:5.8,2013:7.2,2014:3.4,2015:17.2,2016:20.0,2017:5.4,2018:9.3,2019:3.8,2020:-40.8,2021:77.0

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8583  ls_ann_return_pct=14.5893  ls_ann_vol_pct=16.9969  ls_maxdd_pct=-43.9810  ls_hit_rate_pct=63.0435  n_months=276  worst_12m_pct=-41.0035  turnover_long_pct=59.4748  turnover_short_pct=55.6761  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.6171  ls_beta_mean=-0.5955  ls_beta_fullwindow=-0.6408  ls_sharpe_ex_top_years=0.5413  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9859  ls_sharpe_bull=1.0373
hedge/regime (diagnostics): beta ex-ante -0.5955 full-window -0.6408  raw Sharpe 0.6171  Sharpe ex top years 0.5413 (2000,2001,2021)  bear/bull 0.9859/1.0373
annual LS %: 1999:-29.9,2000:118.1,2001:46.5,2002:30.8,2003:24.8,2004:23.9,2005:14.1,2006:30.5,2007:-5.2,2008:7.8,2009:-4.4,2010:16.0,2011:25.2,2012:7.0,2013:4.8,2014:6.2,2015:17.5,2016:18.0,2017:7.6,2018:8.6,2019:2.0,2020:-40.5,2021:82.5

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9020  ls_ann_return_pct=15.5421  ls_ann_vol_pct=17.2299  ls_maxdd_pct=-33.0623  ls_hit_rate_pct=62.6812  n_months=276  worst_12m_pct=-27.6691  turnover_long_pct=39.0837  turnover_short_pct=37.7284  construction_weights=Size=0.009;Value=0.027;Profitability=0.063;Investment=0.025;Momentum=0.037;PctAcc=0.073;CBOperProf=0.063;ShareIss5Y=0.066;cfp=0.072;XFIN=0.059;GP=0.060;MaxRet=0.055;roaq=0.060;RoE=0.054;IdioVol3F=0.054;STreversal=0.053;zerotrade6M=0.056;VolumeTrend=0.059;TrendFactor=0.056  ls_raw_sharpe=0.4641  ls_beta_mean=-0.8085  ls_beta_fullwindow=-0.9288  ls_sharpe_ex_top_years=0.6360  ls_top_years=2000,2004,2021  ls_sharpe_bear=0.6617  ls_sharpe_bull=1.2494
hedge/regime (diagnostics): beta ex-ante -0.8085 full-window -0.9288  raw Sharpe 0.4641  Sharpe ex top years 0.6360 (2000,2004,2021)  bear/bull 0.6617/1.2494
annual LS %: 1999:-27.5,2000:84.3,2001:19.7,2002:21.5,2003:32.6,2004:34.1,2005:22.4,2006:21.9,2007:13.0,2008:4.7,2009:-11.7,2010:23.9,2011:21.3,2012:7.1,2013:11.7,2014:9.5,2015:14.0,2016:4.3,2017:15.1,2018:13.2,2019:9.4,2020:-23.1,2021:80.5

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9540  ls_ann_return_pct=15.0110  ls_ann_vol_pct=15.7347  ls_maxdd_pct=-41.9743  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-38.5913  turnover_long_pct=38.5017  turnover_short_pct=32.5827  construction_weights=buffer 20%  ls_raw_sharpe=0.7195  ls_beta_mean=-0.5615  ls_beta_fullwindow=-0.5744  ls_sharpe_ex_top_years=0.6489  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2601  ls_sharpe_bull=1.0711
hedge/regime (diagnostics): beta ex-ante -0.5615 full-window -0.5744  raw Sharpe 0.7195  Sharpe ex top years 0.6489 (2000,2001,2021)  bear/bull 1.2601/1.0711
annual LS %: 1999:-25.3,2000:113.9,2001:57.2,2002:35.0,2003:35.1,2004:24.9,2005:15.0,2006:23.3,2007:-3.6,2008:8.7,2009:0.1,2010:16.0,2011:23.6,2012:5.7,2013:5.1,2014:5.4,2015:13.7,2016:22.0,2017:4.7,2018:6.4,2019:3.6,2020:-38.3,2021:67.1

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9006  ls_ann_return_pct=10.9355  ls_ann_vol_pct=12.1427  ls_maxdd_pct=-30.5929  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-29.2160  turnover_long_pct=58.1350  turnover_short_pct=54.4051  construction_weights=target 10% vol, cap 3.0x, mean lev 0.92  ls_raw_sharpe=0.7107  ls_beta_mean=-0.3902  ls_beta_fullwindow=-0.3133  ls_sharpe_ex_top_years=0.6143  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.7140  ls_sharpe_bull=1.1401
hedge/regime (diagnostics): beta ex-ante -0.3902 full-window -0.3133  raw Sharpe 0.7107  Sharpe ex top years 0.6143 (2006,2011,2021)  bear/bull 0.7140/1.1401
annual LS %: 1999:-14.7,2000:19.6,2001:14.1,2002:18.3,2003:9.8,2004:20.9,2005:14.9,2006:35.0,2007:-5.0,2008:0.1,2009:-1.0,2010:15.4,2011:51.5,2012:1.5,2013:11.4,2014:1.6,2015:25.6,2016:20.6,2017:8.1,2018:16.6,2019:6.2,2020:-28.7,2021:33.1
