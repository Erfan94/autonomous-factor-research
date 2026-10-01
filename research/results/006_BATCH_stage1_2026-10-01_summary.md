# RUN 006 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## EntMult  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0134 | >= 0.01 | PASS |
| ic_tstat_nw | 1.9611 | >= 2.5 | FAIL |
| ic_half_min | -0.0052 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 5.5491 | >= 0.0 | PASS |
| coverage_pct | 65.9122 | >= 40.0 | PASS |
| avg_names_per_decile | 129.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0134  ic_tstat_nw=1.9611  icir=0.1352  ic_half1_mean=0.0320  ic_half2_mean=-0.0052  ls_sharpe=0.1942  ls_ann_return_pct=2.8528  ls_ann_vol_pct=14.6900  ls_maxdd_pct=-65.7699  ls_hit_rate_pct=49.2754  turnover_d10_pct=18.6232  turnover_d1_pct=19.1309  coverage_pct=65.9122  avg_names_per_decile=129.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3713  ls_beta_mean=-0.0796  ls_beta_fullwindow=-0.0767  ls_sharpe_ex_top_years=-0.1269  ls_top_years=2001,2003,2021  ls_sharpe_bear=0.8739  ls_sharpe_bull=0.0292
deciles D1..D10 avg %/mo: 0.882,0.923,0.980,0.920,1.045,1.087,1.051,1.158,1.287,1.345
hedge/regime (diagnostics): beta ex-ante -0.0796 full-window -0.0767  raw Sharpe 0.3713  Sharpe ex top years -0.1269 (2001,2003,2021)  bear/bull 0.8739/0.0292
ic decay: h1=0.0063  h2=0.0052  h3=0.0058  h6=0.0053  h12=0.0084
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0113 0.0818 0.2930 5.4900 291; MID 0.0093 0.0822 0.2880 5.0200 404; SMALL 0.0143 0.1612 0.3130 4.4100 598; ALL 0.0134 0.1352 0.3710 5.5500 1295
annual IC: 1999:-0.019 2000:+0.046 2001:+0.107 2002:+0.072 2003:+0.035 2004:+0.057 2005:+0.020 2006:+0.030 2007:-0.041 2008:+0.039 2009:+0.024 2010:-0.001 2011:-0.001 2012:+0.002 2013:+0.010 2014:+0.034 2015:-0.022 2016:+0.024 2017:-0.032 2018:-0.050 2019:-0.002 2020:-0.074 2021:+0.049

## EquityDuration  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0104 | >= 0.01 | PASS |
| ic_tstat_nw | 1.8558 | >= 2.5 | FAIL |
| ic_half_min | 0.0004 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 2.3265 | >= 0.0 | PASS |
| coverage_pct | 94.7419 | >= 40.0 | PASS |
| avg_names_per_decile | 186.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0104  ic_tstat_nw=1.8558  icir=0.1316  ic_half1_mean=0.0203  ic_half2_mean=0.0004  ls_sharpe=0.2529  ls_ann_return_pct=2.9832  ls_ann_vol_pct=11.7939  ls_maxdd_pct=-51.5042  ls_hit_rate_pct=49.6377  turnover_d10_pct=16.8700  turnover_d1_pct=14.9910  coverage_pct=94.7419  avg_names_per_decile=186.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1806  ls_beta_mean=-0.2795  ls_beta_fullwindow=-0.3004  ls_sharpe_ex_top_years=-0.0609  ls_top_years=2000,2001,2002  ls_sharpe_bear=0.4574  ls_sharpe_bull=0.2224
deciles D1..D10 avg %/mo: 0.889,0.969,1.045,1.000,0.938,1.022,0.962,1.108,1.089,1.083
hedge/regime (diagnostics): beta ex-ante -0.2795 full-window -0.3004  raw Sharpe 0.1806  Sharpe ex top years -0.0609 (2000,2001,2002)  bear/bull 0.4574/0.2224
ic decay: h1=0.0107  h2=0.0113  h3=0.0120  h6=0.0116  h12=0.0105
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0073 0.0690 0.1880 3.1800 381; MID 0.0087 0.0969 0.3090 4.9600 562; SMALL 0.0112 0.1458 0.0070 0.0900 916; ALL 0.0104 0.1316 0.1810 2.3300 1861
annual IC: 1999:-0.019 2000:+0.069 2001:+0.063 2002:+0.066 2003:+0.020 2004:+0.023 2005:+0.014 2006:+0.014 2007:-0.042 2008:+0.016 2009:+0.009 2010:-0.004 2011:-0.001 2012:+0.004 2013:-0.005 2014:+0.015 2015:-0.010 2016:+0.034 2017:-0.026 2018:-0.020 2019:+0.003 2020:-0.047 2021:+0.060

