# RUN 011 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## VolumeTrend  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0114 | >= 0.01 | PASS |
| ic_tstat_nw | 2.8698 | >= 2.5 | PASS |
| ic_half_min | 0.0091 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.3999 | >= 0.0 | PASS |
| coverage_pct | 66.2952 | >= 40.0 | PASS |
| avg_names_per_decile | 157.7 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=0.0114  ic_tstat_nw=2.8698  icir=0.1941  ic_half1_mean=0.0091  ic_half2_mean=0.0136  ls_sharpe=0.6612  ls_ann_return_pct=5.0506  ls_ann_vol_pct=7.6389  ls_maxdd_pct=-32.6772  ls_hit_rate_pct=60.9649  turnover_d10_pct=10.1827  turnover_d1_pct=9.3816  coverage_pct=66.2952  avg_names_per_decile=157.7  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2954  ls_beta_mean=-0.2313  ls_beta_fullwindow=-0.2329  ls_sharpe_ex_top_years=0.3307  ls_top_years=2011,2014,2021  ls_sharpe_bear=0.0002  ls_sharpe_bull=0.8106
deciles D1..D10 avg %/mo: 1.023,1.128,1.137,1.136,1.101,1.102,1.209,1.143,1.213,1.223
hedge/regime (diagnostics): beta ex-ante -0.2313 full-window -0.2329  raw Sharpe 0.2954  Sharpe ex top years 0.3307 (2011,2014,2021)  bear/bull 0.0002/0.8106
ic decay: h1=0.0118  h2=0.0116  h3=0.0120  h6=0.0131  h12=0.0128
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0047 0.0485 -0.1000 -1.3700 349; MID 0.0170 0.2150 0.4230 4.5300 486; SMALL 0.0075 0.1315 0.1880 1.6300 740; ALL 0.0114 0.1941 0.2950 2.4000 1576
annual IC: 2003:-0.025 2004:-0.011 2005:+0.002 2006:+0.024 2007:+0.012 2008:+0.028 2009:-0.011 2010:+0.011 2011:+0.052 2012:+0.002 2013:-0.004 2014:+0.027 2015:+0.019 2016:+0.002 2017:+0.036 2018:+0.010 2019:+0.010 2020:-0.023 2021:+0.055

## XFIN  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0170 | >= 0.01 | PASS |
| ic_tstat_nw | 3.5702 | >= 2.5 | PASS |
| ic_half_min | 0.0105 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 6.5690 | >= 0.0 | PASS |
| coverage_pct | 95.6379 | >= 40.0 | PASS |
| avg_names_per_decile | 187.9 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0170  ic_tstat_nw=3.5702  icir=0.2299  ic_half1_mean=0.0235  ic_half2_mean=0.0105  ls_sharpe=0.7338  ls_ann_return_pct=8.6117  ls_ann_vol_pct=11.7366  ls_maxdd_pct=-25.6841  ls_hit_rate_pct=61.5942  turnover_d10_pct=14.7616  turnover_d1_pct=16.7104  coverage_pct=95.6379  avg_names_per_decile=187.9  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4775  ls_beta_mean=-0.4217  ls_beta_fullwindow=-0.4733  ls_sharpe_ex_top_years=0.4842  ls_top_years=2000,2006,2021  ls_sharpe_bear=0.5659  ls_sharpe_bull=0.8787
deciles D1..D10 avg %/mo: 0.618,0.915,0.868,1.017,1.029,1.014,1.064,1.160,1.090,1.166
hedge/regime (diagnostics): beta ex-ante -0.4217 full-window -0.4733  raw Sharpe 0.4775  Sharpe ex top years 0.4842 (2000,2006,2021)  bear/bull 0.5659/0.8787
ic decay: h1=0.0158  h2=0.0149  h3=0.0142  h6=0.0136  h12=0.0130
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0182 0.1722 0.2150 4.3400 384; MID 0.0162 0.1906 0.3290 5.6000 567; SMALL 0.0162 0.2363 0.7000 8.7100 927; ALL 0.0170 0.2299 0.4780 6.5700 1879
annual IC: 1999:+0.016 2000:+0.077 2001:+0.042 2002:+0.049 2003:-0.007 2004:+0.004 2005:+0.006 2006:+0.020 2007:+0.004 2008:+0.040 2009:+0.001 2010:+0.007 2011:+0.027 2012:+0.010 2013:-0.004 2014:+0.024 2015:+0.013 2016:+0.007 2017:-0.006 2018:+0.032 2019:-0.012 2020:-0.044 2021:+0.085

