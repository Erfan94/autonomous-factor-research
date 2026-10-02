*Table 02_snapshots. The two snapshot recordings. Source: research/events.jsonl `snapshot_recorded` (record text truncated at 260 characters).*

| events line | ts (UTC) | old DATA_SHA | new DATA_SHA | tables | reason (record text) |
|---|---|---|---|---|---|
| 13 | 2026-09-30T16:41:44Z | (none) | 198b281de1a0 | 13 | first pull, full history, 13 tables; verify OK (vocabularies match config: exchanges, categories, 10 delisting actions, ART; marketcap median 712m); live OK column-complete; FUNDS mapped, not held |
| 1104 | 2026-10-01T23:27:07Z | 198b281de1a0 | 42587e08609a | 13 Sharadar + TB3MS (detail) | D8 step 1 refresh (owner-approved stop-and-ask 3): 13 Sharadar tables re-pulled full history (SEP 45,393,854 rows to 2026-10-01; 2026-09-30 present with 6,262 names vs 6,324 on 09-29) + TB3MS external (FRED, 1,113 rows 1934-01..2026-09, 2026-09 = 3.94, no fill … |
