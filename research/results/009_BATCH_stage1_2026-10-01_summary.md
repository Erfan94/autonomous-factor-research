# RUN 009 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## OPLeverage  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0087 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.8949 | >= 2.5 | PASS |
| ic_half_min | 0.0073 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.0859 | >= 0.0 | PASS |
| coverage_pct | 85.4069 | >= 40.0 | PASS |
| avg_names_per_decile | 167.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0087  ic_tstat_nw=2.8949  icir=0.1748  ic_half1_mean=0.0101  ic_half2_mean=0.0073  ls_sharpe=0.4291  ls_ann_return_pct=3.4591  ls_ann_vol_pct=8.0621  ls_maxdd_pct=-28.3686  ls_hit_rate_pct=56.5217  turnover_d10_pct=8.1901  turnover_d1_pct=7.9425  coverage_pct=85.4069  avg_names_per_decile=167.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.5052  ls_beta_mean=-0.0535  ls_beta_fullwindow=-0.0958  ls_sharpe_ex_top_years=0.1535  ls_top_years=2001,2020,2021  ls_sharpe_bear=0.5747  ls_sharpe_bull=0.5513
deciles D1..D10 avg %/mo: 0.773,0.901,0.939,0.888,0.988,1.115,1.131,1.088,1.128,1.113
hedge/regime (diagnostics): beta ex-ante -0.0535 full-window -0.0958  raw Sharpe 0.5052  Sharpe ex top years 0.1535 (2001,2020,2021)  bear/bull 0.5747/0.5513
ic decay: h1=0.0089  h2=0.0092  h3=0.0095  h6=0.0093  h12=0.0100
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0155 0.1882 0.4530 8.5500 348; MID 0.0038 0.0618 0.1120 1.1900 518; SMALL 0.0082 0.1537 0.3980 3.4700 810; ALL 0.0087 0.1748 0.5050 4.0900 1678
annual IC: 1999:-0.018 2000:+0.007 2001:+0.046 2002:+0.020 2003:+0.006 2004:+0.015 2005:+0.018 2006:+0.008 2007:-0.008 2008:+0.009 2009:+0.005 2010:+0.010 2011:+0.018 2012:+0.007 2013:+0.026 2014:+0.012 2015:-0.004 2016:+0.005 2017:-0.005 2018:-0.001 2019:+0.005 2020:+0.000 2021:+0.018

## OperProfRD  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0192 | >= 0.01 | PASS |
| ic_tstat_nw | 3.1835 | >= 2.5 | PASS |
| ic_half_min | 0.0122 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 6.4373 | >= 0.0 | PASS |
| coverage_pct | 70.7416 | >= 40.0 | PASS |
| avg_names_per_decile | 139.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0192  ic_tstat_nw=3.1835  icir=0.2199  ic_half1_mean=0.0263  ic_half2_mean=0.0122  ls_sharpe=0.7329  ls_ann_return_pct=10.9401  ls_ann_vol_pct=14.9269  ls_maxdd_pct=-45.8573  ls_hit_rate_pct=60.1449  turnover_d10_pct=8.1172  turnover_d1_pct=13.0087  coverage_pct=70.7416  avg_names_per_decile=139.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3706  ls_beta_mean=-0.5138  ls_beta_fullwindow=-0.6048  ls_sharpe_ex_top_years=0.4519  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.4761  ls_sharpe_bull=0.8838
deciles D1..D10 avg %/mo: 0.598,0.891,0.841,1.024,1.050,1.171,1.193,1.134,1.130,1.135
hedge/regime (diagnostics): beta ex-ante -0.5138 full-window -0.6048  raw Sharpe 0.3706  Sharpe ex top years 0.4519 (2000,2002,2021)  bear/bull 0.4761/0.8838
ic decay: h1=0.0173  h2=0.0160  h3=0.0158  h6=0.0152  h12=0.0135
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0253 0.2302 0.2940 7.1400 298; MID 0.0206 0.2056 0.5580 11.1700 428; SMALL 0.0171 0.2003 0.2400 4.3500 662; ALL 0.0192 0.2199 0.3710 6.4400 1389
annual IC: 1999:+0.022 2000:+0.093 2001:+0.030 2002:+0.081 2003:-0.013 2004:+0.026 2005:+0.019 2006:-0.016 2007:+0.021 2008:+0.039 2009:-0.015 2010:+0.008 2011:+0.045 2012:-0.025 2013:-0.020 2014:+0.029 2015:+0.031 2016:-0.000 2017:+0.015 2018:+0.036 2019:-0.016 2020:-0.042 2021:+0.094

