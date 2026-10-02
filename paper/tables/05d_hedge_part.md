*Table 05d_hedge_part. The guard's delta split into raw spread and hedge term, as recorded from ladder 2 on. Source: events `factor_evaluated` (stage 2) field raw_vs_hedged_dls_pp; ladder 1 rows predate the field.*

| run | factor | raw dLS pp/yr | hedge part pp/yr | hedged dLS pp/yr | guard t | verdict |
|---|---|---|---|---|---|---|
| 023 | GP | +0.35 | -0.20 | +0.16 | 0.43 | PASS |
| 023 | ShareIss1Y | +0.04 | +0.03 | +0.07 | 0.17 | FAIL |
| 023 | MaxRet | -0.59 | +2.82 | +2.23 | 1.75 | PASS |
| 023 | roaq | +0.72 | +0.51 | +1.23 | 1.95 | PASS |
| 023 | RoE | -0.45 | +0.14 | -0.31 | -1.26 | PASS |
| 032 | OperProfRD | +0.19 | -0.02 | +0.17 | 0.92 | FAIL |
| 032 | IdioVol3F | +0.41 | -0.03 | +0.38 | 0.89 | PASS |
| 032 | NetEquityFinance | +0.01 | +0.18 | +0.19 | 0.47 | FAIL |
| 032 | CF | -0.67 | +0.28 | -0.40 | -0.76 | FAIL |
| 032 | STreversal | +1.09 | -1.73 | -0.64 | -0.54 | PASS |
| 037 | zerotrade6M | +0.64 | +0.90 | +1.55 | 1.72 | PASS |
| 037 | VolumeTrend | +0.18 | -0.21 | -0.03 | -0.09 | PASS |
| 037 | zerotrade12M | -0.06 | +0.11 | +0.04 | 0.14 | FAIL |
| 037 | RealizedVol | -0.38 | +0.25 | -0.13 | -0.61 | FAIL |
| 037 | TrendFactor | +0.77 | -0.77 | +0.00 | -0.01 | PASS |
| 044 | BidAskSpreadFlip | -0.20 | +0.40 | +0.20 | 0.43 | FAIL |
| 044 | IdioVolAHT | +0.02 | +0.00 | +0.02 | 0.06 | FAIL |
| 044 | zerotrade1M | -0.03 | +0.08 | +0.05 | 0.11 | FAIL |
| 044 | NetPayoutYield | -0.43 | +0.45 | +0.03 | 0.06 | FAIL |
