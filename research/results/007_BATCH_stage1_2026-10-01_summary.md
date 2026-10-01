# RUN 007 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## Illiquidity  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0064 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.1861 | >= 2.5 | FAIL |
| ic_half_min | -0.0127 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.3065 | >= 0.0 | PASS |
| coverage_pct | 96.4198 | >= 40.0 | PASS |
| avg_names_per_decile | 189.4 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0064  ic_tstat_nw=-1.1861  icir=-0.0657  ic_half1_mean=-0.0000  ic_half2_mean=-0.0127  ls_sharpe=0.0783  ls_ann_return_pct=1.1309  ls_ann_vol_pct=14.4401  ls_maxdd_pct=-54.4854  ls_hit_rate_pct=49.2754  turnover_d10_pct=23.2061  turnover_d1_pct=2.7736  coverage_pct=96.4198  avg_names_per_decile=189.4  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2938  ls_beta_mean=0.3292  ls_beta_fullwindow=0.2886  ls_sharpe_ex_top_years=-0.1368  ls_top_years=2001,2003,2008  ls_sharpe_bear=0.7553  ls_sharpe_bull=-0.1761
deciles D1..D10 avg %/mo: 0.843,0.902,0.936,0.957,0.971,0.957,1.009,1.041,1.132,1.201
hedge/regime (diagnostics): beta ex-ante 0.3292 full-window 0.2886  raw Sharpe 0.2938  Sharpe ex top years -0.1368 (2001,2003,2008)  bear/bull 0.7553/-0.1761
ic decay: h1=-0.0058  h2=-0.0044  h3=-0.0031  h6=-0.0024  h12=-0.0037
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0074 -0.0650 0.0680 1.7600 386; MID -0.0181 -0.1369 0.0290 0.8000 572; SMALL -0.0090 -0.1138 0.0060 0.0900 935; ALL -0.0064 -0.0657 0.2940 4.3100 1894
annual IC: 1999:-0.009 2000:-0.030 2001:+0.044 2002:+0.002 2003:+0.017 2004:+0.005 2005:-0.008 2006:-0.006 2007:-0.033 2008:+0.019 2009:-0.011 2010:+0.021 2011:-0.011 2012:-0.005 2013:+0.021 2014:-0.044 2015:-0.023 2016:+0.022 2017:-0.023 2018:-0.026 2019:-0.018 2020:-0.001 2021:-0.050

## IntMom  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0031 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.5010 | >= 2.5 | FAIL |
| ic_half_min | -0.0011 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -1.1190 | >= 0.0 | FAIL |
| coverage_pct | 95.3703 | >= 40.0 | PASS |
| avg_names_per_decile | 188.1 | >= 30 | PASS |
| ls_n_months | 275 | >= 247 | PASS |
stats: ic_mean=0.0031  ic_tstat_nw=0.5010  icir=0.0329  ic_half1_mean=-0.0011  ic_half2_mean=0.0073  ls_sharpe=0.1512  ls_ann_return_pct=2.2373  ls_ann_vol_pct=14.7983  ls_maxdd_pct=-41.1622  ls_hit_rate_pct=53.0909  turnover_d10_pct=38.9242  turnover_d1_pct=39.8131  coverage_pct=95.3703  avg_names_per_decile=188.1  n_months=275  ls_n_months=275  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0770  ls_beta_mean=-0.0953  ls_beta_fullwindow=-0.1776  ls_sharpe_ex_top_years=-0.1167  ls_top_years=2002,2010,2015  ls_sharpe_bear=-0.2482  ls_sharpe_bull=0.2921
deciles D1..D10 avg %/mo: 0.997,0.990,1.104,1.001,1.034,1.046,1.031,0.938,1.011,0.904
hedge/regime (diagnostics): beta ex-ante -0.0953 full-window -0.1776  raw Sharpe -0.0770  Sharpe ex top years -0.1167 (2002,2010,2015)  bear/bull -0.2482/0.2921
ic decay: h1=0.0016  h2=-0.0002  h3=-0.0020  h6=0.0032  h12=0.0048
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0019 0.0146 0.0390 0.7200 384; MID 0.0012 0.0110 -0.1100 -1.9500 569; SMALL 0.0043 0.0507 -0.0630 -0.9500 926; ALL 0.0031 0.0329 -0.0770 -1.1200 1880
annual IC: 1999:+0.035 2000:-0.027 2001:-0.026 2002:+0.087 2003:-0.041 2004:-0.010 2005:+0.030 2006:-0.029 2007:+0.020 2008:+0.006 2009:-0.053 2010:+0.029 2011:+0.042 2012:+0.043 2013:+0.024 2014:+0.002 2015:+0.054 2016:-0.044 2017:+0.006 2018:-0.017 2019:-0.020 2020:+0.005 2021:-0.040

