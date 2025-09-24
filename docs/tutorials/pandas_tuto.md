# Pandas integration: vectorized IOD from DataFrames

This tutorial shows how to run Gauss IOD directly from a flat Pandas DataFrame via the `DataFrame.outfit` accessor. You will learn how to:

- initialize the environment and register the accessor,
- run the degrees+arcseconds workflow,
- use a radians workflow,
- adapt to custom column names with `Schema`,
- handle successes and errors, and join results with external metadata.

The accessor is implemented in `py_outfit.pandas_pyoutfit` and builds a `TrajectorySet` from NumPy arrays under the hood.

## Prerequisites

Importing the module registers the accessor and we create a simple observing environment:

```py linenums="1" title="Setup environment and accessor"
--8<-- "docs/tutorials/tutorial_snippets/pandas_setup.py"
```

---

## Degrees + arcseconds workflow

Your DataFrame provides `tid`, `mjd`, `ra`, `dec`. Angles are degrees and uncertainties are provided in arcseconds.

```py linenums="1" title="Minimal example (degrees + arcsec)"
--8<-- "docs/tutorials/tutorial_snippets/pandas_basic_degrees.py"
```

Notes

- Internally, RA/DEC are converted once to radians; uncertainties are converted from arcsec to radians using `RADSEC`.
- Use `rng_seed` for deterministic exploration.

---

## Radians workflow

Supply angles and uncertainties in radians to avoid conversions.

```py linenums="1" title="Radians end-to-end"
--8<-- "docs/tutorials/tutorial_snippets/pandas_radians_workflow.py"
```

---

## Custom column names with Schema

If your DataFrame uses different names, provide a `Schema` mapping.

```py linenums="1" title="Adapt to arbitrary column names"
--8<-- "docs/tutorials/tutorial_snippets/pandas_custom_schema.py"
```

---

## Handling successes and errors, joining metadata

The accessor returns a success table and may append error rows. You can split and join with other tables.

```py linenums="1" title="Post-processing: statuses and joins"
--8<-- "docs/tutorials/tutorial_snippets/pandas_handle_status.py"
```

---

## Caveats and reproducibility

- Known backend caveat: due to an upstream issue in batch RMS correction, per‑observation uncertainties may be modified in place during a run. Re-using the same `Observations` instance and calling `estimate_best_orbit` repeatedly can yield different RMS between calls. When using the accessor this is typically not visible, but for strict reproducibility recreate the underlying `TrajectorySet` or source DataFrame before repeated runs.
- `rng_seed` ensures deterministic random sampling but does not prevent in-place mutations from earlier runs.

## See also

- API reference: `Pandas Integration`
- Core container: `TrajectorySet`
- Configuration: `IODParams` tutorial

