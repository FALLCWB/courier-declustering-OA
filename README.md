# courier-declustering-OA

Open-access code of the courier declustering study. It holds an event-driven simulator of evening food deliveries in Curitiba, Brazil, and a pre-registered benchmark of ten dispatch models. Every model starts from the same courier clusters. The only lever under test is which courier gets each order, when an order is assigned, and where idle couriers are sent. Couriers drift back to their preferred area at the rate measured in the Meituan data, so a model that only works when couriers obey is caught.

This research was supported by data provided by Meituan.

This repository is a curated snapshot of the study's code, taken at commit e7fa224 of the private study repository, with a fresh history. It holds the simulator, the models, the run and analysis scripts, the tests, the figure scripts and the three pre-registrations. It also holds the aggregate results that the paper-number and figure scripts read, under `avaliacao/`: the training records of the five learned models, the first round's results and the G8 results. The episode files, the other run outputs, the decision log, the plans and the gate reviews stay in the study's private records. Comments that cite `DECISIONS.md` or another `avaliacao/` folder point to those records.

## Layout

| Path | Holds |
|---|---|
| `sim/city/` | Build of the Curitiba city model: H3 resolution-9 cells, IBGE 2022 population, road travel times, restaurant layouts |
| `sim/core/` | Simulator: demand, engine, courier idle behavior, metrics, baseline policies |
| `sim/` (other modules) | Calibration, scenarios, the episode runners (`run_cells.py` for the first round, `run_extension.py` for the extension), the analyses (`analysis.py`, `analysis_extension.py`), statistics (`stats.py`), training of the learned models (`train_*.py`), videos |
| `models/` | The published dispatch models reimplemented as policies, with one fidelity note each (`models/fidelity/`) and the trained policies (`models/trained/`) |
| `scripts/` | Data profiles, checks, pilot and G8 pipelines, paper numbers and figure data |
| `tests/` | Tests with known answers |
| `figures/` | MATLAB figure scripts; `figures/paper/` holds the Paper A figures |
| `scenarios/` | The starting layouts and the scenario manifest |
| `data/` | `README.md` describes every source; `fetch.sh` and `fetch_cnpj.sh` download the public ones; raw files are never in git |
| `preregistration*.md` | The pre-registrations of the first round and of the extension, and the R3 addendum, each with its PDF |
| `avaliacao/` | Aggregate results only: training records (`run.json`, `curve.csv`, `training.csv`), the first round's `results/`, and `20261105-1405-g8-results/` (E1, E2, the R4 block, paper numbers) |

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
