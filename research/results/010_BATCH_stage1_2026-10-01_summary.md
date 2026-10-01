# RUN 010 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## ReturnSkew3F  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0007 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.3493 | >= 2.5 | FAIL |
| ic_half_min | -0.0007 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -1.3397 | >= 0.0 | FAIL |
| coverage_pct | 96.7275 | >= 40.0 | PASS |
| avg_names_per_decile | 195.0 | >= 30 | PASS |
| ls_n_months | 269 | >= 242 | PASS |
stats: ic_mean=0.0007  ic_tstat_nw=0.3493  icir=0.0222  ic_half1_mean=0.0022  ic_half2_mean=-0.0007  ls_sharpe=-0.3069  ls_ann_return_pct=-1.9296  ls_ann_vol_pct=6.2872  ls_maxdd_pct=-49.5128  ls_hit_rate_pct=43.1227  turnover_d10_pct=90.6116  turnover_d1_pct=90.2583  coverage_pct=96.7275  avg_names_per_decile=195.0  n_months=269  ls_n_months=269  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.2233  ls_beta_mean=0.0260  ls_beta_fullwindow=0.0169  ls_sharpe_ex_top_years=-0.6785  ls_top_years=2000,2012,2021  ls_sharpe_bear=-0.1107  ls_sharpe_bull=-0.2835
deciles D1..D10 avg %/mo: 1.029,0.897,0.930,0.970,0.932,0.952,0.934,0.933,1.013,0.918
hedge/regime (diagnostics): beta ex-ante 0.0260 full-window 0.0169  raw Sharpe -0.2233  Sharpe ex top years -0.6785 (2000,2012,2021)  bear/bull -0.1107/-0.2835
ic decay: h1=0.0036  h2=0.0063  h3=0.0033  h6=0.0027  h12=0.0057
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0002 -0.0031 -0.2230 -2.8500 390; MID 0.0008 0.0136 -0.2300 -2.1600 585; SMALL 0.0018 0.0461 -0.0630 -0.4800 974; ALL 0.0007 0.0222 -0.2230 -1.3400 1949
annual IC: 1999:+0.004 2000:+0.028 2001:+0.001 2002:+0.013 2003:-0.005 2004:-0.001 2005:-0.014 2006:+0.008 2007:-0.020 2008:+0.004 2009:-0.000 2010:+0.008 2011:-0.008 2012:+0.009 2013:-0.016 2014:+0.004 2015:-0.004 2016:+0.006 2017:-0.017 2018:+0.001 2019:-0.002 2020:-0.000 2021:+0.020

## RevenueSurprise  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0094 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.7821 | >= 2.5 | PASS |
| ic_half_min | 0.0059 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.8243 | >= 0.0 | PASS |
| coverage_pct | 86.6066 | >= 40.0 | PASS |
| avg_names_per_decile | 170.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0094  ic_tstat_nw=2.7821  icir=0.1875  ic_half1_mean=0.0059  ic_half2_mean=0.0129  ls_sharpe=0.3471  ls_ann_return_pct=2.5877  ls_ann_vol_pct=7.4553  ls_maxdd_pct=-21.7328  ls_hit_rate_pct=57.6087  turnover_d10_pct=27.8134  turnover_d1_pct=29.2728  coverage_pct=86.6066  avg_names_per_decile=170.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2499  ls_beta_mean=-0.0306  ls_beta_fullwindow=-0.0524  ls_sharpe_ex_top_years=0.0931  ls_top_years=2007,2017,2021  ls_sharpe_bear=-0.5186  ls_sharpe_bull=0.6783
deciles D1..D10 avg %/mo: 0.872,0.947,0.995,0.993,1.096,1.179,0.993,1.051,1.142,1.024
hedge/regime (diagnostics): beta ex-ante -0.0306 full-window -0.0524  raw Sharpe 0.2499  Sharpe ex top years 0.0931 (2007,2017,2021)  bear/bull -0.5186/0.6783
ic decay: h1=0.0060  h2=0.0061  h3=0.0062  h6=0.0021  h12=0.0020
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0070 0.0854 0.0200 0.2400 360; MID 0.0135 0.1966 0.1800 1.9100 519; SMALL 0.0087 0.1677 0.2840 2.3100 821; ALL 0.0094 0.1875 0.2500 1.8200 1701
annual IC: 1999:+0.010 2000:+0.021 2001:-0.025 2002:+0.018 2003:-0.001 2004:+0.016 2005:+0.009 2006:-0.010 2007:+0.058 2008:+0.008 2009:-0.027 2010:+0.001 2011:+0.011 2012:+0.039 2013:+0.017 2014:+0.016 2015:+0.017 2016:-0.018 2017:+0.043 2018:+0.002 2019:-0.012 2020:-0.007 2021:+0.030

