SHELL := /bin/bash

.PHONY: help recover-range recover-month recover-august check

help:
	@echo "Targets:"
	@echo "  recover-range   Recover lottery data for START_DATE..END_DATE (required)"
	@echo "  recover-month   Recover lottery data for RECOVER_MONTH (YYYY-MM, required)"
	@echo "  recover-august  Recover August 2026"
	@echo "  check           Run unit tests"

recover-range:
	@if [ -z "$(START_DATE)" ] || [ -z "$(END_DATE)" ]; then \
		echo "START_DATE and END_DATE are required (YYYY-MM-DD)"; \
		exit 1; \
	fi
	python query.py --start-date $(START_DATE) --end-date $(END_DATE) --overwrite-existing
	python query_locker.py
	python validators.py lottery_results.csv

recover-month:
	@if [ -z "$(RECOVER_MONTH)" ]; then \
		echo "RECOVER_MONTH is required (YYYY-MM)"; \
		exit 1; \
	fi
	@RECOVER_MONTH="$(RECOVER_MONTH)" python - <<'PY'
import os
import datetime
import subprocess

month = datetime.datetime.strptime(os.environ["RECOVER_MONTH"] + "-01", "%Y-%m-%d").date()
if month.month == 12:
    end = datetime.date(month.year + 1, 1, 1) - datetime.timedelta(days=1)
else:
    end = datetime.date(month.year, month.month + 1, 1) - datetime.timedelta(days=1)

start = month.isoformat()
end = end.isoformat()

cmd = [
    "python",
    "query.py",
    "--start-date",
    start,
    "--end-date",
    end,
    "--overwrite-existing",
]
print(f"Running: {' '.join(cmd)}")
subprocess.check_call(cmd)
PY
	python query_locker.py
	python validators.py lottery_results.csv

recover-august:
	@$(MAKE) recover-month RECOVER_MONTH=2026-08

check:
	python -m unittest discover -s tests -v
