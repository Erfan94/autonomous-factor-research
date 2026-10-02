*Table 07e_layer_positive_net_rows. Every construction-layer row with a positive net Sharpe. Source: runs 049 (`net_sharpe`), 057 (`cut_inwindow_net_sharpe`, `cut_holdout_net_sharpe`), all 33 variants each; `half_spread_mode` from the block.*

| run / window | variant | net Sharpe | half-spread mode |
|---|---|---|---|
| 049 | layer_dollar_neutral_only@100M | 0.034 | measured |
| 049 | layer_eta_0.25@100M | 0.023 | measured |
| 049 | layer_fixed_tier_spread@1000M | 0.156 | fixed |
| 049 | layer_fixed_tier_spread@100M | 0.502 | fixed |
| 049 | layer_no_beta_constraint@100M | 0.018 | measured |
| 057 in-window | layer_dollar_neutral_only@100M | 0.054 | measured |
| 057 in-window | layer_eta_0.25@100M | 0.058 | measured |
| 057 in-window | layer_fixed_tier_spread@1000M | 0.189 | fixed |
| 057 in-window | layer_fixed_tier_spread@100M | 0.519 | fixed |
