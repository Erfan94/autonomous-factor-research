*Table 05_rungs. Every Stage 2 rung. Source: research/registry/<name>.yaml `stage2_run`, `stage2` (verbatim from the rung's block), `decided_by`; version from MODEL_MANIFEST.yaml `ratchet`. Acceptance-time, pre-refresh bytes (DATA 198b281de1a0).*

| run | rung | order rank | factor | family | base legs | resid IC | resid IC NW t (bar > 2.0) | resid months | guard t (bar >= -2.0) | paired dIC t (diag.) | verdict | decided by | version |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 012 | 1 | 1 | PctAcc | investment | 5 | 0.0098 | 4.673595 | 276 | 0.0874 | 2.81 | PASS | all bars | v1 |
| 012 | 2 | 2 | CBOperProf | profitability | 6 | 0.0104 | 3.020413 | 276 | 0.9458 | -0.01 | PASS | all bars | v2 |
| 012 | 3 | 3 | ShareIss5Y | external_financing | 7 | 0.0120 | 3.608529 | 223 | 2.8334 | 3.03 | PASS | all bars | v3 |
| 012 | 4 | 4 | cfp | value | 8 | 0.0104 | 2.974093 | 276 | 2.1869 | 3.10 | PASS | all bars | v4 |
| 012 | 5 | 5 | XFIN | external_financing | 9 | 0.0069 | 3.273460 | 276 | -0.6374 | -0.62 | PASS | all bars | v5 |
| 023 | 1 | 6 | GP | profitability | 10 | 0.0073 | 2.741182 | 276 | 0.4291 | -0.79 | PASS | all bars | v6 |
| 023 | 2 | 7 | ShareIss1Y | external_financing | 11 | 0.0044 | 1.879334 | 270 | 0.1724 | 1.76 | FAIL | resid_ic_tstat_nw |  |
| 023 | 3 | 8 | MaxRet | volatility | 11 | 0.0179 | 4.007615 | 276 | 1.7489 | 2.61 | PASS | all bars | v7 |
| 023 | 4 | 9 | roaq | profitability | 12 | 0.0119 | 3.727830 | 276 | 1.9515 | 2.66 | PASS | all bars | v8 |
| 023 | 5 | 10 | RoE | profitability | 13 | 0.0045 | 2.412780 | 276 | -1.2571 | 1.44 | PASS | all bars | v9 |
| 032 | 1 | 11 | OperProfRD | profitability | 14 | -0.0011 | -0.424080 | 276 | 0.9243 | -0.20 | FAIL | resid_ic_tstat_nw |  |
| 032 | 2 | 12 | IdioVol3F | volatility | 14 | 0.0065 | 2.030731 | 269 | 0.8872 | 0.81 | PASS | all bars | v10 |
| 032 | 3 | 13 | NetEquityFinance | external_financing | 15 | 0.0035 | 1.395688 | 276 | 0.4727 | 1.86 | FAIL | resid_ic_tstat_nw |  |
| 032 | 4 | 14 | CF | value | 15 | 0.0023 | 1.020438 | 276 | -0.7610 | 0.72 | FAIL | resid_ic_tstat_nw |  |
| 032 | 5 | 15 | STreversal | short_term_reversal | 15 | 0.0153 | 3.808913 | 276 | -0.5362 | 1.50 | PASS | all bars | v11 |
| 037 | 1 | 16 | zerotrade6M | liquidity | 16 | 0.0099 | 2.686514 | 276 | 1.7206 | 0.99 | PASS | all bars | v12 |
| 037 | 2 | 17 | VolumeTrend | liquidity | 17 | 0.0047 | 2.043637 | 228 | -0.0866 | -0.19 | PASS | all bars | v13 |
| 037 | 3 | 18 | zerotrade12M | liquidity | 18 | 0.0010 | 0.490011 | 275 | 0.1364 | 0.10 | FAIL | resid_ic_tstat_nw |  |
| 037 | 4 | 19 | RealizedVol | volatility | 18 | 0.0055 | 1.730033 | 276 | -0.6125 | 0.37 | FAIL | resid_ic_tstat_nw |  |
| 037 | 5 | 20 | TrendFactor | momentum | 18 | 0.0078 | 2.140869 | 228 | -0.0051 | 1.36 | PASS | all bars | v14 |
| 044 | 1 | 21 | BidAskSpreadFlip | liquidity | 19 | 0.0051 | 1.769160 | 276 | 0.4268 | 1.83 | FAIL | resid_ic_tstat_nw |  |
| 044 | 2 | 22 | IdioVolAHT | volatility | 19 | 0.0073 | 1.923537 | 272 | 0.0617 | 0.71 | FAIL | resid_ic_tstat_nw |  |
| 044 | 3 | 23 | zerotrade1M | liquidity | 19 | -0.0025 | -1.278064 | 276 | 0.1143 | -0.36 | FAIL | resid_ic_tstat_nw |  |
| 044 | 4 | 24 | NetPayoutYield | value | 19 | 0.0003 | 0.116485 | 264 | 0.0604 | -0.56 | FAIL | resid_ic_tstat_nw |  |
