# RUN 004 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## CF  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0201 | >= 0.01 | PASS |
| ic_tstat_nw | 3.0279 | >= 2.5 | PASS |
| ic_half_min | 0.0070 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.3158 | >= 0.0 | PASS |
| coverage_pct | 96.0589 | >= 40.0 | PASS |
| avg_names_per_decile | 188.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0201  ic_tstat_nw=3.0279  icir=0.2125  ic_half1_mean=0.0331  ic_half2_mean=0.0070  ls_sharpe=0.1787  ls_ann_return_pct=2.7465  ls_ann_vol_pct=15.3709  ls_maxdd_pct=-64.1643  ls_hit_rate_pct=53.2609  turnover_d10_pct=16.9678  turnover_d1_pct=16.3589  coverage_pct=96.0589  avg_names_per_decile=188.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2014  ls_beta_mean=-0.2758  ls_beta_fullwindow=-0.2890  ls_sharpe_ex_top_years=-0.1690  ls_top_years=2000,2001,2002  ls_sharpe_bear=0.5178  ls_sharpe_bull=0.1764
deciles D1..D10 avg %/mo: 0.944,0.862,0.821,0.912,0.799,0.967,1.011,1.106,1.238,1.220
hedge/regime (diagnostics): beta ex-ante -0.2758 full-window -0.2890  raw Sharpe 0.2014  Sharpe ex top years -0.1690 (2000,2001,2002)  bear/bull 0.5178/0.1764
ic decay: h1=0.0155  h2=0.0146  h3=0.0154  h6=0.0143  h12=0.0155
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0178 0.1480 0.1570 3.1900 385; MID 0.0157 0.1442 0.2840 5.3500 569; SMALL 0.0223 0.2463 0.1890 3.3100 932; ALL 0.0201 0.2125 0.2010 3.3200 1887
annual IC: 1999:-0.017 2000:+0.095 2001:+0.090 2002:+0.085 2003:+0.017 2004:+0.046 2005:+0.019 2006:+0.031 2007:-0.039 2008:+0.033 2009:+0.017 2010:+0.001 2011:+0.008 2012:+0.008 2013:+0.009 2014:+0.040 2015:-0.014 2016:+0.038 2017:-0.019 2018:-0.024 2019:+0.007 2020:-0.060 2021:+0.089

## Cash  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0091 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.8574 | >= 2.5 | FAIL |
| ic_half_min | -0.0092 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.5688 | >= 0.0 | FAIL |
| coverage_pct | 99.6225 | >= 40.0 | PASS |
| avg_names_per_decile | 195.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0091  ic_tstat_nw=-1.8574  icir=-0.1210  ic_half1_mean=-0.0091  ic_half2_mean=-0.0092  ls_sharpe=-0.0171  ls_ann_return_pct=-0.2422  ls_ann_vol_pct=14.1380  ls_maxdd_pct=-65.3259  ls_hit_rate_pct=47.1014  turnover_d10_pct=12.0712  turnover_d1_pct=13.6743  coverage_pct=99.6225  avg_names_per_decile=195.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0364  ls_beta_mean=0.3772  ls_beta_fullwindow=0.3298  ls_sharpe_ex_top_years=-0.4264  ls_top_years=1999,2002,2020  ls_sharpe_bear=0.2178  ls_sharpe_bull=-0.3808
deciles D1..D10 avg %/mo: 0.973,0.950,0.914,0.970,0.964,1.045,1.054,0.998,0.867,0.926
hedge/regime (diagnostics): beta ex-ante 0.3772 full-window 0.3298  raw Sharpe -0.0364  Sharpe ex top years -0.4264 (1999,2002,2020)  bear/bull 0.2178/-0.3808
ic decay: h1=-0.0104  h2=-0.0097  h3=-0.0091  h6=-0.0088  h12=-0.0077
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0018 0.0173 0.2000 4.2400 392; MID -0.0085 -0.0932 -0.0210 -0.3900 587; SMALL -0.0135 -0.1861 -0.1400 -2.0600 977; ALL -0.0091 -0.1210 -0.0360 -0.5700 1957
annual IC: 1999:+0.042 2000:-0.060 2001:-0.041 2002:-0.035 2003:+0.011 2004:+0.002 2005:+0.008 2006:-0.006 2007:+0.014 2008:-0.019 2009:+0.000 2010:-0.011 2011:-0.011 2012:-0.005 2013:-0.008 2014:-0.029 2015:-0.019 2016:-0.025 2017:+0.036 2018:+0.009 2019:-0.014 2020:+0.032 2021:-0.080

