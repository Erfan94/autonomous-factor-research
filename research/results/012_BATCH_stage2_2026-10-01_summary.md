# RUN 012 BATCH stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE f9d9d9d95731 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v0: Size, Value, Profitability, Investment, Momentum

## PctAcc  (stage 2)  → **PASS**
rung 1 vs Size,Value,Profitability,Investment,Momentum  | base IC 0.0145 Sharpe 0.600 ann ret 7.32% MaxDD -45.6
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 4.6736 | > 2.0 | PASS |
| paired_delta_ls_tstat | 0.0874 | >= -2.0 | PASS |
stats: ic_mean=0.0169  ic_tstat_nw=3.0165  icir=0.2085  ic_half1_mean=0.0304  ic_half2_mean=0.0033  ls_sharpe=0.6139  ls_ann_return_pct=7.3826  ls_ann_vol_pct=12.0247  ls_maxdd_pct=-41.2812  ls_hit_rate_pct=56.5217  turnover_d10_pct=27.6281  turnover_d1_pct=24.0838  coverage_pct=95.5826  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=91.3598  resid_ic_mean=0.0098  resid_ic_tstat_nw=4.6736  spanning_alpha_ann_pct=2.6939  spanning_alpha_tstat_nw=2.4748  spanning_r2=0.1542  corr_to_composite=0.3927  paired_delta_ic_mean=0.0023  paired_delta_ic_tstat=2.8148  paired_delta_ls_mean=0.0001  paired_delta_ls_tstat=0.0874  delta_ls_sharpe=0.0140  maxdd_worsening_pct=-4.2787  ls_raw_sharpe=0.7371  ls_beta_mean=-0.0742  ls_beta_fullwindow=-0.1210  ls_sharpe_ex_top_years=0.2017  ls_top_years=2000,2001,2003  ls_sharpe_bear=0.8526  ls_sharpe_bull=0.5544
deciles D1..D10 avg %/mo: 0.488,0.677,0.740,0.919,0.993,0.992,1.044,1.178,1.382,1.256
hedge/regime (diagnostics): beta ex-ante -0.0742 full-window -0.1210  raw Sharpe 0.7371  Sharpe ex top years 0.2017 (2000,2001,2003)  bear/bull 0.8526/0.5544
ic decay: h1=0.0113  h2=0.0097  h3=0.0116  h6=0.0097  h12=0.0120
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0159 0.1557 0.2760 5.6600 393; MID 0.0147 0.1671 0.7350 11.7900 589; SMALL 0.0193 0.2748 0.7060 8.1000 981; ALL 0.0169 0.2085 0.7370 9.2200 1964
annual IC: 1999:+0.015 2000:+0.064 2001:+0.091 2002:+0.075 2003:+0.021 2004:+0.035 2005:+0.038 2006:+0.004 2007:-0.036 2008:+0.047 2009:-0.021 2010:+0.029 2011:+0.000 2012:+0.018 2013:+0.032 2014:+0.004 2015:+0.001 2016:+0.029 2017:-0.024 2018:-0.016 2019:-0.027 2020:-0.041 2021:+0.049

## CBOperProf  (stage 2)  → **PASS**
rung 2 vs Size,Value,Profitability,Investment,Momentum,PctAcc  | base IC 0.0169 Sharpe 0.614 ann ret 7.38% MaxDD -41.3
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 3.0204 | > 2.0 | PASS |
| paired_delta_ls_tstat | 0.9458 | >= -2.0 | PASS |
stats: ic_mean=0.0169  ic_tstat_nw=3.0237  icir=0.2099  ic_half1_mean=0.0312  ic_half2_mean=0.0025  ls_sharpe=0.6606  ls_ann_return_pct=7.8213  ls_ann_vol_pct=11.8406  ls_maxdd_pct=-37.0655  ls_hit_rate_pct=55.7971  turnover_d10_pct=27.9507  turnover_d1_pct=24.4075  coverage_pct=73.4223  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=72.7197  resid_ic_mean=0.0104  resid_ic_tstat_nw=3.0204  spanning_alpha_ann_pct=9.7638  spanning_alpha_tstat_nw=3.7127  spanning_r2=0.0370  corr_to_composite=0.1923  paired_delta_ic_mean=-0.0000  paired_delta_ic_tstat=-0.0058  paired_delta_ls_mean=0.0004  paired_delta_ls_tstat=0.9458  delta_ls_sharpe=0.0466  maxdd_worsening_pct=-4.2157  ls_raw_sharpe=0.7770  ls_beta_mean=-0.0631  ls_beta_fullwindow=-0.1220  ls_sharpe_ex_top_years=0.2490  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9231  ls_sharpe_bull=0.5730
deciles D1..D10 avg %/mo: 0.470,0.624,0.767,0.890,0.941,1.040,1.049,1.212,1.414,1.264
hedge/regime (diagnostics): beta ex-ante -0.0631 full-window -0.1220  raw Sharpe 0.7770  Sharpe ex top years 0.2490 (2000,2001,2021)  bear/bull 0.9231/0.5730
ic decay: h1=0.0110  h2=0.0095  h3=0.0113  h6=0.0093  h12=0.0116
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0162 0.1660 0.3490 6.7500 393; MID 0.0144 0.1641 0.7430 11.4800 589; SMALL 0.0194 0.2781 0.7810 8.7100 981; ALL 0.0169 0.2099 0.7770 9.5300 1964
annual IC: 1999:+0.022 2000:+0.065 2001:+0.092 2002:+0.076 2003:+0.022 2004:+0.035 2005:+0.038 2006:+0.003 2007:-0.040 2008:+0.050 2009:-0.020 2010:+0.031 2011:-0.000 2012:+0.014 2013:+0.027 2014:+0.002 2015:+0.000 2016:+0.028 2017:-0.024 2018:-0.009 2019:-0.032 2020:-0.039 2021:+0.048

