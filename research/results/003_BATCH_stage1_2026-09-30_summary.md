# RUN 003 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## AM  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0098 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.2581 | >= 2.5 | FAIL |
| ic_half_min | 0.0028 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.7181 | >= 0.0 | PASS |
| coverage_pct | 99.5949 | >= 40.0 | PASS |
| avg_names_per_decile | 195.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0098  ic_tstat_nw=1.2581  icir=0.0842  ic_half1_mean=0.0168  ic_half2_mean=0.0028  ls_sharpe=-0.1488  ls_ann_return_pct=-3.1676  ls_ann_vol_pct=21.2915  ls_maxdd_pct=-80.1383  ls_hit_rate_pct=41.6667  turnover_d10_pct=12.5037  turnover_d1_pct=13.3560  coverage_pct=99.5949  avg_names_per_decile=195.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2160  ls_beta_mean=0.2511  ls_beta_fullwindow=0.3388  ls_sharpe_ex_top_years=-0.4494  ls_top_years=2003,2009,2021  ls_sharpe_bear=0.2674  ls_sharpe_bull=-0.2362
deciles D1..D10 avg %/mo: 0.818,0.783,0.903,0.843,0.946,0.916,0.984,1.068,1.189,1.211
hedge/regime (diagnostics): beta ex-ante 0.2511 full-window 0.3388  raw Sharpe 0.2160  Sharpe ex top years -0.4494 (2003,2009,2021)  bear/bull 0.2674/-0.2362
ic decay: h1=0.0069  h2=0.0066  h3=0.0066  h6=0.0053  h12=0.0068
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0040 0.0268 0.1090 2.6300 392; MID 0.0076 0.0606 0.1200 2.7400 587; SMALL 0.0124 0.1151 0.2800 6.1200 977; ALL 0.0098 0.0842 0.2160 4.7200 1956
annual IC: 1999:-0.023 2000:+0.061 2001:+0.067 2002:+0.007 2003:+0.057 2004:+0.028 2005:-0.001 2006:+0.029 2007:-0.071 2008:-0.017 2009:+0.056 2010:+0.008 2011:-0.039 2012:+0.032 2013:+0.027 2014:+0.017 2015:-0.028 2016:+0.047 2017:-0.036 2018:-0.048 2019:+0.012 2020:-0.040 2021:+0.079

## Accruals  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0048 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.8353 | >= 2.5 | FAIL |
| ic_half_min | 0.0021 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.9203 | >= 0.0 | PASS |
| coverage_pct | 76.6645 | >= 40.0 | PASS |
| avg_names_per_decile | 150.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0048  ic_tstat_nw=1.8353  icir=0.1204  ic_half1_mean=0.0075  ic_half2_mean=0.0021  ls_sharpe=0.3292  ls_ann_return_pct=2.4880  ls_ann_vol_pct=7.5586  ls_maxdd_pct=-26.4682  ls_hit_rate_pct=56.1594  turnover_d10_pct=19.1350  turnover_d1_pct=19.5157  coverage_pct=76.6645  avg_names_per_decile=150.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4022  ls_beta_mean=0.0105  ls_beta_fullwindow=0.0365  ls_sharpe_ex_top_years=0.1069  ls_top_years=1999,2002,2005  ls_sharpe_bear=0.5808  ls_sharpe_bull=0.0747
deciles D1..D10 avg %/mo: 0.814,0.941,1.056,0.994,1.126,1.033,1.054,1.197,1.215,1.057
hedge/regime (diagnostics): beta ex-ante 0.0105 full-window 0.0365  raw Sharpe 0.4022  Sharpe ex top years 0.1069 (1999,2002,2005)  bear/bull 0.5808/0.0747
ic decay: h1=-0.0001  h2=0.0005  h3=0.0012  h6=-0.0019  h12=0.0024
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0046 0.0662 -0.0110 -0.1200 322; MID 0.0015 0.0257 0.2080 2.4300 466; SMALL 0.0066 0.1381 0.4400 4.4100 717; ALL 0.0048 0.1204 0.4020 2.9200 1506
annual IC: 1999:+0.029 2000:-0.000 2001:+0.007 2002:+0.011 2003:+0.016 2004:+0.010 2005:+0.017 2006:-0.009 2007:-0.011 2008:+0.009 2009:+0.010 2010:-0.001 2011:+0.003 2012:-0.000 2013:+0.010 2014:+0.019 2015:-0.006 2016:-0.012 2017:-0.006 2018:+0.028 2019:-0.032 2020:-0.009 2021:+0.029