## cfp  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0246 | >= 0.01 | PASS |
| ic_tstat_nw | 3.6515 | >= 2.5 | PASS |
| ic_half_min | 0.0102 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 9.4499 | >= 0.0 | PASS |
| coverage_pct | 95.6727 | >= 40.0 | PASS |
| avg_names_per_decile | 188.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0246  ic_tstat_nw=3.6515  icir=0.2614  ic_half1_mean=0.0391  ic_half2_mean=0.0102  ls_sharpe=0.5101  ls_ann_return_pct=7.4656  ls_ann_vol_pct=14.6365  ls_maxdd_pct=-51.1069  ls_hit_rate_pct=52.8986  turnover_d10_pct=16.4432  turnover_d1_pct=16.7376  coverage_pct=95.6727  avg_names_per_decile=188.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6245  ls_beta_mean=-0.1404  ls_beta_fullwindow=-0.1297  ls_sharpe_ex_top_years=0.2458  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.8803  ls_sharpe_bull=0.3977
deciles D1..D10 avg %/mo: 0.617,0.683,0.858,0.909,0.899,1.008,1.058,1.139,1.366,1.405
hedge/regime (diagnostics): beta ex-ante -0.1404 full-window -0.1297  raw Sharpe 0.6245  Sharpe ex top years 0.2458 (2000,2002,2021)  bear/bull 0.8803/0.3977
ic decay: h1=0.0174  h2=0.0166  h3=0.0168  h6=0.0131  h12=0.0152
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0175 0.1473 0.3330 5.6300 384; MID 0.0222 0.2002 0.5640 10.5000 567; SMALL 0.0282 0.3066 0.6580 10.2600 927; ALL 0.0246 0.2614 0.6250 9.4500 1879
annual IC: 1999:+0.011 2000:+0.099 2001:+0.085 2002:+0.074 2003:+0.027 2004:+0.042 2005:+0.029 2006:+0.031 2007:-0.026 2008:+0.032 2009:+0.041 2010:+0.002 2011:+0.006 2012:+0.007 2013:+0.029 2014:+0.043 2015:-0.021 2016:+0.048 2017:-0.020 2018:-0.016 2019:-0.011 2020:-0.049 2021:+0.104

## dNoa  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0077 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.1885 | >= 2.5 | FAIL |
| ic_half_min | -0.0002 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 7.7423 | >= 0.0 | PASS |
| coverage_pct | 95.2320 | >= 40.0 | PASS |
| avg_names_per_decile | 187.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0077  ic_tstat_nw=2.1885  icir=0.1476  ic_half1_mean=0.0156  ic_half2_mean=-0.0002  ls_sharpe=0.8166  ls_ann_return_pct=6.6248  ls_ann_vol_pct=8.1125  ls_maxdd_pct=-27.3321  ls_hit_rate_pct=56.1594  turnover_d10_pct=18.3983  turnover_d1_pct=15.6718  coverage_pct=95.2320  avg_names_per_decile=187.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.9474  ls_beta_mean=-0.0231  ls_beta_fullwindow=-0.0685  ls_sharpe_ex_top_years=0.3954  ls_top_years=1999,2000,2001  ls_sharpe_bear=1.0960  ls_sharpe_bull=0.5739
deciles D1..D10 avg %/mo: 0.557,0.805,0.985,0.967,1.036,1.046,1.075,1.154,1.248,1.202
hedge/regime (diagnostics): beta ex-ante -0.0231 full-window -0.0685  raw Sharpe 0.9474  Sharpe ex top years 0.3954 (1999,2000,2001)  bear/bull 1.0960/0.5739
ic decay: h1=0.0055  h2=0.0053  h3=0.0050  h6=0.0034  h12=0.0065
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0108 0.1258 0.2800 4.1700 383; MID 0.0088 0.1370 0.5560 5.5100 565; SMALL 0.0046 0.0860 1.0860 9.6200 922; ALL 0.0077 0.1476 0.9470 7.7400 1871
annual IC: 1999:+0.028 2000:+0.039 2001:+0.041 2002:+0.018 2003:+0.009 2004:-0.008 2005:+0.009 2006:+0.017 2007:-0.015 2008:+0.018 2009:+0.016 2010:+0.002 2011:+0.001 2012:+0.017 2013:+0.016 2014:+0.012 2015:-0.009 2016:+0.007 2017:-0.013 2018:+0.016 2019:-0.021 2020:-0.039 2021:+0.016