## GP  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0155 | >= 0.01 | PASS |
| ic_tstat_nw | 3.5204 | >= 2.5 | PASS |
| ic_half_min | 0.0105 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 8.6402 | >= 0.0 | PASS |
| coverage_pct | 74.3904 | >= 40.0 | PASS |
| avg_names_per_decile | 146.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0155  ic_tstat_nw=3.5204  icir=0.2371  ic_half1_mean=0.0206  ic_half2_mean=0.0105  ls_sharpe=1.0906  ls_ann_return_pct=11.3369  ls_ann_vol_pct=10.3952  ls_maxdd_pct=-17.3637  ls_hit_rate_pct=61.5942  turnover_d10_pct=9.0287  turnover_d1_pct=10.3820  coverage_pct=74.3904  avg_names_per_decile=146.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.6876  ls_beta_mean=-0.3961  ls_beta_fullwindow=-0.4457  ls_sharpe_ex_top_years=0.9211  ls_top_years=2000,2018,2021  ls_sharpe_bear=1.2561  ls_sharpe_bull=1.0599
deciles D1..D10 avg %/mo: 0.419,0.790,1.061,1.081,1.138,1.058,1.123,1.139,1.157,1.139
hedge/regime (diagnostics): beta ex-ante -0.3961 full-window -0.4457  raw Sharpe 0.6876  Sharpe ex top years 0.9211 (2000,2018,2021)  bear/bull 1.2561/1.0599
ic decay: h1=0.0141  h2=0.0133  h3=0.0132  h6=0.0133  h12=0.0121
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0210 0.2099 0.5220 8.9900 316; MID 0.0115 0.1470 0.5260 8.3600 451; SMALL 0.0153 0.2297 0.6430 8.3200 693; ALL 0.0155 0.2371 0.6880 8.6400 1461
annual IC: 1999:+0.008 2000:+0.048 2001:+0.041 2002:+0.059 2003:-0.006 2004:+0.021 2005:+0.017 2006:+0.004 2007:-0.009 2008:+0.039 2009:+0.000 2010:+0.022 2011:+0.037 2012:-0.012 2013:-0.005 2014:+0.006 2015:+0.023 2016:-0.017 2017:+0.005 2018:+0.054 2019:-0.023 2020:-0.006 2021:+0.054