## AnnouncementReturn  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0092 | >= 0.01 | FAIL |
| ic_tstat_nw | 2.2764 | >= 2.5 | FAIL |
| ic_half_min | 0.0081 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.5128 | >= 0.0 | PASS |
| coverage_pct | 66.5305 | >= 40.0 | PASS |
| avg_names_per_decile | 173.5 | >= 30 | PASS |
| ls_n_months | 208 | >= 187 | PASS |
stats: ic_mean=0.0092  ic_tstat_nw=2.2764  icir=0.1665  ic_half1_mean=0.0102  ic_half2_mean=0.0081  ls_sharpe=0.6428  ls_ann_return_pct=5.1899  ls_ann_vol_pct=8.0739  ls_maxdd_pct=-21.9985  ls_hit_rate_pct=57.2115  turnover_d10_pct=36.2734  turnover_d1_pct=36.1909  coverage_pct=66.5305  avg_names_per_decile=173.5  n_months=208  ls_n_months=208  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2960  ls_beta_mean=-0.1786  ls_beta_fullwindow=-0.2074  ls_sharpe_ex_top_years=0.3425  ls_top_years=2007,2013,2017  ls_sharpe_bear=-0.9884  ls_sharpe_bull=1.1295
deciles D1..D10 avg %/mo: 1.077,1.022,1.016,1.077,1.012,1.132,1.114,1.006,1.096,1.287
hedge/regime (diagnostics): beta ex-ante -0.1786 full-window -0.2074  raw Sharpe 0.2960  Sharpe ex top years 0.3425 (2007,2013,2017)  bear/bull -0.9884/1.1295
ic decay: h1=0.0035  h2=0.0069  h3=0.0090  h6=0.0074  h12=0.0012
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0068 0.0853 0.1170 1.8700 346; MID 0.0129 0.1824 0.3300 3.6400 526; SMALL 0.0067 0.1177 0.2320 1.8400 870; ALL 0.0092 0.1665 0.2470 2.0500 1734
annual IC: 2004:+0.069 2005:+0.018 2006:+0.005 2007:+0.049 2008:-0.010 2009:-0.030 2010:+0.002 2011:+0.026 2012:+0.007 2013:+0.006 2014:+0.012 2015:+0.017 2016:-0.011 2017:+0.008 2018:+0.012 2019:-0.013 2020:+0.003 2021:+0.035

