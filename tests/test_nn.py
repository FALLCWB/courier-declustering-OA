"""The numpy MLP: gradients against finite differences, and Adam fitting a known function."""
import numpy as np

from sim.nn import MLP


def test_gradients_match_finite_differences():
    net = MLP([3, 5, 4, 1], seed=1)
    x = np.random.default_rng(2).normal(size=(7, 3))
    w = np.random.default_rng(3).normal(size=(7, 1))
    net.forward(x, keep=True)
    gW, gb = net.grads(w)
    eps = 1e-6
    for li in range(len(net.W)):
        for idx in [(0, 0), (1, 0), (2, 0)] if net.W[li].shape[0] > 2 else [(0, 0)]:
            if idx[0] >= net.W[li].shape[0] or idx[1] >= net.W[li].shape[1]:
                continue
            old = net.W[li][idx]
            net.W[li][idx] = old + eps
            up = (net.forward(x) * w).sum()
            net.W[li][idx] = old - eps
            dn = (net.forward(x) * w).sum()
            net.W[li][idx] = old
            assert abs((up - dn) / (2 * eps) - gW[li][idx]) < 1e-5


def test_adam_fits_a_decreasing_line():
    rng = np.random.default_rng(4)
    net = MLP([1, 16, 1], seed=5, lr=1e-2)
    x = rng.uniform(0, 1, (256, 1))
    y = 3.0 - 2.0 * x
    for _ in range(1500):
        out = net.forward(x, keep=True)
        gW, gb = net.grads(2 * (out - y) / len(x))
        net.step(gW, gb)
    assert np.abs(net.forward(x) - y).max() < 0.1
