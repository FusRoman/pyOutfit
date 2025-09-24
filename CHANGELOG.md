# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog and this repository follows semantic versioning.

## [1.0.0] - 2025-09-17
### Added
- Initial stable release of pyOutfit (Rust core with Python bindings).
- Reimplementation of OrbFit IOD functionality in Rust.
- Core Rust modules:
  - `iod_gauss.rs` — Gauss initial orbit determination implementation and result types.
  - `iod_params.rs` — Parameter builder and validation utilities for IOD routines.
  - `observations.rs` — In-memory observation batch representation and helpers.
  - `observer.rs` — `Observer` utilities for geodetic conversions and observer positions.
  - `trajectories.rs` — Trajectory batch readers and IOD orchestration helpers.
  - `orbit_type/keplerian.rs`, `equinoctial.rs`, `cometary.rs` — Orbital element representations and conversions.
  - `lib.rs` — crate entrypoint and Python binding exports.
- Pandas integration: `DataFrame.outfit` accessor in `py_outfit.pandas_pyoutfit` with
  `estimate_orbits(...)` and a `Schema` helper for column remapping. Supports both
  degrees+arcseconds and radians workflows, and uses a single `Observer` for the set.
- Observatory-aware helpers and estimation methods:
  - Trajectory ingestion builders accept an `Observer` (single-station workflow) and
    `TrajectorySet.estimate_all_orbits(...)` performs batch IOD using that site.
  - Single-object `Observations.estimate_best_orbit(env, params, seed=...)` mirrors the
    batch path for a single trajectory.
  - Display helpers resolving observatory names via the environment:
    `show_with_env`, `table_wide_with_env`, `table_iso_with_env`.
- User documentation:
  - New tutorial “IOD from trajectories” (loading from MPC/ADES, NumPy arrays, batch/single IOD).
  - New tutorial “Working with orbit results” (inspect `GaussResult`, extract/convert element sets, export).
  - New tutorial “Using pandas with pyOutfit” (vectorized IOD from DataFrames via the accessor).
  Each tutorial’s code blocks were externalized into standalone, runnable Python snippets under
  `docs/tutorials/tutorial_snippets/` and included via the snippets macro.
- CI: Added a job “Run documentation Python snippets” that builds the extension with `maturin
  develop` and executes every `docs/tutorials/tutorial_snippets/*.py` to keep examples up to date.

### Python bindings
- Stub type hinting files (`.pyi`) and `py.typed` are included to provide static typing / IDE support:
  - `py_outfit.pyi`, `iod_gauss.pyi`, `iod_params.pyi`, `observations.pyi`, `observer.pyi`, `trajectories.pyi`, plus `orbit_type` submodule `.pyi` files.

### Observations & Input formats
- Support for multiple observation formats and batch ingestion (MPC 80-column, ADES XML, Parquet planned via modular readers).
- In-memory batch representation suitable for bulk IOD processing.

### Execution and parallelism
- Support for sequential and parallel execution modes (Rayon) with configurable thread counts and reproducible SplitMix64-based seeds.
- Progress reporting and cancellation hooks in executor utilities.

### Error handling & robustness
- Rich `OutfitError` variants for explicit failure modes (e.g., `NoFeasibleTriplets`, `NonFiniteScore`).
- Serialization helpers to flatten errors for batch result buckets.

### Testing
- Python-side tests (pytest) covering the public Python API and integration points.

### Build & Development
- Cargo manifests (`Cargo.toml`, `Cargo.lock`) and Python packaging (`pyproject.toml`, `pdm.lock`) included to build the Rust crate and Python wheel/extension.
- `target/` contains compiled artifacts for debug and release builds when built locally.

### Misc
- Licensing: `LICENSE` at repository root.
- Examples and incremental builds live under `target/` in build subdirectories.

### Notes and Implementation Details
- Units and conventions: consistent handling of AU, radians, and MJD across element representations.
- Conversion utilities for precession, nutation and planetary ephemerides (JPL DE440 integration referenced in design notes).
- Python integration carefully handles GIL release for long-running operations and provides pyi stubs for comfortable IDE usage.

## Unreleased
No unreleased changes at the time of 1.0.0.

---