## BMdec  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0045 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.8173 | >= 2.5 | FAIL |
| ic_half_min | -0.0028 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.6849 | >= 0.0 | PASS |
| coverage_pct | 92.1102 | >= 40.0 | PASS |
| avg_names_per_decile | 185.0 | >= 30 | PASS |
| ls_n_months | 270 | >= 243 | PASS |
stats: ic_mean=0.0045  ic_tstat_nw=0.8173  icir=0.0580  ic_half1_mean=0.0118  ic_half2_mean=-0.0028  ls_sharpe=0.0539  ls_ann_return_pct=0.6070  ls_ann_vol_pct=11.2623  ls_maxdd_pct=-63.9621  ls_hit_rate_pct=49.2593  turnover_d10_pct=8.8605  turnover_d1_pct=6.8474  coverage_pct=92.1102  avg_names_per_decile=185.0  n_months=270  ls_n_months=270  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3108  ls_beta_mean=-0.0470  ls_beta_fullwindow=-0.0318  ls_sharpe_ex_top_years=-0.4233  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.0891  ls_sharpe_bull=0.0760
deciles D1..D10 avg %/mo: 0.842,0.857,0.847,0.862,0.922,0.965,1.012,1.088,1.037,1.149
hedge/regime (diagnostics): beta ex-ante -0.0470 full-window -0.0318  raw Sharpe 0.3108  Sharpe ex top years -0.4233 (2000,2003,2021)  bear/bull 0.0891/0.0760
ic decay: h1=0.0039  h2=0.0035  h3=0.0042  h6=0.0041  h12=0.0052
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0018 -0.0165 0.1440 2.4600 380; MID 0.0026 0.0301 0.2010 2.7600 559; SMALL 0.0061 0.0838 0.2350 2.7800 909; ALL 0.0045 0.0580 0.3110 3.6800 1849
annual IC: 1999:-0.024 2000:+0.059 2001:+0.047 2002:+0.019 2003:+0.018 2004:+0.008 2005:+0.011 2006:+0.019 2007:-0.047 2008:+0.017 2009:+0.006 2010:-0.004 2011:-0.017 2012:+0.021 2013:+0.006 2014:+0.009 2015:-0.022 2016:+0.038 2017:-0.037 2018:-0.033 2019:-0.007 2020:-0.041 2021:+0.045

## BPEBM  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0092 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.0572 | >= 2.5 | FAIL |
| ic_half_min | -0.0112 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 0.3875 | >= 0.0 | PASS |
| coverage_pct | 75.6276 | >= 40.0 | PASS |
| avg_names_per_decile | 148.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0092  ic_tstat_nw=-2.0572  icir=-0.1303  ic_half1_mean=-0.0072  ic_half2_mean=-0.0112  ls_sharpe=-0.0362  ls_ann_return_pct=-0.3808  ls_ann_vol_pct=10.5116  ls_maxdd_pct=-55.6406  ls_hit_rate_pct=46.3768  turnover_d10_pct=20.0127  turnover_d1_pct=17.6738  coverage_pct=75.6276  avg_names_per_decile=148.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0343  ls_beta_mean=0.2442  ls_beta_fullwindow=0.2254  ls_sharpe_ex_top_years=-0.4483  ls_top_years=1999,2001,2020  ls_sharpe_bear=0.5893  ls_sharpe_bull=-0.5003
deciles D1..D10 avg %/mo: 0.993,0.967,0.968,0.926,0.899,1.079,0.930,1.087,0.876,1.026
hedge/regime (diagnostics): beta ex-ante 0.2442 full-window 0.2254  raw Sharpe 0.0343  Sharpe ex top years -0.4483 (1999,2001,2020)  bear/bull 0.5893/-0.5003
ic decay: h1=-0.0091  h2=-0.0088  h3=-0.0078  h6=-0.0079  h12=-0.0058
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0010 0.0093 0.1340 1.9400 321; MID -0.0058 -0.0642 -0.0040 -0.0600 454; SMALL -0.0145 -0.2045 -0.1850 -2.0100 709; ALL -0.0092 -0.1303 0.0340 0.3900 1485
annual IC: 1999:+0.036 2000:-0.044 2001:-0.015 2002:-0.029 2003:+0.004 2004:-0.006 2005:+0.005 2006:-0.024 2007:-0.003 2008:+0.004 2009:+0.001 2010:-0.002 2011:-0.004 2012:-0.021 2013:-0.024 2014:-0.029 2015:-0.015 2016:-0.016 2017:+0.022 2018:+0.014 2019:-0.023 2020:+0.029 2021:-0.071

