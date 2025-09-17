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
