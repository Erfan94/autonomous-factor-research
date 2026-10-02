*Table 06i_stage3. Stage 3 on v14, in-window, acceptance-time, pre-refresh bytes. Source: MODEL_MANIFEST.yaml v14 `construction` (run 043); run 048 reproduced run 043 on every field but harness_sha (docs/JOURNAL.md, Phase E). Gross, hedged; raw Sharpe and full-window beta beside.*

| variant | sharpe | ls_t_nw | ann_ret_pct | vol_pct | maxdd_pct | worst_12m_pct | turnover_long_pct | turnover_short_pct | raw_sharpe | beta_fullwindow | sharpe_ex_top_years |
|---|---|---|---|---|---|---|---|---|---|---|---|
| equal_rank_decile | 0.983 | 3.91 | 16.12 | 16.41 | -43.2 | -41.4 | 58.1 | 54.4 | 0.773 | -0.56 | 0.65 |
| tier_neutral | 0.858 | 3.55 | 14.59 | 17.0 | -44.0 | -41.0 | 59.5 | 55.7 | 0.617 | -0.64 | 0.54 |
| icir_weighted | 0.902 | 4.2 | 15.54 | 17.23 | -33.1 | -27.7 | 39.1 | 37.7 | 0.464 | -0.93 | 0.64 |
| buffered | 0.954 | 3.81 | 15.01 | 15.73 | -42.0 | -38.6 | 38.5 | 32.6 | 0.72 | -0.57 | 0.65 |
| vol_targeted | 0.901 | 3.95 | 10.94 | 12.14 | -30.6 | -29.2 | 58.1 | 54.4 | 0.711 | -0.31 | 0.61 |