## GrLTNOA  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0059 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.7546 | >= 2.5 | FAIL |
| ic_half_min | -0.0069 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.0819 | >= 0.0 | FAIL |
| coverage_pct | 76.7894 | >= 40.0 | PASS |
| avg_names_per_decile | 150.9 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0059  ic_tstat_nw=-2.7546  icir=-0.1668  ic_half1_mean=-0.0049  ic_half2_mean=-0.0069  ls_sharpe=-0.1145  ls_ann_return_pct=-0.7611  ls_ann_vol_pct=6.6487  ls_maxdd_pct=-50.9168  ls_hit_rate_pct=48.9130  turnover_d10_pct=19.2465  turnover_d1_pct=19.3796  coverage_pct=76.7894  avg_names_per_decile=150.9  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0126  ls_beta_mean=-0.0162  ls_beta_fullwindow=0.0437  ls_sharpe_ex_top_years=-0.4907  ls_top_years=1999,2014,2016  ls_sharpe_bear=-0.0649  ls_sharpe_bull=-0.3322
deciles D1..D10 avg %/mo: 0.871,1.064,1.230,1.127,1.106,1.164,1.018,1.009,1.017,0.864
hedge/regime (diagnostics): beta ex-ante -0.0162 full-window 0.0437  raw Sharpe -0.0126  Sharpe ex top years -0.4907 (1999,2014,2016)  bear/bull -0.0649/-0.3322
ic decay: h1=-0.0044  h2=-0.0038  h3=-0.0032  h6=-0.0011  h12=-0.0015
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0096 -0.1530 -0.3290 -3.7700 322; MID -0.0095 -0.1656 -0.1290 -1.5200 467; SMALL -0.0027 -0.0626 0.1700 1.5100 718; ALL -0.0059 -0.1668 -0.0130 -0.0800 1508
annual IC: 1999:+0.006 2000:-0.006 2001:-0.006 2002:-0.026 2003:-0.007 2004:-0.003 2005:-0.008 2006:-0.004 2007:-0.017 2008:+0.001 2009:+0.014 2010:-0.009 2011:-0.028 2012:-0.020 2013:-0.013 2014:+0.011 2015:-0.004 2016:+0.020 2017:-0.020 2018:+0.001 2019:-0.009 2020:-0.009 2021:-0.002

## GrSaleToGrInv  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0035 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.5834 | >= 2.5 | FAIL |
| ic_half_min | 0.0005 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.6164 | >= 0.0 | PASS |
| coverage_pct | 57.0513 | >= 40.0 | PASS |
| avg_names_per_decile | 112.1 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0035  ic_tstat_nw=1.5834  icir=0.0950  ic_half1_mean=0.0065  ic_half2_mean=0.0005  ls_sharpe=0.2171  ls_ann_return_pct=1.5858  ls_ann_vol_pct=7.3050  ls_maxdd_pct=-25.5566  ls_hit_rate_pct=53.6232  turnover_d10_pct=17.9518  turnover_d1_pct=19.2459  coverage_pct=57.0513  avg_names_per_decile=112.1  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2327  ls_beta_mean=0.0098  ls_beta_fullwindow=-0.0092  ls_sharpe_ex_top_years=-0.1669  ls_top_years=1999,2003,2021  ls_sharpe_bear=0.1762  ls_sharpe_bull=0.0574
deciles D1..D10 avg %/mo: 0.882,1.081,1.018,1.107,1.052,1.259,1.191,1.159,1.078,1.017
hedge/regime (diagnostics): beta ex-ante 0.0098 full-window -0.0092  raw Sharpe 0.2327  Sharpe ex top years -0.1669 (1999,2003,2021)  bear/bull 0.1762/0.0574
ic decay: h1=0.0017  h2=0.0011  h3=-0.0010  h6=-0.0017  h12=0.0008
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0019 0.0262 -0.0270 -0.2900 262; MID 0.0070 0.1191 0.1880 2.0000 350; SMALL 0.0019 0.0376 0.1570 1.7400 507; ALL 0.0035 0.0950 0.2330 1.6200 1120
annual IC: 1999:+0.007 2000:-0.013 2001:+0.006 2002:+0.024 2003:+0.017 2004:+0.003 2005:+0.016 2006:+0.002 2007:+0.007 2008:+0.013 2009:-0.006 2010:-0.006 2011:+0.007 2012:-0.006 2013:-0.002 2014:+0.006 2015:+0.010 2016:-0.012 2017:+0.019 2018:-0.003 2019:-0.003 2020:-0.025 2021:+0.020

