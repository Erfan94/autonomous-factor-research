# RUN 037 BATCH stage 2

stamps: HARNESS 73a95d352942 CONFIG 0d88328d5b10 COMPOSITE 335b06e3d608 DATA 198b281de1a0
window: 1999-01-01 .. 2021-12-31  holdout_included: False
composite: v11: Size, Value, Profitability, Investment, Momentum, PctAcc, CBOperProf, ShareIss5Y, cfp, XFIN, GP, MaxRet, roaq, RoE, IdioVol3F, STreversal

## zerotrade6M  (stage 2)  → **PASS**
rung 1 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal  | base IC 0.0355 Sharpe 0.942 ann ret 14.61% MaxDD -39.5
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.6865 | > 2.0 | PASS |
| paired_delta_ls_tstat | 1.7206 | >= -2.0 | PASS |
stats: ic_mean=0.0373  ic_tstat_nw=5.1535  icir=0.3550  ic_half1_mean=0.0467  ic_half2_mean=0.0279  ls_sharpe=0.9846  ls_ann_return_pct=16.1589  ls_ann_vol_pct=16.4119  ls_maxdd_pct=-41.1079  ls_hit_rate_pct=64.8551  turnover_d10_pct=56.7968  turnover_d1_pct=52.6024  coverage_pct=97.5928  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=0.0099  resid_ic_tstat_nw=2.6865  spanning_alpha_ann_pct=2.1622  spanning_alpha_tstat_nw=0.7644  spanning_r2=0.2342  corr_to_composite=0.4839  paired_delta_ic_mean=0.0018  paired_delta_ic_tstat=0.9942  paired_delta_ls_mean=0.0013  paired_delta_ls_tstat=1.7206  delta_ls_sharpe=0.0423  maxdd_worsening_pct=1.5788  ls_raw_sharpe=0.7084  ls_beta_mean=-0.5991  ls_beta_fullwindow=-0.6348  ls_sharpe_ex_top_years=0.6455  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9250  ls_sharpe_bull=1.2290
deciles D1..D10 avg %/mo: 0.312,0.629,0.753,0.829,1.000,1.049,1.138,1.188,1.320,1.451
hedge/regime (diagnostics): beta ex-ante -0.5991 full-window -0.6348  raw Sharpe 0.7084  Sharpe ex top years 0.6455 (2000,2001,2021)  bear/bull 0.9250/1.2290
ic decay: h1=0.0265  h2=0.0215  h3=0.0238  h6=0.0210  h12=0.0249
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0318 0.2077 0.2560 6.6000 393; MID 0.0332 0.2900 0.6020 12.5600 589; SMALL 0.0396 0.4036 0.7800 14.8200 981; ALL 0.0373 0.3550 0.7080 13.6700 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.010 2004:+0.040 2005:+0.027 2006:+0.039 2007:-0.011 2008:+0.086 2009:-0.029 2010:+0.025 2011:+0.058 2012:+0.019 2013:+0.022 2014:+0.044 2015:+0.051 2016:+0.018 2017:+0.008 2018:+0.047 2019:-0.000 2020:-0.054 2021:+0.111

## VolumeTrend  (stage 2)  → **PASS**
rung 2 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M  | base IC 0.0373 Sharpe 0.985 ann ret 16.16% MaxDD -41.1
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.0436 | > 2.0 | PASS |
| paired_delta_ls_tstat | -0.0866 | >= -2.0 | PASS |
stats: ic_mean=0.0372  ic_tstat_nw=5.2391  icir=0.3624  ic_half1_mean=0.0467  ic_half2_mean=0.0277  ls_sharpe=0.9786  ls_ann_return_pct=16.1259  ls_ann_vol_pct=16.4788  ls_maxdd_pct=-41.6031  ls_hit_rate_pct=64.4928  turnover_d10_pct=56.5533  turnover_d1_pct=53.1515  coverage_pct=66.2952  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=0.0047  resid_ic_tstat_nw=2.0436  spanning_alpha_ann_pct=1.1555  spanning_alpha_tstat_nw=0.6746  spanning_r2=0.3180  corr_to_composite=0.5640  paired_delta_ic_mean=-0.0001  paired_delta_ic_tstat=-0.1906  paired_delta_ls_mean=-0.0000  paired_delta_ls_tstat=-0.0866  delta_ls_sharpe=-0.0060  maxdd_worsening_pct=0.4951  ls_raw_sharpe=0.7188  ls_beta_mean=-0.5891  ls_beta_fullwindow=-0.6194  ls_sharpe_ex_top_years=0.6349  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9616  ls_sharpe_bull=1.2044
deciles D1..D10 avg %/mo: 0.268,0.621,0.779,0.846,1.000,1.088,1.117,1.190,1.338,1.422
hedge/regime (diagnostics): beta ex-ante -0.5891 full-window -0.6194  raw Sharpe 0.7188  Sharpe ex top years 0.6349 (2000,2001,2021)  bear/bull 0.9616/1.2044
ic decay: h1=0.0263  h2=0.0214  h3=0.0236  h6=0.0209  h12=0.0250
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0323 0.2212 0.2510 6.4500 393; MID 0.0336 0.3013 0.6110 12.8000 589; SMALL 0.0388 0.4049 0.7870 14.6800 981; ALL 0.0372 0.3624 0.7190 13.8500 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.009 2004:+0.039 2005:+0.031 2006:+0.038 2007:-0.015 2008:+0.082 2009:-0.025 2010:+0.029 2011:+0.056 2012:+0.021 2013:+0.021 2014:+0.045 2015:+0.046 2016:+0.020 2017:+0.009 2018:+0.040 2019:+0.001 2020:-0.053 2021:+0.113

