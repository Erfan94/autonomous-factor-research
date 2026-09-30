# Orchestration — how the agents run the search

## Session model
- **Runner**: the session model (Claude Fable 5.1 at bootstrap) in the Claude Code desktop app, one session per stretch of the loop, `CLAUDE.md` as the standing instruction. The runner reads `research/session_state.yaml` first and ends every reply with the two mandatory blocks.
- **Advisor**: Claude Fable through the advisor tool, consulted by the runner at every phase boundary (A→B, B→C, C→D, D→E), before every acceptance is committed, before any stop-and-ask is raised, and whenever a result looks too good (single-factor NW t above ~6, residual share near 100%). Advice that changes a decision is logged as a `process_finding` event.
- **Human**: supplies the API key, answers the stop-and-ask list, steers occasionally, and decides when and what to publish. Never edits records by hand.

## Subagents (`.claude/agents/`)
| agent | model | job | invoked |
|---|---|---|---|
| `osap-fetcher` | sonnet | one predictor's source at the pinned OSAP commit → a construction-only spec | Phase A, per acronym, eight in parallel |
| `sharadar-field-checker` | sonnet | verify a field's existence, units, nulls and point-in-time shape on THIS snapshot | Phase A, per unverified field |
| `sharadar-translator` | sonnet | spec → `factors/candidates/<Name>.py` + preflight; `family` left unset | Phase A, per feasible predictor |
| `alpha-reviewer` | inherits | adversarial point-in-time and survivorship audit, read-only | after every translated batch; after any harness change |
| `factor-evaluator` | inherits | provenance check, bars, explanation, every record; acceptance mechanics | after every run |

## Skills and hooks
- `/commit-step`: one logical step per LOCAL commit, four stamps in every message, tags per composite version. No remote, no push (D9).
- `.githooks/pre-commit`: refuses snapshot bytes, credentials, an API key in the diff, a harness change without passing tests, an edit to a committed results file. `.githooks/commit-msg`: type prefix and the four stamps.
- `.claude/settings.json`: allow list for the loop's commands; asks before the download, a config edit, the holdout; denies every sibling project, `git push`, and the key file.

## Phase gates enforced by code
`scripts/records.py check`: Stage 2 may not start while a constructible predictor lacks a Stage 1 row or a passer lacks a family; a completed run must be evaluated before any stamp moves; the live-API proof must be fresh; the frontier must reconcile to SignalDoc.

## Cost model (what to expect)
A month-frame build is the expensive step: on the predecessor's machine (this one) about 100 s per month for ~115 factors, roughly linear in factor count, and one process peaks near 18 GB of memory — never run two builds at once. A 12-factor Stage 1 batch is about an hour; a 5-rung ladder about 1.5 h; a baseline about 25 min. Phase A is subagent time (three agents per predictor, about 200 predictors).
