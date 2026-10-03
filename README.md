# Agents Propose, Code Decides

**Agentic AI that builds an equity alpha model end to end, under rules it cannot change.**

This repository holds the code, the rules and the complete record of an autonomous research loop in which
large-language-model (LLM) agents build a multi-factor US equity alpha model. The agents inventory every predictor in
Chen and Zimmermann's [Open Source Asset Pricing](https://github.com/OpenSourceAP/CrossSection) catalogue,
translate each one to a frozen Sharadar data snapshot, test it, and assemble the survivors into a sector-neutral,
market-hedged composite. A deterministic Python harness computes every statistic and applies every acceptance rule.
The agents decide **what** to test; the code decides **how it is measured**.

> **Paper:** *Agents Propose, Code Decides: An Autonomous Research Loop Framework to Build an Equity Alpha Model*,
> Erfan Sadeghi (2026). Forthcoming; the link will be added here.

---

## Why this exists

Factor research usually fails procedurally rather than statistically: the number of signals tried is not recorded,
thresholds settle after the results are in, the backtest code changes between candidates, the holdout is looked at
more than once, and redundant signals are added anyway. An AI agent makes each of these failures easier, because it
tests faster than any person and forgets what it tried. This project puts the safeguards in the environment instead
of in the agent's conduct:

- **Agents propose, code decides.** A factor file may only compute a signal. Universe filters, ranking, hedging,
  statistics and verdicts live in the harness, which no agent can change without the change showing on every
  later result.
- **Provenance is a property of the bytes.** Every result is stamped with four hashes (harness code,
  pre-registration file, composite, data manifest), and a result that does not match the repository is refused.
- **Every rule is written before it is needed.** The bars, the test order, the out-of-sample boundary and the
  expectations the out-of-sample block is read against were fixed before the numbers they govern existed.
- **The denominator is the whole catalogue.** All 212 predictors are accounted for, tested or excluded with a
  measured reason.
- **Autonomy has a closed boundary.** The loop decides everything except seven questions reserved for the human.
- **Everything is written down, rejections included.**

## How the loop works

| Participant | Role |
|---|---|
| **Runner** (Claude Opus, in Claude Code) | Drives the search from the standing instruction file [`CLAUDE.md`](CLAUDE.md): reads the state, launches sub-agents, runs the harness, commits and tags. |
| **Advisor** (Claude Fable) | A stronger model consulted at phase boundaries, before acceptances and when a result looks too good. |
| `osap-fetcher` | Writes a construction spec for one predictor from the catalogue's code at a pinned commit. |
| `sharadar-field-checker` | Verifies every data field a factor needs by querying the snapshot itself. |
| `sharadar-translator` | Translates the spec into a factor file and runs preflight. |
| `alpha-reviewer` | Read-only adversarial audit for look-ahead, survivorship and point-in-time errors. |
| `factor-evaluator` | Checks the stamps, re-derives every verdict from the raw statistics and writes the records. |
| **Harness** (`harness/`) | Deterministic measurement: universe, within-sector ranks, deciles, market hedge, IC, Newey-West t-stats, bars. |
| **Enforcement** | Git hooks, a permission layer, phase gates in `scripts/records.py`, and the four stamps. |

The agent definitions are in [`.claude/agents/`](.claude/agents), the permission tiers in
[`.claude/settings.json`](.claude/settings.json), and the hooks in [`.githooks/`](.githooks).

The search runs in five phases, and no phase starts before the previous one closes:

| Phase | What happens |
|---|---|
| **A. Inventory** | Every catalogue predictor is specified, field-checked, translated and preflighted, or excluded with a measured reason. |
| **B. Stage 1 screen** | Every constructible predictor is tested alone, in alphabetical batches of twelve. |
| **C. Families** | Each passer is assigned to an economic family; the Stage 2 order is declared once, by Stage 1 t-stat. |
| **D. Stage 2 ratchet** | Candidates are tested in declared order against the current composite; each acceptance becomes a tagged version. |
| **E. Construction and validation** | Construction variants and an institutional construction layer on the final composite, then one spend of the out-of-sample block. |

## The selection rules

All parameters are fixed in [`config/test_config.yaml`](config/test_config.yaml) and hashed into `CONFIG_SHA`.

- **Universe:** US common stock on NYSE, NASDAQ and NYSE American, price ≥ $1; entry at the NYSE 20th percentile of
  market cap and the 20th percentile of dollar volume, exit below the 15th percentiles; rebuilt monthly.
- **Window:** decisions on January 1999 to December 2021 (276 months); January 2022 to September 2026 (57 months)
  reserved and spent once at the end.
- **Ranking and hedge:** every signal is percentile-ranked within its sector; every long-short is hedged to the
  market with a beta estimated on the prior 36 months only, and the raw series and its beta are reported alongside.
- **Stage 1 (standalone screen):** mean rank IC ≥ 0.010; Newey-West IC t-stat ≥ 2.50; positive IC in both halves;
  positive raw decile-10-minus-decile-1 return; coverage ≥ 40%; ≥ 30 names per decile.
- **Composite:** a two-level family blend, equal weight across fewer than ten economic families and within each.
- **Stage 2 (ratchet):** a candidate is admitted only if its *residual* IC, after projection on every current leg,
  has a Newey-West t-stat above 2.0, and adding it does not significantly hurt the hedged long-short
  (paired t-stat ≥ −2.0).
