"""Restaurant layouts for Curitiba drawn from the Receita Federal CNPJ registry, placed with IBGE CNEFE 2022 coordinates.

Usage: python sim/city/restaurants.py <project_root> <out_dir> [release]

Registry: active establishments (situacao cadastral 02) in Curitiba (Receita municipality code from Municipios.zip,
expected 7535) whose main CNAE is 5611-2/01 (restaurants) or 5611-2/03 (snack bars). Each is placed at the mean
CNEFE 2022 coordinate of its postal code and street number (exact match), or at the mean coordinate of its postal
code (fallback), then counted per H3 resolution-9 cell of the city grid. Five layouts are drawn from that density
(multinomial, same total, seeds 0 to 4; seed 0 is the main layout) and compared with the registry and with
OpenStreetMap at zone level (H3 resolution 8) by Spearman correlation.

Outputs:
  data/derived/cnpj_food_curitiba.parquet       one row per establishment, never published (git-ignored)
  data/public/restaurant_density_h3r9.csv       registry establishments per cell, published
  sim/city/curitiba/restaurant_layouts.parquet  per cell: registry, s0..s4, osm (rebuilt from the public density)
  <out_dir>/report.json, report.md, zone_counts.csv, layouts.png
"""
import csv
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

import h3
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

FOOD = {"5611201": "restaurant", "5611203": "snack_bar"}
CONTEXT = {"5611204": "bar", "5611205": "bar_entertainment", "5620104": "home_meal_supply", "5612100": "street_food"}
ACTIVE = "02"
RES = 9
N_LAYOUTS = 5
# Estabelecimentos columns (Receita layout LAYOUT_DADOS_ABERTOS_CNPJ): positions used here
C_BASICO, C_ORDEM, C_DV, C_SIT, C_START, C_CNAE, C_CNAE2 = 0, 1, 2, 5, 10, 11, 12
C_TIPO, C_LOGR, C_NUM, C_BAIRRO, C_CEP, C_UF, C_MUN = 13, 14, 15, 17, 18, 19, 20


def municipality_code(rel):
    with zipfile.ZipFile(rel / "Municipios.zip") as z:
        text = z.read(z.namelist()[0]).decode("latin-1")
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    hits = [code for code, name in rows if name.strip().upper() == "CURITIBA"]
    assert len(hits) == 1, hits
    return hits[0]


def scan_registry(rel, mun):
    """Stream every Estabelecimentos file and keep Curitiba establishments with a food CNAE (main or secondary)."""
    key = f'"PR";"{mun}";'.encode()
    codes = set(FOOD) | set(CONTEXT)
    rows, n_city = [], 0
    for path in sorted(rel.glob("Estabelecimentos*.zip")):
        with zipfile.ZipFile(path) as z, z.open(z.namelist()[0]) as f:
            for line in f:
                if key not in line:
                    continue
                r = next(csv.reader([line.decode("latin-1")], delimiter=";"))
                if r[C_UF] != "PR" or r[C_MUN] != mun:
                    continue
                n_city += 1
                second = set(r[C_CNAE2].split(",")) if r[C_CNAE2] else set()
                if r[C_CNAE] in codes or second & set(FOOD):
                    rows.append({"cnpj": r[C_BASICO] + r[C_ORDEM] + r[C_DV], "status": r[C_SIT], "start": r[C_START],
                                 "cnae": r[C_CNAE], "food_secondary": bool(second & set(FOOD)),
                                 "street_type": r[C_TIPO], "street": r[C_LOGR], "number": r[C_NUM],
                                 "district": r[C_BAIRRO], "cep": r[C_CEP]})
        print(f"{path.name}: {len(rows)} food rows so far, {n_city} Curitiba establishments", flush=True)
    return pd.DataFrame(rows), n_city


def house_number(s):
    m = re.match(r"\s*0*(\d+)", s or "")
    return int(m.group(1)) if m and int(m.group(1)) > 0 else -1


