---
name: commit-step
description: Commit one logical step of the research loop to the LOCAL repository (no remote, no push — docs/DECISIONS.md D9) with the project's message format and stamp block. Use after a screen, a ratchet, a harness change, a data recording or a docs change, when CLAUDE.md says to commit.
---

# Commit one logical step

One logical change per commit: a screen's rows + summary + results file
together; a ratchet's composite edit + manifest block + rows + results
together; a harness change with its tests. Never mix a harness change into
a ratchet commit. Never `--no-verify` past a hook.

## Steps

1. `git status` — confirm only the step's files are staged-to-be. Never
   stage `data/sharadar/`, `data/cache/`, `.env`.
2. `python3 scripts/stamp_block.py` — prints the six stamp lines (moved /
   unmoved against HEAD) plus pytest count and holdout state.
3. Message:

```
<type>: <what changed, one line>

<what it means for the model — the stats that moved, or "number-neutral">

HARNESS_SHA   <12 hex>  (moved from <old> | unmoved)
CONFIG_SHA    <12 hex>  (moved from <old> | unmoved)
COMPOSITE_SHA <12 hex>  (moved from <old> | unmoved)
DATA_SHA      <12 hex>  (moved from <old> | unmoved)
pytest        <N> passed
holdout       unspent | SPENT <date>

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

Types: `ratchet` (composite version changed), `screen` (Stage 1 or a
rejecting ladder logged), `construct` (Stage 3 report logged), `harness`,
`config` (re-baseline), `data`, `probe`, `docs`, `chore`.

4. `git commit`. Never `git push`, never add a remote: the repository is
   local until the owner provides the GitHub link (D9). A ratchet also gets
   `git tag -a vN-add-<name> -m "<headline stats>"`. A snapshot recording
   gets `data-<DATA_SHA>`. Tags are never moved.
5. Log `repository_committed` in `research/events.jsonl` (commit sha, tags,
   `remote: none`).

## Hooks (enforced by the bytes, `.githooks/`)

- `pre-commit`: refuses snapshot/cache bytes, credential-looking files or
  an API key in the diff; runs `pytest tests/` when harness/factors/config
  changed; refuses a modification to a results file already committed.
- `commit-msg`: refuses a message without a type prefix and all four stamps.
