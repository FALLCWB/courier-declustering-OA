"""G1 fix F3: does adding home-meal kitchens (main CNAE 5620-1/04) change where restaurants are?

Usage: python sim/city/home_meal_check.py <project_root> <out_dir> [release]

Scans the same Receita release as sim/city/restaurants.py, geocodes the active establishments whose main CNAE is
5620-1/04 (meals prepared for home consumption: marmitarias, delivery-only kitchens) the same way, and compares
the density without them (the published layout source) and with them by Spearman correlation at zone level
(H3 resolution 8) and at cell level. Rule from the G1 verdict: 0.95 or above, one sentence in the report; below,
a robustness layout with them, and the main layout choice goes to Filipe.

Outputs: <out_dir>/report.json, report.md, zone_counts.csv. No establishment-level file is written.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sim.city.restaurants import ACTIVE, FOOD, cell_counts, geocode, load_cnefe, municipality_code, scan_registry  # noqa: E402

HOME_MEAL = "5620104"
THRESHOLD = 0.95


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    release = sys.argv[3] if len(sys.argv) > 3 else "2026-10"
    out.mkdir(parents=True, exist_ok=True)
    rel = root / "data/raw/cnpj" / release
    t0 = time.time()
    reg, _ = scan_registry(rel, municipality_code(rel))
    cn = load_cnefe(root / "data/raw/cnefe/4106902_CURITIBA.zip")
    cells = pd.read_parquet(root / "sim/city/curitiba/cells.parquet")

    food = geocode(reg[reg.cnae.isin(FOOD) & (reg.status == ACTIVE)], cn)
    home = geocode(reg[(reg.cnae == HOME_MEAL) & (reg.status == ACTIVE)], cn)
    without, _ = cell_counts(food, cells)
    extra, home_outside = cell_counts(home, cells)
    with_home = without + extra

    # The main-CNAE density computed here must equal the published one (same scan, same geocoding).
    pub = pd.read_csv(root / "data/public/restaurant_density_h3r9.csv")
    pos = {c: i for i, c in enumerate(cells.cell)}
    published = np.zeros(len(cells), int)
    published[pub.cell.map(pos).to_numpy()] = pub.registry_food_establishments.to_numpy()

    lay = pd.DataFrame({"zone": cells.parent8.to_numpy(), "without": without, "home_meal": extra, "with": with_home})
    z = lay.groupby("zone")[["without", "home_meal", "with"]].sum()
    z.to_csv(out / "zone_counts.csv")
    rz, pz = spearmanr(z["without"], z["with"])
    rc, pc = spearmanr(lay["without"], lay["with"])
    rh, ph = spearmanr(z["without"], z["home_meal"])
    rep = {"release": release, "home_meal_cnae": HOME_MEAL,
           "home_meal_active": int(len(home)),
           "home_meal_match_share": {k: round(float((home.match == k).mean()), 4) for k in ["exact", "postal_code", "none"]},
           "home_meal_placed_in_grid": int(extra.sum()), "home_meal_placed_outside_grid": home_outside,
           "food_main_cnae_placed_in_grid": int(without.sum()),
           "home_meal_share_of_food_placed": round(float(extra.sum() / without.sum()), 4),
           "published_density_reproduced": bool((published == without).all()),
           "zones": int(len(z)),
           "zone_spearman_without_vs_with": round(float(rz), 4), "zone_p": float(pz),
           "cell_spearman_without_vs_with": round(float(rc), 4), "cell_p": float(pc),
           "zone_spearman_food_vs_home_meal_alone": round(float(rh), 4), "zone_p_home_meal_alone": float(ph),
           "threshold": THRESHOLD, "passes": bool(rz >= THRESHOLD), "seconds": round(time.time() - t0, 1)}
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    verdict = ("at or above 0.95: the main layout stays on main CNAE 5611-2/01 and 5611-2/03; home-meal kitchens "
               "sit where the restaurants already are" if rep["passes"] else
               "below 0.95: a robustness layout with home-meal kitchens is added, and the main layout choice goes to Filipe")
    (out / "report.md").write_text(
        f"# Home-meal kitchens check (G1 fix F3), release {release}\n\n"
        f"Active establishments with main CNAE 5620-1/04 in Curitiba: {rep['home_meal_active']:,}; CNEFE match exact "
        f"{100 * rep['home_meal_match_share']['exact']:.1f}%, postal code {100 * rep['home_meal_match_share']['postal_code']:.1f}%, "
        f"none {100 * rep['home_meal_match_share']['none']:.1f}%; {rep['home_meal_placed_in_grid']:,} placed in the grid, "
        f"{100 * rep['home_meal_share_of_food_placed']:.1f}% of the {rep['food_main_cnae_placed_in_grid']:,} restaurants and "
        f"snack bars placed.\n\n"
        f"| Comparison | Spearman | Units |\n|---|---|---|\n"
        f"| Density without vs with home-meal kitchens, zones | {rep['zone_spearman_without_vs_with']:.4f} | {rep['zones']} H3 res-8 zones |\n"
        f"| Density without vs with home-meal kitchens, cells | {rep['cell_spearman_without_vs_with']:.4f} | {len(cells):,} H3 res-9 cells |\n"
        f"| Restaurants and snack bars vs home-meal kitchens alone, zones | {rep['zone_spearman_food_vs_home_meal_alone']:.4f} | {rep['zones']} zones |\n\n"
        f"Zone-level Spearman {verdict}. The density without them equals the published `data/public/restaurant_density_h3r9.csv`: "
        f"{'yes' if rep['published_density_reproduced'] else 'NO'}.\n")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