## Beta  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0091 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.9652 | >= 2.5 | FAIL |
| ic_half_min | -0.0106 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.1239 | >= 0.0 | PASS |
| coverage_pct | 85.3945 | >= 40.0 | PASS |
| avg_names_per_decile | 180.9 | >= 30 | PASS |
| ls_n_months | 256 | >= 230 | PASS |
stats: ic_mean=-0.0091  ic_tstat_nw=-0.9652  icir=-0.0606  ic_half1_mean=-0.0075  ic_half2_mean=-0.0106  ls_sharpe=-0.6077  ls_ann_return_pct=-10.3094  ls_ann_vol_pct=16.9638  ls_maxdd_pct=-91.9296  ls_hit_rate_pct=37.1094  turnover_d10_pct=10.5164  turnover_d1_pct=10.8681  coverage_pct=85.3945  avg_names_per_decile=180.9  n_months=256  ls_n_months=256  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0493  ls_beta_mean=1.0497  ls_beta_fullwindow=1.1131  ls_sharpe_ex_top_years=-0.9745  ls_top_years=2008,2009,2020  ls_sharpe_bear=0.1735  ls_sharpe_bull=-1.1630
deciles D1..D10 avg %/mo: 0.834,0.971,0.969,0.966,1.052,0.910,0.993,0.915,0.962,0.928
hedge/regime (diagnostics): beta ex-ante 1.0497 full-window 1.1131  raw Sharpe 0.0493  Sharpe ex top years -0.9745 (2008,2009,2020)  bear/bull 0.1735/-1.1630
ic decay: h1=-0.0094  h2=-0.0082  h3=-0.0073  h6=-0.0073  h12=-0.0066
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0182 -0.0930 -0.0180 -0.4400 374; MID -0.0144 -0.0854 -0.0530 -1.2900 551; SMALL -0.0035 -0.0272 0.0990 2.2200 882; ALL -0.0091 -0.0606 0.0490 1.1200 1808
annual IC: 2000:-0.174 2001:-0.029 2002:-0.075 2003:+0.036 2004:-0.020 2005:+0.006 2006:+0.002 2007:-0.008 2008:-0.049 2009:+0.076 2010:+0.028 2011:-0.058 2012:+0.022 2013:+0.036 2014:-0.031 2015:-0.060 2016:+0.009 2017:+0.006 2018:-0.075 2019:+0.030 2020:+0.046 2021:-0.025

## BetaFP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0123 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.2760 | >= 2.5 | FAIL |
| ic_half_min | -0.0144 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.1291 | >= 0.0 | PASS |
| coverage_pct | 83.1090 | >= 40.0 | PASS |
| avg_names_per_decile | 178.1 | >= 30 | PASS |
| ls_n_months | 253 | >= 227 | PASS |
stats: ic_mean=-0.0123  ic_tstat_nw=-1.2760  icir=-0.0778  ic_half1_mean=-0.0144  ic_half2_mean=-0.0103  ls_sharpe=-0.6554  ls_ann_return_pct=-11.4838  ls_ann_vol_pct=17.5227  ls_maxdd_pct=-94.8368  ls_hit_rate_pct=33.9921  turnover_d10_pct=12.3938  turnover_d1_pct=12.3338  coverage_pct=83.1090  avg_names_per_decile=178.1  n_months=253  ls_n_months=253  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0468  ls_beta_mean=1.1610  ls_beta_fullwindow=1.2201  ls_sharpe_ex_top_years=-1.0305  ls_top_years=2009,2016,2020  ls_sharpe_bear=-0.0219  ls_sharpe_bull=-1.2334
deciles D1..D10 avg %/mo: 0.948,1.047,1.049,1.046,1.058,1.092,1.018,1.039,0.967,1.042
hedge/regime (diagnostics): beta ex-ante 1.1610 full-window 1.2201  raw Sharpe 0.0468  Sharpe ex top years -1.0305 (2009,2016,2020)  bear/bull -0.0219/-1.2334
ic decay: h1=-0.0119  h2=-0.0125  h3=-0.0109  h6=-0.0111  h12=-0.0115
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0140 -0.0682 -0.0610 -1.6200 371; MID -0.0144 -0.0802 0.0170 0.4500 544; SMALL -0.0080 -0.0586 0.1890 4.5000 864; ALL -0.0123 -0.0778 0.0470 1.1300 1781
annual IC: 2000:-0.028 2001:-0.041 2002:-0.092 2003:+0.035 2004:-0.022 2005:+0.003 2006:-0.022 2007:-0.032 2008:-0.052 2009:+0.061 2010:+0.025 2011:-0.082 2012:+0.019 2013:+0.022 2014:-0.039 2015:-0.053 2016:+0.022 2017:-0.007 2018:-0.076 2019:+0.039 2020:+0.056 2021:-0.023

