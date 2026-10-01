# RUN 023 BATCH stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE d27916e567f2 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v5: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN

## GP  (stage 2)  → **PASS**
rung 1 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN  | base IC 0.0245 Sharpe 0.914 ann ret 11.56% MaxDD -47.8
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.7412 | > 2.0 | PASS |
| paired_delta_ls_tstat | 0.4291 | >= -2.0 | PASS |
stats: ic_mean=0.0242  ic_tstat_nw=4.2330  icir=0.3058  ic_half1_mean=0.0377  ic_half2_mean=0.0107  ls_sharpe=0.9255  ls_ann_return_pct=11.7157  ls_ann_vol_pct=12.6589  ls_maxdd_pct=-49.4236  ls_hit_rate_pct=61.9565  turnover_d10_pct=25.2323  turnover_d1_pct=22.2917  coverage_pct=74.3904  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=46.5243  resid_ic_mean=0.0073  resid_ic_tstat_nw=2.7412  spanning_alpha_ann_pct=7.7796  spanning_alpha_tstat_nw=3.6178  spanning_r2=0.1401  corr_to_composite=0.3744  paired_delta_ic_mean=-0.0003  paired_delta_ic_tstat=-0.7907  paired_delta_ls_mean=0.0001  paired_delta_ls_tstat=0.4291  delta_ls_sharpe=0.0114  maxdd_worsening_pct=1.6703  ls_raw_sharpe=0.8434  ls_beta_mean=-0.2766  ls_beta_fullwindow=-0.3225  ls_sharpe_ex_top_years=0.4897  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2686  ls_sharpe_bull=0.8422
deciles D1..D10 avg %/mo: 0.301,0.690,0.661,0.861,1.046,1.143,1.151,1.280,1.248,1.288
hedge/regime (diagnostics): beta ex-ante -0.2766 full-window -0.3225  raw Sharpe 0.8434  Sharpe ex top years 0.4897 (2000,2001,2021)  bear/bull 1.2686/0.8422
ic decay: h1=0.0181  h2=0.0169  h3=0.0184  h6=0.0162  h12=0.0177
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0259 0.2375 0.3560 7.3200 393; MID 0.0221 0.2498 0.8560 14.4600 589; SMALL 0.0239 0.3198 0.8130 10.3300 981; ALL 0.0242 0.3058 0.8430 11.8500 1964
annual IC: 1999:+0.023 2000:+0.085 2001:+0.085 2002:+0.089 2003:+0.013 2004:+0.034 2005:+0.042 2006:+0.013 2007:-0.023 2008:+0.065 2009:-0.017 2010:+0.029 2011:+0.024 2012:+0.012 2013:+0.027 2014:+0.020 2015:+0.012 2016:+0.022 2017:-0.013 2018:+0.015 2019:-0.035 2020:-0.049 2021:+0.083

## ShareIss1Y  (stage 2)  → **FAIL**
rung 2 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP  | base IC 0.0242 Sharpe 0.925 ann ret 11.72% MaxDD -49.4
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.8793 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.1724 | >= -2.0 | PASS |
stats: ic_mean=0.0248  ic_tstat_nw=4.1964  icir=0.3053  ic_half1_mean=0.0385  ic_half2_mean=0.0112  ls_sharpe=0.8999  ls_ann_return_pct=11.7883  ls_ann_vol_pct=13.0997  ls_maxdd_pct=-51.4097  ls_hit_rate_pct=61.5942  turnover_d10_pct=25.1716  turnover_d1_pct=21.9685  coverage_pct=90.4895  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=46.5134  resid_ic_mean=0.0044  resid_ic_tstat_nw=1.8793  spanning_alpha_ann_pct=3.9471  spanning_alpha_tstat_nw=2.6148  spanning_r2=0.3073  corr_to_composite=0.5544  paired_delta_ic_mean=0.0006  paired_delta_ic_tstat=1.7620  paired_delta_ls_mean=0.0001  paired_delta_ls_tstat=0.1724  delta_ls_sharpe=-0.0256  maxdd_worsening_pct=1.9862  ls_raw_sharpe=0.8177  ls_beta_mean=-0.2875  ls_beta_fullwindow=-0.3277  ls_sharpe_ex_top_years=0.4804  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.1245  ls_sharpe_bull=0.8416
deciles D1..D10 avg %/mo: 0.289,0.649,0.687,0.878,1.024,1.182,1.104,1.297,1.280,1.280
hedge/regime (diagnostics): beta ex-ante -0.2875 full-window -0.3277  raw Sharpe 0.8177  Sharpe ex top years 0.4804 (2000,2001,2021)  bear/bull 1.1245/0.8416
ic decay: h1=0.0186  h2=0.0172  h3=0.0187  h6=0.0164  h12=0.0180
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0268 0.2447 0.3920 8.2200 393; MID 0.0233 0.2572 0.7880 13.4400 589; SMALL 0.0241 0.3143 0.7620 10.3300 981; ALL 0.0248 0.3053 0.8180 11.8900 1964
annual IC: 1999:+0.023 2000:+0.090 2001:+0.089 2002:+0.094 2003:+0.011 2004:+0.034 2005:+0.042 2006:+0.013 2007:-0.026 2008:+0.065 2009:-0.016 2010:+0.029 2011:+0.027 2012:+0.012 2013:+0.029 2014:+0.021 2015:+0.013 2016:+0.023 2017:-0.015 2018:+0.013 2019:-0.035 2020:-0.051 2021:+0.086

