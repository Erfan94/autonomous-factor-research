# RUN 002 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.5999  ls_ann_return_pct=7.3218  ls_ann_vol_pct=12.2043  ls_maxdd_pct=-45.5599  ls_hit_rate_pct=55.0725  n_months=276  worst_12m_pct=-33.0608  turnover_long_pct=28.0020  turnover_short_pct=23.6973  construction_weights=family blend  ls_raw_sharpe=0.7191  ls_beta_mean=-0.0846  ls_beta_fullwindow=-0.1399  ls_sharpe_ex_top_years=0.1590  ls_top_years=2000,2001,2003  ls_sharpe_bear=1.0745  ls_sharpe_bull=0.4561
hedge/regime (diagnostics): beta ex-ante -0.0846 full-window -0.1399  raw Sharpe 0.7191  Sharpe ex top years 0.1590 (2000,2001,2003)  bear/bull 1.0745/0.4561
annual LS %: 1999:0.7,2000:55.0,2001:70.8,2002:16.4,2003:36.2,2004:13.7,2005:8.8,2006:3.7,2007:-18.4,2008:15.3,2009:-4.1,2010:16.7,2011:2.6,2012:4.8,2013:-1.3,2014:-11.7,2015:-0.0,2016:15.3,2017:-5.7,2018:-4.7,2019:-9.0,2020:-33.1,2021:34.0

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6394  ls_ann_return_pct=7.9100  ls_ann_vol_pct=12.3702  ls_maxdd_pct=-50.5087  ls_hit_rate_pct=55.0725  n_months=276  worst_12m_pct=-36.5364  turnover_long_pct=31.1515  turnover_short_pct=28.1899  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.6419  ls_beta_mean=-0.1608  ls_beta_fullwindow=-0.2313  ls_sharpe_ex_top_years=0.1338  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7673  ls_sharpe_bull=0.5931
hedge/regime (diagnostics): beta ex-ante -0.1608 full-window -0.2313  raw Sharpe 0.6419  Sharpe ex top years 0.1338 (2000,2001,2021)  bear/bull 0.7673/0.5931
annual LS %: 1999:5.8,2000:80.6,2001:52.0,2002:10.2,2003:28.9,2004:16.1,2005:9.8,2006:1.8,2007:-14.5,2008:12.4,2009:-10.3,2010:13.8,2011:-0.8,2012:8.9,2013:3.3,2014:-4.4,2015:0.1,2016:16.7,2017:-4.8,2018:-8.6,2019:-10.4,2020:-36.5,2021:59.8

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6434  ls_ann_return_pct=9.4774  ls_ann_vol_pct=14.7295  ls_maxdd_pct=-27.8966  ls_hit_rate_pct=57.9710  n_months=276  worst_12m_pct=-27.8966  turnover_long_pct=27.0764  turnover_short_pct=26.8214  construction_weights=Size=0.043;Value=0.137;Profitability=0.451;Investment=0.141;Momentum=0.228  ls_raw_sharpe=0.4414  ls_beta_mean=-0.3407  ls_beta_fullwindow=-0.4504  ls_sharpe_ex_top_years=0.3053  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.6047  ls_sharpe_bull=0.7030
hedge/regime (diagnostics): beta ex-ante -0.3407 full-window -0.4504  raw Sharpe 0.4414  Sharpe ex top years 0.3053 (2000,2003,2021)  bear/bull 0.6047/0.7030
annual LS %: 1999:0.7,2000:74.5,2001:24.3,2002:9.6,2003:33.8,2004:18.5,2005:2.7,2006:-1.9,2007:18.8,2008:0.9,2009:-0.9,2010:10.0,2011:-9.9,2012:-3.7,2013:7.4,2014:-6.9,2015:11.0,2016:-4.8,2017:9.1,2018:-1.5,2019:-1.6,2020:-10.7,2021:59.3

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.5555  ls_ann_return_pct=6.3172  ls_ann_vol_pct=11.3725  ls_maxdd_pct=-43.3700  ls_hit_rate_pct=53.9855  n_months=276  worst_12m_pct=-30.8822  turnover_long_pct=15.2247  turnover_short_pct=10.8532  construction_weights=buffer 20%  ls_raw_sharpe=0.6701  ls_beta_mean=-0.0883  ls_beta_fullwindow=-0.1363  ls_sharpe_ex_top_years=0.1356  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9825  ls_sharpe_bull=0.4379
hedge/regime (diagnostics): beta ex-ante -0.0883 full-window -0.1363  raw Sharpe 0.6701  Sharpe ex top years 0.1356 (2000,2001,2021)  bear/bull 0.9825/0.4379
annual LS %: 1999:-1.9,2000:50.9,2001:54.0,2002:9.0,2003:32.8,2004:12.5,2005:7.7,2006:2.2,2007:-17.8,2008:14.7,2009:-2.3,2010:15.4,2011:1.3,2012:6.6,2013:-2.6,2014:-6.5,2015:-1.6,2016:15.7,2017:-5.3,2018:-5.6,2019:-8.3,2020:-30.9,2021:33.8

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.3064  ls_ann_return_pct=3.6873  ls_ann_vol_pct=12.0363  ls_maxdd_pct=-50.7389  ls_hit_rate_pct=55.0725  n_months=276  worst_12m_pct=-29.2231  turnover_long_pct=28.0020  turnover_short_pct=23.6973  construction_weights=target 10% vol, cap 3.0x, mean lev 1.19  ls_raw_sharpe=0.4764  ls_beta_mean=0.0261  ls_beta_fullwindow=-0.0153  ls_sharpe_ex_top_years=0.0784  ls_top_years=2001,2003,2016  ls_sharpe_bear=0.7780  ls_sharpe_bull=0.1732
hedge/regime (diagnostics): beta ex-ante 0.0261 full-window -0.0153  raw Sharpe 0.4764  Sharpe ex top years 0.0784 (2001,2003,2016)  bear/bull 0.7780/0.1732
annual LS %: 1999:3.8,2000:21.7,2001:27.5,2002:6.8,2003:22.0,2004:15.0,2005:11.7,2006:11.9,2007:-29.2,2008:18.5,2009:-3.8,2010:14.0,2011:-2.6,2012:7.0,2013:1.9,2014:-18.0,2015:-0.5,2016:21.7,2017:-4.0,2018:-7.7,2019:-11.2,2020:-28.8,2021:20.2
