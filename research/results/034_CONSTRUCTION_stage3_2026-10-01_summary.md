# RUN 034 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 1b4195ff18b4 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v10: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9193  ls_ann_return_pct=15.2529  ls_ann_vol_pct=16.5916  ls_maxdd_pct=-45.7772  ls_hit_rate_pct=63.4058  n_months=276  worst_12m_pct=-40.6494  turnover_long_pct=39.7994  turnover_short_pct=35.3912  construction_weights=family blend  ls_raw_sharpe=0.5785  ls_beta_mean=-0.6803  ls_beta_fullwindow=-0.7519  ls_sharpe_ex_top_years=0.5749  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8423  ls_sharpe_bull=1.0930
hedge/regime (diagnostics): beta ex-ante -0.6803 full-window -0.7519  raw Sharpe 0.5785  Sharpe ex top years 0.5749 (2000,2001,2021)  bear/bull 0.8423/1.0930
annual LS %: 1999:-16.3,2000:130.5,2001:60.1,2002:24.8,2003:37.9,2004:22.3,2005:19.5,2006:22.5,2007:5.0,2008:12.2,2009:-14.9,2010:10.3,2011:23.2,2012:5.3,2013:10.4,2014:3.0,2015:12.0,2016:21.9,2017:6.3,2018:3.6,2019:-4.7,2020:-39.2,2021:78.8

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8738  ls_ann_return_pct=14.6904  ls_ann_vol_pct=16.8126  ls_maxdd_pct=-46.9263  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-43.0135  turnover_long_pct=40.9512  turnover_short_pct=36.4932  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5141  ls_beta_mean=-0.7100  ls_beta_fullwindow=-0.7911  ls_sharpe_ex_top_years=0.5712  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.6919  ls_sharpe_bull=1.1007
hedge/regime (diagnostics): beta ex-ante -0.7100 full-window -0.7911  raw Sharpe 0.5141  Sharpe ex top years 0.5712 (2000,2001,2021)  bear/bull 0.6919/1.1007
annual LS %: 1999:-19.0,2000:119.8,2001:41.4,2002:25.3,2003:31.7,2004:19.6,2005:21.7,2006:23.0,2007:6.1,2008:4.9,2009:-13.4,2010:9.5,2011:24.2,2012:11.4,2013:14.0,2014:7.0,2015:11.4,2016:22.3,2017:10.1,2018:3.6,2019:-1.3,2020:-43.0,2021:82.1

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7628  ls_ann_return_pct=13.6225  ls_ann_vol_pct=17.8579  ls_maxdd_pct=-35.6156  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-33.4817  turnover_long_pct=31.3010  turnover_short_pct=29.2539  construction_weights=Size=0.011;Value=0.033;Profitability=0.081;Investment=0.030;Momentum=0.048;PctAcc=0.091;CBOperProf=0.079;ShareIss5Y=0.091;cfp=0.090;XFIN=0.076;GP=0.080;MaxRet=0.072;roaq=0.078;RoE=0.069;IdioVol3F=0.072  ls_raw_sharpe=0.3610  ls_beta_mean=-0.8275  ls_beta_fullwindow=-0.9346  ls_sharpe_ex_top_years=0.4722  ls_top_years=2000,2004,2021  ls_sharpe_bear=0.4917  ls_sharpe_bull=1.0778
hedge/regime (diagnostics): beta ex-ante -0.8275 full-window -0.9346  raw Sharpe 0.3610  Sharpe ex top years 0.4722 (2000,2004,2021)  bear/bull 0.4917/1.0778
annual LS %: 1999:-26.5,2000:107.3,2001:21.9,2002:19.1,2003:27.3,2004:28.5,2005:23.0,2006:16.2,2007:15.0,2008:2.3,2009:-22.3,2010:14.9,2011:13.4,2012:5.4,2013:12.5,2014:5.7,2015:6.3,2016:6.5,2017:10.7,2018:14.2,2019:9.7,2020:-26.0,2021:75.3

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8991  ls_ann_return_pct=13.8910  ls_ann_vol_pct=15.4502  ls_maxdd_pct=-43.9563  ls_hit_rate_pct=63.0435  n_months=276  worst_12m_pct=-37.7914  turnover_long_pct=22.0040  turnover_short_pct=17.6522  construction_weights=buffer 20%  ls_raw_sharpe=0.5589  ls_beta_mean=-0.6421  ls_beta_fullwindow=-0.7101  ls_sharpe_ex_top_years=0.5731  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7904  ls_sharpe_bull=1.0807
hedge/regime (diagnostics): beta ex-ante -0.6421 full-window -0.7101  raw Sharpe 0.5589  Sharpe ex top years 0.5731 (2000,2001,2021)  bear/bull 0.7904/1.0807
annual LS %: 1999:-15.6,2000:120.4,2001:44.5,2002:20.4,2003:33.8,2004:21.4,2005:20.3,2006:20.8,2007:2.6,2008:13.9,2009:-15.9,2010:13.4,2011:17.2,2012:9.4,2013:8.1,2014:4.3,2015:8.4,2016:20.3,2017:5.8,2018:4.2,2019:-6.6,2020:-36.7,2021:76.5

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7942  ls_ann_return_pct=9.2864  ls_ann_vol_pct=11.6927  ls_maxdd_pct=-33.2825  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-28.9043  turnover_long_pct=39.7994  turnover_short_pct=35.3912  construction_weights=target 10% vol, cap 3.0x, mean lev 0.90  ls_raw_sharpe=0.4841  ls_beta_mean=-0.4535  ls_beta_fullwindow=-0.4187  ls_sharpe_ex_top_years=0.5072  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.3851  ls_sharpe_bull=1.0475
hedge/regime (diagnostics): beta ex-ante -0.4535 full-window -0.4187  raw Sharpe 0.4841  Sharpe ex top years 0.5072 (2006,2011,2021)  bear/bull 0.3851/1.0475
annual LS %: 1999:-10.7,2000:21.3,2001:9.8,2002:8.4,2003:8.5,2004:18.8,2005:22.9,2006:32.4,2007:4.8,2008:7.3,2009:-5.6,2010:2.5,2011:39.4,2012:-2.3,2013:16.8,2014:2.3,2015:12.8,2016:17.6,2017:7.2,2018:7.9,2019:-0.6,2020:-27.7,2021:36.3
