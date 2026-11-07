#!/usr/bin/env bash
# Download every public source of the study into data/raw. Run from the repository root.
# Sources checked on 2026-11-01. Raw files are never committed and never redistributed.
set -euo pipefail
RAW=data/raw
mkdir -p "$RAW"/{meituan,grubhub,ibge,osm,cnefe}
get() { curl -sS -L --fail --retry 5 --retry-delay 20 -C - -o "$2" "$1"; echo "ok $2"; }

# 1. Meituan INFORMS TSL Data-Driven Research Challenge (CC BY-NC 4.0; read License.txt before use).
#    Every publication must carry: "This research was supported by data provided by Meituan."
M=https://raw.githubusercontent.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/main
for f in License.txt all_waybill_info_meituan_0322.csv.zip courier_wave_info_meituan.csv \
         dispatch_rider_meituan.csv dispatch_waybill_meituan.csv \
         "TSL-Meituan%20challenge_background%20and%20data_20240321.pdf" tsl_meituan_2024_data_report_20241015.pdf; do
  get "$M/$f" "$RAW/meituan/$(printf '%b' "${f//%/\\x}")"
done

# 2. Grubhub Meal Delivery Routing Problem instances (repository states no license; research use with citation).
get https://github.com/grubhub/mdrplib/archive/refs/heads/master.zip "$RAW/grubhub/mdrplib.zip"
(cd "$RAW/grubhub" && unzip -oq mdrplib.zip)

# 3. IBGE 2022 census tracts with attributes, Parana (population v0001).
get https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/Agregados_por_Setores_Censitarios/malha_com_atributos/setores/gpkg/UF/PR/PR_setores_CD2022.gpkg \
    "$RAW/ibge/PR_setores_CD2022.gpkg"

# 4. IBGE CNEFE 2022 address coordinates for Curitiba (municipality 4106902) and the data dictionary.
C=https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV
get "$C/Municipio/41_PR/4106902_CURITIBA.zip" "$RAW/cnefe/4106902_CURITIBA.zip"
get "$C/Dicionario_CNEFE_Censo_2022.xls" "$RAW/cnefe/Dicionario_CNEFE_Censo_2022.xls"

# 5. Receita Federal open CNPJ data, release 2026-10 (Estabelecimentos and code tables): see data/fetch_cnpj.sh.
bash data/fetch_cnpj.sh 2026-10

# 6. OpenStreetMap (ODbL). Food places by bounding box from Overpass; the study file came from a mirror whose
#    snapshot was dated 2026-07-24T11:04:51Z, so a new download can differ slightly.
Q='[out:json][timeout:300];(nwr["amenity"~"^(restaurant|fast_food|cafe|ice_cream|food_court)$"](-25.65,-49.40,-25.34,-49.18);nwr["shop"~"^(bakery|pastry)$"](-25.65,-49.40,-25.34,-49.18););out center;'
curl -sS --fail --retry 5 --retry-delay 30 --data-urlencode "data=$Q" https://overpass-api.de/api/interpreter -o "$RAW/osm/curitiba_food.json"
echo "ok $RAW/osm/curitiba_food.json"
# The drive road network is downloaded by OSMnx inside sim/city/build.py when sim/city/curitiba/roads.graphml is absent.
