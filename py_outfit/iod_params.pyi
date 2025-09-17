class IODParams:
    """
    Configuration for Gauss Initial Orbit Determination (IOD).

    Purpose
    -----------------
    Centralizes all tunable parameters used by the Gauss pipeline to:
    - Select and filter candidate observation triplets (time spans, downsampling, maximum counts),
    - Apply Monte Carlo perturbations to simulate astrometric noise,
    - Enforce physical plausibility constraints (eccentricity, perihelion, distance bounds, geometry),
    - Adjust numerical tolerances for Newton–Raphson and root filtering,
    - Control the RMS evaluation time window over the observation arc,
    - Control Gauss polynomial solving (Aberth iterations/eps; real-root acceptance),
    - Cap the number of admissible solutions scanned.

    Pipeline overview (context)
    -----------------
    1) Triplet generation — constrained by `dt_min`, `dt_max_triplet`, `optimal_interval_time`.
       Oversized datasets may be downsampled to `max_obs_for_triplets` before triplet selection.
    2) Monte Carlo perturbation — each triplet is expanded into `n_noise_realizations` copies
       drawn from Gaussian perturbations scaled by `noise_scale`.
    3) Orbit computation & filtering — candidate orbits are produced by the Gauss solver and
       filtered by physical bounds (`max_ecc`, `max_perihelion_au`, `r2_min_au`, `r2_max_au`,
       `min_rho2_au`) and numerical criteria (`newton_eps`, `newton_max_it`, `root_imag_eps`,
       `aberth_max_iter`, `aberth_eps`, `kepler_eps`). Up to `max_tested_solutions` are retained.
    4) RMS evaluation — candidates are scored by RMS residuals in a window derived from
       `extf × (triplet span)` and clamped to at least `dtmax`. Lowest RMS wins.

    Defaults
    -----------------
    The following are the **exact** default values (Rust `Default`):
    - Triplet / MC:
      * `n_noise_realizations`: 20
      * `noise_scale`: 1.0
      * `extf`: -1.0  (negative means “broad fallback window”; see Notes)
      * `dtmax`: 30.0  (days)
      * `dt_min`: 0.03  (days)
      * `dt_max_triplet`: 150.0  (days)
      * `optimal_interval_time`: 20.0  (days)
      * `max_obs_for_triplets`: 100
      * `max_triplets`: 10
      * `gap_max`: 8/24  (days; 8 hours)

    - Physical filters:
      * `max_ecc`: 5.0
      * `max_perihelion_au`: 1.0e3
      * `min_rho2_au`: 0.01  (AU)

    - Heliocentric r2 bounds:
      * `r2_min_au`: 0.05  (AU)
      * `r2_max_au`: 200.0  (AU)

    - Gauss polynomial / solver:
      * `aberth_max_iter`: 50
      * `aberth_eps`: 1.0e-6
      * `kepler_eps`: 1e3 * f64::EPSILON  (≈ 2.22e-13 on 64-bit IEEE754)

    - Numerics:
      * `newton_eps`: 1.0e-10
      * `newton_max_it`: 50
      * `root_imag_eps`: 1.0e-6

    - Multi-threading (feature-gated in Rust):
      * `batch_size`: 4  (only effective if the crate is built with `parallel/rayon`)

    Notes
    -----------------
    - RMS window:
        dt_window = (triplet_last − triplet_first) × extf,
        then clamped so dt_window ≥ dtmax.
      If `extf < 0`, the implementation uses a broad fallback (e.g., a multiple of the full dataset span).
    - Geometry: `min_rho2_au` is a **topocentric** distance constraint (central epoch) to avoid
      near-observer pathologies.
    - Root selection: `r2_min_au ≤ r2_max_au` are plausibility bounds for the **central heliocentric distance**
      used while selecting roots of the degree-8 distance polynomial.
    - Typical constraints: `max_ecc ≥ 0`, `max_perihelion_au > 0`, `min_rho2_au > 0`,
      `aberth_max_iter ≥ 1`, `aberth_eps > 0`, `kepler_eps > 0`, `newton_eps > 0`, `newton_max_it ≥ 1`,
      `root_imag_eps ≥ 0`, `max_tested_solutions ≥ 1`.

    See also
    -----------------
    * `TrajectorySet.estimate_all_orbits` — batch IOD entry point consuming these params.
    * Gauss solver & results (`GaussResult`) in the Outfit core.
    """

    def __init__(self) -> None: ...
    @staticmethod
    def builder() -> "IODParamsBuilder":
        """
        Create a new `IODParamsBuilder` initialized with the **Default** values listed above.

        Return
        ----------
        * A fresh `IODParamsBuilder` ready for fluent, chainable configuration.
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

    # --- Read-only getters (mirror the Rust struct fields) ---

    # Triplet generation / Monte Carlo
    @property
    def n_noise_realizations(self) -> int:
        """Number of Monte Carlo perturbations per original triplet. **Default:** 20."""
        ...

    @property
    def noise_scale(self) -> float:
        """Scale applied to nominal RA/DEC uncertainties (1.0 ⇒ nominal). **Default:** 1.0."""
        ...

    @property
    def extf(self) -> float:
        """
        Extrapolation factor for the RMS evaluation window:
        `dt_window = (triplet span) × extf`, then clamped so `dt_window ≥ dtmax`.
        Negative values trigger a broad fallback window. **Default:** -1.0.
        """
        ...

    @property
    def dtmax(self) -> float:
        """Floor (days) for the RMS evaluation window. **Default:** 30.0."""
        ...

    @property
    def dt_min(self) -> float:
        """
        Minimum allowed span (days) between the **first** and **last** observations in a triplet.
        **Default:** 0.03.
        """
        ...

    @property
    def dt_max_triplet(self) -> float:
        """Maximum allowed span (days) within any candidate triplet. **Default:** 150.0."""
        ...

    @property
    def optimal_interval_time(self) -> float:
        """Target intra-triplet spacing (days) to favor well-separated observations. **Default:** 20.0."""
        ...

    @property
    def max_obs_for_triplets(self) -> int:
        """Cap on observations used to build triplets (with uniform downsampling if exceeded). **Default:** 100."""
        ...

    @property
    def max_triplets(self) -> int:
        """Maximum number of triplets evaluated per trajectory (post-filter). **Default:** 10."""
        ...

    @property
    def gap_max(self) -> float:
        """Maximum allowed intra-batch time gap (days) for RMS calibration. **Default:** 8/24 (≈ 0.3333)."""
        ...

    # Physical plausibility / filtering
    @property
    def max_ecc(self) -> float:
        """Maximum accepted eccentricity. **Default:** 5.0."""
        ...

    @property
    def max_perihelion_au(self) -> float:
        """Maximum accepted perihelion distance (AU). **Default:** 1.0e3."""
        ...

    @property
    def min_rho2_au(self) -> float:
        """Minimum admissible topocentric distance at the central epoch (AU). **Default:** 0.01."""
        ...

    @property
    def r2_min_au(self) -> float:
        """Lower plausibility bound on central heliocentric distance (AU). **Default:** 0.05."""
        ...

    @property
    def r2_max_au(self) -> float:
        """Upper plausibility bound on central heliocentric distance (AU). **Default:** 200.0."""
        ...

    # Gauss polynomial / solver
    @property
    def aberth_max_iter(self) -> int:
        """Maximum iterations for the Aberth–Ehrlich polynomial solver. **Default:** 50."""
        ...

    @property
    def aberth_eps(self) -> float:
        """Convergence tolerance for the Aberth solver. **Default:** 1.0e-6."""
        ...

    @property
    def kepler_eps(self) -> float:
        """Tolerance used by the universal Kepler solver in velocity correction. **Default:** 1e3 * f64::EPSILON."""
        ...

    @property
    def max_tested_solutions(self) -> int:
        """Cap on admissible Gauss solutions kept after root finding. **Default:** 3."""
        ...

    # Numerics
    @property
    def newton_eps(self) -> float:
        """Absolute tolerance for Newton–Raphson inner solves. **Default:** 1.0e-10."""
        ...

    @property
    def newton_max_it(self) -> int:
        """Maximum iterations for Newton–Raphson inner solves. **Default:** 50."""
        ...

    @property
    def root_imag_eps(self) -> float:
        """Max imaginary part magnitude to treat a complex root as real. **Default:** 1.0e-6."""
        ...

    # Multi-threading (feature-gated in Rust)
    @property
    def batch_size(self) -> int:
        """
        Batch size for parallel trajectory processing. Only effective if the crate
        is compiled with the `parallel`/`rayon` feature. **Default:** 4.
        """
        ...

    @property
    def do_parallel(self) -> bool:
        """
        Whether this configuration requests parallel execution in higher-level APIs.

        Notes
        ----------
        This is carried alongside `IODParams` in the Python binding and consumed by callers
        (the core Rust struct is independent of this advisory flag).
        """
        ...


class IODParamsBuilder:
    """
    Fluent builder for `IODParams`.

    Defaults
    -----------------
    The builder starts with the **exact** defaults documented in `IODParams` (see there).

    See also
    -----------------
    * `IODParams` — Read-only parameter object produced by `.build()`.
    """

    def __init__(self) -> None: ...

    # --- Triplet generation / Monte Carlo ---
    def n_noise_realizations(self, v: int) -> "IODParamsBuilder":
        """Set the number of Monte Carlo perturbations per original triplet. **Default:** 20."""
        ...

    def noise_scale(self, v: float) -> "IODParamsBuilder":
        """Set the scale applied to nominal astrometric uncertainties. **Default:** 1.0."""
        ...

    def extf(self, v: float) -> "IODParamsBuilder":
        """
        Set the extrapolation factor for the RMS window (negative ⇒ broad fallback).
        Window formula: `dt_window = (triplet span) × v`, then clamp `≥ dtmax`.
        **Default:** -1.0.
        """
        ...

    def dtmax(self, v: float) -> "IODParamsBuilder":
        """Set the minimum RMS window size (days). **Default:** 30.0."""
        ...

    def dt_min(self, v: float) -> "IODParamsBuilder":
        """
        Set the minimum allowed span (days) between first and last obs in a triplet.
        **Default:** 0.03.
        """
        ...

    def dt_max_triplet(self, v: float) -> "IODParamsBuilder":
        """Set the maximum allowed span (days) within a triplet. **Default:** 150.0."""
        ...

    def optimal_interval_time(self, v: float) -> "IODParamsBuilder":
        """Set the target intra-triplet spacing (days). **Default:** 20.0."""
        ...

    def max_obs_for_triplets(self, v: int) -> "IODParamsBuilder":
        """Cap observations used to build triplets (uniform downsampling if exceeded). **Default:** 100."""
        ...

    def max_triplets(self, v: int) -> "IODParamsBuilder":
        """Cap the number of triplets evaluated per trajectory. **Default:** 10."""
        ...

    def gap_max(self, v: float) -> "IODParamsBuilder":
        """Set the maximum intra-batch time gap (days) for RMS calibration. **Default:** 8/24."""
        ...

    # --- Physical filters ---
    def max_ecc(self, v: float) -> "IODParamsBuilder":
        """Set the maximum eccentricity accepted. **Default:** 5.0."""
        ...

    def max_perihelion_au(self, v: float) -> "IODParamsBuilder":
        """Set the maximum perihelion distance (AU). **Default:** 1.0e3."""
        ...

    def min_rho2_au(self, v: float) -> "IODParamsBuilder":
        """Set the minimum topocentric distance at the central epoch (AU). **Default:** 0.01."""
        ...

    def r2_min_au(self, v: float) -> "IODParamsBuilder":
        """Set the lower plausibility bound on heliocentric distance (AU). **Default:** 0.05."""
        ...

    def r2_max_au(self, v: float) -> "IODParamsBuilder":
        """Set the upper plausibility bound on heliocentric distance (AU). **Default:** 200.0."""
        ...

    # --- Gauss polynomial / solver ---
    def aberth_max_iter(self, v: int) -> "IODParamsBuilder":
        """Set the maximum iterations for the Aberth–Ehrlich solver. **Default:** 50."""
        ...

    def aberth_eps(self, v: float) -> "IODParamsBuilder":
        """Set the Aberth convergence tolerance. **Default:** 1.0e-6."""
        ...

    def kepler_eps(self, v: float) -> "IODParamsBuilder":
        """Set the universal Kepler solver tolerance. **Default:** 1e3 * f64::EPSILON."""
        ...

    def max_tested_solutions(self, v: int) -> "IODParamsBuilder":
        """Cap the number of admissible solutions retained. **Default:** 3."""
        ...

    # --- Numerics ---
    def newton_eps(self, v: float) -> "IODParamsBuilder":
        """Set the Newton–Raphson absolute tolerance. **Default:** 1.0e-10."""
        ...

    def newton_max_it(self, v: int) -> "IODParamsBuilder":
        """Set the maximum Newton–Raphson iterations. **Default:** 50."""
        ...

    def root_imag_eps(self, v: float) -> "IODParamsBuilder":
        """Set the imaginary-part threshold to accept nearly-real roots. **Default:** 1.0e-6."""
        ...

    # --- Multi-threading (feature-gated in Rust) ---
    def batch_size(self, v: int) -> "IODParamsBuilder":
        """
        Set the batch size for parallel scheduling. Effective only when the crate
        is compiled with the `parallel`/`rayon` feature. **Default:** 4.
        """
        ...

    def do_parallel(self) -> "IODParamsBuilder":
        """
        Request parallel execution (Rayon-backed) in higher-level APIs that accept it.
        (Advisory flag carried by the Python binding; core Rust struct is independent.)
        """
        ...

    def do_sequential(self) -> "IODParamsBuilder":
        """Request sequential execution in higher-level APIs that accept it."""
        ...

    def build(self) -> IODParams:
        """
        Finalize and materialize an immutable `IODParams` with the chosen settings.

        Return
        ----------
        * A read-only `IODParams`.
        """
        ...