## IntanBM  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0003 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.0404 | >= 2.5 | FAIL |
| ic_half_min | -0.0040 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.3352 | >= 0.0 | PASS |
| coverage_pct | 61.1258 | >= 40.0 | PASS |
| avg_names_per_decile | 145.4 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=-0.0003  ic_tstat_nw=-0.0404  icir=-0.0028  ic_half1_mean=0.0034  ic_half2_mean=-0.0040  ls_sharpe=-0.2284  ls_ann_return_pct=-3.5360  ls_ann_vol_pct=15.4789  ls_maxdd_pct=-72.2992  ls_hit_rate_pct=41.2281  turnover_d10_pct=18.9800  turnover_d1_pct=19.0632  coverage_pct=61.1258  avg_names_per_decile=145.4  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2587  ls_beta_mean=0.4563  ls_beta_fullwindow=0.5625  ls_sharpe_ex_top_years=-0.8367  ls_top_years=2003,2009,2016  ls_sharpe_bear=0.6342  ls_sharpe_bull=-0.7205
deciles D1..D10 avg %/mo: 0.991,1.085,1.131,1.096,1.078,1.104,1.143,1.153,1.182,1.352
hedge/regime (diagnostics): beta ex-ante 0.4563 full-window 0.5625  raw Sharpe 0.2587  Sharpe ex top years -0.8367 (2003,2009,2016)  bear/bull 0.6342/-0.7205
ic decay: h1=-0.0035  h2=-0.0038  h3=-0.0029  h6=-0.0050  h12=-0.0077
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0105 -0.0834 -0.0880 -1.3300 325; MID -0.0063 -0.0484 0.1020 1.8300 447; SMALL 0.0079 0.0724 0.3400 6.5400 680; ALL -0.0003 -0.0028 0.2590 4.3400 1453
annual IC: 2003:+0.040 2004:+0.017 2005:-0.017 2006:+0.026 2007:-0.063 2008:+0.000 2009:+0.069 2010:+0.015 2011:-0.052 2012:+0.023 2013:+0.005 2014:+0.000 2015:-0.043 2016:+0.056 2017:-0.049 2018:-0.033 2019:+0.006 2020:-0.025 2021:+0.019

