# Part 1 results, untrained models (results)

This research was supported by data provided by Meituan.

Episodes: 9,840; 30 seeds in every cell and model; undelivered orders at the drain's end: 104. The smallest W1 effect of F3 and F4 cells, which have no pilot, uses the nearest-courier mean of their own runs.
Contrasts: model minus nearest courier, paired by seed; 95% percentile bootstrap intervals (10,000 resamples); two-sided paired t-test p-values, Holm within each family.

## F1 joint reading (cells per class and model)

| Model | declusters at no delivery cost | does not decluster |
|---|---|---|
| backpressure | 2 | 13 |
| foodmatch | 0 | 15 |
| forecast | 4 | 11 |

## Share of the gap to a scattered start closed on clustered starts (G4 verdict V1; descriptive, fitted behavior)

Cut = nearest-courier W1 minus the model's W1; gap = nearest-courier W1 on that start minus on the scattered start, same supply level and seeds; share = mean cut / mean gap with a 95% bootstrap interval over seeds. Sweep settings: `gap_share.csv`.

| Start | Level | Model | Nearest W1 | Nearest W1, scattered | Gap (min) | Cut (min) | Share of gap (95% CI) |
|---|---|---|---|---|---|---|---|
| big_cluster | loose | foodmatch | 15.56 | 3.95 | 11.61 | 0.70 | 0.060 (0.058 to 0.063) |
| big_cluster | loose | forecast | 15.56 | 3.95 | 11.61 | -0.29 | -0.025 (-0.026 to -0.024) |
| big_cluster | loose | backpressure | 15.56 | 3.95 | 11.61 | 0.55 | 0.048 (0.046 to 0.049) |
| three_clusters | loose | foodmatch | 17.46 | 3.95 | 13.51 | 0.76 | 0.056 (0.053 to 0.059) |
| three_clusters | loose | forecast | 17.46 | 3.95 | 13.51 | -0.01 | -0.000 (-0.002 to 0.002) |
| three_clusters | loose | backpressure | 17.46 | 3.95 | 13.51 | 0.19 | 0.014 (0.012 to 0.016) |
| mixed | loose | foodmatch | 13.86 | 3.95 | 9.90 | -0.24 | -0.024 (-0.027 to -0.021) |
| mixed | loose | forecast | 13.86 | 3.95 | 9.90 | -0.42 | -0.042 (-0.044 to -0.039) |
| mixed | loose | backpressure | 13.86 | 3.95 | 9.90 | 0.22 | 0.022 (0.020 to 0.025) |
| big_cluster | normal | foodmatch | 12.35 | 4.58 | 7.77 | -0.36 | -0.047 (-0.055 to -0.039) |
| big_cluster | normal | forecast | 12.35 | 4.58 | 7.77 | -0.05 | -0.006 (-0.008 to -0.003) |
| big_cluster | normal | backpressure | 12.35 | 4.58 | 7.77 | 0.54 | 0.070 (0.066 to 0.074) |
| three_clusters | normal | foodmatch | 13.47 | 4.58 | 8.90 | -0.30 | -0.034 (-0.046 to -0.022) |
| three_clusters | normal | forecast | 13.47 | 4.58 | 8.90 | 0.15 | 0.017 (0.012 to 0.022) |
| three_clusters | normal | backpressure | 13.47 | 4.58 | 8.90 | 0.12 | 0.013 (0.008 to 0.018) |
| mixed | normal | foodmatch | 10.30 | 4.58 | 5.72 | -0.50 | -0.087 (-0.097 to -0.078) |
| mixed | normal | forecast | 10.30 | 4.58 | 5.72 | -0.27 | -0.047 (-0.052 to -0.041) |
| mixed | normal | backpressure | 10.30 | 4.58 | 5.72 | 0.34 | 0.059 (0.054 to 0.064) |
| big_cluster | tight | foodmatch | 8.51 | 4.82 | 3.69 | -1.07 | -0.289 (-0.306 to -0.271) |
| big_cluster | tight | forecast | 8.51 | 4.82 | 3.69 | 0.01 | 0.004 (-0.002 to 0.010) |
| big_cluster | tight | backpressure | 8.51 | 4.82 | 3.69 | 0.06 | 0.017 (0.012 to 0.023) |
| three_clusters | tight | foodmatch | 8.52 | 4.82 | 3.70 | -0.37 | -0.099 (-0.117 to -0.083) |
| three_clusters | tight | forecast | 8.52 | 4.82 | 3.70 | 0.05 | 0.014 (0.007 to 0.022) |
| three_clusters | tight | backpressure | 8.52 | 4.82 | 3.70 | 0.06 | 0.017 (0.010 to 0.023) |
| mixed | tight | foodmatch | 7.77 | 4.82 | 2.95 | -0.36 | -0.121 (-0.141 to -0.103) |
| mixed | tight | forecast | 7.77 | 4.82 | 2.95 | 0.03 | 0.010 (0.002 to 0.017) |
| mixed | tight | backpressure | 7.77 | 4.82 | 2.95 | 0.09 | 0.030 (0.021 to 0.039) |

## FoodMatch at tight supply (G4 verdict V4)

Its p90 gain is read only with the orders it leaves unassigned for more than 30 min and those not delivered by the drain's end; the paper's own design rejects orders unassigned for 30 min (fidelity note, adaptation 2).

| Start | p90 difference (95% CI) | Holm p | Unassigned over 30 min, FoodMatch / nearest | Undelivered, FoodMatch / nearest (30 seeds) |
|---|---|---|---|---|
| big_cluster | -11.08 (-11.37 to -10.80) | 6e-33 | 3.06% / 0.00% | 20 / 0 |
| burst | -6.77 (-7.18 to -6.35) | 3e-22 | 0.05% / 0.00% | 0 / 0 |
| mixed | -11.14 (-11.40 to -10.89) | 2e-34 | 0.46% / 0.00% | 0 / 0 |
| scattered | -0.69 (-1.01 to -0.43) | 0.0016 | 0.00% / 0.00% | 0 / 0 |
| three_clusters | -12.96 (-13.23 to -12.72) | 3.2e-36 | 1.62% / 0.00% | 0 / 0 |

## F1: 90 contrasts, 77 established after Holm