## RoE  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0192 | >= 0.01 | PASS |
| ic_tstat_nw | 3.3373 | >= 2.5 | PASS |
| ic_half_min | 0.0153 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.9522 | >= 0.0 | PASS |
| coverage_pct | 93.1349 | >= 40.0 | PASS |
| avg_names_per_decile | 183.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0192  ic_tstat_nw=3.3373  icir=0.2115  ic_half1_mean=0.0231  ic_half2_mean=0.0153  ls_sharpe=0.5316  ls_ann_return_pct=7.3824  ls_ann_vol_pct=13.8873  ls_maxdd_pct=-38.7245  ls_hit_rate_pct=59.0580  turnover_d10_pct=9.7391  turnover_d1_pct=14.8738  coverage_pct=93.1349  avg_names_per_decile=183.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1795  ls_beta_mean=-0.5129  ls_beta_fullwindow=-0.5893  ls_sharpe_ex_top_years=0.3718  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.2824  ls_sharpe_bull=0.6942
deciles D1..D10 avg %/mo: 0.843,0.940,0.926,0.931,0.951,0.958,1.001,1.056,1.148,1.089
hedge/regime (diagnostics): beta ex-ante -0.5129 full-window -0.5893  raw Sharpe 0.1795  Sharpe ex top years 0.3718 (2000,2002,2021)  bear/bull 0.2824/0.6942
ic decay: h1=0.0172  h2=0.0170  h3=0.0169  h6=0.0158  h12=0.0151
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0282 0.2500 0.3050 6.4200 374; MID 0.0208 0.2125 0.3700 6.8200 552; SMALL 0.0160 0.1804 0.0300 0.5000 903; ALL 0.0192 0.2115 0.1800 2.9500 1829
annual IC: 1999:+0.006 2000:+0.086 2001:+0.030 2002:+0.077 2003:-0.011 2004:+0.025 2005:+0.009 2006:-0.004 2007:+0.039 2008:+0.022 2009:-0.023 2010:-0.009 2011:+0.053 2012:-0.003 2013:-0.002 2014:+0.030 2015:+0.022 2016:-0.005 2017:+0.027 2018:+0.019 2019:+0.002 2020:-0.020 2021:+0.071

