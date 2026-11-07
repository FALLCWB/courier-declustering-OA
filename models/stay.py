"""Exploratory policy `stay` (package C, part 2; preregistration-addendum-C.md): nearest-courier assignment, and every
obedient idle courier stays where it is unless dispatched. It is an arm C policy with an empty command set: the engine
treats a policy with `relocate` as arm C, and obedient couriers make no idle decision of their own, so at 100% obedience
nobody moves while idle and at 0% obedience it equals nearest courier."""
from sim.core.policies import NearestIdle


class StayPolicy:
    name = "stay"

    def __init__(self, seed=0):
        self._nearest = NearestIdle()

    def assign(self, v):
        return self._nearest.assign(v)

    def relocate(self, v):
        return []
