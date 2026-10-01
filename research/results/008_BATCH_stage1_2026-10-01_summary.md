# RUN 008 BATCH stage 1

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## MeanRankRevGrowth  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0005 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.1171 | >= 2.5 | FAIL |
| ic_half_min | -0.0029 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.2278 | >= 0.0 | PASS |
| coverage_pct | 46.6139 | >= 40.0 | PASS |
| avg_names_per_decile | 117.0 | >= 30 | PASS |
| ls_n_months | 216 | >= 194 | PASS |
stats: ic_mean=-0.0005  ic_tstat_nw=-0.1171  icir=-0.0088  ic_half1_mean=0.0019  ic_half2_mean=-0.0029  ls_sharpe=0.0930  ls_ann_return_pct=0.7575  ls_ann_vol_pct=8.1457  ls_maxdd_pct=-38.3092  ls_hit_rate_pct=51.3889  turnover_d10_pct=26.2284  turnover_d1_pct=25.4017  coverage_pct=46.6139  avg_names_per_decile=117.0  n_months=216  ls_n_months=216  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2725  ls_beta_mean=0.0895  ls_beta_fullwindow=0.0991  ls_sharpe_ex_top_years=-0.2254  ls_top_years=2006,2012,2021  ls_sharpe_bear=-0.1182  ls_sharpe_bull=0.1355
deciles D1..D10 avg %/mo: 0.992,1.012,1.156,1.065,1.115,1.011,1.010,1.061,1.083,1.177
hedge/regime (diagnostics): beta ex-ante 0.0895 full-window 0.0991  raw Sharpe 0.2725  Sharpe ex top years -0.2254 (2006,2012,2021)  bear/bull -0.1182/0.1355
ic decay: h1=-0.0031  h2=-0.0011  h3=0.0003  h6=-0.0007  h12=-0.0021
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0016 0.0157 0.0440 0.7700 275; MID 0.0052 0.0711 0.3580 3.7100 359; SMALL -0.0062 -0.1018 0.1990 1.9700 535; ALL -0.0005 -0.0088 0.2720 2.2300 1170
annual IC: 2004:-0.003 2005:+0.006 2006:+0.023 2007:-0.011 2008:+0.011 2009:-0.007 2010:-0.002 2011:-0.029 2012:+0.029 2013:+0.020 2014:+0.019 2015:-0.003 2016:+0.003 2017:-0.002 2018:-0.010 2019:-0.015 2020:-0.046 2021:+0.008

## Mom12mOffSeason  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0084 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.2361 | >= 2.5 | FAIL |
| ic_half_min | 0.0047 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 7.0759 | >= 0.0 | PASS |
| coverage_pct | 96.4483 | >= 40.0 | PASS |
| avg_names_per_decile | 189.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0084  ic_tstat_nw=1.2361  icir=0.0695  ic_half1_mean=0.0047  ic_half2_mean=0.0121  ls_sharpe=0.5831  ls_ann_return_pct=13.3358  ls_ann_vol_pct=22.8713  ls_maxdd_pct=-60.2957  ls_hit_rate_pct=62.6812  turnover_d10_pct=29.7736  turnover_d1_pct=33.5742  coverage_pct=96.4483  avg_names_per_decile=189.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3142  ls_beta_mean=-0.2184  ls_beta_fullwindow=-0.3489  ls_sharpe_ex_top_years=0.4176  ls_top_years=1999,2007,2017  ls_sharpe_bear=-0.1263  ls_sharpe_bull=0.9440
deciles D1..D10 avg %/mo: 0.720,0.967,0.937,0.998,0.957,0.942,1.015,0.982,1.116,1.310
hedge/regime (diagnostics): beta ex-ante -0.2184 full-window -0.3489  raw Sharpe 0.3142  Sharpe ex top years 0.4176 (1999,2007,2017)  bear/bull -0.1263/0.9440
ic decay: h1=0.0071  h2=0.0011  h3=0.0003  h6=-0.0011  h12=0.0023
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0089 0.0568 0.3020 9.1300 386; MID 0.0094 0.0672 0.3060 7.9600 572; SMALL 0.0071 0.0657 0.2340 5.0800 935; ALL 0.0084 0.0695 0.3140 7.0800 1895
annual IC: 1999:+0.043 2000:-0.025 2001:-0.003 2002:+0.036 2003:-0.023 2004:+0.006 2005:+0.045 2006:-0.009 2007:+0.067 2008:+0.005 2009:-0.084 2010:+0.008 2011:+0.014 2012:+0.017 2013:+0.030 2014:+0.008 2015:+0.059 2016:-0.047 2017:+0.031 2018:+0.030 2019:-0.016 2020:+0.014 2021:-0.012