## CashProd  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0030 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.4705 | >= 2.5 | FAIL |
| ic_half_min | -0.0035 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.7379 | >= 0.0 | PASS |
| coverage_pct | 99.1932 | >= 40.0 | PASS |
| avg_names_per_decile | 194.9 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0030  ic_tstat_nw=0.4705  icir=0.0321  ic_half1_mean=0.0094  ic_half2_mean=-0.0035  ls_sharpe=-0.1271  ls_ann_return_pct=-1.7487  ls_ann_vol_pct=13.7630  ls_maxdd_pct=-62.3095  ls_hit_rate_pct=46.3768  turnover_d10_pct=14.4917  turnover_d1_pct=16.4121  coverage_pct=99.1932  avg_names_per_decile=194.9  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2589  ls_beta_mean=0.2162  ls_beta_fullwindow=0.2609  ls_sharpe_ex_top_years=-0.4830  ls_top_years=2000,2001,2009  ls_sharpe_bear=0.3962  ls_sharpe_bull=-0.2417
deciles D1..D10 avg %/mo: 0.778,0.911,0.900,0.882,0.980,0.986,1.004,1.103,1.040,1.089
hedge/regime (diagnostics): beta ex-ante 0.2162 full-window 0.2609  raw Sharpe 0.2589  Sharpe ex top years -0.4830 (2000,2001,2009)  bear/bull 0.3962/-0.2417
ic decay: h1=-0.0002  h2=0.0002  h3=-0.0003  h6=-0.0008  h12=0.0011
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0006 -0.0048 -0.0480 -0.6900 392; MID 0.0032 0.0304 0.1930 3.0900 585; SMALL 0.0037 0.0439 0.3620 5.3200 971; ALL 0.0030 0.0321 0.2590 3.7400 1948
annual IC: 1999:-0.015 2000:+0.041 2001:+0.052 2002:-0.004 2003:+0.041 2004:+0.015 2005:-0.008 2006:+0.017 2007:-0.069 2008:-0.002 2009:+0.040 2010:+0.007 2011:-0.028 2012:+0.016 2013:+0.016 2014:+0.015 2015:-0.020 2016:+0.038 2017:-0.039 2018:-0.054 2019:+0.003 2020:-0.040 2021:+0.047

