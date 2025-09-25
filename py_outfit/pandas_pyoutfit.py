"""
Pandas accessor for batch Initial Orbit Determination (IOD) with Outfit.

This module adds a `DataFrame.outfit` accessor exposing a vectorized entry-point
to run **Gauss IOD** on a flat, columnar table of astrometric measurements.

Examples
-----------------
>>> df = pd.DataFrame({
...     "tid":  [0, 0, 0, 1, 1, 1],
...     "mjd":  [60000.0, 60000.01, 60000.02, 60000.0, 60000.01, 60000.02],
...     "ra":   [10.1, 10.2, 10.3, 33.4, 33.5, 33.6],   # degrees by default
...     "dec":  [-5.0, -4.9, -4.8,  2.0,  2.1,  2.2],  # degrees by default
... })
>>> env = PyOutfit(ephem="horizon:DE440", error_model="FCCT14")
>>> params = IODParams() # default settings
>>> obs = PyOutfit.get_observer_from_mpc_code("I41") # ZTF
>>> orb_pdf = pandas_traj.outfit.estimate_orbits(
...     env, params, obs, ra_error=0.5, dec_error=0.5
... )
>>> orb_pdf.columns[:5]  # doctest: +ELLIPSIS
Index(['object_id', 'variant', 'element_set', 'rms', ...], dtype='object')

Design
-----------------
- **Schema**: maps your column names to the expected fields (`tid/mjd/ra/dec`).
- **Vector ingestion**: we assemble a `TrajectorySet` directly from NumPy arrays.
- **Units**: `units="degrees"` (default) interprets RA/DEC in degrees and
  uncertainties in arcseconds; `"radians"` expects everything in radians.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Literal, Optional, Tuple, Union

import numpy as np
import pandas as pd

from py_outfit import PyOutfit, IODParams, Observer, TrajectorySet
from py_outfit import GaussResult
from py_outfit import RADSEC

Number = Union[int, float, np.number]
ObjectID = Union[int, str, np.integer, np.str_]

@dataclass(frozen=True)
class Schema:
    """
    Column schema used to map a DataFrame to py_outfit's vector ingestion.

    Attributes
    -----------------
    tid : str
        Column containing object/trajectory IDs (int or str). Repeated per-row.
    mjd : str
        Modified Julian Date (TT, **days**).
    ra : str
        Right Ascension values (degrees if `units='degrees'`, else radians).
    dec : str
        Declination values (degrees if `units='degrees'`, else radians).

    Notes
    ----------
    * Only these four columns are required for the accessor.
    * If your DataFrame uses different names, override the defaults:
      `schema=Schema(tid="object", mjd="epoch", ra="alpha", dec="delta")`.
    """

    tid: str = "tid"
    mjd: str = "mjd"
    ra: str = "ra"
    dec: str = "dec"


def _ensure_float64(a: Iterable[Number]) -> np.ndarray:
    """
    Ensure a contiguous float64 NumPy array.

    Parameters
    -----------------
    * `a`: Any sequence/array-like of numeric values.

    Returns
    ----------
    * A C-contiguous `np.ndarray` with `dtype=np.float64`.

    Notes
    ----------
    * This helper avoids hidden copies later and standardizes dtypes for the Rust side.
    """
    return np.ascontiguousarray(np.asarray(a, dtype=np.float64))


def _ensure_object_ids(a: Iterable[ObjectID]) -> np.ndarray:
    """
    Normalize a vector of object IDs for Outfit ingestion.

    Parameters
    -----------------
    * `a`: Sequence of IDs (integers or strings). `np.uint32` is supported.

    Returns
    ----------
    * `np.ndarray` with a stable dtype:
      - `np.uint32` for pure-integer inputs,
      - `object` for string/heterogeneous inputs.

    Notes
    ----------
    * Keeping a compact integer dtype improves memory locality.
    * Mixed types are coerced to `object` for safety.
    """
    arr = np.asarray(a)
    if np.issubdtype(arr.dtype, np.integer):
        # Normalize to a stable integer dtype (compact and hash-friendly)
        return np.ascontiguousarray(arr.astype(np.uint32))
    if np.issubdtype(arr.dtype, np.str_) or arr.dtype == object:
        return np.ascontiguousarray(arr.astype(object))
    # Fallback: coerce to object (e.g., unexpected dtypes)
    return np.ascontiguousarray(arr.astype(object))


def _detect_element_set(
    d: Dict[str, Any],
) -> Literal["keplerian", "equinoctial", "cometary"]:
    """
    Infer the orbital element set from keys produced by `GaussResult.to_dict()`.

    Parameters
    -----------------
    * `d`: Dictionary exported from a `GaussResult` (native keys).

    Returns
    ----------
    * Literal string identifying the set: `"keplerian"`, `"equinoctial"`, or `"cometary"`.

    See also
    ------------
    * `GaussResult.to_dict` – Source of the native element names.
    """
    k = set(d.keys())
    if {"semi_major_axis", "mean_anomaly", "periapsis_argument"}.issubset(k):
        return "keplerian"
    if {"eccentricity_sin_lon", "tan_half_incl_cos_node", "mean_longitude"}.issubset(k):
        return "equinoctial"
    if {"perihelion_distance", "true_anomaly", "ascending_node_longitude"}.issubset(k):
        return "cometary"
    # Conservative default (rare/ambiguous)
    return "keplerian"


def _rows_from_ok_map(ok: Dict[int | str, Tuple[GaussResult, float]]) -> pd.DataFrame:
    """
    Flatten the success map from `TrajectorySet.estimate_all_orbits` to a DataFrame.

    Parameters
    -----------------
    * `ok`: Mapping `object_id -> (GaussResult, rms)`.

    Returns
    ----------
    * `pd.DataFrame` with columns:
      - `object_id`, `variant` (`PrelimOrbit`|`CorrectedOrbit`),
      - `element_set` (`keplerian`|`equinoctial`|`cometary`),
      - `rms` (dimensionless residual metric),
      - plus the native orbital element fields.

    Notes
    ----------
    * The `variant` is inferred from the string representation, which mirrors
      the Rust enum variants (stable in Outfit).
    """
    records: list[Dict[str, Any]] = []
    for obj_id, (res, rms) in ok.items():
        edict = res.to_dict()  # native element keys
        element_set = _detect_element_set(edict)
        variant = "CorrectedOrbit" if "corrected" in str(res).lower() else "PrelimOrbit"
        records.append(
            {
                "object_id": obj_id,
                "variant": variant,
                "element_set": element_set,
                "rms": float(rms),
                **edict,
            }
        )
    return pd.DataFrame.from_records(records)


def _rows_from_err_map(err: Dict[Any, str]) -> pd.DataFrame:
    """
    Flatten the error map to a diagnostic DataFrame.

    Parameters
    -----------------
    * `err`: Mapping `object_id -> error_message`.

    Returns
    ----------
    * `pd.DataFrame` with `object_id` and `error` columns (empty if no errors).

    Notes
    ----------
    * This shape is convenient for joining/merging with the success table.
    """
    if not err:
        return pd.DataFrame(columns=["object_id", "error"])
    return pd.DataFrame({"object_id": list(err.keys()), "error": list(err.values())})


@pd.api.extensions.register_dataframe_accessor("outfit")
class OutfitAccessor:
    """
    Pandas accessor for running Gauss IOD from a DataFrame.

    Use via the attribute accessor ``DataFrame.outfit``. It exposes
    :meth:`estimate_orbits` to run a vectorized Initial Orbit Determination over
    a flat table of astrometric measurements.

    Examples
    --------
    Basic usage with degrees and arcseconds
    >>> out = df.outfit.estimate_orbits(env, params, observer, ra_error=0.5, dec_error=0.5)

    Radians workflow
    >>> out = df.outfit.estimate_orbits(
    ...     env, params, observer,
    ...     ra_error=1e-6, dec_error=1e-6,
    ...     units="radians",
    ... )
    """

    def __init__(self, pandas_obj: pd.DataFrame) -> None:
        self._df = pandas_obj

    def _validate_schema(self, schema: Schema) -> None:
        """
        Validate presence of the required columns.

        Parameters
        -----------------
        * `schema`: Column mapping to validate.

        Raises
        ----------
        * `ValueError` if one or more required columns are missing.
        """
        missing = [
            c
            for c in (schema.tid, schema.mjd, schema.ra, schema.dec)
            if c not in self._df.columns
        ]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

    def estimate_orbits(
        self,
        env: PyOutfit,
        params: IODParams,
        observer: Observer,
        ra_error: float,
        dec_error: float,
        *,
        schema: Schema = Schema(),
        units: Literal["degrees", "radians"] = "degrees",
        rng_seed: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Run Gauss IOD on a flat astrometry table and return a one-row-per-object
        summary.

        The input DataFrame must at least provide a trajectory/object identifier,
        Modified Julian Date in TT, and right ascension/declination angles. The
        names of these columns are defined by `schema` (defaults are `tid`, `mjd`,
        `ra`, `dec`).

        Parameters
        ----------
        env : PyOutfit
            Configured computation engine, including ephemerides, the error model
            and the available observers.
        params : IODParams
            IOD configuration controlling triplet search, Monte Carlo
            perturbations, filters, and tolerances.
        observer : Observer
            Default observer applied to all rows. This covers the common
            single-station use case.
        ra_error : float
            Uncertainty on right ascension. When `units="degrees"`, the value is
            interpreted in arcseconds; when `units="radians"`, the value is in
            radians.
        dec_error : float
            Uncertainty on declination. Follows the same unit convention as
            `ra_error`.
        schema : Schema, optional
            Column mapping for the current DataFrame. Use this to adapt to
            non-standard column names. The default expects `tid`, `mjd`, `ra`,
            and `dec`.
        units : {"degrees", "radians"}, default "degrees"
            Angle units for `ra`/`dec` and the corresponding uncertainties.
            Degrees imply RA/DEC are in degrees and uncertainties are in
            arcseconds. Radians imply both values and uncertainties are already
            expressed in radians.
        rng_seed : int or None, optional
            Optional seed to make randomized internals deterministic.

        Returns
        -------
        pd.DataFrame
            A summary DataFrame with one row per object containing the RMS value,
            the detected orbital element set, the orbit variant, and the native
            orbital elements returned by the engine. The `object_id` column
            mirrors the original identifier from `schema.tid`. When some
            trajectories fail, additional rows are included with `object_id` and
            an `error` message; successful rows include `status="ok"`.

        Raises
        ------
        ValueError
            Raised when required columns are missing in the DataFrame, or when
            `units` is not one of {"degrees", "radians"}.

        Notes
        -----
        Ingestion is vectorized and avoids Python-level grouping. For
        `units="degrees"`, `ra_error` and `dec_error` are converted from
        arcseconds to radians using `RADSEC`. If needed, multi-observer or
        per-row observatory support can be added by extending the
        `TrajectorySet.from_numpy_*` builder to accept vectorized observers.

        See Also
        --------
        - `TrajectorySet.estimate_all_orbits`:
            Batch Gauss IOD over trajectories.

        - `GaussResult.to_dict`:
            Native orbital element names used in the output.

        - `Schema`:
            Column mapping used to interpret the input DataFrame.
        """
        # --- Validate input columns
        self._validate_schema(schema)

        # --- Extract columns
        df = self._df
        tid = _ensure_object_ids(df[schema.tid].values)
        mjd = _ensure_float64(df[schema.mjd].values)
        ra = _ensure_float64(df[schema.ra].values)
        dec = _ensure_float64(df[schema.dec].values)

        # --- Convert angles if needed
        if units == "degrees":
            ra_rad = np.deg2rad(ra)
            dec_rad = np.deg2rad(dec)
            # arcsec -> radians
            ra_error = ra_error / RADSEC
            dec_error = dec_error / RADSEC
        elif units == "radians":
            ra_rad = ra
            dec_rad = dec
        else:
            raise ValueError("units must be 'degrees' or 'radians'")

        # --- Build TrajectorySet from flat arrays (radians ingestion)
        tset = TrajectorySet.from_numpy_radians(
            env,
            tid,
            ra_rad.astype(np.float64),
            dec_rad.astype(np.float64),
            float(ra_error),
            float(dec_error),
            mjd.astype(np.float64),
            observer,
        )

        # --- Run batch IOD
        ok, err = tset.estimate_all_orbits(env, params, seed=rng_seed)

        # --- Build output frames
        df_ok = _rows_from_ok_map(ok)
        df_err = _rows_from_err_map(err)

        # Prefer returning successes; include errors if any as additional rows
        if len(df_err) > 0:
            df_ok["status"] = "ok"
            df_err["status"] = "error"
            return pd.concat([df_ok, df_err], ignore_index=True, sort=False)
        return df_ok
