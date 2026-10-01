# RUN 044 BATCH stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 7fe6f001e708 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v14: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal, zerotrade6M, VolumeTrend, TrendFactor

## BidAskSpreadFlip  (stage 2)  → **FAIL**
rung 1 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend,TrendFactor  | base IC 0.0389 Sharpe 0.983 ann ret 16.12% MaxDD -43.2
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.7692 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.4268 | >= -2.0 | PASS |
stats: ic_mean=0.0398  ic_tstat_nw=5.6192  icir=0.3825  ic_half1_mean=0.0510  ic_half2_mean=0.0286  ls_sharpe=0.9514  ls_ann_return_pct=16.3246  ls_ann_vol_pct=17.1590  ls_maxdd_pct=-41.3794  ls_hit_rate_pct=63.7681  turnover_d10_pct=59.0442  turnover_d1_pct=55.1396  coverage_pct=99.1272  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3867  resid_ic_mean=0.0051  resid_ic_tstat_nw=1.7692  spanning_alpha_ann_pct=-2.5205  spanning_alpha_tstat_nw=-0.7293  spanning_r2=0.4044  corr_to_composite=0.6359  paired_delta_ic_mean=0.0009  paired_delta_ic_tstat=1.8304  paired_delta_ls_mean=0.0002  paired_delta_ls_tstat=0.4268  delta_ls_sharpe=-0.0312  maxdd_worsening_pct=-1.8349  ls_raw_sharpe=0.7189  ls_beta_mean=-0.5915  ls_beta_fullwindow=-0.6168  ls_sharpe_ex_top_years=0.6430  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1366  ls_sharpe_bull=1.1088
deciles D1..D10 avg %/mo: 0.277,0.557,0.748,0.818,0.987,1.064,1.141,1.300,1.299,1.479
hedge/regime (diagnostics): beta ex-ante -0.5915 full-window -0.6168  raw Sharpe 0.7189  Sharpe ex top years 0.6430 (2000,2001,2021)  bear/bull 1.1366/1.1088
ic decay: h1=0.0274  h2=0.0230  h3=0.0251  h6=0.0196  h12=0.0235
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0342 0.2364 0.3610 9.2200 393; MID 0.0348 0.3092 0.5420 11.9600 589; SMALL 0.0423 0.4309 0.8420 15.8200 981; ALL 0.0398 0.3825 0.7190 14.4200 1964
annual IC: 1999:+0.020 2000:+0.130 2001:+0.109 2002:+0.120 2003:-0.001 2004:+0.042 2005:+0.028 2006:+0.040 2007:-0.015 2008:+0.081 2009:+0.001 2010:+0.031 2011:+0.059 2012:+0.019 2013:+0.018 2014:+0.043 2015:+0.040 2016:+0.030 2017:-0.000 2018:+0.043 2019:+0.010 2020:-0.049 2021:+0.118

## IdioVolAHT  (stage 2)  → **FAIL**
rung 2 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend,TrendFactor  | base IC 0.0389 Sharpe 0.983 ann ret 16.12% MaxDD -43.2
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.9235 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.0617 | >= -2.0 | PASS |
stats: ic_mean=0.0392  ic_tstat_nw=5.5822  icir=0.3811  ic_half1_mean=0.0497  ic_half2_mean=0.0287  ls_sharpe=0.9667  ls_ann_return_pct=16.1426  ls_ann_vol_pct=16.6983  ls_maxdd_pct=-44.4599  ls_hit_rate_pct=61.5942  turnover_d10_pct=55.7946  turnover_d1_pct=51.2507  coverage_pct=96.7563  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=0.0073  resid_ic_tstat_nw=1.9235  spanning_alpha_ann_pct=-2.8360  spanning_alpha_tstat_nw=-0.6947  spanning_r2=0.4037  corr_to_composite=0.6354  paired_delta_ic_mean=0.0002  paired_delta_ic_tstat=0.7123  paired_delta_ls_mean=0.0000  paired_delta_ls_tstat=0.0617  delta_ls_sharpe=-0.0158  maxdd_worsening_pct=1.2455  ls_raw_sharpe=0.7558  ls_beta_mean=-0.5632  ls_beta_fullwindow=-0.5846  ls_sharpe_ex_top_years=0.6300  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2144  ls_sharpe_bull=1.1089
deciles D1..D10 avg %/mo: 0.284,0.512,0.756,0.819,1.043,1.065,1.115,1.233,1.339,1.504
hedge/regime (diagnostics): beta ex-ante -0.5632 full-window -0.5846  raw Sharpe 0.7558  Sharpe ex top years 0.6300 (2000,2001,2021)  bear/bull 1.2144/1.1089
ic decay: h1=0.0275  h2=0.0234  h3=0.0255  h6=0.0202  h12=0.0239
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0334 0.2272 0.3040 7.8900 393; MID 0.0352 0.3163 0.5850 12.4900 589; SMALL 0.0413 0.4323 0.8760 16.0400 981; ALL 0.0392 0.3811 0.7560 14.6400 1964
annual IC: 1999:+0.016 2000:+0.126 2001:+0.109 2002:+0.119 2003:-0.002 2004:+0.041 2005:+0.025 2006:+0.041 2007:-0.016 2008:+0.082 2009:+0.002 2010:+0.032 2011:+0.061 2012:+0.018 2013:+0.019 2014:+0.042 2015:+0.042 2016:+0.032 2017:+0.001 2018:+0.040 2019:+0.009 2020:-0.052 2021:+0.116

