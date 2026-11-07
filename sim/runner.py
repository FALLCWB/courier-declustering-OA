"""One episode of the experiment: scenario x supply level x seed x behavior setting x model.

Every model sees the same city, orders, start cells, preferred areas, full-time flags and travel-time factors for a
given (scenario, level, seed): common random numbers. The episode-level W1 follows the few-idle rule frozen in
`scenarios/manifest.json` (S4).
"""
import json
from pathlib import Path

import numpy as np

from sim.config import load_calibration, make_demand, make_params
from sim.core.behavior import Behavior, BehaviorParams
from sim.core.city import load
from sim.core.engine import Fleet, Simulator
from sim.core.metrics import summarize
from sim.core.policies import NearestIdle
from sim import scenarios as sc

ROOT = Path(__file__).resolve().parents[1]
SWEEP = [0.0, 0.25, 0.5, 0.75, 1.0]          # plan decision 8: return probability sweep (secondary family)


def model(name, **kw):
    if name == "nearest":
        return NearestIdle()
    from models import MODELS
    return MODELS[name](**kw)


class Experiment:
    def __init__(self, root=ROOT, manifest=None, layout=None):
        """layout: restaurant layout (s0 to s4 or osm); the manifest's main layout when None (family F3 uses others)."""
        self.root = Path(root)
        self.cal = load_calibration()
        self.man = manifest or json.loads((self.root / "scenarios/manifest.json").read_text())
        self.layout = layout or self.man["layout"]
        bp = BehaviorParams().__dict__
        if any(bp[k] != v for k, v in self.man["behavior"].items()):
            raise ValueError("BehaviorParams defaults differ from scenarios/manifest.json")
        if bp["no_hotspot"]:                                  # options added later must default to the frozen behavior
            raise ValueError("BehaviorParams.no_hotspot must default to False")
        self.city = load(self.root / "sim/city/curitiba", layout=self.layout)
        from sim.blas import threads
        self.blas_threads = threads()                        # recorded in every row (sim/blas.py)
        self.base = make_demand(self.city, self.cal, orders_4h=self.man["orders_4h"])
        self.hubs = [int(self.city.cell_index[c]) for c in self.man["cluster"]["hub_cells"]]
        self.burst_zone = int(self.city.zone[self.city.cell_index[self.man["burst"]["zone_rep_cell"]]])
        # Only the burst changes the demand; the other starts share the base demand object (memory per worker).
        self.demand = {s: (sc.scenario_demand(self.city, self.cal, s, self.man["orders_4h"], self.burst_zone)
                           if s == "burst" else self.base) for s in self.man["scenarios"]}
        meet = self.man.get("meetup")                         # extension scenario: scattered start plus a 19:00 meet-up
        self.meetup = {}
        if meet:                                              # 'meetup': the manifest's variant (jump, primary);
            for name, jump in (("meetup", bool(meet.get("jump", False))), ("meetup_ride", False)):  # 'meetup_ride': ride
                self.demand[name] = self.base
                self.meetup[name] = dict(meetup_s=float(meet["time_s"]), meetup_share=float(meet["share"]),
                                         meetup_cell=int(self.city.cell_index[meet["cell"]]), meetup_jump=jump)
            med = self.man.get("meetup_median")              # 'meetup_median': the exploratory point (G7 verdict E2(c)),
            if med:                                           # with the primary meet-up's time, share and jump
                self.demand["meetup_median"] = self.base
                self.meetup["meetup_median"] = dict(self.meetup["meetup"], meetup_cell=int(self.city.cell_index[med["cell"]]))

    def behavior_params(self, setting):
        """'fitted', or 'p<value>' for the return-probability sweep with the other fitted values; a '-nohotspot' suffix
        drops the hotspot alternative (exploratory, G4 verdict V3). Package C (preregistration-addendum-C.md): 'indep'
        has the fitted values (its homes differ, see episode); 'ashkrof' sets the part-time coefficient to 0 with the
        stay constant and return probability recalibrated (sim/params/behavior_ashkrof.json)."""
        bp = BehaviorParams()
        base, _, flag = setting.partition("-")
        if base in ("ashkrof", "ashkrofw"):                # ashkrofw: the wide-grid recalibration (DECISIONS.md)
            name = "behavior_ashkrof.json" if base == "ashkrof" else "behavior_ashkrof_wide.json"
            fit = json.loads((self.root / "sim/params" / name).read_text())
            bp.p_return = float(fit["p_return"])
            bp.coef = {**bp.coef, "asc_stay": float(fit["asc_stay"]), "part_time_stay": 0.0}
        elif base not in ("fitted", "indep", "resid"):
            bp.p_return = float(base[1:])
        if flag == "nohotspot":
            bp.no_hotspot = True
        elif flag:
            raise ValueError(f"unknown behavior setting {setting}")
        return bp

    def episode(self, scenario, level, seed, model_name, setting="fitted", trace=False, model_kw=None, scale=1.0,
                time_mult=1.0, obedience=None, light=False, demand_noise=None):
        """scale and time_mult serve the D1 robustness family (fleet and orders x0.5; travel times x0.75).
        obedience: share of couriers that follow an arm C model's relocation commands, drawn once per courier from the
        seed (nested: a courier obedient at 25% is obedient at 50%); None for models without commands.
        light: training runs that read no concentration metric take one snapshot (at 17:00) instead of one per minute;
        the simulation is unchanged (test_fewer_snapshots_leave_the_simulation_unchanged) and every concentration
        field of the row is NaN."""
        city, n = self.city, int(round(self.man["fleets"][level] * scale))
        orders_4h = self.man["orders_4h"] * scale
        demand = self.demand[scenario] if scale == 1.0 else sc.scenario_demand(city, self.cal, scenario, orders_4h,
                                                                              self.burst_zone)
        base = self.base if scale == 1.0 else make_demand(city, self.cal, orders_4h=orders_4h)
        params = make_params(self.cal, speed_factor=self.cal["speed_factor"] * time_mult,
                             soon_s=self.man["soon_s"] if self.man["few_idle_rule"] == "soon_free" else 0.0,
                             **self.meetup.get(scenario, {}), **({"snapshot_s": 4 * 3600.0} if light else {}))
        orders = demand.sample(seed)
        start = sc.starts(city, base, "scattered" if scenario in self.meetup else scenario, n, seed, self.hubs)
        obedient = None
        if obedience is not None:
            obedient = np.random.default_rng(np.random.SeedSequence([seed, 11])).uniform(size=n) < obedience
        if setting == "indep":
            home = sc.indep_homes(base.expected_pickups(0, 1800), n, seed)
        elif setting == "resid":                          # C6: homes where the customers are, 17:00 to 21:00
            home = sc.indep_homes(base.expected_dropoffs(0, 14400.0), n, seed, tag=42)
        else:
            home = start.copy()
        fleet = Fleet(start=start, home=home, full_time=sc.full_time(n, seed), obedient=obedient)
        beh = Behavior(city, self.behavior_params(setting), base.pickup_share[0], params.speed_factor, seed, n)
        pol = model(model_name, **({} if model_name == "nearest" else {"seed": seed, **(model_kw or {})}))
        if demand_noise:                                  # package C part 4: the policy reads noisy expected demand
            from sim.noise import NoisyDemand, noisy_input, zone_factors
            pol = noisy_input(pol, NoisyDemand(demand, city.zone, zone_factors(city.n_zones, seed, demand_noise)))
        sim = Simulator(city, demand, orders, fleet, pol, beh, params, seed=seed, trace=trace).run()
        row = {"scenario": scenario, "level": level, "seed": seed, "model": model_name, "behavior": setting, "layout": self.layout,
               "couriers": n, "scale": scale, "time_mult": time_mult, "obedience": obedience, "blas_threads": self.blas_threads,
               **summarize(sim)}
        row["w1_rule_min"] = rule_w1(sim.snapshots, self.man["few_idle_rule"])
        row["w1_rule_first30_min"] = rule_w1([s for s in sim.snapshots if s["t"] < 1800], self.man["few_idle_rule"])
        key = "w1_soon_min" if self.man["few_idle_rule"] == "soon_free" else "w1_min"
        row["w1_rule_nan_snapshots"] = int(sum(1 for s in sim.snapshots if not np.isfinite(s.get(key, np.nan))))
        inside = sim.orders.placed < params.horizon_s
        end = params.horizon_s + params.drain_s                 # an event that never happened counts at the drain's end (C2)
        pickup = np.where(np.isnan(sim.o_pickup) | (sim.o_pickup > end), end, sim.o_pickup)[inside]
        wait = np.maximum(pickup - sim.orders.ready[inside], 0.0)
        row["food_wait_mean_min"] = float(wait.mean() / 60)
        row["food_wait_p90_min"] = float(np.percentile(wait, 90) / 60)
        assigned = np.where(np.isnan(sim.o_assigned), end, sim.o_assigned)[inside]
        row["unassigned_over_30min_share"] = float(((assigned - sim.orders.placed[inside]) > 1800).mean())
        row["w1_idle_weighted_min"] = rule_w1(sim.snapshots, "idle_weighted")      # secondary (C3)
        # Extension Q2: W1 over the 60 min after the cluster appears (17:00 for the starts, the meet-up time otherwise),
        # and the per-minute W1 series from which the time to undo is read against the scattered start.
        t0 = params.meetup_s if scenario in self.meetup else 0.0
        row["w1_rule_60min_after_min"] = rule_w1([s for s in sim.snapshots if t0 <= s["t"] < t0 + 3600.0],
                                                 self.man["few_idle_rule"])
        row["w1_rule_series"] = [float(s.get(key, np.nan)) for s in sim.snapshots]
        if light:
            for k in [k for k in row if k.startswith(("w1", "gini_idle", "tv", "uncovered", "no_idle"))]:
                row[k] = np.nan
        for k, val in getattr(pol, "counts", {}).items():                         # closest-courier fallbacks (C3)
            if k != "orders":
                row[f"fallback_{k}_share"] = val / max(pol.counts["orders"], 1)
        for k, val in getattr(pol, "events", {}).items():                         # model events (Zhu's empty-part rule)
            row[f"events_{k}"] = int(val)
        return row, sim


def rule_w1(snaps, rule):
    """Episode W1 under the few-idle rule: idle-weighted mean of snapshot W1, or plain mean of the soon-free W1."""
    if not snaps:
        return np.nan
    if rule == "idle_weighted":
        w = np.array([s["n_idle"] for s in snaps], float)
        x = np.array([s["w1_min"] for s in snaps], float)
        ok = np.isfinite(x) & (w > 0)
        return float((x[ok] * w[ok]).sum() / w[ok].sum()) if ok.any() else np.nan
    return float(np.nanmean([s["w1_soon_min"] for s in snaps]))
