# RUN 005 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## CoskewACX  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0062 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.6541 | >= 2.5 | FAIL |
| ic_half_min | -0.0011 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.7803 | >= 0.0 | PASS |
| coverage_pct | 91.1458 | >= 40.0 | PASS |
| avg_names_per_decile | 187.2 | >= 30 | PASS |
| ls_n_months | 264 | >= 237 | PASS |
stats: ic_mean=0.0062  ic_tstat_nw=1.6541  icir=0.0973  ic_half1_mean=-0.0011  ic_half2_mean=0.0135  ls_sharpe=0.1096  ls_ann_return_pct=1.2459  ls_ann_vol_pct=11.3646  ls_maxdd_pct=-36.7208  ls_hit_rate_pct=54.5455  turnover_d10_pct=28.2828  turnover_d1_pct=28.5277  coverage_pct=91.1458  avg_names_per_decile=187.2  n_months=264  ls_n_months=264  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2559  ls_beta_mean=0.1816  ls_beta_fullwindow=0.2181  ls_sharpe_ex_top_years=-0.1181  ls_top_years=2001,2002,2020  ls_sharpe_bear=0.6103  ls_sharpe_bull=-0.1170
deciles D1..D10 avg %/mo: 0.733,0.910,0.972,0.940,1.033,1.038,0.987,1.008,1.004,0.964
hedge/regime (diagnostics): beta ex-ante 0.1816 full-window 0.2181  raw Sharpe 0.2559  Sharpe ex top years -0.1181 (2001,2002,2020)  bear/bull 0.6103/-0.1170
ic decay: h1=0.0065  h2=0.0059  h3=0.0064  h6=0.0065  h12=0.0045
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0119 0.1094 0.2380 4.5400 382; MID 0.0036 0.0446 0.1640 2.2400 567; SMALL 0.0045 0.0744 0.3130 3.3300 922; ALL 0.0062 0.0973 0.2560 2.7800 1872
annual IC: 2000:-0.046 2001:+0.013 2002:+0.018 2003:+0.012 2004:-0.011 2005:+0.006 2006:+0.011 2007:+0.012 2008:-0.007 2009:-0.001 2010:-0.020 2011:-0.000 2012:+0.010 2013:+0.025 2014:+0.013 2015:+0.009 2016:+0.020 2017:+0.013 2018:-0.005 2019:+0.015 2020:+0.034 2021:+0.016

## Coskewness  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0068 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.6542 | >= 2.5 | FAIL |
| ic_half_min | -0.0001 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.6072 | >= 0.0 | PASS |
| coverage_pct | 91.1458 | >= 40.0 | PASS |
| avg_names_per_decile | 187.2 | >= 30 | PASS |
| ls_n_months | 264 | >= 237 | PASS |
stats: ic_mean=0.0068  ic_tstat_nw=1.6542  icir=0.1047  ic_half1_mean=-0.0001  ic_half2_mean=0.0137  ls_sharpe=-0.0452  ls_ann_return_pct=-0.5205  ls_ann_vol_pct=11.5233  ls_maxdd_pct=-40.7621  ls_hit_rate_pct=45.4545  turnover_d10_pct=15.5481  turnover_d1_pct=15.8787  coverage_pct=91.1458  avg_names_per_decile=187.2  n_months=264  ls_n_months=264  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1296  ls_beta_mean=0.2284  ls_beta_fullwindow=0.3325  ls_sharpe_ex_top_years=-0.2287  ls_top_years=2007,2009,2017  ls_sharpe_bear=0.4680  ls_sharpe_bull=-0.3015
deciles D1..D10 avg %/mo: 0.928,0.908,0.932,0.930,1.032,0.976,0.995,0.923,0.901,1.062
hedge/regime (diagnostics): beta ex-ante 0.2284 full-window 0.3325  raw Sharpe 0.1296  Sharpe ex top years -0.2287 (2007,2009,2017)  bear/bull 0.4680/-0.3015
ic decay: h1=0.0050  h2=0.0045  h3=0.0055  h6=0.0041  h12=0.0031
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0040 0.0377 -0.0580 -1.2100 382; MID 0.0034 0.0414 -0.1680 -2.5000 567; SMALL 0.0094 0.1566 0.4790 5.5900 922; ALL 0.0068 0.1047 0.1300 1.6100 1872
annual IC: 2000:-0.036 2001:-0.017 2002:-0.028 2003:+0.000 2004:-0.018 2005:+0.005 2006:+0.015 2007:+0.027 2008:+0.013 2009:+0.041 2010:-0.002 2011:+0.019 2012:+0.001 2013:+0.008 2014:-0.020 2015:+0.005 2016:+0.001 2017:+0.013 2018:-0.009 2019:+0.036 2020:+0.041 2021:+0.057