## SP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0182 | >= 0.01 | PASS |
| ic_tstat_nw | 2.4968 | >= 2.5 | FAIL |
| ic_half_min | 0.0093 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 9.2140 | >= 0.0 | PASS |
| coverage_pct | 96.0710 | >= 40.0 | PASS |
| avg_names_per_decile | 188.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0182  ic_tstat_nw=2.4968  icir=0.1739  ic_half1_mean=0.0270  ic_half2_mean=0.0093  ls_sharpe=0.1454  ls_ann_return_pct=2.7940  ls_ann_vol_pct=19.2172  ls_maxdd_pct=-63.5959  ls_hit_rate_pct=49.2754  turnover_d10_pct=10.8318  turnover_d1_pct=12.7869  coverage_pct=96.0710  avg_names_per_decile=188.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4677  ls_beta_mean=0.1423  ls_beta_fullwindow=0.1843  ls_sharpe_ex_top_years=-0.2011  ls_top_years=2001,2009,2021  ls_sharpe_bear=0.6565  ls_sharpe_bull=0.0738
deciles D1..D10 avg %/mo: 0.633,0.794,0.901,0.876,0.935,0.951,1.013,1.188,1.183,1.401
hedge/regime (diagnostics): beta ex-ante 0.1423 full-window 0.1843  raw Sharpe 0.4677  Sharpe ex top years -0.2011 (2001,2009,2021)  bear/bull 0.6565/0.0738
ic decay: h1=0.0150  h2=0.0140  h3=0.0139  h6=0.0133  h12=0.0142
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0133 0.0958 0.4260 10.1700 385; MID 0.0121 0.1047 0.2410 5.1300 569; SMALL 0.0226 0.2346 0.4940 9.6700 932; ALL 0.0182 0.1739 0.4680 9.2100 1887
annual IC: 1999:-0.028 2000:+0.067 2001:+0.082 2002:+0.027 2003:+0.042 2004:+0.033 2005:+0.030 2006:+0.033 2007:-0.047 2008:+0.003 2009:+0.062 2010:+0.019 2011:-0.020 2012:+0.034 2013:+0.043 2014:+0.027 2015:-0.026 2016:+0.038 2017:-0.017 2018:-0.040 2019:+0.000 2020:-0.035 2021:+0.091

## STreversal  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0145 | >= 0.01 | PASS |
| ic_tstat_nw | 2.9630 | >= 2.5 | PASS |
| ic_half_min | 0.0141 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.3689 | >= 0.0 | PASS |
| coverage_pct | 99.8027 | >= 40.0 | PASS |
| avg_names_per_decile | 196.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0145  ic_tstat_nw=2.9630  icir=0.1522  ic_half1_mean=0.0141  ic_half2_mean=0.0148  ls_sharpe=-0.0287  ls_ann_return_pct=-0.4766  ls_ann_vol_pct=16.6209  ls_maxdd_pct=-65.5021  ls_hit_rate_pct=44.5652  turnover_d10_pct=86.3402  turnover_d1_pct=88.5964  coverage_pct=99.8027  avg_names_per_decile=196.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1956  ls_beta_mean=0.3489  ls_beta_fullwindow=0.4367  ls_sharpe_ex_top_years=-0.3690  ls_top_years=2001,2002,2004  ls_sharpe_bear=0.4589  ls_sharpe_bull=-0.1972
deciles D1..D10 avg %/mo: 0.832,0.738,0.820,0.947,0.916,0.939,1.077,1.146,1.150,1.113
hedge/regime (diagnostics): beta ex-ante 0.3489 full-window 0.4367  raw Sharpe 0.1956  Sharpe ex top years -0.3690 (2001,2002,2004)  bear/bull 0.4589/-0.1972
ic decay: h1=0.0027  h2=-0.0059  h3=-0.0021  h6=-0.0024  h12=0.0102
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0100 0.0807 -0.0780 -1.5000 392; MID 0.0080 0.0718 -0.0860 -1.7500 588; SMALL 0.0188 0.2091 0.4740 8.3900 979; ALL 0.0145 0.1522 0.1960 3.3700 1960
annual IC: 1999:+0.011 2000:+0.001 2001:+0.057 2002:+0.057 2003:+0.006 2004:+0.034 2005:-0.002 2006:+0.028 2007:-0.055 2008:-0.003 2009:+0.024 2010:+0.036 2011:-0.017 2012:+0.032 2013:+0.005 2014:+0.022 2015:+0.005 2016:+0.016 2017:-0.001 2018:-0.004 2019:+0.060 2020:+0.011 2021:+0.007

