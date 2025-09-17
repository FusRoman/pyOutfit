<div align="center">

# pyOutfit

High-performance Python bindings for the **Outfit** orbit-determination engine (Initial Orbit Determination, observation ingestion, orbital element conversions & batch processing) powered by Rust + PyO3.

[![License: CeCILL-C](https://img.shields.io/badge/license-CeCILL--C-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](pyproject.toml)
[![Rust 1.82+](https://img.shields.io/badge/rust-1.82%2B-orange.svg)](Cargo.toml)
[![Build (maturin)](https://img.shields.io/badge/build-maturin-informational.svg)](https://github.com/PyO3/maturin)
[![Platform](https://img.shields.io/badge/platform-Linux%20|%20macOS%20|%20Windows-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#roadmap--status)
<!-- Uncomment once published on PyPI
[![PyPI version](https://img.shields.io/pypi/v/pyOutfit.svg)](https://pypi.org/project/pyOutfit/)
[![Downloads](https://img.shields.io/pypi/dm/pyOutfit.svg)](https://pypistats.org/packages/pyOutfit)
-->

</div>

## ✨ Overview

`pyOutfit` exposes the Rust **Outfit** crate to Python with a thin, typed interface. It enables:

* Gauss-based **Initial Orbit Determination (IOD)** with configurable numerical & physical filters.
* Manipulation of multiple orbital element representations (Keplerian, Equinoctial, Cometary).
* Efficient ingest of astrometric observations (single trajectories or large batches) with zero-copy / single-conversion paths.
* Parallel batch processing for thousands of trajectories (opt-in).
* Access & registration of observatories (MPC code lookup & custom definitions).

Rust performs all heavy numerical work; Python orchestrates workflows with minimal overhead.

## 🔍 Feature Highlights

| Area | Highlights |
|------|-----------|
| IOD | Gauss method with configurable solver tolerances & physical filters |
| Elements | Keplerian / Equinoctial / Cometary conversions & wrappers |
| Observations | NumPy ingestion in radians or degrees (with automatic conversion) |
| Performance | Optional parallel batches, detached GIL region for compute-heavy steps |
| Safety | Rust error types mapped to Python `RuntimeError` (idiomatic try/except) |
| Extensibility | Builder pattern for `IODParams` & ergonomic container types |

## 🚀 Quick Start

```bash
# (Recommended) Create & activate a virtual environment first
python3.12 -m venv .venv
source .venv/bin/activate

# Install build backend (only needed for local builds)
pip install --upgrade pip maturin

# Build and install the extension in development mode
maturin develop
```

Verify the module loads:

```bash
python -c "import py_outfit; print('Classes:', [c for c in dir(py_outfit) if c[0].isupper()])"
```

## 📦 Installation Options

Until wheels are published on PyPI, build from source:

```bash
git clone <this-repo-url>
cd pyOutfit
pip install maturin
maturin develop  # or: maturin build --release && pip install target/wheels/pyOutfit-*.whl
```

System requirements:

* Python 3.12 (matching the `pyproject.toml` requirement)
* Rust toolchain (≥ 1.82)
* C toolchain (e.g. `build-essential` on Debian/Ubuntu)

Example (Debian/Ubuntu):

```bash
sudo apt update
sudo apt install -y build-essential python3.12-dev pkg-config libssl-dev
```

Install Rust if needed: https://rustup.rs

## 🧪 Minimal End‑to‑End Example

Below: create an environment, register an observer, ingest synthetic observations, configure Gauss IOD, and estimate orbits.

```python
import numpy as np
from py_outfit import PyOutfit, Observer, IODParams, TrajectorySet

# 1. Global environment (ephemeris + error model)
env = PyOutfit("horizon:DE440", "FCCT14")

# 2. Define (or fetch) an observer
obs = Observer(longitude=12.345, latitude=-5.0, elevation=1_000.0, name="DemoSite", ra_accuracy=None, dec_accuracy=None)
env.add_observer(obs)
print(env.show_observatories())

# 3. Fake observation batch for TWO trajectories (IDs 10 & 11)
trajectory_id = np.array([10,10,10, 11,11,11], dtype=np.uint32)
ra_deg        = np.array([10.0,10.01,10.02, 180.0,180.02,180.05])  # degrees
dec_deg       = np.array([ 5.0, 5.01, 5.015, -10.0,-10.02,-10.03])  # degrees
times_mjd_tt  = np.array([60000.0,60000.01,60000.03, 60000.0,60000.02,60000.05])

# 4. Build trajectory set (degree ingestion path auto-converts to radians)
ts = TrajectorySet.trajectory_set_from_numpy_degrees(
	env,
	trajectory_id,
	ra_deg,
	dec_deg,
	error_ra_arcsec=0.3,
	error_dec_arcsec=0.3,
	mjd_tt=times_mjd_tt,
	observer=obs,
)
print(ts, "Total obs:", ts.total_observations())

# 5. Configure IOD parameters (builder pattern + parallel disabled for small sample)
params = (IODParams.builder()
		  .max_triplets(200)
		  .gap_max(2.0)
		  .do_sequential()  # or .do_parallel() for large data
		  .build())

# 6. Estimate orbits (returns (ok_dict, err_dict))
ok, errors = ts.estimate_all_orbits(env, params, seed=42)
print("Success keys:", list(ok.keys()))
print("Errors:", errors)

# 7. Inspect one result
traj_id, (gauss_res, rms) = next(iter(ok.items()))
print("Trajectory", traj_id, "elements type:", gauss_res.elements_type())
if gauss_res.keplerian():
	kep = gauss_res.keplerian()
	print("Have keplerian elements (semi-major axis etc.)")
```

## 🔧 Working with `IODParams`

```python
from py_outfit import IODParams

default_params = IODParams()            # All defaults
print(default_params.max_triplets)      # Read-only getter

custom = (IODParams.builder()
		  .max_triplets(500)
		  .aberth_eps(1e-14)
		  .do_parallel()               # enable multi-threaded batches
		  .build())
print("Parallel:", custom.do_parallel)
```

## 📊 Accessing Observations

```python
traj_keys = ts.keys()          # list of IDs
first_key = traj_keys[0]
traj = ts[first_key]           # Observations object
print(len(traj), "observations")
mjd, ra, dec, sra, sdec = traj.to_numpy()  # NumPy arrays

for (t, r, d, sr, sd) in traj:             # iteration yields tuples
	pass
```

## 🗂 API Surface (Python Names)

| Class / Function | Purpose |
|------------------|---------|
| `PyOutfit` | Global environment (ephemerides, error model, observatory catalog) |
| `Observer` | Observatory definition / MPC lookup handle |
| `IODParams` / `IODParams.builder()` | IOD configuration (physical filters, solver tolerances, parallelism) |
| `TrajectorySet` | Mapping-like container of trajectories (IDs → `Observations`) |
| `Observations` | Read-only per-trajectory access + NumPy export |
| `GaussResult` | Result wrapper (preliminary / corrected orbit + element extraction) |
| `KeplerianElements`, `EquinoctialElements`, `CometaryElements` | Different orbital element families |

## ⚙️ Performance Notes

* Core numerical routines run in Rust without the Python GIL (`py.detach`).
* Batch ingestion uses zero-copy (radian path) or a single conversion (degree path).
* Parallel processing is opt-in via `IODParams.builder().do_parallel()` to avoid contention when working with small data.
* Deterministic runs are achievable by passing a `seed` to `TrajectorySet.estimate_all_orbits`.
* Error propagation: all `OutfitError` variants surface as Python `RuntimeError` with descriptive messages.

## 🧭 Error Handling Pattern

```python
try:
	env = PyOutfit("horizon:DE440", "VFCC17")
except RuntimeError as e:
	print("Failed to init environment:", e)
```

## 🧑‍💻 Development Workflow

```bash
# 1. (one time) Setup
pip install maturin pytest

# 2. Rebuild after Rust changes
maturin develop

# 3. Run Python tests
pytest -q

# 4. Optional: run Rust unit tests (if added)
cargo test
```

### Project Layout

```
src/                 # Rust sources (PyO3 classes & bindings)
py_outfit/           # Generated Python package (stub .pyi + compiled extension)
tests/               # Python tests (pytest)
Cargo.toml           # Rust crate metadata
pyproject.toml       # Python build config (maturin backend)
```

## 🤝 Contributing

Contributions are welcome:

1. Fork & create a feature branch.
2. Add tests (Python or Rust) for new behavior.
3. Keep public Python API backwards compatible when possible.
4. Run `pytest` before opening a PR.

Feel free to open an issue for design discussions first.

## 📄 License

Distributed under the **CeCILL-C** license. See `LICENSE` for the full text.

## 🙌 Acknowledgements

Built on top of the Rust **Outfit** crate and the [PyO3](https://github.com/PyO3/pyo3) + [maturin](https://github.com/PyO3/maturin) ecosystem.

---

Questions, ideas, or issues? Open an issue or start a discussion – happy to help.