## MaxRet  (stage 2)  → **PASS**
rung 3 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP  | base IC 0.0242 Sharpe 0.925 ann ret 11.72% MaxDD -49.4
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 4.0076 | > 2.0 | PASS |
| paired_delta_ls_tstat | 1.7489 | >= -2.0 | PASS |
stats: ic_mean=0.0305  ic_tstat_nw=4.4930  icir=0.3160  ic_half1_mean=0.0444  ic_half2_mean=0.0166  ls_sharpe=0.9512  ls_ann_return_pct=13.9480  ls_ann_vol_pct=14.6632  ls_maxdd_pct=-41.6776  ls_hit_rate_pct=62.3188  turnover_d10_pct=43.4076  turnover_d1_pct=39.4165  coverage_pct=99.8027  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=46.5243  resid_ic_mean=0.0179  resid_ic_tstat_nw=4.0076  spanning_alpha_ann_pct=4.8546  spanning_alpha_tstat_nw=1.3829  spanning_r2=0.1273  corr_to_composite=0.3567  paired_delta_ic_mean=0.0063  paired_delta_ic_tstat=2.6068  paired_delta_ls_mean=0.0019  paired_delta_ls_tstat=1.7489  delta_ls_sharpe=0.0257  maxdd_worsening_pct=-7.7460  ls_raw_sharpe=0.6220  ls_beta_mean=-0.5866  ls_beta_fullwindow=-0.6493  ls_sharpe_ex_top_years=0.6234  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9739  ls_sharpe_bull=1.0454
deciles D1..D10 avg %/mo: 0.332,0.487,0.806,0.995,0.994,1.158,1.151,1.146,1.330,1.270
hedge/regime (diagnostics): beta ex-ante -0.5866 full-window -0.6493  raw Sharpe 0.6220  Sharpe ex top years 0.6234 (2000,2001,2021)  bear/bull 0.9739/1.0454
ic decay: h1=0.0232  h2=0.0203  h3=0.0212  h6=0.0194  h12=0.0219
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0296 0.2199 0.4150 10.1100 393; MID 0.0278 0.2580 0.6250 12.5000 589; SMALL 0.0311 0.3431 0.6530 11.4900 981; ALL 0.0305 0.3160 0.6220 11.2600 1964
annual IC: 1999:+0.027 2000:+0.112 2001:+0.097 2002:+0.104 2003:+0.001 2004:+0.035 2005:+0.038 2006:+0.023 2007:-0.011 2008:+0.080 2009:-0.026 2010:+0.025 2011:+0.040 2012:+0.011 2013:+0.023 2014:+0.033 2015:+0.030 2016:+0.016 2017:-0.005 2018:+0.033 2019:-0.028 2020:-0.058 2021:+0.104