## grcapx  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0041 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.3746 | >= 2.5 | FAIL |
| ic_half_min | 0.0015 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.0204 | >= 0.0 | PASS |
| coverage_pct | 81.0125 | >= 40.0 | PASS |
| avg_names_per_decile | 159.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0041  ic_tstat_nw=1.3746  icir=0.0888  ic_half1_mean=0.0067  ic_half2_mean=0.0015  ls_sharpe=0.4880  ls_ann_return_pct=3.3960  ls_ann_vol_pct=6.9593  ls_maxdd_pct=-19.0226  ls_hit_rate_pct=52.5362  turnover_d10_pct=12.3794  turnover_d1_pct=11.6706  coverage_pct=81.0125  avg_names_per_decile=159.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.5553  ls_beta_mean=-0.0361  ls_beta_fullwindow=-0.0788  ls_sharpe_ex_top_years=0.2626  ls_top_years=2001,2003,2010  ls_sharpe_bear=0.7710  ls_sharpe_bull=0.3262
deciles D1..D10 avg %/mo: 0.779,1.000,0.924,1.068,1.026,1.086,1.107,1.086,1.162,1.114
hedge/regime (diagnostics): beta ex-ante -0.0361 full-window -0.0788  raw Sharpe 0.5553  Sharpe ex top years 0.2626 (2001,2003,2010)  bear/bull 0.7710/0.3262
ic decay: h1=0.0041  h2=0.0030  h3=0.0039  h6=0.0044  h12=0.0027
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0045 0.0524 0.2280 3.0400 342; MID 0.0018 0.0284 0.0070 0.0700 489; SMALL 0.0038 0.0819 0.4730 4.0900 759; ALL 0.0041 0.0888 0.5550 4.0200 1591
annual IC: 1999:+0.005 2000:+0.005 2001:+0.022 2002:+0.039 2003:+0.013 2004:-0.014 2005:+0.003 2006:+0.009 2007:-0.023 2008:+0.030 2009:-0.018 2010:+0.022 2011:-0.007 2012:+0.026 2013:+0.006 2014:+0.017 2015:-0.007 2016:+0.013 2017:-0.016 2018:+0.004 2019:-0.011 2020:-0.024 2021:+0.001

## grcapx3y  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0028 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.8944 | >= 2.5 | FAIL |
| ic_half_min | 0.0012 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.9708 | >= 0.0 | PASS |
| coverage_pct | 72.3367 | >= 40.0 | PASS |
| avg_names_per_decile | 142.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0028  ic_tstat_nw=0.8944  icir=0.0592  ic_half1_mean=0.0044  ic_half2_mean=0.0012  ls_sharpe=0.4455  ls_ann_return_pct=3.4192  ls_ann_vol_pct=7.6749  ls_maxdd_pct=-22.1667  ls_hit_rate_pct=53.9855  turnover_d10_pct=11.8899  turnover_d1_pct=11.3564  coverage_pct=72.3367  avg_names_per_decile=142.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.5235  ls_beta_mean=0.0021  ls_beta_fullwindow=-0.0420  ls_sharpe_ex_top_years=0.2325  ls_top_years=2001,2003,2010  ls_sharpe_bear=0.7775  ls_sharpe_bull=0.3437
deciles D1..D10 avg %/mo: 0.772,1.039,0.974,0.991,1.036,1.105,1.013,1.101,1.246,1.103
hedge/regime (diagnostics): beta ex-ante 0.0021 full-window -0.0420  raw Sharpe 0.5235  Sharpe ex top years 0.2325 (2001,2003,2010)  bear/bull 0.7775/0.3437
ic decay: h1=0.0027  h2=0.0026  h3=0.0041  h6=0.0047  h12=0.0028
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0042 0.0477 0.2560 4.3100 319; MID 0.0015 0.0220 0.1240 1.4400 440; SMALL 0.0014 0.0288 0.5170 5.7100 661; ALL 0.0028 0.0592 0.5230 3.9700 1421
annual IC: 1999:-0.000 2000:-0.014 2001:+0.023 2002:+0.032 2003:+0.009 2004:-0.011 2005:+0.002 2006:+0.012 2007:-0.022 2008:+0.033 2009:-0.015 2010:+0.021 2011:-0.003 2012:+0.024 2013:+0.008 2014:+0.016 2015:-0.008 2016:+0.016 2017:-0.019 2018:+0.006 2019:-0.016 2020:-0.028 2021:-0.003