## ShareIss1Y  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0165 | >= 0.01 | PASS |
| ic_tstat_nw | 3.5164 | >= 2.5 | PASS |
| ic_half_min | 0.0142 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 7.1161 | >= 0.0 | PASS |
| coverage_pct | 90.4895 | >= 40.0 | PASS |
| avg_names_per_decile | 181.7 | >= 30 | PASS |
| ls_n_months | 270 | >= 243 | PASS |
stats: ic_mean=0.0165  ic_tstat_nw=3.5164  icir=0.2319  ic_half1_mean=0.0188  ic_half2_mean=0.0142  ls_sharpe=0.9086  ls_ann_return_pct=9.0639  ls_ann_vol_pct=9.9755  ls_maxdd_pct=-32.1855  ls_hit_rate_pct=61.8519  turnover_d10_pct=13.2970  turnover_d1_pct=14.7635  coverage_pct=90.4895  avg_names_per_decile=181.7  n_months=270  ls_n_months=270  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6051  ls_beta_mean=-0.3753  ls_beta_fullwindow=-0.3822  ls_sharpe_ex_top_years=0.7420  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.8072  ls_sharpe_bull=0.9159
deciles D1..D10 avg %/mo: 0.613,0.995,0.961,0.952,1.050,1.036,0.965,1.123,1.118,1.207
hedge/regime (diagnostics): beta ex-ante -0.3753 full-window -0.3822  raw Sharpe 0.6051  Sharpe ex top years 0.7420 (2000,2002,2021)  bear/bull 0.8072/0.9159
ic decay: h1=0.0156  h2=0.0152  h3=0.0141  h6=0.0129  h12=0.0120
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0209 0.2040 0.5960 8.5900 377; MID 0.0213 0.2560 0.5840 8.5300 552; SMALL 0.0103 0.1557 0.5150 6.2500 887; ALL 0.0165 0.2319 0.6050 7.1200 1817
annual IC: 1999:+0.018 2000:+0.061 2001:+0.045 2002:+0.048 2003:-0.018 2004:+0.003 2005:+0.006 2006:+0.013 2007:-0.014 2008:+0.037 2009:+0.007 2010:+0.001 2011:+0.044 2012:+0.002 2013:+0.014 2014:+0.027 2015:+0.021 2016:+0.012 2017:-0.004 2018:+0.025 2019:-0.005 2020:-0.039 2021:+0.075

## ShareIss5Y  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0158 | >= 0.01 | PASS |
| ic_tstat_nw | 3.6671 | >= 2.5 | PASS |
| ic_half_min | 0.0152 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.8818 | >= 0.0 | PASS |
| coverage_pct | 62.6064 | >= 40.0 | PASS |
| avg_names_per_decile | 152.2 | >= 30 | PASS |
| ls_n_months | 223 | >= 200 | PASS |
stats: ic_mean=0.0158  ic_tstat_nw=3.6671  icir=0.2559  ic_half1_mean=0.0152  ic_half2_mean=0.0164  ls_sharpe=1.0852  ls_ann_return_pct=8.2338  ls_ann_vol_pct=7.5870  ls_maxdd_pct=-18.1987  ls_hit_rate_pct=66.8161  turnover_d10_pct=6.4650  turnover_d1_pct=8.1128  coverage_pct=62.6064  avg_names_per_decile=152.2  n_months=223  ls_n_months=223  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6080  ls_beta_mean=-0.3037  ls_beta_fullwindow=-0.2357  ls_sharpe_ex_top_years=0.7495  ls_top_years=2004,2006,2021  ls_sharpe_bear=0.1504  ls_sharpe_bull=1.3926
deciles D1..D10 avg %/mo: 0.836,1.015,1.073,1.108,1.120,1.084,1.159,1.153,1.138,1.243
hedge/regime (diagnostics): beta ex-ante -0.3037 full-window -0.2357  raw Sharpe 0.6080  Sharpe ex top years 0.7495 (2004,2006,2021)  bear/bull 0.1504/1.3926
ic decay: h1=0.0150  h2=0.0150  h3=0.0150  h6=0.0149  h12=0.0128
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0197 0.2384 0.4970 6.6000 343; MID 0.0174 0.2359 0.4690 4.9700 470; SMALL 0.0124 0.1994 0.5490 4.7200 709; ALL 0.0158 0.2559 0.6080 4.8800 1522
annual IC: 2003:-0.004 2004:+0.013 2005:+0.008 2006:+0.017 2007:-0.003 2008:+0.041 2009:+0.003 2010:+0.012 2011:+0.050 2012:+0.003 2013:+0.009 2014:+0.022 2015:+0.028 2016:-0.002 2017:+0.025 2018:+0.041 2019:-0.005 2020:-0.021 2021:+0.054

