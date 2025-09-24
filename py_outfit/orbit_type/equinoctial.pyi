from __future__ import annotations

from py_outfit.orbit_type.keplerian import KeplerianElements

class EquinoctialElements:
    """
    Equinoctial orbital elements.

    Definitions
    ----------
    * `h = e * sin(ϖ)` with ϖ = Ω + ω
    * `k = e * cos(ϖ)`
    * `p = tan(i/2) * sin(Ω)`
    * `q = tan(i/2) * cos(Ω)`
    * `λ` (here `mean_longitude`) = mean longitude (rad), i.e. Ω + ω + M in the usual convention

    Units
    ----------
    * `reference_epoch`: MJD (TDB)
    * `semi_major_axis`: AU
    * `h`, `k`, `p`, `q`: dimensionless
    * `mean_longitude`: radians

    See also
    ------------
    * `to_keplerian` — Convert to Keplerian elements.
    """

    def __init__(
        self,
        reference_epoch: float,
        semi_major_axis: float,
        eccentricity_sin_lon: float,
        eccentricity_cos_lon: float,
        tan_half_incl_sin_node: float,
        tan_half_incl_cos_node: float,
        mean_longitude: float,
    ) -> None:
        """
        Build a new equinoctial element set.

        Parameters
        -----------------
        * `reference_epoch`: MJD (TDB).
        * `semi_major_axis`: Semi-major axis (AU).
        * `eccentricity_sin_lon`: h = e * sin(ϖ).
        * `eccentricity_cos_lon`: k = e * cos(ϖ).
        * `tan_half_incl_sin_node`: p = tan(i/2) * sin(Ω).
        * `tan_half_incl_cos_node`: q = tan(i/2) * cos(Ω).
        * `mean_longitude`: λ (radians).

        Returns
        ----------
        EquinoctialElements
            A new equinoctial element set.
        """
        ...

    # --- Read-only properties (exact names as exposed by the binding) ---
    @property
    def reference_epoch(self) -> float:
        """Reference epoch of the element set (MJD, TDB)."""
        ...

    @property
    def semi_major_axis(self) -> float:
        """Semi-major axis a (AU)."""
        ...

    @property
    def eccentricity_sin_lon(self) -> float:
        """h = e * sin(ϖ), dimensionless."""
        ...

    @property
    def eccentricity_cos_lon(self) -> float:
        """k = e * cos(ϖ), dimensionless."""
        ...

    @property
    def tan_half_incl_sin_node(self) -> float:
        """p = tan(i/2) * sin(Ω), dimensionless."""
        ...

    @property
    def tan_half_incl_cos_node(self) -> float:
        """q = tan(i/2) * cos(Ω), dimensionless."""
        ...

    @property
    def mean_longitude(self) -> float:
        """Mean longitude λ (radians)."""
        ...

    # --- Conversions ---
    def to_keplerian(self) -> KeplerianElements:
        """
        Convert equinoctial → Keplerian elements.

        Returns
        ----------
        KeplerianElements
            The equivalent Keplerian elements.
        """
        ...

    # --- Representations ---
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
