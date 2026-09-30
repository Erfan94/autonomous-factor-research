# Methodology — what is measured and how a signal is admitted

## Objects
- **Signal**: a stock-level number per month from point-in-time Sharadar data, defined in one `FactorDef` (`harness/factor_def.py`). Winsorised 1/99 on the month's cross-section, then percentile-ranked **within its sector** (a sector-month with fewer than 10 scored names ranks on the cross-section).
- **Universe**: relative screens with a membership band (`CLAUDE.md`), rebuilt every month from that month's rows; forward return from the signal-date close to the next business month-end with the Shumway delisting convention.
- **Market**: the universe's own cap-weighted holding-month return (`analytics.universe_market_return`), never an index.
- **IC**: Spearman correlation of the continuous score with the forward return, monthly; every t is Newey-West (3 lags). Halves, tiers, annual IC and decay on every block.
- **Composite**: the family blend (`blend_family_ranks`): mean of available member ranks within a family, mean across families with a score. Deciles cut per month; D10 minus D1, equal-weight names, gross.
- **Long-short (headline)**: D10−D1 minus β_t × market, β_t from months t−36..t−1 only (β = 0 before 12 months). The raw series and β sit beside it on every block.
- **MaxDD**: the worst drop of the compounded monthly LS series below its running peak, with the peak floored at 1.0, so a loss from inception counts.
- **Diagnostics on every block and rung** (never bars): full-window and ex-ante β, raw Sharpe, Sharpe ex the 3 best LS calendar years (with those years and their share of the summed return), Sharpe in bear and bull months (state = sign of the trailing 12-month market return at t−1).

## Stages
1. **Stage 1** (standalone): IC ≥ 0.010, NW t ≥ 2.5, both halves > 0, hedged gross D10−D1 > 0, coverage ≥ 40%, ≥ 30 names per decile, LS months ≥ floor.
2. **Families**: fewer than ten, assigned by economic definition after Stage 1, before any Stage 2 number.
3. **Stage 2** (marginal information): residual IC NW t > 2.0 after projecting the candidate's normal score on every current leg's normal score (within-sector ranks); guard: paired Δ of the family blend's hedged gross LS return, t ≥ −2.0. Diagnostics: paired ΔIC, spanning alpha, R², ΔSharpe, ΔMaxDD, Δβ, Δ ex-regime Sharpe.
4. **Stage 3** (construction, reported): equal decile, tier-neutral, ICIR-weighted, buffered, vol-targeted, each hedged as the search construction is. The institutional construction layer on the finished composite is `docs/CONSTRUCTION.md`, with the changes D7 owes it.
5. **Holdout**: 2022-01 .. 2026-09, spent once on the finished composite under D8, read from the `cut_holdout_*` fields of a continuous run.

## Why these rules
`research/LESSONS.md` numbers each rule's evidence. In short: information decides, construction reports; a one-leg change to a many-family blend is below a paired test's resolution on 276 months, so the residual test carries Stage 2; families stop duplicates from taking whole votes; the membership band removes boundary churn; no cost is charged so implementability is priced by the reader; the hedge and the sector ranking remove the two exposures the predecessor's information bars accumulated without measuring (LESSONS 27–29).

## Provenance
Four stamps on every block (`harness/provenance.py`); `records.py check` reconciles registry, events, frontier, phase gate, stranded runs and the live-API proof. Results are immutable once committed (`.githooks/pre-commit`).