## IntanCFP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0033 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.3999 | >= 2.5 | FAIL |
| ic_half_min | -0.0053 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.6690 | >= 0.0 | PASS |
| coverage_pct | 62.9250 | >= 40.0 | PASS |
| avg_names_per_decile | 149.7 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=-0.0033  ic_tstat_nw=-0.3999  icir=-0.0274  ic_half1_mean=-0.0013  ic_half2_mean=-0.0053  ls_sharpe=-0.2626  ls_ann_return_pct=-4.3486  ls_ann_vol_pct=16.5610  ls_maxdd_pct=-76.9372  ls_hit_rate_pct=38.1579  turnover_d10_pct=18.5911  turnover_d1_pct=20.3223  coverage_pct=62.9250  avg_names_per_decile=149.7  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2538  ls_beta_mean=0.5386  ls_beta_fullwindow=0.6510  ls_sharpe_ex_top_years=-0.7975  ls_top_years=2003,2009,2016  ls_sharpe_bear=0.7101  ls_sharpe_bull=-0.7553
deciles D1..D10 avg %/mo: 1.050,1.015,1.083,1.186,1.078,1.071,1.119,1.121,1.243,1.439
hedge/regime (diagnostics): beta ex-ante 0.5386 full-window 0.6510  raw Sharpe 0.2538  Sharpe ex top years -0.7975 (2003,2009,2016)  bear/bull 0.7101/-0.7553
ic decay: h1=-0.0053  h2=-0.0055  h3=-0.0039  h6=-0.0035  h12=-0.0070
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0100 -0.0738 -0.0300 -0.4900 336; MID -0.0048 -0.0348 0.1370 2.6400 461; SMALL 0.0005 0.0043 0.3240 6.9000 698; ALL -0.0033 -0.0274 0.2540 4.6700 1496
annual IC: 2003:+0.032 2004:-0.017 2005:-0.023 2006:+0.024 2007:-0.065 2008:+0.017 2009:+0.069 2010:+0.008 2011:-0.063 2012:+0.028 2013:+0.003 2014:+0.003 2015:-0.053 2016:+0.048 2017:-0.046 2018:-0.023 2019:-0.000 2020:-0.025 2021:+0.019

## IntanEP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0045 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.5465 | >= 2.5 | FAIL |
| ic_half_min | -0.0067 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 4.5781 | >= 0.0 | PASS |
| coverage_pct | 62.9250 | >= 40.0 | PASS |
| avg_names_per_decile | 149.7 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=-0.0045  ic_tstat_nw=-0.5465  icir=-0.0375  ic_half1_mean=-0.0023  ic_half2_mean=-0.0067  ls_sharpe=-0.2580  ls_ann_return_pct=-4.3147  ls_ann_vol_pct=16.7247  ls_maxdd_pct=-76.6164  ls_hit_rate_pct=36.8421  turnover_d10_pct=18.3309  turnover_d1_pct=20.2915  coverage_pct=62.9250  avg_names_per_decile=149.7  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2479  ls_beta_mean=0.5299  ls_beta_fullwindow=0.6427  ls_sharpe_ex_top_years=-0.7980  ls_top_years=2003,2009,2016  ls_sharpe_bear=0.6975  ls_sharpe_bull=-0.7542
deciles D1..D10 avg %/mo: 1.043,1.045,1.098,1.131,1.107,1.055,1.104,1.137,1.261,1.424
hedge/regime (diagnostics): beta ex-ante 0.5299 full-window 0.6427  raw Sharpe 0.2479  Sharpe ex top years -0.7980 (2003,2009,2016)  bear/bull 0.6975/-0.7542
ic decay: h1=-0.0066  h2=-0.0067  h3=-0.0046  h6=-0.0039  h12=-0.0068
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0112 -0.0817 0.0460 0.7400 336; MID -0.0059 -0.0430 0.1260 2.4200 461; SMALL -0.0008 -0.0073 0.2900 6.1700 698; ALL -0.0045 -0.0375 0.2480 4.5800 1496
annual IC: 2003:+0.031 2004:-0.017 2005:-0.023 2006:+0.019 2007:-0.068 2008:+0.017 2009:+0.069 2010:+0.009 2011:-0.063 2012:+0.028 2013:+0.003 2014:-0.002 2015:-0.053 2016:+0.048 2017:-0.046 2018:-0.022 2019:-0.001 2020:-0.025 2021:+0.010