## zerotrade12M  (stage 2)  → **FAIL**
rung 3 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend  | base IC 0.0372 Sharpe 0.979 ann ret 16.13% MaxDD -41.6
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 0.4900 | > 2.0 | FAIL |
| paired_delta_ls_tstat | 0.1364 | >= -2.0 | PASS |
stats: ic_mean=0.0372  ic_tstat_nw=5.2119  icir=0.3604  ic_half1_mean=0.0467  ic_half2_mean=0.0278  ls_sharpe=0.9855  ls_ann_return_pct=16.1682  ls_ann_vol_pct=16.4065  ls_maxdd_pct=-40.8331  ls_hit_rate_pct=63.7681  turnover_d10_pct=56.7628  turnover_d1_pct=53.0538  coverage_pct=94.6675  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3856  resid_ic_mean=0.0010  resid_ic_tstat_nw=0.4900  spanning_alpha_ann_pct=1.9728  spanning_alpha_tstat_nw=0.7932  spanning_r2=0.2820  corr_to_composite=0.5310  paired_delta_ic_mean=0.0000  paired_delta_ic_tstat=0.1042  paired_delta_ls_mean=0.0000  paired_delta_ls_tstat=0.1364  delta_ls_sharpe=0.0069  maxdd_worsening_pct=-0.7699  ls_raw_sharpe=0.7160  ls_beta_mean=-0.5924  ls_beta_fullwindow=-0.6251  ls_sharpe_ex_top_years=0.6612  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9659  ls_sharpe_bull=1.2135
deciles D1..D10 avg %/mo: 0.281,0.606,0.774,0.870,0.974,1.097,1.108,1.178,1.351,1.430
hedge/regime (diagnostics): beta ex-ante -0.5924 full-window -0.6251  raw Sharpe 0.7160  Sharpe ex top years 0.6612 (2000,2001,2021)  bear/bull 0.9659/1.2135
ic decay: h1=0.0262  h2=0.0212  h3=0.0235  h6=0.0208  h12=0.0250
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0320 0.2164 0.2670 6.8300 393; MID 0.0334 0.2979 0.5890 12.2700 589; SMALL 0.0392 0.4046 0.7980 14.8700 981; ALL 0.0372 0.3604 0.7160 13.7800 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.010 2004:+0.039 2005:+0.030 2006:+0.038 2007:-0.014 2008:+0.084 2009:-0.026 2010:+0.027 2011:+0.057 2012:+0.021 2013:+0.022 2014:+0.045 2015:+0.048 2016:+0.020 2017:+0.009 2018:+0.042 2019:+0.000 2020:-0.053 2021:+0.111

