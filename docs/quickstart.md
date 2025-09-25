# Quickstart

This quickstart shows the smallest end-to-end example: create an environment, define (or fetch) an observer, ingest three astrometric observations for a single trajectory, and run a Gauss Initial Orbit Determination (IOD) to obtain a preliminary orbit.

If you have not installed the package yet, see the Installation page first.

## 1. Import and environment

The environment holds ephemerides and the astrometric error model. The first call may trigger a download of planetary ephemerides (JPL DE440) depending on cache state.

```py linenums="1" title="Environment initialization"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:env_init"
```

## 2. Define or fetch an observer

You can supply your own geodetic coordinates or use an MPC code if available. Elevation is expected in kilometers.

```py linenums="1" title="Observer creation"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:observer_init"
```

## 3. Prepare a minimal observation set

We create three observations (the minimum for Gauss IOD) at distinct times. Use either the degree ingestion path (shown) or radians. Times are MJD(TT). Uncertainties are 1-sigma values (arcseconds in the degree path).

```py linenums="1" title="Setup small data"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:minimal_data"
```

## 4. Build a TrajectorySet and extract the single trajectory

The TrajectorySet groups observations by ID. Even for one object it is the simplest way to obtain an `Observations` handle that exposes `estimate_best_orbit`.

```py linenums="1" title="Push data into a trajectory container"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:build_trajectoryset"
```

## 5. Configure IOD parameters

Use the builder to tweak only what you need. Here we disable noise realizations for determinism and cap the search space for speed.

```py linenums="1" title="IOD Parameter configuration"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:configure_iodparams"
```

## 6. Run Gauss IOD for the single trajectory

`estimate_best_orbit` returns a `(GaussResult, rms)` pair. The RMS is an internal quality metric (angular residual scale).

```py linenums="1" title="Initial orbit determination"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:estimate_orbit"
```

## 7. Inspect the resulting orbital elements

Depending on internal selection, a Keplerian, Equinoctial, or Cometary set is produced. Access helpers return `None` when the family does not match.

```py linenums="1" title="inspect results"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py:inspect_results"
```

## 8. Full minimal script (copy & run)

```py linenums="1" title="Full quickstart script (copy and past)"
--8<-- "docs/tutorials/tutorial_snippets/quickstart_snippet.py"
```

At the end of the run, typical console output looks like:
```text
Number of observations: 3
RMS: 0.62            # angular residual scale (approx.)
Elements family: keplerian
Semi-major axis (AU): 2.72084815
Eccentricity: 0.27511014
Inclination (rad): 0.27433785 (~15.7 deg)
```

Note: Exact numbers can vary slightly (last decimals) depending on platform, floating‑point rounding, and random seed (if noise realizations were enabled). Differences at the 1e-9–1e-12 level are normal.

## 9. Next steps

Proceed to:

- Tutorials for batch processing and parameter tuning.
- API reference (`IODParams`, `GaussResult`, orbital element classes) for deeper control.

If your first run downloads ephemerides, subsequent runs should start much faster.

