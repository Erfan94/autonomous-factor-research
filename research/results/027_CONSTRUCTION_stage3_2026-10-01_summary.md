# RUN 027 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 43c92213ae73 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v7: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9512  ls_ann_return_pct=13.9480  ls_ann_vol_pct=14.6632  ls_maxdd_pct=-41.6776  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-36.4499  turnover_long_pct=43.4076  turnover_short_pct=39.4165  construction_weights=family blend  ls_raw_sharpe=0.6220  ls_beta_mean=-0.5866  ls_beta_fullwindow=-0.6493  ls_sharpe_ex_top_years=0.6234  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9739  ls_sharpe_bull=1.0454
hedge/regime (diagnostics): beta ex-ante -0.5866 full-window -0.6493  raw Sharpe 0.6220  Sharpe ex top years 0.6234 (2000,2001,2021)  bear/bull 0.9739/1.0454
annual LS %: 1999:-6.6,2000:102.3,2001:54.2,2002:27.0,2003:34.7,2004:20.9,2005:18.0,2006:18.9,2007:0.6,2008:11.8,2009:-12.2,2010:13.6,2011:16.5,2012:2.9,2013:12.5,2014:3.5,2015:7.6,2016:16.3,2017:6.8,2018:3.7,2019:-2.4,2020:-35.8,2021:66.4

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9685  ls_ann_return_pct=14.7489  ls_ann_vol_pct=15.2294  ls_maxdd_pct=-44.7100  ls_hit_rate_pct=63.0435  n_months=276  worst_12m_pct=-39.1733  turnover_long_pct=44.6887  turnover_short_pct=40.5236  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5995  ls_beta_mean=-0.6288  ls_beta_fullwindow=-0.7084  ls_sharpe_ex_top_years=0.6259  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7944  ls_sharpe_bull=1.1507
hedge/regime (diagnostics): beta ex-ante -0.6288 full-window -0.7084  raw Sharpe 0.5995  Sharpe ex top years 0.6259 (2000,2001,2021)  bear/bull 0.7944/1.1507
annual LS %: 1999:-9.5,2000:104.8,2001:43.7,2002:24.9,2003:29.2,2004:19.8,2005:20.0,2006:19.6,2007:-1.3,2008:9.2,2009:-10.3,2010:11.8,2011:18.2,2012:8.9,2013:14.5,2014:7.0,2015:9.2,2016:17.7,2017:11.3,2018:5.8,2019:-3.1,2020:-39.2,2021:101.2

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9109  ls_ann_return_pct=13.5293  ls_ann_vol_pct=14.8526  ls_maxdd_pct=-27.2932  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-24.4825  turnover_long_pct=30.7783  turnover_short_pct=29.4957  construction_weights=Size=0.013;Value=0.038;Profitability=0.106;Investment=0.037;Momentum=0.063;PctAcc=0.114;CBOperProf=0.102;ShareIss5Y=0.120;cfp=0.110;XFIN=0.096;GP=0.104;MaxRet=0.098  ls_raw_sharpe=0.4927  ls_beta_mean=-0.6738  ls_beta_fullwindow=-0.7575  ls_sharpe_ex_top_years=0.6049  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.7188  ls_sharpe_bull=1.1544
hedge/regime (diagnostics): beta ex-ante -0.6738 full-window -0.7575  raw Sharpe 0.4927  Sharpe ex top years 0.6049 (2000,2003,2021)  bear/bull 0.7188/1.1544
annual LS %: 1999:-16.2,2000:91.4,2001:27.7,2002:17.7,2003:29.2,2004:21.2,2005:19.2,2006:16.5,2007:9.8,2008:2.4,2009:-5.9,2010:14.9,2011:10.3,2012:4.0,2013:11.8,2014:3.8,2015:2.7,2016:6.2,2017:10.1,2018:10.0,2019:4.8,2020:-17.9,2021:78.8

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9277  ls_ann_return_pct=12.9334  ls_ann_vol_pct=13.9414  ls_maxdd_pct=-42.7669  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-36.7194  turnover_long_pct=24.5729  turnover_short_pct=20.6496  construction_weights=buffer 20%  ls_raw_sharpe=0.6135  ls_beta_mean=-0.5607  ls_beta_fullwindow=-0.6197  ls_sharpe_ex_top_years=0.5640  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9023  ls_sharpe_bull=1.0698
hedge/regime (diagnostics): beta ex-ante -0.5607 full-window -0.6197  raw Sharpe 0.6135  Sharpe ex top years 0.5640 (2000,2001,2021)  bear/bull 0.9023/1.0698
annual LS %: 1999:-11.2,2000:98.4,2001:48.8,2002:22.7,2003:34.7,2004:20.2,2005:17.8,2006:15.8,2007:-0.9,2008:11.8,2009:-12.8,2010:11.1,2011:14.9,2012:5.3,2013:11.3,2014:4.6,2015:7.9,2016:14.3,2017:5.8,2018:3.7,2019:-4.0,2020:-36.3,2021:75.0

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8425  ls_ann_return_pct=9.8067  ls_ann_vol_pct=11.6405  ls_maxdd_pct=-32.3684  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-27.3959  turnover_long_pct=43.4076  turnover_short_pct=39.4165  construction_weights=target 10% vol, cap 3.0x, mean lev 0.97  ls_raw_sharpe=0.5490  ls_beta_mean=-0.4298  ls_beta_fullwindow=-0.3967  ls_sharpe_ex_top_years=0.5987  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.6062  ls_sharpe_bull=0.9873
hedge/regime (diagnostics): beta ex-ante -0.4298 full-window -0.3967  raw Sharpe 0.5490  Sharpe ex top years 0.5987 (2006,2011,2021)  bear/bull 0.6062/0.9873
annual LS %: 1999:-3.1,2000:18.8,2001:10.7,2002:10.7,2003:9.6,2004:19.5,2005:21.2,2006:31.0,2007:-0.1,2008:8.3,2009:-4.7,2010:7.6,2011:29.6,2012:-4.4,2013:20.6,2014:3.1,2015:9.8,2016:16.1,2017:9.4,2018:14.8,2019:2.4,2020:-26.7,2021:35.0
