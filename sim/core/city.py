"""City model used by the simulator: cells, road travel times, neighbors, zones, demand weights."""
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

EARTH_M = 6371000.0


@dataclass
class City:
    cell: np.ndarray       # cell ids, [N]
    lat: np.ndarray        # cell centre latitude, [N]
    lng: np.ndarray        # cell centre longitude, [N]
    T: np.ndarray          # free-flow road travel time from row cell to column cell, seconds, [N, N]
    Dm: np.ndarray         # road distance from row cell to column cell, metres, [N, N]
    nbr: np.ndarray        # neighbor cell indices, [N, K], -1 where absent
    pop: np.ndarray        # residents per cell, [N]
    rest: np.ndarray       # restaurants per cell, [N]
    zone: np.ndarray       # zone index of each cell (H3 resolution 8 parent), [N]
    zone_rep: np.ndarray   # representative cell of each zone, [Z]
    centre: int            # index of the cell at the city centre

    @property
    def n(self):
        return len(self.cell)

    @property
    def n_zones(self):
        return len(self.zone_rep)

    @property
    def cell_index(self):
        """Cell id to row index."""
        if not hasattr(self, "_cell_index"):
            self._cell_index = {c: i for i, c in enumerate(self.cell)}
        return self._cell_index

    def set_intra_cell(self, t_s, d_m):
        """Give trips that start and end in the same cell a travel time and road distance (the diagonal)."""
        np.fill_diagonal(self.T, t_s)
        np.fill_diagonal(self.Dm, d_m)

    def straight_m(self, i, j):
        """Great-circle distance in metres between cell centres (vectorized over j)."""
        p1, p2 = np.radians(self.lat[i]), np.radians(self.lat[j])
        dl = np.radians(self.lng[j] - self.lng[i])
        a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
        return 2 * EARTH_M * np.arcsin(np.sqrt(a))


def load(folder, centre_latlng=(-25.4295, -49.2713), layout=None, intra_cell=True):
    """Load the city built by sim/city/build.py. The default centre is Praca Tiradentes, Curitiba.

    `layout` picks the restaurants per cell: None keeps the OpenStreetMap count of the build; "registry", "s0" to
    "s4" or "osm" read sim/city/curitiba/restaurant_layouts.parquet (sim/city/restaurants.py). "s0" is the main layout.
    `intra_cell` gives same-cell trips a positive time and distance (False reproduces the handed-over sanity run).
    """
    import h3

    folder = Path(folder)
    cells = pd.read_parquet(folder / "cells.parquet")
    if layout is not None:
        lay = pd.read_parquet(folder / "restaurant_layouts.parquet")
        assert (lay["cell"].to_numpy() == cells["cell"].to_numpy()).all(), "layout cells differ from the city grid"
        cells["restaurants"] = lay[layout].to_numpy()
    ids = cells["cell"].to_numpy()
    pos = {c: i for i, c in enumerate(ids)}
    nbr = np.full((len(ids), 6), -1, dtype=np.int32)
    for i, c in enumerate(ids):
        ring = [pos[x] for x in h3.grid_ring(c, 1) if x in pos]
        nbr[i, : len(ring)] = ring
    parents = cells["parent8"].to_numpy()
    zones, zone = np.unique(parents, return_inverse=True)
    zone_rep = np.empty(len(zones), dtype=np.int32)
    for z, p in enumerate(zones):
        child = h3.cell_to_center_child(p, 9)
        members = np.flatnonzero(zone == z)
        zone_rep[z] = pos[child] if child in pos else members[0]
    centre = pos.get(h3.latlng_to_cell(*centre_latlng, 9))
    city = City(cell=ids, lat=cells["lat"].to_numpy(), lng=cells["lng"].to_numpy(),
                T=np.load(folder / "travel_s.npy"), Dm=np.load(folder / "distance_m.npy"),
                nbr=nbr, pop=cells["pop"].to_numpy(float), rest=cells["restaurants"].to_numpy(float),
                zone=zone.astype(np.int32), zone_rep=zone_rep, centre=int(centre))
    if intra_cell:
        city.set_intra_cell(*intra_cell_trip(city, h3.average_hexagon_edge_length(9, unit="m")))
    return city


def hex_points(n, rng):
    """n points drawn uniformly in a regular hexagon of side 1 centred at the origin, shape [n, 2]."""
    pts, got = [], 0
    while got < n:
        xy = rng.uniform(-1, 1, (2 * n + 16, 2))
        x, y = np.abs(xy[:, 0]), np.abs(xy[:, 1])
        xy = xy[(y <= np.sqrt(3) / 2) & (np.sqrt(3) * x + y <= np.sqrt(3))]
        pts.append(xy)
        got += len(xy)
    return np.concatenate(pts)[:n]


def hex_mean_distance(n=200000, seed=0):
    """Mean distance between two points drawn uniformly in a regular hexagon of side 1 (Monte Carlo, about 0.8262)."""
    p = hex_points(2 * n, np.random.default_rng(seed))
    return float(np.linalg.norm(p[:n] - p[n:], axis=1).mean())


def intra_cell_trip(city, edge_m):
    """Travel time and road distance of a trip inside one cell: the mean straight distance between two random points
    of the hexagon, times the median detour of neighbor-cell trips, at the median speed of neighbor-cell trips."""
    i = np.repeat(np.arange(city.n), city.nbr.shape[1])
    j = city.nbr.ravel()
    i, j = i[j >= 0], j[j >= 0]
    ok = (city.T[i, j] > 0) & (city.Dm[i, j] > 0)      # neighbors snapped to the same road node have zero time
    i, j = i[ok], j[ok]
    straight = city.straight_m(i, j)
    detour = float(np.median(city.Dm[i, j] / straight))
    speed = float(np.median(city.Dm[i, j] / city.T[i, j]))
    d_m = hex_mean_distance() * edge_m * detour
    return d_m / speed, d_m


def toy_line(n, hop_s=60.0, hop_m=300.0, pop=None, rest=None):
    """A city of n cells on a line, for tests: travel time and distance grow with |i - j|."""
    idx = np.arange(n)
    gap = np.abs(idx[:, None] - idx[None, :]).astype(np.float32)
    nbr = np.stack([idx - 1, idx + 1], axis=1).astype(np.int32)
    nbr[nbr >= n] = -1
    return City(cell=idx.astype(str), lat=np.full(n, -25.43), lng=-49.27 + idx * hop_m / 100000.0,
                T=gap * hop_s, Dm=gap * hop_m, nbr=nbr,
                pop=np.ones(n) if pop is None else np.asarray(pop, float),
                rest=np.ones(n) if rest is None else np.asarray(rest, float),
                zone=idx.astype(np.int32), zone_rep=idx.astype(np.int32), centre=n // 2)
