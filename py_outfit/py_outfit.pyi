# py_outfit.pyi
from __future__ import annotations

from py_outfit.iod_params import IODParams
from py_outfit.iod_gauss import GaussResult
from py_outfit.observer import Observer
from py_outfit.orbit_type.cometary import CometaryElements
from py_outfit.orbit_type.equinoctial import EquinoctialElements
from py_outfit.orbit_type.keplerian import KeplerianElements
from py_outfit.trajectories import TrajectorySet
from py_outfit.observations import Observations

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

        Arguments
        -----------------
        * `ephem`: Ephemerides selector, e.g. "horizon:DE440".
        * `error_model`: Astrometric error model, e.g. "FCCT14" or "VFCC17".
          Unknown strings default to "FCCT14".

        Return
        ----------
        * A configured `PyOutfit` ready to accept observatories and run IOD.
        """
        ...

    def add_observer(self, observer: Observer) -> None:
        """
        Register an `Observer` in the current environment.

        Arguments
        -----------------
        * `observer`: The observatory/site descriptor to register.

        Return
        ----------
        * `None` on success.
        """
        ...

    def show_observatories(self) -> str:
        """
        Render a human-readable list of currently known observatories.

        Arguments
        -----------------
        * (none)

        Return
        ----------
        * A formatted `str` (table/list) of observatories.
        """
        ...

    def get_observer_from_mpc_code(self, code: str) -> Observer:
        """
        Lookup an `Observer` from its MPC code.

        Arguments
        -----------------
        * `code`: MPC observatory code, e.g. "807".

        Return
        ----------
        * An `Observer` handle usable with `add_observer`.
        """
        ...