## ChAssetTurnover  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0058 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.2379 | >= 2.5 | FAIL |
| ic_half_min | 0.0033 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.3723 | >= 0.0 | PASS |
| coverage_pct | 83.4485 | >= 40.0 | PASS |
| avg_names_per_decile | 164.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0058  ic_tstat_nw=2.2379  icir=0.1384  ic_half1_mean=0.0084  ic_half2_mean=0.0033  ls_sharpe=0.3761  ls_ann_return_pct=2.3852  ls_ann_vol_pct=6.3427  ls_maxdd_pct=-29.1834  ls_hit_rate_pct=53.9855  turnover_d10_pct=16.5617  turnover_d1_pct=17.1342  coverage_pct=83.4485  avg_names_per_decile=164.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3801  ls_beta_mean=0.0058  ls_beta_fullwindow=-0.0596  ls_sharpe_ex_top_years=0.1364  ls_top_years=2003,2009,2021  ls_sharpe_bear=0.6735  ls_sharpe_bull=0.2422
deciles D1..D10 avg %/mo: 0.866,1.012,1.063,0.919,1.003,1.069,1.041,1.074,1.039,1.064
hedge/regime (diagnostics): beta ex-ante 0.0058 full-window -0.0596  raw Sharpe 0.3801  Sharpe ex top years 0.1364 (2003,2009,2021)  bear/bull 0.6735/0.2422
ic decay: h1=0.0033  h2=0.0027  h3=0.0023  h6=0.0005  h12=0.0039
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0050 0.0698 0.0720 0.7300 347; MID 0.0051 0.0911 -0.0760 -0.7600 503; SMALL 0.0057 0.1231 0.5050 4.1400 788; ALL 0.0058 0.1384 0.3800 2.3700 1639
annual IC: 1999:+0.002 2000:+0.003 2001:+0.004 2002:+0.024 2003:+0.019 2004:+0.006 2005:+0.013 2006:+0.009 2007:+0.013 2008:+0.017 2009:-0.013 2010:+0.015 2011:+0.006 2012:+0.015 2013:+0.017 2014:+0.011 2015:+0.002 2016:-0.012 2017:+0.011 2018:-0.003 2019:-0.010 2020:-0.037 2021:+0.023

## ChEQ  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0057 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.4037 | >= 2.5 | FAIL |
| ic_half_min | 0.0047 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 7.6617 | >= 0.0 | PASS |
| coverage_pct | 91.2062 | >= 40.0 | PASS |
| avg_names_per_decile | 179.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0057  ic_tstat_nw=1.4037  icir=0.0899  ic_half1_mean=0.0068  ic_half2_mean=0.0047  ls_sharpe=0.4547  ls_ann_return_pct=5.1680  ls_ann_vol_pct=11.3670  ls_maxdd_pct=-33.6656  ls_hit_rate_pct=54.7101  turnover_d10_pct=16.6865  turnover_d1_pct=15.7651  coverage_pct=91.2062  avg_names_per_decile=179.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6918  ls_beta_mean=-0.0108  ls_beta_fullwindow=0.0244  ls_sharpe_ex_top_years=0.0922  ls_top_years=2000,2009,2021  ls_sharpe_bear=0.4312  ls_sharpe_bull=0.4347
deciles D1..D10 avg %/mo: 0.567,0.958,0.965,1.074,0.933,1.008,1.125,1.146,1.150,1.205
hedge/regime (diagnostics): beta ex-ante -0.0108 full-window 0.0244  raw Sharpe 0.6918  Sharpe ex top years 0.0922 (2000,2009,2021)  bear/bull 0.4312/0.4347
ic decay: h1=0.0071  h2=0.0069  h3=0.0064  h6=0.0051  h12=0.0029
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0081 0.0787 0.2510 4.4000 368; MID 0.0065 0.0846 0.4090 5.9300 541; SMALL 0.0027 0.0441 0.6870 8.1700 882; ALL 0.0057 0.0899 0.6920 7.6600 1792
annual IC: 1999:+0.013 2000:+0.042 2001:+0.039 2002:-0.025 2003:-0.001 2004:-0.024 2005:-0.006 2006:+0.019 2007:-0.038 2008:+0.023 2009:+0.028 2010:+0.005 2011:-0.000 2012:+0.012 2013:+0.007 2014:+0.009 2015:-0.006 2016:+0.022 2017:-0.012 2018:+0.016 2019:-0.003 2020:-0.021 2021:+0.033

