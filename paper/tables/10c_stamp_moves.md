*Table 10c_stamp_moves. Every stamp move. Source: events `harness_changed`, `config_changed`, `snapshot_recorded`, `composite_updated`, and finding_corrected bootstrap_stamps for the first commit (the two bootstrap rows that preceded it carry no SHA).*

| events line | ts (UTC) | event | old | new | reason (record text, truncated at 160) |
|---|---|---|---|---|---|
| 7 | 2026-09-30T13:05:45Z | first commit 705d9f9 | HARNESS / CONFIG / COMPOSITE / DATA | e2e0b18a0115 / 1cef53e19e16 / f9d9d9d95731 / nodata | stamps of the first commit (finding_corrected bootstrap_stamps) |
| 10 | 2026-09-30T16:11:08Z | config_changed | 1cef53e19e16 | 0d88328d5b10 | [text omitted: refers to another project; events.jsonl line 10] |
| 11 | 2026-09-30T16:11:08Z | harness_changed | e2e0b18a0115 | 73a95d352942 | D11: stage1_checks reads ls_spread_series (default raw) and names the bar row after the series; ls_raw_ann_return_pct required on Stage 1 blocks; records.py ind … |
| 13 | 2026-09-30T16:41:44Z | snapshot_recorded | nodata | 198b281de1a0 | first pull, full history, 13 tables; verify OK (vocabularies match config: exchanges, categories, 10 delisting actions, ART; marketcap median 712m); live OK col … |
| 27 | 2026-09-30T16:53:36Z | composite_updated v0 |  | f9d9d9d95731 | runs 001,002 |
| 899 | 2026-10-01T06:13:22Z | composite_updated v1 |  | cbeb16455bf4 | runs 012,013,014 |
| 908 | 2026-10-01T06:25:38Z | composite_updated v2 |  | 8b444636f0a1 | runs 012,015,016 |
| 916 | 2026-10-01T06:36:15Z | composite_updated v3 |  | 73ee92fe0723 | runs 012,017,018 |
| 924 | 2026-10-01T06:47:03Z | composite_updated v4 |  | 3329679c69fb | runs 012,019,020 |
| 932 | 2026-10-01T06:58:27Z | composite_updated v5 |  | d27916e567f2 | runs 012,021,022 |
| 953 | 2026-10-01T07:32:25Z | composite_updated v6 |  | 21a6688ae5d1 | runs 023,024,025 |
| 961 | 2026-10-01T07:51:16Z | composite_updated v7 |  | 43c92213ae73 | runs 023,026,027 |
| 969 | 2026-10-01T08:10:20Z | composite_updated v8 |  | a12e87c5fb36 | runs 023,028,029 |
| 977 | 2026-10-01T08:29:53Z | composite_updated v9 |  | c961f5791816 | runs 023,030,031 |
| 999 | 2026-10-01T09:25:17Z | composite_updated v10 |  | 1b4195ff18b4 | runs 032,033,034 |
| 1007 | 2026-10-01T09:58:12Z | composite_updated v11 |  | 335b06e3d608 | runs 032,035,036 |
| 1028 | 2026-10-01T12:02:46Z | composite_updated v12 |  | 612e59349f40 | runs 037,038,039 |
| 1036 | 2026-10-01T13:11:19Z | composite_updated v13 |  | fa17bd1cd37e | runs 037,040,041 |
| 1044 | 2026-10-01T14:38:34Z | composite_updated v14 |  | 7fe6f001e708 | runs 037,042,043 |
| 1060 | 2026-10-01T17:04:10Z | harness_changed | 73a95d352942 | 471f70782486 | D7 construction layer: (1) sector+market-beta neutrality via a constraint matrix [sector dummies \| beta_i], beta_i trailing 36m on D4's M (min 12, sector-month … |
| 1071 | 2026-10-01T18:44:13Z | harness_changed | 471f70782486 | 3561590b660a | alpha_review fixes to the D7 layer (layer path only): declared vs effective ex-years fields (2000 precedes book_start; effective 2001,2021); name_cap_excess car … |
| 1089 | 2026-10-01T21:21:35Z | harness_changed | 3561590b660a | aef490297071 | diagnostic --return-start skip1 (alpha_review major 1): forward return of t+1 based at the first SEP trade of t+1 (within 7 days of the market's first trading d … |
| 1098 | 2026-10-01T23:07:10Z | harness_changed | aef490297071 | 1271266472a9 | rf diagnostic (owner_stop_and_ask_3_approved): external-table kind in snapshot.py (TB3MS from FRED fredgraph.csv, keyless, frozen in data/sharadar/TB3MS.parquet … |
| 1104 | 2026-10-01T23:27:07Z | snapshot_recorded | 198b281de1a0 | 42587e08609a | D8 step 1 refresh (owner-approved stop-and-ask 3): 13 Sharadar tables re-pulled full history (SEP 45,393,854 rows to 2026-10-01; 2026-09-30 present with 6,262 n … |