## ShareIss5Y  (stage 2)  → **PASS**
rung 3 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf  | base IC 0.0169 Sharpe 0.661 ann ret 7.82% MaxDD -37.1
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 3.6085 | > 2.0 | PASS |
| paired_delta_ls_tstat | 2.8334 | >= -2.0 | PASS |
stats: ic_mean=0.0215  ic_tstat_nw=3.9766  icir=0.2843  ic_half1_mean=0.0336  ic_half2_mean=0.0095  ls_sharpe=0.8479  ls_ann_return_pct=10.2876  ls_ann_vol_pct=12.1324  ls_maxdd_pct=-41.9210  ls_hit_rate_pct=59.4203  turnover_d10_pct=26.3407  turnover_d1_pct=22.9657  coverage_pct=62.6064  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5778  resid_ic_mean=0.0120  resid_ic_tstat_nw=3.6085  spanning_alpha_ann_pct=7.9968  spanning_alpha_tstat_nw=4.5107  spanning_r2=0.0156  corr_to_composite=0.1248  paired_delta_ic_mean=0.0047  paired_delta_ic_tstat=3.0344  paired_delta_ls_mean=0.0021  paired_delta_ls_tstat=2.8334  delta_ls_sharpe=0.1874  maxdd_worsening_pct=4.8555  ls_raw_sharpe=0.8738  ls_beta_mean=-0.1575  ls_beta_fullwindow=-0.1917  ls_sharpe_ex_top_years=0.4646  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0370  ls_sharpe_bull=0.8064
deciles D1..D10 avg %/mo: 0.444,0.553,0.775,0.850,0.955,1.046,1.174,1.199,1.314,1.359
hedge/regime (diagnostics): beta ex-ante -0.1575 full-window -0.1917  raw Sharpe 0.8738  Sharpe ex top years 0.4646 (2000,2001,2021)  bear/bull 1.0370/0.8064
ic decay: h1=0.0155  h2=0.0141  h3=0.0159  h6=0.0141  h12=0.0153
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0229 0.2289 0.4360 8.5500 393; MID 0.0204 0.2436 0.8490 13.3100 589; SMALL 0.0216 0.3171 0.8870 10.1200 981; ALL 0.0215 0.2843 0.8740 10.9900 1964
annual IC: 1999:+0.022 2000:+0.065 2001:+0.092 2002:+0.076 2003:+0.020 2004:+0.036 2005:+0.037 2006:+0.008 2007:-0.037 2008:+0.063 2009:-0.020 2010:+0.033 2011:+0.020 2012:+0.015 2013:+0.027 2014:+0.014 2015:+0.012 2016:+0.024 2017:-0.011 2018:+0.010 2019:-0.031 2020:-0.044 2021:+0.065

