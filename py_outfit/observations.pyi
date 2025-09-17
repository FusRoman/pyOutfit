# py_outfit/observations.pyi
from __future__ import annotations

from typing import Iterator
import numpy as np

class Observations:
    """
    Read-only Python view over a single trajectory (list of astrometric observations).

    See also
    ------------
    * `TrajectorySet` – Mapping from object key to observation lists.
    * `to_numpy` – Export RA/DEC/MJD and uncertainties to NumPy arrays.
    """

    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[tuple[float, float, float, float, float]]:
        """
        Iterate observations as tuples.

        Arguments
        -----------------
        * *(none)* – Iterator over stored observations.

        Return
        ----------
        * An `Iterator[tuple[float, float, float, float, float]]` yielding:
          `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.

        See also
        ------------
        * `to_list` – Materialize the whole sequence as a Python list.
        * `to_numpy` – Export column arrays as NumPy ndarrays.
        """
        ...

    def __getitem__(self, idx: int) -> tuple[float, float, float, float, float]:
        """
        Random access to an observation.

        Arguments
        -----------------
        * `idx`: Zero-based index (supports negative indexing).

        Return
        ----------
        * A 5-tuple `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.

        Raises
        ----------
        * `IndexError` if `idx` is out of range.

        See also
        ------------
        * `__iter__` – Row-wise iteration.
        * `to_numpy` – Vectorized export.
        """
        ...

    def to_numpy(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Export arrays to NumPy (rad / days).

        Arguments
        -----------------
        * *(none)* – Accessor method.

        Return
        ----------
        * A tuple of five `np.ndarray` with dtype `float64` and shape `(N,)`:
          `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.

        See also
        ------------
        * `__iter__` – Iterate row by row instead of exporting full arrays.
        * `to_list` – Export as a list of Python tuples.
        """
        ...

    def to_list(self) -> list[tuple[float, float, float, float, float]]:
        """
        Return a Python list of observation tuples.

        Arguments
        -----------------
        * *(none)* – Accessor method.

        Return
        ----------
        * `list[tuple[float, float, float, float, float]]` where each tuple is
          `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.

        See also
        ------------
        * `__iter__` – Lazy iteration.
        * `to_numpy` – Columnar export as NumPy arrays.
        """
        ...
