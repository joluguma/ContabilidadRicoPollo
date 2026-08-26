#!/usr/bin/env bash
# Reobtiene las referencias externas OCA usadas por ERP Colombia.
# No se versionan en git (ver .gitignore): son código de terceros,
# se traen frescas con este script cuando se clona el proyecto en una
# máquina nueva.
set -euo pipefail
cd "$(dirname "$0")/.."/custom_addons

if [ ! -d oca_l10n_colombia ]; then
  git clone --branch 19.0 --single-branch --depth 1 \
    https://github.com/OCA/l10n-colombia.git oca_l10n_colombia
fi

if [ ! -d oca_account_financial_reporting ]; then
  git clone --branch 19.0 --single-branch --depth 1 \
    https://github.com/OCA/account-financial-reporting.git oca_account_financial_reporting
fi

if [ ! -d oca_deps/date_range ] || [ ! -d oca_deps/report_xlsx ]; then
  mkdir -p oca_deps
  tmp_dir=$(mktemp -d)
  git clone --branch 19.0 --single-branch --depth 1 \
    https://github.com/OCA/server-ux.git "$tmp_dir/server-ux"
  git clone --branch 19.0 --single-branch --depth 1 \
    https://github.com/OCA/reporting-engine.git "$tmp_dir/reporting-engine"
  cp -R "$tmp_dir/server-ux/date_range" oca_deps/date_range
  cp -R "$tmp_dir/reporting-engine/report_xlsx" oca_deps/report_xlsx
  rm -rf "$tmp_dir"
fi

echo "Referencias OCA listas en custom_addons/."