## cfp  (stage 2)  → **PASS**
rung 4 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y  | base IC 0.0215 Sharpe 0.848 ann ret 10.29% MaxDD -41.9
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.9741 | > 2.0 | PASS |
| paired_delta_ls_tstat | 2.1869 | >= -2.0 | PASS |
stats: ic_mean=0.0249  ic_tstat_nw=4.5109  icir=0.3273  ic_half1_mean=0.0375  ic_half2_mean=0.0124  ls_sharpe=0.9960  ls_ann_return_pct=12.0191  ls_ann_vol_pct=12.0674  ls_maxdd_pct=-40.6324  ls_hit_rate_pct=62.6812  turnover_d10_pct=25.1677  turnover_d1_pct=22.3010  coverage_pct=95.6727  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5701  resid_ic_mean=0.0104  resid_ic_tstat_nw=2.9741  spanning_alpha_ann_pct=1.1015  spanning_alpha_tstat_nw=0.4047  spanning_r2=0.2629  corr_to_composite=0.5128  paired_delta_ic_mean=0.0034  paired_delta_ic_tstat=3.0960  paired_delta_ls_mean=0.0014  paired_delta_ls_tstat=2.1869  delta_ls_sharpe=0.1481  maxdd_worsening_pct=-1.2886  ls_raw_sharpe=0.9134  ls_beta_mean=-0.2295  ls_beta_fullwindow=-0.2627  ls_sharpe_ex_top_years=0.6135  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2300  ls_sharpe_bull=0.9550
deciles D1..D10 avg %/mo: 0.354,0.615,0.704,0.854,0.979,1.126,1.122,1.250,1.319,1.346
hedge/regime (diagnostics): beta ex-ante -0.2295 full-window -0.2627  raw Sharpe 0.9134  Sharpe ex top years 0.6135 (2000,2001,2021)  bear/bull 1.2300/0.9550
ic decay: h1=0.0183  h2=0.0169  h3=0.0185  h6=0.0160  h12=0.0175
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2567 0.4900 9.6500 393; MID 0.0236 0.2756 0.8000 12.9900 589; SMALL 0.0248 0.3458 0.9310 11.1500 981; ALL 0.0249 0.3273 0.9130 11.9000 1964
annual IC: 1999:+0.025 2000:+0.079 2001:+0.088 2002:+0.090 2003:+0.015 2004:+0.038 2005:+0.041 2006:+0.009 2007:-0.023 2008:+0.063 2009:-0.017 2010:+0.027 2011:+0.026 2012:+0.013 2013:+0.032 2014:+0.024 2015:+0.013 2016:+0.023 2017:-0.007 2018:+0.013 2019:-0.033 2020:-0.046 2021:+0.079

## XFIN  (stage 2)  → **PASS**
rung 5 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp  | base IC 0.0249 Sharpe 0.996 ann ret 12.02% MaxDD -40.6
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 3.2735 | > 2.0 | PASS |
| paired_delta_ls_tstat | -0.6374 | >= -2.0 | PASS |
stats: ic_mean=0.0245  ic_tstat_nw=4.2703  icir=0.3091  ic_half1_mean=0.0380  ic_half2_mean=0.0110  ls_sharpe=0.9141  ls_ann_return_pct=11.5584  ls_ann_vol_pct=12.6443  ls_maxdd_pct=-47.7533  ls_hit_rate_pct=64.4928  turnover_d10_pct=25.0179  turnover_d1_pct=22.3389  coverage_pct=95.6379  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=47.5459  resid_ic_mean=0.0069  resid_ic_tstat_nw=3.2735  spanning_alpha_ann_pct=2.4208  spanning_alpha_tstat_nw=1.2827  spanning_r2=0.2805  corr_to_composite=0.5296  paired_delta_ic_mean=-0.0005  paired_delta_ic_tstat=-0.6208  paired_delta_ls_mean=-0.0004  paired_delta_ls_tstat=-0.6374  delta_ls_sharpe=-0.0819  maxdd_worsening_pct=7.1209  ls_raw_sharpe=0.8082  ls_beta_mean=-0.2975  ls_beta_fullwindow=-0.3445  ls_sharpe_ex_top_years=0.4789  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1271  ls_sharpe_bull=0.8731
deciles D1..D10 avg %/mo: 0.330,0.664,0.692,0.843,1.050,1.107,1.166,1.226,1.305,1.287
hedge/regime (diagnostics): beta ex-ante -0.2975 full-window -0.3445  raw Sharpe 0.8082  Sharpe ex top years 0.4789 (2000,2001,2021)  bear/bull 1.1271/0.8731
ic decay: h1=0.0183  h2=0.0170  h3=0.0185  h6=0.0162  h12=0.0178
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2360 0.3480 7.1900 393; MID 0.0228 0.2560 0.8420 14.4200 589; SMALL 0.0239 0.3191 0.7630 9.9500 981; ALL 0.0245 0.3091 0.8080 11.4900 1964
annual IC: 1999:+0.024 2000:+0.088 2001:+0.084 2002:+0.090 2003:+0.012 2004:+0.035 2005:+0.042 2006:+0.012 2007:-0.019 2008:+0.064 2009:-0.018 2010:+0.027 2011:+0.023 2012:+0.012 2013:+0.028 2014:+0.023 2015:+0.012 2016:+0.024 2017:-0.012 2018:+0.012 2019:-0.033 2020:-0.050 2021:+0.085
