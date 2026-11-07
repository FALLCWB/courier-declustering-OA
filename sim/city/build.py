"""Build the Curitiba city model: H3 cells, population, restaurants, road travel times between cells.

Usage: python build.py <project_root>
Inputs: data/raw/ibge/PR_setores_CD2022.gpkg (IBGE 2022 census tracts); OpenStreetMap via OSMnx (cached in data/raw/osm_cache).
Outputs in sim/city/curitiba/: cells.parquet, restaurants.parquet, travel_s.npy, build_report.txt.
"""
import sys
import time
from pathlib import Path

import geopandas as gpd
import h3
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import Polygon, mapping

ROOT = Path(sys.argv[1])
OUT = ROOT / "sim" / "city" / "curitiba"
OUT.mkdir(parents=True, exist_ok=True)
RES = 9                      # H3 resolution of the simulation grid (about 0.1 km2 per cell)
UTM = "EPSG:31982"           # SIRGAS 2000 / UTM zone 22S
# Free-flow car speeds by road class (km/h) where OSM has no maxspeed; scaled at run time by a calibrated factor.
HWY_SPEEDS = {"motorway": 80, "trunk": 60, "primary": 50, "secondary": 40, "tertiary": 40,
              "unclassified": 30, "residential": 30, "living_street": 20, "service": 20}
FOOD_TAGS = {"amenity": ["restaurant", "fast_food", "cafe", "ice_cream", "food_court"], "shop": ["bakery", "pastry"]}
report = []
log = report.append
t0 = time.time()

# 1. Census tracts and the municipal boundary.
tracts = gpd.read_file(ROOT / "data/raw/ibge/PR_setores_CD2022.gpkg", where="NM_MUN = 'Curitiba'")
tracts = tracts[["CD_SETOR", "NM_BAIRRO", "SITUACAO", "v0001", "geometry"]].rename(columns={"v0001": "pop"})
tracts["pop"] = pd.to_numeric(tracts["pop"], errors="coerce").fillna(0)
tracts = tracts.to_crs("EPSG:4326")
boundary = tracts.geometry.union_all()
log(f"tracts: {len(tracts)}; population (v0001): {int(tracts['pop'].sum()):,}")

# 2. H3 cells whose centroid falls inside Curitiba, with area-weighted population.
cell_ids = sorted(h3.geo_to_cells(mapping(boundary), RES))
cells = gpd.GeoDataFrame(
    {"cell": cell_ids},
    geometry=[Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]) for c in cell_ids],
    crs="EPSG:4326")
cells["lat"] = [h3.cell_to_latlng(c)[0] for c in cell_ids]
cells["lng"] = [h3.cell_to_latlng(c)[1] for c in cell_ids]
cells["parent8"] = [h3.cell_to_parent(c, 8) for c in cell_ids]
tu, cu = tracts.to_crs(UTM), cells.to_crs(UTM)
tu["tract_area"] = tu.area
inter = gpd.overlay(cu[["cell", "geometry"]], tu[["CD_SETOR", "pop", "tract_area", "geometry"]], how="intersection")
inter["pop_part"] = inter["pop"] * inter.area / inter["tract_area"]
cells["pop"] = cells["cell"].map(inter.groupby("cell")["pop_part"].sum()).fillna(0.0)
log(f"H3 res {RES} cells: {len(cells)}; population assigned to cells: {cells['pop'].sum():,.0f}")

# 3. Road network (drive), largest strongly connected component, free-flow travel times.
ox.settings.cache_folder = str(ROOT / "data/raw/osm_cache")
ox.settings.use_cache = True
ox.settings.requests_timeout = 120
ox.settings.overpass_rate_limit = False
OVERPASS = ["https://overpass-api.de/api", "https://overpass.private.coffee/api", "https://overpass.kumi.systems/api"]


def overpass(fn, *args, **kw):
    """Call an OSMnx download, moving to the next public Overpass endpoint when one is at capacity."""
    for attempt in range(6):
        ox.settings.overpass_url = OVERPASS[attempt % len(OVERPASS)]
        try:
            return fn(*args, **kw)
        except Exception as e:  # noqa: BLE001 - network errors from any endpoint
            print(f"{ox.settings.overpass_url}: {type(e).__name__}; trying next", flush=True)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError("all Overpass endpoints failed")


if (OUT / "roads.graphml").exists():   # downloaded once; Overpass is often at capacity
    G = ox.load_graphml(OUT / "roads.graphml")
else:
    G = overpass(ox.graph_from_polygon, boundary.buffer(0.01), network_type="drive", simplify=True)
    G = ox.truncate.largest_component(G, strongly=True)
    G = ox.routing.add_edge_speeds(G, hwy_speeds=HWY_SPEEDS, fallback=30)
    G = ox.routing.add_edge_travel_times(G)