- **No transaction cost** is charged in the search; turnover is reported and never decides. Trading costs are
  modelled separately in the construction layer.

## Results

| | Baseline (v0) | Final composite (v14) |
|---|---|---|
| Legs / families | 5 / 5 | 19 / 9 |
| Mean rank IC, 1999–2021 | 0.0145 (t-stat 2.62) | 0.0389 (t-stat 5.68) |
| Hedged long-short Sharpe | 0.60 | 0.98 |
| Beta of the raw long-short | −0.14 | −0.56 |

- **The funnel:** 212 predictors inventoried, 107 screened (106 constructible predictors plus one declared sign
  reversal), 24 passed Stage 1, 14 accepted at Stage 2. The 101 not tested are listed with their reasons.
- **The final composite (v14)** has nine families: size, value, profitability, investment, momentum, external
  financing, volatility, short-term reversal and liquidity.
- **Out of sample (January 2022 to September 2026),** the ranking information held: the IC was 0.030, significant
  at the 10% level (t-stat 1.87). The hedged long-short earned 10.8% a year at a Sharpe of 0.52, about half the
  expected 1.00, and most of that return came from the market hedge rather than the stock selection. The
  beta-neutral construction layer was negative after costs.

The point of the project is the framework rather than the model: a research process that runs itself, traces every
number to the bytes that produced it, and reports a mixed out-of-sample result against expectations written down
before the test.

## Repository layout

| Path | Contents |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The standing instruction file: goal, rules, phases, stop-and-ask list, commands. |
| `harness/` | Data layer, analytics, runner, portfolio and construction layer, provenance, snapshot tools. |
| `config/` | The pre-registration (`test_config.yaml`), runtime settings and the construction layer's parameters. |
| `factors/` | The composite definition, the accepted legs, every candidate and the preflight failures. |
| `research/` | The record: registry (one row per candidate), event log, results of every run, families, Stage 2 order. |
| `MODEL_MANIFEST.yaml` | One block per composite version with its construction table, and the holdout state. |
| `osap_source/` | Specs and cached catalogue code at the pinned commit, the field map, and the untested predictors with reasons. |
| `docs/` | Decisions, methodology, construction layer, orchestration, and the step-by-step journal. |
| `scripts/` | Record maintenance and drift checks (`records.py`), commit stamps (`stamp_block.py`). |
| `tests/` | The harness test suite. |
| `data/` | The snapshot manifest only; the licensed data itself is not included. |

Each composite version has one annotated git tag, from `v0-baseline` to `v14-add-TrendFactor`. The `v1-add-PctAcc`
tag points at the commit before v1 (a logged process error); tags are never moved.

## Reproducing the results

Requirements: Python 3.11 and the packages in [`requirements.txt`](requirements.txt). The data come from a
[Sharadar](https://sharadar.com) subscription, which is licensed and cannot be redistributed, so you need your own
API key. [`data/README.md`](data/README.md) describes the setup.

```bash
pip install -r requirements.txt
pytest tests/                                      # the harness test suite

# Build and freeze your own snapshot (needs SHARADAR_API_KEY in the gitignored .env)
python3 harness/snapshot.py probe
python3 harness/snapshot.py download
python3 harness/snapshot.py verify
python3 harness/snapshot.py manifest
python3 harness/provenance.py                      # prints the four stamps

# Measure and construct the final composite on the decision window
python3 harness/run_test.py --baseline --stage 2
python3 harness/run_test.py --baseline --stage 3

# Inspect the records
python3 scripts/records.py state
python3 scripts/records.py check
```

The recorded results were produced under these stamps:

| Stamp | Covers | Value |
|---|---|---|
| `HARNESS_SHA` | `harness/*.py` | `1271266472a9` |
| `CONFIG_SHA` | `config/test_config.yaml` | `0d88328d5b10` |
| `COMPOSITE_SHA` | `factors/composite.py` and the accepted legs | `7fe6f001e708` |
| `DATA_SHA` | `data/SNAPSHOT_MANIFEST.yaml` | `42587e08609a` |

A snapshot pulled at a different time will carry a different `DATA_SHA`, because the vendor revises history; the
harness reports the stamps on every result so any difference is visible. The out-of-sample block has been spent:
re-running it on this snapshot would be a second look, and a new hypothesis needs a new window.

## License

Copyright (C) 2026 Erfan Sadeghi.

This project is licensed under the **GNU General Public License, version 2** ([`LICENSE`](LICENSE)). It includes
reference code from the Open Source Asset Pricing project by Andrew Y. Chen and Tom Zimmermann
(`osap_source/cache/`), which is itself distributed under GPL-2.0, and the factor translations in `factors/` follow
those constructions. Sharadar data are not included and remain subject to Sharadar's terms.

This repository is for research only and is not investment advice.

## Citation

If you use this work, please cite the paper:

```
Sadeghi, Erfan, 2026, Agents Propose, Code Decides: An Autonomous Research Loop Framework to Build an
Equity Alpha Model, working paper.
```

## Acknowledgements

The predictor catalogue is Chen, Andrew Y., and Tom Zimmermann, 2022, Open source cross-sectional asset pricing,
*Critical Finance Review* 11, 207–264. Data are from Sharadar. The agents run on Claude models by Anthropic,
through Claude Code.