## GrSaleToGrOverhead  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0020 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.7460 | >= 2.5 | FAIL |
| ic_half_min | -0.0038 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -3.0418 | >= 0.0 | FAIL |
| coverage_pct | 85.1336 | >= 40.0 | PASS |
| avg_names_per_decile | 167.3 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0020  ic_tstat_nw=-0.7460  icir=-0.0461  ic_half1_mean=-0.0002  ic_half2_mean=-0.0038  ls_sharpe=-0.3941  ls_ann_return_pct=-2.7282  ls_ann_vol_pct=6.9232  ls_maxdd_pct=-58.9895  ls_hit_rate_pct=48.9130  turnover_d10_pct=14.5898  turnover_d1_pct=14.9958  coverage_pct=85.1336  avg_names_per_decile=167.3  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.4475  ls_beta_mean=0.0095  ls_beta_fullwindow=-0.0448  ls_sharpe_ex_top_years=-0.5488  ls_top_years=2003,2007,2008  ls_sharpe_bear=-0.2833  ls_sharpe_bull=-0.4983
deciles D1..D10 avg %/mo: 0.975,1.053,1.076,1.137,1.143,1.125,1.073,1.015,1.020,0.721
hedge/regime (diagnostics): beta ex-ante 0.0095 full-window -0.0448  raw Sharpe -0.4475  Sharpe ex top years -0.5488 (2003,2007,2008)  bear/bull -0.2833/-0.4983
ic decay: h1=-0.0030  h2=-0.0032  h3=-0.0022  h6=-0.0015  h12=0.0005
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0043 -0.0560 0.0290 0.3800 348; MID -0.0008 -0.0132 -0.2940 -3.2600 507; SMALL -0.0021 -0.0428 -0.4750 -4.6100 816; ALL -0.0020 -0.0461 -0.4470 -3.0400 1672
annual IC: 1999:+0.004 2000:-0.010 2001:-0.009 2002:+0.026 2003:-0.006 2004:-0.001 2005:-0.004 2006:-0.007 2007:+0.016 2008:+0.004 2009:-0.013 2010:-0.002 2011:-0.007 2012:-0.001 2013:-0.004 2014:+0.003 2015:-0.013 2016:-0.009 2017:+0.011 2018:-0.010 2019:-0.015 2020:-0.015 2021:+0.019

## Herf  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0028 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.1535 | >= 2.5 | FAIL |
| ic_half_min | -0.0029 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 0.0323 | >= 0.0 | PASS |
| coverage_pct | 91.5168 | >= 40.0 | PASS |
| avg_names_per_decile | 179.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0028  ic_tstat_nw=-1.1535  icir=-0.0695  ic_half1_mean=-0.0027  ic_half2_mean=-0.0029  ls_sharpe=-0.1056  ls_ann_return_pct=-0.7926  ls_ann_vol_pct=7.5054  ls_maxdd_pct=-29.5181  ls_hit_rate_pct=47.1014  turnover_d10_pct=6.9030  turnover_d1_pct=5.3586  coverage_pct=91.5168  avg_names_per_decile=179.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0043  ls_beta_mean=0.0554  ls_beta_fullwindow=0.0369  ls_sharpe_ex_top_years=-0.3263  ls_top_years=2002,2013,2014  ls_sharpe_bear=-0.0298  ls_sharpe_bull=-0.2027
deciles D1..D10 avg %/mo: 0.912,1.068,0.961,1.072,1.040,0.991,1.167,0.585,1.311,0.915
hedge/regime (diagnostics): beta ex-ante 0.0554 full-window 0.0369  raw Sharpe 0.0043  Sharpe ex top years -0.3263 (2002,2013,2014)  bear/bull -0.0298/-0.2027
ic decay: h1=-0.0032  h2=-0.0036  h3=-0.0031  h6=-0.0019  h12=-0.0024
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0051 -0.0742 -0.0990 -1.4100 369; MID -0.0022 -0.0360 0.1350 1.3900 541; SMALL -0.0027 -0.0558 -0.0370 -0.3600 887; ALL -0.0028 -0.0695 0.0040 0.0300 1798
annual IC: 1999:-0.008 2000:-0.005 2001:-0.009 2002:+0.001 2003:+0.004 2004:-0.002 2005:-0.001 2006:-0.017 2007:+0.003 2008:+0.021 2009:-0.007 2010:-0.014 2011:-0.002 2012:-0.011 2013:-0.007 2014:+0.024 2015:-0.003 2016:+0.013 2017:-0.020 2018:-0.017 2019:+0.007 2020:-0.020 2021:+0.005

