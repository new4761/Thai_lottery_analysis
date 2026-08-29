# Thai Lottery Tools

## Random Lottery Number Generator
**Generates random Thai lottery numbers for entertainment purposes.**

→ [Open lottery tool](https://new4761.github.io/tools/lottery/)

## Historical Data & Analysis
**View Thai lottery results and trends in Looker Studio dashboard.**

→ [View on Looker Studio](https://lookerstudio.google.com/u/0/reporting/c0a35bdd-e32a-4bb8-b5fe-8a4f5d926cf3/page/9kEHF)

---

## Operations

**Data sync**: Runs automatically on the 3rd and 17th of each month at 15:00 Thailand time. The pipeline:
1. Fetches Thai lottery results from GLO API
2. Transforms data for Looker Studio
3. Commits updated CSVs to repository
4. Publishes results to Google Sheets
5. Triggers new4761.github.io site rebuild

**Manual backfill**: To recover a specific window (for example August), run workflow_dispatch with:
```text
start_date: YYYY-MM-DD
end_date: YYYY-MM-DD
overwrite_existing: true
publish_updates: false
```

By default, manual backfills run without publishing to Google Sheets or triggering site deploy.
Set `publish_updates: true` only when you want CI publication side effects.

Or run locally to mimic CI behavior:
```bash
python query.py --start-date 2026-08-01 --end-date 2026-08-31 --overwrite-existing
python query_locker.py
python validators.py lottery_results.csv
```

Or use make:
```bash
make recover-range START_DATE=2026-08-01 END_DATE=2026-08-31
make recover-month RECOVER_MONTH=2026-08
make recover-august
make check
```

**Requirements**:
- Python 3.11+
- `pip install -r requirements.txt`

**Secrets** (GitHub Actions):
- `NEW4761_SITE_DISPATCH_TOKEN`: PAT to trigger site rebuild workflow
- `GOOGLE_APPLICATION_CREDENTIALS`: Service account JSON for Google Sheets

**Test**:
```bash
python -m unittest discover -s tests -v
```
