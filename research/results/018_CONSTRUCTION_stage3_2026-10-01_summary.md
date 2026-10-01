# RUN 018 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 73ee92fe0723 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v3: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8479  ls_ann_return_pct=10.2876  ls_ann_vol_pct=12.1324  ls_maxdd_pct=-41.9210  ls_hit_rate_pct=59.4203  n_months=276  worst_12m_pct=-35.2929  turnover_long_pct=26.3407  turnover_short_pct=22.9657  construction_weights=family blend  ls_raw_sharpe=0.8738  ls_beta_mean=-0.1575  ls_beta_fullwindow=-0.1917  ls_sharpe_ex_top_years=0.4646  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0370  ls_sharpe_bull=0.8064
hedge/regime (diagnostics): beta ex-ante -0.1575 full-window -0.1917  raw Sharpe 0.8738  Sharpe ex top years 0.4646 (2000,2001,2021)  bear/bull 1.0370/0.8064
annual LS %: 1999:6.9,2000:60.1,2001:60.9,2002:22.7,2003:32.0,2004:11.4,2005:13.3,2006:8.2,2007:-12.0,2008:18.1,2009:-4.4,2010:17.4,2011:5.9,2012:4.7,2013:1.9,2014:-3.6,2015:6.5,2016:13.7,2017:3.1,2018:-0.9,2019:-4.0,2020:-34.9,2021:49.4

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9094  ls_ann_return_pct=10.8823  ls_ann_vol_pct=11.9669  ls_maxdd_pct=-44.0722  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-35.9591  turnover_long_pct=29.2830  turnover_short_pct=26.6981  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.8411  ls_beta_mean=-0.2149  ls_beta_fullwindow=-0.2560  ls_sharpe_ex_top_years=0.5051  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8053  ls_sharpe_bull=0.9033
hedge/regime (diagnostics): beta ex-ante -0.2149 full-window -0.2560  raw Sharpe 0.8411  Sharpe ex top years 0.5051 (2000,2001,2021)  bear/bull 0.8053/0.9033
annual LS %: 1999:18.3,2000:69.9,2001:44.0,2002:16.6,2003:30.1,2004:12.2,2005:15.1,2006:7.8,2007:-9.5,2008:14.2,2009:-10.3,2010:12.7,2011:9.3,2012:9.0,2013:4.6,2014:-5.7,2015:6.6,2016:17.1,2017:7.4,2018:-3.9,2019:-5.7,2020:-36.0,2021:76.6

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9485  ls_ann_return_pct=10.7355  ls_ann_vol_pct=11.3189  ls_maxdd_pct=-31.5329  ls_hit_rate_pct=62.6812  n_months=276  worst_12m_pct=-25.7103  turnover_long_pct=22.6264  turnover_short_pct=23.3717  construction_weights=Size=0.020;Value=0.064;Profitability=0.180;Investment=0.063;Momentum=0.103;PctAcc=0.186;CBOperProf=0.174;ShareIss5Y=0.209  ls_raw_sharpe=0.5802  ls_beta_mean=-0.4134  ls_beta_fullwindow=-0.4679  ls_sharpe_ex_top_years=0.5748  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.8549  ls_sharpe_bull=1.0705
hedge/regime (diagnostics): beta ex-ante -0.4134 full-window -0.4679  raw Sharpe 0.5802  Sharpe ex top years 0.5748 (2000,2003,2021)  bear/bull 0.8549/1.0705
annual LS %: 1999:-1.0,2000:52.6,2001:21.2,2002:19.4,2003:27.9,2004:16.2,2005:14.6,2006:7.5,2007:14.8,2008:2.6,2009:-1.9,2010:9.6,2011:5.7,2012:-5.5,2013:14.8,2014:4.3,2015:7.1,2016:-2.5,2017:12.6,2018:11.2,2019:-6.3,2020:-23.4,2021:77.9

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7887  ls_ann_return_pct=8.4054  ls_ann_vol_pct=10.6568  ls_maxdd_pct=-42.9135  ls_hit_rate_pct=58.6957  n_months=276  worst_12m_pct=-32.5841  turnover_long_pct=13.8536  turnover_short_pct=10.3824  construction_weights=buffer 20%  ls_raw_sharpe=0.7959  ls_beta_mean=-0.1635  ls_beta_fullwindow=-0.1973  ls_sharpe_ex_top_years=0.3825  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9758  ls_sharpe_bull=0.7484
hedge/regime (diagnostics): beta ex-ante -0.1635 full-window -0.1973  raw Sharpe 0.7959  Sharpe ex top years 0.3825 (2000,2001,2021)  bear/bull 0.9758/0.7484
annual LS %: 1999:4.7,2000:55.4,2001:50.1,2002:21.7,2003:32.3,2004:11.2,2005:10.9,2006:4.2,2007:-10.6,2008:13.3,2009:-7.5,2010:14.7,2011:7.2,2012:1.9,2013:3.8,2014:-2.6,2015:3.8,2016:16.5,2017:0.3,2018:-3.6,2019:-8.4,2020:-32.6,2021:39.9

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6550  ls_ann_return_pct=7.8217  ls_ann_vol_pct=11.9423  ls_maxdd_pct=-42.5240  ls_hit_rate_pct=60.1449  n_months=276  worst_12m_pct=-30.5453  turnover_long_pct=26.3407  turnover_short_pct=22.9657  construction_weights=target 10% vol, cap 3.0x, mean lev 1.19  ls_raw_sharpe=0.7202  ls_beta_mean=-0.1054  ls_beta_fullwindow=-0.1047  ls_sharpe_ex_top_years=0.4494  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7495  ls_sharpe_bull=0.6263
hedge/regime (diagnostics): beta ex-ante -0.1054 full-window -0.1047  raw Sharpe 0.7202  Sharpe ex top years 0.4494 (2000,2001,2021)  bear/bull 0.7495/0.6263
annual LS %: 1999:8.0,2000:23.9,2001:26.6,2002:11.6,2003:19.9,2004:11.8,2005:17.4,2006:19.9,2007:-18.9,2008:18.1,2009:-2.5,2010:20.1,2011:5.0,2012:4.8,2013:4.2,2014:-6.7,2015:13.3,2016:17.3,2017:7.6,2018:-4.2,2019:-2.5,2020:-30.2,2021:28.0