## zerotrade1M  (stage 2)  → **FAIL**
rung 3 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend,TrendFactor  | base IC 0.0389 Sharpe 0.983 ann ret 16.12% MaxDD -43.2
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | -1.2781 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.1143 | >= -2.0 | PASS |
stats: ic_mean=0.0388  ic_tstat_nw=5.6517  icir=0.3841  ic_half1_mean=0.0498  ic_half2_mean=0.0279  ls_sharpe=0.9863  ls_ann_return_pct=16.1699  ls_ann_vol_pct=16.3942  ls_maxdd_pct=-41.0665  ls_hit_rate_pct=62.6812  turnover_d10_pct=58.5562  turnover_d1_pct=54.2469  coverage_pct=99.3756  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=-0.0025  resid_ic_tstat_nw=-1.2781  spanning_alpha_ann_pct=-2.3915  spanning_alpha_tstat_nw=-0.7372  spanning_r2=0.3662  corr_to_composite=0.6052  paired_delta_ic_mean=-0.0001  paired_delta_ic_tstat=-0.3622  paired_delta_ls_mean=0.0000  paired_delta_ls_tstat=0.1143  delta_ls_sharpe=0.0038  maxdd_worsening_pct=-2.1479  ls_raw_sharpe=0.7663  ls_beta_mean=-0.5565  ls_beta_fullwindow=-0.5784  ls_sharpe_ex_top_years=0.6990  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2566  ls_sharpe_bull=1.1034
deciles D1..D10 avg %/mo: 0.263,0.600,0.772,0.776,0.982,1.055,1.114,1.272,1.356,1.479
hedge/regime (diagnostics): beta ex-ante -0.5565 full-window -0.5784  raw Sharpe 0.7663  Sharpe ex top years 0.6990 (2000,2001,2021)  bear/bull 1.2566/1.1034
ic decay: h1=0.0266  h2=0.0225  h3=0.0246  h6=0.0197  h12=0.0235
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0335 0.2265 0.3140 8.0600 393; MID 0.0349 0.3168 0.6160 12.9100 589; SMALL 0.0410 0.4394 0.9000 15.9800 981; ALL 0.0388 0.3841 0.7660 14.5900 1964
annual IC: 1999:+0.020 2000:+0.119 2001:+0.110 2002:+0.119 2003:-0.001 2004:+0.042 2005:+0.027 2006:+0.041 2007:-0.016 2008:+0.082 2009:+0.001 2010:+0.030 2011:+0.059 2012:+0.020 2013:+0.019 2014:+0.040 2015:+0.041 2016:+0.030 2017:-0.000 2018:+0.042 2019:+0.009 2020:-0.050 2021:+0.111

## NetPayoutYield  (stage 2)  → **FAIL**
rung 4 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend,TrendFactor  | base IC 0.0389 Sharpe 0.983 ann ret 16.12% MaxDD -43.2
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 0.1165 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.0604 | >= -2.0 | PASS |
stats: ic_mean=0.0387  ic_tstat_nw=5.6124  icir=0.3800  ic_half1_mean=0.0485  ic_half2_mean=0.0289  ls_sharpe=0.9822  ls_ann_return_pct=16.1485  ls_ann_vol_pct=16.4413  ls_maxdd_pct=-42.9245  ls_hit_rate_pct=64.8551  turnover_d10_pct=57.3844  turnover_d1_pct=54.0442  coverage_pct=65.5130  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=44.3799  resid_ic_mean=0.0003  resid_ic_tstat_nw=0.1165  spanning_alpha_ann_pct=-2.4779  spanning_alpha_tstat_nw=-1.0486  spanning_r2=0.4161  corr_to_composite=0.6451  paired_delta_ic_mean=-0.0003  paired_delta_ic_tstat=-0.5626  paired_delta_ls_mean=0.0000  paired_delta_ls_tstat=0.0604  delta_ls_sharpe=-0.0004  maxdd_worsening_pct=-0.2898  ls_raw_sharpe=0.7412  ls_beta_mean=-0.5657  ls_beta_fullwindow=-0.5928  ls_sharpe_ex_top_years=0.6742  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1164  ls_sharpe_bull=1.1483
deciles D1..D10 avg %/mo: 0.285,0.545,0.767,0.787,1.076,1.070,1.082,1.236,1.352,1.468
hedge/regime (diagnostics): beta ex-ante -0.5657 full-window -0.5928  raw Sharpe 0.7412  Sharpe ex top years 0.6742 (2000,2001,2021)  bear/bull 1.1164/1.1483
ic decay: h1=0.0269  h2=0.0228  h3=0.0248  h6=0.0198  h12=0.0236
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0342 0.2338 0.2700 7.1100 393; MID 0.0350 0.3160 0.5890 12.5200 589; SMALL 0.0404 0.4283 0.9020 15.9100 981; ALL 0.0387 0.3800 0.7410 14.1900 1964
annual IC: 1999:+0.018 2000:+0.121 2001:+0.105 2002:+0.117 2003:-0.004 2004:+0.039 2005:+0.024 2006:+0.038 2007:-0.013 2008:+0.081 2009:+0.001 2010:+0.031 2011:+0.062 2012:+0.018 2013:+0.018 2014:+0.040 2015:+0.043 2016:+0.029 2017:+0.003 2018:+0.044 2019:+0.008 2020:-0.049 2021:+0.114