## RealizedVol  (stage 2)  → **FAIL**
rung 4 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend  | base IC 0.0372 Sharpe 0.979 ann ret 16.13% MaxDD -41.6
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 1.7300 | > 2.0 | FAIL |
| paired_delta_ls_tstat | -0.6125 | >= -2.0 | PASS |
stats: ic_mean=0.0373  ic_tstat_nw=5.1853  icir=0.3568  ic_half1_mean=0.0468  ic_half2_mean=0.0278  ls_sharpe=0.9560  ls_ann_return_pct=15.9915  ls_ann_vol_pct=16.7279  ls_maxdd_pct=-41.5236  ls_hit_rate_pct=63.7681  turnover_d10_pct=55.1511  turnover_d1_pct=51.9137  coverage_pct=99.8007  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=0.0055  resid_ic_tstat_nw=1.7300  spanning_alpha_ann_pct=-1.8382  spanning_alpha_tstat_nw=-0.5004  spanning_r2=0.5102  corr_to_composite=0.7143  paired_delta_ic_mean=0.0001  paired_delta_ic_tstat=0.3732  paired_delta_ls_mean=-0.0001  paired_delta_ls_tstat=-0.6125  delta_ls_sharpe=-0.0226  maxdd_worsening_pct=-0.0795  ls_raw_sharpe=0.6858  ls_beta_mean=-0.6117  ls_beta_fullwindow=-0.6449  ls_sharpe_ex_top_years=0.6193  ls_top_years=2000,2001,2021  ls_sharpe_bear=0.9459  ls_sharpe_bull=1.1906
deciles D1..D10 avg %/mo: 0.298,0.606,0.783,0.859,0.965,1.098,1.126,1.189,1.324,1.420
hedge/regime (diagnostics): beta ex-ante -0.6117 full-window -0.6449  raw Sharpe 0.6858  Sharpe ex top years 0.6193 (2000,2001,2021)  bear/bull 0.9459/1.1906
ic decay: h1=0.0266  h2=0.0215  h3=0.0238  h6=0.0210  h12=0.0250
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0325 0.2184 0.2610 6.8100 393; MID 0.0339 0.2967 0.6070 12.8500 589; SMALL 0.0389 0.4000 0.7880 14.9200 981; ALL 0.0373 0.3568 0.6860 13.4700 1964
annual IC: 1999:+0.017 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.010 2004:+0.039 2005:+0.031 2006:+0.038 2007:-0.013 2008:+0.082 2009:-0.026 2010:+0.028 2011:+0.059 2012:+0.020 2013:+0.020 2014:+0.046 2015:+0.047 2016:+0.020 2017:+0.011 2018:+0.042 2019:-0.001 2020:-0.054 2021:+0.113

## TrendFactor  (stage 2)  → **PASS**
rung 5 vs Size,Value,Profitability,Investment,Momentum,PctAcc,CBOperProf,ShareIss5Y,cfp,XFIN,GP,MaxRet,roaq,RoE,IdioVol3F,STreversal,zerotrade6M,VolumeTrend  | base IC 0.0372 Sharpe 0.979 ann ret 16.13% MaxDD -41.6
| bar | value | bound | result |
|---|---|---|---|
| resid_ic_tstat_nw | 2.1409 | > 2.0 | PASS |
| paired_delta_ls_tstat | -0.0051 | >= -2.0 | PASS |
stats: ic_mean=0.0389  ic_tstat_nw=5.6831  icir=0.3870  ic_half1_mean=0.0498  ic_half2_mean=0.0281  ls_sharpe=0.9826  ls_ann_return_pct=16.1222  ls_ann_vol_pct=16.4084  ls_maxdd_pct=-43.2143  ls_hit_rate_pct=63.7681  turnover_d10_pct=58.1350  turnover_d1_pct=54.4051  coverage_pct=68.7213  avg_names_per_decile=196.5  n_months=276  ls_n_months=276  delisting_adjusted_pct=0.4367  leg_coverage_pct_full=45.3876  resid_ic_mean=0.0078  resid_ic_tstat_nw=2.1409  spanning_alpha_ann_pct=10.4448  spanning_alpha_tstat_nw=1.7709  spanning_r2=0.0098  corr_to_composite=-0.0988  paired_delta_ic_mean=0.0017  paired_delta_ic_tstat=1.3649  paired_delta_ls_mean=-0.0000  paired_delta_ls_tstat=-0.0051  delta_ls_sharpe=0.0040  maxdd_worsening_pct=1.6113  ls_raw_sharpe=0.7734  ls_beta_mean=-0.5437  ls_beta_fullwindow=-0.5596  ls_sharpe_ex_top_years=0.6498  ls_top_years=2000,2001,2021  ls_sharpe_bear=1.2192  ls_sharpe_bull=1.1146
deciles D1..D10 avg %/mo: 0.275,0.539,0.757,0.802,1.006,1.061,1.132,1.249,1.355,1.493
hedge/regime (diagnostics): beta ex-ante -0.5437 full-window -0.5596  raw Sharpe 0.7734  Sharpe ex top years 0.6498 (2000,2001,2021)  bear/bull 1.2192/1.1146
ic decay: h1=0.0269  h2=0.0226  h3=0.0247  h6=0.0197  h12=0.0234
tiers (tier, IC, ICIR, Sharpe, ann%, avgN): MEGA 0.0335 0.2307 0.2840 7.3000 393; MID 0.0348 0.3193 0.6370 13.1600 589; SMALL 0.0412 0.4404 0.9050 16.2100 981; ALL 0.0389 0.3870 0.7730 14.6200 1964
annual IC: 1999:+0.018 2000:+0.122 2001:+0.109 2002:+0.118 2003:-0.000 2004:+0.042 2005:+0.027 2006:+0.040 2007:-0.016 2008:+0.081 2009:+0.003 2010:+0.032 2011:+0.058 2012:+0.019 2013:+0.019 2014:+0.040 2015:+0.040 2016:+0.031 2017:+0.001 2018:+0.039 2019:+0.009 2020:-0.049 2021:+0.114
