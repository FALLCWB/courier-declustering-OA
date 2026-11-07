#!/usr/bin/env bash
# Download one monthly release of the Receita Federal open CNPJ data (Estabelecimentos and code tables).
# Usage: bash data/fetch_cnpj.sh [YYYY-MM]   (default 2026-10, the release used in the study)
# Source: Receita Federal public share "Dados/Cadastros/CNPJ", served by Nextcloud (SERPRO+):
#   https://arquivos.receitafederal.gov.br/index.php/s/gn672Ad4CF8N6TK?dir=/Dados/Cadastros/CNPJ
# The old directory https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/ answered 404 on 2026-11-01.
set -euo pipefail
REL=${1:-2026-10}
BASE="https://arquivos.receitafederal.gov.br/public.php/dav/files/gn672Ad4CF8N6TK/Dados/Cadastros/CNPJ/$REL"
OUT="data/raw/cnpj/$REL"
mkdir -p "$OUT"
FILES="Cnaes.zip Municipios.zip Motivos.zip $(for i in 0 1 2 3 4 5 6 7 8 9; do printf 'Estabelecimentos%s.zip ' $i; done)"
echo "file,url,downloaded_utc,bytes" > "$OUT/manifest.csv"
for f in $FILES; do
  curl -sS -L --fail --retry 8 --retry-delay 30 -C - -o "$OUT/$f" "$BASE/$f"
  unzip -tq "$OUT/$f" > /dev/null
  echo "$f,$BASE/$f,$(date -u +%Y-%m-%dT%H:%M:%SZ),$(stat -c %s "$OUT/$f")" >> "$OUT/manifest.csv"
  echo "ok $f"
done
