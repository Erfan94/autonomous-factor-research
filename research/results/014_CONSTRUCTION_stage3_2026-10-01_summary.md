# RUN 014 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE cbeb16455bf4 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v1: Size, Value, Profitability, Investment, Momentum, PctAcc

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6139  ls_ann_return_pct=7.3826  ls_ann_vol_pct=12.0247  ls_maxdd_pct=-41.2812  ls_hit_rate_pct=56.5217  n_months=276  worst_12m_pct=-30.2953  turnover_long_pct=27.6281  turnover_short_pct=24.0838  construction_weights=family blend  ls_raw_sharpe=0.7371  ls_beta_mean=-0.0742  ls_beta_fullwindow=-0.1210  ls_sharpe_ex_top_years=0.2017  ls_top_years=2000,2001,2003  ls_sharpe_bear=0.8526  ls_sharpe_bull=0.5544
hedge/regime (diagnostics): beta ex-ante -0.0742 full-window -0.1210  raw Sharpe 0.7371  Sharpe ex top years 0.2017 (2000,2001,2003)  bear/bull 0.8526/0.5544
annual LS %: 1999:2.1,2000:58.7,2001:57.9,2002:21.2,2003:34.5,2004:12.8,2005:12.4,2006:2.4,2007:-16.5,2008:16.1,2009:-14.2,2010:19.0,2011:-2.8,2012:5.0,2013:2.5,2014:-7.7,2015:3.8,2016:9.7,2017:-2.8,2018:-6.7,2019:-7.9,2020:-29.7,2021:33.3

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6042  ls_ann_return_pct=7.6662  ls_ann_vol_pct=12.6874  ls_maxdd_pct=-49.4004  ls_hit_rate_pct=55.4348  n_months=276  worst_12m_pct=-32.3208  turnover_long_pct=31.2230  turnover_short_pct=28.8942  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.6399  ls_beta_mean=-0.1298  ls_beta_fullwindow=-0.1961  ls_sharpe_ex_top_years=0.1271  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.6861  ls_sharpe_bull=0.5556
hedge/regime (diagnostics): beta ex-ante -0.1298 full-window -0.1961  raw Sharpe 0.6399  Sharpe ex top years 0.1271 (2000,2001,2021)  bear/bull 0.6861/0.5556
annual LS %: 1999:10.2,2000:78.1,2001:44.3,2002:21.7,2003:28.6,2004:14.0,2005:10.5,2006:-0.6,2007:-12.6,2008:13.7,2009:-17.7,2010:13.6,2011:-2.7,2012:7.2,2013:2.7,2014:-8.4,2015:-1.2,2016:15.6,2017:-3.2,2018:-9.6,2019:-12.5,2020:-32.3,2021:62.1

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.7089  ls_ann_return_pct=8.4842  ls_ann_vol_pct=11.9673  ls_maxdd_pct=-27.2695  ls_hit_rate_pct=60.5072  n_months=276  worst_12m_pct=-26.9454  turnover_long_pct=26.4003  turnover_short_pct=27.2406  construction_weights=Size=0.030;Value=0.093;Profitability=0.322;Investment=0.098;Momentum=0.168;PctAcc=0.290  ls_raw_sharpe=0.4936  ls_beta_mean=-0.3117  ls_beta_fullwindow=-0.3928  ls_sharpe_ex_top_years=0.3638  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.6767  ls_sharpe_bull=0.7809
hedge/regime (diagnostics): beta ex-ante -0.3117 full-window -0.3928  raw Sharpe 0.4936  Sharpe ex top years 0.3638 (2000,2003,2021)  bear/bull 0.6767/0.7809
annual LS %: 1999:2.5,2000:44.1,2001:19.7,2002:12.8,2003:29.8,2004:16.5,2005:10.5,2006:8.8,2007:13.8,2008:4.3,2009:-6.9,2010:9.6,2011:-12.1,2012:-4.3,2013:7.7,2014:-2.5,2015:4.5,2016:-4.3,2017:8.2,2018:0.1,2019:-0.4,2020:-10.2,2021:58.1

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.5546  ls_ann_return_pct=6.0719  ls_ann_vol_pct=10.9481  ls_maxdd_pct=-43.4824  ls_hit_rate_pct=54.7101  n_months=276  worst_12m_pct=-27.9587  turnover_long_pct=14.7008  turnover_short_pct=10.7132  construction_weights=buffer 20%  ls_raw_sharpe=0.6649  ls_beta_mean=-0.0777  ls_beta_fullwindow=-0.1279  ls_sharpe_ex_top_years=0.1374  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8882  ls_sharpe_bull=0.4702
hedge/regime (diagnostics): beta ex-ante -0.0777 full-window -0.1279  raw Sharpe 0.6649  Sharpe ex top years 0.1374 (2000,2001,2021)  bear/bull 0.8882/0.4702
annual LS %: 1999:-0.5,2000:49.7,2001:48.0,2002:19.7,2003:32.6,2004:12.9,2005:10.6,2006:-1.7,2007:-16.2,2008:14.3,2009:-9.1,2010:14.1,2011:0.8,2012:4.0,2013:0.2,2014:-5.7,2015:-0.7,2016:10.2,2017:-5.8,2018:-7.9,2019:-9.1,2020:-28.0,2021:34.0

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.3392  ls_ann_return_pct=4.0367  ls_ann_vol_pct=11.9001  ls_maxdd_pct=-44.9627  ls_hit_rate_pct=55.0725  n_months=276  worst_12m_pct=-29.8459  turnover_long_pct=27.6281  turnover_short_pct=24.0838  construction_weights=target 10% vol, cap 3.0x, mean lev 1.20  ls_raw_sharpe=0.5110  ls_beta_mean=0.0263  ls_beta_fullwindow=-0.0106  ls_sharpe_ex_top_years=0.1250  ls_top_years=2001,2008,2021  ls_sharpe_bear=0.5451  ls_sharpe_bull=0.2762
hedge/regime (diagnostics): beta ex-ante 0.0263 full-window -0.0106  raw Sharpe 0.5110  Sharpe ex top years 0.1250 (2001,2008,2021)  bear/bull 0.5451/0.2762
annual LS %: 1999:3.8,2000:19.7,2001:24.5,2002:11.0,2003:19.9,2004:12.6,2005:15.7,2006:6.5,2007:-27.5,2008:21.5,2009:-12.0,2010:16.3,2011:-9.0,2012:6.3,2013:18.8,2014:-11.7,2015:7.3,2016:14.5,2017:-2.4,2018:-11.8,2019:-9.7,2020:-29.1,2021:21.5
