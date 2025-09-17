from __future__ import annotations

from typing import Any, Dict, Iterator, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray

from py_outfit.iod_gauss import GaussResult
from py_outfit.iod_params import IODParams
from py_outfit.observations import Observations
from py_outfit.observer import Observer
from py_outfit.py_outfit import PyOutfit

Key = Union[int, str]

class TrajectorySet:
    """
    Container of time-ordered observations grouped by object (trajectory),
    with helpers to run Gauss-based IOD in batch.

    See also
    ------------
    * `trajectory_set_from_numpy_radians` — Zero-copy ingestion from radians.
    * `trajectory_set_from_numpy_degrees` — Degree/arcsec ingestion with conversion.
    * `estimate_all_orbits` — Batch Gauss IOD over all trajectories.
    """

    # --- Introspection & stats ---
    def __repr__(self) -> str:
        """Return a concise, human-friendly representation."""
        ...

        def __len__(self) -> int: ...

    def __contains__(self, key: Key) -> bool:
        """
        Membership test (like a Python dict).

        Arguments
        -----------------
        * `key`: Object identifier (int MPC packed code or string id).

        Return
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

        Arguments
        -----------------
        * `key`: Object identifier (int or str).

        Return
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

        Arguments
        -----------------
        * *(none)*

        Return
        ----------
        * `list[Key]` of all object identifiers.

        See also
        ------------
        * `values` – All trajectories.
        * `items` – Key/value pairs.
        """
        ...

    def values(self) -> list[Observations]:
        """
        Return the list of trajectories (like `dict.values()`).

        Arguments
        -----------------
        * *(none)*

        Return
        ----------
        * `list[Observations]` containing one entry per object.

        See also
        ------------
        * `keys` – All keys.
        * `items` – Key/value pairs.
        """
        ...

    def items(self) -> list[tuple[Key, Observations]]:
        """
        Return the list of `(key, Observations)` pairs (like `dict.items()`).

        Arguments
        -----------------
        * *(none)*

        Return
        ----------
        * `list[tuple[Key, Observations]]`.

        See also
        ------------
        * `keys` – All keys.
        * `values` – All trajectories.
        """
        ...

    def __iter__(self) -> Iterator[Key]:
        """
        Iterate over keys (like a dict).

        Arguments
        -----------------
        * *(none)*

        Return
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

        Return
        ----------
        * `int` — sum over all per-trajectory counts.
        """
        ...

    def number_of_trajectories(self) -> int:
        """
        Number of trajectories currently stored.

        Return
        ----------
        * `int` — number of distinct trajectory IDs.
        """
        ...

    def get_traj_stat(self) -> str:
        """
        Pretty-printed statistics about observations per trajectory.

        Return
        ----------
        * A formatted `str` (histogram/stats), or
          `"No trajectories available."` if empty.
        """
        ...
    # --- Ingestion from NumPy ---
    @staticmethod
    def trajectory_set_from_numpy_radians(
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

        Arguments
        -----------------
        * `pyoutfit`: Global environment (ephemerides, observers, error model).
        * `trajectory_id`: `np.uint32` array — one ID per observation.
        * `ra`: `np.float64` array — Right Ascension in **radians**.
        * `dec`: `np.float64` array — Declination in **radians**.
        * `error_ra_rad`: 1-σ RA uncertainty (**radians**) applied to the whole batch.
        * `error_dec_rad`: 1-σ DEC uncertainty (**radians**) applied to the whole batch.
        * `mjd_tt`: `np.float64` array — epochs in **MJD (TT)** (days).
        * `observer`: Single observing site for the whole batch.

        Return
        ----------
        * A new `TrajectorySet` populated from the provided inputs.

        Raises
        ----------
        * `ValueError` if input arrays have mismatched lengths.
        """
        ...

    @staticmethod
    def trajectory_set_from_numpy_degrees(
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

        Arguments
        -----------------
        * `pyoutfit`: Global environment (ephemerides, observers, error model).
        * `trajectory_id`: `np.uint32` array — one ID per observation.
        * `ra_deg`: `np.float64` array — Right Ascension in **degrees**.
        * `dec_deg`: `np.float64` array — Declination in **degrees**.
        * `error_ra_arcsec`: 1-σ RA uncertainty (**arcseconds**) applied to the batch.
        * `error_dec_arcsec`: 1-σ DEC uncertainty (**arcseconds**) applied to the batch.
        * `mjd_tt`: `np.float64` array — epochs in **MJD (TT)** (days).
        * `observer`: Single observing site for the whole batch.

        Return
        ----------
        * A new `TrajectorySet` populated from the provided inputs.

        Raises
        ----------
        * `ValueError` if input arrays have mismatched lengths.

        See also
        ------------
        * `trajectory_set_from_numpy_radians` — Zero-copy variant for radian inputs.
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
        The computation periodically checks for `KeyboardInterrupt` (Ctrl-C). If
        triggered, partial results accumulated so far are returned:
        * the first dict contains successful `(GaussResult, rms)` per object,
        * the second dict contains error messages per object.

        Arguments
        -----------------
        * `env`: Global Outfit state (ephemerides, EOP, error model).
        * `params`: IOD tuning parameters (`IODParams`). If `params.do_parallel()`
          is `True`, a parallel path is used internally; otherwise a sequential
          path with cooperative cancellation.
        * `seed`: Optional RNG seed for reproducibility.

        Return
        ----------
        * `(ok, err)` where:
          - `ok: Dict[object_id, (GaussResult, float)]` — successful results with RMS,
          - `err: Dict[object_id, str]` — human-readable error messages.

        Notes
        ----------
        * `object_id` preserves the input trajectory identifiers (either `int`
          or `str`, depending on how trajectories were ingested).
        * The RMS value is engine-defined (e.g., post-fit residual RMS in radians).
        """
        ...
