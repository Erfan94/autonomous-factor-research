# RUN 031 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE c961f5791816 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v9: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9316  ls_ann_return_pct=14.8709  ls_ann_vol_pct=15.9633  ls_maxdd_pct=-43.6667  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-39.0055  turnover_long_pct=44.3025  turnover_short_pct=39.5813  construction_weights=family blend  ls_raw_sharpe=0.5790  ls_beta_mean=-0.6626  ls_beta_fullwindow=-0.7338  ls_sharpe_ex_top_years=0.5814  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9337  ls_sharpe_bull=1.0696
hedge/regime (diagnostics): beta ex-ante -0.6626 full-window -0.7338  raw Sharpe 0.5790  Sharpe ex top years 0.5814 (2000,2001,2021)  bear/bull 0.9337/1.0696
annual LS %: 1999:-14.0,2000:120.2,2001:63.3,2002:28.5,2003:37.0,2004:18.1,2005:17.6,2006:20.5,2007:3.4,2008:11.8,2009:-14.5,2010:11.8,2011:21.1,2012:6.3,2013:11.3,2014:2.2,2015:11.9,2016:17.8,2017:8.0,2018:3.7,2019:-3.2,2020:-38.4,2021:74.4

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9052  ls_ann_return_pct=14.7625  ls_ann_vol_pct=16.3083  ls_maxdd_pct=-44.3262  ls_hit_rate_pct=63.4058  n_months=276  worst_12m_pct=-40.4959  turnover_long_pct=45.7460  turnover_short_pct=40.4560  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5398  ls_beta_mean=-0.6875  ls_beta_fullwindow=-0.7673  ls_sharpe_ex_top_years=0.5877  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7896  ls_sharpe_bull=1.1144
hedge/regime (diagnostics): beta ex-ante -0.6875 full-window -0.7673  raw Sharpe 0.5398  Sharpe ex top years 0.5877 (2000,2001,2021)  bear/bull 0.7896/1.1144
annual LS %: 1999:-18.5,2000:122.3,2001:44.4,2002:30.3,2003:32.9,2004:17.7,2005:20.7,2006:21.5,2007:0.5,2008:5.3,2009:-12.6,2010:8.3,2011:23.7,2012:14.3,2013:12.7,2014:5.7,2015:12.5,2016:18.9,2017:11.4,2018:4.3,2019:-0.9,2020:-40.5,2021:80.5

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8059  ls_ann_return_pct=13.3923  ls_ann_vol_pct=16.6174  ls_maxdd_pct=-33.0059  ls_hit_rate_pct=61.5942  n_months=276  worst_12m_pct=-28.2879  turnover_long_pct=27.6729  turnover_short_pct=26.2966  construction_weights=Size=0.011;Value=0.034;Profitability=0.088;Investment=0.032;Momentum=0.052;PctAcc=0.097;CBOperProf=0.085;ShareIss5Y=0.100;cfp=0.095;XFIN=0.082;GP=0.086;MaxRet=0.079;roaq=0.085;RoE=0.075  ls_raw_sharpe=0.4150  ls_beta_mean=-0.7483  ls_beta_fullwindow=-0.8475  ls_sharpe_ex_top_years=0.5030  ls_top_years=2000,2004,2021  ls_sharpe_bear=0.6814  ls_sharpe_bull=1.0547
hedge/regime (diagnostics): beta ex-ante -0.7483 full-window -0.8475  raw Sharpe 0.4150  Sharpe ex top years 0.5030 (2000,2004,2021)  bear/bull 0.6814/1.0547
annual LS %: 1999:-24.5,2000:109.8,2001:26.2,2002:23.6,2003:25.3,2004:27.1,2005:23.0,2006:15.4,2007:15.0,2008:2.9,2009:-15.6,2010:12.5,2011:11.5,2012:4.4,2013:9.8,2014:0.8,2015:4.8,2016:7.4,2017:11.8,2018:11.6,2019:3.1,2020:-22.7,2021:73.4

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9186  ls_ann_return_pct=13.8449  ls_ann_vol_pct=15.0715  ls_maxdd_pct=-43.7997  ls_hit_rate_pct=63.0435  n_months=276  worst_12m_pct=-38.2751  turnover_long_pct=25.7705  turnover_short_pct=20.9563  construction_weights=buffer 20%  ls_raw_sharpe=0.5742  ls_beta_mean=-0.6235  ls_beta_fullwindow=-0.6929  ls_sharpe_ex_top_years=0.5772  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8731  ls_sharpe_bull=1.0732
hedge/regime (diagnostics): beta ex-ante -0.6235 full-window -0.6929  raw Sharpe 0.5742  Sharpe ex top years 0.5772 (2000,2001,2021)  bear/bull 0.8731/1.0732
annual LS %: 1999:-13.9,2000:114.9,2001:53.3,2002:24.2,2003:35.7,2004:21.9,2005:19.1,2006:19.3,2007:0.8,2008:11.0,2009:-15.4,2010:12.8,2011:15.1,2012:8.8,2013:9.9,2014:4.1,2015:9.1,2016:19.3,2017:6.7,2018:3.1,2019:-4.4,2020:-37.5,2021:70.7

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7769  ls_ann_return_pct=8.9595  ls_ann_vol_pct=11.5327  ls_maxdd_pct=-32.8967  ls_hit_rate_pct=62.6812  n_months=276  worst_12m_pct=-28.7381  turnover_long_pct=44.3025  turnover_short_pct=39.5813  construction_weights=target 10% vol, cap 3.0x, mean lev 0.91  ls_raw_sharpe=0.4560  ls_beta_mean=-0.4507  ls_beta_fullwindow=-0.4212  ls_sharpe_ex_top_years=0.5097  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.4089  ls_sharpe_bull=1.0109
hedge/regime (diagnostics): beta ex-ante -0.4507 full-window -0.4212  raw Sharpe 0.4560  Sharpe ex top years 0.5097 (2006,2011,2021)  bear/bull 0.4089/1.0109
annual LS %: 1999:-9.7,2000:21.6,2001:10.9,2002:10.2,2003:8.8,2004:13.5,2005:20.8,2006:30.6,2007:2.4,2008:6.9,2009:-6.5,2010:4.1,2011:33.4,2012:0.7,2013:17.4,2014:2.2,2015:12.5,2016:15.1,2017:9.1,2018:8.6,2019:0.1,2020:-28.0,2021:35.2