| Start | Level | Behavior | Layout | Scale | Time x | Model | Metric | Mean (95% CI) | Holm p | delta |
|---|---|---|---|---|---|---|---|---|---|---|
| big_cluster | loose | fitted | s0 | 1 | 1 | foodmatch | W1 | -0.698 (-0.727 to -0.669) | 5.6e-27 | 1.55 |
| big_cluster | loose | fitted | s0 | 1 | 1 | foodmatch | p90 | 1.871 (1.797 to 1.947) | 1.3e-27 | 1.00 |
| big_cluster | loose | fitted | s0 | 1 | 1 | forecast | W1 | 0.287 (0.275 to 0.298) | 1.9e-27 | 1.55 |
| big_cluster | loose | fitted | s0 | 1 | 1 | forecast | p90 | 0.256 (0.233 to 0.279) | 1.7e-17 | 1.00 |
| big_cluster | loose | fitted | s0 | 1 | 1 | backpressure | W1 | -0.552 (-0.569 to -0.534) | 2.1e-30 | 1.55 |
| big_cluster | loose | fitted | s0 | 1 | 1 | backpressure | p90 | 0.020 (-0.006 to 0.045) | 1 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.363 (0.305 to 0.424) | 1e-10 | 1.24 |
| big_cluster | normal | fitted | s0 | 1 | 1 | foodmatch | p90 | 1.104 (0.988 to 1.216) | 5.9e-16 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 1 | forecast | W1 | 0.045 (0.026 to 0.065) | 0.0022 | 1.24 |
| big_cluster | normal | fitted | s0 | 1 | 1 | forecast | p90 | 0.344 (0.300 to 0.391) | 4.7e-13 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 1 | backpressure | W1 | -0.541 (-0.571 to -0.514) | 6.6e-24 | 1.24 |
| big_cluster | normal | fitted | s0 | 1 | 1 | backpressure | p90 | 0.365 (0.318 to 0.411) | 1.9e-13 | 1.00 |
| big_cluster | tight | fitted | s0 | 1 | 1 | foodmatch | W1 | 1.065 (1.013 to 1.114) | 4.3e-25 | 0.86 |
| big_cluster | tight | fitted | s0 | 1 | 1 | foodmatch | p90 | -11.081 (-11.365 to -10.803) | 6e-33 | 1.00 |
| big_cluster | tight | fitted | s0 | 1 | 1 | forecast | W1 | -0.013 (-0.037 to 0.008) | 1 | 0.86 |
| big_cluster | tight | fitted | s0 | 1 | 1 | forecast | p90 | 0.013 (-0.169 to 0.190) | 1 | 1.00 |
| big_cluster | tight | fitted | s0 | 1 | 1 | backpressure | W1 | -0.063 (-0.084 to -0.042) | 7.3e-05 | 0.86 |
| big_cluster | tight | fitted | s0 | 1 | 1 | backpressure | p90 | -0.108 (-0.321 to 0.104) | 1 | 1.00 |
| burst | loose | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.080 (0.056 to 0.105) | 2e-05 | 0.42 |
| burst | loose | fitted | s0 | 1 | 1 | foodmatch | p90 | 0.063 (0.053 to 0.073) | 3.8e-11 | 1.00 |
| burst | loose | fitted | s0 | 1 | 1 | forecast | W1 | -0.542 (-0.571 to -0.515) | 4.1e-24 | 0.42 |
| burst | loose | fitted | s0 | 1 | 1 | forecast | p90 | 0.621 (0.596 to 0.647) | 6.3e-27 | 1.00 |
| burst | loose | fitted | s0 | 1 | 1 | backpressure | W1 | -0.421 (-0.452 to -0.392) | 2.9e-20 | 0.42 |
| burst | loose | fitted | s0 | 1 | 1 | backpressure | p90 | 0.134 (0.116 to 0.152) | 9.2e-13 | 1.00 |
| burst | normal | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.063 (0.033 to 0.091) | 0.0055 | 0.49 |
| burst | normal | fitted | s0 | 1 | 1 | foodmatch | p90 | 0.016 (0.003 to 0.029) | 0.28 | 1.00 |
| burst | normal | fitted | s0 | 1 | 1 | forecast | W1 | -0.585 (-0.615 to -0.555) | 1.9e-24 | 0.49 |
| burst | normal | fitted | s0 | 1 | 1 | forecast | p90 | 0.559 (0.526 to 0.590) | 5.8e-23 | 1.00 |
| burst | normal | fitted | s0 | 1 | 1 | backpressure | W1 | -0.304 (-0.331 to -0.276) | 1.7e-17 | 0.49 |
| burst | normal | fitted | s0 | 1 | 1 | backpressure | p90 | 0.229 (0.203 to 0.255) | 7.1e-15 | 1.00 |
| burst | tight | fitted | s0 | 1 | 1 | foodmatch | W1 | -0.154 (-0.196 to -0.110) | 4.3e-06 | 0.49 |
| burst | tight | fitted | s0 | 1 | 1 | foodmatch | p90 | -6.770 (-7.178 to -6.348) | 3e-22 | 1.00 |
| burst | tight | fitted | s0 | 1 | 1 | forecast | W1 | -0.233 (-0.261 to -0.206) | 1.7e-14 | 0.49 |
| burst | tight | fitted | s0 | 1 | 1 | forecast | p90 | 0.505 (0.350 to 0.651) | 1.1e-05 | 1.00 |
| burst | tight | fitted | s0 | 1 | 1 | backpressure | W1 | -0.154 (-0.180 to -0.127) | 1.8e-10 | 0.49 |
| burst | tight | fitted | s0 | 1 | 1 | backpressure | p90 | 0.469 (0.286 to 0.650) | 0.00065 | 1.00 |
| mixed | loose | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.240 (0.212 to 0.271) | 4.9e-14 | 1.38 |
| mixed | loose | fitted | s0 | 1 | 1 | foodmatch | p90 | -0.257 (-0.308 to -0.206) | 4.2e-09 | 1.00 |
| mixed | loose | fitted | s0 | 1 | 1 | forecast | W1 | 0.416 (0.392 to 0.438) | 3.5e-23 | 1.38 |
| mixed | loose | fitted | s0 | 1 | 1 | forecast | p90 | 0.708 (0.669 to 0.749) | 5.4e-23 | 1.00 |
| mixed | loose | fitted | s0 | 1 | 1 | backpressure | W1 | -0.220 (-0.244 to -0.195) | 6.4e-15 | 1.38 |
| mixed | loose | fitted | s0 | 1 | 1 | backpressure | p90 | 0.062 (0.030 to 0.094) | 0.012 | 1.00 |
| mixed | normal | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.497 (0.442 to 0.552) | 2e-15 | 1.02 |
| mixed | normal | fitted | s0 | 1 | 1 | foodmatch | p90 | -0.869 (-0.948 to -0.784) | 5.6e-17 | 1.00 |
| mixed | normal | fitted | s0 | 1 | 1 | forecast | W1 | 0.266 (0.234 to 0.298) | 2.9e-14 | 1.02 |
| mixed | normal | fitted | s0 | 1 | 1 | forecast | p90 | 0.606 (0.551 to 0.657) | 5.2e-18 | 1.00 |
| mixed | normal | fitted | s0 | 1 | 1 | backpressure | W1 | -0.336 (-0.366 to -0.305) | 3.3e-17 | 1.02 |
| mixed | normal | fitted | s0 | 1 | 1 | backpressure | p90 | 0.022 (-0.015 to 0.059) | 1 | 1.00 |
| mixed | tight | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.358 (0.308 to 0.412) | 3.2e-12 | 0.78 |
| mixed | tight | fitted | s0 | 1 | 1 | foodmatch | p90 | -11.142 (-11.397 to -10.892) | 2e-34 | 1.00 |
| mixed | tight | fitted | s0 | 1 | 1 | forecast | W1 | -0.030 (-0.052 to -0.007) | 0.18 | 0.78 |
| mixed | tight | fitted | s0 | 1 | 1 | forecast | p90 | 0.541 (0.354 to 0.732) | 0.00013 | 1.00 |
| mixed | tight | fitted | s0 | 1 | 1 | backpressure | W1 | -0.089 (-0.116 to -0.063) | 1.2e-05 | 0.78 |
| mixed | tight | fitted | s0 | 1 | 1 | backpressure | p90 | 0.025 (-0.195 to 0.247) | 1 | 1.00 |
| scattered | loose | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.098 (0.081 to 0.115) | 1.7e-10 | 0.39 |
| scattered | loose | fitted | s0 | 1 | 1 | foodmatch | p90 | 0.050 (0.042 to 0.058) | 1.4e-11 | 1.00 |
| scattered | loose | fitted | s0 | 1 | 1 | forecast | W1 | -0.564 (-0.598 to -0.529) | 3.3e-22 | 0.39 |
| scattered | loose | fitted | s0 | 1 | 1 | forecast | p90 | 0.613 (0.582 to 0.646) | 6.3e-24 | 1.00 |
| scattered | loose | fitted | s0 | 1 | 1 | backpressure | W1 | -0.448 (-0.474 to -0.423) | 5.8e-23 | 0.39 |
| scattered | loose | fitted | s0 | 1 | 1 | backpressure | p90 | 0.110 (0.099 to 0.121) | 1.5e-16 | 1.00 |
| scattered | normal | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.116 (0.090 to 0.144) | 7.6e-08 | 0.45 |
| scattered | normal | fitted | s0 | 1 | 1 | foodmatch | p90 | 0.049 (0.040 to 0.058) | 2.9e-09 | 1.00 |
| scattered | normal | fitted | s0 | 1 | 1 | forecast | W1 | -0.699 (-0.734 to -0.663) | 1.3e-24 | 0.45 |
| scattered | normal | fitted | s0 | 1 | 1 | forecast | p90 | 0.570 (0.543 to 0.597) | 4.1e-25 | 1.00 |
| scattered | normal | fitted | s0 | 1 | 1 | backpressure | W1 | -0.270 (-0.303 to -0.236) | 5.5e-14 | 0.45 |
| scattered | normal | fitted | s0 | 1 | 1 | backpressure | p90 | 0.227 (0.209 to 0.246) | 2.6e-18 | 1.00 |
| scattered | tight | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.069 (0.035 to 0.103) | 0.0099 | 0.48 |
| scattered | tight | fitted | s0 | 1 | 1 | foodmatch | p90 | -0.690 (-1.007 to -0.433) | 0.0016 | 1.00 |
| scattered | tight | fitted | s0 | 1 | 1 | forecast | W1 | -0.413 (-0.446 to -0.380) | 6.6e-19 | 0.48 |
| scattered | tight | fitted | s0 | 1 | 1 | forecast | p90 | 0.334 (0.226 to 0.428) | 1.8e-05 | 1.00 |
| scattered | tight | fitted | s0 | 1 | 1 | backpressure | W1 | -0.206 (-0.236 to -0.174) | 9.5e-12 | 0.48 |
| scattered | tight | fitted | s0 | 1 | 1 | backpressure | p90 | 0.317 (0.211 to 0.425) | 6.8e-05 | 1.00 |
| three_clusters | loose | fitted | s0 | 1 | 1 | foodmatch | W1 | -0.756 (-0.793 to -0.720) | 8.9e-25 | 1.75 |
| three_clusters | loose | fitted | s0 | 1 | 1 | foodmatch | p90 | -0.092 (-0.162 to -0.025) | 0.17 | 1.00 |
| three_clusters | loose | fitted | s0 | 1 | 1 | forecast | W1 | 0.005 (-0.021 to 0.032) | 1 | 1.75 |
| three_clusters | loose | fitted | s0 | 1 | 1 | forecast | p90 | 0.302 (0.268 to 0.337) | 7.1e-15 | 1.00 |
| three_clusters | loose | fitted | s0 | 1 | 1 | backpressure | W1 | -0.191 (-0.220 to -0.164) | 3.8e-12 | 1.75 |
| three_clusters | loose | fitted | s0 | 1 | 1 | backpressure | p90 | 0.170 (0.128 to 0.214) | 7.3e-07 | 1.00 |
| three_clusters | normal | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.303 (0.204 to 0.400) | 4.2e-05 | 1.36 |
| three_clusters | normal | fitted | s0 | 1 | 1 | foodmatch | p90 | -1.764 (-1.857 to -1.666) | 1.6e-23 | 1.00 |
| three_clusters | normal | fitted | s0 | 1 | 1 | forecast | W1 | -0.148 (-0.193 to -0.105) | 1.1e-05 | 1.36 |
| three_clusters | normal | fitted | s0 | 1 | 1 | forecast | p90 | 0.271 (0.225 to 0.319) | 2.8e-10 | 1.00 |
| three_clusters | normal | fitted | s0 | 1 | 1 | backpressure | W1 | -0.117 (-0.164 to -0.072) | 0.0007 | 1.36 |
| three_clusters | normal | fitted | s0 | 1 | 1 | backpressure | p90 | 0.082 (0.027 to 0.137) | 0.1 | 1.00 |
| three_clusters | tight | fitted | s0 | 1 | 1 | foodmatch | W1 | 0.367 (0.309 to 0.428) | 9.4e-11 | 0.85 |
| three_clusters | tight | fitted | s0 | 1 | 1 | foodmatch | p90 | -12.964 (-13.228 to -12.723) | 3.2e-36 | 1.00 |
| three_clusters | tight | fitted | s0 | 1 | 1 | forecast | W1 | -0.053 (-0.081 to -0.027) | 0.011 | 0.85 |
| three_clusters | tight | fitted | s0 | 1 | 1 | forecast | p90 | 0.051 (-0.186 to 0.277) | 1 | 1.00 |
| three_clusters | tight | fitted | s0 | 1 | 1 | backpressure | W1 | -0.061 (-0.087 to -0.035) | 0.0016 | 0.85 |
| three_clusters | tight | fitted | s0 | 1 | 1 | backpressure | p90 | -0.237 (-0.473 to 0.004) | 0.56 | 1.00 |