## OrgCap  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0054 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.6968 | >= 2.5 | FAIL |
| ic_half_min | 0.0043 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.2082 | >= 0.0 | PASS |
| coverage_pct | 50.3583 | >= 40.0 | PASS |
| avg_names_per_decile | 98.9435 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0054  ic_tstat_nw=1.6968  icir=0.1028  ic_half1_mean=0.0043  ic_half2_mean=0.0065  ls_sharpe=0.4013  ls_ann_return_pct=4.3639  ls_ann_vol_pct=10.8748  ls_maxdd_pct=-29.2294  ls_hit_rate_pct=54.7101  turnover_d10_pct=9.3803  turnover_d1_pct=8.1284  coverage_pct=50.3583  avg_names_per_decile=98.9435  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3991  ls_beta_mean=0.1007  ls_beta_fullwindow=0.0847  ls_sharpe_ex_top_years=0.1944  ls_top_years=1999,2001,2010  ls_sharpe_bear=0.7961  ls_sharpe_bull=0.1921
deciles D1..D10 avg %/mo: 0.605,0.858,0.748,0.965,1.005,1.020,0.959,1.090,1.149,0.956
hedge/regime (diagnostics): beta ex-ante 0.1007 full-window 0.0847  raw Sharpe 0.3991  Sharpe ex top years 0.1944 (1999,2001,2010)  bear/bull 0.7961/0.1921
ic decay: h1=0.0047  h2=0.0050  h3=0.0055  h6=0.0068  h12=0.0049
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0097 0.1049 0.2710 4.4200 199; MID 0.0040 0.0554 0.2240 3.2700 304; SMALL 0.0047 0.0713 0.2870 4.1100 485; ALL 0.0054 0.1028 0.3990 4.2100 989
annual IC: 1999:+0.005 2000:-0.024 2001:+0.020 2002:+0.031 2003:+0.005 2004:-0.010 2005:+0.006 2006:+0.014 2007:-0.030 2008:+0.026 2009:-0.002 2010:+0.025 2011:+0.001 2012:+0.006 2013:+0.008 2014:+0.003 2015:+0.012 2016:+0.000 2017:+0.011 2018:+0.033 2019:-0.007 2020:-0.000 2021:-0.008

