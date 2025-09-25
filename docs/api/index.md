# API Reference

This section documents the public Python API exposed by pyOutfit. It describes the main classes, their responsibilities, configuration options, data representations, and how results are structured. The focus is on clarity and practical use within astrometric and orbit-determination workflows.

## What you will find here

- A guided description of the core classes that make up the user-facing API.
- The configuration surface for Initial Orbit Determination (IOD) and related numerical and physical filters.
- The data containers used to ingest, store, and iterate over observations and trajectory batches.
- The different orbital element families and how to interpret their fields and reference epochs.
- The observer model and ephemeris context needed by the solvers.
- Notes on performance, parallel execution, determinism, and error handling.

## Package layout (Python names)

- Environment and context: `PyOutfit` (ephemerides, error model, observatory registry).
- Observers: `Observer` (MPC-coded or custom definitions, geodetic parameters).
- IOD configuration: `IODParams` and its builder for numerical tolerances and execution mode.
- Observations and batches: `Observations` (per-trajectory), `TrajectorySet` (ID → observations mapping).
- IOD results: `GaussResult` (preliminary/corrected solution access, element extraction).
- Orbital elements: `KeplerianElements`, `EquinoctialElements`, `CometaryElements`.
- Pandas helpers: optional utilities for tabular ingestion and export.

## Conventions and units

- Angles are expressed in radians internally. Degree ingestion is supported and converted on input.
- Times are Modified Julian Date (MJD), typically in the TT scale consistent with the ephemerides.
- Distances follow conventions of the underlying Rust core: astronomical units for orbital scales and kilometers for observer elevation.
- All public classes are typed; the package ships with type stubs and a `py.typed` marker for static analysis.
- Errors from the Rust core surface as Python `RuntimeError` with descriptive messages; error variants are flattened for batch results.

## Parallelism and determinism

- Parallel execution is opt-in and controlled through `IODParams`; it is designed for large batches.
- Deterministic runs can be achieved by providing a seed where supported (e.g., batch estimation pathways).
- Heavy numerical work executes outside the Python GIL, minimizing interpreter overhead.

## Navigation

- Python package overview: [py_outfit](py_outfit.md)
- Observers and observatory registry: [observer](observer.md)
- IOD configuration parameters: [iod_params](iod_params.md)
- Gauss Initial Orbit Determination: [iod_gauss](iod_gauss.md)
- Observations container: [observations](observations.md)
- Trajectories and batch processing: [trajectories](trajectories.md)
- Orbital element families:
	- [Keplerian](orbit_type/keplerian.md)
	- [Equinoctial](orbit_type/equinoctial.md)
	- [Cometary](orbit_type/cometary.md)
- Pandas integration notes: [pandas_pyoutfit](pandas_pyoutfit.md)

## Stability and status

The API is designed to be practical and predictable, with an emphasis on scientific correctness. While the project is still evolving, changes aim to preserve user-facing stability where feasible. Type information and documentation are maintained to ease integration into existing pipelines.
