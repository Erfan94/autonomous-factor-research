*Table 05e_versions. Version history v0-v14, acceptance-time, pre-refresh bytes (DATA 198b281de1a0). Source: MODEL_MANIFEST.yaml `versions[*]` (`legs`, `families`, `ratchet.bars`, `baseline`, `construction.run`, `stamps`). Gross; LS hedged unless labelled raw.*

| version | leg added | family | legs | families | ratchet run/rung | resid t | guard t | baseline run | IC | IC NW t | hedged Sharpe | hedged ann % | hedged MaxDD % | beta (full window) | raw Sharpe | Sharpe ex top-3 yrs | D10 turnover % | Stage 3 run | COMPOSITE_SHA |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| v0 | (seed: Size, Value, Profitability, Investment, Momentum) |  | 5 | 5 |  |  |  | 001 | 0.0145 | 2.62 | 0.600 | 7.32 | -45.56 | -0.140 | 0.719 | 0.159 | 28.0 | 002 | f9d9d9d95731 |
| v1 | PctAcc | investment | 6 | 5 | 012/1 | 4.67 | 0.09 | 013 | 0.0169 | 3.02 | 0.614 | 7.38 | -41.28 | -0.121 | 0.737 | 0.202 | 27.6 | 014 | cbeb16455bf4 |
| v2 | CBOperProf | profitability | 7 | 5 | 012/2 | 3.02 | 0.95 | 015 | 0.0169 | 3.02 | 0.661 | 7.82 | -37.07 | -0.122 | 0.777 | 0.249 | 28.0 | 016 | 8b444636f0a1 |
| v3 | ShareIss5Y | external_financing | 8 | 6 | 012/3 | 3.61 | 2.83 | 017 | 0.0215 | 3.98 | 0.848 | 10.29 | -41.92 | -0.192 | 0.874 | 0.465 | 26.3 | 018 | 73ee92fe0723 |
| v4 | cfp | value | 9 | 6 | 012/4 | 2.97 | 2.19 | 019 | 0.0249 | 4.51 | 0.996 | 12.02 | -40.63 | -0.263 | 0.913 | 0.614 | 25.2 | 020 | 3329679c69fb |
| v5 | XFIN | external_financing | 10 | 6 | 012/5 | 3.27 | -0.64 | 021 | 0.0245 | 4.27 | 0.914 | 11.56 | -47.75 | -0.344 | 0.808 | 0.479 | 25.0 | 022 | d27916e567f2 |
| v6 | GP | profitability | 11 | 6 | 023/1 | 2.74 | 0.43 | 024 | 0.0242 | 4.23 | 0.925 | 11.72 | -49.42 | -0.323 | 0.843 | 0.490 | 25.2 | 025 | 21a6688ae5d1 |
| v7 | MaxRet | volatility | 12 | 7 | 023/3 | 4.01 | 1.75 | 026 | 0.0305 | 4.49 | 0.951 | 13.95 | -41.68 | -0.649 | 0.622 | 0.623 | 43.4 | 027 | 43c92213ae73 |
| v8 | roaq | profitability | 13 | 7 | 023/4 | 3.73 | 1.95 | 028 | 0.0320 | 4.50 | 0.967 | 15.18 | -43.36 | -0.721 | 0.613 | 0.604 | 44.1 | 029 | a12e87c5fb36 |
| v9 | RoE | profitability | 14 | 7 | 023/5 | 2.41 | -1.26 | 030 | 0.0323 | 4.50 | 0.932 | 14.87 | -43.67 | -0.734 | 0.579 | 0.581 | 44.3 | 031 | c961f5791816 |
| v10 | IdioVol3F | volatility | 15 | 7 | 032/2 | 2.03 | 0.89 | 033 | 0.0326 | 4.48 | 0.919 | 15.25 | -45.78 | -0.752 | 0.578 | 0.575 | 39.8 | 034 | 1b4195ff18b4 |
| v11 | STreversal | short_term_reversal | 16 | 8 | 032/5 | 3.81 | -0.54 | 035 | 0.0355 | 5.36 | 0.942 | 14.61 | -39.53 | -0.512 | 0.737 | 0.565 | 59.1 | 036 | 335b06e3d608 |
| v12 | zerotrade6M | liquidity | 17 | 9 | 037/1 | 2.69 | 1.72 | 038 | 0.0373 | 5.15 | 0.985 | 16.16 | -41.11 | -0.635 | 0.708 | 0.646 | 56.8 | 039 | 612e59349f40 |
| v13 | VolumeTrend | liquidity | 18 | 9 | 037/2 | 2.04 | -0.09 | 040 | 0.0372 | 5.24 | 0.979 | 16.13 | -41.60 | -0.619 | 0.719 | 0.635 | 56.6 | 041 | fa17bd1cd37e |
| v14 | TrendFactor | momentum | 19 | 9 | 037/5 | 2.14 | -0.01 | 042 | 0.0389 | 5.68 | 0.983 | 16.12 | -43.21 | -0.560 | 0.773 | 0.650 | 58.1 | 043 | 7fe6f001e708 |
