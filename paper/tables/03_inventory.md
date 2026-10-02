*Table 03_inventory. Inventory accounting. Sources: research/events.jsonl `inventory_classified`; osap_source/osap_frontier.yaml; research/registry/*.yaml; research/registry_index.yaml `search_accounting`.*

| class | count | source |
|---|---|---|
| OSAP predictors (SignalDoc Cat.Signal = Predictor, ref b4e911e6) | 212 | inventory_classified |
| seed legs (v0, never screened) | 5 | inventory_classified |
| constructible: translated and preflight-passed | 106 | inventory_classified |
| constructible: preflight failed (frontier class preflight_failed) | 28 | osap_frontier.yaml |
| not constructible: data unavailable in Sharadar (frontier class data_unavailable) | 64 | osap_frontier.yaml |
| not constructible: data start too late (frontier class data_start) | 9 | osap_frontier.yaml |
| Stage 1 screens (translated candidates plus one declared flip) | 107 | registry rows |
| Stage 1 passes | 24 | registry rows |
| Stage 1 rejections | 83 | registry rows |
| Stage 1 inconclusive | 0 | registry_index |