## F2: 360 contrasts, 277 established after Holm

| Start | Level | Behavior | Layout | Scale | Time x | Model | Metric | Mean (95% CI) | Holm p | delta |
|---|---|---|---|---|---|---|---|---|---|---|
| big_cluster | loose | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.264 (0.199 to 0.330) | 1.8e-06 | 1.13 |
| big_cluster | loose | p0 | s0 | 1 | 1 | foodmatch | p90 | 1.894 (1.818 to 1.969) | 1.2e-26 | 1.00 |
| big_cluster | loose | p0 | s0 | 1 | 1 | forecast | W1 | 0.226 (0.200 to 0.254) | 6.2e-14 | 1.13 |
| big_cluster | loose | p0 | s0 | 1 | 1 | forecast | p90 | 0.255 (0.231 to 0.277) | 4.7e-17 | 1.00 |
| big_cluster | loose | p0 | s0 | 1 | 1 | backpressure | W1 | -0.618 (-0.642 to -0.594) | 3.2e-27 | 1.13 |
| big_cluster | loose | p0 | s0 | 1 | 1 | backpressure | p90 | -0.003 (-0.029 to 0.024) | 1 | 1.00 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | foodmatch | W1 | -0.954 (-1.000 to -0.909) | 3e-24 | 1.26 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | foodmatch | p90 | 1.884 (1.811 to 1.955) | 2.2e-27 | 1.00 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | forecast | W1 | 0.343 (0.318 to 0.371) | 6.5e-19 | 1.26 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.305 (0.280 to 0.329) | 2.5e-18 | 1.00 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.440 (-0.469 to -0.411) | 1.1e-20 | 1.26 |
| big_cluster | loose | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.006 (-0.014 to 0.026) | 1 | 1.00 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | foodmatch | W1 | -1.021 (-1.060 to -0.983) | 2.7e-27 | 1.44 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 1.884 (1.807 to 1.960) | 1.4e-26 | 1.00 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | forecast | W1 | 0.321 (0.299 to 0.344) | 6.5e-20 | 1.44 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.283 (0.256 to 0.311) | 4.5e-16 | 1.00 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.558 (-0.586 to -0.530) | 1.1e-23 | 1.44 |
| big_cluster | loose | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.026 (0.003 to 0.049) | 1 | 1.00 |
| big_cluster | loose | p1 | s0 | 1 | 1 | foodmatch | W1 | -0.528 (-0.552 to -0.503) | 5.7e-25 | 1.61 |
| big_cluster | loose | p1 | s0 | 1 | 1 | foodmatch | p90 | 1.887 (1.810 to 1.965) | 2.7e-26 | 1.00 |
| big_cluster | loose | p1 | s0 | 1 | 1 | forecast | W1 | 0.234 (0.227 to 0.242) | 2.8e-30 | 1.61 |
| big_cluster | loose | p1 | s0 | 1 | 1 | forecast | p90 | 0.238 (0.214 to 0.264) | 4.3e-15 | 1.00 |
| big_cluster | loose | p1 | s0 | 1 | 1 | backpressure | W1 | -0.378 (-0.389 to -0.365) | 3.6e-29 | 1.61 |
| big_cluster | loose | p1 | s0 | 1 | 1 | backpressure | p90 | 0.033 (0.006 to 0.060) | 1 | 1.00 |
| big_cluster | normal | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.644 (0.535 to 0.756) | 9.1e-10 | 1.18 |
| big_cluster | normal | p0 | s0 | 1 | 1 | foodmatch | p90 | 1.082 (0.955 to 1.202) | 2.6e-14 | 1.00 |
| big_cluster | normal | p0 | s0 | 1 | 1 | forecast | W1 | -0.389 (-0.414 to -0.363) | 7.4e-21 | 1.18 |
| big_cluster | normal | p0 | s0 | 1 | 1 | forecast | p90 | 0.208 (0.179 to 0.239) | 1.3e-11 | 1.00 |
| big_cluster | normal | p0 | s0 | 1 | 1 | backpressure | W1 | -0.256 (-0.290 to -0.219) | 3.1e-12 | 1.18 |
| big_cluster | normal | p0 | s0 | 1 | 1 | backpressure | p90 | -0.069 (-0.107 to -0.031) | 0.13 | 1.00 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.461 (0.372 to 0.552) | 1.5e-08 | 1.02 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | foodmatch | p90 | 1.083 (0.955 to 1.203) | 2.3e-14 | 1.00 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.157 (-0.184 to -0.134) | 1.3e-10 | 1.02 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.363 (0.320 to 0.407) | 1.5e-13 | 1.00 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.315 (-0.346 to -0.284) | 5.5e-16 | 1.02 |
| big_cluster | normal | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.395 (0.351 to 0.444) | 5.7e-14 | 1.00 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.187 (0.114 to 0.261) | 0.0037 | 1.14 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 1.097 (0.977 to 1.212) | 7.7e-15 | 1.00 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.026 (-0.054 to 0.004) | 1 | 1.14 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.343 (0.309 to 0.379) | 1.4e-15 | 1.00 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.537 (-0.566 to -0.507) | 6.3e-23 | 1.14 |
| big_cluster | normal | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.368 (0.327 to 0.409) | 1.4e-14 | 1.00 |
| big_cluster | normal | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.478 (0.422 to 0.535) | 1.1e-13 | 1.29 |
| big_cluster | normal | p1 | s0 | 1 | 1 | foodmatch | p90 | 1.114 (1.004 to 1.218) | 4.3e-16 | 1.00 |
| big_cluster | normal | p1 | s0 | 1 | 1 | forecast | W1 | 0.012 (-0.002 to 0.025) | 1 | 1.29 |
| big_cluster | normal | p1 | s0 | 1 | 1 | forecast | p90 | 0.315 (0.278 to 0.354) | 1.3e-13 | 1.00 |
| big_cluster | normal | p1 | s0 | 1 | 1 | backpressure | W1 | -0.369 (-0.387 to -0.351) | 2.5e-24 | 1.29 |
| big_cluster | normal | p1 | s0 | 1 | 1 | backpressure | p90 | 0.314 (0.267 to 0.361) | 2.6e-11 | 1.00 |
| big_cluster | tight | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.359 (0.277 to 0.447) | 9.8e-07 | 0.86 |
| big_cluster | tight | p0 | s0 | 1 | 1 | foodmatch | p90 | -11.168 (-11.454 to -10.890) | 2.3e-32 | 1.00 |
| big_cluster | tight | p0 | s0 | 1 | 1 | forecast | W1 | -0.084 (-0.104 to -0.065) | 6.9e-07 | 0.86 |
| big_cluster | tight | p0 | s0 | 1 | 1 | forecast | p90 | 0.071 (-0.125 to 0.277) | 1 | 1.00 |
| big_cluster | tight | p0 | s0 | 1 | 1 | backpressure | W1 | -0.026 (-0.050 to -0.001) | 1 | 0.86 |
| big_cluster | tight | p0 | s0 | 1 | 1 | backpressure | p90 | -0.106 (-0.318 to 0.106) | 1 | 1.00 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.042 (-0.004 to 0.087) | 1 | 0.85 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -11.131 (-11.368 to -10.899) | 7.1e-35 | 1.00 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.064 (-0.086 to -0.041) | 0.00056 | 0.85 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | forecast | p90 | -0.140 (-0.346 to 0.056) | 1 | 1.00 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.053 (-0.077 to -0.030) | 0.018 | 0.85 |
| big_cluster | tight | p0.25 | s0 | 1 | 1 | backpressure | p90 | -0.120 (-0.363 to 0.121) | 1 | 1.00 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.534 (0.490 to 0.574) | 1e-18 | 0.85 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -11.106 (-11.340 to -10.879) | 7.5e-35 | 1.00 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.022 (-0.045 to 0.002) | 1 | 0.85 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | forecast | p90 | -0.051 (-0.250 to 0.131) | 1 | 1.00 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.061 (-0.081 to -0.040) | 0.00056 | 0.85 |
| big_cluster | tight | p0.5 | s0 | 1 | 1 | backpressure | p90 | -0.115 (-0.323 to 0.078) | 1 | 1.00 |
| big_cluster | tight | p1 | s0 | 1 | 1 | foodmatch | W1 | 1.395 (1.345 to 1.444) | 2.8e-28 | 0.87 |
| big_cluster | tight | p1 | s0 | 1 | 1 | foodmatch | p90 | -11.104 (-11.376 to -10.833) | 8.4e-33 | 1.00 |
| big_cluster | tight | p1 | s0 | 1 | 1 | forecast | W1 | 0.014 (-0.009 to 0.041) | 1 | 0.87 |
| big_cluster | tight | p1 | s0 | 1 | 1 | forecast | p90 | -0.079 (-0.256 to 0.092) | 1 | 1.00 |
| big_cluster | tight | p1 | s0 | 1 | 1 | backpressure | W1 | -0.056 (-0.075 to -0.038) | 0.00028 | 0.87 |
| big_cluster | tight | p1 | s0 | 1 | 1 | backpressure | p90 | 0.029 (-0.171 to 0.239) | 1 | 1.00 |
| burst | loose | p0 | s0 | 1 | 1 | foodmatch | W1 | -0.025 (-0.043 to -0.008) | 0.72 | 0.56 |
| burst | loose | p0 | s0 | 1 | 1 | foodmatch | p90 | 0.030 (0.019 to 0.041) | 0.0014 | 1.00 |
| burst | loose | p0 | s0 | 1 | 1 | forecast | W1 | -0.787 (-0.825 to -0.750) | 1.6e-24 | 0.56 |
| burst | loose | p0 | s0 | 1 | 1 | forecast | p90 | 0.401 (0.377 to 0.424) | 5.8e-22 | 1.00 |
| burst | loose | p0 | s0 | 1 | 1 | backpressure | W1 | -0.443 (-0.477 to -0.409) | 8.5e-19 | 0.56 |
| burst | loose | p0 | s0 | 1 | 1 | backpressure | p90 | 0.073 (0.059 to 0.089) | 3.9e-08 | 1.00 |
| burst | loose | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.025 (0.008 to 0.042) | 0.49 | 0.51 |
| burst | loose | p0.25 | s0 | 1 | 1 | foodmatch | p90 | 0.061 (0.051 to 0.072) | 9.3e-10 | 1.00 |
| burst | loose | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.754 (-0.788 to -0.718) | 5.4e-25 | 0.51 |
| burst | loose | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.547 (0.522 to 0.574) | 1.7e-24 | 1.00 |
| burst | loose | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.471 (-0.508 to -0.435) | 7.8e-19 | 0.51 |
| burst | loose | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.173 (0.155 to 0.192) | 4.2e-15 | 1.00 |
| burst | loose | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.062 (0.039 to 0.085) | 0.0014 | 0.47 |
| burst | loose | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 0.067 (0.057 to 0.078) | 1.2e-10 | 1.00 |
| burst | loose | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.677 (-0.703 to -0.649) | 8.6e-27 | 0.47 |
| burst | loose | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.607 (0.575 to 0.638) | 1.4e-23 | 1.00 |
| burst | loose | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.474 (-0.509 to -0.439) | 1.7e-19 | 0.47 |
| burst | loose | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.157 (0.141 to 0.173) | 1.5e-15 | 1.00 |
| burst | loose | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.062 (0.047 to 0.077) | 1.6e-06 | 0.38 |
| burst | loose | p1 | s0 | 1 | 1 | foodmatch | p90 | 0.054 (0.045 to 0.064) | 7.2e-10 | 1.00 |
| burst | loose | p1 | s0 | 1 | 1 | forecast | W1 | -0.416 (-0.447 to -0.385) | 3.8e-19 | 0.38 |
| burst | loose | p1 | s0 | 1 | 1 | forecast | p90 | 0.643 (0.611 to 0.674) | 3e-24 | 1.00 |
| burst | loose | p1 | s0 | 1 | 1 | backpressure | W1 | -0.393 (-0.421 to -0.366) | 8e-20 | 0.38 |
| burst | loose | p1 | s0 | 1 | 1 | backpressure | p90 | 0.123 (0.107 to 0.139) | 6e-13 | 1.00 |
| burst | normal | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.033 (0.003 to 0.064) | 1 | 0.64 |
| burst | normal | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.031 (-0.044 to -0.020) | 0.0026 | 1.00 |
| burst | normal | p0 | s0 | 1 | 1 | forecast | W1 | -0.670 (-0.695 to -0.643) | 8.7e-27 | 0.64 |
| burst | normal | p0 | s0 | 1 | 1 | forecast | p90 | 0.290 (0.266 to 0.313) | 3.2e-18 | 1.00 |
| burst | normal | p0 | s0 | 1 | 1 | backpressure | W1 | -0.357 (-0.391 to -0.323) | 3e-16 | 0.64 |
| burst | normal | p0 | s0 | 1 | 1 | backpressure | p90 | 0.075 (0.057 to 0.093) | 1.1e-06 | 1.00 |
| burst | normal | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.056 (0.027 to 0.086) | 0.079 | 0.59 |
| burst | normal | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -0.001 (-0.017 to 0.015) | 1 | 1.00 |
| burst | normal | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.657 (-0.696 to -0.618) | 6.9e-22 | 0.59 |
| burst | normal | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.442 (0.411 to 0.474) | 1.2e-19 | 1.00 |
| burst | normal | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.365 (-0.397 to -0.333) | 3.4e-17 | 0.59 |
| burst | normal | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.200 (0.174 to 0.226) | 1e-12 | 1.00 |
| burst | normal | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.058 (0.034 to 0.082) | 0.0066 | 0.54 |
| burst | normal | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 0.015 (0.003 to 0.028) | 1 | 1.00 |
| burst | normal | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.640 (-0.675 to -0.605) | 4.4e-23 | 0.54 |
| burst | normal | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.510 (0.476 to 0.543) | 1.3e-20 | 1.00 |
| burst | normal | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.326 (-0.356 to -0.297) | 7.3e-17 | 0.54 |
| burst | normal | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.225 (0.200 to 0.250) | 1.4e-14 | 1.00 |
| burst | normal | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.006 (-0.015 to 0.026) | 1 | 0.45 |
| burst | normal | p1 | s0 | 1 | 1 | foodmatch | p90 | 0.032 (0.021 to 0.043) | 0.00071 | 1.00 |
| burst | normal | p1 | s0 | 1 | 1 | forecast | W1 | -0.536 (-0.564 to -0.509) | 2.6e-23 | 0.45 |
| burst | normal | p1 | s0 | 1 | 1 | forecast | p90 | 0.609 (0.576 to 0.641) | 8.7e-23 | 1.00 |
| burst | normal | p1 | s0 | 1 | 1 | backpressure | W1 | -0.241 (-0.266 to -0.214) | 1.1e-14 | 0.45 |
| burst | normal | p1 | s0 | 1 | 1 | backpressure | p90 | 0.235 (0.213 to 0.257) | 1.8e-16 | 1.00 |
| burst | tight | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.298 (0.237 to 0.359) | 3.3e-08 | 0.52 |
| burst | tight | p0 | s0 | 1 | 1 | foodmatch | p90 | -6.998 (-7.356 to -6.624) | 1.8e-23 | 1.00 |
| burst | tight | p0 | s0 | 1 | 1 | forecast | W1 | -0.197 (-0.225 to -0.168) | 9e-12 | 0.52 |
| burst | tight | p0 | s0 | 1 | 1 | forecast | p90 | -0.030 (-0.179 to 0.121) | 1 | 1.00 |
| burst | tight | p0 | s0 | 1 | 1 | backpressure | W1 | -0.180 (-0.203 to -0.156) | 6.5e-13 | 0.52 |
| burst | tight | p0 | s0 | 1 | 1 | backpressure | p90 | 0.116 (-0.033 to 0.257) | 1 | 1.00 |
| burst | tight | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.168 (0.111 to 0.229) | 0.00063 | 0.51 |
| burst | tight | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -6.946 (-7.308 to -6.582) | 2.9e-23 | 1.00 |
| burst | tight | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.207 (-0.235 to -0.180) | 1.4e-12 | 0.51 |
| burst | tight | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.127 (0.003 to 0.247) | 1 | 1.00 |
| burst | tight | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.163 (-0.192 to -0.134) | 1.6e-09 | 0.51 |
| burst | tight | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.221 (0.049 to 0.387) | 1 | 1.00 |
| burst | tight | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.001 (-0.047 to 0.056) | 1 | 0.49 |
| burst | tight | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -6.811 (-7.204 to -6.420) | 2.8e-22 | 1.00 |
| burst | tight | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.232 (-0.263 to -0.200) | 2.3e-12 | 0.49 |
| burst | tight | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.465 (0.316 to 0.611) | 0.00015 | 1.00 |
| burst | tight | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.161 (-0.183 to -0.140) | 1.5e-12 | 0.49 |
| burst | tight | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.326 (0.162 to 0.492) | 0.056 | 1.00 |
| burst | tight | p1 | s0 | 1 | 1 | foodmatch | W1 | -0.304 (-0.341 to -0.264) | 4.4e-13 | 0.48 |
| burst | tight | p1 | s0 | 1 | 1 | foodmatch | p90 | -6.828 (-7.241 to -6.405) | 1.6e-21 | 1.00 |
| burst | tight | p1 | s0 | 1 | 1 | forecast | W1 | -0.233 (-0.253 to -0.211) | 6.7e-17 | 0.48 |
| burst | tight | p1 | s0 | 1 | 1 | forecast | p90 | 0.649 (0.522 to 0.785) | 3.9e-08 | 1.00 |
| burst | tight | p1 | s0 | 1 | 1 | backpressure | W1 | -0.160 (-0.182 to -0.139) | 2e-12 | 0.48 |
| burst | tight | p1 | s0 | 1 | 1 | backpressure | p90 | 0.477 (0.308 to 0.642) | 0.00083 | 1.00 |
| mixed | loose | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.281 (0.246 to 0.320) | 1.4e-12 | 1.25 |
| mixed | loose | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.247 (-0.302 to -0.197) | 1.2e-07 | 1.00 |
| mixed | loose | p0 | s0 | 1 | 1 | forecast | W1 | 0.457 (0.425 to 0.488) | 4e-20 | 1.25 |
| mixed | loose | p0 | s0 | 1 | 1 | forecast | p90 | 0.564 (0.532 to 0.595) | 1.2e-22 | 1.00 |
| mixed | loose | p0 | s0 | 1 | 1 | backpressure | W1 | -0.489 (-0.522 to -0.456) | 1.8e-20 | 1.25 |
| mixed | loose | p0 | s0 | 1 | 1 | backpressure | p90 | -0.018 (-0.055 to 0.018) | 1 | 1.00 |
| mixed | loose | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.241 (0.203 to 0.280) | 1.5e-10 | 1.29 |
| mixed | loose | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -0.256 (-0.313 to -0.199) | 3.4e-07 | 1.00 |
| mixed | loose | p0.25 | s0 | 1 | 1 | forecast | W1 | 0.461 (0.436 to 0.488) | 2e-22 | 1.29 |
| mixed | loose | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.630 (0.591 to 0.667) | 1.8e-21 | 1.00 |
| mixed | loose | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.329 (-0.360 to -0.297) | 4.2e-16 | 1.29 |
| mixed | loose | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.006 (-0.027 to 0.041) | 1 | 1.00 |
| mixed | loose | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.222 (0.194 to 0.253) | 2.5e-12 | 1.34 |
| mixed | loose | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -0.237 (-0.294 to -0.180) | 1.1e-06 | 1.00 |
| mixed | loose | p0.5 | s0 | 1 | 1 | forecast | W1 | 0.432 (0.409 to 0.458) | 3e-22 | 1.34 |
| mixed | loose | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.679 (0.646 to 0.712) | 2.4e-24 | 1.00 |
| mixed | loose | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.246 (-0.273 to -0.218) | 3.2e-14 | 1.34 |
| mixed | loose | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.058 (0.027 to 0.088) | 0.072 | 1.00 |
| mixed | loose | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.260 (0.232 to 0.289) | 1.1e-14 | 1.42 |
| mixed | loose | p1 | s0 | 1 | 1 | foodmatch | p90 | -0.245 (-0.305 to -0.185) | 1.4e-06 | 1.00 |
| mixed | loose | p1 | s0 | 1 | 1 | forecast | W1 | 0.391 (0.375 to 0.407) | 3e-26 | 1.42 |
| mixed | loose | p1 | s0 | 1 | 1 | forecast | p90 | 0.708 (0.668 to 0.748) | 1.8e-22 | 1.00 |
| mixed | loose | p1 | s0 | 1 | 1 | backpressure | W1 | -0.184 (-0.208 to -0.160) | 8.8e-13 | 1.42 |
| mixed | loose | p1 | s0 | 1 | 1 | backpressure | p90 | 0.090 (0.058 to 0.122) | 0.00092 | 1.00 |
| mixed | normal | p0 | s0 | 1 | 1 | foodmatch | W1 | -0.279 (-0.337 to -0.223) | 4.4e-08 | 0.97 |
| mixed | normal | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.871 (-0.947 to -0.792) | 4.4e-17 | 1.00 |
| mixed | normal | p0 | s0 | 1 | 1 | forecast | W1 | -0.370 (-0.399 to -0.342) | 1.3e-18 | 0.97 |
| mixed | normal | p0 | s0 | 1 | 1 | forecast | p90 | 0.411 (0.374 to 0.447) | 4.8e-17 | 1.00 |
| mixed | normal | p0 | s0 | 1 | 1 | backpressure | W1 | -0.283 (-0.308 to -0.258) | 7.3e-17 | 0.97 |
| mixed | normal | p0 | s0 | 1 | 1 | backpressure | p90 | -0.082 (-0.121 to -0.042) | 0.036 | 1.00 |
| mixed | normal | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.210 (0.145 to 0.269) | 5.2e-05 | 0.90 |
| mixed | normal | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -0.893 (-0.967 to -0.814) | 1.9e-17 | 1.00 |
| mixed | normal | p0.25 | s0 | 1 | 1 | forecast | W1 | 0.036 (0.001 to 0.070) | 1 | 0.90 |
| mixed | normal | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.491 (0.449 to 0.530) | 5.6e-18 | 1.00 |
| mixed | normal | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.283 (-0.322 to -0.245) | 2.4e-12 | 0.90 |
| mixed | normal | p0.25 | s0 | 1 | 1 | backpressure | p90 | -0.073 (-0.116 to -0.029) | 0.24 | 1.00 |
| mixed | normal | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.392 (0.321 to 0.462) | 2.4e-09 | 0.95 |
| mixed | normal | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -0.888 (-0.962 to -0.809) | 2.6e-17 | 1.00 |
| mixed | normal | p0.5 | s0 | 1 | 1 | forecast | W1 | 0.202 (0.166 to 0.237) | 2e-09 | 0.95 |
| mixed | normal | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.557 (0.507 to 0.605) | 3.8e-17 | 1.00 |
| mixed | normal | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.287 (-0.329 to -0.244) | 1.5e-11 | 0.95 |
| mixed | normal | p0.5 | s0 | 1 | 1 | backpressure | p90 | -0.037 (-0.080 to 0.004) | 1 | 1.00 |
| mixed | normal | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.645 (0.596 to 0.694) | 7.5e-19 | 1.08 |
| mixed | normal | p1 | s0 | 1 | 1 | foodmatch | p90 | -0.867 (-0.941 to -0.789) | 2.6e-17 | 1.00 |
| mixed | normal | p1 | s0 | 1 | 1 | forecast | W1 | 0.327 (0.297 to 0.357) | 8.6e-17 | 1.08 |
| mixed | normal | p1 | s0 | 1 | 1 | forecast | p90 | 0.669 (0.619 to 0.721) | 9.5e-19 | 1.00 |
| mixed | normal | p1 | s0 | 1 | 1 | backpressure | W1 | -0.293 (-0.325 to -0.261) | 1.6e-14 | 1.08 |
| mixed | normal | p1 | s0 | 1 | 1 | backpressure | p90 | 0.065 (0.027 to 0.106) | 0.27 | 1.00 |
| mixed | tight | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.474 (0.394 to 0.555) | 4.7e-10 | 0.79 |
| mixed | tight | p0 | s0 | 1 | 1 | foodmatch | p90 | -11.058 (-11.315 to -10.811) | 7.9e-34 | 1.00 |
| mixed | tight | p0 | s0 | 1 | 1 | forecast | W1 | -0.056 (-0.080 to -0.032) | 0.012 | 0.79 |
| mixed | tight | p0 | s0 | 1 | 1 | forecast | p90 | 0.361 (0.149 to 0.587) | 0.27 | 1.00 |
| mixed | tight | p0 | s0 | 1 | 1 | backpressure | W1 | -0.050 (-0.086 to -0.014) | 0.74 | 0.79 |
| mixed | tight | p0 | s0 | 1 | 1 | backpressure | p90 | -0.012 (-0.213 to 0.201) | 1 | 1.00 |
| mixed | tight | p0.25 | s0 | 1 | 1 | foodmatch | W1 | -0.003 (-0.063 to 0.065) | 1 | 0.78 |
| mixed | tight | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -11.178 (-11.433 to -10.922) | 1.1e-33 | 1.00 |
| mixed | tight | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.095 (-0.121 to -0.070) | 1.1e-05 | 0.78 |
| mixed | tight | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.326 (0.107 to 0.542) | 0.48 | 1.00 |
| mixed | tight | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.057 (-0.086 to -0.030) | 0.05 | 0.78 |
| mixed | tight | p0.25 | s0 | 1 | 1 | backpressure | p90 | -0.092 (-0.301 to 0.106) | 1 | 1.00 |
| mixed | tight | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.005 (-0.047 to 0.059) | 1 | 0.77 |
| mixed | tight | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -11.099 (-11.329 to -10.863) | 8e-35 | 1.00 |
| mixed | tight | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.057 (-0.083 to -0.030) | 0.019 | 0.77 |
| mixed | tight | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.480 (0.280 to 0.679) | 0.0065 | 1.00 |
| mixed | tight | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.068 (-0.095 to -0.042) | 0.0021 | 0.77 |
| mixed | tight | p0.5 | s0 | 1 | 1 | backpressure | p90 | -0.060 (-0.227 to 0.112) | 1 | 1.00 |
| mixed | tight | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.728 (0.674 to 0.788) | 1.6e-18 | 0.79 |
| mixed | tight | p1 | s0 | 1 | 1 | foodmatch | p90 | -11.169 (-11.376 to -10.969) | 2.7e-36 | 1.00 |
| mixed | tight | p1 | s0 | 1 | 1 | forecast | W1 | 0.013 (-0.014 to 0.041) | 1 | 0.79 |
| mixed | tight | p1 | s0 | 1 | 1 | forecast | p90 | 0.680 (0.492 to 0.865) | 1.3e-05 | 1.00 |
| mixed | tight | p1 | s0 | 1 | 1 | backpressure | W1 | -0.092 (-0.120 to -0.065) | 6.9e-05 | 0.79 |
| mixed | tight | p1 | s0 | 1 | 1 | backpressure | p90 | 0.053 (-0.115 to 0.229) | 1 | 1.00 |
| scattered | loose | p0 | s0 | 1 | 1 | foodmatch | W1 | -0.034 (-0.057 to -0.013) | 0.38 | 0.53 |
| scattered | loose | p0 | s0 | 1 | 1 | foodmatch | p90 | 0.039 (0.030 to 0.048) | 6.6e-07 | 1.00 |
| scattered | loose | p0 | s0 | 1 | 1 | forecast | W1 | -0.887 (-0.920 to -0.856) | 5.2e-28 | 0.53 |
| scattered | loose | p0 | s0 | 1 | 1 | forecast | p90 | 0.424 (0.398 to 0.450) | 1.5e-21 | 1.00 |
| scattered | loose | p0 | s0 | 1 | 1 | backpressure | W1 | -0.468 (-0.508 to -0.432) | 2.9e-18 | 0.53 |
| scattered | loose | p0 | s0 | 1 | 1 | backpressure | p90 | 0.078 (0.068 to 0.089) | 2.5e-12 | 1.00 |
| scattered | loose | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.034 (0.013 to 0.057) | 0.44 | 0.49 |
| scattered | loose | p0.25 | s0 | 1 | 1 | foodmatch | p90 | 0.051 (0.042 to 0.059) | 5e-10 | 1.00 |
| scattered | loose | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.838 (-0.872 to -0.802) | 4.2e-26 | 0.49 |
| scattered | loose | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.548 (0.518 to 0.576) | 4.9e-23 | 1.00 |
| scattered | loose | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.483 (-0.520 to -0.447) | 3.7e-19 | 0.49 |
| scattered | loose | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.140 (0.128 to 0.153) | 1.5e-17 | 1.00 |
| scattered | loose | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.074 (0.050 to 0.097) | 0.00015 | 0.44 |
| scattered | loose | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 0.056 (0.048 to 0.064) | 7.4e-12 | 1.00 |
| scattered | loose | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.723 (-0.761 to -0.684) | 2.6e-23 | 0.44 |
| scattered | loose | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.593 (0.566 to 0.620) | 3.7e-25 | 1.00 |
| scattered | loose | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.486 (-0.522 to -0.450) | 3.2e-19 | 0.44 |
| scattered | loose | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.121 (0.108 to 0.135) | 2.6e-14 | 1.00 |
| scattered | loose | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.094 (0.079 to 0.108) | 6.6e-11 | 0.36 |
| scattered | loose | p1 | s0 | 1 | 1 | foodmatch | p90 | 0.047 (0.040 to 0.056) | 4.9e-10 | 1.00 |
| scattered | loose | p1 | s0 | 1 | 1 | forecast | W1 | -0.421 (-0.453 to -0.388) | 7.2e-19 | 0.36 |
| scattered | loose | p1 | s0 | 1 | 1 | forecast | p90 | 0.632 (0.602 to 0.663) | 2.8e-24 | 1.00 |
| scattered | loose | p1 | s0 | 1 | 1 | backpressure | W1 | -0.404 (-0.428 to -0.380) | 1.1e-21 | 0.36 |
| scattered | loose | p1 | s0 | 1 | 1 | backpressure | p90 | 0.106 (0.095 to 0.119) | 1.6e-14 | 1.00 |
| scattered | normal | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.022 (-0.004 to 0.050) | 1 | 0.61 |
| scattered | normal | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.003 (-0.017 to 0.011) | 1 | 1.00 |
| scattered | normal | p0 | s0 | 1 | 1 | forecast | W1 | -0.886 (-0.925 to -0.848) | 8.4e-26 | 0.61 |
| scattered | normal | p0 | s0 | 1 | 1 | forecast | p90 | 0.324 (0.297 to 0.350) | 5.4e-18 | 1.00 |
| scattered | normal | p0 | s0 | 1 | 1 | backpressure | W1 | -0.408 (-0.452 to -0.364) | 6.3e-15 | 0.61 |
| scattered | normal | p0 | s0 | 1 | 1 | backpressure | p90 | 0.067 (0.055 to 0.080) | 3.7e-09 | 1.00 |
| scattered | normal | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.058 (0.032 to 0.085) | 0.018 | 0.56 |
| scattered | normal | p0.25 | s0 | 1 | 1 | foodmatch | p90 | 0.031 (0.020 to 0.044) | 0.0014 | 1.00 |
| scattered | normal | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.864 (-0.904 to -0.825) | 1.4e-24 | 0.56 |
| scattered | normal | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.465 (0.432 to 0.496) | 4.6e-20 | 1.00 |
| scattered | normal | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.401 (-0.440 to -0.357) | 3.9e-15 | 0.56 |
| scattered | normal | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.204 (0.182 to 0.227) | 7.9e-15 | 1.00 |
| scattered | normal | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.102 (0.069 to 0.134) | 0.00016 | 0.50 |
| scattered | normal | p0.5 | s0 | 1 | 1 | foodmatch | p90 | 0.038 (0.028 to 0.048) | 1e-05 | 1.00 |
| scattered | normal | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.789 (-0.827 to -0.750) | 5.6e-24 | 0.50 |
| scattered | normal | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.526 (0.493 to 0.557) | 1.7e-21 | 1.00 |
| scattered | normal | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.365 (-0.406 to -0.324) | 1.7e-14 | 0.50 |
| scattered | normal | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.207 (0.184 to 0.230) | 1.7e-14 | 1.00 |
| scattered | normal | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.076 (0.061 to 0.091) | 2.5e-08 | 0.41 |
| scattered | normal | p1 | s0 | 1 | 1 | foodmatch | p90 | 0.056 (0.047 to 0.064) | 2.3e-11 | 1.00 |
| scattered | normal | p1 | s0 | 1 | 1 | forecast | W1 | -0.591 (-0.624 to -0.555) | 3.4e-22 | 0.41 |
| scattered | normal | p1 | s0 | 1 | 1 | forecast | p90 | 0.591 (0.561 to 0.619) | 2.6e-24 | 1.00 |
| scattered | normal | p1 | s0 | 1 | 1 | backpressure | W1 | -0.244 (-0.274 to -0.215) | 1.3e-13 | 0.41 |
| scattered | normal | p1 | s0 | 1 | 1 | backpressure | p90 | 0.217 (0.196 to 0.238) | 4.2e-16 | 1.00 |
| scattered | tight | p0 | s0 | 1 | 1 | foodmatch | W1 | 0.219 (0.170 to 0.269) | 3.4e-07 | 0.57 |
| scattered | tight | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.905 (-1.271 to -0.601) | 0.0016 | 1.00 |
| scattered | tight | p0 | s0 | 1 | 1 | forecast | W1 | -0.382 (-0.419 to -0.345) | 4.8e-16 | 0.57 |
| scattered | tight | p0 | s0 | 1 | 1 | forecast | p90 | -0.008 (-0.115 to 0.087) | 1 | 1.00 |
| scattered | tight | p0 | s0 | 1 | 1 | backpressure | W1 | -0.254 (-0.291 to -0.216) | 1.3e-11 | 0.57 |
| scattered | tight | p0 | s0 | 1 | 1 | backpressure | p90 | 0.083 (-0.012 to 0.195) | 1 | 1.00 |
| scattered | tight | p0.25 | s0 | 1 | 1 | foodmatch | W1 | 0.190 (0.149 to 0.232) | 1.3e-07 | 0.54 |
| scattered | tight | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -0.851 (-1.226 to -0.541) | 0.0048 | 1.00 |
| scattered | tight | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.406 (-0.442 to -0.370) | 6.2e-17 | 0.54 |
| scattered | tight | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.145 (0.034 to 0.243) | 0.82 | 1.00 |
| scattered | tight | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.241 (-0.273 to -0.208) | 2.8e-12 | 0.54 |
| scattered | tight | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.211 (0.128 to 0.295) | 0.0038 | 1.00 |
| scattered | tight | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.138 (0.101 to 0.180) | 2.6e-05 | 0.51 |
| scattered | tight | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -0.780 (-1.120 to -0.492) | 0.0066 | 1.00 |
| scattered | tight | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.410 (-0.447 to -0.373) | 5.7e-17 | 0.51 |
| scattered | tight | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.241 (0.113 to 0.349) | 0.043 | 1.00 |
| scattered | tight | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.234 (-0.259 to -0.209) | 5.8e-15 | 0.51 |
| scattered | tight | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.257 (0.140 to 0.357) | 0.0096 | 1.00 |
| scattered | tight | p1 | s0 | 1 | 1 | foodmatch | W1 | -0.006 (-0.036 to 0.028) | 1 | 0.47 |
| scattered | tight | p1 | s0 | 1 | 1 | foodmatch | p90 | -0.596 (-0.929 to -0.351) | 0.04 | 1.00 |
| scattered | tight | p1 | s0 | 1 | 1 | forecast | W1 | -0.372 (-0.406 to -0.339) | 8.7e-17 | 0.47 |
| scattered | tight | p1 | s0 | 1 | 1 | forecast | p90 | 0.448 (0.367 to 0.526) | 1.3e-09 | 1.00 |
| scattered | tight | p1 | s0 | 1 | 1 | backpressure | W1 | -0.177 (-0.197 to -0.156) | 4e-14 | 0.47 |
| scattered | tight | p1 | s0 | 1 | 1 | backpressure | p90 | 0.419 (0.340 to 0.511) | 3.3e-08 | 1.00 |
| three_clusters | loose | p0 | s0 | 1 | 1 | foodmatch | W1 | -1.002 (-1.054 to -0.951) | 2.9e-23 | 1.64 |
| three_clusters | loose | p0 | s0 | 1 | 1 | foodmatch | p90 | -0.042 (-0.105 to 0.023) | 1 | 1.00 |
| three_clusters | loose | p0 | s0 | 1 | 1 | forecast | W1 | -0.092 (-0.113 to -0.071) | 3.2e-07 | 1.64 |
| three_clusters | loose | p0 | s0 | 1 | 1 | forecast | p90 | 0.206 (0.176 to 0.236) | 1.5e-11 | 1.00 |
| three_clusters | loose | p0 | s0 | 1 | 1 | backpressure | W1 | -0.382 (-0.411 to -0.355) | 1.5e-19 | 1.64 |
| three_clusters | loose | p0 | s0 | 1 | 1 | backpressure | p90 | -0.025 (-0.068 to 0.018) | 1 | 1.00 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | foodmatch | W1 | -0.948 (-1.004 to -0.891) | 5.8e-22 | 1.68 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -0.060 (-0.126 to 0.008) | 1 | 1.00 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.039 (-0.068 to -0.009) | 1 | 1.68 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.298 (0.262 to 0.334) | 1.3e-13 | 1.00 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.296 (-0.325 to -0.266) | 1.4e-15 | 1.68 |
| three_clusters | loose | p0.25 | s0 | 1 | 1 | backpressure | p90 | 0.108 (0.071 to 0.144) | 0.00052 | 1.00 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | foodmatch | W1 | -0.850 (-0.896 to -0.804) | 4.6e-23 | 1.72 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -0.071 (-0.140 to -0.001) | 1 | 1.00 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.004 (-0.035 to 0.028) | 1 | 1.72 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.314 (0.283 to 0.347) | 1.2e-15 | 1.00 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.244 (-0.272 to -0.217) | 3.1e-14 | 1.72 |
| three_clusters | loose | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.139 (0.095 to 0.182) | 0.00015 | 1.00 |
| three_clusters | loose | p1 | s0 | 1 | 1 | foodmatch | W1 | -0.681 (-0.714 to -0.648) | 5.6e-24 | 1.77 |
| three_clusters | loose | p1 | s0 | 1 | 1 | foodmatch | p90 | -0.086 (-0.157 to -0.012) | 1 | 1.00 |
| three_clusters | loose | p1 | s0 | 1 | 1 | forecast | W1 | 0.003 (-0.019 to 0.024) | 1 | 1.77 |
| three_clusters | loose | p1 | s0 | 1 | 1 | forecast | p90 | 0.279 (0.244 to 0.313) | 2e-13 | 1.00 |
| three_clusters | loose | p1 | s0 | 1 | 1 | backpressure | W1 | -0.124 (-0.147 to -0.103) | 1.4e-09 | 1.77 |
| three_clusters | loose | p1 | s0 | 1 | 1 | backpressure | p90 | 0.175 (0.130 to 0.221) | 6.4e-06 | 1.00 |
| three_clusters | normal | p0 | s0 | 1 | 1 | foodmatch | W1 | -0.239 (-0.325 to -0.153) | 0.0011 | 1.27 |
| three_clusters | normal | p0 | s0 | 1 | 1 | foodmatch | p90 | -1.780 (-1.883 to -1.675) | 5.1e-22 | 1.00 |
| three_clusters | normal | p0 | s0 | 1 | 1 | forecast | W1 | -0.414 (-0.446 to -0.382) | 9.5e-19 | 1.27 |
| three_clusters | normal | p0 | s0 | 1 | 1 | forecast | p90 | 0.128 (0.085 to 0.172) | 0.0004 | 1.00 |
| three_clusters | normal | p0 | s0 | 1 | 1 | backpressure | W1 | -0.212 (-0.251 to -0.173) | 3.2e-09 | 1.27 |
| three_clusters | normal | p0 | s0 | 1 | 1 | backpressure | p90 | -0.148 (-0.202 to -0.095) | 0.00096 | 1.00 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | foodmatch | W1 | -0.092 (-0.192 to 0.006) | 1 | 1.26 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -1.779 (-1.882 to -1.670) | 1e-21 | 1.00 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.367 (-0.406 to -0.328) | 4.3e-15 | 1.26 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | forecast | p90 | 0.252 (0.197 to 0.308) | 2e-07 | 1.00 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.137 (-0.177 to -0.095) | 5.3e-05 | 1.26 |
| three_clusters | normal | p0.25 | s0 | 1 | 1 | backpressure | p90 | -0.019 (-0.096 to 0.057) | 1 | 1.00 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | foodmatch | W1 | 0.137 (0.049 to 0.227) | 0.48 | 1.31 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -1.755 (-1.855 to -1.650) | 4.4e-22 | 1.00 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.225 (-0.272 to -0.177) | 1.1e-07 | 1.31 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.285 (0.232 to 0.338) | 4.5e-09 | 1.00 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.116 (-0.162 to -0.069) | 0.0039 | 1.31 |
| three_clusters | normal | p0.5 | s0 | 1 | 1 | backpressure | p90 | 0.036 (-0.023 to 0.096) | 1 | 1.00 |
| three_clusters | normal | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.420 (0.325 to 0.517) | 3.8e-07 | 1.40 |
| three_clusters | normal | p1 | s0 | 1 | 1 | foodmatch | p90 | -1.749 (-1.845 to -1.646) | 2e-22 | 1.00 |
| three_clusters | normal | p1 | s0 | 1 | 1 | forecast | W1 | -0.111 (-0.146 to -0.077) | 9.7e-05 | 1.40 |
| three_clusters | normal | p1 | s0 | 1 | 1 | forecast | p90 | 0.236 (0.176 to 0.296) | 2.9e-06 | 1.00 |
| three_clusters | normal | p1 | s0 | 1 | 1 | backpressure | W1 | -0.025 (-0.069 to 0.020) | 1 | 1.40 |
| three_clusters | normal | p1 | s0 | 1 | 1 | backpressure | p90 | 0.110 (0.049 to 0.169) | 0.11 | 1.00 |
| three_clusters | tight | p0 | s0 | 1 | 1 | foodmatch | W1 | -0.222 (-0.279 to -0.165) | 4e-06 | 0.86 |
| three_clusters | tight | p0 | s0 | 1 | 1 | foodmatch | p90 | -12.908 (-13.163 to -12.669) | 9.7e-36 | 1.00 |
| three_clusters | tight | p0 | s0 | 1 | 1 | forecast | W1 | -0.112 (-0.144 to -0.080) | 3.2e-05 | 0.86 |
| three_clusters | tight | p0 | s0 | 1 | 1 | forecast | p90 | 0.081 (-0.090 to 0.247) | 1 | 1.00 |
| three_clusters | tight | p0 | s0 | 1 | 1 | backpressure | W1 | -0.088 (-0.118 to -0.061) | 0.0002 | 0.86 |
| three_clusters | tight | p0 | s0 | 1 | 1 | backpressure | p90 | -0.262 (-0.465 to -0.051) | 1 | 1.00 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | foodmatch | W1 | -0.343 (-0.410 to -0.277) | 9.7e-09 | 0.85 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | foodmatch | p90 | -13.015 (-13.260 to -12.771) | 4.2e-36 | 1.00 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | forecast | W1 | -0.090 (-0.115 to -0.065) | 1.3e-05 | 0.85 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | forecast | p90 | -0.025 (-0.220 to 0.164) | 1 | 1.00 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | backpressure | W1 | -0.058 (-0.083 to -0.034) | 0.0096 | 0.85 |
| three_clusters | tight | p0.25 | s0 | 1 | 1 | backpressure | p90 | -0.295 (-0.491 to -0.096) | 0.5 | 1.00 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | foodmatch | W1 | -0.044 (-0.104 to 0.016) | 1 | 0.85 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | foodmatch | p90 | -12.908 (-13.132 to -12.679) | 4.9e-37 | 1.00 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | forecast | W1 | -0.063 (-0.086 to -0.042) | 0.00091 | 0.85 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | forecast | p90 | 0.066 (-0.144 to 0.263) | 1 | 1.00 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | backpressure | W1 | -0.047 (-0.067 to -0.029) | 0.0047 | 0.85 |
| three_clusters | tight | p0.5 | s0 | 1 | 1 | backpressure | p90 | -0.233 (-0.437 to -0.021) | 1 | 1.00 |
| three_clusters | tight | p1 | s0 | 1 | 1 | foodmatch | W1 | 0.705 (0.642 to 0.769) | 7.9e-17 | 0.86 |
| three_clusters | tight | p1 | s0 | 1 | 1 | foodmatch | p90 | -12.903 (-13.167 to -12.649) | 1.6e-35 | 1.00 |
| three_clusters | tight | p1 | s0 | 1 | 1 | forecast | W1 | -0.016 (-0.042 to 0.014) | 1 | 0.86 |
| three_clusters | tight | p1 | s0 | 1 | 1 | forecast | p90 | 0.045 (-0.151 to 0.257) | 1 | 1.00 |
| three_clusters | tight | p1 | s0 | 1 | 1 | backpressure | W1 | -0.034 (-0.058 to -0.009) | 0.77 | 0.86 |
| three_clusters | tight | p1 | s0 | 1 | 1 | backpressure | p90 | -0.180 (-0.383 to 0.016) | 1 | 1.00 |

