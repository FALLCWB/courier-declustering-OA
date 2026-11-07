"""Map video of simulated episodes (plan decision 11), rendered with matplotlib and piped to ffmpeg on FE-SIM-1.

Couriers: blue when idle, orange on the way to a pickup or waiting for the food, red when carrying food. Restaurants in
grey, with a light heat layer of the pickups expected in the next 30 min. One panel per episode (the final video has
two, nearest-courier and the best model, same start and seed), a W1 strip below, 160x speed at 30 fps, 1920x1080.
Positions move in a straight line between cell centres along each recorded leg (`Simulator(trace=True)`); the base
map is the OSM road graph of the city build, with no tile servers.
"""
import subprocess
from pathlib import Path

import numpy as np

COLORS = {"idle": "#2b6cb0", "pickup": "#ed8936", "loaded": "#c53030"}
STATE_OF_LEG = {"idle": "idle", "to_pickup": "pickup", "wait": "pickup", "loaded": "loaded", "drop": "loaded"}
ACK = "This research was supported by data provided by Meituan."


def road_segments(folder):
    """(n, 2, 2) lng/lat segments of the road graph, cached next to it."""
    cache = Path(folder) / "road_segments.npz"
    if cache.exists():
        return np.load(cache)["seg"]
    import osmnx as ox
    G = ox.load_graphml(Path(folder) / "roads.graphml")
    xy = {n: (d["x"], d["y"]) for n, d in G.nodes(data=True)}
    seg = np.array([[xy[u], xy[v]] for u, v in G.edges()], dtype=np.float32)
    np.savez_compressed(cache, seg=seg)
    return seg


def positions(city, legs, start, frame_t):
    """Courier positions (lng, lat) and state names at each frame time. legs: (c, t0, t1, a, b, kind) tuples."""
    n, F = len(start), len(frame_t)
    lng, lat = np.empty((F, n)), np.empty((F, n))
    state = np.full((F, n), "idle", dtype=object)
    by_c = [[] for _ in range(n)]
    for leg in legs:
        by_c[leg[0]].append(leg)
    for c in range(n):
        L = sorted(by_c[c], key=lambda x: (x[1], x[2]))
        if not L:
            lng[:, c], lat[:, c] = city.lng[start[c]], city.lat[start[c]]
            continue
        t0 = np.array([x[1] for x in L])
        t1 = np.array([x[2] for x in L])
        a = np.array([x[3] for x in L])
        b = np.array([x[4] for x in L])
        kind = np.array([STATE_OF_LEG[x[5]] for x in L], dtype=object)
        i = np.searchsorted(t0, frame_t, side="right") - 1
        before = i < 0
        i = np.maximum(i, 0)
        active = (frame_t <= t1[i]) & ~before
        span = np.maximum(t1[i] - t0[i], 1e-9)
        f = np.where(active, np.clip((frame_t - t0[i]) / span, 0, 1), 1.0)
        ca, cb = np.where(before, start[c], a[i]), np.where(before, start[c], b[i])
        lng[:, c] = city.lng[ca] + f * (city.lng[cb] - city.lng[ca])
        lat[:, c] = city.lat[ca] + f * (city.lat[cb] - city.lat[ca])
        state[:, c] = np.where(active, kind[i], "idle")
    return lng, lat, state