## HerfAsset  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0049 | >= 0.01 | FAIL |
| ic_tstat_nw | -2.0027 | >= 2.5 | FAIL |
| ic_half_min | -0.0062 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.5946 | >= 0.0 | FAIL |
| coverage_pct | 91.5924 | >= 40.0 | PASS |
| avg_names_per_decile | 180.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0049  ic_tstat_nw=-2.0027  icir=-0.1193  ic_half1_mean=-0.0037  ic_half2_mean=-0.0062  ls_sharpe=-0.1817  ls_ann_return_pct=-1.4462  ls_ann_vol_pct=7.9583  ls_maxdd_pct=-41.3384  ls_hit_rate_pct=46.0145  turnover_d10_pct=6.3201  turnover_d1_pct=5.1891  coverage_pct=91.5924  avg_names_per_decile=180.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0748  ls_beta_mean=0.0737  ls_beta_fullwindow=0.0597  ls_sharpe_ex_top_years=-0.4318  ls_top_years=1999,2008,2014  ls_sharpe_bear=-0.2728  ls_sharpe_bull=-0.2280
deciles D1..D10 avg %/mo: 0.925,1.030,1.024,1.130,0.986,1.041,1.194,0.778,1.037,0.875
hedge/regime (diagnostics): beta ex-ante 0.0737 full-window 0.0597  raw Sharpe -0.0748  Sharpe ex top years -0.4318 (1999,2008,2014)  bear/bull -0.2728/-0.2280
ic decay: h1=-0.0050  h2=-0.0052  h3=-0.0046  h6=-0.0037  h12=-0.0042
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0088 -0.1336 -0.1800 -2.6500 369; MID -0.0058 -0.0960 -0.0560 -0.5900 541; SMALL -0.0031 -0.0604 0.0080 0.0800 888; ALL -0.0049 -0.1193 -0.0750 -0.5900 1799
annual IC: 1999:-0.003 2000:-0.007 2001:-0.004 2002:-0.013 2003:+0.017 2004:-0.006 2005:-0.011 2006:-0.012 2007:-0.004 2008:+0.019 2009:-0.015 2010:-0.013 2011:-0.007 2012:-0.018 2013:-0.013 2014:+0.024 2015:+0.001 2016:+0.012 2017:-0.025 2018:-0.010 2019:+0.007 2020:-0.030 2021:-0.001

## HerfBE  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0030 | >= 0.01 | FAIL |
| ic_tstat_nw | -1.2141 | >= 2.5 | FAIL |
| ic_half_min | -0.0056 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 0.2778 | >= 0.0 | PASS |
| coverage_pct | 91.5924 | >= 40.0 | PASS |
| avg_names_per_decile | 180.0 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=-0.0030  ic_tstat_nw=-1.2141  icir=-0.0743  ic_half1_mean=-0.0005  ic_half2_mean=-0.0056  ls_sharpe=-0.0611  ls_ann_return_pct=-0.4424  ls_ann_vol_pct=7.2379  ls_maxdd_pct=-39.9179  ls_hit_rate_pct=48.1884  turnover_d10_pct=7.0435  turnover_d1_pct=5.7863  coverage_pct=91.5924  avg_names_per_decile=180.0  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0390  ls_beta_mean=-0.0018  ls_beta_fullwindow=-0.0308  ls_sharpe_ex_top_years=-0.3304  ls_top_years=2008,2014,2016  ls_sharpe_bear=0.1050  ls_sharpe_bull=-0.0095
deciles D1..D10 avg %/mo: 0.918,0.912,1.056,1.099,1.140,0.964,1.020,0.845,1.254,0.941
hedge/regime (diagnostics): beta ex-ante -0.0018 full-window -0.0308  raw Sharpe 0.0390  Sharpe ex top years -0.3304 (2008,2014,2016)  bear/bull 0.1050/-0.0095
ic decay: h1=-0.0031  h2=-0.0037  h3=-0.0033  h6=-0.0022  h12=-0.0031
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0079 -0.1269 -0.3230 -3.6500 369; MID -0.0054 -0.0935 -0.1020 -0.9500 541; SMALL -0.0000 -0.0001 0.0650 0.6600 888; ALL -0.0030 -0.0743 0.0390 0.2800 1799
annual IC: 1999:-0.007 2000:-0.008 2001:+0.003 2002:-0.003 2003:+0.019 2004:+0.004 2005:-0.007 2006:-0.008 2007:-0.002 2008:+0.016 2009:-0.009 2010:-0.015 2011:-0.004 2012:-0.009 2013:-0.013 2014:+0.010 2015:-0.008 2016:+0.014 2017:-0.018 2018:-0.019 2019:+0.011 2020:-0.021 2021:+0.003

