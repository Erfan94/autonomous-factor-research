# RUN 032 BATCH stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE c961f5791816 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v9: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE

## OperProfRD  (stage 2)  → **FAIL**
rung 1 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE  | base IC 0.0323 Sharpe 0.932 ann ret 14.87% MaxDD -43.7
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | -0.4241 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.9243 | >= -2.0 | PASS |
stats: ic_mean=0.0322  ic_tstat_nw=4.4982  icir=0.3147  ic_half1_mean=0.0463  ic_half2_mean=0.0182  ls_sharpe=0.9442  ls_ann_return_pct=15.0407  ls_ann_vol_pct=15.9290  ls_maxdd_pct=-43.4431  ls_hit_rate_pct=62.3188  turnover_d10_pct=44.2688  turnover_d1_pct=39.4193  coverage_pct=70.7416  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=42.8928  resid_ic_mean=-0.0011  resid_ic_tstat_nw=-0.4241  spanning_alpha_ann_pct=2.6608  spanning_alpha_tstat_nw=0.8643  spanning_r2=0.3545  corr_to_composite=0.5954  paired_delta_ic_mean=-0.0000  paired_delta_ic_tstat=-0.1967  paired_delta_ls_mean=0.0001  paired_delta_ls_tstat=0.9243  delta_ls_sharpe=0.0127  maxdd_worsening_pct=-0.2236  ls_raw_sharpe=0.5896  ls_beta_mean=-0.6598  ls_beta_fullwindow=-0.7355  ls_sharpe_ex_top_years=0.5952  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9507  ls_sharpe_bull=1.0835
deciles D1..D10 avg %/mo: 0.332,0.485,0.821,0.975,0.970,1.147,1.145,1.200,1.286,1.309
hedge/regime (diagnostics): beta ex-ante -0.6598 full-window -0.7355  raw Sharpe 0.5896  Sharpe ex top years 0.5952 (2000,2001,2021)  bear/bull 0.9507/1.0835
ic decay: h1=0.0246  h2=0.0216  h3=0.0224  h6=0.0199  h12=0.0225
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0304 0.2217 0.4110 9.8800 393; MID 0.0284 0.2521 0.5870 12.7000 589; SMALL 0.0337 0.3435 0.5790 11.5000 981; ALL 0.0322 0.3147 0.5900 11.7200 1964
annual IC: 1999:+0.027 2000:+0.125 2001:+0.101 2002:+0.109 2003:-0.002 2004:+0.037 2005:+0.037 2006:+0.025 2007:-0.007 2008:+0.081 2009:-0.033 2010:+0.022 2011:+0.046 2012:+0.012 2013:+0.020 2014:+0.034 2015:+0.034 2016:+0.016 2017:-0.003 2018:+0.036 2019:-0.029 2020:-0.058 2021:+0.111

## IdioVol3F  (stage 2)  → **PASS**
rung 2 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE  | base IC 0.0323 Sharpe 0.932 ann ret 14.87% MaxDD -43.7
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.0307 | > 2.0 | PASS |
| paired_delta_ls_tstat | 0.8872 | >= -2.0 | PASS |
stats: ic_mean=0.0326  ic_tstat_nw=4.4757  icir=0.3120  ic_half1_mean=0.0457  ic_half2_mean=0.0195  ls_sharpe=0.9193  ls_ann_return_pct=15.2529  ls_ann_vol_pct=16.5916  ls_maxdd_pct=-45.7772  ls_hit_rate_pct=63.4058  turnover_d10_pct=39.7994  turnover_d1_pct=35.3912  coverage_pct=96.7275  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3884  resid_ic_mean=0.0065  resid_ic_tstat_nw=2.0307  spanning_alpha_ann_pct=-2.8656  spanning_alpha_tstat_nw=-0.8487  spanning_r2=0.5134  corr_to_composite=0.7165  paired_delta_ic_mean=0.0003  paired_delta_ic_tstat=0.8130  paired_delta_ls_mean=0.0003  paired_delta_ls_tstat=0.8872  delta_ls_sharpe=-0.0123  maxdd_worsening_pct=2.1106  ls_raw_sharpe=0.5785  ls_beta_mean=-0.6803  ls_beta_fullwindow=-0.7519  ls_sharpe_ex_top_years=0.5749  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8423  ls_sharpe_bull=1.0930
deciles D1..D10 avg %/mo: 0.272,0.560,0.813,0.936,1.037,1.125,1.130,1.233,1.296,1.267
hedge/regime (diagnostics): beta ex-ante -0.6803 full-window -0.7519  raw Sharpe 0.5785  Sharpe ex top years 0.5749 (2000,2001,2021)  bear/bull 0.8423/1.0930
ic decay: h1=0.0251  h2=0.0225  h3=0.0235  h6=0.0206  h12=0.0228
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0305 0.2220 0.3890 9.5500 393; MID 0.0292 0.2569 0.5400 12.0100 589; SMALL 0.0338 0.3352 0.5310 10.9200 981; ALL 0.0326 0.3120 0.5780 11.9400 1964
annual IC: 1999:+0.026 2000:+0.127 2001:+0.098 2002:+0.106 2003:-0.004 2004:+0.035 2005:+0.037 2006:+0.025 2007:-0.004 2008:+0.083 2009:-0.035 2010:+0.021 2011:+0.051 2012:+0.012 2013:+0.023 2014:+0.033 2015:+0.037 2016:+0.017 2017:-0.003 2018:+0.039 2019:-0.029 2020:-0.060 2021:+0.114

