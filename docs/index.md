# pyOutfit

High-performance Python bindings for the Outfit orbit-determination engine. pyOutfit provides a thin, typed interface to the Rust core to perform initial orbit determination, manipulate orbital elements, ingest astrometric observations, and process large batches efficiently.

## What this project is

pyOutfit is a Python package that exposes the Rust Outfit crate through PyO3. It brings robust, numerically stable routines for orbit determination and observation handling to Python workflows while keeping the heavy computation in Rust. The design emphasizes reliability, performance, and a clean user-facing API that integrates well with scientific Python stacks.

## Purpose and scope

The package focuses on initial orbit determination (IOD) based on the classical Gauss method, conversions between orbital element representations, ingestion of astrometric observations from multiple sources, and scalable batch processing. It is intended for researchers and engineers working on astrometry pipelines, moving-object detection, and orbit characterization.

## Core capabilities

- Initial Orbit Determination using the Gauss method, with configurable numerical tolerances and physical filters.
- Multiple orbital element families with conversions: Keplerian, Equinoctial, and Cometary.
- Observation ingestion from common astronomy formats and in-memory arrays with minimal overhead.
- Parallel batch execution for large datasets, with deterministic behavior via seed control.
- Observer management, including MPC-coded observatories and custom definitions.
- Typed Python interface with docstrings, type stubs, and consistent error mapping.

## Architecture at a glance

- Rust core (Outfit crate) implements numerical algorithms, ephemerides access, reference frame transformations, and data structures.
- Python bindings (PyO3) expose high-level classes and functions, keeping data copies and conversions to a minimum.
- Optional parallelism in the Rust layer leverages multi-core systems transparently to Python users.
- The interface is designed to be predictable and stable for integration into existing pipelines.

## Data and models

- Orbital elements: Keplerian, Equinoctial, and Cometary families with consistent units and reference epochs.
- Observations: right ascension, declination, timing, and uncertainties, with support for degrees or radians ingestion paths.
- Reference frames and corrections: precession, nutation, aberration, and observer geometry are handled in the Rust core.
- Ephemerides: planetary positions are obtained from high-accuracy JPL series (e.g., DE440) via the Outfit crate.

## Observation ingestion and batches

- Single-trajectory and multi-trajectory ingestion are both supported.
- Batch containers group observations by trajectory identifier for efficient processing.
- Readers and adapters cover traditional astronomy formats (e.g., MPC 80-column and ADES XML) and tabular data sources (e.g., Parquet), alongside direct NumPy-based ingestion.

## Performance and reliability

- Numerical kernels run in Rust without the Python GIL, minimizing overhead.
- Parallel execution is opt-in to avoid contention on small datasets and can be toggled via configuration.
- Deterministic runs are available by providing a random seed when executing batch estimations.
- Errors from the Rust core are mapped to idiomatic Python exceptions with informative messages.

## Requirements and compatibility

- Python 3.12.
- A recent Rust toolchain matching the Outfit crate minimum supported version.
- Linux (POSIX) is the primary target platform for packaged distributions.
- The package is distributed with type information (py.typed) and Python type stubs.

## Project status

The project is in active development and aims for scientific correctness, clear documentation, and practical performance. The public Python API is designed to be stable where possible; incremental improvements and extensions are expected as the Rust core evolves.

## Documentation map

- Python package overview: [PyOutfit](api/py_outfit.md)
- Observer definitions and utilities: [Observer](api/observer.md)
- IOD parameters and configuration: [IODParams](api/iod_params.md)
- Initial Orbit Determination (Gauss): [IODGauss](api/iod_gauss.md)
- Observations and containers: [Observations](api/observations.md), [Trajectories](api/trajectories.md)
- Orbital element types: [Keplerian](api/orbit_type/keplerian.md), [Equinoctial](api/orbit_type/equinoctial.md), [Cometary](api/orbit_type/cometary.md)
- Pandas integration notes: [Pandas Integration](api/pandas_pyoutfit.md)

## Heritage and licensing

pyOutfit builds on the Outfit Rust crate, which is a modern reimplementation of classical Fortran-based orbit determination approaches. The package is distributed under the CeCILL-C license. See the repository license file for details.