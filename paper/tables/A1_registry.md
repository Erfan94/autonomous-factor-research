*Table A1_registry. The full registry, 112 rows (five seed legs carry no screen). Source: research/registry_index.yaml (derived from research/registry/*.yaml) and `stage2_run` from the rows. Acceptance-time, pre-refresh bytes.*

| name | status | batch | Stage 1 run | Stage 2 run | family | IC | IC NW t | raw LS %/yr | hedged LS %/yr | hedged Sharpe | coverage % | beta | Sharpe ex top-3 | resid t | guard t | decided by |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Accruals | rejected | stage1_b1 | 003 |  |  | 0.0048 | 1.84 | 2.92 | 2.49 | 0.329 | 76.7 | 0.04 | 0.107 |  |  | ic_tstat_nw |
| AM | rejected | stage1_b1 | 003 |  |  | 0.0098 | 1.26 | 4.72 | -3.17 | -0.149 | 99.6 | 0.34 | -0.449 |  |  | ic_tstat_nw |
| AnnouncementReturn | rejected | stage1_b1 | 003 |  |  | 0.0092 | 2.28 | 2.51 | 5.19 | 0.643 | 66.5 | -0.21 | 0.342 |  |  | ic_tstat_nw |
| Beta | rejected | stage1_b1 | 003 |  |  | -0.0091 | -0.97 | 1.12 | -10.31 | -0.608 | 85.4 | 1.11 | -0.974 |  |  | ic_tstat_nw |
| BetaFP | rejected | stage1_b1 | 003 |  |  | -0.0123 | -1.28 | 1.13 | -11.48 | -0.655 | 83.1 | 1.22 | -1.03 |  |  | ic_tstat_nw |
| BetaLiquidityPS | rejected | stage1_b1 | 003 |  |  | -0.0008 | -0.27 | -0.57 | -1.3 | -0.173 | 67.2 | 0.11 | -0.621 |  |  | ic_tstat_nw |
| BetaTailRisk | rejected | stage1_b1 | 003 |  |  | -0.0006 | -0.06 | 1.09 | -8.79 | -0.766 | 60.2 | 0.78 | -1.236 |  |  | ic_tstat_nw |
| BidAskSpread | rejected | stage1_b1 | 003 |  |  | -0.0205 | -2.77 | -0.94 | -8.63 | -0.482 | 99.1 | 0.97 | -0.889 |  |  | ic_tstat_nw |
| BidAskSpreadFlip | rejected | stage1_b9 | 011 | 044 | liquidity | 0.0206 | 2.76 | 1.07 | 8.72 | 0.485 | 99.1 | -0.98 | 0.295 | 1.77 | 0.43 | resid_ic_tstat_nw |
| BMdec | rejected | stage1_b1 | 003 |  |  | 0.0045 | 0.82 | 3.68 | 0.61 | 0.054 | 92.1 | -0.03 | -0.423 |  |  | ic_tstat_nw |
| BookLeverage | rejected | stage1_b1 | 003 |  |  | -0.0096 | -2.59 | -3.63 | -1.29 | -0.13 | 99.6 | -0.04 | -0.398 |  |  | ic_tstat_nw |
| BPEBM | rejected | stage1_b1 | 003 |  |  | -0.0092 | -2.06 | 0.39 | -0.38 | -0.036 | 75.6 | 0.23 | -0.448 |  |  | ic_tstat_nw |
| Cash | rejected | stage1_b2 | 004 |  |  | -0.0091 | -1.86 | -0.57 | -0.24 | -0.017 | 99.6 | 0.33 | -0.426 |  |  | ic_tstat_nw |
| CashProd | rejected | stage1_b2 | 004 |  |  | 0.003 | 0.47 | 3.74 | -1.75 | -0.127 | 99.2 | 0.26 | -0.483 |  |  | ic_tstat_nw |
| CBOperProf | accepted | stage1_b1 | 003 | 012 | profitability | 0.0209 | 3.74 | 7.24 | 11.24 | 0.901 | 73.4 | -0.57 | 0.638 | 3.02 | 0.95 | all bars |
| CF | rejected | stage1_b2 | 004 | 032 | value | 0.0201 | 3.03 | 3.32 | 2.75 | 0.179 | 96.1 | -0.29 | -0.169 | 1.02 | -0.76 | resid_ic_tstat_nw |
| cfp | accepted | stage1_b9 | 011 | 012 | value | 0.0246 | 3.65 | 9.45 | 7.47 | 0.51 | 95.7 | -0.13 | 0.246 | 2.97 | 2.19 | all bars |
| ChAssetTurnover | rejected | stage1_b2 | 004 |  |  | 0.0058 | 2.24 | 2.37 | 2.39 | 0.376 | 83.4 | -0.06 | 0.136 |  |  | ic_tstat_nw |
| ChEQ | rejected | stage1_b2 | 004 |  |  | 0.0057 | 1.4 | 7.66 | 5.17 | 0.455 | 91.2 | 0.02 | 0.092 |  |  | ic_tstat_nw |
| ChInv | rejected | stage1_b2 | 004 |  |  | 0.0052 | 1.51 | 5.14 | 5.65 | 0.649 | 60.3 | -0.1 | 0.359 |  |  | ic_tstat_nw |
| ChInvIA | rejected | stage1_b2 | 004 |  |  | 0.0009 | 0.36 | 4.04 | 3.69 | 0.564 | 87.2 | -0.11 | 0.331 |  |  | ic_tstat_nw |
| ChNNCOA | rejected | stage1_b2 | 004 |  |  | 0.0094 | 4.15 | 4.81 | 4.49 | 0.656 | 77.2 | -0.07 | 0.233 |  |  | ic_mean |
| ChNWC | rejected | stage1_b2 | 004 |  |  | 0.0042 | 2.04 | 1.15 | 1.35 | 0.221 | 77.0 | -0.02 | 0.035 |  |  | ic_tstat_nw |
| ChTax | rejected | stage1_b2 | 004 |  |  | 0.0048 | 1.42 | 0.09 | 1.02 | 0.128 | 87.1 | -0.03 | -0.161 |  |  | ic_tstat_nw |
| CompEquIss | rejected | stage1_b2 | 004 |  |  | 0.0119 | 2.44 | 3.62 | 5.25 | 0.614 | 65.1 | -0.06 | 0.375 |  |  | ic_tstat_nw |
| CompositeDebtIssuance | rejected | stage1_b2 | 004 |  |  | 0.0046 | 1.49 | 1.33 | 2.81 | 0.319 | 46.2 | -0.11 | -0.018 |  |  | ic_tstat_nw |
| CoskewACX | rejected | stage1_b3 | 005 |  |  | 0.0062 | 1.65 | 2.78 | 1.25 | 0.11 | 91.1 | 0.22 | -0.118 |  |  | ic_tstat_nw |
| Coskewness | rejected | stage1_b3 | 005 |  |  | 0.0068 | 1.65 | 1.61 | -0.52 | -0.045 | 91.1 | 0.33 | -0.229 |  |  | ic_tstat_nw |
| DelCOA | rejected | stage1_b3 | 005 |  |  | 0.0009 | 0.26 | 4.97 | 4.91 | 0.583 | 77.3 | -0.07 | 0.195 |  |  | ic_tstat_nw |
| DelCOL | rejected | stage1_b3 | 005 |  |  | -0.0035 | -0.92 | 0.81 | 0.36 | 0.04 | 77.1 | -0.06 | -0.287 |  |  | ic_tstat_nw |
| DelEqu | rejected | stage1_b3 | 005 |  |  | 0.0052 | 1.25 | 6.06 | 3.53 | 0.333 | 95.2 | 0.0 | 0.008 |  |  | ic_tstat_nw |
| DelFINL | rejected | stage1_b3 | 005 |  |  | 0.0039 | 1.36 | 2.26 | 3.53 | 0.451 | 69.6 | -0.18 | 0.112 |  |  | ic_tstat_nw |
| DelNetFin | rejected | stage1_b3 | 005 |  |  | 0.0025 | 1.08 | 1.07 | 2.22 | 0.317 | 77.2 | -0.0 | -0.237 |  |  | ic_tstat_nw |
| dNoa | rejected | stage1_b9 | 011 |  |  | 0.0077 | 2.19 | 7.74 | 6.62 | 0.817 | 95.2 | -0.07 | 0.395 |  |  | ic_tstat_nw |
| DolVol | rejected | stage1_b3 | 005 |  |  | -0.0008 | -0.18 | 3.69 | 1.65 | 0.165 | 99.5 | -0.01 | -0.119 |  |  | ic_tstat_nw |
| EarningsConsistency | rejected | stage1_b3 | 005 |  |  | 0.009 | 2.6 | -0.13 | 2.92 | 0.338 | 43.3 | -0.18 | 0.183 |  |  | ic_mean |
| EarningsSurprise | rejected | stage1_b3 | 005 |  |  | 0.0048 | 1.63 | 1.33 | 2.32 | 0.324 | 86.2 | -0.09 | 0.051 |  |  | ic_tstat_nw |
| EBM | rejected | stage1_b3 | 005 |  |  | 0.0018 | 0.42 | 3.22 | 0.3 | 0.032 | 75.6 | 0.24 | -0.331 |  |  | ic_tstat_nw |
| EntMult | rejected | stage1_b4 | 006 |  |  | 0.0134 | 1.96 | 5.55 | 2.85 | 0.194 | 65.9 | -0.08 | -0.127 |  |  | ic_tstat_nw |
| EP | rejected | stage1_b3 | 005 |  |  | 0.0055 | 0.96 | 3.53 | 1.76 | 0.17 | 75.1 | -0.05 | -0.12 |  |  | ic_tstat_nw |
| EquityDuration | rejected | stage1_b4 | 006 |  |  | 0.0104 | 1.86 | 2.33 | 2.98 | 0.253 | 94.7 | -0.3 | -0.061 |  |  | ic_tstat_nw |
| GP | accepted | stage1_b4 | 006 | 023 | profitability | 0.0155 | 3.52 | 8.64 | 11.34 | 1.091 | 74.4 | -0.45 | 0.921 | 2.74 | 0.43 | all bars |
| grcapx | rejected | stage1_b9 | 011 |  |  | 0.0041 | 1.37 | 4.02 | 3.4 | 0.488 | 81.0 | -0.08 | 0.263 |  |  | ic_tstat_nw |
| grcapx3y | rejected | stage1_b9 | 011 |  |  | 0.0028 | 0.89 | 3.97 | 3.42 | 0.446 | 72.3 | -0.04 | 0.233 |  |  | ic_tstat_nw |
| GrLTNOA | rejected | stage1_b4 | 006 |  |  | -0.0059 | -2.75 | -0.08 | -0.76 | -0.114 | 76.8 | 0.04 | -0.491 |  |  | ic_tstat_nw |
| GrSaleToGrInv | rejected | stage1_b4 | 006 |  |  | 0.0035 | 1.58 | 1.62 | 1.59 | 0.217 | 57.1 | -0.01 | -0.167 |  |  | ic_tstat_nw |
| GrSaleToGrOverhead | rejected | stage1_b4 | 006 |  |  | -0.002 | -0.75 | -3.04 | -2.73 | -0.394 | 85.1 | -0.04 | -0.549 |  |  | ic_tstat_nw |
| Herf | rejected | stage1_b4 | 006 |  |  | -0.0028 | -1.15 | 0.03 | -0.79 | -0.106 | 91.5 | 0.04 | -0.326 |  |  | ic_tstat_nw |
| HerfAsset | rejected | stage1_b4 | 006 |  |  | -0.0049 | -2.0 | -0.59 | -1.45 | -0.182 | 91.6 | 0.06 | -0.432 |  |  | ic_tstat_nw |
| HerfBE | rejected | stage1_b4 | 006 |  |  | -0.003 | -1.21 | 0.28 | -0.44 | -0.061 | 91.6 | -0.03 | -0.33 |  |  | ic_tstat_nw |
| High52 | rejected | stage1_b4 | 006 |  |  | 0.0065 | 0.77 | -0.13 | 9.38 | 0.448 | 96.1 | -1.01 | 0.255 |  |  | ic_tstat_nw |
| IdioVol3F | accepted | stage1_b4 | 006 | 032 | volatility | 0.0229 | 3.15 | 3.28 | 10.1 | 0.536 | 96.7 | -0.98 | 0.374 | 2.03 | 0.89 | all bars |
| IdioVolAHT | rejected | stage1_b4 | 006 | 044 | volatility | 0.0238 | 2.63 | 3.89 | 11.68 | 0.545 | 96.8 | -1.07 | 0.389 | 1.92 | 0.06 | resid_ic_tstat_nw |
| Illiquidity | rejected | stage1_b5 | 007 |  |  | -0.0064 | -1.19 | 4.31 | 1.13 | 0.078 | 96.4 | 0.29 | -0.137 |  |  | ic_tstat_nw |
| IntanBM | rejected | stage1_b5 | 007 |  |  | -0.0003 | -0.04 | 4.34 | -3.54 | -0.228 | 61.1 | 0.56 | -0.837 |  |  | ic_tstat_nw |
| IntanCFP | rejected | stage1_b5 | 007 |  |  | -0.0033 | -0.4 | 4.67 | -4.35 | -0.263 | 62.9 | 0.65 | -0.798 |  |  | ic_tstat_nw |
| IntanEP | rejected | stage1_b5 | 007 |  |  | -0.0045 | -0.55 | 4.58 | -4.31 | -0.258 | 62.9 | 0.64 | -0.798 |  |  | ic_tstat_nw |
| IntanSP | rejected | stage1_b5 | 007 |  |  | -0.0052 | -0.62 | 5.2 | -3.97 | -0.233 | 62.9 | 0.67 | -0.772 |  |  | ic_tstat_nw |
| IntMom | rejected | stage1_b5 | 007 |  |  | 0.0031 | 0.5 | -1.12 | 2.24 | 0.151 | 95.4 | -0.18 | -0.117 |  |  | ic_tstat_nw |
| Investment | baseline | BASELINE | 001 |  | investment |  |  |  |  |  |  |  |  |  |  |  |
| InvestmentTWX | rejected | stage1_b5 | 007 |  |  | 0.0003 | 0.15 | 2.68 | 1.98 | 0.342 | 78.7 | 0.03 | 0.097 |  |  | ic_tstat_nw |
| InvGrowth | rejected | stage1_b5 | 007 |  |  | 0.0055 | 1.56 | 3.5 | 3.82 | 0.386 | 51.7 | -0.14 | 0.009 |  |  | ic_tstat_nw |
| Leverage | rejected | stage1_b5 | 007 |  |  | 0.0125 | 1.71 | 7.09 | -0.5 | -0.025 | 99.6 | 0.3 | -0.342 |  |  | ic_tstat_nw |
| LRreversal | rejected | stage1_b5 | 007 |  |  | -0.008 | -1.29 | 2.84 | -0.97 | -0.068 | 78.9 | 0.09 | -0.381 |  |  | ic_tstat_nw |
| MaxRet | accepted | stage1_b5 | 007 | 023 | volatility | 0.0233 | 3.42 | 4.17 | 10.57 | 0.611 | 99.8 | -0.86 | 0.544 | 4.01 | 1.75 | all bars |
| MeanRankRevGrowth | rejected | stage1_b6 | 008 |  |  | -0.0005 | -0.12 | 2.23 | 0.76 | 0.093 | 46.6 | 0.1 | -0.225 |  |  | ic_tstat_nw |
| Mom12mOffSeason | rejected | stage1_b6 | 008 |  |  | 0.0084 | 1.24 | 7.08 | 13.34 | 0.583 | 96.4 | -0.35 | 0.418 |  |  | ic_tstat_nw |
| Mom6m | rejected | stage1_b6 | 008 |  |  | 0.0077 | 1.24 | 6.47 | 12.93 | 0.616 | 98.2 | -0.47 | 0.449 |  |  | ic_tstat_nw |
| Momentum | baseline | BASELINE | 001 |  | momentum |  |  |  |  |  |  |  |  |  |  |  |
| MomOffSeason | rejected | stage1_b6 | 008 |  |  | -0.0052 | -0.97 | 2.23 | 1.19 | 0.113 | 66.6 | 0.05 | -0.208 |  |  | ic_tstat_nw |
| MomOffSeason06YrPlus | rejected | stage1_b6 | 008 |  |  | 0.0065 | 1.76 | 1.45 | 1.64 | 0.268 | 40.6 | 0.01 | -0.063 |  |  | ic_tstat_nw |
| MomSeason | rejected | stage1_b6 | 008 |  |  | 0.002 | 0.58 | -0.27 | 0.17 | 0.022 | 66.1 | 0.0 | -0.221 |  |  | ic_tstat_nw |
| MomSeason06YrPlus | rejected | stage1_b6 | 008 |  |  | 0.0069 | 1.9 | 0.21 | 0.12 | 0.018 | 40.3 | -0.0 | -0.287 |  |  | ic_tstat_nw |
| MomSeasonShort | rejected | stage1_b6 | 008 |  |  | 0.0013 | 0.28 | -0.44 | 1.02 | 0.096 | 96.1 | 0.02 | -0.345 |  |  | ic_tstat_nw |
| MRreversal | rejected | stage1_b5 | 007 |  |  | -0.0043 | -0.96 | 3.69 | 0.62 | 0.051 | 91.0 | 0.09 | -0.2 |  |  | ic_tstat_nw |
| NetDebtFinance | rejected | stage1_b6 | 008 |  |  | 0.0034 | 1.38 | 2.25 | 2.95 | 0.455 | 88.1 | -0.16 | 0.163 |  |  | ic_tstat_nw |
| NetEquityFinance | rejected | stage1_b6 | 008 | 032 | external_financing | 0.0166 | 3.03 | 4.54 | 7.02 | 0.601 | 93.9 | -0.52 | 0.434 | 1.4 | 0.47 | resid_ic_tstat_nw |
| NetPayoutYield | rejected | stage1_b6 | 008 | 044 | value | 0.0145 | 2.6 | 4.92 | 6.87 | 0.542 | 65.5 | -0.41 | 0.302 | 0.12 | 0.06 | resid_ic_tstat_nw |
| NOA | rejected | stage1_b6 | 008 |  |  | 0.0016 | 0.62 | 8.64 | 7.92 | 0.907 | 77.3 | -0.02 | 0.605 |  |  | ic_tstat_nw |
| OperProfRD | rejected | stage1_b7 | 009 | 032 | profitability | 0.0192 | 3.18 | 6.44 | 10.94 | 0.733 | 70.7 | -0.6 | 0.452 | -0.42 | 0.92 | resid_ic_tstat_nw |
| OPLeverage | rejected | stage1_b7 | 009 |  |  | 0.0087 | 2.89 | 4.09 | 3.46 | 0.429 | 85.4 | -0.1 | 0.153 |  |  | ic_mean |
| OrgCap | rejected | stage1_b7 | 009 |  |  | 0.0054 | 1.7 | 4.21 | 4.36 | 0.401 | 50.4 | 0.08 | 0.194 |  |  | ic_tstat_nw |
| PctAcc | accepted | stage1_b7 | 009 | 012 | investment | 0.0112 | 4.03 | 4.74 | 4.15 | 0.672 | 95.6 | -0.04 | 0.462 | 4.67 | 0.09 | all bars |
| PctTotAcc | rejected | stage1_b7 | 009 |  |  | 0.0022 | 0.91 | 2.48 | 2.16 | 0.377 | 95.6 | -0.08 | 0.187 |  |  | ic_tstat_nw |
| Price | rejected | stage1_b7 | 009 |  |  | -0.01 | -1.41 | 2.98 | -5.89 | -0.315 | 100.0 | 0.77 | -0.766 |  |  | ic_tstat_nw |
| PriceDelayRsq | rejected | stage1_b7 | 009 |  |  | -0.007 | -2.12 | -1.09 | 0.01 | 0.001 | 87.8 | -0.17 | -0.232 |  |  | ic_tstat_nw |
| PriceDelaySlope | rejected | stage1_b7 | 009 |  |  | -0.0055 | -1.69 | -0.6 | -2.93 | -0.42 | 87.8 | 0.23 | -0.816 |  |  | ic_tstat_nw |
| PriceDelayTstat | rejected | stage1_b7 | 009 |  |  | -0.0055 | -1.68 | -0.59 | -2.93 | -0.419 | 87.8 | 0.23 | -0.809 |  |  | ic_tstat_nw |
| Profitability | baseline | BASELINE | 001 |  | profitability |  |  |  |  |  |  |  |  |  |  |  |
| RealizedVol | rejected | stage1_b7 | 009 | 037 | volatility | 0.0234 | 2.81 | 3.39 | 12.13 | 0.607 | 99.8 | -1.16 | 0.479 | 1.73 | -0.61 | resid_ic_tstat_nw |
| ResidualMomentum | rejected | stage1_b7 | 009 |  |  | 0.0035 | 0.72 | 1.76 | 4.92 | 0.466 | 67.4 | -0.24 | 0.187 |  |  | ic_tstat_nw |
| ReturnSkew | rejected | stage1_b7 | 009 |  |  | 0.005 | 2.22 | 0.4 | 0.45 | 0.066 | 99.8 | -0.03 | -0.269 |  |  | ic_tstat_nw |
| ReturnSkew3F | rejected | stage1_b8 | 010 |  |  | 0.0007 | 0.35 | -1.34 | -1.93 | -0.307 | 96.7 | 0.02 | -0.679 |  |  | ic_tstat_nw |
| RevenueSurprise | rejected | stage1_b8 | 010 |  |  | 0.0094 | 2.78 | 1.82 | 2.59 | 0.347 | 86.6 | -0.05 | 0.093 |  |  | ic_mean |
| roaq | accepted | stage1_b9 | 011 | 023 | profitability | 0.0208 | 3.37 | 5.28 | 9.95 | 0.705 | 96.3 | -0.58 | 0.386 | 3.73 | 1.95 | all bars |
| RoE | accepted | stage1_b8 | 010 | 023 | profitability | 0.0192 | 3.34 | 2.95 | 7.38 | 0.532 | 93.1 | -0.59 | 0.372 | 2.41 | -1.26 | all bars |
| ShareIss1Y | rejected | stage1_b8 | 010 | 023 | external_financing | 0.0165 | 3.52 | 7.12 | 9.06 | 0.909 | 90.5 | -0.38 | 0.742 | 1.88 | 0.17 | resid_ic_tstat_nw |
| ShareIss5Y | accepted | stage1_b8 | 010 | 012 | external_financing | 0.0158 | 3.67 | 4.88 | 8.23 | 1.085 | 62.6 | -0.24 | 0.749 | 3.61 | 2.83 | all bars |
| Size | baseline | BASELINE | 001 |  | size |  |  |  |  |  |  |  |  |  |  |  |
| SP | rejected | stage1_b8 | 010 |  |  | 0.0182 | 2.5 | 9.21 | 2.79 | 0.145 | 96.1 | 0.18 | -0.201 |  |  | ic_tstat_nw |
| STreversal | accepted | stage1_b8 | 010 | 032 | short_term_reversal | 0.0145 | 2.96 | 3.37 | -0.48 | -0.029 | 99.8 | 0.44 | -0.369 | 3.81 | -0.54 | all bars |
| TotalAccruals | rejected | stage1_b8 | 010 |  |  | -0.0 | -0.01 | 1.47 | -0.7 | -0.093 | 94.6 | 0.12 | -0.361 |  |  | ic_tstat_nw |
| TrendFactor | accepted | stage1_b8 | 010 | 037 | momentum | 0.0171 | 2.79 | 10.12 | 8.94 | 0.523 | 68.7 | 0.05 | 0.276 | 2.14 | -0.01 | all bars |
| Value | baseline | BASELINE | 001 |  | value |  |  |  |  |  |  |  |  |  |  |  |
| VarCF | rejected | stage1_b8 | 010 |  |  | 0.0064 | 0.76 | -3.97 | 5.59 | 0.406 | 60.7 | -0.79 | 0.174 |  |  | ic_tstat_nw |
| VolMkt | rejected | stage1_b8 | 010 |  |  | 0.0161 | 2.25 | 2.38 | 9.55 | 0.551 | 97.1 | -0.94 | 0.32 |  |  | ic_tstat_nw |
| VolSD | rejected | stage1_b8 | 010 |  |  | 0.0112 | 2.36 | 1.95 | 6.05 | 0.534 | 79.8 | -0.47 | 0.398 |  |  | ic_tstat_nw |
| VolumeTrend | accepted | stage1_b9 | 011 | 037 | liquidity | 0.0114 | 2.87 | 2.4 | 5.05 | 0.661 | 66.3 | -0.23 | 0.331 | 2.04 | -0.09 | all bars |
| XFIN | accepted | stage1_b9 | 011 | 012 | external_financing | 0.017 | 3.57 | 6.57 | 8.61 | 0.734 | 95.6 | -0.47 | 0.484 | 3.27 | -0.64 | all bars |
| zerotrade12M | rejected | stage1_b9 | 011 | 037 | liquidity | 0.018 | 2.83 | 3.69 | 8.97 | 0.692 | 94.7 | -0.7 | 0.449 | 0.49 | 0.14 | resid_ic_tstat_nw |
| zerotrade1M | rejected | stage1_b9 | 011 | 044 | liquidity | 0.0155 | 2.63 | 2.56 | 6.89 | 0.441 | 99.4 | -0.73 | 0.281 | -1.28 | 0.11 | resid_ic_tstat_nw |
| zerotrade6M | accepted | stage1_b9 | 011 | 037 | liquidity | 0.0185 | 2.93 | 4.19 | 8.92 | 0.602 | 97.6 | -0.73 | 0.427 | 2.69 | 1.72 | all bars |
