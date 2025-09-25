# pyOutfit Environment

This tutorial introduces the `PyOutfit` environment object and explains its role as the central coordination point for ephemerides, error models, and observatory management. It also outlines how the environment interacts with observations and batch orbit determination.

## Purpose of `PyOutfit`

`PyOutfit` encapsulates the configuration needed by the Outfit core engine to perform initial orbit determination and related computations. It holds the selected planetary ephemerides, the astrometric error model, and a registry of observatories. Other components, such as `TrajectorySet`, rely on an initialized environment to resolve observer geometry, reference frames, and numerical settings consistently.

In typical workflows, a single `PyOutfit` instance is created at the beginning of a session or pipeline and passed to ingestion and batch-processing functions. This pattern ensures consistent context across all computations and avoids duplicating configuration.

## Key responsibilities

- Manage ephemerides selection (e.g., DE440) used for precise solar-system positions.
- Provide a registry for `Observer` definitions, either fetched from MPC codes or created manually.
- Serve as a context object for ingestion of observations and for batch estimation of orbits.
- Expose convenience utilities for listing and validating available observatories.

## Typical usage pattern

- Initialize the environment with an ephemerides selector and an astrometric error model string.
- Register at least one `Observer` that represents the observing site used in your data.
- Ingest observations into a `TrajectorySet`, using either radian-based zero‑copy arrays, degree-based arrays with conversion, or supported file formats.
- Configure `IODParams` and run batch Gauss IOD, passing the environment and parameters.

## Example snippets

Below are non-executable snippets demonstrating the expected structure of a session. The code is provided in separate files and included here for readability.

### Environment initialization

```py linenums="1" title="Minimal environment setup"
--8<-- "docs/tutorials/tutorial_snippets/environment_init.py"
```

1. The constructor accepts two strings: an ephemerides selector and an astrometric error model. The ephemerides selector uses the format "{source}:{version}" and recognizes two backends: "horizon" for legacy JPL DE binaries and "naif" for NAIF SPK/DAF kernels. Examples include "horizon:DE440" and "naif:DE440". The resolved file is stored under the OS cache (e.g., ~/.cache/outfit_cache/jpl_ephem/…), and when the build enables JPL downloads, a missing file is fetched automatically; otherwise an error is raised. The error model selects per‑site RA/DEC bias and RMS tables used during orbit determination. Supported names include "FCCT14", "VFCC17", and "CBM10"; unknown names default to "FCCT14". These two parameters define the numerical and physical context shared by ingestion and IOD routines.

### Observer registration

```py linenums="1" title="Observer registration"
--8<-- "docs/tutorials/tutorial_snippets/observer_registration.py:observer_simple_init"
```

### Fetching an observer from an MPC code

Often you already know the MPC observatory code (e.g. "I41" for ZTF at Palomar, "807" for Cerro Paranal, etc.). Instead of manually constructing an `Observer`, you can request a ready‑made instance from the internal registry using `get_observer_from_mpc_code`.

On its first use the environment fetches and parses the MPC Observatory Codes HTML page (ObsCodes list) from the Minor Planet Center. The resulting table is cached in-memory for the remainder of the process, so subsequent lookups do not re-contact the network. If the network is unavailable on the very first lookup, an exception will be raised. Unknown codes also raise a `ValueError` (wrapping a Rust error). Retrieved observers can be used immediately for ingestion; explicit re‑registration is not required unless you are mixing them with custom user-defined sites.

```py linenums="1" title="Fetch from MPC"
--8<-- "docs/tutorials/tutorial_snippets/observer_registration.py:from_mpc_code"
```

Notes:

- Returned observers are immutable handles exposing their geometry to the Rust core; you do not modify longitude/latitude/elevation after creation.
- If you need to introduce a completely custom site not present in the catalog, build an `Observer` manually and register it (see the previous section snippet) before ingestion.

## Notes on configuration

- The ephemerides selector is a string understood by the Outfit core; consult the API reference for supported values. A common choice is an identifier referring to JPL DE series. The error model string controls how observational uncertainties are interpreted and propagated; unknown strings default to a standard model.
- The environment’s observatory registry is independent of trajectory ingestion. Multiple observers can be registered, but an ingestion call typically associates a single observer with the new data. If observations originate from multiple sites, separate ingestion steps or containers are recommended.
- `PyOutfit` does not itself perform orbit determination; instead, it supplies the context required by `TrajectorySet.estimate_all_orbits` and related functions. This separation keeps configuration centralized and computation modules focused.

## Reliability and performance considerations

- The environment is lightweight to construct and is intended to be reused. Creating many separate environments for a single batch is unnecessary.
- Numerical work is performed in Rust and detached from the Python GIL. Parallel execution can be enabled through IOD configuration and is generally beneficial for large batches.
- Deterministic operation is available by providing a random seed to batch execution routines that support it.

## Where to go next

- Consult the API pages for `PyOutfit` and `Observer` to explore available methods and parameters.
