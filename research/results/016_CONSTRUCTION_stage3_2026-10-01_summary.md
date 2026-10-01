# RUN 016 CONSTRUCTION stage 3

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 8b444636f0a1 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v2: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf

## equal_rank_decile  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6606  ls_ann_return_pct=7.8213  ls_ann_vol_pct=11.8406  ls_maxdd_pct=-37.0655  ls_hit_rate_pct=55.7971  n_months=276  worst_12m_pct=-27.9255  turnover_long_pct=27.9507  turnover_short_pct=24.4075  construction_weights=family blend  ls_raw_sharpe=0.7770  ls_beta_mean=-0.0631  ls_beta_fullwindow=-0.1220  ls_sharpe_ex_top_years=0.2490  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9231  ls_sharpe_bull=0.5730
hedge/regime (diagnostics): beta ex-ante -0.0631 full-window -0.1220  raw Sharpe 0.7770  Sharpe ex top years 0.2490 (2000,2001,2021)  bear/bull 0.9231/0.5730
annual LS %: 1999:6.9,2000:60.1,2001:60.9,2002:22.7,2003:32.5,2004:12.1,2005:10.6,2006:3.1,2007:-16.9,2008:17.0,2009:-12.1,2010:20.0,2011:-4.7,2012:5.9,2013:-0.6,2014:-8.4,2015:3.3,2016:8.3,2017:0.2,2018:-5.2,2019:-7.8,2020:-26.9,2021:32.9

## tier_neutral  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6925  ls_ann_return_pct=8.2801  ls_ann_vol_pct=11.9571  ls_maxdd_pct=-43.4995  ls_hit_rate_pct=56.8841  n_months=276  worst_12m_pct=-30.4419  turnover_long_pct=31.8830  turnover_short_pct=29.5263  construction_weights=family blend, tier-neutral  ls_raw_sharpe=0.7143  ls_beta_mean=-0.1309  ls_beta_fullwindow=-0.2036  ls_sharpe_ex_top_years=0.2403  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.7741  ls_sharpe_bull=0.6096
hedge/regime (diagnostics): beta ex-ante -0.1309 full-window -0.2036  raw Sharpe 0.7143  Sharpe ex top years 0.2403 (2000,2001,2021)  bear/bull 0.7741/0.6096
annual LS %: 1999:18.3,2000:69.9,2001:44.0,2002:16.6,2003:28.0,2004:10.6,2005:11.1,2006:-1.2,2007:-13.0,2008:17.5,2009:-13.4,2010:15.0,2011:-1.5,2012:8.7,2013:3.3,2014:-6.4,2015:-2.1,2016:13.5,2017:0.6,2018:-7.0,2019:-11.8,2020:-30.4,2021:61.8

## icir_weighted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.8131  ls_ann_return_pct=9.6530  ls_ann_vol_pct=11.8725  ls_maxdd_pct=-25.0954  ls_hit_rate_pct=61.9565  n_months=276  worst_12m_pct=-25.0954  turnover_long_pct=24.7160  turnover_short_pct=25.6314  construction_weights=Size=0.024;Value=0.074;Profitability=0.238;Investment=0.076;Momentum=0.133;PctAcc=0.229;CBOperProf=0.228  ls_raw_sharpe=0.4985  ls_beta_mean=-0.3716  ls_beta_fullwindow=-0.4660  ls_sharpe_ex_top_years=0.4622  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.7680  ls_sharpe_bull=0.9081
hedge/regime (diagnostics): beta ex-ante -0.3716 full-window -0.4660  raw Sharpe 0.4985  Sharpe ex top years 0.4622 (2000,2003,2021)  bear/bull 0.7680/0.9081
annual LS %: 1999:-1.0,2000:52.6,2001:21.2,2002:19.4,2003:27.9,2004:16.0,2005:13.8,2006:6.7,2007:19.0,2008:4.1,2009:-3.4,2010:10.5,2011:-7.1,2012:-7.8,2013:12.4,2014:-0.7,2015:6.3,2016:-3.6,2017:7.3,2018:7.2,2019:-2.8,2020:-14.5,2021:59.4

## buffered  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.6319  ls_ann_return_pct=6.8042  ls_ann_vol_pct=10.7672  ls_maxdd_pct=-41.5353  ls_hit_rate_pct=55.7971  n_months=276  worst_12m_pct=-26.6803  turnover_long_pct=14.9973  turnover_short_pct=11.0920  construction_weights=buffer 20%  ls_raw_sharpe=0.7455  ls_beta_mean=-0.0627  ls_beta_fullwindow=-0.1186  ls_sharpe_ex_top_years=0.1993  ls_top_years=2000,2001,2003  ls_sharpe_bear=0.9873  ls_sharpe_bull=0.5128
hedge/regime (diagnostics): beta ex-ante -0.0627 full-window -0.1186  raw Sharpe 0.7455  Sharpe ex top years 0.1993 (2000,2001,2003)  bear/bull 0.9873/0.5128
annual LS %: 1999:4.7,2000:55.4,2001:50.1,2002:21.7,2003:33.5,2004:12.2,2005:10.2,2006:0.0,2007:-17.5,2008:17.8,2009:-8.9,2010:15.2,2011:1.3,2012:2.4,2013:-0.1,2014:-6.3,2015:-1.1,2016:9.3,2017:-5.1,2018:-5.2,2019:-9.2,2020:-26.7,2021:32.9

## vol_targeted  (stage 3)  → **REPORTED**
stats: ls_sharpe=0.3777  ls_ann_return_pct=4.4546  ls_ann_vol_pct=11.7935  ls_maxdd_pct=-41.7506  ls_hit_rate_pct=55.4348  n_months=276  worst_12m_pct=-27.4804  turnover_long_pct=27.9507  turnover_short_pct=24.4075  construction_weights=target 10% vol, cap 3.0x, mean lev 1.20  ls_raw_sharpe=0.5429  ls_beta_mean=0.0341  ls_beta_fullwindow=-0.0157  ls_sharpe_ex_top_years=0.1527  ls_top_years=2000,2001,2008  ls_sharpe_bear=0.6104  ls_sharpe_bull=0.2915
hedge/regime (diagnostics): beta ex-ante 0.0341 full-window -0.0157  raw Sharpe 0.5429  Sharpe ex top years 0.1527 (2000,2001,2008)  bear/bull 0.6104/0.2915
annual LS %: 1999:8.0,2000:23.9,2001:26.6,2002:11.6,2003:20.4,2004:11.5,2005:13.7,2006:6.6,2007:-26.8,2008:21.2,2009:-9.9,2010:17.8,2011:-10.9,2012:8.0,2013:11.8,2014:-13.1,2015:7.2,2016:11.0,2017:1.0,2018:-10.3,2019:-8.4,2020:-26.6,2021:21.1