## NetEquityFinance  (stage 2)  → **FAIL**
rung 3 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F  | base IC 0.0326 Sharpe 0.919 ann ret 15.25% MaxDD -45.8
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.3957 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.4727 | >= -2.0 | PASS |
stats: ic_mean=0.0333  ic_tstat_nw=4.4483  icir=0.3090  ic_half1_mean=0.0464  ic_half2_mean=0.0203  ls_sharpe=0.9081  ls_ann_return_pct=15.4408  ls_ann_vol_pct=17.0031  ls_maxdd_pct=-47.0203  ls_hit_rate_pct=63.7681  turnover_d10_pct=40.5758  turnover_d1_pct=35.0540  coverage_pct=93.8925  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3131  resid_ic_mean=0.0035  resid_ic_tstat_nw=1.3957  spanning_alpha_ann_pct=-0.5478  spanning_alpha_tstat_nw=-0.2849  spanning_r2=0.4970  corr_to_composite=0.7050  paired_delta_ic_mean=0.0008  paired_delta_ic_tstat=1.8618  paired_delta_ls_mean=0.0002  paired_delta_ls_tstat=0.4727  delta_ls_sharpe=-0.0112  maxdd_worsening_pct=1.2430  ls_raw_sharpe=0.5617  ls_beta_mean=-0.7074  ls_beta_fullwindow=-0.7779  ls_sharpe_ex_top_years=0.5689  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.8670  ls_sharpe_bull=1.0680
deciles D1..D10 avg %/mo: 0.253,0.595,0.799,0.909,1.049,1.172,1.128,1.178,1.337,1.249
hedge/regime (diagnostics): beta ex-ante -0.7074 full-window -0.7779  raw Sharpe 0.5617  Sharpe ex top years 0.5689 (2000,2001,2021)  bear/bull 0.8670/1.0680
ic decay: h1=0.0259  h2=0.0231  h3=0.0240  h6=0.0209  h12=0.0232
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0315 0.2217 0.4440 11.4200 393; MID 0.0305 0.2599 0.5890 13.2800 589; SMALL 0.0343 0.3294 0.5220 10.8400 981; ALL 0.0333 0.3090 0.5620 11.9500 1964
annual IC: 1999:+0.024 2000:+0.131 2001:+0.100 2002:+0.110 2003:-0.007 2004:+0.035 2005:+0.036 2006:+0.025 2007:-0.004 2008:+0.086 2009:-0.036 2010:+0.022 2011:+0.054 2012:+0.012 2013:+0.023 2014:+0.035 2015:+0.038 2016:+0.017 2017:-0.003 2018:+0.041 2019:-0.027 2020:-0.061 2021:+0.116

