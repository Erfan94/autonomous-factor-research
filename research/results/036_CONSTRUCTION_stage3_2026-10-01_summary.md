# RUN 036 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 335b06e3d608 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v11: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9423  ls_ann_return_pct=14.6139  ls_ann_vol_pct=15.5088  ls_maxdd_pct=-39.5291  ls_hit_rate_pct=59.4203  n_months=276  worst_12m_pct=-36.5521  turnover_long_pct=59.0772  turnover_short_pct=59.3116  construction_weights=family blend  ls_raw_sharpe=0.7372  ls_beta_mean=-0.4800  ls_beta_fullwindow=-0.5122  ls_sharpe_ex_top_years=0.5653  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0847  ls_sharpe_bull=1.0636
hedge/regime (diagnostics): beta ex-ante -0.4800 full-window -0.5122  raw Sharpe 0.7372  Sharpe ex top years 0.5653 (2000,2001,2021)  bear/bull 1.0847/1.0636
annual LS %: 1999:-17.8,2000:111.3,2001:67.9,2002:47.2,2003:28.2,2004:23.8,2005:17.7,2006:25.8,2007:-8.1,2008:8.6,2009:-12.5,2010:17.9,2011:18.5,2012:8.3,2013:0.3,2014:1.7,2015:9.7,2016:16.2,2017:2.2,2018:7.7,2019:1.2,2020:-36.6,2021:77.1

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8680  ls_ann_return_pct=13.6045  ls_ann_vol_pct=15.6738  ls_maxdd_pct=-41.8878  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-40.5938  turnover_long_pct=60.8377  turnover_short_pct=60.1179  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.6414  ls_beta_mean=-0.5011  ls_beta_fullwindow=-0.5497  ls_sharpe_ex_top_years=0.5161  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9245  ls_sharpe_bull=1.0133
hedge/regime (diagnostics): beta ex-ante -0.5011 full-window -0.5497  raw Sharpe 0.6414  Sharpe ex top years 0.5161 (2000,2001,2021)  bear/bull 0.9245/1.0133
annual LS %: 1999:-18.9,2000:93.6,2001:57.2,2002:41.1,2003:24.5,2004:20.9,2005:16.8,2006:22.6,2007:-9.4,2008:6.5,2009:-13.8,2010:13.7,2011:21.3,2012:12.0,2013:3.1,2014:2.5,2015:14.7,2016:14.4,2017:7.2,2018:5.5,2019:4.6,2020:-40.6,2021:82.2

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7873  ls_ann_return_pct=13.1111  ls_ann_vol_pct=16.6527  ls_maxdd_pct=-35.1418  ls_hit_rate_pct=62.6812  n_months=276  worst_12m_pct=-32.6573  turnover_long_pct=38.6199  turnover_short_pct=37.8576  construction_weights=Size=0.010;Value=0.030;Profitability=0.076;Investment=0.029;Momentum=0.045;PctAcc=0.084;CBOperProf=0.074;ShareIss5Y=0.084;cfp=0.084;XFIN=0.072;GP=0.073;MaxRet=0.067;roaq=0.072;RoE=0.065;IdioVol3F=0.067;STreversal=0.065  ls_raw_sharpe=0.3675  ls_beta_mean=-0.7917  ls_beta_fullwindow=-0.9088  ls_sharpe_ex_top_years=0.5096  ls_top_years=2000,2004,2021  ls_sharpe_bear=0.5175  ls_sharpe_bull=1.1219
hedge/regime (diagnostics): beta ex-ante -0.7917 full-window -0.9088  raw Sharpe 0.3675  Sharpe ex top years 0.5096 (2000,2004,2021)  bear/bull 0.5175/1.1219
annual LS %: 1999:-22.4,2000:83.1,2001:22.3,2002:26.3,2003:27.6,2004:31.9,2005:17.9,2006:17.9,2007:10.8,2008:4.3,2009:-22.4,2010:16.6,2011:10.9,2012:3.6,2013:10.9,2014:5.0,2015:5.7,2016:10.9,2017:9.4,2018:13.5,2019:8.1,2020:-21.9,2021:65.3

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9068  ls_ann_return_pct=13.6738  ls_ann_vol_pct=15.0797  ls_maxdd_pct=-37.7303  ls_hit_rate_pct=60.8696  n_months=276  worst_12m_pct=-35.0504  turnover_long_pct=40.0875  turnover_short_pct=38.2368  construction_weights=buffer 20%  ls_raw_sharpe=0.7043  ls_beta_mean=-0.4808  ls_beta_fullwindow=-0.5179  ls_sharpe_ex_top_years=0.5302  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1657  ls_sharpe_bull=1.0009
hedge/regime (diagnostics): beta ex-ante -0.4808 full-window -0.5179  raw Sharpe 0.7043  Sharpe ex top years 0.5302 (2000,2001,2021)  bear/bull 1.1657/1.0009
annual LS %: 1999:-19.1,2000:107.8,2001:67.5,2002:40.5,2003:29.0,2004:21.7,2005:16.5,2006:22.6,2007:-5.9,2008:13.4,2009:-12.5,2010:14.3,2011:16.5,2012:7.2,2013:1.7,2014:1.4,2015:7.8,2016:16.4,2017:0.9,2018:3.7,2019:1.1,2020:-34.8,2021:68.5

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8265  ls_ann_return_pct=10.2362  ls_ann_vol_pct=12.3847  ls_maxdd_pct=-30.6598  ls_hit_rate_pct=59.7826  n_months=276  worst_12m_pct=-27.8115  turnover_long_pct=59.0772  turnover_short_pct=59.3116  construction_weights=target 10% vol, cap 3.0x, mean lev 0.98  ls_raw_sharpe=0.6615  ls_beta_mean=-0.3517  ls_beta_fullwindow=-0.2985  ls_sharpe_ex_top_years=0.5542  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.6468  ls_sharpe_bull=1.0073
hedge/regime (diagnostics): beta ex-ante -0.3517 full-window -0.2985  raw Sharpe 0.6615  Sharpe ex top years 0.5542 (2006,2011,2021)  bear/bull 0.6468/1.0073
annual LS %: 1999:-10.3,2000:19.0,2001:17.1,2002:22.4,2003:9.2,2004:21.1,2005:23.6,2006:44.9,2007:-12.0,2008:3.6,2009:-8.4,2010:12.0,2011:29.6,2012:5.9,2013:-0.7,2014:0.7,2015:15.9,2016:17.9,2017:4.5,2018:20.7,2019:7.1,2020:-27.8,2021:41.7