## Mom6m  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0077 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.2435 | >= 2.5 | FAIL |
| ic_half_min | 0.0060 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 6.4681 | >= 0.0 | PASS |
| coverage_pct | 98.1565 | >= 40.0 | PASS |
| avg_names_per_decile | 192.9 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0077  ic_tstat_nw=1.2435  icir=0.0666  ic_half1_mean=0.0060  ic_half2_mean=0.0094  ls_sharpe=0.6159  ls_ann_return_pct=12.9314  ls_ann_vol_pct=20.9951  ls_maxdd_pct=-52.9963  ls_hit_rate_pct=64.1304  turnover_d10_pct=43.3225  turnover_d1_pct=42.4573  coverage_pct=98.1565  avg_names_per_decile=192.9  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3025  ls_beta_mean=-0.3843  ls_beta_fullwindow=-0.4691  ls_sharpe_ex_top_years=0.4487  ls_top_years=2003,2007,2013  ls_sharpe_bear=-0.0757  ls_sharpe_bull=1.0481
deciles D1..D10 avg %/mo: 0.718,0.927,0.938,0.990,0.948,0.960,0.970,1.011,1.074,1.257
hedge/regime (diagnostics): beta ex-ante -0.3843 full-window -0.4691  raw Sharpe 0.3025  Sharpe ex top years 0.4487 (2003,2007,2013)  bear/bull -0.0757/1.0481
ic decay: h1=0.0077  h2=0.0072  h3=0.0119  h6=0.0084  h12=0.0030
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0082 0.0548 0.3340 8.9200 389; MID 0.0071 0.0550 0.2780 6.7200 580; SMALL 0.0080 0.0750 0.2770 5.9100 957; ALL 0.0077 0.0666 0.3030 6.4700 1928
annual IC: 1999:+0.020 2000:+0.020 2001:+0.004 2002:+0.009 2003:-0.010 2004:+0.003 2005:+0.018 2006:-0.004 2007:+0.073 2008:+0.008 2009:-0.055 2010:-0.035 2011:+0.023 2012:-0.025 2013:+0.022 2014:+0.015 2015:+0.042 2016:-0.021 2017:+0.019 2018:+0.036 2019:-0.018 2020:+0.011 2021:+0.021