## TotalAccruals  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0000 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.0108 | >= 2.5 | FAIL |
| ic_half_min | -0.0004 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.4658 | >= 0.0 | PASS |
| coverage_pct | 94.5565 | >= 40.0 | PASS |
| avg_names_per_decile | 185.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0000  ic_tstat_nw=-0.0108  icir=-0.0006  ic_half1_mean=-0.0004  ic_half2_mean=0.0003  ls_sharpe=-0.0926  ls_ann_return_pct=-0.7041  ls_ann_vol_pct=7.6031  ls_maxdd_pct=-35.5955  ls_hit_rate_pct=48.5507  turnover_d10_pct=18.4287  turnover_d1_pct=17.6512  coverage_pct=94.5565  avg_names_per_decile=185.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1911  ls_beta_mean=0.0998  ls_beta_fullwindow=0.1166  ls_sharpe_ex_top_years=-0.3612  ls_top_years=1999,2003,2009  ls_sharpe_bear=0.1952  ls_sharpe_bull=-0.3376
deciles D1..D10 avg %/mo: 0.818,1.039,0.976,0.954,0.995,1.043,1.063,1.134,1.161,0.940
hedge/regime (diagnostics): beta ex-ante 0.0998 full-window 0.1166  raw Sharpe 0.1911  Sharpe ex top years -0.3612 (1999,2003,2009)  bear/bull 0.1952/-0.3376
ic decay: h1=-0.0006  h2=-0.0005  h3=-0.0012  h6=-0.0026  h12=0.0008
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0043 0.0619 -0.0860 -0.9400 381; MID 0.0019 0.0303 -0.0130 -0.1400 561; SMALL -0.0032 -0.0608 0.3650 3.5300 914; ALL -0.0000 -0.0006 0.1910 1.4700 1857
annual IC: 1999:+0.014 2000:-0.015 2001:+0.003 2002:-0.025 2003:+0.009 2004:-0.004 2005:-0.003 2006:+0.018 2007:-0.029 2008:+0.011 2009:+0.014 2010:+0.004 2011:-0.004 2012:+0.007 2013:+0.012 2014:-0.003 2015:-0.001 2016:+0.003 2017:-0.006 2018:+0.022 2019:-0.004 2020:-0.005 2021:-0.016

## TrendFactor  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0171 | >= 0.01 | PASS |
| ic_tstat_nw | 2.7874 | >= 2.5 | PASS |
| ic_half_min | 0.0053 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 10.1209 | >= 0.0 | PASS |
| coverage_pct | 68.7213 | >= 40.0 | PASS |
| avg_names_per_decile | 163.4 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=0.0171  ic_tstat_nw=2.7874  icir=0.1786  ic_half1_mean=0.0290  ic_half2_mean=0.0053  ls_sharpe=0.5229  ls_ann_return_pct=8.9357  ls_ann_vol_pct=17.0872  ls_maxdd_pct=-27.3300  ls_hit_rate_pct=57.0175  turnover_d10_pct=63.4480  turnover_d1_pct=64.8978  coverage_pct=68.7213  avg_names_per_decile=163.4  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6122  ls_beta_mean=0.0508  ls_beta_fullwindow=0.0457  ls_sharpe_ex_top_years=0.2758  ls_top_years=2007,2009,2021  ls_sharpe_bear=0.8374  ls_sharpe_bull=0.4465
deciles D1..D10 avg %/mo: 0.786,0.879,0.965,1.067,1.103,1.137,1.276,1.258,1.345,1.629
hedge/regime (diagnostics): beta ex-ante 0.0508 full-window 0.0457  raw Sharpe 0.6122  Sharpe ex top years 0.2758 (2007,2009,2021)  bear/bull 0.8374/0.4465
ic decay: h1=0.0030  h2=0.0076  h3=0.0082  h6=-0.0050  h12=-0.0040
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0133 0.1092 0.5900 12.1900 355; MID 0.0175 0.1645 0.4930 7.9000 503; SMALL 0.0182 0.1954 0.5840 11.3300 774; ALL 0.0171 0.1786 0.6120 10.1200 1634
annual IC: 2003:+0.015 2004:+0.013 2005:+0.023 2006:+0.010 2007:+0.047 2008:-0.000 2009:+0.097 2010:+0.035 2011:+0.048 2012:-0.002 2013:+0.016 2014:-0.019 2015:+0.013 2016:+0.014 2017:-0.023 2018:+0.016 2019:+0.008 2020:+0.026 2021:-0.009

