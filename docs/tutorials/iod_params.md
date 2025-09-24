# IODParams: configuring Gauss IOD

This tutorial explains the purpose of `IODParams`, how it shapes the Gauss Initial Orbit Determination (IOD) pipeline, and practical ways to configure it for different datasets. The goal is to keep configuration centralized, reproducible, and explicit.

## What IODParams is for

`IODParams` collects all tunable parameters used by the Gauss IOD solver. It controls how observation triplets are selected, how Monte Carlo perturbations are applied, which physical and numerical filters are enforced, and how candidate solutions are ranked by RMS. The same parameter object can be reused across many trajectories and batches for consistent behavior.

At a high level, the pipeline proceeds by generating triplets from time-ordered observations, expanding them via controlled noise, solving the Gauss polynomial to obtain candidate orbits, filtering candidates by physical plausibility and numerical quality, and selecting the best solution by RMS over a controlled time window.

## Getting a configuration

You can either instantiate `IODParams()` to get the defaults, or use the fluent builder to override only what you need before producing an immutable configuration.

```py linenums="1" title="IODParams defaults"
--8<-- "docs/tutorials/tutorial_snippets/iod_params_defaults.py"
```

The defaults are conservative and intended to work on a wide range of small datasets. For larger data or specific science goals, it is common to change the number of triplets, the extrapolation window for RMS, and parallel execution.

## Turning on parallel execution

Parallel execution can reduce wall-clock time for many trajectories. The advisory flag is carried by `IODParams` and consumed by higher-level APIs that accept it.

```py linenums="1" title="Requesting parallel execution"
--8<-- "docs/tutorials/tutorial_snippets/iod_params_parallel.py"
```

When processing many trajectories, prefer larger batch sizes (for example, 500–1000), because the overhead of assembling and scheduling batches can dominate when batches are too small. In sequential mode, cooperative cancellation (Ctrl‑C) remains responsive; in parallel mode, cancellation is not supported and you may need to terminate the process to stop long runs.

## Physical and numerical filters

The Gauss pipeline produces multiple mathematical candidates per triplet. `IODParams` constrains the search to physically plausible and numerically stable regions, which prevents spurious or degenerate solutions.

```py linenums="1" title="Plausibility and solver tolerances"
--8<-- "docs/tutorials/tutorial_snippets/iod_params_filters.py"
```

- Physical constraints (eccentricity, perihelion, heliocentric distance bounds, minimum topocentric distance) help reduce non-physical or near-observer pathologies.
- Numerical tolerances for the Aberth–Ehrlich polynomial solver, Newton steps, and the universal Kepler solver govern convergence and robustness. The parameter `root_imag_eps` controls how small the imaginary part of a complex root must be to treat it as effectively real when selecting roots of the 8th‑degree Gauss polynomial. The bounds `r2_min_au` and `r2_max_au` apply plausibility constraints to the central heliocentric distance used during root selection. The parameter `min_rho2_au` rejects spurious geometries by enforcing a minimum topocentric distance at the central epoch.

## RMS window and triplet selection

RMS evaluation is carried out over a time window derived from the triplet span and clamped to a minimum. Triplet generation itself is constrained by minimum and maximum spans and a target spacing.

```py linenums="1" title="RMS window and triplet spacing"
--8<-- "docs/tutorials/tutorial_snippets/iod_params_rms_window.py"
```

The RMS window is derived from the triplet span and clamped to a minimum: `dt_window = (last − first) × extf`, with the final window ensured to be at least `dtmax`. Use a negative `extf` to trigger a broad fallback window when observations are sparse or irregularly sampled. Increase `dtmax` if the default minimum window is too short for your cadence.

## Practical guidance

- Prefer the builder for clarity and reproducibility; only set what you need.
- Start from defaults, adjust triplet and RMS controls first, then refine physical and numerical filters.
- Enable parallelism for large batches; keep sequential mode for small, interactive runs so that cancellation remains responsive.
- Use a fixed seed when you need bitwise reproducibility across runs.

## Validation and special cases

`IODParams` is validated when built to prevent inconsistent configurations. Time spans must be non‑negative; tolerances must be positive; and plausibility bounds must be ordered and strictly positive. Two special cases are worth noting. First, setting `n_noise_realizations = 0` disables noisy clones and uses only the original triplet, which can be useful for speed‑of‑light checks or deterministic baselines. Second, `max_obs_for_triplets < 3` is accepted and behaves like `3`, effectively selecting first/middle/last so that at least one valid triplet is always available. Negative `extf` activates the broad fallback window; regardless of `extf`, the RMS window is clamped to be at least `dtmax`.

## Tuning cheat sheet

- Too many spurious candidates or unstable solutions: tighten `max_ecc`, decrease `r2_max_au`, increase `min_rho2_au`, or reduce `root_imag_eps`.
- Convergence issues on some datasets: raise `aberth_max_iter` moderately and relax `aberth_eps` slightly; check `newton_eps`/`newton_max_it` and `kepler_eps`.
- Sparse or irregular sampling: use a negative `extf` or increase `dtmax`; increase `dt_min` to avoid ultra‑short triplets.
- Large volume batches: enable `.do_parallel()` and increase `batch_size`; prefer larger batch sizes (hundreds to a thousand) to amortize scheduling overhead.