## DelCOA  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0009 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.2636 | >= 2.5 | FAIL |
| ic_half_min | -0.0055 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.9722 | >= 0.0 | PASS |
| coverage_pct | 77.2849 | >= 40.0 | PASS |
| avg_names_per_decile | 151.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0009  ic_tstat_nw=0.2636  icir=0.0179  ic_half1_mean=0.0074  ic_half2_mean=-0.0055  ls_sharpe=0.5835  ls_ann_return_pct=4.9125  ls_ann_vol_pct=8.4193  ls_maxdd_pct=-22.8059  ls_hit_rate_pct=55.4348  turnover_d10_pct=20.8843  turnover_d1_pct=18.0178  coverage_pct=77.2849  avg_names_per_decile=151.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6124  ls_beta_mean=-0.0458  ls_beta_fullwindow=-0.0660  ls_sharpe_ex_top_years=0.1953  ls_top_years=1999,2003,2021  ls_sharpe_bear=0.8049  ls_sharpe_bull=0.2676
deciles D1..D10 avg %/mo: 0.784,0.945,1.019,1.003,1.062,1.037,1.065,1.203,1.162,1.198
hedge/regime (diagnostics): beta ex-ante -0.0458 full-window -0.0660  raw Sharpe 0.6124  Sharpe ex top years 0.1953 (1999,2003,2021)  bear/bull 0.8049/0.2676
ic decay: h1=-0.0013  h2=-0.0002  h3=-0.0005  h6=-0.0027  h12=0.0004
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0036 -0.0409 0.2080 3.1700 324; MID -0.0000 -0.0002 0.3950 4.5300 470; SMALL 0.0021 0.0402 0.6040 5.9900 723; ALL 0.0009 0.0179 0.6120 4.9700 1518
annual IC: 1999:+0.027 2000:+0.021 2001:+0.030 2002:+0.005 2003:+0.013 2004:-0.011 2005:-0.001 2006:+0.005 2007:-0.047 2008:+0.028 2009:+0.011 2010:-0.007 2011:-0.011 2012:+0.002 2013:-0.015 2014:+0.007 2015:-0.007 2016:+0.015 2017:-0.025 2018:+0.010 2019:-0.020 2020:-0.026 2021:+0.017

