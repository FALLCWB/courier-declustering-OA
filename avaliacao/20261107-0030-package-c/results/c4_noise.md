This research was supported by data provided by Meituan.

## Part 4. Noisy demand information (exploratory, no test)

Forecast-aware matching, Li et al., Zhu et al. and Jusup et al. read the expected demand times a lognormal factor per zone and episode (mean 1, CV 0.2); W1 keeps the true demand. Seeds 1001 to 1030; nearest courier and the true-input rows come from the full runs at the same seeds. Holm runs within the E1-shaped and E2-shaped sets of each input, as a reading device. The noisy and true intervals of one contrast share their bootstrap resamples (common random numbers), so their difference is not blurred by resampling. Episodes equal to the true-input episode in every metric: forecast 0 of 480, li 480 of 480, zhu 0 of 480, jusup 6 of 480; a model with all its episodes equal reads no expected demand at run time. Contrasts: `c4_noise_contrasts.csv`; classes: `c4_noise_classes.csv`; identity: `c4_noise_identity.csv`.

W1 is W1 over the evening on Q1 cells and W1 over 60 min on Q2 cells; differences are model minus nearest courier, in minutes; lower is better.

| input | holm_set | contrasts | established |
|---|---|---|---|
| noisy | E1-shaped | 48 | 39 |
| noisy | E2-shaped | 80 | 69 |
| true | E1-shaped | 48 | 39 |
| true | E2-shaped | 80 | 70 |

Classes by model (cells):

| model | class | noisy | true |
|---|---|---|---|
| forecast | does not undo | 10 | 10 |
| forecast | prevents at no delivery cost | 4 | 4 |
| forecast | does not prevent | 2 | 2 |
| jusup | does not prevent | 6 | 6 |
| jusup | does not undo | 6 | 6 |
| jusup | undoes at no delivery cost | 4 | 4 |
| li | does not undo | 10 | 10 |
| li | prevents at no delivery cost | 4 | 4 |
| li | does not prevent | 2 | 2 |
| zhu | does not undo | 10 | 10 |
| zhu | does not prevent | 6 | 6 |

Classes that change: 0 of 64.

None.

This research was supported by data provided by Meituan.