## MomOffSeason  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | -0.0052 | >= 0.01 | FAIL |
| ic_tstat_nw | -0.9687 | >= 2.5 | FAIL |
| ic_half_min | -0.0119 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.2263 | >= 0.0 | PASS |
| coverage_pct | 66.5919 | >= 40.0 | PASS |
| avg_names_per_decile | 157.7 | >= 30 | PASS |
| ls_n_months | 229 | >= 206 | PASS |
stats: ic_mean=-0.0052  ic_tstat_nw=-0.9687  icir=-0.0710  ic_half1_mean=0.0015  ic_half2_mean=-0.0119  ls_sharpe=0.1125  ls_ann_return_pct=1.1899  ls_ann_vol_pct=10.5765  ls_maxdd_pct=-43.6580  ls_hit_rate_pct=49.3450  turnover_d10_pct=35.5099  turnover_d1_pct=28.8898  coverage_pct=66.5919  avg_names_per_decile=157.7  n_months=229  ls_n_months=229  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2131  ls_beta_mean=-0.0485  ls_beta_fullwindow=0.0514  ls_sharpe_ex_top_years=-0.2082  ls_top_years=2009,2016,2021  ls_sharpe_bear=0.4729  ls_sharpe_bull=0.0090
deciles D1..D10 avg %/mo: 1.014,1.186,1.099,1.165,1.176,1.045,1.039,1.130,1.115,1.199
hedge/regime (diagnostics): beta ex-ante -0.0485 full-window 0.0514  raw Sharpe 0.2131  Sharpe ex top years -0.2082 (2009,2016,2021)  bear/bull 0.4729/0.0090
ic decay: h1=-0.0082  h2=-0.0069  h3=-0.0048  h6=0.0009  h12=0.0032
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0144 -0.1284 0.0100 0.1800 349; MID -0.0037 -0.0410 0.2970 3.5100 486; SMALL -0.0024 -0.0367 0.2110 2.3000 740; ALL -0.0052 -0.0710 0.2130 2.2300 1576
annual IC: 2002:+0.112 2003:-0.005 2004:-0.007 2005:-0.005 2006:+0.026 2007:-0.030 2008:+0.037 2009:-0.004 2010:+0.003 2011:-0.009 2012:+0.013 2013:-0.008 2014:-0.004 2015:-0.014 2016:+0.016 2017:-0.037 2018:-0.003 2019:-0.040 2020:-0.053 2021:+0.015

## MomOffSeason06YrPlus  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0065 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.7594 | >= 2.5 | FAIL |
| ic_half_min | 0.0052 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 1.4493 | >= 0.0 | PASS |
| coverage_pct | 40.6243 | >= 40.0 | PASS |
| avg_names_per_decile | 130.4 | >= 30 | PASS |
| ls_n_months | 169 | >= 152 | PASS |
stats: ic_mean=0.0065  ic_tstat_nw=1.7594  icir=0.1250  ic_half1_mean=0.0079  ic_half2_mean=0.0052  ls_sharpe=0.2683  ls_ann_return_pct=1.6434  ls_ann_vol_pct=6.1252  ls_maxdd_pct=-13.8324  ls_hit_rate_pct=53.8462  turnover_d10_pct=36.4245  turnover_d1_pct=30.4190  coverage_pct=40.6243  avg_names_per_decile=130.4  n_months=169  ls_n_months=169  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.2443  ls_beta_mean=-0.0186  ls_beta_fullwindow=0.0116  ls_sharpe_ex_top_years=-0.0629  ls_top_years=2013,2014,2015  ls_sharpe_bear=-0.2168  ls_sharpe_bull=0.3959
deciles D1..D10 avg %/mo: 0.937,1.058,1.063,1.042,0.970,1.121,1.082,1.066,1.135,1.057
hedge/regime (diagnostics): beta ex-ante -0.0186 full-window 0.0116  raw Sharpe 0.2443  Sharpe ex top years -0.0629 (2013,2014,2015)  bear/bull -0.2168/0.3959
ic decay: h1=0.0016  h2=0.0029  h3=0.0015  h6=-0.0012  h12=0.0032
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0122 0.1389 0.2680 2.6400 313; MID 0.0133 0.1884 0.1080 1.0100 405; SMALL -0.0002 -0.0028 0.1660 1.4600 584; ALL 0.0065 0.1250 0.2440 1.4500 1303
annual IC: 2007:+0.026 2008:-0.010 2009:+0.011 2010:-0.002 2011:+0.005 2012:+0.003 2013:+0.022 2014:+0.027 2015:+0.020 2016:+0.017 2017:-0.007 2018:+0.019 2019:+0.004 2020:-0.022 2021:+0.000