## IntanSP  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0052 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.6191 | >= 2.5 | FAIL |
| ic_half_min | -0.0081 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 5.1968 | >= 0.0 | PASS |
| coverage_pct | 62.9313 | >= 40.0 | PASS |
| avg_names_per_decile | 149.7 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=-0.0052  ic_tstat_nw=-0.6191  icir=-0.0423  ic_half1_mean=-0.0023  ic_half2_mean=-0.0081  ls_sharpe=-0.2331  ls_ann_return_pct=-3.9675  ls_ann_vol_pct=17.0240  ls_maxdd_pct=-76.8830  ls_hit_rate_pct=39.4737  turnover_d10_pct=16.4616  turnover_d1_pct=19.9791  coverage_pct=62.9313  avg_names_per_decile=149.7  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2746  ls_beta_mean=0.5753  ls_beta_fullwindow=0.6734  ls_sharpe_ex_top_years=-0.7725  ls_top_years=2003,2009,2016  ls_sharpe_bear=0.7405  ls_sharpe_bull=-0.7352
deciles D1..D10 avg %/mo: 1.034,1.030,1.109,1.157,1.058,1.068,1.074,1.166,1.242,1.467
hedge/regime (diagnostics): beta ex-ante 0.5753 full-window 0.6734  raw Sharpe 0.2746  Sharpe ex top years -0.7725 (2003,2009,2016)  bear/bull 0.7405/-0.7352
ic decay: h1=-0.0069  h2=-0.0068  h3=-0.0054  h6=-0.0045  h12=-0.0073
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0111 -0.0802 0.1990 4.2700 336; MID -0.0072 -0.0514 0.1270 2.5500 461; SMALL -0.0013 -0.0108 0.3310 7.2100 698; ALL -0.0052 -0.0423 0.2750 5.2000 1496
annual IC: 2003:+0.030 2004:-0.014 2005:-0.022 2006:+0.022 2007:-0.070 2008:+0.012 2009:+0.071 2010:+0.008 2011:-0.063 2012:+0.028 2013:+0.005 2014:-0.010 2015:-0.054 2016:+0.049 2017:-0.047 2018:-0.022 2019:-0.002 2020:-0.025 2021:+0.003

## InvGrowth  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0055 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.5551 | >= 2.5 | FAIL |
| ic_half_min | 0.0016 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.4975 | >= 0.0 | PASS |
| coverage_pct | 51.7013 | >= 40.0 | PASS |
| avg_names_per_decile | 101.6 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0055  ic_tstat_nw=1.5551  icir=0.0993  ic_half1_mean=0.0094  ic_half2_mean=0.0016  ls_sharpe=0.3860  ls_ann_return_pct=3.8152  ls_ann_vol_pct=9.8832  ls_maxdd_pct=-20.9986  ls_hit_rate_pct=57.2464  turnover_d10_pct=19.4790  turnover_d1_pct=17.8834  coverage_pct=51.7013  avg_names_per_decile=101.6  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3519  ls_beta_mean=-0.1294  ls_beta_fullwindow=-0.1361  ls_sharpe_ex_top_years=0.0093  ls_top_years=1999,2003,2021  ls_sharpe_bear=0.0710  ls_sharpe_bull=0.3275
deciles D1..D10 avg %/mo: 0.863,0.985,1.018,1.153,1.064,1.203,1.160,1.239,1.356,1.154
hedge/regime (diagnostics): beta ex-ante -0.1294 full-window -0.1361  raw Sharpe 0.3519  Sharpe ex top years 0.0093 (1999,2003,2021)  bear/bull 0.0710/0.3275
ic decay: h1=0.0046  h2=0.0054  h3=0.0029  h6=0.0005  h12=0.0036
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0019 0.0194 0.0600 1.2700 231; MID 0.0071 0.0901 0.0680 0.9300 315; SMALL 0.0056 0.0967 0.3820 4.2700 468; ALL 0.0055 0.0993 0.3520 3.5000 1015
annual IC: 1999:+0.021 2000:+0.011 2001:+0.023 2002:+0.014 2003:+0.009 2004:-0.011 2005:+0.008 2006:+0.015 2007:-0.022 2008:+0.038 2009:+0.001 2010:-0.003 2011:+0.000 2012:+0.007 2013:+0.012 2014:+0.011 2015:+0.003 2016:+0.013 2017:-0.017 2018:+0.025 2019:-0.014 2020:-0.031 2021:+0.011

