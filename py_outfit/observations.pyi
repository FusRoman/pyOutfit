# py_outfit/observations.pyi
from __future__ import annotations

from typing import Iterator
import numpy as np
from numpy.typing import NDArray

from py_outfit.py_outfit import PyOutfit

class Observations:
    """
    Read-only Python view over a single trajectory (list of astrometric observations).

    Highlights
    ----------
    - Vector exports: `to_numpy()` and `to_list()`
    - Row access / iteration: `__getitem__`, `__iter__`
    - Pretty display helpers:
        * `show(...)` – compact, fixed-width table
        * `table_wide(...)` – diagnostic table with JD, radians, distances (AU)
        * `table_iso(...)` – timestamp-centric (ISO TT / ISO UTC)
        * `*_with_env(env, ...)` – same as above, but resolves observer names using `PyOutfit`
    """

    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __len__(self) -> int: ...

    # -------------------------
    # Iteration / random access
    # -------------------------
    def __iter__(self) -> Iterator[tuple[float, float, float, float, float]]:
        """
        Iterate observations as tuples.

        Returns
        -------
        Iterator[tuple[float, float, float, float, float]]
            Yields `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.
        """
        ...

    def __getitem__(self, idx: int) -> tuple[float, float, float, float, float]:
        """
        Random access to an observation.

        Parameters
        ----------
        idx : int
            Zero-based index (negative indexing supported).

        Returns
        -------
        tuple[float, float, float, float, float]
            `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.

        Raises
        ------
        IndexError
            If `idx` is out of range.
        """
        ...
    # ---------------
    # Columnar export
    # ---------------
    def to_numpy(
        self,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
        """
        Export arrays to NumPy (rad / days).

        Returns
        -------
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            Five 1D arrays of dtype float64:
            `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.
        """
        ...

    def to_list(self) -> list[tuple[float, float, float, float, float]]:
        """
        Return a Python list of observation tuples.

        Returns
        -------
        list[tuple[float, float, float, float, float]]
            Each tuple is `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.
        """
        ...
    # -----------------
    # Display (compact)
    # -----------------
    def show(self, *, sorted: bool = False, sec_prec: int = 3) -> str:
        """
        Render a compact, fixed-width table.

        Parameters
        ----------
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for sexagesimal seconds (default: 3).

        Returns
        -------
        str
            Formatted table.
        """
        ...

    def show_with_env(
        self, env: PyOutfit, *, sorted: bool = False, sec_prec: int = 3
    ) -> str:
        """
        Compact table, resolving observer names via `env`.

        Parameters
        ----------
        env : PyOutfit
            Global environment used to resolve site names.
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for sexagesimal seconds (default: 3).

        Returns
        -------
        str
            Formatted table (with site names when available).
        """
        ...
    # --------------
    # Display (wide)
    # --------------
    def table_wide(
        self, *, sorted: bool = False, sec_prec: int = 3, dist_prec: int = 6
    ) -> str:
        """
        Diagnostic table (Unicode) with JD, radians, and AU distances.

        Columns
        -------
        `# | Site | MJD (TT) | JD (TT) | RA±σ[arcsec] | RA [rad] | DEC±σ[arcsec] | DEC [rad] | |r_geo| AU | |r_hel| AU`

        Parameters
        ----------
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for sexagesimal seconds (default: 3).
        dist_prec : int, optional
            Fixed-point digits for AU distances (default: 6).

        Returns
        -------
        str
            Unicode table (box drawing).
        """
        ...

    def table_wide_with_env(
        self,
        env: PyOutfit,
        *,
        sorted: bool = False,
        sec_prec: int = 3,
        dist_prec: int = 6,
    ) -> str:
        """
        Diagnostic table (Unicode) using `env` to resolve observer names.

        See `table_wide` for columns and knobs.

        Parameters
        ----------
        env : PyOutfit
            Global environment used to resolve site names.
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for sexagesimal seconds (default: 3).
        dist_prec : int, optional
            Fixed-point digits for AU distances (default: 6).

        Returns
        -------
        str
            Unicode table (box drawing).
        """
        ...
    # -------------
    # Display (ISO)
    # -------------
    def table_iso(self, *, sorted: bool = False, sec_prec: int = 3) -> str:
        """
        ISO-centric table (Unicode) with TT & UTC timestamps.

        Columns
        -------
        `# | Site | ISO (TT) | ISO (UTC) | RA±σ[arcsec] | DEC±σ[arcsec]`

        Parameters
        ----------
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for seconds (applied to ISO & sexagesimal, default: 3).

        Returns
        -------
        str
            Unicode table (box drawing).
        """
        ...

    def table_iso_with_env(
        self, env: PyOutfit, *, sorted: bool = False, sec_prec: int = 3
    ) -> str:
        """
        ISO-centric table (Unicode) using `env` to resolve observer names.

        See `table_iso` for columns and knobs.

        Parameters
        ----------
        env : PyOutfit
            Global environment used to resolve site names.
        sorted : bool, optional
            Sort rows by MJD(TT) ascending (default: False).
        sec_prec : int, optional
            Fractional digits for seconds (applied to ISO & sexagesimal, default: 3).

        Returns
        -------
        str
            Unicode table (box drawing).
        """
        ...