def load_cnefe(path):
    with zipfile.ZipFile(path) as z, z.open(z.namelist()[0]) as f:
        df = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str,
                         usecols=["CEP", "NUM_ENDERECO", "LATITUDE", "LONGITUDE", "COD_ESPECIE"])
    df["cep"] = df["CEP"].str.zfill(8)
    df["num"] = pd.to_numeric(df["NUM_ENDERECO"], errors="coerce").fillna(-1).astype(int)
    df["lat"] = pd.to_numeric(df["LATITUDE"], errors="coerce")
    df["lng"] = pd.to_numeric(df["LONGITUDE"], errors="coerce")
    return df.dropna(subset=["lat", "lng"])


def geocode(act, cn):
    """Place establishments at the mean CNEFE coordinate of (postal code, number), else of the postal code."""
    act = act.copy()
    exact = cn[cn.num > 0].groupby(["cep", "num"])[["lat", "lng"]].mean()
    by_cep = cn.groupby("cep")[["lat", "lng"]].mean()
    act["cep"] = act.cep.str.zfill(8)
    act["num"] = act.number.map(house_number)
    ex = act.join(exact, on=["cep", "num"])
    fb = act.join(by_cep, on="cep")
    act["match"] = np.where(ex.lat.notna(), "exact", np.where(fb.lat.notna(), "postal_code", "none"))
    act["lat"] = ex.lat.fillna(fb.lat)
    act["lng"] = ex.lng.fillna(fb.lng)
    return act