def render(path, city, road_seg, panels, rest_weight, expected_fn, start_s=0.0, end_s=4 * 3600.0, speed=160.0,
           fps=30, clock0_h=17, title=""):
    """panels: list of dicts with name, legs, start (cells), snapshots (list of rows with t and w1_min)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    frame_t = np.arange(start_s, end_s, speed / fps)
    pos = [positions(city, p["legs"], np.asarray(p["start"]), frame_t) for p in panels]
    k = len(panels)
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    gs = fig.add_gridspec(2, k, height_ratios=[5, 1], hspace=0.12, wspace=0.03, left=0.02, right=0.98, top=0.93, bottom=0.07)
    aspect = 1 / np.cos(np.radians(city.lat.mean()))
    lng_lim = (city.lng.min() - 0.005, city.lng.max() + 0.005)
    lat_lim = (city.lat.min() - 0.005, city.lat.max() + 0.005)
    heat0 = expected_fn(start_s)
    scat, heat = [], []
    for j, p in enumerate(panels):
        ax = fig.add_subplot(gs[0, j])
        ax.add_collection(LineCollection(road_seg, colors="#d9d9d9", linewidths=0.25, zorder=0))
        h = ax.scatter(city.lng, city.lat, s=22, c=heat0, cmap="Greens", vmin=0, vmax=max(heat0.max(), 1e-9), alpha=0.35,
                       linewidths=0, zorder=1)
        m = rest_weight > 0
        ax.scatter(city.lng[m], city.lat[m], s=1 + 3 * np.sqrt(rest_weight[m] / rest_weight[m].max()), c="#7f7f7f",
                   linewidths=0, zorder=2)
        s = ax.scatter(pos[j][0][0], pos[j][1][0], s=5, c=[COLORS[x] for x in pos[j][2][0]], linewidths=0, zorder=3)
        ax.set_xlim(*lng_lim), ax.set_ylim(*lat_lim), ax.set_aspect(aspect)
        ax.set_xticks([]), ax.set_yticks([])
        ax.set_title(p["name"], fontsize=15)
        scat.append(s)
        heat.append(h)
    axs = fig.add_subplot(gs[1, :])
    for p in panels:
        t = np.array([r["t"] for r in p["snapshots"]])
        w = np.array([r["w1_min"] for r in p["snapshots"]])
        axs.plot(clock0_h + t / 3600, w, lw=1.6, label=p["name"])
    axs.set_xlim(clock0_h + start_s / 3600, clock0_h + end_s / 3600)
    if end_s > 3.5 * 3600:                                 # G4 verdict ruling 6: state the shrinking window
        axs.axvspan(clock0_h + 3.5, clock0_h + 4.0, color="#eeeeee", zorder=0)
        axs.text(clock0_h + 3.52, axs.get_ylim()[1] * 0.92, "after 20:30 the 30-min demand window\nshrinks (no orders after 21:00)",
                 fontsize=9, va="top", color="#555555")
    axs.set_ylabel("W1 (min)", fontsize=12)
    axs.set_xlabel("Time of day (h)", fontsize=12)
    cursor = axs.axvline(clock0_h + start_s / 3600, color="k", lw=1)
    handles = [plt.Line2D([], [], marker="o", ls="", color=v, label=n) for n, v in
               [("idle", COLORS["idle"]), ("to pickup or waiting", COLORS["pickup"]), ("carrying food", COLORS["loaded"])]]
    fig.legend(handles=handles + axs.get_legend_handles_labels()[0], loc="lower center", ncol=3 + k, frameon=False,
               fontsize=12)
    clock = fig.suptitle("", fontsize=16)
    fig.text(0.99, 0.005, ACK, ha="right", fontsize=9, color="#555555")
    W, H = fig.canvas.get_width_height()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f, t in enumerate(frame_t):
        for j in range(k):
            scat[j].set_offsets(np.column_stack([pos[j][0][f], pos[j][1][f]]))
            scat[j].set_color([COLORS[x] for x in pos[j][2][f]])
            if f % fps == 0:
                e = expected_fn(t)
                heat[j].set_array(e)
        cursor.set_xdata([clock0_h + t / 3600] * 2)
        hh = clock0_h + int(t // 3600)
        clock.set_text(f"{title}   {hh:02d}:{int(t % 3600 // 60):02d}")
        fig.canvas.draw()
        proc.stdin.write(np.asarray(fig.canvas.buffer_rgba()).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed")
    plt.close(fig)
    return len(frame_t)


def stills(path_fmt, city, road_seg, panels, rest_weight, expected_fn, minutes=(0, 30, 60, 120, 240), **kw):
    """PNG stills at the given minutes (E8): one 1-frame render per minute, saved with matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = []
    for m in minutes:
        t = min(m * 60.0, 4 * 3600.0 - 1)
        fig, axes = plt.subplots(1, len(panels), figsize=(9.6 * len(panels), 10.8), dpi=100, squeeze=False)
        for ax, p in zip(axes[0], panels):
            lng, lat, st = positions(city, p["legs"], np.asarray(p["start"]), np.array([t]))
            from matplotlib.collections import LineCollection
            ax.add_collection(LineCollection(road_seg, colors="#d9d9d9", linewidths=0.25, zorder=0))
            ax.scatter(city.lng, city.lat, s=22, c=expected_fn(t), cmap="Greens", alpha=0.35, linewidths=0, zorder=1)
            ax.scatter(lng[0], lat[0], s=6, c=[COLORS[x] for x in st[0]], linewidths=0, zorder=3)
            ax.set_aspect(1 / np.cos(np.radians(city.lat.mean())))
            ax.set_xticks([]), ax.set_yticks([])
            ax.set_title(f"{p['name']}, {17 + int(t // 3600):02d}:{int(t % 3600 // 60):02d}", fontsize=14)
        handles = [plt.Line2D([], [], marker="o", ls="", color=v, label=n) for n, v in
                   [("idle", COLORS["idle"]), ("to pickup or waiting", COLORS["pickup"]), ("carrying food", COLORS["loaded"])]]
        fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=12)
        fig.text(0.99, 0.01, ACK, ha="right", fontsize=8, color="#555555")
        f = str(path_fmt).format(minute=m)
        fig.savefig(f, dpi=100, bbox_inches="tight")
        plt.close(fig)
        out.append(f)
    return out