## MomSeason  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0020 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.5802 | >= 2.5 | FAIL |
| ic_half_min | -0.0049 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.2733 | >= 0.0 | FAIL |
| coverage_pct | 66.0824 | >= 40.0 | PASS |
| avg_names_per_decile | 157.2 | >= 30 | PASS |
| ls_n_months | 228 | >= 205 | PASS |
stats: ic_mean=0.0020  ic_tstat_nw=0.5802  icir=0.0385  ic_half1_mean=0.0090  ic_half2_mean=-0.0049  ls_sharpe=0.0222  ls_ann_return_pct=0.1669  ls_ann_vol_pct=7.5205  ls_maxdd_pct=-44.8749  ls_hit_rate_pct=52.6316  turnover_d10_pct=85.9759  turnover_d1_pct=86.7755  coverage_pct=66.0824  avg_names_per_decile=157.2  n_months=228  ls_n_months=228  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0376  ls_beta_mean=-0.0153  ls_beta_fullwindow=0.0050  ls_sharpe_ex_top_years=-0.2214  ls_top_years=2004,2005,2012  ls_sharpe_bear=0.2698  ls_sharpe_bull=-0.0652
deciles D1..D10 avg %/mo: 1.188,1.111,1.099,1.070,1.176,1.133,1.093,1.132,1.227,1.165
hedge/regime (diagnostics): beta ex-ante -0.0153 full-window 0.0050  raw Sharpe -0.0376  Sharpe ex top years -0.2214 (2004,2005,2012)  bear/bull 0.2698/-0.0652
ic decay: h1=-0.0043  h2=-0.0017  h3=0.0000  h6=-0.0003  h12=0.0038
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0012 -0.0139 -0.2720 -4.1900 349; MID 0.0038 0.0534 0.0160 0.1600 485; SMALL 0.0023 0.0399 0.2190 2.0200 737; ALL 0.0020 0.0385 -0.0380 -0.2700 1571
annual IC: 2003:+0.008 2004:+0.039 2005:+0.029 2006:+0.008 2007:+0.010 2008:-0.000 2009:-0.009 2010:+0.004 2011:+0.009 2012:+0.002 2013:+0.008 2014:-0.005 2015:-0.003 2016:-0.032 2017:+0.002 2018:-0.023 2019:-0.016 2020:+0.007 2021:+0.001

## MomSeason06YrPlus  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0069 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.9014 | >= 2.5 | FAIL |
| ic_half_min | 0.0015 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 0.2089 | >= 0.0 | PASS |
| coverage_pct | 40.2717 | >= 40.0 | PASS |
| avg_names_per_decile | 130.0 | >= 30 | PASS |
| ls_n_months | 168 | >= 151 | PASS |
stats: ic_mean=0.0069  ic_tstat_nw=1.9014  icir=0.1497  ic_half1_mean=0.0124  ic_half2_mean=0.0015  ls_sharpe=0.0175  ls_ann_return_pct=0.1219  ls_ann_vol_pct=6.9488  ls_maxdd_pct=-30.7361  ls_hit_rate_pct=51.1905  turnover_d10_pct=86.3788  turnover_d1_pct=86.4737  coverage_pct=40.2717  avg_names_per_decile=130.0  n_months=168  ls_n_months=168  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.0302  ls_beta_mean=-0.0217  ls_beta_fullwindow=-0.0028  ls_sharpe_ex_top_years=-0.2874  ls_top_years=2009,2012,2014  ls_sharpe_bear=0.6885  ls_sharpe_bull=-0.2356
deciles D1..D10 avg %/mo: 1.039,0.976,0.924,1.086,1.052,1.095,1.040,1.241,1.131,1.056
hedge/regime (diagnostics): beta ex-ante -0.0217 full-window -0.0028  raw Sharpe 0.0302  Sharpe ex top years -0.2874 (2009,2012,2014)  bear/bull 0.6885/-0.2356
ic decay: h1=-0.0023  h2=0.0005  h3=-0.0003  h6=-0.0019  h12=0.0055
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0197 0.2509 0.0090 0.1500 312; MID 0.0035 0.0543 0.2590 2.4100 404; SMALL 0.0019 0.0358 -0.1000 -0.8300 582; ALL 0.0069 0.1497 0.0300 0.2100 1299
annual IC: 2008:+0.010 2009:+0.014 2010:+0.004 2011:+0.006 2012:+0.025 2013:+0.011 2014:+0.016 2015:-0.002 2016:+0.020 2017:-0.021 2018:+0.003 2019:+0.002 2020:-0.016 2021:+0.025

