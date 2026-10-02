*Table 08_vs_expectation. The holdout against the expectations written before it. Source: MODEL_MANIFEST.yaml v14 `holdout.vs_expectation` (= events `holdout_spent` vs_expectation); expectations from decision holdout_expectations_v14_spend_snapshot.*

| metric | in-window expectation (run 053 unless noted) | holdout | holdout source |
|---|---|---|---|
| hedged_sharpe | 0.9964 | 0.5233 | 054 |
| hedged_ann_return_pct | 16.34 | 10.81 | 054 |
| hedged_ls_t_nw | 3.96 | 1.18 | 054 |
| ex_top3_hedged_sharpe | 0.6665 | -0.5717 | 055 only (054 cut prints none); top years 2022,2024,2026 = 3 of 5 calendar years |
| excess_sharpe | 0.9285 | 0.413 | 054 |
| excess_ann_return_pct | 15.09 | 8.54 | 054 |
| excess_ex_top3_sharpe | 0.6045 | -0.7084 | 054; top years 2022,2024,2026 |
| rf_credit_pp | -1.25 | -2.26 | 054 |
| ic_mean | 0.0389 | 0.03 | 054; vs second-half benchmark 0.0283 |
| ic_t_nw | 5.68 | 1.87 | 054 |
| raw_sharpe | 0.7902 | 0.1239 | 054 (= 055) |
| raw_ann_return_pct | 14.91 | 3.01 | 054 (= 055) |
| hedged_maxdd_pct | -43.23 | -35.65 | 054 |
| layer_net_sharpe_100M | -0.06 | -0.367 | 057 layer@100M; expectation is run 049 on the old bytes (057 in-window restates it to -0.022) |