## PctAcc  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0112 | >= 0.01 | PASS |
| ic_tstat_nw | 4.0320 | >= 2.5 | PASS |
| ic_half_min | 0.0071 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.7395 | >= 0.0 | PASS |
| coverage_pct | 95.5826 | >= 40.0 | PASS |
| avg_names_per_decile | 187.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0112  ic_tstat_nw=4.0320  icir=0.2606  ic_half1_mean=0.0152  ic_half2_mean=0.0071  ls_sharpe=0.6723  ls_ann_return_pct=4.1475  ls_ann_vol_pct=6.1693  ls_maxdd_pct=-11.0137  ls_hit_rate_pct=55.7971  turnover_d10_pct=17.5574  turnover_d1_pct=16.6245  coverage_pct=95.5826  avg_names_per_decile=187.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.7625  ls_beta_mean=-0.0511  ls_beta_fullwindow=-0.0383  ls_sharpe_ex_top_years=0.4619  ls_top_years=2000,2005,2021  ls_sharpe_bear=0.9057  ls_sharpe_bull=0.5282
deciles D1..D10 avg %/mo: 0.732,0.870,0.919,0.957,1.015,1.025,0.997,1.153,1.156,1.127
hedge/regime (diagnostics): beta ex-ante -0.0511 full-window -0.0383  raw Sharpe 0.7625  Sharpe ex top years 0.4619 (2000,2005,2021)  bear/bull 0.9057/0.5282
ic decay: h1=0.0089  h2=0.0080  h3=0.0078  h6=0.0045  h12=0.0031
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0009 -0.0121 -0.0150 -0.1500 384; MID 0.0122 0.2153 0.4670 4.3500 567; SMALL 0.0156 0.3258 0.9070 6.9700 926; ALL 0.0112 0.2606 0.7620 4.7400 1877
annual IC: 1999:+0.029 2000:+0.032 2001:+0.014 2002:+0.016 2003:+0.014 2004:+0.011 2005:+0.030 2006:+0.011 2007:-0.010 2008:+0.008 2009:+0.014 2010:+0.014 2011:-0.013 2012:+0.002 2013:+0.026 2014:+0.016 2015:-0.007 2016:+0.011 2017:+0.001 2018:+0.011 2019:-0.015 2020:+0.001 2021:+0.041

## PctTotAcc  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0022 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.9111 | >= 2.5 | FAIL |
| ic_half_min | 0.0014 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.4836 | >= 0.0 | PASS |
| coverage_pct | 95.5746 | >= 40.0 | PASS |
| avg_names_per_decile | 187.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0022  ic_tstat_nw=0.9111  icir=0.0560  ic_half1_mean=0.0014  ic_half2_mean=0.0029  ls_sharpe=0.3765  ls_ann_return_pct=2.1628  ls_ann_vol_pct=5.7446  ls_maxdd_pct=-22.6384  ls_hit_rate_pct=57.2464  turnover_d10_pct=20.2119  turnover_d1_pct=20.5786  coverage_pct=95.5746  avg_names_per_decile=187.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4342  ls_beta_mean=-0.0861  ls_beta_fullwindow=-0.0833  ls_sharpe_ex_top_years=0.1868  ls_top_years=2003,2018,2021  ls_sharpe_bear=0.0292  ls_sharpe_bull=0.5218
deciles D1..D10 avg %/mo: 0.872,0.926,0.945,0.959,1.023,1.000,1.110,0.947,1.091,1.079
hedge/regime (diagnostics): beta ex-ante -0.0861 full-window -0.0833  raw Sharpe 0.4342  Sharpe ex top years 0.1868 (2003,2018,2021)  bear/bull 0.0292/0.5218
ic decay: h1=0.0008  h2=0.0008  h3=0.0003  h6=-0.0012  h12=0.0009
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0052 0.0773 0.0560 0.5900 384; MID 0.0032 0.0574 0.3520 3.0500 567; SMALL 0.0003 0.0076 0.3400 2.6800 926; ALL 0.0022 0.0560 0.4340 2.4800 1877
annual IC: 1999:+0.019 2000:-0.015 2001:+0.002 2002:-0.013 2003:+0.010 2004:-0.004 2005:-0.004 2006:+0.012 2007:-0.014 2008:+0.004 2009:+0.015 2010:+0.004 2011:+0.007 2012:+0.002 2013:+0.004 2014:+0.000 2015:-0.002 2016:+0.004 2017:-0.003 2018:+0.031 2019:-0.007 2020:-0.006 2021:+0.003