## F3: 30 contrasts, 27 established after Holm

| Start | Level | Behavior | Layout | Scale | Time x | Model | Metric | Mean (95% CI) | Holm p | delta |
|---|---|---|---|---|---|---|---|---|---|---|
| big_cluster | normal | fitted | osm | 1 | 1 | foodmatch | W1 | -0.031 (-0.086 to 0.027) | 0.58 | 1.23 |
| big_cluster | normal | fitted | osm | 1 | 1 | foodmatch | p90 | 0.153 (-0.122 to 0.421) | 0.58 | 1.00 |
| big_cluster | normal | fitted | osm | 1 | 1 | forecast | W1 | -0.377 (-0.407 to -0.348) | 1.8e-19 | 1.23 |
| big_cluster | normal | fitted | osm | 1 | 1 | forecast | p90 | 0.523 (0.456 to 0.589) | 3.5e-14 | 1.00 |
| big_cluster | normal | fitted | osm | 1 | 1 | backpressure | W1 | -0.540 (-0.569 to -0.511) | 3.9e-24 | 1.23 |
| big_cluster | normal | fitted | osm | 1 | 1 | backpressure | p90 | 0.754 (0.660 to 0.846) | 2.6e-14 | 1.00 |
| big_cluster | normal | fitted | s1 | 1 | 1 | foodmatch | W1 | 0.364 (0.297 to 0.434) | 2.5e-10 | 1.23 |
| big_cluster | normal | fitted | s1 | 1 | 1 | foodmatch | p90 | 1.048 (0.890 to 1.194) | 1.2e-12 | 1.00 |
| big_cluster | normal | fitted | s1 | 1 | 1 | forecast | W1 | 0.032 (0.007 to 0.057) | 0.062 | 1.23 |
| big_cluster | normal | fitted | s1 | 1 | 1 | forecast | p90 | 0.321 (0.278 to 0.367) | 5.6e-13 | 1.00 |
| big_cluster | normal | fitted | s1 | 1 | 1 | backpressure | W1 | -0.603 (-0.635 to -0.568) | 1.6e-23 | 1.23 |
| big_cluster | normal | fitted | s1 | 1 | 1 | backpressure | p90 | 0.352 (0.288 to 0.418) | 2.5e-10 | 1.00 |
| big_cluster | normal | fitted | s2 | 1 | 1 | foodmatch | W1 | 0.386 (0.322 to 0.452) | 2.7e-11 | 1.22 |
| big_cluster | normal | fitted | s2 | 1 | 1 | foodmatch | p90 | 1.136 (0.961 to 1.296) | 1.4e-12 | 1.00 |
| big_cluster | normal | fitted | s2 | 1 | 1 | forecast | W1 | 0.060 (0.035 to 0.086) | 0.00048 | 1.22 |
| big_cluster | normal | fitted | s2 | 1 | 1 | forecast | p90 | 0.308 (0.277 to 0.339) | 1.4e-16 | 1.00 |
| big_cluster | normal | fitted | s2 | 1 | 1 | backpressure | W1 | -0.556 (-0.586 to -0.527) | 4e-24 | 1.22 |
| big_cluster | normal | fitted | s2 | 1 | 1 | backpressure | p90 | 0.410 (0.360 to 0.463) | 3.5e-14 | 1.00 |
| big_cluster | normal | fitted | s3 | 1 | 1 | foodmatch | W1 | 0.336 (0.287 to 0.388) | 4.8e-12 | 1.24 |
| big_cluster | normal | fitted | s3 | 1 | 1 | foodmatch | p90 | 0.944 (0.769 to 1.108) | 1.3e-10 | 1.00 |
| big_cluster | normal | fitted | s3 | 1 | 1 | forecast | W1 | 0.036 (0.016 to 0.056) | 0.0073 | 1.24 |
| big_cluster | normal | fitted | s3 | 1 | 1 | forecast | p90 | 0.337 (0.300 to 0.377) | 6.8e-15 | 1.00 |
| big_cluster | normal | fitted | s3 | 1 | 1 | backpressure | W1 | -0.596 (-0.622 to -0.571) | 4.4e-27 | 1.24 |
| big_cluster | normal | fitted | s3 | 1 | 1 | backpressure | p90 | 0.353 (0.302 to 0.405) | 1.4e-12 | 1.00 |
| big_cluster | normal | fitted | s4 | 1 | 1 | foodmatch | W1 | 0.321 (0.258 to 0.387) | 1.1e-09 | 1.23 |
| big_cluster | normal | fitted | s4 | 1 | 1 | foodmatch | p90 | 1.070 (0.914 to 1.218) | 9.4e-13 | 1.00 |
| big_cluster | normal | fitted | s4 | 1 | 1 | forecast | W1 | 0.049 (0.030 to 0.068) | 0.00022 | 1.23 |
| big_cluster | normal | fitted | s4 | 1 | 1 | forecast | p90 | 0.307 (0.263 to 0.349) | 5e-13 | 1.00 |
| big_cluster | normal | fitted | s4 | 1 | 1 | backpressure | W1 | -0.582 (-0.606 to -0.558) | 4.8e-27 | 1.23 |
| big_cluster | normal | fitted | s4 | 1 | 1 | backpressure | p90 | 0.394 (0.335 to 0.451) | 1.4e-12 | 1.00 |