## ChInv  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0052 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.5106 | >= 2.5 | FAIL |
| ic_half_min | 0.0010 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 5.1411 | >= 0.0 | PASS |
| coverage_pct | 60.2908 | >= 40.0 | PASS |
| avg_names_per_decile | 118.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0052  ic_tstat_nw=1.5106  icir=0.0970  ic_half1_mean=0.0093  ic_half2_mean=0.0010  ls_sharpe=0.6492  ls_ann_return_pct=5.6463  ls_ann_vol_pct=8.6977  ls_maxdd_pct=-25.2787  ls_hit_rate_pct=56.5217  turnover_d10_pct=19.2135  turnover_d1_pct=16.5267  coverage_pct=60.2908  avg_names_per_decile=118.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6025  ls_beta_mean=-0.0864  ls_beta_fullwindow=-0.1028  ls_sharpe_ex_top_years=0.3588  ls_top_years=1999,2001,2021  ls_sharpe_bear=0.7039  ls_sharpe_bull=0.4680
deciles D1..D10 avg %/mo: 0.882,0.941,0.964,1.077,0.998,1.048,1.111,1.093,1.217,1.310
hedge/regime (diagnostics): beta ex-ante -0.0864 full-window -0.1028  raw Sharpe 0.6025  Sharpe ex top years 0.3588 (1999,2001,2021)  bear/bull 0.7039/0.4680
ic decay: h1=0.0037  h2=0.0041  h3=0.0011  h6=-0.0031  h12=0.0002
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0006 -0.0069 0.0500 0.8600 270; MID 0.0055 0.0746 0.5720 6.6500 369; SMALL 0.0070 0.1217 0.4340 4.5300 544; ALL 0.0052 0.0970 0.6020 5.1400 1184
annual IC: 1999:+0.025 2000:+0.011 2001:+0.016 2002:+0.009 2003:+0.014 2004:-0.009 2005:+0.008 2006:+0.013 2007:-0.029 2008:+0.035 2009:+0.007 2010:+0.005 2011:-0.008 2012:-0.001 2013:+0.016 2014:+0.018 2015:+0.004 2016:+0.009 2017:-0.017 2018:+0.030 2019:-0.020 2020:-0.028 2021:+0.011

## ChInvIA  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0009 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.3575 | >= 2.5 | FAIL |
| ic_half_min | -0.0026 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.0419 | >= 0.0 | PASS |
| coverage_pct | 87.2155 | >= 40.0 | PASS |
| avg_names_per_decile | 171.4 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0009  ic_tstat_nw=0.3575  icir=0.0228  ic_half1_mean=0.0045  ic_half2_mean=-0.0026  ls_sharpe=0.5643  ls_ann_return_pct=3.6876  ls_ann_vol_pct=6.5349  ls_maxdd_pct=-21.2031  ls_hit_rate_pct=55.4348  turnover_d10_pct=15.7353  turnover_d1_pct=14.3478  coverage_pct=87.2155  avg_names_per_decile=171.4  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.5909  ls_beta_mean=-0.0905  ls_beta_fullwindow=-0.1068  ls_sharpe_ex_top_years=0.3308  ls_top_years=2000,2003,2016  ls_sharpe_bear=0.7781  ls_sharpe_bull=0.5102
deciles D1..D10 avg %/mo: 0.800,1.000,1.073,1.041,1.036,1.100,1.010,1.055,1.032,1.136
hedge/regime (diagnostics): beta ex-ante -0.0905 full-window -0.1068  raw Sharpe 0.5909  Sharpe ex top years 0.3308 (2000,2003,2016)  bear/bull 0.7781/0.5102
ic decay: h1=0.0016  h2=0.0005  h3=0.0017  h6=0.0015  h12=0.0006
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0052 0.0669 0.5720 6.8400 358; MID -0.0027 -0.0476 0.2530 2.7900 523; SMALL 0.0003 0.0072 0.4450 3.8800 831; ALL 0.0009 0.0228 0.5910 4.0400 1713
annual IC: 1999:+0.000 2000:+0.003 2001:+0.018 2002:+0.021 2003:-0.001 2004:-0.009 2005:-0.002 2006:+0.017 2007:-0.002 2008:+0.033 2009:-0.014 2010:+0.008 2011:-0.006 2012:+0.002 2013:+0.006 2014:+0.024 2015:+0.000 2016:+0.005 2017:-0.027 2018:-0.009 2019:-0.018 2020:-0.012 2021:-0.015

