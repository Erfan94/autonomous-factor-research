# RUN 029 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE a12e87c5fb36 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v8: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9673  ls_ann_return_pct=15.1807  ls_ann_vol_pct=15.6937  ls_maxdd_pct=-43.3632  ls_hit_rate_pct=64.1304  n_months=276  worst_12m_pct=-38.5998  turnover_long_pct=44.0720  turnover_short_pct=39.5197  construction_weights=family blend  ls_raw_sharpe=0.6127  ls_beta_mean=-0.6497  ls_beta_fullwindow=-0.7212  ls_sharpe_ex_top_years=0.6039  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9605  ls_sharpe_bull=1.1220
hedge/regime (diagnostics): beta ex-ante -0.6497 full-window -0.7212  raw Sharpe 0.6127  Sharpe ex top years 0.6039 (2000,2001,2021)  bear/bull 0.9605/1.1220
annual LS %: 1999:-14.2,2000:125.8,2001:64.8,2002:28.3,2003:36.5,2004:18.9,2005:19.0,2006:20.8,2007:3.4,2008:11.8,2009:-14.1,2010:11.8,2011:21.5,2012:6.7,2013:13.7,2014:2.5,2015:10.3,2016:16.5,2017:9.3,2018:4.8,2019:-4.0,2020:-37.8,2021:74.0

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9472  ls_ann_return_pct=15.2838  ls_ann_vol_pct=16.1366  ls_maxdd_pct=-43.4856  ls_hit_rate_pct=64.8551  n_months=276  worst_12m_pct=-39.8711  turnover_long_pct=45.4138  turnover_short_pct=40.4866  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.5679  ls_beta_mean=-0.6829  ls_beta_fullwindow=-0.7647  ls_sharpe_ex_top_years=0.6418  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7824  ls_sharpe_bull=1.1810
hedge/regime (diagnostics): beta ex-ante -0.6829 full-window -0.7647  raw Sharpe 0.5679  Sharpe ex top years 0.6418 (2000,2001,2021)  bear/bull 0.7824/1.1810
annual LS %: 1999:-18.6,2000:118.9,2001:43.7,2002:25.8,2003:35.7,2004:18.3,2005:22.5,2006:23.2,2007:1.9,2008:8.0,2009:-10.8,2010:9.8,2011:22.8,2012:13.0,2013:13.4,2014:7.0,2015:12.1,2016:19.3,2017:11.8,2018:5.7,2019:-0.5,2020:-39.9,2021:84.8

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8167  ls_ann_return_pct=13.4087  ls_ann_vol_pct=16.4175  ls_maxdd_pct=-30.9133  ls_hit_rate_pct=63.4058  n_months=276  worst_12m_pct=-30.4154  turnover_long_pct=29.0152  turnover_short_pct=27.4272  construction_weights=Size=0.012;Value=0.036;Profitability=0.095;Investment=0.034;Momentum=0.057;PctAcc=0.104;CBOperProf=0.092;ShareIss5Y=0.108;cfp=0.102;XFIN=0.088;GP=0.092;MaxRet=0.086;roaq=0.094  ls_raw_sharpe=0.4233  ls_beta_mean=-0.7300  ls_beta_fullwindow=-0.8329  ls_sharpe_ex_top_years=0.5191  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.6225  ls_sharpe_bull=1.0841
hedge/regime (diagnostics): beta ex-ante -0.7300 full-window -0.8329  raw Sharpe 0.4233  Sharpe ex top years 0.5191 (2000,2001,2021)  bear/bull 0.6225/1.0841
annual LS %: 1999:-22.3,2000:109.4,2001:30.9,2002:21.4,2003:29.7,2004:23.5,2005:21.1,2006:16.9,2007:13.8,2008:-1.4,2009:-16.2,2010:14.1,2011:10.1,2012:3.4,2013:11.8,2014:3.1,2015:2.7,2016:6.5,2017:11.4,2018:11.1,2019:3.3,2020:-21.2,2021:74.1

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9375  ls_ann_return_pct=13.9361  ls_ann_vol_pct=14.8646  ls_maxdd_pct=-44.0713  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-38.1450  turnover_long_pct=25.5328  turnover_short_pct=20.9344  construction_weights=buffer 20%  ls_raw_sharpe=0.5960  ls_beta_mean=-0.6095  ls_beta_fullwindow=-0.6808  ls_sharpe_ex_top_years=0.5638  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8961  ls_sharpe_bull=1.0972
hedge/regime (diagnostics): beta ex-ante -0.6095 full-window -0.6808  raw Sharpe 0.5960  Sharpe ex top years 0.5638 (2000,2001,2021)  bear/bull 0.8961/1.0972
annual LS %: 1999:-14.0,2000:116.8,2001:53.4,2002:23.6,2003:34.9,2004:20.9,2005:19.0,2006:18.8,2007:-0.3,2008:13.8,2009:-15.4,2010:11.4,2011:16.6,2012:7.6,2013:10.9,2014:4.4,2015:8.7,2016:17.5,2017:6.2,2018:3.2,2019:-5.3,2020:-37.3,2021:80.7

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8438  ls_ann_return_pct=9.7385  ls_ann_vol_pct=11.5407  ls_maxdd_pct=-32.9382  ls_hit_rate_pct=63.0435  n_months=276  worst_12m_pct=-28.6560  turnover_long_pct=44.0720  turnover_short_pct=39.5197  construction_weights=target 10% vol, cap 3.0x, mean lev 0.93  ls_raw_sharpe=0.5171  ls_beta_mean=-0.4501  ls_beta_fullwindow=-0.4215  ls_sharpe_ex_top_years=0.5769  ls_top_years=2006,2011,2021  ls_sharpe_bear=0.4931  ls_sharpe_bull=1.0851
hedge/regime (diagnostics): beta ex-ante -0.4501 full-window -0.4215  raw Sharpe 0.5171  Sharpe ex top years 0.5769 (2006,2011,2021)  bear/bull 0.4931/1.0851
annual LS %: 1999:-9.8,2000:23.5,2001:11.4,2002:10.5,2003:8.8,2004:14.6,2005:22.7,2006:31.7,2007:3.1,2008:7.9,2009:-6.1,2010:5.5,2011:34.4,2012:1.1,2013:21.6,2014:1.8,2015:11.7,2016:15.2,2017:11.3,2018:11.3,2019:-0.3,2020:-27.7,2021:36.3