## MomSeasonShort  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0013 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.2778 | >= 2.5 | FAIL |
| ic_half_min | -0.0028 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | -0.4366 | >= 0.0 | FAIL |
| coverage_pct | 96.1065 | >= 40.0 | PASS |
| avg_names_per_decile | 188.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0013  ic_tstat_nw=0.2778  icir=0.0195  ic_half1_mean=0.0054  ic_half2_mean=-0.0028  ls_sharpe=0.0959  ls_ann_return_pct=1.0249  ls_ann_vol_pct=10.6821  ls_maxdd_pct=-43.7514  ls_hit_rate_pct=49.2754  turnover_d10_pct=86.8547  turnover_d1_pct=86.9690  coverage_pct=96.1065  avg_names_per_decile=188.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=-0.0424  ls_beta_mean=0.0152  ls_beta_fullwindow=0.0210  ls_sharpe_ex_top_years=-0.3448  ls_top_years=1999,2002,2020  ls_sharpe_bear=0.5741  ls_sharpe_bull=-0.3055
deciles D1..D10 avg %/mo: 1.007,0.982,1.020,0.915,0.931,1.018,1.038,1.110,1.011,0.970
hedge/regime (diagnostics): beta ex-ante 0.0152 full-window 0.0210  raw Sharpe -0.0424  Sharpe ex top years -0.3448 (1999,2002,2020)  bear/bull 0.5741/-0.3055
ic decay: h1=-0.0102  h2=-0.0005  h3=0.0048  h6=0.0042  h12=0.0050
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0025 0.0235 0.1250 2.2700 385; MID -0.0026 -0.0320 -0.2520 -3.1700 571; SMALL 0.0022 0.0364 -0.0030 -0.0300 931; ALL 0.0013 0.0195 -0.0420 -0.4400 1888
annual IC: 1999:+0.032 2000:+0.005 2001:-0.006 2002:+0.067 2003:-0.021 2004:-0.010 2005:+0.014 2006:-0.039 2007:+0.005 2008:+0.000 2009:-0.006 2010:+0.036 2011:+0.038 2012:+0.004 2013:+0.014 2014:-0.013 2015:+0.016 2016:-0.007 2017:-0.035 2018:-0.034 2019:-0.051 2020:+0.036 2021:-0.016

## NOA  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0016 | >= 0.01 | FAIL |
| ic_tstat_nw | 0.6237 | >= 2.5 | FAIL |
| ic_half_min | -0.0019 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 8.6385 | >= 0.0 | PASS |
| coverage_pct | 77.2545 | >= 40.0 | PASS |
| avg_names_per_decile | 151.8 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0016  ic_tstat_nw=0.6237  icir=0.0367  ic_half1_mean=0.0052  ic_half2_mean=-0.0019  ls_sharpe=0.9069  ls_ann_return_pct=7.9221  ls_ann_vol_pct=8.7357  ls_maxdd_pct=-17.9284  ls_hit_rate_pct=57.6087  turnover_d10_pct=11.4379  turnover_d1_pct=14.3243  coverage_pct=77.2545  avg_names_per_decile=151.8  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=1.0082  ls_beta_mean=0.0565  ls_beta_fullwindow=-0.0187  ls_sharpe_ex_top_years=0.6046  ls_top_years=1999,2000,2001  ls_sharpe_bear=1.6457  ls_sharpe_bull=0.5430
deciles D1..D10 avg %/mo: 0.553,0.840,1.036,1.074,1.112,1.131,1.112,1.078,1.231,1.273
hedge/regime (diagnostics): beta ex-ante 0.0565 full-window -0.0187  raw Sharpe 1.0082  Sharpe ex top years 0.6046 (1999,2000,2001)  bear/bull 1.6457/0.5430
ic decay: h1=0.0008  h2=0.0006  h3=0.0005  h6=-0.0000  h12=0.0008
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0145 0.2087 0.7740 12.5900 324; MID 0.0013 0.0197 0.3440 3.8000 470; SMALL -0.0040 -0.0640 0.8190 9.7800 723; ALL 0.0016 0.0367 1.0080 8.6400 1517
annual IC: 1999:+0.026 2000:+0.010 2001:+0.020 2002:-0.014 2003:+0.012 2004:-0.009 2005:+0.001 2006:+0.007 2007:-0.012 2008:+0.011 2009:+0.015 2010:-0.000 2011:+0.003 2012:-0.006 2013:+0.011 2014:-0.005 2015:+0.005 2016:-0.011 2017:+0.014 2018:+0.017 2019:-0.021 2020:-0.013 2021:-0.023

