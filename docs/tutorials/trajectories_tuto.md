# Trajectories: loading data and running batch IOD

This tutorial shows how to work with `TrajectorySet`, the container for many objects with time‑ordered astrometric observations. You will learn how to:

- import trajectories from files (MPC 80‑column and ADES),
- build trajectories from in‑memory NumPy arrays,
- estimate preliminary orbits for all trajectories or just one.

The heavy lifting is performed by the Rust engine; the Python API keeps things concise and composable.

## Prerequisites

You will need a global environment and at least one observing site:

```py linenums="1" title="Register an observing site"
--8<-- "docs/tutorials/tutorial_snippets/observer_registration.py"
```

> Units used in this API: angles are radians unless stated otherwise; epochs are MJD (TT, days); uncertainties may be provided in arcseconds for convenience where noted.

---

## Import from files

### MPC 80‑column

Create a set from a single MPC 80‑column file, or append into an existing set.

```py linenums="1" title="From MPC 80-column"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_from_mpc_80col.py"
```

Notes

- Input parsing mirrors the Rust engine. Avoid ingesting the same file twice: no de‑duplication is performed.

### ADES (JSON or XML)

When creating from ADES, you can provide global uncertainties (arcsec) if they are not specified per row.

```py linenums="1" title="From ADES (JSON/XML)"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_from_ades.py"
```

---

## Build from in‑memory arrays

Two ingestion helpers are available. Use degrees/arcseconds for convenience, or supply radians for a zero‑copy path.

### Degrees + arcseconds (converted once to radians)

```py linenums="1" title="From NumPy (degrees + arcsec)"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_from_numpy_degrees.py"
```

### Radians (zero‑copy)

```py linenums="1" title="From NumPy (radians, zero-copy)"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_from_numpy_radians.py"
```

---

## Estimate orbits

You can estimate preliminary orbits for all trajectories in a set, or for a single trajectory.

### Batch over all trajectories

```py linenums="1" title="Batch IOD across the set"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_estimate_all.py"
```

Notes

- In sequential mode, pressing Ctrl‑C returns partial results collected so far.
- If `.do_parallel()` is enabled in `IODParams`, cancellation is not available.
- Set `seed` for deterministic noise sampling and triplet exploration.

### One trajectory only

Use the dict‑like access to get an `Observations` view, then call its single‑object API.

```py linenums="1" title="Single trajectory IOD"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_estimate_single.py"
```

---

## Caveats and reproducibility

- Known caveat: due to an upstream issue in the backend’s batch RMS correction, per‑observation uncertainties may be modified in place during a run. Calling `estimate_best_orbit` multiple times on the same `Observations` instance can yield different RMS values across calls. As a temporary workaround, recreate the `Observations` (or `TrajectorySet`) before each repeated estimation when you need strict reproducibility.
- Providing a `seed` makes noise sampling deterministic but does not prevent such in‑place mutations.

---

## See also

- API reference: `py_outfit.trajectories.TrajectorySet`
- Configuration: `IODParams` tutorial for tuning Gauss IOD
- High‑level snippet used in examples:

```py linenums="1" title="Overview"
--8<-- "docs/tutorials/tutorial_snippets/trajectories_overview.py"
```