## BetaLiquidityPS  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0008 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.2688 | >= 2.5 | FAIL |
| ic_half_min | -0.0029 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.5669 | >= 0.0 | FAIL |
| coverage_pct | 67.1533 | >= 40.0 | PASS |
| avg_names_per_decile | 169.4 | >= 30 | PASS |
| ls_n_months | 215 | >= 193 | PASS |
stats: ic_mean=-0.0008  ic_tstat_nw=-0.2688  icir=-0.0183  ic_half1_mean=0.0013  ic_half2_mean=-0.0029  ls_sharpe=-0.1728  ls_ann_return_pct=-1.2987  ls_ann_vol_pct=7.5161  ls_maxdd_pct=-49.1055  ls_hit_rate_pct=50.2326  turnover_d10_pct=13.8768  turnover_d1_pct=13.8169  coverage_pct=67.1533  avg_names_per_decile=169.4  n_months=215  ls_n_months=215  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0762  ls_beta_mean=0.0060  ls_beta_fullwindow=0.1090  ls_sharpe_ex_top_years=-0.6206  ls_top_years=2006,2007,2020  ls_sharpe_bear=-0.5371  ls_sharpe_bull=-0.0510
deciles D1..D10 avg %/mo: 1.095,0.939,1.017,1.038,1.076,0.972,0.972,0.994,0.946,1.048
hedge/regime (diagnostics): beta ex-ante 0.0060 full-window 0.1090  raw Sharpe -0.0762  Sharpe ex top years -0.6206 (2006,2007,2020)  bear/bull -0.5371/-0.0510
ic decay: h1=-0.0007  h2=-0.0006  h3=-0.0004  h6=-0.0002  h12=-0.0010
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0019 -0.0250 -0.1390 -1.7400 361; MID -0.0067 -0.1004 -0.3790 -4.1700 520; SMALL 0.0031 0.0626 0.1070 0.8800 811; ALL -0.0008 -0.0183 -0.0760 -0.5700 1693
annual IC: 2004:-0.004 2005:+0.011 2006:+0.020 2007:+0.029 2008:-0.020 2009:-0.015 2010:-0.005 2011:-0.010 2012:+0.005 2013:-0.005 2014:-0.014 2015:-0.005 2016:+0.006 2017:-0.012 2018:-0.017 2019:-0.018 2020:+0.040 2021:-0.001

## BetaTailRisk  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0006 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.0648 | >= 2.5 | FAIL |
| ic_half_min | -0.0008 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 1.0920 | >= 0.0 | PASS |
| coverage_pct | 60.1691 | >= 40.0 | PASS |
| avg_names_per_decile | 151.1 | >= 30 | PASS |
| ls_n_months | 216 | >= 194 | PASS |
stats: ic_mean=-0.0006  ic_tstat_nw=-0.0648  icir=-0.0044  ic_half1_mean=-0.0004  ic_half2_mean=-0.0008  ls_sharpe=-0.7658  ls_ann_return_pct=-8.7902  ls_ann_vol_pct=11.4780  ls_maxdd_pct=-82.5450  ls_hit_rate_pct=37.9630  turnover_d10_pct=8.9314  turnover_d1_pct=9.1323  coverage_pct=60.1691  avg_names_per_decile=151.1  n_months=216  ls_n_months=216  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0690  ls_beta_mean=0.7852  ls_beta_fullwindow=0.7782  ls_sharpe_ex_top_years=-1.2363  ls_top_years=2005,2009,2020  ls_sharpe_bear=0.1546  ls_sharpe_bull=-1.0106
deciles D1..D10 avg %/mo: 0.973,0.980,0.948,0.906,1.014,1.038,1.121,1.058,1.081,1.064
hedge/regime (diagnostics): beta ex-ante 0.7852 full-window 0.7782  raw Sharpe 0.0690  Sharpe ex top years -1.2363 (2005,2009,2020)  bear/bull 0.1546/-1.0106
ic decay: h1=-0.0014  h2=-0.0009  h3=-0.0003  h6=-0.0014  h12=-0.0037
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0034 -0.0192 -0.1860 -3.8500 341; MID -0.0050 -0.0351 -0.0600 -0.9800 466; SMALL 0.0048 0.0427 0.2860 4.6000 702; ALL -0.0006 -0.0044 0.0690 1.0900 1510
annual IC: 2004:-0.007 2005:+0.013 2006:-0.004 2007:+0.002 2008:-0.050 2009:+0.058 2010:+0.025 2011:-0.065 2012:+0.025 2013:+0.036 2014:-0.036 2015:-0.045 2016:+0.016 2017:+0.030 2018:-0.079 2019:+0.034 2020:+0.038 2021:-0.001