## InvestmentTWX  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0003 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.1497 | >= 2.5 | FAIL |
| ic_half_min | -0.0000 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.6761 | >= 0.0 | PASS |
| coverage_pct | 78.7126 | >= 40.0 | PASS |
| avg_names_per_decile | 154.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0003  ic_tstat_nw=0.1497  icir=0.0091  ic_half1_mean=-0.0000  ic_half2_mean=0.0006  ls_sharpe=0.3419  ls_ann_return_pct=1.9795  ls_ann_vol_pct=5.7889  ls_maxdd_pct=-18.5585  ls_hit_rate_pct=52.1739  turnover_d10_pct=12.2878  turnover_d1_pct=12.3237  coverage_pct=78.7126  avg_names_per_decile=154.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.4798  ls_beta_mean=0.0585  ls_beta_fullwindow=0.0283  ls_sharpe_ex_top_years=0.0973  ls_top_years=1999,2001,2010  ls_sharpe_bear=0.2052  ls_sharpe_bull=0.3034
deciles D1..D10 avg %/mo: 0.874,1.091,0.956,1.098,1.062,1.042,1.108,1.112,1.053,1.097
hedge/regime (diagnostics): beta ex-ante 0.0585 full-window 0.0283  raw Sharpe 0.4798  Sharpe ex top years 0.0973 (1999,2001,2010)  bear/bull 0.2052/0.3034
ic decay: h1=-0.0005  h2=-0.0009  h3=-0.0005  h6=-0.0006  h12=-0.0008
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0005 0.0071 0.1070 1.1200 339; MID -0.0020 -0.0387 0.1470 1.3500 476; SMALL -0.0000 -0.0008 0.2160 1.7000 730; ALL 0.0003 0.0091 0.4800 2.6800 1546
annual IC: 1999:+0.006 2000:-0.013 2001:+0.012 2002:+0.013 2003:+0.012 2004:-0.009 2005:+0.003 2006:-0.009 2007:-0.015 2008:+0.015 2009:-0.017 2010:+0.013 2011:+0.006 2012:+0.007 2013:+0.007 2014:+0.004 2015:-0.002 2016:+0.003 2017:-0.008 2018:-0.001 2019:-0.014 2020:-0.002 2021:-0.006

## LRreversal  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0080 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.2934 | >= 2.5 | FAIL |
| ic_half_min | -0.0123 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.8390 | >= 0.0 | PASS |
| coverage_pct | 78.8898 | >= 40.0 | PASS |
| avg_names_per_decile | 170.4 | >= 30 | PASS |
| ls_n_months | 251 | >= 225 | PASS |
stats: ic_mean=-0.0080  ic_tstat_nw=-1.2934  icir=-0.0874  ic_half1_mean=-0.0036  ic_half2_mean=-0.0123  ls_sharpe=-0.0677  ls_ann_return_pct=-0.9658  ls_ann_vol_pct=14.2563  ls_maxdd_pct=-61.7407  ls_hit_rate_pct=45.0199  turnover_d10_pct=22.5301  turnover_d1_pct=21.6281  coverage_pct=78.8898  avg_names_per_decile=170.4  n_months=251  ls_n_months=251  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2154  ls_beta_mean=0.0689  ls_beta_fullwindow=0.0851  ls_sharpe_ex_top_years=-0.3813  ls_top_years=2001,2003,2016  ls_sharpe_bear=0.3222  ls_sharpe_bull=-0.2917
deciles D1..D10 avg %/mo: 0.845,0.974,0.910,0.999,0.993,1.041,1.015,0.978,1.016,1.081
hedge/regime (diagnostics): beta ex-ante 0.0689 full-window 0.0851  raw Sharpe 0.2154  Sharpe ex top years -0.3813 (2001,2003,2016)  bear/bull 0.3222/-0.2917
ic decay: h1=-0.0092  h2=-0.0094  h3=-0.0078  h6=-0.0081  h12=-0.0090
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0050 -0.0382 0.2580 5.6100 364; MID -0.0066 -0.0625 0.0220 0.3200 523; SMALL -0.0114 -0.1409 0.1010 1.2800 816; ALL -0.0080 -0.0874 0.2150 2.8400 1704
annual IC: 2001:+0.040 2002:+0.025 2003:+0.003 2004:-0.044 2005:-0.026 2006:-0.001 2007:-0.058 2008:+0.023 2009:-0.005 2010:+0.023 2011:-0.037 2012:+0.005 2013:+0.002 2014:-0.012 2015:-0.016 2016:+0.035 2017:-0.028 2018:-0.008 2019:-0.018 2020:-0.055 2021:-0.011

