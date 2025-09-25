# Working with orbit results (Gauss IOD)

This tutorial shows how to consume the successful results returned by `TrajectorySet.estimate_all_orbits(...)` and how to navigate the different orbital element families produced by the Gauss solver.

You will learn how to:

- iterate over the successful results map and inspect `GaussResult` objects,
- check whether the result is a preliminary or corrected orbit,
- extract the concrete orbital elements (Keplerian, Equinoctial, or Cometary),
- convert between element families when supported,
- serialize results to dictionaries for logging or downstream processing.

> The examples assume you already ran batch IOD and obtained `(ok, errors)` from `estimate_all_orbits(env, params, ...)`. See the Trajectories and IODParams tutorials for how to configure and run the solver.

??? example "Reference: run_iod() used by the snippets"
    The code examples below call a shared helper that builds a small dataset, runs batch IOD,
    and returns `(ok, errors)`. For completeness, here is the helper once:

    ```py linenums="1" title="common_tuto.run_iod()"
    --8<-- "docs/tutorials/tutorial_snippets/common_tuto.py"
    ```

---

## Iterate over successful results

```py linenums="1" title="Iterate results"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_iterate.py"
```

- `obj_id` is the same identifier you used when ingesting trajectories (int or str).
- `rms` is the post-fit residual RMS (radians) computed over the chosen time window.

---

## Determine the element family

```py linenums="1" title="Family and stage"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_family_stage.py"
```

---

## Extract concrete elements

Use the typed accessors; they return `None` if the stored family differs.

```py linenums="1" title="Extract typed elements"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_extract.py"
```

Units reminder:
- Epochs are MJD (TDB). Angles are radians. Distances are AU.

---

## Convert between element families

Conversions are provided by the element classes themselves.

- Keplerian → Equinoctial:

```py linenums="1" title="Convert between families"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_convert.py"
```

> Note: parabolic cometary elements (e = 1) cannot be converted by these helpers and will raise a `ValueError`.

---

## Structured dict serialization

Every `GaussResult` can be converted to a plain dictionary for easy logging and JSON export:

```py linenums="1" title="Structured dict serialization"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_to_dict.py"
```

Example for a Keplerian result:

```python
{
    'stage': 'corrected', 
    'type': 'keplerian', 
    'elements': {
        'reference_epoch': 58794.29503864708, 
        'semi_major_axis': 2.618543557694562, 
        'eccentricity': 0.2917924222538649, 
        'inclination': 0.23168624097364912, 
        'ascending_node_longitude': 0.20856161706357348, 
        'periapsis_argument': 6.264575557486691, 
        'mean_anomaly': 0.29001350766154466
    }
}
```

---

## Putting it together: filter, convert, export

Below is a compact pattern you can adapt to your pipeline:

```py linenums="1" title="Filter, convert, export"
--8<-- "docs/tutorials/tutorial_snippets/orbit_results_export.py"
```

---

## Tips

- Always check the element family via `elements_type()` before calling accessors; the typed helpers return `None` when mismatched.
- When you need a single canonical representation, prefer converting to Keplerian where defined, but keep native cometary elements for `e = 1`.
- Store the RMS alongside the elements; it’s a useful quality metric for ranking and filtering.
- If you run `estimate_best_orbit` repeatedly on the same `Observations` instance, be aware of the in-place uncertainty scaling caveat described in the Observations tutorial; recreate the object for bitwise reproducibility.