## Price  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0100 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.4133 | >= 2.5 | FAIL |
| ic_half_min | -0.0174 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.9800 | >= 0.0 | PASS |
| coverage_pct | 100.0 | >= 40.0 | PASS |
| avg_names_per_decile | 196.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0100  ic_tstat_nw=-1.4133  icir=-0.0868  ic_half1_mean=-0.0027  ic_half2_mean=-0.0174  ls_sharpe=-0.3146  ls_ann_return_pct=-5.8925  ls_ann_vol_pct=18.7275  ls_maxdd_pct=-86.4586  ls_hit_rate_pct=37.6812  turnover_d10_pct=16.3128  turnover_d1_pct=10.3971  coverage_pct=100.0  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1367  ls_beta_mean=0.7150  ls_beta_fullwindow=0.7700  ls_sharpe_ex_top_years=-0.7659  ls_top_years=2001,2009,2016  ls_sharpe_bear=0.6893  ls_sharpe_bull=-0.9723
deciles D1..D10 avg %/mo: 0.842,0.785,0.864,0.933,1.004,1.067,0.998,1.033,1.053,1.091
hedge/regime (diagnostics): beta ex-ante 0.7150 full-window 0.7700  raw Sharpe 0.1367  Sharpe ex top years -0.7659 (2001,2009,2016)  bear/bull 0.6893/-0.9723
ic decay: h1=-0.0130  h2=-0.0130  h3=-0.0114  h6=-0.0095  h12=-0.0051
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0143 -0.1177 -0.1130 -2.7400 393; MID -0.0134 -0.1125 0.0210 0.4700 589; SMALL -0.0104 -0.0901 0.1380 3.2800 981; ALL -0.0100 -0.0868 0.1370 2.9800 1964
annual IC: 1999:-0.024 2000:-0.032 2001:+0.059 2002:-0.029 2003:+0.057 2004:-0.008 2005:-0.026 2006:+0.004 2007:-0.073 2008:-0.011 2009:+0.054 2010:+0.024 2011:-0.059 2012:+0.008 2013:+0.002 2014:-0.022 2015:-0.051 2016:+0.031 2017:-0.029 2018:-0.044 2019:-0.007 2020:+0.001 2021:-0.056

## PriceDelayRsq  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0070 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.1241 | >= 2.5 | FAIL |
| ic_half_min | -0.0131 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -1.0873 | >= 0.0 | FAIL |
| coverage_pct | 87.7969 | >= 40.0 | PASS |
| avg_names_per_decile | 185.3 | >= 30 | PASS |
| ls_n_months | 257 | >= 231 | PASS |
stats: ic_mean=-0.0070  ic_tstat_nw=-2.1241  icir=-0.1248  ic_half1_mean=-0.0009  ic_half2_mean=-0.0131  ls_sharpe=0.0013  ls_ann_return_pct=0.0113  ls_ann_vol_pct=8.6010  ls_maxdd_pct=-33.4852  ls_hit_rate_pct=49.4163  turnover_d10_pct=14.0630  turnover_d1_pct=9.0247  coverage_pct=87.7969  avg_names_per_decile=185.3  n_months=257  ls_n_months=257  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.1220  ls_beta_mean=-0.1166  ls_beta_fullwindow=-0.1659  ls_sharpe_ex_top_years=-0.2317  ls_top_years=2003,2004,2020  ls_sharpe_bear=-0.0191  ls_sharpe_bull=0.0103
deciles D1..D10 avg %/mo: 0.965,0.997,0.946,0.947,0.873,1.048,0.958,0.999,0.965,0.874
hedge/regime (diagnostics): beta ex-ante -0.1166 full-window -0.1659  raw Sharpe -0.1220  Sharpe ex top years -0.2317 (2003,2004,2020)  bear/bull -0.0191/0.0103
ic decay: h1=-0.0075  h2=-0.0067  h3=-0.0056  h6=-0.0060  h12=-0.0051
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0062 -0.0622 -0.0410 -0.6200 379; MID -0.0077 -0.1051 -0.1770 -1.9400 562; SMALL -0.0092 -0.1708 -0.3990 -3.4600 911; ALL -0.0070 -0.1248 -0.1220 -1.0900 1852
annual IC: 2000:+0.001 2001:+0.014 2002:+0.033 2003:+0.001 2004:+0.019 2005:-0.006 2006:-0.013 2007:-0.019 2008:-0.028 2009:-0.001 2010:-0.004 2011:-0.010 2012:-0.017 2013:-0.010 2014:-0.016 2015:-0.019 2016:-0.001 2017:-0.021 2018:+0.003 2019:-0.028 2020:+0.015 2021:-0.042