## DelCOL  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0035 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.9185 | >= 2.5 | FAIL |
| ic_half_min | -0.0095 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 0.8062 | >= 0.0 | PASS |
| coverage_pct | 77.0973 | >= 40.0 | PASS |
| avg_names_per_decile | 151.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0035  ic_tstat_nw=-0.9185  icir=-0.0629  ic_half1_mean=0.0025  ic_half2_mean=-0.0095  ls_sharpe=0.0398  ls_ann_return_pct=0.3602  ls_ann_vol_pct=9.0577  ls_maxdd_pct=-48.1161  ls_hit_rate_pct=50.7246  turnover_d10_pct=22.1945  turnover_d1_pct=18.5838  coverage_pct=77.0973  avg_names_per_decile=151.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0904  ls_beta_mean=-0.0545  ls_beta_fullwindow=-0.0647  ls_sharpe_ex_top_years=-0.2868  ls_top_years=2003,2016,2021  ls_sharpe_bear=0.3089  ls_sharpe_bull=-0.1321
deciles D1..D10 avg %/mo: 0.997,1.006,0.996,1.061,1.076,0.974,1.088,1.067,1.118,1.064
hedge/regime (diagnostics): beta ex-ante -0.0545 full-window -0.0647  raw Sharpe 0.0904  Sharpe ex top years -0.2868 (2003,2016,2021)  bear/bull 0.3089/-0.1321
ic decay: h1=-0.0008  h2=-0.0004  h3=-0.0015  h6=0.0003  h12=-0.0012
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0062 -0.0639 0.0650 1.0800 323; MID -0.0033 -0.0465 0.1790 2.2400 469; SMALL -0.0033 -0.0573 0.0730 0.7300 722; ALL -0.0035 -0.0629 0.0900 0.8100 1514
annual IC: 1999:-0.001 2000:+0.022 2001:+0.030 2002:-0.014 2003:-0.005 2004:-0.023 2005:-0.015 2006:+0.015 2007:-0.038 2008:+0.033 2009:+0.020 2010:-0.003 2011:-0.023 2012:-0.008 2013:-0.017 2014:-0.010 2015:-0.014 2016:+0.034 2017:-0.034 2018:-0.009 2019:-0.002 2020:-0.022 2021:+0.006

## DelEqu  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0052 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.2465 | >= 2.5 | FAIL |
| ic_half_min | 0.0045 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 6.0551 | >= 0.0 | PASS |
| coverage_pct | 95.2338 | >= 40.0 | PASS |
| avg_names_per_decile | 187.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0052  ic_tstat_nw=1.2465  icir=0.0785  ic_half1_mean=0.0060  ic_half2_mean=0.0045  ls_sharpe=0.3334  ls_ann_return_pct=3.5337  ls_ann_vol_pct=10.6003  ls_maxdd_pct=-32.8957  ls_hit_rate_pct=55.7971  turnover_d10_pct=16.7431  turnover_d1_pct=15.2239  coverage_pct=95.2338  avg_names_per_decile=187.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.5804  ls_beta_mean=-0.0297  ls_beta_fullwindow=0.0024  ls_sharpe_ex_top_years=0.0083  ls_top_years=2000,2009,2021  ls_sharpe_bear=0.4584  ls_sharpe_bull=0.2618
deciles D1..D10 avg %/mo: 0.589,0.946,0.932,1.014,1.027,1.024,1.062,1.198,1.190,1.094
hedge/regime (diagnostics): beta ex-ante -0.0297 full-window 0.0024  raw Sharpe 0.5804  Sharpe ex top years 0.0083 (2000,2009,2021)  bear/bull 0.4584/0.2618
ic decay: h1=0.0064  h2=0.0066  h3=0.0058  h6=0.0046  h12=0.0033
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0090 0.0836 0.1740 3.0600 383; MID 0.0042 0.0536 0.2240 3.1100 565; SMALL 0.0032 0.0497 0.6560 7.4200 922; ALL 0.0052 0.0785 0.5800 6.0600 1871
annual IC: 1999:+0.008 2000:+0.042 2001:+0.038 2002:-0.022 2003:+0.007 2004:-0.018 2005:-0.010 2006:+0.019 2007:-0.044 2008:+0.016 2009:+0.027 2010:-0.000 2011:-0.007 2012:+0.016 2013:+0.013 2014:+0.012 2015:-0.007 2016:+0.022 2017:-0.012 2018:+0.013 2019:+0.003 2020:-0.028 2021:+0.033