## NetDebtFinance  (stage 1)  → **FAIL**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0034 | >= 0.01 | FAIL |
| ic_tstat_nw | 1.3843 | >= 2.5 | FAIL |
| ic_half_min | -0.0019 | >= 0.0 | FAIL |
| ls_raw_ann_return_pct | 2.2486 | >= 0.0 | PASS |
| coverage_pct | 88.1436 | >= 40.0 | PASS |
| avg_names_per_decile | 173.2 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0034  ic_tstat_nw=1.3843  icir=0.0858  ic_half1_mean=0.0087  ic_half2_mean=-0.0019  ls_sharpe=0.4548  ls_ann_return_pct=2.9469  ls_ann_vol_pct=6.4798  ls_maxdd_pct=-23.5733  ls_hit_rate_pct=55.0725  turnover_d10_pct=18.5468  turnover_d1_pct=16.0870  coverage_pct=88.1436  avg_names_per_decile=173.2  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3208  ls_beta_mean=-0.1182  ls_beta_fullwindow=-0.1584  ls_sharpe_ex_top_years=0.1627  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.0548  ls_sharpe_bull=0.5671
deciles D1..D10 avg %/mo: 0.834,0.934,0.957,0.971,1.035,1.066,1.020,1.097,1.057,1.021
hedge/regime (diagnostics): beta ex-ante -0.1182 full-window -0.1584  raw Sharpe 0.3208  Sharpe ex top years 0.1627 (2000,2003,2021)  bear/bull 0.0548/0.5671
ic decay: h1=0.0022  h2=0.0021  h3=0.0026  h6=0.0036  h12=0.0051
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA -0.0009 -0.0120 -0.0530 -0.6600 364; MID 0.0034 0.0629 0.0310 0.3100 528; SMALL 0.0038 0.0836 0.3620 2.8800 839; ALL 0.0034 0.0858 0.3210 2.2500 1731
annual IC: 1999:+0.017 2000:+0.006 2001:+0.016 2002:+0.031 2003:-0.001 2004:+0.006 2005:+0.004 2006:+0.011 2007:+0.004 2008:+0.005 2009:-0.002 2010:+0.010 2011:-0.007 2012:+0.020 2013:+0.006 2014:+0.002 2015:-0.007 2016:+0.003 2017:-0.018 2018:-0.008 2019:-0.022 2020:-0.026 2021:+0.027

