from __future__ import annotations

from py_outfit.orbit_type.equinoctial import EquinoctialElements
from py_outfit.orbit_type.keplerian import KeplerianElements

class CometaryElements:
    """
    Cometary orbital elements (q, e ≥ 1, i, Ω, ω, ν).

    Units
    ----------
    * `reference_epoch`: MJD (TDB)
    * `perihelion_distance` (q): AU
    * `eccentricity` (e): dimensionless; `e = 1` parabolic, `e > 1` hyperbolic
    * `inclination` (i): radians
    * `ascending_node_longitude` (Ω): radians
    * `periapsis_argument` (ω): radians
    * `true_anomaly` (ν): radians at reference epoch

    See also
    ------------
    * `to_keplerian` — Convert to Keplerian (hyperbolic only).
    * `to_equinoctial` — Convert to Equinoctial (hyperbolic only).
    """

    def __init__(
        self,
        reference_epoch: float,
        perihelion_distance: float,
        eccentricity: float,
        inclination: float,
        ascending_node_longitude: float,
        periapsis_argument: float,
        true_anomaly: float,
    ) -> None:
        """
        Build a new cometary element set.

        Parameters
        -----------------
        * `reference_epoch`: MJD (TDB).
        * `perihelion_distance`: q (AU).
        * `eccentricity`: e (≥ 1).
        * `inclination`: i (rad).
        * `ascending_node_longitude`: Ω (rad).
        * `periapsis_argument`: ω (rad).
        * `true_anomaly`: ν at epoch (rad).

        Returns
        ----------
        CometaryElements
            A new cometary element set.
        """
        ...

    # --- Read-only properties ---
    @property
    def reference_epoch(self) -> float:
        """Reference epoch of the element set (MJD, TDB)."""
        ...

    @property
    def perihelion_distance(self) -> float:
        """Perihelion distance q (AU)."""
        ...

    @property
    def eccentricity(self) -> float:
        """Eccentricity e (dimensionless). For cometary: e ≥ 1."""
        ...

    @property
    def inclination(self) -> float:
        """Inclination i (radians)."""
        ...

    @property
    def ascending_node_longitude(self) -> float:
        """Longitude of the ascending node Ω (radians)."""
        ...

    @property
    def periapsis_argument(self) -> float:
        """Argument of periapsis ω (radians)."""
        ...

    @property
    def true_anomaly(self) -> float:
        """True anomaly ν at the reference epoch (radians)."""
        ...

    # --- Conversions ---
    def to_keplerian(self) -> KeplerianElements:
        """
        Convert cometary → Keplerian elements.

        Returns
        ----------
        KeplerianElements
            if `e > 1`.

        Raises
        ----------
        * `ValueError` if `e == 1` (parabolic case unsupported by this conversion).
        """
        ...

    def to_equinoctial(self) -> EquinoctialElements:
        """
        Convert cometary → Equinoctial elements.

        Returns
        ----------
        EquinoctialElements
            if `e > 1`

        Raises
        ----------
        * `ValueError` if `e == 1` (parabolic case unsupported by this conversion).
        """
        ...

    # --- Representations ---
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