## DelFINL  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0039 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.3588 | >= 2.5 | FAIL |
| ic_half_min | -0.0026 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.2638 | >= 0.0 | PASS |
| coverage_pct | 69.6221 | >= 40.0 | PASS |
| avg_names_per_decile | 136.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0039  ic_tstat_nw=1.3588  icir=0.0868  ic_half1_mean=0.0104  ic_half2_mean=-0.0026  ls_sharpe=0.4511  ls_ann_return_pct=3.5254  ls_ann_vol_pct=7.8147  ls_maxdd_pct=-25.9780  ls_hit_rate_pct=55.7971  turnover_d10_pct=19.2183  turnover_d1_pct=16.3645  coverage_pct=69.6221  avg_names_per_decile=136.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2775  ls_beta_mean=-0.1172  ls_beta_fullwindow=-0.1768  ls_sharpe_ex_top_years=0.1122  ls_top_years=2001,2003,2021  ls_sharpe_bear=0.4860  ls_sharpe_bull=0.4623
deciles D1..D10 avg %/mo: 0.856,0.874,0.967,1.023,1.055,1.107,1.035,1.208,1.113,1.045
hedge/regime (diagnostics): beta ex-ante -0.1172 full-window -0.1768  raw Sharpe 0.2775  Sharpe ex top years 0.1122 (2001,2003,2021)  bear/bull 0.4860/0.4623
ic decay: h1=0.0026  h2=0.0024  h3=0.0032  h6=0.0023  h12=0.0046
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0030 -0.0398 -0.1040 -1.3900 304; MID 0.0028 0.0456 0.1690 2.0000 429; SMALL 0.0057 0.1074 0.3210 3.0800 634; ALL 0.0039 0.0868 0.2770 2.2600 1367
annual IC: 1999:+0.017 2000:+0.012 2001:+0.026 2002:+0.040 2003:+0.011 2004:+0.009 2005:+0.002 2006:+0.010 2007:-0.002 2008:+0.008 2009:-0.013 2010:+0.007 2011:+0.003 2012:+0.014 2013:+0.003 2014:-0.007 2015:-0.011 2016:+0.003 2017:-0.019 2018:-0.006 2019:-0.018 2020:-0.038 2021:+0.041

## DelNetFin  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0025 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.0797 | >= 2.5 | FAIL |
| ic_half_min | -0.0024 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.0674 | >= 0.0 | PASS |
| coverage_pct | 77.1600 | >= 40.0 | PASS |
| avg_names_per_decile | 151.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0025  ic_tstat_nw=1.0797  icir=0.0668  ic_half1_mean=0.0074  ic_half2_mean=-0.0024  ls_sharpe=0.3169  ls_ann_return_pct=2.2208  ls_ann_vol_pct=7.0069  ls_maxdd_pct=-29.5357  ls_hit_rate_pct=49.6377  turnover_d10_pct=19.1090  turnover_d1_pct=17.4310  coverage_pct=77.1600  avg_names_per_decile=151.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1537  ls_beta_mean=0.0356  ls_beta_fullwindow=-0.0045  ls_sharpe_ex_top_years=-0.2372  ls_top_years=1999,2002,2021  ls_sharpe_bear=0.1384  ls_sharpe_bull=0.1221
deciles D1..D10 avg %/mo: 0.859,0.959,1.055,1.019,1.081,1.077,1.149,1.271,1.059,0.948
hedge/regime (diagnostics): beta ex-ante 0.0356 full-window -0.0045  raw Sharpe 0.1537  Sharpe ex top years -0.2372 (1999,2002,2021)  bear/bull 0.1384/0.1221
ic decay: h1=0.0013  h2=0.0013  h3=0.0010  h6=0.0014  h12=0.0011
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0028 -0.0406 -0.2580 -3.1600 324; MID 0.0031 0.0532 0.3310 3.6100 469; SMALL 0.0036 0.0784 0.1130 1.0500 721; ALL 0.0025 0.0668 0.1540 1.0700 1516
annual IC: 1999:+0.022 2000:-0.004 2001:+0.009 2002:+0.041 2003:+0.011 2004:+0.008 2005:-0.001 2006:-0.001 2007:+0.007 2008:+0.004 2009:-0.010 2010:+0.008 2011:+0.004 2012:+0.007 2013:+0.008 2014:+0.004 2015:-0.012 2016:-0.014 2017:-0.013 2018:-0.011 2019:-0.019 2020:-0.017 2021:+0.027