## Leverage  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0125 | >= 0.01 | PASS |
| ic_tstat_nw | 1.7081 | >= 2.5 | FAIL |
| ic_half_min | 0.0082 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 7.0928 | >= 0.0 | PASS |
| coverage_pct | 99.5807 | >= 40.0 | PASS |
| avg_names_per_decile | 195.7 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0125  ic_tstat_nw=1.7081  icir=0.1149  ic_half1_mean=0.0168  ic_half2_mean=0.0082  ls_sharpe=-0.0253  ls_ann_return_pct=-0.5038  ls_ann_vol_pct=19.8881  ls_maxdd_pct=-69.2146  ls_hit_rate_pct=44.9275  turnover_d10_pct=11.3943  turnover_d1_pct=11.9919  coverage_pct=99.5807  avg_names_per_decile=195.7  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3435  ls_beta_mean=0.2268  ls_beta_fullwindow=0.3014  ls_sharpe_ex_top_years=-0.3421  ls_top_years=2003,2009,2021  ls_sharpe_bear=0.2508  ls_sharpe_bull=-0.0344
deciles D1..D10 avg %/mo: 0.652,0.819,0.897,0.991,0.867,0.983,1.020,1.055,1.140,1.243
hedge/regime (diagnostics): beta ex-ante 0.2268 full-window 0.3014  raw Sharpe 0.3435  Sharpe ex top years -0.3421 (2003,2009,2021)  bear/bull 0.2508/-0.0344
ic decay: h1=0.0102  h2=0.0099  h3=0.0096  h6=0.0081  h12=0.0091
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0090 0.0623 0.2210 5.4100 392; MID 0.0088 0.0733 0.1690 3.8100 586; SMALL 0.0152 0.1495 0.4110 8.4000 977; ALL 0.0125 0.1149 0.3440 7.0900 1956
annual IC: 1999:-0.027 2000:+0.067 2001:+0.062 2002:+0.015 2003:+0.049 2004:+0.026 2005:+0.002 2006:+0.030 2007:-0.059 2008:-0.024 2009:+0.050 2010:+0.009 2011:-0.029 2012:+0.037 2013:+0.034 2014:+0.021 2015:-0.015 2016:+0.041 2017:-0.030 2018:-0.039 2019:+0.013 2020:-0.036 2021:+0.091

