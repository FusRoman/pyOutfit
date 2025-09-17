class IODParams:
    """
    Tuning parameters for the Gauss Initial Orbit Determination (IOD).

    This object is **immutable** from Python (read-only properties). To create or
    modify a configuration, use the builder: `IODParams.builder()` or
    `IODParamsBuilder()` and then call `.build()`.

    Parameters overview
    -----------------
    General knobs
    ~~~~~~~~~~~~~
    - `n_noise_realizations: int`  
      Number of Monte-Carlo noise realizations per candidate triplet. Increases
      robustness at the cost of runtime. **Unit:** count.

    - `noise_scale: float`  
      Multiplicative factor applied to quoted astrometric uncertainties (e.g., to
      compensate underestimated catalog errors). **Unit:** dimensionless (> 0).

    - `extf: float`  
      External error floor added by the error model (e.g., catalog/atmospheric
      floor). **Unit:** radians (≥ 0).

    - `dtmax: float`  
      Maximum allowed overall time span of the IOD problem (e.g., between the
      first and last obs considered). **Unit:** days.

    - `dt_min: float`  
      Minimum time separation enforced between any two observations inside a
      chosen triplet (helps reject nearly-coincident pairs). **Unit:** days.

    - `dt_max_triplet: float`  
      Maximum time separation allowed within a candidate triplet (controls
      degeneracies and dynamics coverage). **Unit:** days.

    - `optimal_interval_time: float`  
      Preferred intra-triplet spacing guiding the triplet enumerator toward
      better-conditioned triplets. **Unit:** days.

    - `max_obs_for_triplets: int`  
      Hard cap on the number of observations taken from a trajectory to build
      triplets (tradeoff between coverage and combinatorics). **Unit:** count.

    - `max_triplets: int`  
      Hard cap on the number of candidate triplets evaluated per trajectory.
      **Unit:** count.

    - `gap_max: float`  
      Maximum acceptable temporal gap for RMS calibration steps (e.g., when
      aligning quoted errors to empirical residuals). **Unit:** days.

    Physical filters
    ~~~~~~~~~~~~~~~~
    - `max_ecc: float`  
      Maximum eccentricity accepted for candidate orbits (rejects unphysical or
      undesired solutions). **Unit:** dimensionless (≥ 0).

    - `max_perihelion_au: float`  
      Upper bound on perihelion distance for accepted solutions. **Unit:** AU.

    - `min_rho2_au: float`  
      Lower bound on squared topocentric distance during fitting, to avoid
      pathological near-observer cases. **Unit:** AU².

    - `r2_min_au: float`, `r2_max_au: float`  
      Bounds on heliocentric distance for candidate solutions. **Unit:** AU.

    Gauss polynomial / solver
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    - `aberth_max_iter: int`  
      Maximum iterations for the Aberth root-finding scheme used to solve the
      Gauss polynomial. **Unit:** iterations (≥ 1).

    - `aberth_eps: float`  
      Convergence tolerance for the Aberth solver. **Unit:** dimensionless
      (absolute polynomial/step criterion; engine-defined interpretation).

    - `kepler_eps: float`  
      Convergence tolerance for solving Kepler’s equation inside the IOD loop.
      **Unit:** radians (typical interpretation as angle tolerance).

    - `max_tested_solutions: int`  
      Maximum number of candidate roots/solutions evaluated after root finding.
      **Unit:** count.

    Numerics
    ~~~~~~~~
    - `newton_eps: float`  
      Convergence tolerance for Newton iterations in post-processing steps
      (e.g., refinement). **Unit:** dimensionless or radians (engine-defined).

    - `newton_max_it: int`  
      Maximum Newton iterations when used. **Unit:** iterations (≥ 1).

    - `root_imag_eps: float`  
      Threshold on the imaginary part of a complex root to accept it as “real”.
      **Unit:** dimensionless.

    Multi-threading
    ~~~~~~~~~~~~~~~
    - `batch_size: int`  
      Batch size for scheduling candidate work in parallel. Larger batches reduce
      overhead but may impact load balancing. **Unit:** count.

    - `do_parallel: bool`  
      Advisory flag carried alongside `IODParams` to request Rayon-backed
      parallel execution in higher-level APIs. The core Rust struct remains
      independent; this flag is consumed by the caller.

    Usage
    ----------
    >>> builder = IODParams.builder()
    >>> params = (
    ...     builder
    ...     .n_noise_realizations(8)
    ...     .noise_scale(1.1)
    ...     .dt_min(0.01).dt_max_triplet(2.0)
    ...     .max_obs_for_triplets(12).max_triplets(200)
    ...     .max_ecc(0.99).r2_min_au(0.5).r2_max_au(50.0)
    ...     .aberth_eps(1e-12).aberth_max_iter(200)
    ...     .do_parallel()
    ...     .build()
    ... )

    See also
    ------------
    * `IODParams.builder` — Returns an `IODParamsBuilder`.
    * `IODParamsBuilder` — Fluent, chainable builder for `IODParams`.
    * `TrajectorySet.estimate_all_orbits` — Batch IOD entry-point consuming these params.

    Notes
    ----------
    The underlying Rust struct is `outfit::IODParams`. Default values are
    **engine-defined** and may change across versions. Some flags (e.g., `do_parallel`)
    are modeled externally to toggle sequential vs. multithreaded execution paths.
    """

    def __init__(self) -> None: ...
    @staticmethod
    def builder() -> "IODParamsBuilder":
        """
        Create a new `IODParamsBuilder` initialized with default values.

        Usage
        ----------
        >>> params = (
        ...     IODParams.builder()
        ...     .n_noise_realizations(8)
        ...     .noise_scale(1.1)
        ...     .dt_min(0.01)
        ...     .dt_max_triplet(2.0)
        ...     .max_obs_for_triplets(12)
        ...     .max_triplets(200)
        ...     .do_parallel()     # or .do_sequential()
        ...     .build()
        ... )

        Return
        ----------
        * A fresh `IODParamsBuilder` ready for fluent, chainable configuration.
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

    # --- Read-only getters for testing & user introspection ---
    @property
    def n_noise_realizations(self) -> int:
        """
        Number of Monte-Carlo noise realizations per candidate.
        """
        ...

    @property
    def noise_scale(self) -> float:
        """
        Multiplicative factor applied to quoted astrometric uncertainties.
        """
        ...

    @property
    def extf(self) -> float:
        """
        External error floor (model-dependent scalar), in radians.
        """
        ...

    @property
    def dtmax(self) -> float:
        """
        Maximum allowed total time span (days) for the IOD process.
        """
        ...

    @property
    def dt_min(self) -> float:
        """
        Minimum separation (days) between observations used in a triplet.
        """
        ...

    @property
    def dt_max_triplet(self) -> float:
        """
        Maximum separation (days) allowed within an observation triplet.
        """
        ...

    @property
    def optimal_interval_time(self) -> float:
        """
        Preferred intra-triplet spacing (days) used by the triplet enumerator.
        """
        ...

    @property
    def max_obs_for_triplets(self) -> int:
        """
        Hard cap on observations considered when building triplets.
        """
        ...

    @property
    def max_triplets(self) -> int:
        """
        Hard cap on the number of triplets tested per trajectory.
        """
        ...

    @property
    def gap_max(self) -> float:
        """
        Maximum acceptable temporal gap (days) for RMS calibration.
        """
        ...
    # --- Physical filters ---
    @property
    def max_ecc(self) -> float:
        """
        Maximum eccentricity allowed for accepted solutions.
        """
        ...

    @property
    def max_perihelion_au(self) -> float:
        """
        Maximum perihelion distance (AU) filter for accepted solutions.
        """
        ...

    @property
    def min_rho2_au(self) -> float:
        """
        Minimum topocentric distance squared (AU^2) during fitting.
        """
        ...

    @property
    def r2_min_au(self) -> float:
        """
        Minimum heliocentric distance (AU) for candidate solutions.
        """
        ...

    @property
    def r2_max_au(self) -> float:
        """
        Maximum heliocentric distance (AU) for candidate solutions.
        """
        ...
    # --- Gauss polynomial / solver ---
    @property
    def aberth_max_iter(self) -> int:
        """
        Maximum iterations for the Aberth root-finding scheme.
        """
        ...

    @property
    def aberth_eps(self) -> float:
        """
        Convergence tolerance for the Aberth solver.
        """
        ...

    @property
    def kepler_eps(self) -> float:
        """
        Convergence tolerance for Kepler-equation solves within IOD.
        """
        ...

    @property
    def max_tested_solutions(self) -> int:
        """
        Maximum number of candidate roots/solutions evaluated.
        """
        ...
    # --- Numerics ---
    @property
    def newton_eps(self) -> float:
        """
        Convergence tolerance for Newton iterations (when used).
        """
        ...

    @property
    def newton_max_it(self) -> int:
        """
        Maximum Newton iterations (when used).
        """
        ...

    @property
    def root_imag_eps(self) -> float:
        """
        Threshold on imaginary part to accept a root as 'real'.
        """
        ...
    # --- Multi-threading ---
    @property
    def batch_size(self) -> int:
        """
        Batch size used when scheduling parallel work.
        """
        ...

    @property
    def do_parallel(self) -> bool:
        """
        Whether this configuration requests parallel execution.

        Notes
        ----------
        This flag is carried alongside `IODParams` (not inside the Rust struct) and
        is normally consumed by higher-level APIs to decide between sequential vs.
        parallel execution paths.
        """
        ...

class IODParamsBuilder:
    """
    Fluent builder for `IODParams`.

    See also
    ------------
    * `IODParams` — Read-only parameter object produced by `.build()`.
    """

    def __init__(self) -> None: ...

    # --- General knobs ---
    def n_noise_realizations(self, v: int) -> "IODParamsBuilder":
        """Set the number of Monte-Carlo noise realizations per candidate."""
        ...

    def noise_scale(self, v: float) -> "IODParamsBuilder":
        """Set the multiplicative scale applied to astrometric uncertainties."""
        ...

    def extf(self, v: float) -> "IODParamsBuilder":
        """Set the external error floor (radians)."""
        ...

    def dtmax(self, v: float) -> "IODParamsBuilder":
        """Set the maximum allowed overall time span (days)."""
        ...

    def dt_min(self, v: float) -> "IODParamsBuilder":
        """Set the minimum time separation (days) between observations in a triplet."""
        ...

    def dt_max_triplet(self, v: float) -> "IODParamsBuilder":
        """Set the maximum time separation (days) allowed within a triplet."""
        ...

    def optimal_interval_time(self, v: float) -> "IODParamsBuilder":
        """Set the preferred intra-triplet spacing (days)."""
        ...

    def max_obs_for_triplets(self, v: int) -> "IODParamsBuilder":
        """Limit the number of observations considered when building triplets."""
        ...

    def max_triplets(self, v: int) -> "IODParamsBuilder":
        """Limit the number of triplets tested per trajectory."""
        ...

    def gap_max(self, v: float) -> "IODParamsBuilder":
        """Set the maximum temporal gap (days) for RMS calibration."""
        ...
    # --- Physical filters ---
    def max_ecc(self, v: float) -> "IODParamsBuilder":
        """Set the maximum eccentricity allowed for solutions."""
        ...

    def max_perihelion_au(self, v: float) -> "IODParamsBuilder":
        """Set the maximum perihelion distance (AU)."""
        ...

    def min_rho2_au(self, v: float) -> "IODParamsBuilder":
        """Set the minimum topocentric distance squared (AU²)."""
        ...

    def r2_min_au(self, v: float) -> "IODParamsBuilder":
        """Set the minimum heliocentric distance (AU)."""
        ...

    def r2_max_au(self, v: float) -> "IODParamsBuilder":
        """Set the maximum heliocentric distance (AU)."""
        ...
    # --- Gauss polynomial / solver ---
    def aberth_max_iter(self, v: int) -> "IODParamsBuilder":
        """Set the maximum number of iterations for the Aberth solver."""
        ...

    def aberth_eps(self, v: float) -> "IODParamsBuilder":
        """Set the convergence tolerance for the Aberth solver."""
        ...

    def kepler_eps(self, v: float) -> "IODParamsBuilder":
        """Set the convergence tolerance for solving Kepler’s equation."""
        ...

    def max_tested_solutions(self, v: int) -> "IODParamsBuilder":
        """Set the maximum number of candidate solutions to test."""
        ...
    # --- Numerics ---
    def newton_eps(self, v: float) -> "IODParamsBuilder":
        """Set the convergence tolerance for Newton iterations."""
        ...

    def newton_max_it(self, v: int) -> "IODParamsBuilder":
        """Set the maximum number of Newton iterations."""
        ...

    def root_imag_eps(self, v: float) -> "IODParamsBuilder":
        """Set the threshold on imaginary part to accept a root as real."""
        ...
    # --- Multi-threading ---
    def batch_size(self, v: int) -> "IODParamsBuilder":
        """Set the batch size used for parallel scheduling."""
        ...

    def do_parallel(self) -> "IODParamsBuilder":
        """
        Request parallel execution (Rayon-backed) for downstream calls that accept it.
        """
        ...

    def do_sequential(self) -> "IODParamsBuilder":
        """
        Request sequential execution for downstream calls that accept it.
        """
        ...

    def build(self) -> IODParams:
        """
        Finalize and materialize an immutable `IODParams`.

        Return
        ----------
        * A read-only `IODParams` carrying all chosen parameters and flags.
        """
        ...