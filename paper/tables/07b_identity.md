*Table 07b_identity. The gross-versus-cost identity: with net vol close to gross vol, net Sharpe = gross Sharpe x (1 - cost/gross). Source: run 049 result blocks, computed here.*

| variant @ $100M | gross Sharpe | cost / gross | gross Sharpe x (1 - cost/gross) | net Sharpe | difference | gross vol % | net vol % |
|---|---|---|---|---|---|---|---|
| layer | 0.856 | 1.070 | -0.060 | -0.060 | +0.000 | 4.76 | 4.74 |
| layer_eta_0.25 | 0.857 | 0.973 | 0.023 | 0.023 | +0.000 | 4.76 | 4.75 |
| layer_eta_1 | 0.857 | 1.264 | -0.226 | -0.227 | -0.001 | 4.76 | 4.73 |
| layer_fixed_tier_spread | 0.854 | 0.416 | 0.499 | 0.502 | +0.003 | 4.76 | 4.73 |
| layer_exec_half_month | 0.662 | 1.464 | -0.307 | -0.308 | -0.001 | 4.50 | 4.49 |
| layer_tiered_borrow | 0.856 | 1.242 | -0.207 | -0.208 | -0.001 | 4.76 | 4.74 |
| layer_no_buffer | 1.068 | 1.794 | -0.848 | -0.843 | +0.005 | 5.98 | 6.01 |
| layer_no_beta_constraint | 0.805 | 0.978 | 0.018 | 0.018 | +0.000 | 5.45 | 5.44 |
| layer_dollar_neutral_only | 0.820 | 0.959 | 0.034 | 0.034 | +0.000 | 5.41 | 5.45 |
| equal_rank_decile | 0.793 | 1.635 | -0.503 | -0.507 | -0.004 | 15.80 | 15.66 |
| buffered | 0.736 | 1.157 | -0.116 | -0.116 | +0.000 | 15.30 | 15.24 |
