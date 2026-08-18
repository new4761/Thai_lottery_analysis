Thai lottery fetch script with script for format data to be able to use with Google locker
Last run 17/04/2025, For my personal use

Visualization : https://lookerstudio.google.com/u/0/reporting/c0a35bdd-e32a-4bb8-b5fe-8a4f5d926cf3/page/9kEHF


Random lottery number tool: https://new4761.github.io/tools/lottery/

Updated tool endpoint (explicit): https://new4761.github.io/tools/lottery/index.html

Data sync: `run_lottery_job.yml` now triggers the site workflow on `3` and `17` each month, and sends a `repository_dispatch` event to
`new4761.github.io` only when `lottery_results.csv` actually changed.
Required secret in this repo:
- `NEW4761_SITE_DISPATCH_TOKEN` (PAT with permission to dispatch workflows on
  `new4761.github.io`).

To reduce unnecessary traffic:
- The workflow now computes a SHA-256 checksum of `lottery_results.csv` before and after refresh and only dispatches when checksum changes.
- The dispatch payload includes `lottery_results_csv_sha` and `lottery_results_csv_sha_prev` for downstream cache checks.

Data refresh is incremental:
- The script reuses existing local CSV rows and requests only newer draw dates (at most one draw cycle back), then rewrites the CSV.