## VarCF  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0064 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.7561 | >= 2.5 | FAIL |
| ic_half_min | 0.0017 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | -3.9694 | >= 0.0 | FAIL |
| coverage_pct | 60.6782 | >= 40.0 | PASS |
| avg_names_per_decile | 143.7 | >= 30 | PASS |
| ls_n_months | 229 | >= 206 | PASS |
stats: ic_mean=0.0064  ic_tstat_nw=0.7561  icir=0.0555  ic_half1_mean=0.0017  ic_half2_mean=0.0110  ls_sharpe=0.4056  ls_ann_return_pct=5.5855  ls_ann_vol_pct=13.7711  ls_maxdd_pct=-40.8738  ls_hit_rate_pct=62.0087  turnover_d10_pct=5.9472  turnover_d1_pct=7.5606  coverage_pct=60.6782  avg_names_per_decile=143.7  n_months=229  ls_n_months=229  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.2256  ls_beta_mean=-0.7411  ls_beta_fullwindow=-0.7915  ls_sharpe_ex_top_years=0.1741  ls_top_years=2011,2014,2017  ls_sharpe_bear=-0.3048  ls_sharpe_bull=0.6397
deciles D1..D10 avg %/mo: 1.348,1.158,1.107,1.069,1.102,1.065,1.131,1.081,1.009,1.017
hedge/regime (diagnostics): beta ex-ante -0.7411 full-window -0.7915  raw Sharpe -0.2256  Sharpe ex top years 0.1741 (2011,2014,2017)  bear/bull -0.3048/0.6397
ic decay: h1=0.0062  h2=0.0058  h3=0.0051  h6=0.0058  h12=0.0067
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0028 0.0221 -0.1860 -4.1200 329; MID 0.0094 0.0716 0.0010 0.0200 441; SMALL 0.0059 0.0538 -0.2950 -5.5300 665; ALL 0.0064 0.0555 -0.2260 -3.9700 1436
annual IC: 2002:+0.036 2003:-0.053 2004:-0.016 2005:-0.011 2006:-0.008 2007:+0.026 2008:+0.062 2009:-0.055 2010:-0.009 2011:+0.071 2012:-0.027 2013:-0.030 2014:+0.012 2015:+0.043 2016:-0.002 2017:+0.014 2018:+0.063 2019:+0.014 2020:+0.003 2021:+0.019