## High52  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0065 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.7734 | >= 2.5 | FAIL |
| ic_half_min | 0.0011 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | -0.1280 | >= 0.0 | FAIL |
| coverage_pct | 96.1065 | >= 40.0 | PASS |
| avg_names_per_decile | 188.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0065  ic_tstat_nw=0.7734  icir=0.0445  ic_half1_mean=0.0011  ic_half2_mean=0.0120  ls_sharpe=0.4477  ls_ann_return_pct=9.3835  ls_ann_vol_pct=20.9591  ls_maxdd_pct=-61.8656  ls_hit_rate_pct=64.4928  turnover_d10_pct=62.2659  turnover_d1_pct=24.8889  coverage_pct=96.1065  avg_names_per_decile=188.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0050  ls_beta_mean=-0.8563  ls_beta_fullwindow=-1.0090  ls_sharpe_ex_top_years=0.2548  ls_top_years=2000,2007,2021  ls_sharpe_bear=-0.6222  ls_sharpe_bull=1.0764
deciles D1..D10 avg %/mo: 1.057,0.974,1.004,1.040,0.923,1.052,0.959,0.982,0.965,1.047
hedge/regime (diagnostics): beta ex-ante -0.8563 full-window -1.0090  raw Sharpe -0.0050  Sharpe ex top years 0.2548 (2000,2007,2021)  bear/bull -0.6222/1.0764
ic decay: h1=0.0130  h2=0.0122  h3=0.0120  h6=0.0120  h12=0.0048
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0092 0.0545 0.2600 6.4300 385; MID 0.0129 0.0817 0.0990 2.7600 571; SMALL 0.0021 0.0150 -0.1360 -3.7200 931; ALL 0.0065 0.0445 -0.0050 -0.1300 1888
annual IC: 1999:+0.018 2000:+0.049 2001:-0.015 2002:+0.025 2003:-0.064 2004:-0.022 2005:+0.020 2006:+0.001 2007:+0.083 2008:+0.043 2009:-0.122 2010:-0.033 2011:+0.063 2012:-0.013 2013:+0.007 2014:+0.021 2015:+0.063 2016:-0.042 2017:+0.034 2018:+0.048 2019:-0.030 2020:-0.031 2021:+0.048

