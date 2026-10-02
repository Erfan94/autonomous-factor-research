*Table 03d_null_fp. Expected false positives under the global null. Normal tail, p = 0.5 erfc(z / sqrt 2); counts from research/registry/*.yaml and research/registry_index.yaml `search_accounting`; bars from config/test_config.yaml; the 2.74 flip bar from CLAUDE.md and events `flip_hypothesis_qualified`. The expectation n x p holds under any dependence between tests; dependence widens its spread.*

| test family | tests n | bar | tail | p = P(Z beyond bar) | expected false positives n x p | observed |
|---|---|---|---|---|---|---|
| Stage 1, published sign | 106 | NW t >= 2.50 | one-sided (upper) | 0.006210 | 0.658 | 27 with t >= bar; 23 passed every bar |
| Stage 1, flip qualification (reversed sign) | 106 | NW t <= -2.74 | one-sided (lower) | 0.003072 | 0.326 | 2 qualified, 1 screened and passed |
| Stage 1, both paths | 106 |  |  | 0.009282 | 0.984 | 24 passed |
| Stage 2, residual IC | 24 | NW t > 2.00 | one-sided (upper) | 0.022750 | 0.546 | 14 accepted |