## DolVol  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0008 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.1825 | >= 2.5 | FAIL |
| ic_half_min | -0.0073 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.6866 | >= 0.0 | PASS |
| coverage_pct | 99.4628 | >= 40.0 | PASS |
| avg_names_per_decile | 195.4 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0008  ic_tstat_nw=-0.1825  icir=-0.0101  ic_half1_mean=0.0056  ic_half2_mean=-0.0073  ls_sharpe=0.1655  ls_ann_return_pct=1.6462  ls_ann_vol_pct=9.9498  ls_maxdd_pct=-36.7529  ls_hit_rate_pct=53.9855  turnover_d10_pct=50.5376  turnover_d1_pct=14.5788  coverage_pct=99.4628  avg_names_per_decile=195.4  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3637  ls_beta_mean=0.0151  ls_beta_fullwindow=-0.0115  ls_sharpe_ex_top_years=-0.1194  ls_top_years=2000,2001,2003  ls_sharpe_bear=0.6579  ls_sharpe_bull=0.0103
deciles D1..D10 avg %/mo: 0.820,0.929,0.868,0.871,1.006,0.967,0.972,1.058,1.034,1.127
hedge/regime (diagnostics): beta ex-ante 0.0151 full-window -0.0115  raw Sharpe 0.3637  Sharpe ex top years -0.1194 (2000,2001,2003)  bear/bull 0.6579/0.0103
ic decay: h1=0.0003  h2=0.0010  h3=0.0025  h6=0.0031  h12=0.0028
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0020 -0.0254 0.2540 3.4400 392; MID -0.0085 -0.1067 -0.1260 -2.1100 586; SMALL -0.0008 -0.0158 0.0650 0.7100 975; ALL -0.0008 -0.0101 0.3640 3.6900 1954
annual IC: 1999:-0.012 2000:+0.003 2001:+0.050 2002:+0.021 2003:+0.008 2004:+0.004 2005:-0.012 2006:+0.004 2007:-0.034 2008:+0.036 2009:-0.018 2010:+0.018 2011:+0.004 2012:-0.006 2013:+0.011 2014:-0.034 2015:-0.008 2016:+0.026 2017:-0.020 2018:-0.014 2019:-0.012 2020:-0.016 2021:-0.018

## EBM  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0018 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.4170 | >= 2.5 | FAIL |
| ic_half_min | -0.0088 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.2204 | >= 0.0 | PASS |
| coverage_pct | 75.6276 | >= 40.0 | PASS |
| avg_names_per_decile | 148.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0018  ic_tstat_nw=0.4170  icir=0.0256  ic_half1_mean=0.0125  ic_half2_mean=-0.0088  ls_sharpe=0.0318  ls_ann_return_pct=0.2997  ls_ann_vol_pct=9.4351  ls_maxdd_pct=-43.7731  ls_hit_rate_pct=45.2899  turnover_d10_pct=18.8002  turnover_d1_pct=17.5879  coverage_pct=75.6276  avg_names_per_decile=148.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3199  ls_beta_mean=0.2044  ls_beta_fullwindow=0.2362  ls_sharpe_ex_top_years=-0.3308  ls_top_years=1999,2001,2009  ls_sharpe_bear=0.6996  ls_sharpe_bull=-0.4809
deciles D1..D10 avg %/mo: 0.925,0.774,0.960,0.907,1.038,0.965,0.978,0.938,1.070,1.193
hedge/regime (diagnostics): beta ex-ante 0.2044 full-window 0.2362  raw Sharpe 0.3199  Sharpe ex top years -0.3308 (1999,2001,2009)  bear/bull 0.6996/-0.4809
ic decay: h1=-0.0002  h2=-0.0013  h3=0.0002  h6=-0.0016  h12=0.0011
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0003 -0.0035 -0.0640 -0.8000 321; MID 0.0032 0.0373 0.3650 4.7200 454; SMALL 0.0017 0.0235 0.0840 0.9200 709; ALL 0.0018 0.0256 0.3200 3.2200 1485
annual IC: 1999:+0.020 2000:+0.016 2001:+0.035 2002:-0.013 2003:+0.035 2004:+0.013 2005:+0.008 2006:+0.011 2007:-0.030 2008:+0.022 2009:+0.035 2010:+0.005 2011:-0.024 2012:-0.004 2013:-0.015 2014:-0.007 2015:-0.031 2016:+0.018 2017:-0.007 2018:-0.020 2019:-0.011 2020:-0.012 2021:-0.005

