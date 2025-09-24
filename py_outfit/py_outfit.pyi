# py_outfit.pyi
from __future__ import annotations

from .iod_params import IODParams
from .iod_gauss import GaussResult
from .observer import Observer
from .orbit_type.cometary import CometaryElements
from .orbit_type.equinoctial import EquinoctialElements
from .orbit_type.keplerian import KeplerianElements
from .trajectories import TrajectorySet
from .observations import Observations

"""
Physical and astronomical constants exposed by Outfit.

These values are provided in SI units or astronomical conventions
"""

DPI: float
"""2π, useful for trigonometric conversions (radians)."""

SECONDS_PER_DAY: float
"""Number of seconds in a Julian day (86,400)."""

AU: float
"""Astronomical Unit in kilometers."""

EPS: float
"""Numerical epsilon used for floating-point comparisons (1e-6)."""

T2000: float
"""MJD epoch of J2000.0 (2000-01-01 12:00:00 TT = 51544.5)."""

JDTOMJD: float
"""Conversion constant between Julian Date and Modified Julian Date (2400000.5)."""

RADEG: float
"""Degrees → radians conversion factor."""

RADSEC: float
"""Arcseconds → radians conversion factor."""

RAD2ARC: float
"""Radians → arcseconds conversion factor."""

RADH: float
"""Hours → radians conversion factor (2π / 24)."""

EARTH_MAJOR_AXIS: float
"""Earth equatorial radius in meters (GRS1980/WGS84)."""

EARTH_MINOR_AXIS: float
"""Earth polar radius in meters (GRS1980/WGS84)."""

ERAU: float
"""Earth equatorial radius expressed in astronomical units."""

GAUSS_GRAV: float
"""Gaussian gravitational constant k, used in classical orbit dynamics."""

GAUSS_GRAV_SQUARED: float
"""Square of Gaussian gravitational constant (k²)."""

VLIGHT: float
"""Speed of light in km/s."""

VLIGHT_AU: float
"""Speed of light in astronomical units per day."""

__all__ = [
    "PyOutfit",
    "Observer",
    "IODParams",
    "TrajectorySet",
    "GaussResult",
    "KeplerianElements",
    "EquinoctialElements",
    "CometaryElements",
    "Observations",
    "DPI",
    "SECONDS_PER_DAY",
    "AU",
    "EPS",
    "T2000",
    "JDTOMJD",
    "RADEG",
    "RADSEC",
    "RAD2ARC",
    "RADH",
    "EARTH_MAJOR_AXIS",
    "EARTH_MINOR_AXIS",
    "ERAU",
    "GAUSS_GRAV",
    "GAUSS_GRAV_SQUARED",
    "VLIGHT",
    "VLIGHT_AU",
]

class PyOutfit:
    """
    pyOutfit: Python bindings for the Outfit orbit-determination engine.

    Provides a thin, Pythonic surface around the Rust core `Outfit`, exposing:
    - High-precision ephemerides configuration (e.g., DE440).
    - Observatories management (MPC code lookup, listing).
    - Gauss-based initial orbit determination (via other types in this module).

    See also
    ------------
    * `Outfit` – Core Rust engine (linked from the Rust docs).
    * `IODParams` – Tuning parameters for Gauss IOD.
    * `TrajectorySet` – Batched ingestion and IOD helpers.
    * `Observer` – Observing site handle.
    """

    def __init__(self, ephem: str, error_model: str) -> None:
        """
        Create a new Outfit environment.

        Parameters
        -----------------
        ephem : str
            Ephemerides selector in the form "{source}:{version}". The source must be
            "horizon" (legacy JPL DE binaries) or "naif" (NAIF SPK/DAF kernels). The
            version must be a supported DE series label recognized by Outfit. Common
            values include "DE430", "DE431", "DE440", "DE441", and "DE442". Examples
            include "horizon:DE440" and "naif:DE441". The ephemeris file is resolved
            into the user cache and opened lazily; when downloads are enabled at build
            time, a missing file may be fetched automatically, otherwise an error is
            raised.
        error_model : str
            Astrometric error model. Accepted values are "FCCT14", "VFCC17", and
            "CBM10". Unknown strings default to "FCCT14". The model provides per-site
            RA/DEC bias and RMS used during orbit determination.

        Returns
        ----------
        PyOutfit
            An initialized `PyOutfit` environment.
        """
        ...

    def add_observer(self, observer: Observer) -> None:
        """
        Register an `Observer` in the current environment.

        Parameters
        -----------------
        observer : Observer
            The observatory/site descriptor to register.
        """
        ...

    def show_observatories(self) -> str:
        """
        Render a human-readable list of currently known observatories.

        Returns
        ----------
        str
            A formatted `str` (table/list) of observatories.
        """
        ...

    def get_observer_from_mpc_code(self, code: str) -> Observer:
        """
        Lookup an `Observer` from its MPC code.

        Parameters
        -----------------
        code : str
            MPC observatory code, e.g. "807".

        Returns
        ----------
        Observer
            an `Observer` handle usable with `add_observer`.
        """
        ...