## roaq  (stage 2)  → **PASS**
rung 4 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet  | base IC 0.0305 Sharpe 0.951 ann ret 13.95% MaxDD -41.7
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 3.7278 | > 2.0 | PASS |
| paired_delta_ls_tstat | 1.9515 | >= -2.0 | PASS |
stats: ic_mean=0.0320  ic_tstat_nw=4.5036  icir=0.3156  ic_half1_mean=0.0460  ic_half2_mean=0.0180  ls_sharpe=0.9673  ls_ann_return_pct=15.1807  ls_ann_vol_pct=15.6937  ls_maxdd_pct=-43.3632  ls_hit_rate_pct=64.1304  turnover_d10_pct=44.0720  turnover_d1_pct=39.5197  coverage_pct=96.2922  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3893  resid_ic_mean=0.0119  resid_ic_tstat_nw=3.7278  spanning_alpha_ann_pct=1.0597  spanning_alpha_tstat_nw=0.3910  spanning_r2=0.4389  corr_to_composite=0.6625  paired_delta_ic_mean=0.0015  paired_delta_ic_tstat=2.6622  paired_delta_ls_mean=0.0010  paired_delta_ls_tstat=1.9515  delta_ls_sharpe=0.0161  maxdd_worsening_pct=1.6856  ls_raw_sharpe=0.6127  ls_beta_mean=-0.6497  ls_beta_fullwindow=-0.7212  ls_sharpe_ex_top_years=0.6039  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9605  ls_sharpe_bull=1.1220
deciles D1..D10 avg %/mo: 0.313,0.519,0.823,0.960,0.976,1.141,1.152,1.171,1.304,1.311
hedge/regime (diagnostics): beta ex-ante -0.6497 full-window -0.7212  raw Sharpe 0.6127  Sharpe ex top years 0.6039 (2000,2001,2021)  bear/bull 0.9605/1.1220
ic decay: h1=0.0246  h2=0.0216  h3=0.0224  h6=0.0197  h12=0.0222
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0299 0.2190 0.4130 9.9300 393; MID 0.0281 0.2521 0.5890 12.7000 589; SMALL 0.0337 0.3467 0.6080 11.8400 981; ALL 0.0320 0.3156 0.6130 11.9800 1964
annual IC: 1999:+0.026 2000:+0.123 2001:+0.101 2002:+0.108 2003:-0.002 2004:+0.036 2005:+0.038 2006:+0.025 2007:-0.008 2008:+0.081 2009:-0.031 2010:+0.022 2011:+0.045 2012:+0.013 2013:+0.021 2014:+0.033 2015:+0.033 2016:+0.015 2017:-0.004 2018:+0.037 2019:-0.029 2020:-0.058 2021:+0.110

## RoE  (stage 2)  → **PASS**
rung 5 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq  | base IC 0.0320 Sharpe 0.967 ann ret 15.18% MaxDD -43.4
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.4128 | > 2.0 | PASS |
| paired_delta_ls_tstat | -1.2571 | >= -2.0 | PASS |
stats: ic_mean=0.0323  ic_tstat_nw=4.5007  icir=0.3146  ic_half1_mean=0.0462  ic_half2_mean=0.0183  ls_sharpe=0.9316  ls_ann_return_pct=14.8709  ls_ann_vol_pct=15.9633  ls_maxdd_pct=-43.6667  ls_hit_rate_pct=62.3188  turnover_d10_pct=44.3025  turnover_d1_pct=39.5813  coverage_pct=93.1349  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3893  resid_ic_mean=0.0045  resid_ic_tstat_nw=2.4128  spanning_alpha_ann_pct=-0.9971  spanning_alpha_tstat_nw=-0.3310  spanning_r2=0.3891  corr_to_composite=0.6238  paired_delta_ic_mean=0.0002  paired_delta_ic_tstat=1.4382  paired_delta_ls_mean=-0.0003  paired_delta_ls_tstat=-1.2571  delta_ls_sharpe=-0.0357  maxdd_worsening_pct=0.3035  ls_raw_sharpe=0.5790  ls_beta_mean=-0.6626  ls_beta_fullwindow=-0.7338  ls_sharpe_ex_top_years=0.5814  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9337  ls_sharpe_bull=1.0696
deciles D1..D10 avg %/mo: 0.344,0.482,0.825,0.983,0.976,1.130,1.153,1.190,1.282,1.304
hedge/regime (diagnostics): beta ex-ante -0.6626 full-window -0.7338  raw Sharpe 0.5790  Sharpe ex top years 0.5814 (2000,2001,2021)  bear/bull 0.9337/1.0696
ic decay: h1=0.0246  h2=0.0216  h3=0.0224  h6=0.0199  h12=0.0225
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0303 0.2202 0.3980 9.6600 393; MID 0.0284 0.2521 0.5610 12.2200 589; SMALL 0.0337 0.3436 0.5660 11.1900 981; ALL 0.0323 0.3146 0.5790 11.5300 1964
annual IC: 1999:+0.026 2000:+0.124 2001:+0.102 2002:+0.109 2003:-0.002 2004:+0.037 2005:+0.037 2006:+0.026 2007:-0.007 2008:+0.081 2009:-0.033 2010:+0.022 2011:+0.046 2012:+0.013 2013:+0.021 2014:+0.034 2015:+0.034 2016:+0.016 2017:-0.003 2018:+0.037 2019:-0.028 2020:-0.058 2021:+0.110
