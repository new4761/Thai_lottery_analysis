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