## PriceDelaySlope  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0055 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.6930 | >= 2.5 | FAIL |
| ic_half_min | -0.0069 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.6019 | >= 0.0 | FAIL |
| coverage_pct | 87.7969 | >= 40.0 | PASS |
| avg_names_per_decile | 185.3 | >= 30 | PASS |
| ls_n_months | 257 | >= 231 | PASS |
stats: ic_mean=-0.0055  ic_tstat_nw=-1.6930  icir=-0.1077  ic_half1_mean=-0.0069  ic_half2_mean=-0.0042  ls_sharpe=-0.4195  ls_ann_return_pct=-2.9277  ls_ann_vol_pct=6.9790  ls_maxdd_pct=-53.3812  ls_hit_rate_pct=43.9689  turnover_d10_pct=13.3077  turnover_d1_pct=11.2665  coverage_pct=87.7969  avg_names_per_decile=185.3  n_months=257  ls_n_months=257  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0800  ls_beta_mean=0.1935  ls_beta_fullwindow=0.2281  ls_sharpe_ex_top_years=-0.8158  ls_top_years=2001,2002,2009  ls_sharpe_bear=0.6081  ls_sharpe_bull=-0.8357
deciles D1..D10 avg %/mo: 0.986,0.970,1.024,1.001,0.945,0.998,0.956,0.929,0.828,0.936
hedge/regime (diagnostics): beta ex-ante 0.1935 full-window 0.2281  raw Sharpe -0.0800  Sharpe ex top years -0.8158 (2001,2002,2009)  bear/bull 0.6081/-0.8357
ic decay: h1=-0.0050  h2=-0.0046  h3=-0.0026  h6=-0.0006  h12=0.0029
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0080 -0.0996 -0.2230 -2.5300 379; MID -0.0075 -0.1078 -0.3070 -3.0000 562; SMALL -0.0063 -0.1124 -0.1490 -1.3000 911; ALL -0.0055 -0.1077 -0.0800 -0.6000 1852
annual IC: 2000:-0.056 2001:-0.004 2002:-0.005 2003:+0.009 2004:-0.022 2005:-0.011 2006:-0.004 2007:-0.011 2008:-0.037 2009:+0.035 2010:-0.002 2011:-0.012 2012:+0.020 2013:+0.004 2014:+0.005 2015:-0.012 2016:+0.005 2017:+0.000 2018:-0.009 2019:+0.014 2020:-0.027 2021:-0.030

## PriceDelayTstat  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0055 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.6785 | >= 2.5 | FAIL |
| ic_half_min | -0.0069 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.5916 | >= 0.0 | FAIL |
| coverage_pct | 87.7969 | >= 40.0 | PASS |
| avg_names_per_decile | 185.3 | >= 30 | PASS |
| ls_n_months | 257 | >= 231 | PASS |
stats: ic_mean=-0.0055  ic_tstat_nw=-1.6785  icir=-0.1070  ic_half1_mean=-0.0069  ic_half2_mean=-0.0042  ls_sharpe=-0.4190  ls_ann_return_pct=-2.9262  ls_ann_vol_pct=6.9834  ls_maxdd_pct=-53.8477  ls_hit_rate_pct=43.1907  turnover_d10_pct=13.2789  turnover_d1_pct=11.3030  coverage_pct=87.7969  avg_names_per_decile=185.3  n_months=257  ls_n_months=257  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0784  ls_beta_mean=0.1944  ls_beta_fullwindow=0.2294  ls_sharpe_ex_top_years=-0.8086  ls_top_years=2001,2002,2009  ls_sharpe_bear=0.6045  ls_sharpe_bull=-0.8370
deciles D1..D10 avg %/mo: 0.984,0.963,1.029,0.994,0.946,1.002,0.955,0.921,0.844,0.935
hedge/regime (diagnostics): beta ex-ante 0.1944 full-window 0.2294  raw Sharpe -0.0784  Sharpe ex top years -0.8086 (2001,2002,2009)  bear/bull 0.6045/-0.8370
ic decay: h1=-0.0050  h2=-0.0046  h3=-0.0025  h6=-0.0006  h12=0.0029
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0079 -0.0988 -0.2310 -2.5900 379; MID -0.0074 -0.1057 -0.2830 -2.8300 562; SMALL -0.0063 -0.1132 -0.1510 -1.3200 911; ALL -0.0055 -0.1070 -0.0780 -0.5900 1852
annual IC: 2000:-0.056 2001:-0.003 2002:-0.005 2003:+0.009 2004:-0.022 2005:-0.011 2006:-0.004 2007:-0.011 2008:-0.037 2009:+0.035 2010:-0.002 2011:-0.012 2012:+0.019 2013:+0.004 2014:+0.005 2015:-0.012 2016:+0.005 2017:+0.001 2018:-0.010 2019:+0.014 2020:-0.027 2021:-0.030