## ChNNCOA  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0094 | >= 0.01 | FAIL |
| ic_tstat_nw | 4.1486 | >= 2.5 | PASS |
| ic_half_min | 0.0041 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.8112 | >= 0.0 | PASS |
| coverage_pct | 77.1709 | >= 40.0 | PASS |
| avg_names_per_decile | 151.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0094  ic_tstat_nw=4.1486  icir=0.2703  ic_half1_mean=0.0146  ic_half2_mean=0.0041  ls_sharpe=0.6562  ls_ann_return_pct=4.4892  ls_ann_vol_pct=6.8417  ls_maxdd_pct=-38.4154  ls_hit_rate_pct=57.2464  turnover_d10_pct=20.8286  turnover_d1_pct=19.0291  coverage_pct=77.1709  avg_names_per_decile=151.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6971  ls_beta_mean=-0.0127  ls_beta_fullwindow=-0.0677  ls_sharpe_ex_top_years=0.2335  ls_top_years=2000,2001,2003  ls_sharpe_bear=1.2532  ls_sharpe_bull=0.4062
deciles D1..D10 avg %/mo: 0.762,0.856,0.973,1.034,1.121,1.116,1.155,1.180,1.117,1.163
hedge/regime (diagnostics): beta ex-ante -0.0127 full-window -0.0677  raw Sharpe 0.6971  Sharpe ex top years 0.2335 (2000,2001,2003)  bear/bull 1.2532/0.4062
ic decay: h1=0.0066  h2=0.0055  h3=0.0058  h6=0.0028  h12=0.0026
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0104 0.1558 0.3090 3.8000 324; MID 0.0063 0.1143 0.1740 2.0200 469; SMALL 0.0108 0.2501 0.7300 6.7800 722; ALL 0.0094 0.2703 0.6970 4.8100 1516
annual IC: 1999:+0.015 2000:+0.028 2001:+0.023 2002:+0.027 2003:+0.022 2004:+0.002 2005:+0.017 2006:+0.007 2007:+0.019 2008:+0.005 2009:-0.003 2010:+0.009 2011:+0.019 2012:+0.019 2013:+0.012 2014:+0.011 2015:-0.011 2016:-0.015 2017:+0.013 2018:+0.007 2019:-0.010 2020:-0.025 2021:+0.022

## ChNWC  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0042 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.0401 | >= 2.5 | FAIL |
| ic_half_min | 0.0035 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.1492 | >= 0.0 | PASS |
| coverage_pct | 77.0369 | >= 40.0 | PASS |
| avg_names_per_decile | 151.4 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0042  ic_tstat_nw=2.0401  icir=0.1242  ic_half1_mean=0.0049  ic_half2_mean=0.0035  ls_sharpe=0.2207  ls_ann_return_pct=1.3452  ls_ann_vol_pct=6.0961  ls_maxdd_pct=-21.2712  ls_hit_rate_pct=53.2609  turnover_d10_pct=22.5181  turnover_d1_pct=23.0322  coverage_pct=77.0369  avg_names_per_decile=151.4  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1942  ls_beta_mean=-0.0435  ls_beta_fullwindow=-0.0180  ls_sharpe_ex_top_years=0.0352  ls_top_years=2000,2002,2015  ls_sharpe_bear=0.1010  ls_sharpe_bull=0.2085
deciles D1..D10 avg %/mo: 0.912,0.906,1.038,1.076,1.068,1.012,1.027,1.229,1.184,1.008
hedge/regime (diagnostics): beta ex-ante -0.0435 full-window -0.0180  raw Sharpe 0.1942  Sharpe ex top years 0.0352 (2000,2002,2015)  bear/bull 0.1010/0.2085
ic decay: h1=-0.0009  h2=0.0008  h3=0.0014  h6=-0.0023  h12=0.0022
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0036 0.0532 0.0510 0.5400 323; MID 0.0077 0.1410 0.0520 0.5800 468; SMALL 0.0024 0.0566 0.0660 0.5800 721; ALL 0.0042 0.1242 0.1940 1.1500 1513
annual IC: 1999:+0.024 2000:+0.017 2001:+0.010 2002:+0.015 2003:+0.014 2004:+0.010 2005:+0.003 2006:-0.010 2007:-0.009 2008:-0.003 2009:-0.010 2010:-0.008 2011:+0.012 2012:+0.007 2013:+0.002 2014:+0.002 2015:+0.016 2016:-0.017 2017:+0.008 2018:+0.010 2019:-0.010 2020:-0.012 2021:+0.026