## NetEquityFinance  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0166 | >= 0.01 | PASS |
| ic_tstat_nw | 3.0279 | >= 2.5 | PASS |
| ic_half_min | 0.0132 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.5410 | >= 0.0 | PASS |
| coverage_pct | 93.8925 | >= 40.0 | PASS |
| avg_names_per_decile | 184.5 | >= 30 | PASS |
| ls_n_months | 276 | >= 248 | PASS |
stats: ic_mean=0.0166  ic_tstat_nw=3.0279  icir=0.1876  ic_half1_mean=0.0199  ic_half2_mean=0.0132  ls_sharpe=0.6012  ls_ann_return_pct=7.0203  ls_ann_vol_pct=11.6768  ls_maxdd_pct=-29.4278  ls_hit_rate_pct=56.5217  turnover_d10_pct=10.2157  turnover_d1_pct=14.9138  coverage_pct=93.8925  avg_names_per_decile=184.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3208  ls_beta_mean=-0.4685  ls_beta_fullwindow=-0.5175  ls_sharpe_ex_top_years=0.4335  ls_top_years=2000,2003,2021  ls_sharpe_bear=0.4122  ls_sharpe_bull=0.7328
deciles D1..D10 avg %/mo: 0.794,1.031,1.018,0.988,0.963,1.021,1.072,1.102,1.098,1.172
hedge/regime (diagnostics): beta ex-ante -0.4685 full-window -0.5175  raw Sharpe 0.3208  Sharpe ex top years 0.4335 (2000,2003,2021)  bear/bull 0.4122/0.7328
ic decay: h1=0.0170  h2=0.0161  h3=0.0148  h6=0.0130  h12=0.0112
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0233 0.1849 0.1970 4.1200 380; MID 0.0201 0.2091 0.2510 4.1000 558; SMALL 0.0122 0.1586 0.4200 5.8800 906; ALL 0.0166 0.1876 0.3210 4.5400 1844
annual IC: 1999:+0.005 2000:+0.068 2001:+0.037 2002:+0.049 2003:-0.019 2004:-0.002 2005:-0.005 2006:+0.012 2007:+0.008 2008:+0.052 2009:-0.002 2010:+0.009 2011:+0.043 2012:-0.004 2013:-0.007 2014:+0.026 2015:+0.022 2016:+0.008 2017:+0.005 2018:+0.044 2019:+0.002 2020:-0.045 2021:+0.074

## NetPayoutYield  (stage 1)  → **PASS**
| bar | value | bound | result |
|---|---|---|---|
| ic_mean | 0.0145 | >= 0.01 | PASS |
| ic_tstat_nw | 2.6046 | >= 2.5 | PASS |
| ic_half_min | 0.0142 | >= 0.0 | PASS |
| ls_raw_ann_return_pct | 4.9239 | >= 0.0 | PASS |
| coverage_pct | 65.5130 | >= 40.0 | PASS |
| avg_names_per_decile | 134.6 | >= 30 | PASS |
| ls_n_months | 264 | >= 237 | PASS |
stats: ic_mean=0.0145  ic_tstat_nw=2.6046  icir=0.1685  ic_half1_mean=0.0142  ic_half2_mean=0.0148  ls_sharpe=0.5419  ls_ann_return_pct=6.8731  ls_ann_vol_pct=12.6837  ls_maxdd_pct=-31.1252  ls_hit_rate_pct=55.3030  turnover_d10_pct=15.0176  turnover_d1_pct=16.3648  coverage_pct=65.5130  avg_names_per_decile=134.6  n_months=264  ls_n_months=264  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=100.0  ls_raw_sharpe=0.3568  ls_beta_mean=-0.4116  ls_beta_fullwindow=-0.4116  ls_sharpe_ex_top_years=0.3022  ls_top_years=2002,2009,2021  ls_sharpe_bear=0.5345  ls_sharpe_bull=0.5430
deciles D1..D10 avg %/mo: 0.821,0.909,1.027,0.983,1.000,0.918,0.959,1.083,1.139,1.232
hedge/regime (diagnostics): beta ex-ante -0.4116 full-window -0.4116  raw Sharpe 0.3568  Sharpe ex top years 0.3022 (2002,2009,2021)  bear/bull 0.5345/0.5430
ic decay: h1=0.0132  h2=0.0134  h3=0.0120  h6=0.0109  h12=0.0100
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0180 0.1494 0.3790 7.5000 298; MID 0.0173 0.1735 0.3470 5.5600 416; SMALL 0.0114 0.1456 0.2840 4.0400 630; ALL 0.0145 0.1685 0.3570 4.9200 1345
annual IC: 2000:+0.045 2001:+0.032 2002:+0.062 2003:-0.019 2004:+0.004 2005:-0.013 2006:+0.013 2007:-0.017 2008:+0.041 2009:+0.018 2010:-0.009 2011:+0.042 2012:-0.006 2013:+0.011 2014:+0.029 2015:+0.012 2016:+0.025 2017:-0.016 2018:+0.031 2019:-0.001 2020:-0.045 2021:+0.081
