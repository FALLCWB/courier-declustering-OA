# courier-declustering-OA

Open-access code of the courier declustering study. It holds an event-driven simulator of evening food deliveries in Curitiba, Brazil, and a pre-registered benchmark of ten dispatch models. Every model starts from the same courier clusters. The only lever under test is which courier gets each order, when an order is assigned, and where idle couriers are sent. Couriers drift back to their preferred area at the rate measured in the Meituan data, so a model that only works when couriers obey is caught.

This research was supported by data provided by Meituan.

This repository is a curated snapshot of the study's code, taken at commit eaee3f4 of the private study repository (the first snapshot was e7fa224), with a fresh history. It holds the simulator, the models, the run and analysis scripts, the tests, the figure scripts, the two pre-registrations and their three addenda (R3, the equivalence reading; addendum C; and the training-budget addendum). It also holds the aggregate results that the paper-number and figure scripts read, under `avaliacao/`: the training records of the five learned models, the first round's results, the G8 results, the behavior fit behind Table 1, the Paper A figure data, package C (the response to the external review: E6, the exploratory parts 2 to 5, C6 and C7), the training-budget check of the learned models and the policy 5 validation check on seeds disjoint from training. The episode files, the other run outputs, the decision log, the plans and the gate reviews stay in the study's private records. Comments that cite `DECISIONS.md` or another `avaliacao/` folder point to those records.

## Layout

| Path | Holds |
|---|---|
| `sim/city/` | Build of the Curitiba city model: H3 resolution-9 cells, IBGE 2022 population, road travel times, restaurant layouts |
| `sim/core/` | Simulator: demand, engine, courier idle behavior, metrics, baseline policies |
| `sim/` (other modules) | Calibration, scenarios, the episode runners (`run_cells.py` for the first round, `run_extension.py` for the extension), the analyses (`analysis.py`, `analysis_extension.py`), statistics (`stats.py`), training of the learned models (`train_*.py`), videos |
| `models/` | The published dispatch models reimplemented as policies, with one fidelity note each (`models/fidelity/`) and the trained policies (`models/trained/`) |
| `scripts/` | Data profiles, checks, pilot and G8 pipelines, package C analyses (`package_c_analysis.py`, `package_c_tables.py`, `paper_numbers_c.py`, `fit_bands_report.py`), paper numbers and figure data |
| `tests/` | Tests with known answers |
| `figures/` | MATLAB figure scripts; `figures/paper/` holds the Paper A figures |
| `scenarios/` | The starting layouts and the scenario manifest |
| `data/` | `README.md` describes every source; `fetch.sh` and `fetch_cnpj.sh` download the public ones; raw files are never in git |
| `preregistration*.md` | The pre-registrations of the first round and of the extension, the R3 addendum, addendum C (package C) and the training-budget addendum, each with its PDF |
| `avaliacao/` | Aggregate results only: training records (`run.json`, `curve.csv`, `training.csv`), the first round's `results/`, `20261105-1405-g8-results/` (E1, E2, the R4 block, paper numbers), `20261102-1146-behavior-single-final/` (the behavior fit behind Table 1), `20261106-1703-paper-figures/data/` (Paper A figure data), `20261107-0030-package-c/` (package C: `results/` with one CSV per table and `paper-numbers-C.md`, the behavior refits, and the sha256 of each episode file), `20261107-2035-budget-check/` (training-budget check: training records of the retrained policy 1 and `results/`) and `20261108-1344-policy5-validation/` (policy 5 validation check on seeds 95501 to 95503: rows, report and `results/`); the retrained policies are in `models/trained_budget/` |

## Pre-registrations

The two pre-registrations are byte-identical to the files frozen in the private study repository before any comparison run:

| File | Frozen at study commit | SHA-256 |
|---|---|---|
| `preregistration.md` | 126631b | `1f32dd215281a7834daa0db041b9add4041ce77dcbb5d7008adb59db1f8d16ff` |
| `preregistration-extension.md` | 8e082e3 | `ad3037d8ba633175d36f26a67b6c6b2783bc4cc90372978c8cf12f1116c24fe6` |

Check with `sha256sum preregistration.md preregistration-extension.md`. The three addenda were written after the freezes, as the paper reports.

## Reproduce

```
uv sync
bash data/fetch.sh            # downloads the public sources into data/raw
uv run python sim/city/build.py .
uv run pytest
```

The full benchmark is about 96,000 four-hour episodes, so it belongs on a server. Values depend on the exact number of OpenBLAS threads. Every evaluation run pins 30 threads before numpy loads (`sim/blas.py`). On a machine with fewer than 30 processors, OpenBLAS caps its threads at the processor count, and `scripts/fake_nprocs.c` (loaded with `LD_PRELOAD`, with `OPENBLAS_CORETYPE=Haswell`) restores the 30 threads. With them, episodes reproduce bit for bit across machines.

## Data terms

- Meituan INFORMS TSL Research Challenge data: CC BY-NC 4.0, academic use, no redistribution. Only fitted parameters and aggregate moments enter this repository. This research was supported by data provided by Meituan.
- Grubhub MDRP instances: used for calibration with citation, not redistributed.
- OpenStreetMap data: ODbL, (c) OpenStreetMap contributors.
- IBGE census tracts and CNEFE addresses, Receita Federal CNPJ open data: Brazilian public open data. The repository publishes restaurant density per cell, never a list of businesses.

## License

MIT, see `LICENSE`.