## ChTax  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0048 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.4233 | >= 2.5 | FAIL |
| ic_half_min | 0.0042 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 0.0946 | >= 0.0 | PASS |
| coverage_pct | 87.1093 | >= 40.0 | PASS |
| avg_names_per_decile | 171.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0048  ic_tstat_nw=1.4233  icir=0.0936  ic_half1_mean=0.0042  ic_half2_mean=0.0055  ls_sharpe=0.1281  ls_ann_return_pct=1.0216  ls_ann_vol_pct=7.9759  ls_maxdd_pct=-37.1546  ls_hit_rate_pct=55.0725  turnover_d10_pct=27.6817  turnover_d1_pct=30.1105  coverage_pct=87.1093  avg_names_per_decile=171.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0122  ls_beta_mean=-0.0008  ls_beta_fullwindow=-0.0301  ls_sharpe_ex_top_years=-0.1609  ls_top_years=2000,2002,2007  ls_sharpe_bear=-0.3022  ls_sharpe_bull=0.3485
deciles D1..D10 avg %/mo: 1.047,1.075,1.013,1.005,1.020,0.992,1.041,1.068,1.066,1.055
hedge/regime (diagnostics): beta ex-ante -0.0008 full-window -0.0301  raw Sharpe 0.0122  Sharpe ex top years -0.1609 (2000,2002,2007)  bear/bull -0.3022/0.3485
ic decay: h1=0.0001  h2=0.0017  h3=0.0033  h6=0.0035  h12=0.0026
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0041 0.0493 0.1670 2.5200 371; MID 0.0066 0.0974 0.0670 0.7400 524; SMALL 0.0046 0.0860 -0.1060 -0.9200 815; ALL 0.0048 0.0936 0.0120 0.0900 1711
annual IC: 1999:-0.005 2000:+0.013 2001:-0.022 2002:+0.029 2003:+0.010 2004:+0.016 2005:+0.018 2006:-0.007 2007:+0.049 2008:-0.009 2009:-0.040 2010:+0.009 2011:+0.013 2012:+0.018 2013:-0.008 2014:+0.016 2015:+0.014 2016:-0.016 2017:+0.016 2018:-0.018 2019:+0.008 2020:-0.015 2021:+0.021