## roaq  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0208 | >= 0.01 | PASS |
| ic_tstat_nw | 3.3661 | >= 2.5 | PASS |
| ic_half_min | 0.0177 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 5.2833 | >= 0.0 | PASS |
| coverage_pct | 96.2922 | >= 40.0 | PASS |
| avg_names_per_decile | 189.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0208  ic_tstat_nw=3.3661  icir=0.2225  ic_half1_mean=0.0238  ic_half2_mean=0.0177  ls_sharpe=0.7053  ls_ann_return_pct=9.9473  ls_ann_vol_pct=14.1032  ls_maxdd_pct=-32.7440  ls_hit_rate_pct=60.8696  turnover_d10_pct=21.0822  turnover_d1_pct=26.5615  coverage_pct=96.2922  avg_names_per_decile=189.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3217  ls_beta_mean=-0.4906  ls_beta_fullwindow=-0.5840  ls_sharpe_ex_top_years=0.3863  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.3558  ls_sharpe_bull=0.9934
deciles D1..D10 avg %/mo: 0.661,1.001,0.901,0.965,0.890,0.976,1.074,1.095,1.062,1.101
hedge/regime (diagnostics): beta ex-ante -0.4906 full-window -0.5840  raw Sharpe 0.3217  Sharpe ex top years 0.3863 (2000,2002,2021)  bear/bull 0.3558/0.9934
ic decay: h1=0.0199  h2=0.0207  h3=0.0190  h6=0.0112  h12=0.0115
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0231 0.1972 0.3770 6.5800 382; MID 0.0204 0.1995 0.2960 5.5400 569; SMALL 0.0206 0.2257 0.2520 4.4700 939; ALL 0.0208 0.2225 0.3220 5.2800 1891
annual IC: 1999:+0.004 2000:+0.104 2001:+0.036 2002:+0.078 2003:-0.016 2004:+0.022 2005:+0.019 2006:-0.010 2007:+0.057 2008:+0.027 2009:-0.042 2010:-0.020 2011:+0.053 2012:-0.001 2013:-0.019 2014:+0.011 2015:+0.037 2016:-0.008 2017:+0.036 2018:+0.040 2019:-0.001 2020:-0.019 2021:+0.090

