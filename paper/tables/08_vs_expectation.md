*Table 08_vs_expectation. The holdout against the expectations written before it. Metrics and sources from MODEL_MANIFEST.yaml v14 `holdout.vs_expectation` (= events `holdout_spent`); values re-read from the named run blocks (run 053; run 054 `cut_holdout_*`; run 055; runs 049 and 057 for the layer) at the paper's precision, and checked against the manifest's rounded values. Expectations from decision holdout_expectations_v14_spend_snapshot.*

| metric | in-window expectation (run 053 unless noted) | holdout | holdout source |
|---|---|---|---|
| hedged_sharpe | 0.996 | 0.523 | 054 |
| hedged_ann_return_pct | 16.34 | 10.81 | 054 |
| hedged_ls_t_nw | 3.96 | 1.18 | 054 |
| ex_top3_hedged_sharpe | 0.666 | -0.572 | 055 only (054 cut prints none); top years 2022,2024,2026 = 3 of 5 calendar years |
| excess_sharpe | 0.928 | 0.413 | 054 |
| excess_ann_return_pct | 15.09 | 8.54 | 054 |
| excess_ex_top3_sharpe | 0.605 | -0.708 | 054; top years 2022,2024,2026 |
| rf_credit_pp | -1.25 | -2.26 | 054 |
| ic_mean | 0.0389 | 0.0300 | 054; vs second-half benchmark 0.0283 |
| ic_t_nw | 5.68 | 1.87 | 054 |
| raw_sharpe | 0.790 | 0.124 | 054 (= 055) |
| raw_ann_return_pct | 14.91 | 3.01 | 054 (= 055) |
| hedged_maxdd_pct | -43.23 | -35.65 | 054 |
| layer_net_sharpe_100M | -0.060 | -0.367 | 057 layer@100M; expectation is run 049 on the old bytes (057 in-window restates it to -0.022) |
