*Table 01b_stop_and_ask. The stop-and-ask list. Source: CLAUDE.md lines 132-139.*

| # | stop and ask (verbatim) |
|---|---|
| 1 | Spending the out-of-sample block (`--include-holdout` / `--holdout-only`, once, ever). |
| 2 | Anything that moves CONFIG_SHA (a re-baseline). |
| 3 | Anything that moves DATA_SHA (refreshing the snapshot, adding a table) — including the refresh the holdout spend needs (D8). |
| 4 | Bumping `osap_source.ref`. |
| 5 | Declaring the search finished and running the final validation. |
| 6 | A rule contradicting itself, or a result implying already-logged rows are wrong. |
| 7 | A tenth family (config `search.families_max`). |