def cell_counts(act, cells):
    """Registry establishments per grid cell (placed ones inside the grid) and the number placed outside it."""
    pos = {c: i for i, c in enumerate(cells.cell)}
    placed = act[act.lat.notna()].copy()
    placed["cell"] = [h3.latlng_to_cell(a, b, RES) for a, b in zip(placed.lat, placed.lng)]
    inside = placed.cell.isin(pos)
    counts = np.bincount(placed.cell[inside].map(pos).to_numpy(), minlength=len(cells)).astype(int)
    return counts, int((~inside).sum())


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    release = sys.argv[3] if len(sys.argv) > 3 else "2026-10"
    out.mkdir(parents=True, exist_ok=True)
    rel = root / "data/raw/cnpj" / release
    t0 = time.time()
    rep = {"release": release, "manifest": pd.read_csv(rel / "manifest.csv").to_dict("records")}

    mun = municipality_code(rel)
    rep["receita_municipality_code"] = mun
    reg, n_city = scan_registry(rel, mun)
    rep["curitiba_establishments_all_status_all_cnae"] = n_city
    main_food = reg[reg.cnae.isin(FOOD)]
    rep["food_main_cnae_any_status"] = {FOOD[k]: int((main_food.cnae == k).sum()) for k in FOOD}
    act = main_food[main_food.status == ACTIVE].copy()
    rep["food_main_cnae_active"] = {FOOD[k]: int((act.cnae == k).sum()) for k in FOOD}
    rep["active_food_only_as_secondary_cnae_not_used"] = int(((reg.status == ACTIVE) & ~reg.cnae.isin(FOOD)
                                                               & reg.food_secondary).sum())
    rep["active_context_codes_not_used"] = {CONTEXT[k]: int(((reg.status == ACTIVE) & (reg.cnae == k)).sum())
                                            for k in CONTEXT}

    # Geocode against CNEFE 2022: exact (postal code, number), else postal-code centroid.
    cn = load_cnefe(root / "data/raw/cnefe/4106902_CURITIBA.zip")
    rep["cnefe_addresses"] = int(len(cn))
    act = geocode(act, cn)
    rep["match_share"] = {k: round(float((act.match == k).mean()), 4) for k in ["exact", "postal_code", "none"]}
    rep["match_count"] = {k: int((act.match == k).sum()) for k in ["exact", "postal_code", "none"]}
    rep["establishments_without_number"] = int((act.num < 0).sum())

    cells = pd.read_parquet(root / "sim/city/curitiba/cells.parquet")
    pos = {c: i for i, c in enumerate(cells.cell)}
    registry, rep["placed_outside_city_grid"] = cell_counts(act, cells)
    act.drop(columns=["number"]).to_parquet(root / "data/derived/cnpj_food_curitiba.parquet")

    rep["registry_in_grid"] = int(registry.sum())
    rep["cells_with_registry_restaurant"] = int((registry > 0).sum())
    pub = root / "data/public"
    pub.mkdir(exist_ok=True)
    pd.DataFrame({"cell": cells.cell, "registry_food_establishments": registry})[registry > 0].to_csv(
        pub / "restaurant_density_h3r9.csv", index=False)

    # Draw the layouts from the published density, so anyone can rebuild them without the registry.
    dens = pd.read_csv(pub / "restaurant_density_h3r9.csv")
    p = np.zeros(len(cells))
    p[dens.cell.map(pos).to_numpy()] = dens.registry_food_establishments.to_numpy()
    total = int(p.sum())
    lay = pd.DataFrame({"cell": cells.cell, "registry": p.astype(int)})
    for s in range(N_LAYOUTS):
        rng = np.random.default_rng(np.random.SeedSequence([s, 5]))
        lay[f"s{s}"] = rng.multinomial(total, p / p.sum())
    lay["osm"] = cells.restaurants.to_numpy()
    lay.to_parquet(root / "sim/city/curitiba/restaurant_layouts.parquet")

    # Zone-level comparison (H3 resolution 8 parents of the grid cells).
    lay["zone"] = cells.parent8.to_numpy()
    z = lay.groupby("zone")[["registry", *[f"s{s}" for s in range(N_LAYOUTS)], "osm"]].sum()
    z.to_csv(out / "zone_counts.csv")
    corr = {}
    for col in [*[f"s{s}" for s in range(N_LAYOUTS)], "osm"]:
        rz, pz = spearmanr(z[col], z["registry"])
        rc, pc = spearmanr(lay[col], lay["registry"])
        corr[col] = {"zone_spearman": round(float(rz), 4), "zone_p": float(pz),
                     "cell_spearman": round(float(rc), 4), "cell_p": float(pc)}
    rep["zones"] = int(len(z))
    rep["spearman_vs_registry"] = corr
    rep["osm_total"] = int(lay.osm.sum())
    top = z.registry.sort_values(ascending=False)
    rep["registry_share_in_top_10pct_zones"] = round(float(top.iloc[: max(1, len(top) // 10)].sum() / top.sum()), 4)
    rep["osm_share_in_same_zones"] = round(float(z.osm[top.index[: max(1, len(top) // 10)]].sum() / z.osm.sum()), 4)
    rep["seconds"] = round(time.time() - t0, 1)
    (out / "report.json").write_text(json.dumps(rep, indent=1, default=str))
    plot(cells, lay, out / "layouts.png")
    print(json.dumps({k: v for k, v in rep.items() if k != "manifest"}, indent=1, default=str))


def plot(cells, lay, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 6.5), constrained_layout=True)
    for ax, col, title in zip(axes, ["registry", "s0", "osm"],
                              ["CNPJ registry (5611-2/01, 5611-2/03, active)", "Simulated layout, seed 0", "OpenStreetMap"]):
        v = lay[col].to_numpy()
        ax.scatter(cells.lng, cells.lat, s=3, c="#e6e6e6", linewidths=0)
        m = v > 0
        sc = ax.scatter(cells.lng[m], cells.lat[m], s=4 + 2 * np.sqrt(v[m]), c=np.log1p(v[m]), cmap="viridis",
                        linewidths=0)
        ax.set_title(f"{title}\n{int(v.sum()):,} places in {int(m.sum()):,} cells", fontsize=10)
        ax.set_aspect(1 / np.cos(np.radians(-25.43)))
        ax.set_xticks([]), ax.set_yticks([])
    cb = fig.colorbar(sc, ax=axes, orientation="horizontal", location="bottom", shrink=0.4)
    cb.set_label("log(1 + places per H3 resolution-9 cell)")
    fig.savefig(path, dpi=130)


if __name__ == "__main__":
    main()