## RealizedVol  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0234 | >= 0.01 | PASS |
| ic_tstat_nw | 2.8096 | >= 2.5 | PASS |
| ic_half_min | 0.0198 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.3869 | >= 0.0 | PASS |
| coverage_pct | 99.8007 | >= 40.0 | PASS |
| avg_names_per_decile | 196.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0234  ic_tstat_nw=2.8096  icir=0.1610  ic_half1_mean=0.0270  ic_half2_mean=0.0198  ls_sharpe=0.6070  ls_ann_return_pct=12.1326  ls_ann_vol_pct=19.9871  ls_maxdd_pct=-54.4551  ls_hit_rate_pct=63.7681  turnover_d10_pct=59.2280  turnover_d1_pct=65.1170  coverage_pct=99.8007  avg_names_per_decile=196.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1276  ls_beta_mean=-1.0911  ls_beta_fullwindow=-1.1614  ls_sharpe_ex_top_years=0.4794  ls_top_years=2000,2007,2021  ls_sharpe_bear=-0.0365  ls_sharpe_bull=1.0391
deciles D1..D10 avg %/mo: 0.736,0.915,1.053,0.971,0.949,1.004,1.027,0.996,1.008,1.019
hedge/regime (diagnostics): beta ex-ante -1.0911 full-window -1.1614  raw Sharpe 0.1276  Sharpe ex top years 0.4794 (2000,2007,2021)  bear/bull -0.0365/1.0391
ic decay: h1=0.0216  h2=0.0173  h3=0.0182  h6=0.0148  h12=0.0167
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0208 0.1155 0.1220 3.9600 392; MID 0.0238 0.1453 0.1430 4.1400 588; SMALL 0.0242 0.1873 0.0960 2.3800 979; ALL 0.0234 0.1610 0.1280 3.3900 1960
annual IC: 1999:+0.011 2000:+0.106 2001:+0.047 2002:+0.064 2003:-0.037 2004:+0.002 2005:+0.003 2006:+0.020 2007:+0.043 2008:+0.063 2009:-0.037 2010:-0.016 2011:+0.076 2012:-0.011 2013:-0.006 2014:+0.034 2015:+0.059 2016:-0.008 2017:+0.025 2018:+0.057 2019:-0.011 2020:-0.033 2021:+0.087

