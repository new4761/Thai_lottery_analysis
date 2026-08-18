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
