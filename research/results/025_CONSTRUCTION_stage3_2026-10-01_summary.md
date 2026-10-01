# RUN 025 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 21a6688ae5d1 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v6: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9255  ls_ann_return_pct=11.7157  ls_ann_vol_pct=12.6589  ls_maxdd_pct=-49.4236  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-38.6538  turnover_long_pct=25.2323  turnover_short_pct=22.2917  construction_weights=family blend  ls_raw_sharpe=0.8434  ls_beta_mean=-0.2766  ls_beta_fullwindow=-0.3225  ls_sharpe_ex_top_years=0.4897  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2686  ls_sharpe_bull=0.8422
hedge/regime (diagnostics): beta ex-ante -0.2766 full-window -0.3225  raw Sharpe 0.8434  Sharpe ex top years 0.4897 (2000,2001,2021)  bear/bull 1.2686/0.8422
annual LS %: 1999:6.1,2000:86.1,2001:58.1,2002:28.9,2003:32.9,2004:13.5,2005:17.4,2006:13.6,2007:-8.0,2008:14.2,2009:-3.7,2010:12.2,2011:6.1,2012:5.6,2013:7.1,2014:-6.6,2015:4.3,2016:17.9,2017:0.2,2018:5.1,2019:-11.1,2020:-38.7,2021:68.1

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9048  ls_ann_return_pct=11.6583  ls_ann_vol_pct=12.8853  ls_maxdd_pct=-47.9342  ls_hit_rate_pct=64.1304  n_months=276  worst_12m_pct=-39.0023  turnover_long_pct=27.9955  turnover_short_pct=24.4471  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.7412  ls_beta_mean=-0.3206  ls_beta_fullwindow=-0.3864  ls_sharpe_ex_top_years=0.5142  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9671  ls_sharpe_bull=0.8801
hedge/regime (diagnostics): beta ex-ante -0.3206 full-window -0.3864  raw Sharpe 0.7412  Sharpe ex top years 0.5142 (2000,2001,2021)  bear/bull 0.9671/0.8801
annual LS %: 1999:10.3,2000:95.3,2001:34.0,2002:27.1,2003:22.1,2004:11.9,2005:20.7,2006:12.3,2007:-4.8,2008:17.1,2009:-6.0,2010:11.7,2011:7.2,2012:6.2,2013:10.3,2014:-4.0,2015:1.6,2016:15.7,2017:4.8,2018:0.7,2019:-8.9,2020:-39.0,2021:81.8

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=1.0260  ls_ann_return_pct=12.0972  ls_ann_vol_pct=11.7902  ls_maxdd_pct=-28.1056  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-22.4922  turnover_long_pct=20.9970  turnover_short_pct=20.6418  construction_weights=Size=0.013;Value=0.041;Profitability=0.119;Investment=0.040;Momentum=0.070;PctAcc=0.125;CBOperProf=0.115;ShareIss5Y=0.136;cfp=0.118;XFIN=0.107;GP=0.116  ls_raw_sharpe=0.6389  ls_beta_mean=-0.4860  ls_beta_fullwindow=-0.5517  ls_sharpe_ex_top_years=0.7165  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2154  ls_sharpe_bull=1.0868
hedge/regime (diagnostics): beta ex-ante -0.4860 full-window -0.5517  raw Sharpe 0.6389  Sharpe ex top years 0.7165 (2000,2001,2021)  bear/bull 1.2154/1.0868
annual LS %: 1999:-8.7,2000:68.2,2001:26.5,2002:20.6,2003:24.7,2004:19.5,2005:15.3,2006:12.7,2007:8.9,2008:8.7,2009:6.4,2010:12.3,2011:10.2,2012:-1.0,2013:12.3,2014:2.8,2015:0.5,2016:7.6,2017:8.5,2018:12.5,2019:-7.8,2020:-16.6,2021:66.1

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8329  ls_ann_return_pct=9.4449  ls_ann_vol_pct=11.3397  ls_maxdd_pct=-44.8913  ls_hit_rate_pct=58.3333  n_months=276  worst_12m_pct=-33.5247  turnover_long_pct=13.2818  turnover_short_pct=10.5607  construction_weights=buffer 20%  ls_raw_sharpe=0.7272  ls_beta_mean=-0.2715  ls_beta_fullwindow=-0.3218  ls_sharpe_ex_top_years=0.3956  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0991  ls_sharpe_bull=0.7623
hedge/regime (diagnostics): beta ex-ante -0.2715 full-window -0.3218  raw Sharpe 0.7272  Sharpe ex top years 0.3956 (2000,2001,2021)  bear/bull 1.0991/0.7623
annual LS %: 1999:5.7,2000:83.6,2001:39.9,2002:27.5,2003:27.9,2004:12.2,2005:15.2,2006:8.3,2007:-10.2,2008:15.2,2009:-6.3,2010:10.9,2011:5.6,2012:1.3,2013:2.6,2014:-5.6,2015:1.7,2016:18.2,2017:-3.0,2018:3.0,2019:-11.1,2020:-33.5,2021:54.0

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6863  ls_ann_return_pct=8.1145  ls_ann_vol_pct=11.8233  ls_maxdd_pct=-48.8891  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-34.2404  turnover_long_pct=25.2323  turnover_short_pct=22.2917  construction_weights=target 10% vol, cap 3.0x, mean lev 1.11  ls_raw_sharpe=0.6861  ls_beta_mean=-0.1970  ls_beta_fullwindow=-0.1865  ls_sharpe_ex_top_years=0.4445  ls_top_years=2000,2006,2021  ls_sharpe_bear=0.8046  ls_sharpe_bull=0.6668
hedge/regime (diagnostics): beta ex-ante -0.1970 full-window -0.1865  raw Sharpe 0.6861  Sharpe ex top years 0.4445 (2000,2006,2021)  bear/bull 0.8046/0.6668
annual LS %: 1999:6.2,2000:28.3,2001:18.7,2002:14.5,2003:14.3,2004:13.9,2005:24.1,2006:28.0,2007:-14.1,2008:11.6,2009:-2.0,2010:10.8,2011:5.9,2012:6.0,2013:17.3,2014:-9.7,2015:6.7,2016:20.5,2017:3.0,2018:6.4,2019:-8.8,2020:-34.2,2021:36.9