## CompEquIss  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0119 | >= 0.01 | PASS |
| ic_tstat_nw | 2.4415 | >= 2.5 | FAIL |
| ic_half_min | 0.0104 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.6223 | >= 0.0 | PASS |
| coverage_pct | 65.0820 | >= 40.0 | PASS |
| avg_names_per_decile | 154.8 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=0.0119  ic_tstat_nw=2.4415  icir=0.1686  ic_half1_mean=0.0134  ic_half2_mean=0.0104  ls_sharpe=0.6143  ls_ann_return_pct=5.2518  ls_ann_vol_pct=8.5493  ls_maxdd_pct=-15.6626  ls_hit_rate_pct=56.5789  turnover_d10_pct=17.6402  turnover_d1_pct=16.7971  coverage_pct=65.0820  avg_names_per_decile=154.8  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4283  ls_beta_mean=-0.0925  ls_beta_fullwindow=-0.0635  ls_sharpe_ex_top_years=0.3752  ls_top_years=2007,2015,2017  ls_sharpe_bear=0.5342  ls_sharpe_bull=0.6473
deciles D1..D10 avg %/mo: 0.991,1.095,1.111,1.085,1.137,1.084,1.140,1.201,1.283,1.293
hedge/regime (diagnostics): beta ex-ante -0.0925 full-window -0.0635  raw Sharpe 0.4283  Sharpe ex top years 0.3752 (2007,2015,2017)  bear/bull 0.5342/0.6473
ic decay: h1=0.0130  h2=0.0132  h3=0.0120  h6=0.0103  h12=0.0096
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0242 0.2218 0.4680 5.9900 346; MID 0.0071 0.0838 0.2080 2.1500 477; SMALL 0.0108 0.1654 0.5470 5.5200 723; ALL 0.0119 0.1686 0.4280 3.6200 1547
annual IC: 2003:-0.013 2004:+0.029 2005:+0.008 2006:+0.002 2007:+0.056 2008:-0.032 2009:+0.007 2010:+0.006 2011:+0.046 2012:+0.002 2013:+0.007 2014:+0.013 2015:+0.047 2016:-0.033 2017:+0.036 2018:+0.018 2019:-0.012 2020:+0.022 2021:+0.018

## CompositeDebtIssuance  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0047 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.4903 | >= 2.5 | FAIL |
| ic_half_min | -0.0008 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.3340 | >= 0.0 | PASS |
| coverage_pct | 46.2425 | >= 40.0 | PASS |
| avg_names_per_decile | 91.1851 | >= 30 | PASS |
| ls_n_months | 275 | >= 247 | PASS |
stats: ic_mean=0.0047  ic_tstat_nw=1.4903  icir=0.0901  ic_half1_mean=0.0102  ic_half2_mean=-0.0008  ls_sharpe=0.3188  ls_ann_return_pct=2.8082  ls_ann_vol_pct=8.8090  ls_maxdd_pct=-27.8552  ls_hit_rate_pct=56.3636  turnover_d10_pct=13.1227  turnover_d1_pct=12.7018  coverage_pct=46.2425  avg_names_per_decile=91.1851  n_months=275  ls_n_months=275  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1528  ls_beta_mean=-0.0696  ls_beta_fullwindow=-0.1101  ls_sharpe_ex_top_years=-0.0178  ls_top_years=1999,2000,2014  ls_sharpe_bear=-0.7184  ls_sharpe_bull=0.5109
deciles D1..D10 avg %/mo: 1.023,0.923,1.079,1.152,1.134,1.096,1.053,1.068,1.113,1.135
hedge/regime (diagnostics): beta ex-ante -0.0696 full-window -0.1101  raw Sharpe 0.1528  Sharpe ex top years -0.0178 (1999,2000,2014)  bear/bull -0.7184/0.5109
ic decay: h1=0.0040  h2=0.0009  h3=0.0033  h6=0.0001  h12=0.0023
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0060 0.0699 -0.0310 -0.4100 235; MID 0.0064 0.0915 0.2000 2.2700 296; SMALL -0.0027 -0.0421 -0.1640 -1.8500 386; ALL 0.0039 0.0778 0.0770 0.6200 915
annual IC: 1999:+0.058 2000:+0.020 2001:-0.013 2002:+0.012 2003:-0.003 2004:+0.015 2005:+0.021 2006:+0.010 2007:+0.013 2008:-0.004 2009:-0.007 2010:+0.007 2011:-0.007 2012:+0.016 2013:+0.008 2014:+0.024 2015:+0.002 2016:-0.001 2017:-0.022 2018:-0.006 2019:-0.006 2020:-0.040 2021:+0.014
