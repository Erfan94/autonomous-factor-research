# data/

| path | tracked | what |
|---|---|---|
| `sharadar/*.parquet` | no | the frozen snapshot, one file per table. Licensed, multi-GB. |
| `SNAPSHOT_MANIFEST.yaml` | **yes** | sha256, rows, columns and date range per table. `DATA_SHA` derives from it. |
| `sharadar_llms.txt` | **yes** | verbatim copy of <https://sharadar.com/llms.txt>, the API contract written for agents. |
| `cache/*.parquet` | no | derived panels, keyed on `DATA_SHA`, rebuilt when absent. |

## The API, in five lines

- Direct Sharadar API at `https://api.sharadar.com/v1.0`. **Not Nasdaq Data Link**; the `nasdaqdatalink` / `quandl` libraries do not work with a sharadar.com key.
- Key from <https://sharadar.com/account>, sent as the `x-api-key` header. Lives in `SHARADAR_API_KEY` in the environment or in the gitignored `.env`. Never on a query string, never in a tracked file.
- Bulk: `GET /data/{table}?years=full` answers 302 to a pre-signed zip of CSV, fetched without the key header. That is what `snapshot.py download` does.
- Tables are addressable by modern name (`stocks`, `fundamentals`) or legacy code (`SEP`, `SF1`); `config/runtime.yaml` maps the harness's legacy names to the API's. Public schemas at `GET /schema/{modern-name}`.
- The SF1 filing date, the point-in-time key, is the `date` column (legacy `datekey`). The harness accepts both. AR dimensions exclude restatements.

Verified live on 2026-09-14: monetary values are raw USD (AAPL ART assets `383266000000`); `tickers.table` values are `stocks` / `fundamentals`; `actions.contraticker` reads `N/A` when absent.

## First-time setup, in order

```bash
echo 'SHARADAR_API_KEY=...' > .env && chmod 600 .env   # gitignored; the hook refuses it anyway
python3 harness/snapshot.py probe          # key + plan entitlement, downloads nothing
python3 harness/snapshot.py download       # full-history bulk zips -> parquet
python3 harness/snapshot.py verify         # prints the vocabularies config must agree with
python3 harness/snapshot.py manifest       # writes SNAPSHOT_MANIFEST.yaml -> DATA_SHA
python3 harness/provenance.py              # all four stamps
```

`verify` prints the exchange, category, `tickers.table`, SF1-dimension and
ACTIONS vocabularies and a market-cap units check. `config/test_config.yaml`
names values from each; if they disagree, fix the config **before** the first
run, because after it every edit is a re-baseline.