## F4: 12 contrasts, 10 established after Holm

| Start | Level | Behavior | Layout | Scale | Time x | Model | Metric | Mean (95% CI) | Holm p | delta |
|---|---|---|---|---|---|---|---|---|---|---|
| big_cluster | normal | fitted | s0 | 0.5 | 1 | foodmatch | W1 | 0.288 (0.228 to 0.346) | 1.5e-09 | 1.24 |
| big_cluster | normal | fitted | s0 | 0.5 | 1 | foodmatch | p90 | -0.400 (-0.929 to 0.070) | 0.23 | 1.00 |
| big_cluster | normal | fitted | s0 | 0.5 | 1 | forecast | W1 | -0.036 (-0.080 to 0.007) | 0.23 | 1.24 |
| big_cluster | normal | fitted | s0 | 0.5 | 1 | forecast | p90 | 0.303 (0.239 to 0.367) | 3.4e-09 | 1.00 |
| big_cluster | normal | fitted | s0 | 0.5 | 1 | backpressure | W1 | -0.436 (-0.475 to -0.394) | 3.6e-18 | 1.24 |
| big_cluster | normal | fitted | s0 | 0.5 | 1 | backpressure | p90 | 0.326 (0.233 to 0.419) | 1.4e-06 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | foodmatch | W1 | -0.399 (-0.425 to -0.372) | 2.9e-22 | 1.12 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | foodmatch | p90 | 0.827 (0.779 to 0.876) | 1.8e-23 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | forecast | W1 | 0.216 (0.204 to 0.228) | 1.4e-24 | 1.12 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | forecast | p90 | 0.148 (0.134 to 0.162) | 1.1e-17 | 1.00 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | backpressure | W1 | -0.359 (-0.379 to -0.339) | 2.7e-24 | 1.12 |
| big_cluster | normal | fitted | s0 | 1 | 0.75 | backpressure | p90 | 0.025 (0.008 to 0.044) | 0.04 | 1.00 |

Secondary metrics (descriptive): `secondary.csv`. Classes per cell: `classes.csv`.
