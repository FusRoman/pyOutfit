from __future__ import annotations

from py_outfit.orbit_type.equinoctial import EquinoctialElements


class KeplerianElements:
    """
    Keplerian orbital elements.

    Units
    ----------
    * `reference_epoch`: MJD (TDB)
    * `semi_major_axis`: AU
    * `eccentricity`: dimensionless
    * `inclination`: radians
    * `ascending_node_longitude` (Ω): radians
    * `periapsis_argument` (ω): radians
    * `mean_anomaly` (M): radians

    See also
    ------------
    * `to_equinoctial` — Convert to equinoctial elements.
    """

    def __init__(
        self,
        reference_epoch: float,
        semi_major_axis: float,
        eccentricity: float,
        inclination: float,
        ascending_node_longitude: float,
        periapsis_argument: float,
        mean_anomaly: float,
    ) -> None:
        """
        Build a new Keplerian element set.

        Parameters
        -----------------
        * `reference_epoch`: MJD (TDB).
        * `semi_major_axis`: Semi-major axis (AU).
        * `eccentricity`: Eccentricity (dimensionless).
        * `inclination`: Inclination (radians).
        * `ascending_node_longitude`: Longitude of ascending node Ω (radians).
        * `periapsis_argument`: Argument of periapsis ω (radians).
        * `mean_anomaly`: Mean anomaly M (radians).

        Returns
        ----------
        KeplerianElements
            A new Keplerian element set.
        """
        ...

    # --- Read-only properties ---
    @property
    def reference_epoch(self) -> float:
        """Reference epoch of the element set (MJD, TDB)."""
        ...

    @property
    def semi_major_axis(self) -> float:
        """Semi-major axis a (AU)."""
        ...

    @property
    def eccentricity(self) -> float:
        """Orbital eccentricity e (dimensionless)."""
        ...

    @property
    def inclination(self) -> float:
        """Inclination i (radians)."""
        ...

    @property
    def ascending_node_longitude(self) -> float:
        """Longitude of ascending node Ω (radians)."""
        ...

    @property
    def periapsis_argument(self) -> float:
        """Argument of periapsis ω (radians)."""
        ...

    @property
    def mean_anomaly(self) -> float:
        """Mean anomaly M (radians)."""
        ...

    # --- Conversions ---
    def to_equinoctial(self) -> EquinoctialElements:
        """
        Convert keplerian → equinoctial elements.

        Returns
        ----------
        EquinoctialElements
            The equivalent equinoctial elements.
        """
        ...

    # --- Representations ---
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
