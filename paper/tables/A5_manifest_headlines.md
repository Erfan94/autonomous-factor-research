*Table A5_manifest_headlines. Manifest headlines v0-v14 in the project's summary format (Sharpe, return and MaxDD hedged; beta the full-window beta of the raw LS; turnover D10 per month). Sources: MODEL_MANIFEST.yaml `versions[*].baseline`; run 053; run 054 `cut_holdout_*` and run 055 (`ls_beta_fullwindow`, `turnover_d10_pct`) for the holdout row.*

| version | run | window and bytes | legs | families | mean IC | IC t (NW) | LS Sharpe | ann ret % | MaxDD % | beta | turnover % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v0 | 001 | acceptance-time (DATA 198b281de1a0) | 5 | 5 | 0.0145 | 2.62 | 0.600 | 7.32 | -45.56 | -0.140 | 28.0 |
| v1 | 013 | acceptance-time (DATA 198b281de1a0) | 6 | 5 | 0.0169 | 3.02 | 0.614 | 7.38 | -41.28 | -0.121 | 27.6 |
| v2 | 015 | acceptance-time (DATA 198b281de1a0) | 7 | 5 | 0.0169 | 3.02 | 0.661 | 7.82 | -37.07 | -0.122 | 28.0 |
| v3 | 017 | acceptance-time (DATA 198b281de1a0) | 8 | 6 | 0.0215 | 3.98 | 0.848 | 10.29 | -41.92 | -0.192 | 26.3 |
| v4 | 019 | acceptance-time (DATA 198b281de1a0) | 9 | 6 | 0.0249 | 4.51 | 0.996 | 12.02 | -40.63 | -0.263 | 25.2 |
| v5 | 021 | acceptance-time (DATA 198b281de1a0) | 10 | 6 | 0.0245 | 4.27 | 0.914 | 11.56 | -47.75 | -0.344 | 25.0 |
| v6 | 024 | acceptance-time (DATA 198b281de1a0) | 11 | 6 | 0.0242 | 4.23 | 0.925 | 11.72 | -49.42 | -0.323 | 25.2 |
| v7 | 026 | acceptance-time (DATA 198b281de1a0) | 12 | 7 | 0.0305 | 4.49 | 0.951 | 13.95 | -41.68 | -0.649 | 43.4 |
| v8 | 028 | acceptance-time (DATA 198b281de1a0) | 13 | 7 | 0.0320 | 4.50 | 0.967 | 15.18 | -43.36 | -0.721 | 44.1 |
| v9 | 030 | acceptance-time (DATA 198b281de1a0) | 14 | 7 | 0.0323 | 4.50 | 0.932 | 14.87 | -43.67 | -0.734 | 44.3 |
| v10 | 033 | acceptance-time (DATA 198b281de1a0) | 15 | 7 | 0.0326 | 4.48 | 0.919 | 15.25 | -45.78 | -0.752 | 39.8 |
| v11 | 035 | acceptance-time (DATA 198b281de1a0) | 16 | 8 | 0.0355 | 5.36 | 0.942 | 14.61 | -39.53 | -0.512 | 59.1 |
| v12 | 038 | acceptance-time (DATA 198b281de1a0) | 17 | 9 | 0.0373 | 5.15 | 0.985 | 16.16 | -41.11 | -0.635 | 56.8 |
| v13 | 040 | acceptance-time (DATA 198b281de1a0) | 18 | 9 | 0.0372 | 5.24 | 0.979 | 16.13 | -41.60 | -0.619 | 56.6 |
| v14 | 042 | acceptance-time (DATA 198b281de1a0) | 19 | 9 | 0.0389 | 5.68 | 0.983 | 16.12 | -43.21 | -0.560 | 58.1 |
| v14 | 053 | in-window, spend snapshot (DATA 42587e08609a) | 19 | 9 | 0.0389 | 5.68 | 0.996 | 16.34 | -43.23 | -0.556 | 58.1 |
| v14 | 054 (055 for beta, turnover) | holdout 2022-01..2026-09 | 19 | 9 | 0.0300 | 1.87 | 0.523 | 10.81 | -35.65 | -0.836 | 54.3 |
