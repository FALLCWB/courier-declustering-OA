"""A small multilayer perceptron in numpy (ReLU hidden layers, linear output) with Adam, for the learned models of the
extension (no deep-learning dependency on FE-SIM-1). Tested against finite differences in tests/test_nn.py.
"""
import numpy as np


class MLP:
    def __init__(self, sizes, seed=0, lr=1e-3):
        rng = np.random.default_rng(seed)
        self.W = [rng.normal(0.0, np.sqrt(2.0 / a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]   # He init
        self.b = [np.zeros(b) for b in sizes[1:]]
        self.lr, self.t = lr, 0
        self.m = [np.zeros_like(p) for p in self.W + self.b]
        self.v = [np.zeros_like(p) for p in self.W + self.b]

    def forward(self, x, keep=False):
        acts = [np.asarray(x, float)]
        h = acts[0]
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            h = h @ W + b
            if i < len(self.W) - 1:
                h = np.maximum(h, 0.0)
            acts.append(h)
        if keep:
            self._acts = acts
        return h

    def grads(self, dout):
        """Gradients of sum(dout * output) for the last forward(keep=True)."""
        acts, gW, gb = self._acts, [], []
        d = np.asarray(dout, float)
        for i in range(len(self.W) - 1, -1, -1):
            gW.insert(0, acts[i].T @ d)
            gb.insert(0, d.sum(axis=0))
            if i > 0:
                d = (d @ self.W[i].T) * (acts[i] > 0)
        return gW, gb

    def step(self, gW, gb, b1=0.9, b2=0.999, eps=1e-8):
        self.t += 1
        for i, (p, g) in enumerate(zip(self.W + self.b, gW + gb)):
            self.m[i] = b1 * self.m[i] + (1 - b1) * g
            self.v[i] = b2 * self.v[i] + (1 - b2) * g * g
            mh, vh = self.m[i] / (1 - b1 ** self.t), self.v[i] / (1 - b2 ** self.t)
            p -= self.lr * mh / (np.sqrt(vh) + eps)

    def copy_from(self, other):
        self.W = [w.copy() for w in other.W]
        self.b = [b.copy() for b in other.b]

    def state(self):
        return {**{f"W{i}": w for i, w in enumerate(self.W)}, **{f"b{i}": b for i, b in enumerate(self.b)}}

    @classmethod
    def from_state(cls, st):
        n = sum(1 for k in st if k.startswith("W"))
        net = cls([st["W0"].shape[0]] + [st[f"W{i}"].shape[1] for i in range(n)])
        net.W = [np.asarray(st[f"W{i}"], float) for i in range(n)]
        net.b = [np.asarray(st[f"b{i}"], float) for i in range(n)]
        return net