## MRreversal  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0043 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.9592 | >= 2.5 | FAIL |
| ic_half_min | -0.0057 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 3.6892 | >= 0.0 | PASS |
| coverage_pct | 90.9916 | >= 40.0 | PASS |
| avg_names_per_decile | 183.4 | >= 30 | PASS |
| ls_n_months | 269 | >= 242 | PASS |
stats: ic_mean=-0.0043  ic_tstat_nw=-0.9592  icir=-0.0572  ic_half1_mean=-0.0028  ic_half2_mean=-0.0057  ls_sharpe=0.0511  ls_ann_return_pct=0.6177  ls_ann_vol_pct=12.0806  ls_maxdd_pct=-42.2974  ls_hit_rate_pct=50.1859  turnover_d10_pct=39.8635  turnover_d1_pct=38.8937  coverage_pct=90.9916  avg_names_per_decile=183.4  n_months=269  ls_n_months=269  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3140  ls_beta_mean=0.0462  ls_beta_fullwindow=0.0864  ls_sharpe_ex_top_years=-0.2002  ls_top_years=2000,2001,2016  ls_sharpe_bear=0.3457  ls_sharpe_bull=-0.1204
deciles D1..D10 avg %/mo: 0.770,0.994,1.111,0.981,0.959,1.079,1.020,0.990,1.100,1.077
hedge/regime (diagnostics): beta ex-ante 0.0462 full-window 0.0864  raw Sharpe 0.3140  Sharpe ex top years -0.2002 (2000,2001,2016)  bear/bull 0.3457/-0.1204
ic decay: h1=-0.0025  h2=-0.0033  h3=-0.0059  h6=-0.0060  h12=0.0032
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0012 0.0104 0.3870 7.1100 379; MID -0.0025 -0.0278 0.2370 3.5500 557; SMALL -0.0065 -0.0999 0.2290 2.6800 897; ALL -0.0043 -0.0572 0.3140 3.6900 1834
annual IC: 1999:+0.005 2000:+0.025 2001:+0.044 2002:-0.033 2003:-0.026 2004:-0.028 2005:-0.008 2006:+0.002 2007:-0.026 2008:+0.022 2009:+0.012 2010:-0.031 2011:-0.011 2012:+0.035 2013:-0.011 2014:-0.013 2015:-0.008 2016:+0.017 2017:-0.016 2018:-0.003 2019:-0.004 2020:-0.035 2021:-0.004

## MaxRet  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0233 | >= 0.01 | PASS |
| ic_tstat_nw | 3.4239 | >= 2.5 | PASS |
| ic_half_min | 0.0178 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.1728 | >= 0.0 | PASS |
| coverage_pct | 99.8027 | >= 40.0 | PASS |
| avg_names_per_decile | 196.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0233  ic_tstat_nw=3.4239  icir=0.2014  ic_half1_mean=0.0287  ic_half2_mean=0.0178  ls_sharpe=0.6107  ls_ann_return_pct=10.5672  ls_ann_vol_pct=17.3024  ls_maxdd_pct=-43.0049  ls_hit_rate_pct=64.8551  turnover_d10_pct=70.8141  turnover_d1_pct=77.4898  coverage_pct=99.8027  avg_names_per_decile=196.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1921  ls_beta_mean=-0.8045  ls_beta_fullwindow=-0.8622  ls_sharpe_ex_top_years=0.5438  ls_top_years=2000,2014,2021  ls_sharpe_bear=0.1945  ls_sharpe_bull=0.9081
deciles D1..D10 avg %/mo: 0.767,0.933,0.908,0.928,0.961,0.949,0.976,1.060,1.082,1.114
hedge/regime (diagnostics): beta ex-ante -0.8045 full-window -0.8622  raw Sharpe 0.1921  Sharpe ex top years 0.5438 (2000,2014,2021)  bear/bull 0.1945/0.9081
ic decay: h1=0.0189  h2=0.0149  h3=0.0147  h6=0.0131  h12=0.0172
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0208 0.1397 0.1140 3.1700 392; MID 0.0227 0.1704 0.2450 5.6300 588; SMALL 0.0243 0.2369 0.2210 4.5700 979; ALL 0.0233 0.2014 0.1920 4.1700 1960
annual IC: 1999:+0.018 2000:+0.096 2001:+0.059 2002:+0.072 2003:-0.028 2004:+0.006 2005:+0.005 2006:+0.022 2007:+0.022 2008:+0.058 2009:-0.024 2010:-0.004 2011:+0.048 2012:-0.001 2013:-0.005 2014:+0.034 2015:+0.046 2016:-0.005 2017:+0.014 2018:+0.046 2019:+0.008 2020:-0.029 2021:+0.077
