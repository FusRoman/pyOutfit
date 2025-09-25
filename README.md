<div align="center">

# pyOutfit

High-performance Python bindings for the **Outfit** orbit-determination engine (Initial Orbit Determination, observation ingestion, orbital element conversions & batch processing) powered by Rust + PyO3.

<!-- pyOutfit badges -->
<p>
	<strong>pyOutfit</strong><br/>
	<a href="https://github.com/FusRoman/pyOutfit/actions/workflows/ci.yml"><img src="https://github.com/FusRoman/pyOutfit/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"/></a>
	<a href="https://pypi.org/project/py-outfit/"><img src="https://img.shields.io/pypi/v/py-outfit.svg" alt="PyPI version"/></a>
	<a href="https://FusRoman.github.io/pyOutfit/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-success.svg" alt="Documentation"/></a>
	<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12"/></a>
	<a href="https://github.com/PyO3/maturin"><img src="https://img.shields.io/badge/build-maturin-informational.svg" alt="Build (maturin)"/></a>
	<a href="LICENSE"><img src="https://img.shields.io/badge/license-CeCILL--C-blue.svg" alt="License: CeCILL-C"/></a>
</p>

<!-- Upstream Outfit (Rust core) badges -->
<p>
	<strong>Upstream Outfit (Rust core)</strong><br/>
	<a href="https://crates.io/crates/outfit"><img src="https://img.shields.io/crates/v/outfit.svg" alt="crates.io"/></a>
	<a href="https://docs.rs/outfit"><img src="https://docs.rs/outfit/badge.svg" alt="docs.rs"/></a>
	<a href="Cargo.toml"><img src="https://img.shields.io/badge/rust-1.82%2B-orange.svg" alt="MSRV"/></a>
</p>

<!-- (Optional) Downloads badge once volume is meaningful
<a href="https://pypistats.org/packages/pyOutfit"><img src="https://img.shields.io/pypi/dm/pyOutfit.svg" alt="Downloads"/></a>
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
maturin develop  # or: maturin build --release && pip install target/wheels/py_outfit-*.whl
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

https://github.com/FusRoman/pyOutfit/blob/f58071657e896f4dc2cf9ee3f7b894b81593c311/docs/tutorials/tutorial_snippets/quickstart_snippet.py#L1-L102

## 🔧 Working with `IODParams`

https://github.com/FusRoman/pyOutfit/blob/f58071657e896f4dc2cf9ee3f7b894b81593c311/docs/tutorials/tutorial_snippets/iod_params_parallel.py#L1-L10

## 📊 Accessing Observations

https://github.com/FusRoman/pyOutfit/blob/f58071657e896f4dc2cf9ee3f7b894b81593c311/docs/tutorials/tutorial_snippets/trajectories_estimate_single.py#L108-L111

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