## BidAskSpread  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0205 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.7705 | >= 2.5 | FAIL |
| ic_half_min | -0.0215 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.9364 | >= 0.0 | FAIL |
| coverage_pct | 99.1272 | >= 40.0 | PASS |
| avg_names_per_decile | 194.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0205  ic_tstat_nw=-2.7705  icir=-0.1655  ic_half1_mean=-0.0195  ic_half2_mean=-0.0215  ls_sharpe=-0.4815  ls_ann_return_pct=-8.6274  ls_ann_vol_pct=17.9172  ls_maxdd_pct=-94.6798  ls_hit_rate_pct=38.4058  turnover_d10_pct=59.9764  turnover_d1_pct=65.9729  coverage_pct=99.1272  avg_names_per_decile=194.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0405  ls_beta_mean=0.9371  ls_beta_fullwindow=0.9698  ls_sharpe_ex_top_years=-0.8887  ls_top_years=1999,2009,2020  ls_sharpe_bear=0.2544  ls_sharpe_bull=-0.9573
deciles D1..D10 avg %/mo: 0.968,1.018,0.982,0.988,0.977,0.967,0.942,0.975,0.944,0.890
hedge/regime (diagnostics): beta ex-ante 0.9371 full-window 0.9698  raw Sharpe -0.0405  Sharpe ex top years -0.8887 (1999,2009,2020)  bear/bull 0.2544/-0.9573
ic decay: h1=-0.0189  h2=-0.0181  h3=-0.0178  h6=-0.0137  h12=-0.0136
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0179 -0.1205 -0.0880 -2.4600 391; MID -0.0195 -0.1415 -0.0340 -0.8400 585; SMALL -0.0214 -0.1905 -0.0500 -1.1400 970; ALL -0.0205 -0.1655 -0.0410 -0.9400 1947
annual IC: 1999:+0.007 2000:-0.095 2001:-0.026 2002:-0.055 2003:+0.035 2004:+0.007 2005:-0.013 2006:-0.013 2007:-0.028 2008:-0.044 2009:+0.027 2010:+0.008 2011:-0.065 2012:-0.000 2013:+0.007 2014:-0.049 2015:-0.042 2016:+0.007 2017:-0.020 2018:-0.053 2019:-0.010 2020:+0.030 2021:-0.088