## zerotrade12M  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0180 | >= 0.01 | PASS |
| ic_tstat_nw | 2.8315 | >= 2.5 | PASS |
| ic_half_min | 0.0168 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.6920 | >= 0.0 | PASS |
| coverage_pct | 94.6675 | >= 40.0 | PASS |
| avg_names_per_decile | 186.7 | >= 30 | PASS |
| ls_n_months | 275 | >= 247 | PASS |
stats: ic_mean=0.0180  ic_tstat_nw=2.8315  icir=0.1759  ic_half1_mean=0.0168  ic_half2_mean=0.0191  ls_sharpe=0.6917  ls_ann_return_pct=8.9655  ls_ann_vol_pct=12.9619  ls_maxdd_pct=-34.9556  ls_hit_rate_pct=64.7273  turnover_d10_pct=13.2480  turnover_d1_pct=7.8220  coverage_pct=94.6675  avg_names_per_decile=186.7  n_months=275  ls_n_months=275  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2185  ls_beta_mean=-0.6685  ls_beta_fullwindow=-0.6986  ls_sharpe_ex_top_years=0.4495  ls_top_years=2000,2007,2011  ls_sharpe_bear=0.0978  ls_sharpe_bull=1.0498
deciles D1..D10 avg %/mo: 0.758,0.843,1.033,1.007,1.012,1.075,1.127,1.116,1.071,1.065
hedge/regime (diagnostics): beta ex-ante -0.6685 full-window -0.6986  raw Sharpe 0.2185  Sharpe ex top years 0.4495 (2000,2007,2011)  bear/bull 0.0978/1.0498
ic decay: h1=0.0173  h2=0.0171  h3=0.0159  h6=0.0137  h12=0.0136
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0114 0.0650 -0.0670 -1.8800 383; MID 0.0185 0.1546 0.1000 1.8700 564; SMALL 0.0175 0.2004 0.2380 3.7400 918; ALL 0.0180 0.1759 0.2180 3.6900 1866
annual IC: 1999:-0.013 2000:+0.063 2001:+0.034 2002:+0.057 2003:-0.032 2004:-0.002 2005:-0.003 2006:+0.029 2007:+0.027 2008:+0.057 2009:-0.037 2010:-0.007 2011:+0.065 2012:+0.004 2013:+0.007 2014:+0.028 2015:+0.051 2016:+0.000 2017:+0.017 2018:+0.049 2019:+0.005 2020:-0.036 2021:+0.048

## zerotrade1M  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0155 | >= 0.01 | PASS |
| ic_tstat_nw | 2.6261 | >= 2.5 | PASS |
| ic_half_min | 0.0148 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.5601 | >= 0.0 | PASS |
| coverage_pct | 99.3756 | >= 40.0 | PASS |
| avg_names_per_decile | 195.3 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0155  ic_tstat_nw=2.6261  icir=0.1581  ic_half1_mean=0.0148  ic_half2_mean=0.0163  ls_sharpe=0.4414  ls_ann_return_pct=6.8923  ls_ann_vol_pct=15.6130  ls_maxdd_pct=-45.8246  ls_hit_rate_pct=59.7826  turnover_d10_pct=39.5296  turnover_d1_pct=40.1126  coverage_pct=99.3756  avg_names_per_decile=195.3  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1348  ls_beta_mean=-0.6790  ls_beta_fullwindow=-0.7275  ls_sharpe_ex_top_years=0.2812  ls_top_years=2007,2011,2014  ls_sharpe_bear=0.1328  ls_sharpe_bull=0.7002
deciles D1..D10 avg %/mo: 0.768,0.907,0.975,1.034,0.986,1.078,0.939,1.016,0.975,0.981
hedge/regime (diagnostics): beta ex-ante -0.6790 full-window -0.7275  raw Sharpe 0.1348  Sharpe ex top years 0.2812 (2007,2011,2014)  bear/bull 0.1328/0.7002
ic decay: h1=0.0161  h2=0.0177  h3=0.0169  h6=0.0149  h12=0.0141
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0134 0.0755 -0.0070 -0.2000 392; MID 0.0192 0.1614 0.0410 0.8600 585; SMALL 0.0110 0.1395 -0.0020 -0.0200 974; ALL 0.0155 0.1581 0.1350 2.5600 1952
annual IC: 1999:-0.018 2000:+0.048 2001:+0.041 2002:+0.050 2003:-0.032 2004:+0.003 2005:-0.002 2006:+0.025 2007:+0.026 2008:+0.053 2009:-0.039 2010:-0.005 2011:+0.058 2012:+0.003 2013:+0.001 2014:+0.031 2015:+0.046 2016:-0.007 2017:+0.020 2018:+0.045 2019:+0.009 2020:-0.045 2021:+0.046