## VolMkt  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0161 | >= 0.01 | PASS |
| ic_tstat_nw | 2.2532 | >= 2.5 | FAIL |
| ic_half_min | 0.0135 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.3753 | >= 0.0 | PASS |
| coverage_pct | 97.1325 | >= 40.0 | PASS |
| avg_names_per_decile | 190.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0161  ic_tstat_nw=2.2532  icir=0.1340  ic_half1_mean=0.0135  ic_half2_mean=0.0187  ls_sharpe=0.5509  ls_ann_return_pct=9.5535  ls_ann_vol_pct=17.3427  ls_maxdd_pct=-43.1606  ls_hit_rate_pct=65.5797  turnover_d10_pct=16.6133  turnover_d1_pct=14.2713  coverage_pct=97.1325  avg_names_per_decile=190.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1050  ls_beta_mean=-0.8602  ls_beta_fullwindow=-0.9441  ls_sharpe_ex_top_years=0.3196  ls_top_years=2000,2007,2011  ls_sharpe_bear=-0.3822  ls_sharpe_bull=1.1072
deciles D1..D10 avg %/mo: 0.804,0.867,1.024,1.004,1.034,1.088,1.035,0.998,1.010,1.002
hedge/regime (diagnostics): beta ex-ante -0.8602 full-window -0.9441  raw Sharpe 0.1050  Sharpe ex top years 0.3196 (2000,2007,2011)  bear/bull -0.3822/1.1072
ic decay: h1=0.0186  h2=0.0187  h3=0.0179  h6=0.0162  h12=0.0126
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0093 0.0522 -0.0710 -2.1200 387; MID 0.0192 0.1415 0.0860 2.0200 576; SMALL 0.0142 0.1275 0.0270 0.6200 944; ALL 0.0161 0.1340 0.1050 2.3800 1908
annual IC: 1999:-0.011 2000:+0.077 2001:+0.019 2002:+0.044 2003:-0.040 2004:-0.002 2005:+0.003 2006:+0.021 2007:+0.050 2008:+0.050 2009:-0.064 2010:-0.014 2011:+0.069 2012:-0.006 2013:+0.010 2014:+0.025 2015:+0.059 2016:-0.012 2017:+0.025 2018:+0.052 2019:-0.006 2020:-0.035 2021:+0.055

## VolSD  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0112 | >= 0.01 | PASS |
| ic_tstat_nw | 2.3624 | >= 2.5 | FAIL |
| ic_half_min | 0.0078 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.9482 | >= 0.0 | PASS |
| coverage_pct | 79.7655 | >= 40.0 | PASS |
| avg_names_per_decile | 171.6 | >= 30 | PASS |
| ls_n_months | 252 | >= 226 | PASS |
stats: ic_mean=0.0112  ic_tstat_nw=2.3624  icir=0.1388  ic_half1_mean=0.0147  ic_half2_mean=0.0078  ls_sharpe=0.5341  ls_ann_return_pct=6.0523  ls_ann_vol_pct=11.3312  ls_maxdd_pct=-34.7705  ls_hit_rate_pct=62.6984  turnover_d10_pct=12.7896  turnover_d1_pct=4.2455  coverage_pct=79.7655  avg_names_per_decile=171.6  n_months=252  ls_n_months=252  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1505  ls_beta_mean=-0.4108  ls_beta_fullwindow=-0.4682  ls_sharpe_ex_top_years=0.3981  ls_top_years=2001,2011,2015  ls_sharpe_bear=0.2735  ls_sharpe_bull=0.6872
deciles D1..D10 avg %/mo: 0.897,1.011,0.986,1.000,0.997,1.025,1.089,0.980,1.117,1.060
hedge/regime (diagnostics): beta ex-ante -0.4108 full-window -0.4682  raw Sharpe 0.1505  Sharpe ex top years 0.3981 (2001,2011,2015)  bear/bull 0.2735/0.6872
ic decay: h1=0.0113  h2=0.0105  h3=0.0102  h6=0.0098  h12=0.0079
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0118 0.1226 -0.1190 -1.6600 365; MID 0.0047 0.0480 -0.1770 -3.1100 527; SMALL 0.0115 0.1144 -0.2120 -4.1300 823; ALL 0.0112 0.1388 0.1510 1.9500 1716
annual IC: 2001:+0.046 2002:+0.051 2003:-0.026 2004:+0.016 2005:+0.004 2006:+0.010 2007:+0.001 2008:+0.056 2009:-0.042 2010:+0.018 2011:+0.044 2012:-0.006 2013:+0.019 2014:-0.019 2015:+0.034 2016:+0.016 2017:-0.005 2018:+0.020 2019:-0.005 2020:-0.017 2021:+0.021