## EP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0055 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.9575 | >= 2.5 | FAIL |
| ic_half_min | -0.0026 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.5261 | >= 0.0 | PASS |
| coverage_pct | 75.0862 | >= 40.0 | PASS |
| avg_names_per_decile | 147.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0055  ic_tstat_nw=0.9575  icir=0.0691  ic_half1_mean=0.0135  ic_half2_mean=-0.0026  ls_sharpe=0.1696  ls_ann_return_pct=1.7574  ls_ann_vol_pct=10.3628  ls_maxdd_pct=-37.9298  ls_hit_rate_pct=51.0870  turnover_d10_pct=19.4670  turnover_d1_pct=22.2246  coverage_pct=75.0862  avg_names_per_decile=147.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3327  ls_beta_mean=-0.0735  ls_beta_fullwindow=-0.0531  ls_sharpe_ex_top_years=-0.1203  ls_top_years=2003,2009,2021  ls_sharpe_bear=0.6164  ls_sharpe_bull=0.0395
deciles D1..D10 avg %/mo: 0.876,0.959,1.031,1.018,1.058,1.020,1.074,1.134,1.148,1.170
hedge/regime (diagnostics): beta ex-ante -0.0735 full-window -0.0531  raw Sharpe 0.3327  Sharpe ex top years -0.1203 (2003,2009,2021)  bear/bull 0.6164/0.0395
ic decay: h1=0.0047  h2=0.0043  h3=0.0052  h6=0.0063  h12=0.0049
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0067 0.0549 0.2000 3.2200 328; MID 0.0015 0.0153 0.4300 5.7200 449; SMALL 0.0052 0.0738 0.1660 1.6100 697; ALL 0.0055 0.0691 0.3330 3.5300 1475
annual IC: 1999:-0.021 2000:+0.031 2001:+0.050 2002:+0.025 2003:+0.027 2004:+0.031 2005:-0.012 2006:+0.004 2007:-0.045 2008:+0.024 2009:+0.039 2010:-0.017 2011:+0.006 2012:-0.008 2013:+0.006 2014:+0.014 2015:-0.031 2016:+0.031 2017:-0.026 2018:-0.034 2019:+0.010 2020:-0.026 2021:+0.047