## ResidualMomentum  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0035 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.7155 | >= 2.5 | FAIL |
| ic_half_min | 0.0009 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.7559 | >= 0.0 | PASS |
| coverage_pct | 67.4028 | >= 40.0 | PASS |
| avg_names_per_decile | 163.9 | >= 30 | PASS |
| ls_n_months | 223 | >= 200 | PASS |
stats: ic_mean=0.0035  ic_tstat_nw=0.7155  icir=0.0442  ic_half1_mean=0.0062  ic_half2_mean=0.0009  ls_sharpe=0.4656  ls_ann_return_pct=4.9231  ls_ann_vol_pct=10.5733  ls_maxdd_pct=-35.7322  ls_hit_rate_pct=58.7444  turnover_d10_pct=33.8822  turnover_d1_pct=32.8208  coverage_pct=67.4028  avg_names_per_decile=163.9  n_months=223  ls_n_months=223  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1619  ls_beta_mean=-0.2076  ls_beta_fullwindow=-0.2401  ls_sharpe_ex_top_years=0.1874  ls_top_years=2013,2017,2021  ls_sharpe_bear=-0.4412  ls_sharpe_bull=0.7649
deciles D1..D10 avg %/mo: 1.034,1.035,1.049,1.075,1.084,1.064,1.180,1.125,1.158,1.180
hedge/regime (diagnostics): beta ex-ante -0.2076 full-window -0.2401  raw Sharpe 0.1619  Sharpe ex top years 0.1874 (2013,2017,2021)  bear/bull -0.4412/0.7649
ic decay: h1=0.0023  h2=0.0018  h3=0.0018  h6=0.0016  h12=0.0059
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0019 0.0160 0.2600 4.9500 356; MID 0.0083 0.0858 0.2320 3.1300 505; SMALL 0.0007 0.0099 -0.0520 -0.5100 777; ALL 0.0035 0.0442 0.1620 1.7600 1639
annual IC: 2003:-0.022 2004:-0.000 2005:+0.041 2006:-0.002 2007:+0.011 2008:+0.016 2009:-0.042 2010:+0.015 2011:+0.025 2012:-0.003 2013:+0.008 2014:-0.004 2015:+0.027 2016:-0.031 2017:+0.033 2018:+0.019 2019:-0.047 2020:+0.002 2021:+0.011

## ReturnSkew  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0050 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.2174 | >= 2.5 | FAIL |
| ic_half_min | 0.0026 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 0.4006 | >= 0.0 | PASS |
| coverage_pct | 99.8007 | >= 40.0 | PASS |
| avg_names_per_decile | 196.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0050  ic_tstat_nw=2.2174  icir=0.1375  ic_half1_mean=0.0074  ic_half2_mean=0.0026  ls_sharpe=0.0659  ls_ann_return_pct=0.4481  ls_ann_vol_pct=6.8055  ls_maxdd_pct=-32.6169  ls_hit_rate_pct=47.8261  turnover_d10_pct=90.3342  turnover_d1_pct=89.9432  coverage_pct=99.8007  avg_names_per_decile=196.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0609  ls_beta_mean=-0.0103  ls_beta_fullwindow=-0.0258  ls_sharpe_ex_top_years=-0.2690  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.3935  ls_sharpe_bull=0.0045
deciles D1..D10 avg %/mo: 0.961,0.883,0.956,0.916,1.003,0.979,0.953,0.995,1.036,0.995
hedge/regime (diagnostics): beta ex-ante -0.0103 full-window -0.0258  raw Sharpe 0.0609  Sharpe ex top years -0.2690 (2000,2002,2021)  bear/bull 0.3935/0.0045
ic decay: h1=0.0035  h2=0.0055  h3=0.0033  h6=0.0029  h12=0.0055
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0059 0.0822 -0.0390 -0.4100 392; MID 0.0023 0.0408 0.0030 0.0200 588; SMALL 0.0062 0.1439 0.0990 0.8200 979; ALL 0.0050 0.1375 0.0610 0.4000 1960
annual IC: 1999:+0.013 2000:+0.028 2001:+0.024 2002:+0.022 2003:-0.006 2004:-0.004 2005:+0.003 2006:+0.004 2007:-0.013 2008:+0.004 2009:+0.002 2010:+0.011 2011:-0.019 2012:+0.017 2013:-0.003 2014:+0.008 2015:-0.011 2016:+0.011 2017:-0.013 2018:+0.007 2019:+0.005 2020:+0.004 2021:+0.022
