#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ "$#" -ne 1 ]; then
  echo "Usage: bash deploy.sh CONNECTION_NAME" >&2
  exit 2
fi

connection="$1"
stage='@LAUNCH_MYSTERY.DEMO.APP_FILES'

for script in sql/01_setup.sql sql/02_seed.sql sql/03_services.sql; do
  snow sql -c "$connection" --enhanced-exit-codes -f "$script"
done

for file in app/streamlit_app.py app/incident.py app/environment.yml; do
  snow stage copy "$file" "$stage" -c "$connection" --overwrite
done

snow sql -c "$connection" --enhanced-exit-codes -f sql/04_app.sql
snow sql -c "$connection" --enhanced-exit-codes -f sql/05_smoke.sql
