"""Python previews of the G8 figures, marked PREVIEW (instructions of 2026-11-05, section 4). The paper figures render
in MATLAB on CT 315 from the same CSVs (`figures/forest_plot_extension.m`, `figures/w1_over_time_extension.m`).

Usage: python scripts/preview_figures.py <analysis_out> <w1_dir> <out_dir>
  analysis_out  contrasts.csv and contrasts_e2_fresh.csv of sim/analysis_extension.py
  w1_dir        w1_over_time_extension.csv of scripts/x9_w1_over_time.py
Writes preview_*.png and README.md in out_dir. Colors: the validated eight-slot categorical palette, one fixed slot per
model; nearest courier and the DQN (descriptive) in neutral greys; marker shapes as the second encoding.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ACK = "This research was supported by data provided by Meituan."
MARK = "PREVIEW (Python); the paper figure renders in MATLAB"
COLORS = {"foodmatch": "#2a78d6", "forecast": "#eb6834", "backpressure": "#1baf7a", "xu": "#eda100", "li": "#e87ba4",
          "auad": "#008300", "zhu": "#6250d6", "jusup": "#e34948", "nearest": "#52514e", "jahanshahi": "#7d7c78"}
REFERENCE = "#b9b8b3"   # nearest courier from the scattered start: lighter grey, dashed
SHAPES = {"foodmatch": "o", "forecast": "s", "backpressure": "D", "xu": "^", "li": "v", "auad": "P", "zhu": "X",
          "jusup": "*", "nearest": "o", "jahanshahi": "o"}
NAMES = {"nearest": "Nearest courier", "foodmatch": "FoodMatch (bundling off)", "forecast": "Forecast-aware matching",
         "backpressure": "Mirror backpressure", "xu": "Xu et al.", "li": "Li et al.", "jahanshahi": "Jahanshahi et al. (DQN)",
         "auad": "Auad et al.", "zhu": "Zhu et al. (100% obedient)", "jusup": "Jusup et al. (100% obedient)"}
NEW5, FROZEN3 = ["xu", "li", "auad", "zhu", "jusup"], ["foodmatch", "forecast", "backpressure"]
LEVELS = ["tight", "normal", "loose"]
Q1 = [(s, lvl) for s in ("scattered", "burst") for lvl in LEVELS]
Q2 = [(s, lvl) for s in ("big_cluster", "three_clusters", "mixed") for lvl in LEVELS] + [("meetup", "normal")]
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
ZOOM = (-1.5, 2.0)
plt.rcParams.update({"font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE})


def finish(fig, path, title, handles, labels, ncol=4):
    fig.suptitle(f"{title}\n{MARK}", fontsize=9, color=INK)
    fig.legend(handles, labels, loc="lower center", ncol=ncol, frameon=False, bbox_to_anchor=(0.5, 0.02))
    fig.text(0.99, 0.003, ACK, ha="right", va="bottom", fontsize=6, color=MUTED)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def axis(ax, cells, isp90):
    ax.axvline(0, color=INK, lw=0.8)
    if isp90:
        ax.axvline(1.0, color=MUTED, lw=0.8, ls=":")
    ax.set_yticks(range(1, len(cells) + 1), [f"{s.replace('_', ' ')}, {lvl}" for s, lvl in reversed(cells)])
    ax.set_ylim(0.4, len(cells) + 0.6)
    ax.grid(axis="x", color=GRID, lw=0.6)


def draw(ax, r, yy, color, shape, zoom, filled=True):
    lo, hi, m = r["lo"], r["hi"], r["mean"]
    if zoom and not (zoom[0] <= m <= zoom[1]):
        edge = zoom[0] if m < zoom[0] else zoom[1]
        ax.text(edge, yy, "◀" if m < zoom[0] else "▶", color=color, ha="center", va="center", fontsize=7)
        return None
    if zoom:                                            # an interval cut by the window ends in a small arrow
        if lo < zoom[0]:
            ax.text(zoom[0], yy, "<", color=color, ha="left", va="center", fontsize=6)
        if hi > zoom[1]:
            ax.text(zoom[1], yy, ">", color=color, ha="right", va="center", fontsize=6)
        lo, hi = max(lo, zoom[0]), min(hi, zoom[1])
    ax.hlines(yy, lo, hi, color=color, lw=1.2)
    return ax.plot(m, yy, shape, color=color, mfc=color if filled else SURFACE, ms=5, mew=1.0, ls="none")[0]


def forest(con, family, metric, cells, models, xlabel, path, title):
    R = con[(con.family == family) & (con.metric == metric)]
    isp90 = metric == "p90_c2d_min"
    fig, axes = plt.subplots(1, 2 if isp90 else 1, figsize=(10 if isp90 else 7, 1.6 + 0.42 * len(cells)), sharey=True,
                             squeeze=False)
    handles = {}
    for k, ax in enumerate(axes[0]):
        zoom = ZOOM if k == 1 else None
        for y, (s, lvl) in enumerate(cells):
            for i, m in enumerate(models):
                r = R[(R.scenario == s) & (R.level == lvl) & (R.model == m)]
                if r.empty:
                    continue
                r = r.iloc[0]
                yy = len(cells) - y + (i - (len(models) - 1) / 2) * 0.09
                h = draw(ax, r, yy, COLORS[m], SHAPES[m], zoom)
                if h is not None:
                    handles.setdefault(m, h)
                if not isp90:
                    ax.plot([-r["delta"]] * 2, [yy - 0.04, yy + 0.04], color=MUTED, lw=0.8, ls=":")
        axis(ax, cells, isp90)
        if zoom:
            ax.set_xlim(*zoom)
            ax.set_title("Zoom, -1.5 to +2 min (triangles: means outside; < >: intervals cut)", fontsize=8, color=MUTED)
    fig.supxlabel(f"{xlabel}, model minus nearest courier (lower is better)", y=0.11, fontsize=8)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.86, bottom=0.2)
    ms = [m for m in models if m in handles]
    finish(fig, path, title, [handles[m] for m in ms], [NAMES[m] for m in ms])


def fresh_figure(con, fr, path):
    cells = Q2
    fig, axes = plt.subplots(1, 2, figsize=(10, 1.6 + 0.42 * len(cells)), sharey=True)
    handles = {}
    for ax, metric, xl in ((axes[0], "w1_rule_60min_after_min", "W1 over the first 60 min (min)"),
                           (axes[1], "p90_c2d_min", "p90 order to door (min)")):
        for y, (s, lvl) in enumerate(cells):
            for i, m in enumerate(FROZEN3):
                base = len(cells) - y + (i - 1) * 0.22
                for off, src, filled, key in ((-0.05, con[con.family == "E2"], False, "frozen"), (0.05, fr, True, "fresh")):
                    r = src[(src.scenario == s) & (src.level == lvl) & (src.model == m) & (src.metric == metric)]
                    if r.empty:
                        continue
                    h = draw(ax, r.iloc[0], base + off, COLORS[m], SHAPES[m], None, filled)
                    handles.setdefault((m, key), h)
        axis(ax, cells, metric == "p90_c2d_min")
        ax.set_xlabel(xl + ", model minus nearest courier", fontsize=8)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.86, bottom=0.22)
    keys = [k for k in [(m, s) for m in FROZEN3 for s in ("frozen", "fresh")] if k in handles]
    labels = [f"{NAMES[m]}, {'seeds 1001 on (hollow)' if s == 'frozen' else 'fresh block 5001 on (filled)'}" for m, s in keys]
    finish(fig, path, "Frozen three on Q2: pre-registered seeds against the fresh seed block (R4); p90 on the starts "
           "exists only on the fresh block (E2 takes it from F1)", [handles[k] for k in keys], labels, ncol=2)


def w1_figure(T, path):
    arms = [["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi"], ["nearest", "auad"],
            ["nearest", "zhu", "jusup"]]
    arm_names = ["Arm A: which courier", "Arm B: when to assign", "Arm C: moving idle couriers (100% obedient)"]
    starts = [("big_cluster", "Big cluster at 17:00"), ("meetup", "Meet-up at 19:00")]
    ref = T[T.start == "reference_scattered"]
    top = 5 * -(-T.hi.max() // 5)
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.4), sharex=True, sharey=True)
    handles = {}
    for r, (s, sname) in enumerate(starts):
        for c, models in enumerate(arms):
            ax = axes[r, c]
            h = ax.plot(17 + ref.minute / 60, ref["mean"], ls="--", color=REFERENCE, lw=1.2)[0]
            handles.setdefault("ref", h)
            for m in models:
                S = T[(T.start == s) & (T.model == m)]
                x = 17 + S.minute / 60
                ax.fill_between(x, S.lo, S.hi, color=COLORS[m], alpha=0.12, lw=0)
                h = ax.plot(x, S["mean"], color=COLORS[m], lw=1.5, ls=":" if m == "jahanshahi" else "-")[0]
                handles.setdefault(m, h)
            ax.set_xlim(17, 21)
            ax.set_ylim(0, top)
            ax.set_xticks(range(17, 22), [f"{h}:00" for h in range(17, 22)])
            ax.grid(color=GRID, lw=0.6)
            if r == 0:
                ax.set_title(arm_names[c], fontsize=8, color=INK)
            if c == 0:
                ax.set_ylabel(f"{sname}\nW1 (min of riding)")
            if r == 1:
                ax.set_xlabel("Time of day")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.88, bottom=0.2, hspace=0.15, wspace=0.06)
    keys = [k for k in ["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu",
                        "jusup", "ref"] if k in handles]
    labels = [NAMES[k] if k != "ref" else "Nearest courier, scattered start" for k in keys]
    finish(fig, path, "W1 over the evening, normal supply, fitted behavior (mean and 95% band over seeds)",
           [handles[k] for k in keys], labels, ncol=4)


def main():
    a, w, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)
    con = pd.read_csv(a / "contrasts.csv")
    fr = pd.read_csv(a / "contrasts_e2_fresh.csv")
    forest(con, "E1", "w1_rule_min", Q1, NEW5, "W1 difference (min)", out / "preview_forest_e1_w1.png",
           "E1 (Q1, prevent): W1; dotted ticks: the smallest effect, 10% of nearest courier's W1")
    forest(con, "E1", "p90_c2d_min", Q1, NEW5, "p90 order to door difference (min)", out / "preview_forest_e1_p90.png",
           "E1 (Q1, prevent): p90 order to door; dotted line: +1 min")
    forest(con, "E2", "w1_rule_60min_after_min", Q2, FROZEN3 + NEW5, "W1 over the first 60 min, difference (min)",
           out / "preview_forest_e2_w1_60.png", "E2 (Q2, undo): W1 over the 60 min after the cluster appears; dotted ticks: "
           "the smallest effect")
    forest(con, "E2", "p90_c2d_min", Q2, FROZEN3 + NEW5, "p90 order to door difference (min)",
           out / "preview_forest_e2_p90.png", "E2 (Q2, undo): p90 order to door; frozen three only on the meet-up "
           "(their start cells are in F1)")
    fresh_figure(con, fr, out / "preview_forest_e2_fresh_frozen3.png")
    w1_figure(pd.read_csv(w / "w1_over_time_extension.csv"), out / "preview_w1_over_time_extension.png")
    (out / "README.md").write_text(
        "# G8 figures: previews\n\n" + ACK + "\n\nThese PNGs are Python previews, marked PREVIEW. The paper figures "
        "render in MATLAB on CT 315 from the same CSVs (`figures/forest_plot_extension.m` reads the analysis's "
        "`contrasts.csv`; `figures/w1_over_time_extension.m` reads `w1_over_time_extension.csv`). Colors: one fixed "
        "slot per model from a validated colorblind-safe palette, with marker shapes as a second cue.\n")


if __name__ == "__main__":
    main()
