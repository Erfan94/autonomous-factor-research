# RUN 022 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE d27916e567f2 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v5: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9141  ls_ann_return_pct=11.5584  ls_ann_vol_pct=12.6443  ls_maxdd_pct=-47.7533  ls_hit_rate_pct=64.4928  n_months=276  worst_12m_pct=-36.6301  turnover_long_pct=25.0179  turnover_short_pct=22.3389  construction_weights=family blend  ls_raw_sharpe=0.8082  ls_beta_mean=-0.2975  ls_beta_fullwindow=-0.3445  ls_sharpe_ex_top_years=0.4789  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1271  ls_sharpe_bull=0.8731
hedge/regime (diagnostics): beta ex-ante -0.2975 full-window -0.3445  raw Sharpe 0.8082  Sharpe ex top years 0.4789 (2000,2001,2021)  bear/bull 1.1271/0.8731
annual LS %: 1999:5.8,2000:86.3,2001:54.3,2002:29.1,2003:32.1,2004:14.6,2005:17.7,2006:14.4,2007:-7.3,2008:13.9,2009:-6.9,2010:13.9,2011:7.0,2012:3.2,2013:4.3,2014:-5.0,2015:4.9,2016:19.4,2017:-0.4,2018:-0.1,2019:-10.6,2020:-36.6,2021:70.7

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8607  ls_ann_return_pct=11.3511  ls_ann_vol_pct=13.1875  ls_maxdd_pct=-50.8391  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-41.7052  turnover_long_pct=27.6998  turnover_short_pct=24.1847  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.7125  ls_beta_mean=-0.3229  ls_beta_fullwindow=-0.3901  ls_sharpe_ex_top_years=0.4407  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8302  ls_sharpe_bull=0.8711
hedge/regime (diagnostics): beta ex-ante -0.3229 full-window -0.3901  raw Sharpe 0.7125  Sharpe ex top years 0.4407 (2000,2001,2021)  bear/bull 0.8302/0.8711
annual LS %: 1999:9.0,2000:110.1,2001:32.0,2002:28.3,2003:24.9,2004:12.0,2005:19.6,2006:10.5,2007:-3.8,2008:12.8,2009:-7.1,2010:11.0,2011:5.9,2012:5.4,2013:9.7,2014:-3.7,2015:0.5,2016:18.2,2017:3.8,2018:-1.9,2019:-8.7,2020:-41.7,2021:82.0

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.9259  ls_ann_return_pct=10.9331  ls_ann_vol_pct=11.8086  ls_maxdd_pct=-33.7216  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-28.8547  turnover_long_pct=21.6833  turnover_short_pct=21.7725  construction_weights=Size=0.015;Value=0.045;Profitability=0.134;Investment=0.045;Momentum=0.077;PctAcc=0.140;CBOperProf=0.132;ShareIss5Y=0.162;cfp=0.130;XFIN=0.120  ls_raw_sharpe=0.5595  ls_beta_mean=-0.4759  ls_beta_fullwindow=-0.5474  ls_sharpe_ex_top_years=0.5580  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9811  ls_sharpe_bull=1.0068
hedge/regime (diagnostics): beta ex-ante -0.4759 full-window -0.5474  raw Sharpe 0.5595  Sharpe ex top years 0.5580 (2000,2001,2021)  bear/bull 0.9811/1.0068
annual LS %: 1999:-5.0,2000:69.4,2001:23.8,2002:20.3,2003:19.9,2004:15.8,2005:13.4,2006:13.3,2007:5.9,2008:4.6,2009:6.0,2010:8.6,2011:7.7,2012:1.7,2013:11.4,2014:3.0,2015:1.2,2016:6.8,2017:6.6,2018:7.1,2019:-6.0,2020:-26.4,2021:79.1

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8303  ls_ann_return_pct=9.3031  ls_ann_vol_pct=11.2041  ls_maxdd_pct=-44.4906  ls_hit_rate_pct=59.7826  n_months=276  worst_12m_pct=-33.2859  turnover_long_pct=13.2401  turnover_short_pct=10.5978  construction_weights=buffer 20%  ls_raw_sharpe=0.7114  ls_beta_mean=-0.2801  ls_beta_fullwindow=-0.3299  ls_sharpe_ex_top_years=0.4048  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9999  ls_sharpe_bull=0.7961
hedge/regime (diagnostics): beta ex-ante -0.2801 full-window -0.3299  raw Sharpe 0.7114  Sharpe ex top years 0.4048 (2000,2001,2021)  bear/bull 0.9999/0.7961
annual LS %: 1999:5.4,2000:81.5,2001:36.8,2002:25.6,2003:28.6,2004:11.6,2005:14.9,2006:8.2,2007:-9.3,2008:14.3,2009:-7.0,2010:11.1,2011:7.0,2012:3.4,2013:4.4,2014:-4.7,2015:1.7,2016:17.0,2017:-3.0,2018:0.1,2019:-10.6,2020:-33.3,2021:53.6

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6532  ls_ann_return_pct=7.6679  ls_ann_vol_pct=11.7396  ls_maxdd_pct=-47.3123  ls_hit_rate_pct=62.3188  n_months=276  worst_12m_pct=-32.5557  turnover_long_pct=25.0179  turnover_short_pct=22.3389  construction_weights=target 10% vol, cap 3.0x, mean lev 1.12  ls_raw_sharpe=0.6398  ls_beta_mean=-0.2003  ls_beta_fullwindow=-0.1916  ls_sharpe_ex_top_years=0.3946  ls_top_years=2000,2006,2021  ls_sharpe_bear=0.6367  ls_sharpe_bull=0.6676
hedge/regime (diagnostics): beta ex-ante -0.2003 full-window -0.1916  raw Sharpe 0.6398  Sharpe ex top years 0.3946 (2000,2006,2021)  bear/bull 0.6367/0.6676
annual LS %: 1999:5.8,2000:27.6,2001:17.6,2002:13.2,2003:13.3,2004:15.2,2005:23.2,2006:30.3,2007:-13.9,2008:11.8,2009:-5.2,2010:13.5,2011:7.3,2012:2.5,2013:11.4,2014:-8.3,2015:7.7,2016:22.8,2017:2.4,2018:-0.8,2019:-9.5,2020:-32.6,2021:37.8