## IdioVol3F  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0229 | >= 0.01 | PASS |
| ic_tstat_nw | 3.1472 | >= 2.5 | PASS |
| ic_half_min | 0.0221 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.2773 | >= 0.0 | PASS |
| coverage_pct | 96.7275 | >= 40.0 | PASS |
| avg_names_per_decile | 195.0 | >= 30 | PASS |
| ls_n_months | 269 | >= 242 | PASS |
stats: ic_mean=0.0229  ic_tstat_nw=3.1472  icir=0.1899  ic_half1_mean=0.0221  ic_half2_mean=0.0237  ls_sharpe=0.5361  ls_ann_return_pct=10.0952  ls_ann_vol_pct=18.8308  ls_maxdd_pct=-43.7207  ls_hit_rate_pct=61.3383  turnover_d10_pct=63.9558  turnover_d1_pct=69.2194  coverage_pct=96.7275  avg_names_per_decile=195.0  n_months=269  ls_n_months=269  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1375  ls_beta_mean=-0.9160  ls_beta_fullwindow=-0.9758  ls_sharpe_ex_top_years=0.3736  ls_top_years=2000,2007,2021  ls_sharpe_bear=-0.2116  ls_sharpe_bull=0.9460
deciles D1..D10 avg %/mo: 0.691,0.942,0.943,0.958,1.007,0.915,1.021,1.024,1.043,0.964
hedge/regime (diagnostics): beta ex-ante -0.9160 full-window -0.9758  raw Sharpe 0.1375  Sharpe ex top years 0.3736 (2000,2007,2021)  bear/bull -0.2116/0.9460
ic decay: h1=0.0204  h2=0.0187  h3=0.0184  h6=0.0170  h12=0.0162
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0177 0.1234 0.0790 2.2500 390; MID 0.0249 0.1837 0.1710 4.3800 585; SMALL 0.0237 0.2124 0.0950 2.2100 974; ALL 0.0229 0.1899 0.1380 3.2800 1949
annual IC: 1999:-0.014 2000:+0.102 2001:+0.032 2002:+0.048 2003:-0.035 2004:-0.002 2005:+0.005 2006:+0.020 2007:+0.039 2008:+0.062 2009:-0.029 2010:-0.006 2011:+0.065 2012:-0.003 2013:+0.002 2014:+0.029 2015:+0.054 2016:-0.001 2017:+0.019 2018:+0.050 2019:+0.010 2020:-0.034 2021:+0.093

## IdioVolAHT  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0238 | >= 0.01 | PASS |
| ic_tstat_nw | 2.6281 | >= 2.5 | PASS |
| ic_half_min | 0.0226 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 3.8889 | >= 0.0 | PASS |
| coverage_pct | 96.7563 | >= 40.0 | PASS |
| avg_names_per_decile | 192.9 | >= 30 | PASS |
| ls_n_months | 272 | >= 244 | PASS |
stats: ic_mean=0.0238  ic_tstat_nw=2.6281  icir=0.1647  ic_half1_mean=0.0249  ic_half2_mean=0.0226  ls_sharpe=0.5452  ls_ann_return_pct=11.6759  ls_ann_vol_pct=21.4167  ls_maxdd_pct=-52.1060  ls_hit_rate_pct=61.7647  turnover_d10_pct=10.9364  turnover_d1_pct=15.3428  coverage_pct=96.7563  avg_names_per_decile=192.9  n_months=272  ls_n_months=272  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.1435  ls_beta_mean=-1.0379  ls_beta_fullwindow=-1.0729  ls_sharpe_ex_top_years=0.3888  ls_top_years=2000,2014,2021  ls_sharpe_bear=-0.1150  ls_sharpe_bull=0.8719
deciles D1..D10 avg %/mo: 0.665,0.930,1.069,0.986,0.985,1.020,1.007,1.017,0.971,0.990
hedge/regime (diagnostics): beta ex-ante -1.0379 full-window -1.0729  raw Sharpe 0.1435  Sharpe ex top years 0.3888 (2000,2014,2021)  bear/bull -0.1150/0.8719
ic decay: h1=0.0230  h2=0.0219  h3=0.0206  h6=0.0184  h12=0.0189
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0193 0.1129 0.0590 1.9000 389; MID 0.0269 0.1667 0.2380 6.9000 580; SMALL 0.0251 0.1869 0.1890 4.9200 958; ALL 0.0238 0.1647 0.1440 3.8900 1929
annual IC: 1999:-0.004 2000:+0.131 2001:+0.044 2002:+0.071 2003:-0.051 2004:-0.007 2005:-0.005 2006:+0.026 2007:+0.024 2008:+0.069 2009:-0.039 2010:-0.011 2011:+0.077 2012:-0.006 2013:-0.005 2014:+0.045 2015:+0.060 2016:+0.000 2017:+0.022 2018:+0.046 2019:+0.015 2020:-0.058 2021:+0.092