## EarningsConsistency  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0090 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.5958 | >= 2.5 | PASS |
| ic_half_min | 0.0055 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | -0.1250 | >= 0.0 | FAIL |
| coverage_pct | 43.3429 | >= 40.0 | PASS |
| avg_names_per_decile | 85.1598 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0090  ic_tstat_nw=2.5958  icir=0.1565  ic_half1_mean=0.0055  ic_half2_mean=0.0125  ls_sharpe=0.3378  ls_ann_return_pct=2.9214  ls_ann_vol_pct=8.6484  ls_maxdd_pct=-24.6061  ls_hit_rate_pct=57.6087  turnover_d10_pct=10.9532  turnover_d1_pct=12.9721  coverage_pct=43.3429  avg_names_per_decile=85.1598  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0139  ls_beta_mean=-0.1615  ls_beta_fullwindow=-0.1848  ls_sharpe_ex_top_years=0.1828  ls_top_years=2001,2002,2014  ls_sharpe_bear=-0.2057  ls_sharpe_bull=0.6283
deciles D1..D10 avg %/mo: 1.132,0.970,1.061,0.917,0.962,1.026,0.934,1.105,1.157,1.122
hedge/regime (diagnostics): beta ex-ante -0.1615 full-window -0.1848  raw Sharpe -0.0139  Sharpe ex top years 0.1828 (2001,2002,2014)  bear/bull -0.2057/0.6283
ic decay: h1=0.0083  h2=0.0097  h3=0.0086  h6=0.0079  h12=0.0069
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0057 0.0555 0.1460 2.0700 190; MID 0.0055 0.0732 0.2090 2.4800 262; SMALL 0.0113 0.1628 -0.1450 -1.9000 399; ALL 0.0090 0.1565 -0.0140 -0.1300 851
annual IC: 1999:+0.015 2000:-0.008 2001:+0.005 2002:+0.009 2003:+0.009 2004:+0.015 2005:+0.020 2006:-0.009 2007:+0.023 2008:-0.025 2009:+0.002 2010:+0.002 2011:+0.050 2012:-0.002 2013:+0.008 2014:+0.003 2015:+0.013 2016:-0.008 2017:+0.025 2018:-0.019 2019:+0.021 2020:+0.025 2021:+0.033

## EarningsSurprise  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0048 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.6324 | >= 2.5 | FAIL |
| ic_half_min | 0.0023 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.3313 | >= 0.0 | PASS |
| coverage_pct | 86.1819 | >= 40.0 | PASS |
| avg_names_per_decile | 169.3 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0048  ic_tstat_nw=1.6324  icir=0.1037  ic_half1_mean=0.0023  ic_half2_mean=0.0072  ls_sharpe=0.3240  ls_ann_return_pct=2.3169  ls_ann_vol_pct=7.1513  ls_maxdd_pct=-29.4083  ls_hit_rate_pct=59.7826  turnover_d10_pct=33.9500  turnover_d1_pct=33.7831  coverage_pct=86.1819  avg_names_per_decile=169.3  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1898  ls_beta_mean=-0.0658  ls_beta_fullwindow=-0.0918  ls_sharpe_ex_top_years=0.0515  ls_top_years=2000,2003,2007  ls_sharpe_bear=-0.3989  ls_sharpe_bull=0.6766
deciles D1..D10 avg %/mo: 0.961,1.070,0.996,1.042,1.066,0.987,1.033,1.021,1.044,1.072
hedge/regime (diagnostics): beta ex-ante -0.0658 full-window -0.0918  raw Sharpe 0.1898  Sharpe ex top years 0.0515 (2000,2003,2007)  bear/bull -0.3989/0.6766
ic decay: h1=-0.0003  h2=0.0023  h3=0.0042  h6=-0.0013  h12=-0.0006
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0073 0.0969 0.2710 3.1500 357; MID 0.0065 0.1015 0.2840 2.8400 516; SMALL 0.0016 0.0319 0.0240 0.2000 819; ALL 0.0048 0.1037 0.1900 1.3300 1693
annual IC: 1999:+0.002 2000:+0.013 2001:-0.019 2002:+0.012 2003:+0.008 2004:+0.007 2005:+0.007 2006:-0.005 2007:+0.045 2008:+0.001 2009:-0.035 2010:-0.005 2011:+0.023 2012:+0.016 2013:+0.006 2014:+0.009 2015:+0.017 2016:-0.005 2017:+0.016 2018:+0.013 2019:-0.027 2020:-0.014 2021:+0.024
