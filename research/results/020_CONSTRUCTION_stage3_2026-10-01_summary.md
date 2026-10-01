# RUN 020 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 3329679c69fb DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v4: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9960  ls_ann_return_pct=12.0191  ls_ann_vol_pct=12.0674  ls_maxdd_pct=-40.6324  ls_hit_rate_pct=62.6812  n_months=276  worst_12m_pct=-29.3696  turnover_long_pct=25.1677  turnover_short_pct=22.3010  construction_weights=family blend  ls_raw_sharpe=0.9134  ls_beta_mean=-0.2295  ls_beta_fullwindow=-0.2627  ls_sharpe_ex_top_years=0.6135  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2300  ls_sharpe_bull=0.9550
hedge/regime (diagnostics): beta ex-ante -0.2295 full-window -0.2627  raw Sharpe 0.9134  Sharpe ex top years 0.6135 (2000,2001,2021)  bear/bull 1.2300/0.9550
annual LS %: 1999:4.2,2000:77.1,2001:59.1,2002:29.0,2003:30.9,2004:13.0,2005:18.1,2006:11.4,2007:-4.0,2008:15.9,2009:-8.3,2010:14.9,2011:9.6,2012:3.6,2013:6.5,2014:-2.7,2015:6.6,2016:15.4,2017:3.9,2018:-1.5,2019:-8.1,2020:-29.4,2021:59.7

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=1.0064  ls_ann_return_pct=12.1956  ls_ann_vol_pct=12.1186  ls_maxdd_pct=-44.6904  ls_hit_rate_pct=63.7681  n_months=276  worst_12m_pct=-34.8805  turnover_long_pct=27.6680  turnover_short_pct=24.7905  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.8343  ls_beta_mean=-0.2821  ls_beta_fullwindow=-0.3416  ls_sharpe_ex_top_years=0.6727  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7938  ls_sharpe_bull=1.0516
hedge/regime (diagnostics): beta ex-ante -0.2821 full-window -0.3416  raw Sharpe 0.8343  Sharpe ex top years 0.6727 (2000,2001,2021)  bear/bull 0.7938/1.0516
annual LS %: 1999:16.9,2000:88.3,2001:32.1,2002:23.7,2003:27.0,2004:12.7,2005:21.9,2006:11.4,2007:-3.5,2008:14.8,2009:-6.9,2010:11.5,2011:8.7,2012:10.4,2013:11.3,2014:-1.5,2015:5.0,2016:12.7,2017:7.9,2018:-1.5,2019:-8.5,2020:-34.9,2021:74.4

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9344  ls_ann_return_pct=10.6753  ls_ann_vol_pct=11.4246  ls_maxdd_pct=-33.4205  ls_hit_rate_pct=60.5072  n_months=276  worst_12m_pct=-25.6653  turnover_long_pct=22.0161  turnover_short_pct=22.4961  construction_weights=Size=0.016;Value=0.050;Profitability=0.154;Investment=0.052;Momentum=0.089;PctAcc=0.156;CBOperProf=0.151;ShareIss5Y=0.185;cfp=0.148  ls_raw_sharpe=0.6055  ls_beta_mean=-0.4171  ls_beta_fullwindow=-0.4723  ls_sharpe_ex_top_years=0.5619  ls_top_years=2000,2003,2021  ls_sharpe_bear=1.0648  ls_sharpe_bull=1.0097
hedge/regime (diagnostics): beta ex-ante -0.4171 full-window -0.4723  raw Sharpe 0.6055  Sharpe ex top years 0.5619 (2000,2003,2021)  bear/bull 1.0648/1.0097
annual LS %: 1999:-7.0,2000:62.8,2001:22.6,2002:22.2,2003:23.5,2004:17.1,2005:14.0,2006:12.5,2007:7.6,2008:2.0,2009:7.3,2010:9.5,2011:4.9,2012:-5.5,2013:9.8,2014:7.9,2015:2.8,2016:6.1,2017:6.9,2018:7.5,2019:-7.5,2020:-23.4,2021:76.3

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9042  ls_ann_return_pct=9.6164  ls_ann_vol_pct=10.6355  ls_maxdd_pct=-42.2028  ls_hit_rate_pct=60.8696  n_months=276  worst_12m_pct=-28.1259  turnover_long_pct=13.0087  turnover_short_pct=10.2323  construction_weights=buffer 20%  ls_raw_sharpe=0.7936  ls_beta_mean=-0.2362  ls_beta_fullwindow=-0.2737  ls_sharpe_ex_top_years=0.5132  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0131  ls_sharpe_bull=0.9035
hedge/regime (diagnostics): beta ex-ante -0.2362 full-window -0.2737  raw Sharpe 0.7936  Sharpe ex top years 0.5132 (2000,2001,2021)  bear/bull 1.0131/0.9035
annual LS %: 1999:3.3,2000:68.8,2001:42.4,2002:23.9,2003:29.6,2004:12.5,2005:14.7,2006:7.2,2007:-4.3,2008:13.9,2009:-8.3,2010:11.3,2011:9.2,2012:1.9,2013:6.7,2014:-0.6,2015:2.7,2016:14.4,2017:1.8,2018:-1.0,2019:-12.6,2020:-28.1,2021:48.1

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7743  ls_ann_return_pct=8.9890  ls_ann_vol_pct=11.6095  ls_maxdd_pct=-43.3786  ls_hit_rate_pct=64.4928  n_months=276  worst_12m_pct=-27.5255  turnover_long_pct=25.1677  turnover_short_pct=22.3010  construction_weights=target 10% vol, cap 3.0x, mean lev 1.18  ls_raw_sharpe=0.7679  ls_beta_mean=-0.1689  ls_beta_fullwindow=-0.1579  ls_sharpe_ex_top_years=0.5639  ls_top_years=2000,2006,2021  ls_sharpe_bear=0.8066  ls_sharpe_bull=0.7840
hedge/regime (diagnostics): beta ex-ante -0.1689 full-window -0.1579  raw Sharpe 0.7679  Sharpe ex top years 0.5639 (2000,2006,2021)  bear/bull 0.8066/0.7840
annual LS %: 1999:4.9,2000:25.1,2001:22.0,2002:15.0,2003:14.9,2004:13.0,2005:24.9,2006:27.6,2007:-8.1,2008:18.4,2009:-7.0,2010:17.5,2011:9.6,2012:4.2,2013:12.6,2014:-4.5,2015:9.9,2016:17.1,2017:7.1,2018:-4.8,2019:-7.4,2020:-27.5,2021:37.7
