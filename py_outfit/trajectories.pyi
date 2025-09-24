from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray

from py_outfit.iod_gauss import GaussResult
from py_outfit.iod_params import IODParams
from py_outfit.observations import Observations
from py_outfit.observer import Observer
from py_outfit.py_outfit import PyOutfit

Key = Union[int, str]
"""
Key used to identify a trajectory (either by its MPC code, a string ID or just an integer).
"""
PathLike = Union[str, Path]
"""
Path-like type (either a `str` or a `Path` from `pathlib`).
"""

class TrajectorySet:
    """
    Container for time‑ordered astrometric observations grouped by object identifiers, designed as the primary entry point for batch workflows.

    A TrajectorySet represents a mapping from a user-supplied key to a time‑ordered view of observations for that object. It enables loading large collections of observations, inspecting basic statistics, and running Gauss-based Initial Orbit Determination across all trajectories in a single operation. Keys can be integers or strings and are preserved end‑to‑end, making it straightforward to relate results back to upstream catalogs or pipeline identifiers.

    The container behaves like a Python dictionary for common operations such as membership tests, iteration, indexing, and length queries. Each entry provides a read‑only Observations view that exposes per‑trajectory data without copying, keeping memory usage predictable. This structure is intended to integrate cleanly with scientific Python workflows while delegating all heavy computation to the Rust engine underneath.

    Ingestion supports two main paths. A zero‑copy path accepts right ascension and declination in radians, epochs in MJD (TT), and a single Observer for the entire batch. A compatible degrees and arcseconds path performs a single conversion to radians before storing data. Trajectories can also be constructed from standard astronomy formats such as MPC 80‑column and ADES (JSON or XML), and an existing set can be extended by appending additional files when needed.

    The container is optimized for batch IOD. The dedicated batch method executes the Gauss solver over all stored trajectories using parameters supplied by IODParams and returns per‑trajectory outcomes together with error messages for failures. Execution may be sequential or parallel depending on configuration, with optional deterministic seeding for reproducibility. When run sequentially, cooperative cancellation allows returning partial results if interrupted by the user.

    The type does not perform de‑duplication or cross‑trajectory merging and assumes inputs are pre‑grouped as intended. Units follow the package conventions: angles are treated in radians internally, epochs use MJD (TT), and when ingesting degrees the provided uncertainties are interpreted in arcseconds. A single observing site applies per ingestion call. The overall goal is to make data flow explicit, predictable, and efficient for production pipelines.
    """

    # --- Introspection & stats ---
    def __repr__(self) -> str:
        """Return a concise, human-friendly representation."""
        ...

    def __len__(self) -> int:
        """Number of trajectories (mapping length)."""
        ...

    def __contains__(self, key: Key) -> bool:
        """
        Membership test (like a Python dict).

        Parameters
        -----------------
        * `key`: Object identifier (int MPC packed code or string id).

        Returns
        ----------
        * `True` if the trajectory exists in the set, `False` otherwise.

        See also
        ------------
        * `__getitem__` – Retrieve the associated `Observations` view.
        """
        ...

    def __getitem__(self, key: Key) -> Observations:
        """
        Subscript access (dict-like): return the `Observations` of a given object.

        Parameters
        -----------------
        * `key`: Object identifier (int or str).

        Returns
        ----------
        * An `Observations` view for that trajectory.

        Raises
        ----------
        * `KeyError` if the key is not present.

        See also
        ------------
        * `keys` – List available keys.
        * `values` – List all `Observations`.
        * `items` – Pairs `(key, Observations)`.
        """
        ...

    def keys(self) -> list[Key]:
        """
        Return the list of keys (like `dict.keys()`).

        Returns
        ----------
        list[Key]
            A list of all object identifiers currently stored.

        See also
        ------------
        * `values` – All trajectories.
        * `items` – Key/value pairs.
        """
        ...

    def values(self) -> list[Observations]:
        """
        Return the list of trajectories (like `dict.values()`).

        Returns
        ----------
        list[Observations]
            A list of all `Observations` currently stored.

        See also
        ------------
        * `keys` – All keys.
        * `items` – Key/value pairs.
        """
        ...

    def items(self) -> list[tuple[Key, Observations]]:
        """
        Return the list of `(key, Observations)` pairs (like `dict.items()`).

        Returns
        ----------
        list[tuple[Key, Observations]]
            A list of all `(object_id, Observations)` pairs currently stored.

        See also
        ------------
        * `keys` – All keys.
        * `values` – All trajectories.
        """
        ...

    def __iter__(self) -> Iterator[Key]:
        """
        Iterate over keys (like a dict).

        Parameters
        -----------------
        * *(none)*

        Returns
        ----------
        * `Iterator[Key]` yielding object identifiers.

        See also
        ------------
        * `keys` – Materialize all keys as a list.
        * `__contains__` – Membership test.
        """
        ...

    def total_observations(self) -> int:
        """
        Total number of observations across all trajectories.

        Returns
        ----------
        int
            sum over all per-trajectory counts.
        """
        ...

    def number_of_trajectories(self) -> int:
        """
        Number of trajectories currently stored.

        Returns
        ----------
        int
            number of distinct trajectory IDs.
        """
        ...

    def get_traj_stat(self) -> str:
        """
        Pretty-printed statistics about observations per trajectory.

        Returns
        ----------
        str
            A formatted `str` (histogram/stats), or
            `"No trajectories available."` if empty.
        """
        ...

    # --- Ingestion from NumPy ---
    @staticmethod
    def from_numpy_radians(
        pyoutfit: PyOutfit,
        trajectory_id: NDArray[np.uint32],
        ra: NDArray[np.float64],
        dec: NDArray[np.float64],
        error_ra_rad: float,
        error_dec_rad: float,
        mjd_tt: NDArray[np.float64],
        observer: Observer,
    ) -> "TrajectorySet":
        """
        Build a `TrajectorySet` from arrays already in **radians** (RA/DEC) and **MJD (TT)**.

        This path uses a zero-copy ingestion under the hood.

        Parameters
        -----------------
        pyoutfit : PyOutfit 
            Global environment (ephemerides, observers, error model).
        trajectory_id : NDArray[np.uint32]
            `np.uint32` array — one ID per observation.
        ra : NDArray[np.float64]
            `np.float64` array — Right Ascension in **radians**.
        dec : NDArray[np.float64]
            `np.float64` array — Declination in **radians**.
        error_ra_rad : float
            1-σ RA uncertainty (**radians**) applied to the whole batch.
        error_dec_rad : float
            1-σ DEC uncertainty (**radians**) applied to the whole batch.
        mjd_tt : NDArray[np.float64]
            `np.float64` array — epochs in **MJD (TT)** (days).
        observer : Observer
            Single observing site for the whole batch.

        Returns
        ----------
        TrajectorySet
            A new `TrajectorySet` populated from the provided inputs.

        Raises
        ----------
        ValueError
            if input arrays have mismatched lengths.
        """
        ...

    @staticmethod
    def from_numpy_degrees(
        pyoutfit: PyOutfit,
        trajectory_id: NDArray[np.uint32],
        ra_deg: NDArray[np.float64],
        dec_deg: NDArray[np.float64],
        error_ra_arcsec: float,
        error_dec_arcsec: float,
        mjd_tt: NDArray[np.float64],
        observer: Observer,
    ) -> "TrajectorySet":
        """
        Build a `TrajectorySet` from **degrees** (RA/DEC), **arcseconds** (uncertainties),
        and **MJD (TT)** for epochs.

        Internally converts once to radians, then ingests.

        Parameters
        -----------------
        pyoutfit : PyOutfit
            Global environment (ephemerides, observers, error model).
        trajectory_id : NDArray[np.uint32]
            `np.uint32` array — one ID per observation.
        ra_deg : NDArray[np.float64]
            `np.float64` array — Right Ascension in **degrees**.
        dec_deg : NDArray[np.float64]
            `np.float64` array — Declination in **degrees**.
        error_ra_arcsec : float
            1-σ RA uncertainty (**arcseconds**) applied to the batch.
        error_dec_arcsec : float
            1-σ DEC uncertainty (**arcseconds**) applied to the batch.
        mjd_tt : NDArray[np.float64]
            `np.float64` array — epochs in **MJD (TT)** (days).
        observer : Observer
            Single observing site for the whole batch.

        Returns
        ----------
        TrajectorySet
            A new `TrajectorySet` populated from the provided inputs.

        Raises
        ----------
        ValueError
            if input arrays have mismatched lengths.

        See also
        ------------
        * `from_numpy_radians` — Zero-copy variant for radian inputs.
        """
        ...

    # --- Ingestion from files ---
    @staticmethod
    def new_from_mpc_80col(
        pyoutfit: PyOutfit,
        path: PathLike,
    ) -> "TrajectorySet":
        """
        Build a `TrajectorySet` from a **MPC 80-column** file.

        Parameters
        -----------------
        pyoutfit : PyOutfit
            Global environment (ephemerides, observers, error model).
        path : PathLike
            File path (`str` or Path from pathlib) to a MPC 80-column text file.

        Returns
        ----------
        TrajectorySet
            A new `TrajectorySet` populated from the file contents.

        Notes
        ----------
        * Mirrors the Rust API semantics and may **panic** on parse errors.

        See also
        ------------
        * `add_from_mpc_80col` — Append a second 80-column file into an existing set.
        * `new_from_ades` — Create from ADES JSON/XML.
        """
        ...

    def add_from_mpc_80col(
        self,
        pyoutfit: PyOutfit,
        path: PathLike,
    ) -> None:
        """
        Append observations from a **MPC 80-column** file into this set.

        Parameters
        -----------------
        pyoutfit : PyOutfit
            Global environment (ephemerides, observers, error model).
        path : PathLike
            File path (`str` or Path from pathlib) to a MPC 80-column text file.

        Returns
        ----------
        None
            The internal map is updated in place.

        Notes
        ----------
        * **No de-duplication** is performed; avoid ingesting the same file twice.

        See also
        ------------
        * `new_from_mpc_80col` — Create a brand-new set from a single file.
        """
        ...

    @staticmethod
    def new_from_ades(
        pyoutfit: PyOutfit,
        path: PathLike,
        error_ra_arcsec: Optional[float],
        error_dec_arcsec: Optional[float],
    ) -> "TrajectorySet":
        """
        Build a `TrajectorySet` from an **ADES** file (JSON or XML).

        Parameters
        -----------------
        pyoutfit : PyOutfit
            Global environment (ephemerides, observers, error model).
        path : PathLike
            File path (`str` or Path from pathlib) to an ADES JSON/XML file.
        error_ra_arcsec : Optional[float]
            Optional global RA 1-σ (arcsec) if not specified per row.
        error_dec_arcsec : Optional[float]
            Optional global DEC 1-σ (arcsec) if not specified per row.

        Returns
        ----------
        TrajectorySet
            A new `TrajectorySet` populated from the ADES file.

        Notes
        ----------
        * Error-handling policy follows the underlying parser (may log or panic).

        See also
        ------------
        * `add_from_ades` — Append ADES observations into an existing set.
        """
        ...

    def add_from_ades(
        self,
        pyoutfit: PyOutfit,
        path: PathLike,
        error_ra_arcsec: Optional[float],
        error_dec_arcsec: Optional[float],
    ) -> None:
        """
        Append observations from an **ADES** file (JSON/XML) into this set.

        Parameters
        -----------------
        pyoutfit : PyOutfit
            Global environment (ephemerides, observers, error model).
        path : PathLike
            File path (`str` or Path from pathlib) to an ADES JSON/XML file.
        error_ra_arcsec : Optional[float]
            Optional global RA 1-σ (arcsec) if not specified per row.
        error_dec_arcsec : Optional[float]
            Optional global DEC 1-σ (arcsec) if not specified per row.

        Returns
        ----------
        None
            The internal map is updated in place.

        Notes
        ----------
        * **No de-duplication** is performed; avoid re-ingesting the same file.

        See also
        ------------
        * `new_from_ades` — Create a brand-new set from a single ADES file.
        """
        ...

    # --- Batch IOD ---
    def estimate_all_orbits(
        self,
        env: PyOutfit,
        params: IODParams,
        seed: Optional[int] = ...,
    ) -> Tuple[Dict[Any, Tuple[GaussResult, float]], Dict[Any, str]]:
        """
        Estimate the best orbit for **all trajectories** in this set.

        Runs Gauss-based IOD for each trajectory using the provided environment
        and parameters. Internally creates a RNG:
        - if `seed` is provided → deterministic `StdRng::seed_from_u64(seed)`;
        - else → `StdRng::from_os_rng()`.

        Cancellation
        ----------
        The computation periodically checks for `KeyboardInterrupt` (Ctrl-C). 
        This work only if parallel is disabled (`params.do_parallel() == False`).
        If parallel is enabled, the computation cannot be interrupted and you will need to kill the process manually.

        If cancellation is triggered, partial results accumulated so far are returned:

        - the first dict contains successful `(GaussResult, rms)` per object,
        - the second dict contains error messages per object.

        Parameters
        -----------------
        env : PyOutfit
            Global environment (ephemerides, observers, error model).
        params : IODParams
            IOD tuning parameters (`IODParams`). If `params.do_parallel()`
            is `True`, a parallel path is used internally; otherwise a sequential
            path with cooperative cancellation.
        seed : Optional[int]
            Optional RNG seed for reproducibility.

        Returns
        ----------
        ok: Dict[object_id, (GaussResult, float)]
            successful gauss results with RMS,
        err: Dict[object_id, str]
            error messages for failed trajectories.

        Notes
        ----------
        * `object_id` preserves the input trajectory identifiers (either `int`
          or `str`, depending on how trajectories were ingested).
        * The RMS value is engine-defined (e.g., post-fit residual RMS in radians).
        """
        ...
