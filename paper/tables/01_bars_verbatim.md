*Table 01_bars_verbatim. The bars and the search rules, verbatim. Source: config/test_config.yaml lines 209-233 (CONFIG_SHA 0d88328d5b10).*

```yaml
acceptance_thresholds:

  stage1_standalone:
    min_ic_mean: 0.010
    min_ic_tstat_nw: 2.50            # Newey-West t of the monthly rank IC
    min_ic_half_mean: 0.0            # mean IC > 0 in BOTH halves of the window
    min_ls_ann_return_pct: 0.0       # D10-D1 GROSS annual return must be positive, on the series named below
    ls_spread_series: "raw"          # D11: the bar reads the RAW D10-D1 (ls_raw_ann_return_pct); "hedged" = the hedged headline
    min_coverage_pct: 40.0
    min_avg_names_per_decile: 30

  stage2_marginal:
    min_resid_ic_tstat_nw: 2.00      # residual IC after projecting on the base legs; STRICTLY GREATER THAN
    min_paired_delta_ls_tstat: -2.00 # guard: the family blend's hedged gross LS return must not fall significantly
    # The paired composite-dIC is a DIAGNOSTIC, not a bar: one leg added to a
    # many-family blend moves its IC by less than a paired test can resolve
    # on 276 months, so a dIC bar rejects on power rather than information.
search:
  composite_construction: "family_blend"   # 1/F across families, 1/n within; two-level, renormalised
  families_max: 9                          # fewer than ten families, assigned after Stage 1, before Stage 2
  stage1_batch_size: 12                    # candidates per Stage 1 run (one frame build per batch)
  stage1_order: "alphabetical_acronym"     # Stage 1 batches are formed in this order, never by any number
  stage2_order: "descending_stage1_ic_tstat_nw"  # over ALL Stage 1 passers, declared before any Stage 2 number
  stage2_ladder_max_rungs: 5
```