## zerotrade6M  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0185 | >= 0.01 | PASS |
| ic_tstat_nw | 2.9273 | >= 2.5 | PASS |
| ic_half_min | 0.0160 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.1904 | >= 0.0 | PASS |
| coverage_pct | 97.5928 | >= 40.0 | PASS |
| avg_names_per_decile | 191.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0185  ic_tstat_nw=2.9273  icir=0.1796  ic_half1_mean=0.0160  ic_half2_mean=0.0211  ls_sharpe=0.6019  ls_ann_return_pct=8.9211  ls_ann_vol_pct=14.8226  ls_maxdd_pct=-41.5041  ls_hit_rate_pct=63.4058  turnover_d10_pct=16.3030  turnover_d1_pct=11.6148  coverage_pct=97.5928  avg_names_per_decile=191.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2264  ls_beta_mean=-0.7025  ls_beta_fullwindow=-0.7319  ls_sharpe_ex_top_years=0.4265  ls_top_years=2000,2007,2011  ls_sharpe_bear=0.0994  ls_sharpe_bull=0.9544
deciles D1..D10 avg %/mo: 0.681,0.971,0.935,0.982,1.014,1.043,1.100,1.034,1.032,1.030
hedge/regime (diagnostics): beta ex-ante -0.7025 full-window -0.7319  raw Sharpe 0.2264  Sharpe ex top years 0.4265 (2000,2007,2011)  bear/bull 0.0994/0.9544
ic decay: h1=0.0190  h2=0.0184  h3=0.0179  h6=0.0159  h12=0.0145
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0129 0.0723 -0.0980 -2.9500 388; MID 0.0206 0.1678 0.0850 1.7100 577; SMALL 0.0169 0.1954 0.1690 2.8000 950; ALL 0.0185 0.1796 0.2260 4.1900 1917
annual IC: 1999:-0.023 2000:+0.063 2001:+0.034 2002:+0.054 2003:-0.031 2004:+0.001 2005:-0.005 2006:+0.030 2007:+0.029 2008:+0.056 2009:-0.036 2010:-0.002 2011:+0.065 2012:+0.001 2013:+0.005 2014:+0.030 2015:+0.057 2016:-0.001 2017:+0.022 2018:+0.050 2019:+0.008 2020:-0.041 2021:+0.062

## BidAskSpreadFlip  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0206 | >= 0.01 | PASS |
| ic_tstat_nw | 2.7628 | >= 2.5 | PASS |
| ic_half_min | 0.0198 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.0664 | >= 0.0 | PASS |
| coverage_pct | 99.1272 | >= 40.0 | PASS |
| avg_names_per_decile | 194.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0206  ic_tstat_nw=2.7628  icir=0.1651  ic_half1_mean=0.0198  ic_half2_mean=0.0214  ls_sharpe=0.4848  ls_ann_return_pct=8.7247  ls_ann_vol_pct=17.9973  ls_maxdd_pct=-48.9848  ls_hit_rate_pct=61.9565  turnover_d10_pct=66.0687  turnover_d1_pct=59.9903  coverage_pct=99.1272  avg_names_per_decile=194.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0458  ls_beta_mean=-0.9443  ls_beta_fullwindow=-0.9791  ls_sharpe_ex_top_years=0.2951  ls_top_years=2000,2014,2021  ls_sharpe_bear=-0.2436  ls_sharpe_bull=0.9564
deciles D1..D10 avg %/mo: 0.881,0.951,0.971,0.958,0.963,0.977,0.978,0.983,1.018,0.970
hedge/regime (diagnostics): beta ex-ante -0.9443 full-window -0.9791  raw Sharpe 0.0458  Sharpe ex top years 0.2951 (2000,2014,2021)  bear/bull -0.2436/0.9564
ic decay: h1=0.0190  h2=0.0182  h3=0.0178  h6=0.0138  h12=0.0137
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0179 0.1195 0.0880 2.4800 391; MID 0.0196 0.1412 0.0320 0.8200 585; SMALL 0.0216 0.1901 0.0670 1.5300 970; ALL 0.0206 0.1651 0.0460 1.0700 1947
annual IC: 1999:-0.008 2000:+0.097 2001:+0.026 2002:+0.056 2003:-0.035 2004:-0.006 2005:+0.013 2006:+0.013 2007:+0.028 2008:+0.044 2009:-0.027 2010:-0.008 2011:+0.065 2012:-0.000 2013:-0.008 2014:+0.049 2015:+0.042 2016:-0.007 2017:+0.019 2018:+0.053 2019:+0.009 2020:-0.030 2021:+0.088