log(f"road graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges, "
    f"{sum(d['length'] for _, _, d in G.edges(data=True)) / 1000:,.0f} km")
if not (OUT / "roads.graphml").exists():
    ox.save_graphml(G, OUT / "roads.graphml")

nodes = list(G.nodes)
idx = {n: i for i, n in enumerate(nodes)}
xs = np.array([G.nodes[n]["x"] for n in nodes])
ys = np.array([G.nodes[n]["y"] for n in nodes])
best, shortest = {}, {}
for u, v, d in G.edges(data=True):
    key = (idx[u], idx[v])
    best[key] = min(best.get(key, np.inf), d["travel_time"])
    shortest[key] = min(shortest.get(key, np.inf), d["length"])
rows, cols = zip(*best.keys())
A = csr_matrix((list(best.values()), (rows, cols)), shape=(len(nodes), len(nodes)))
L = csr_matrix((list(shortest.values()), (rows, cols)), shape=(len(nodes), len(nodes)))

# 4. Snap cell centroids to the nearest road node; walking offset from centroid to node is kept as access time.
cells["node"] = ox.distance.nearest_nodes(G, cells["lng"].values, cells["lat"].values)
cells["node_i"] = cells["node"].map(idx)
snap = gpd.GeoSeries(gpd.points_from_xy(cells["lng"], cells["lat"]), crs="EPSG:4326").to_crs(UTM)
nodept = gpd.GeoSeries(gpd.points_from_xy(xs[cells["node_i"]], ys[cells["node_i"]]), crs="EPSG:4326").to_crs(UTM)
cells["snap_m"] = snap.distance(nodept).values
log(f"cell centroid to road node: median {cells['snap_m'].median():.0f} m, p95 {cells['snap_m'].quantile(0.95):.0f} m")

# 5. Restaurants from OSM, assigned to their H3 cell. Fetched once by bounding box from an Overpass mirror
#    (data/raw/osm/curitiba_food.json; query in data/README.md) because polygon queries timed out.
import json
els = json.loads((ROOT / "data/raw/osm/curitiba_food.json").read_text(encoding="utf-8"))["elements"]
food = pd.DataFrame([{
    "kind": e["tags"].get("amenity") or e["tags"].get("shop"), "name": e["tags"].get("name"),
    "lat": e["lat"] if e["type"] == "node" else e["center"]["lat"],
    "lng": e["lon"] if e["type"] == "node" else e["center"]["lon"]} for e in els])
food["cell"] = [h3.latlng_to_cell(a, b, RES) for a, b in zip(food["lat"], food["lng"])]
food = food[food["cell"].isin(set(cells["cell"]))]
rest = food[["kind", "name", "lat", "lng", "cell"]].reset_index(drop=True)
rest.to_parquet(OUT / "restaurants.parquet")
cells["restaurants"] = cells["cell"].map(rest.groupby("cell").size()).fillna(0).astype(int)
log(f"restaurants (OSM {FOOD_TAGS}): {len(rest):,}; by kind: {rest['kind'].value_counts().to_dict()}")
log(f"cells with at least one restaurant: {(cells['restaurants'] > 0).sum()}")

# 6. Travel time between every pair of cells over the road graph (directed, seconds, free flow).
src = cells["node_i"].values
D = dijkstra(A, directed=True, indices=np.unique(src))
uniq = {n: k for k, n in enumerate(np.unique(src))}
T = D[[uniq[n] for n in src]][:, src].astype(np.float32)
assert np.isfinite(T).all(), "some cell pairs are unreachable"
np.save(OUT / "travel_s.npy", T)
# Road distance along the shortest-length path (a close stand-in for the length of the fastest path).
DL = dijkstra(L, directed=True, indices=np.unique(src))
Dm = DL[[uniq[n] for n in src]][:, src].astype(np.float32)
np.save(OUT / "distance_m.npy", Dm)
log(f"road-distance matrix: median {np.median(Dm) / 1000:.1f} km, max {Dm.max() / 1000:.1f} km")
log(f"travel-time matrix: {T.shape}, median {np.median(T) / 60:.1f} min, max {T.max() / 60:.1f} min (free flow)")

pd.DataFrame(cells.drop(columns="geometry")).to_parquet(OUT / "cells.parquet")
cells[["cell", "pop", "restaurants", "geometry"]].to_file(OUT / "cells.gpkg", driver="GPKG")
log(f"build time: {time.time() - t0:.0f} s")
(OUT / "build_report.txt").write_text("\n".join(report) + "\n")
print("\n".join(report))