## BookLeverage  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0096 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.5874 | >= 2.5 | FAIL |
| ic_half_min | -0.0120 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -3.6278 | >= 0.0 | FAIL |
| coverage_pct | 99.6151 | >= 40.0 | PASS |
| avg_names_per_decile | 195.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0096  ic_tstat_nw=-2.5874  icir=-0.1683  ic_half1_mean=-0.0072  ic_half2_mean=-0.0120  ls_sharpe=-0.1296  ls_ann_return_pct=-1.2871  ls_ann_vol_pct=9.9283  ls_maxdd_pct=-53.1948  ls_hit_rate_pct=49.2754  turnover_d10_pct=11.0329  turnover_d1_pct=9.6587  coverage_pct=99.6151  avg_names_per_decile=195.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.3480  ls_beta_mean=0.0145  ls_beta_fullwindow=-0.0383  ls_sharpe_ex_top_years=-0.3982  ls_top_years=1999,2002,2008  ls_sharpe_bear=0.1222  ls_sharpe_bull=-0.3986
deciles D1..D10 avg %/mo: 1.108,1.046,1.059,0.956,0.971,1.039,0.941,0.910,0.828,0.805
hedge/regime (diagnostics): beta ex-ante 0.0145 full-window -0.0383  raw Sharpe -0.3480  Sharpe ex top years -0.3982 (1999,2002,2008)  bear/bull 0.1222/-0.3986
ic decay: h1=-0.0095  h2=-0.0091  h3=-0.0087  h6=-0.0074  h12=-0.0069
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0125 -0.1434 -0.2560 -4.3500 392; MID -0.0074 -0.1014 -0.1420 -1.8100 587; SMALL -0.0102 -0.1690 -0.4190 -4.9200 977; ALL -0.0096 -0.1683 -0.3480 -3.6300 1957
annual IC: 1999:+0.022 2000:-0.046 2001:-0.016 2002:-0.010 2003:-0.017 2004:-0.013 2005:-0.005 2006:-0.015 2007:+0.017 2008:+0.027 2009:-0.020 2010:+0.000 2011:+0.007 2012:-0.026 2013:-0.038 2014:-0.018 2015:-0.015 2016:-0.005 2017:+0.009 2018:+0.015 2019:-0.022 2020:+0.001 2021:-0.054

## CBOperProf  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0209 | >= 0.01 | PASS |
| ic_tstat_nw | 3.7357 | >= 2.5 | PASS |
| ic_half_min | 0.0127 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 7.2358 | >= 0.0 | PASS |
| coverage_pct | 73.4223 | >= 40.0 | PASS |
| avg_names_per_decile | 144.3 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0209  ic_tstat_nw=3.7357  icir=0.2597  ic_half1_mean=0.0290  ic_half2_mean=0.0127  ls_sharpe=0.9011  ls_ann_return_pct=11.2356  ls_ann_vol_pct=12.4684  ls_maxdd_pct=-37.2195  ls_hit_rate_pct=63.7681  turnover_d10_pct=10.0384  turnover_d1_pct=15.5778  coverage_pct=73.4223  avg_names_per_decile=144.3  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4787  ls_beta_mean=-0.4809  ls_beta_fullwindow=-0.5652  ls_sharpe_ex_top_years=0.6381  ls_top_years=2000,2002,2021  ls_sharpe_bear=0.6144  ls_sharpe_bull=0.9994
deciles D1..D10 avg %/mo: 0.545,0.896,0.919,0.974,0.973,1.124,1.273,1.202,1.231,1.148
hedge/regime (diagnostics): beta ex-ante -0.4809 full-window -0.5652  raw Sharpe 0.4787  Sharpe ex top years 0.6381 (2000,2002,2021)  bear/bull 0.6144/0.9994
ic decay: h1=0.0174  h2=0.0172  h3=0.0164  h6=0.0153  h12=0.0147
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0252 0.2497 0.3950 8.3000 309; MID 0.0203 0.2239 0.4980 8.6400 443; SMALL 0.0210 0.2563 0.4690 7.4900 689; ALL 0.0209 0.2597 0.4790 7.2400 1442
annual IC: 1999:+0.032 2000:+0.084 2001:+0.038 2002:+0.081 2003:-0.004 2004:+0.029 2005:+0.023 2006:-0.007 2007:+0.004 2008:+0.045 2009:-0.007 2010:+0.008 2011:+0.038 2012:-0.023 2013:-0.011 2014:+0.025 2015:+0.022 2016:+0.003 2017:+0.012 2018:+0.050 2019:-0.028 2020:-0.028 2021:+0.094