## CF  (stage 2)  → **FAIL**
rung 4 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F  | base IC 0.0326 Sharpe 0.919 ann ret 15.25% MaxDD -45.8
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.0204 | > 2.0 | FAIL |
| paired_delta_ls_tstat | -0.7609 | >= -2.0 | PASS |
stats: ic_mean=0.0329  ic_tstat_nw=4.4313  icir=0.3081  ic_half1_mean=0.0460  ic_half2_mean=0.0197  ls_sharpe=0.8610  ls_ann_return_pct=14.8569  ls_ann_vol_pct=17.2557  ls_maxdd_pct=-44.9199  ls_hit_rate_pct=63.0435  turnover_d10_pct=39.6306  turnover_d1_pct=34.8617  coverage_pct=96.0589  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3884  resid_ic_mean=0.0023  resid_ic_tstat_nw=1.0204  spanning_alpha_ann_pct=-7.6126  spanning_alpha_tstat_nw=-2.6989  spanning_r2=0.5374  corr_to_composite=0.7331  paired_delta_ic_mean=0.0003  paired_delta_ic_tstat=0.7164  paired_delta_ls_mean=-0.0003  paired_delta_ls_tstat=-0.7609  delta_ls_sharpe=-0.0583  maxdd_worsening_pct=-0.8574  ls_raw_sharpe=0.5238  ls_beta_mean=-0.7120  ls_beta_fullwindow=-0.7909  ls_sharpe_ex_top_years=0.5190  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.6660  ls_sharpe_bull=1.0966
deciles D1..D10 avg %/mo: 0.317,0.547,0.802,0.930,1.061,1.127,1.156,1.198,1.277,1.256
hedge/regime (diagnostics): beta ex-ante -0.7120 full-window -0.7909  raw Sharpe 0.5238  Sharpe ex top years 0.5190 (2000,2001,2021)  bear/bull 0.6660/1.0966
ic decay: h1=0.0255  h2=0.0229  h3=0.0239  h6=0.0211  h12=0.0236
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0314 0.2266 0.4010 10.0900 393; MID 0.0294 0.2541 0.5270 11.9800 589; SMALL 0.0339 0.3279 0.5070 10.9500 981; ALL 0.0329 0.3081 0.5240 11.2700 1964
annual IC: 1999:+0.025 2000:+0.128 2001:+0.098 2002:+0.109 2003:-0.007 2004:+0.037 2005:+0.038 2006:+0.026 2007:-0.002 2008:+0.085 2009:-0.038 2010:+0.020 2011:+0.054 2012:+0.011 2013:+0.022 2014:+0.035 2015:+0.038 2016:+0.015 2017:-0.001 2018:+0.039 2019:-0.027 2020:-0.063 2021:+0.115

## STreversal  (stage 2)  → **PASS**
rung 5 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F  | base IC 0.0326 Sharpe 0.919 ann ret 15.25% MaxDD -45.8
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 3.8089 | > 2.0 | PASS |
| paired_delta_ls_tstat | -0.5362 | >= -2.0 | PASS |
stats: ic_mean=0.0355  ic_tstat_nw=5.3630  icir=0.3806  ic_half1_mean=0.0475  ic_half2_mean=0.0236  ls_sharpe=0.9423  ls_ann_return_pct=14.6139  ls_ann_vol_pct=15.5088  ls_maxdd_pct=-39.5291  ls_hit_rate_pct=59.4203  turnover_d10_pct=59.0772  turnover_d1_pct=59.3116  coverage_pct=99.8027  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3884  resid_ic_mean=0.0153  resid_ic_tstat_nw=3.8089  spanning_alpha_ann_pct=-1.8778  spanning_alpha_tstat_nw=-0.4845  spanning_r2=0.0084  corr_to_composite=0.0917  paired_delta_ic_mean=0.0029  paired_delta_ic_tstat=1.5044  paired_delta_ls_mean=-0.0005  paired_delta_ls_tstat=-0.5362  delta_ls_sharpe=0.0230  maxdd_worsening_pct=-6.2481  ls_raw_sharpe=0.7372  ls_beta_mean=-0.4800  ls_beta_fullwindow=-0.5122  ls_sharpe_ex_top_years=0.5653  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.0847  ls_sharpe_bull=1.0636
deciles D1..D10 avg %/mo: 0.312,0.562,0.741,0.861,0.933,1.040,1.178,1.255,1.390,1.398
hedge/regime (diagnostics): beta ex-ante -0.4800 full-window -0.5122  raw Sharpe 0.7372  Sharpe ex top years 0.5653 (2000,2001,2021)  bear/bull 1.0847/1.0636
ic decay: h1=0.0235  h2=0.0180  h3=0.0209  h6=0.0181  h12=0.0232
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0322 0.2581 0.4270 9.3700 393; MID 0.0304 0.3005 0.5920 11.5200 589; SMALL 0.0379 0.4182 0.7820 13.8000 981; ALL 0.0355 0.3806 0.7370 13.0300 1964
annual IC: 1999:+0.029 2000:+0.117 2001:+0.112 2002:+0.116 2003:+0.000 2004:+0.045 2005:+0.034 2006:+0.033 2007:-0.023 2008:+0.075 2009:-0.021 2010:+0.030 2011:+0.039 2012:+0.024 2013:+0.024 2014:+0.037 2015:+0.035 2016:+0.022 2017:-0.001 2018:+0.033 2019:-0.001 2020:-0.047 2021:+0.105
