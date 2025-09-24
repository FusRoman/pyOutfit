from __future__ import annotations
from typing import Optional, Literal, Dict, Any

from py_outfit.orbit_type.cometary import CometaryElements
from py_outfit.orbit_type.equinoctial import EquinoctialElements
from py_outfit.orbit_type.keplerian import KeplerianElements

class GaussResult:
    """
    Result of a Gauss Initial Orbit Determination (IOD) for a single object.

    Variants
    ----------
    * `PrelimOrbit(OrbitalElements)` — result directly from the Gauss solution.
    * `CorrectedOrbit(OrbitalElements)` — result after the post-Gauss correction step.

    See also
    ------------
    * `from_keplerian`, `from_equinoctial`, `from_cometary` — Build a result from a given element family.
    * `is_preliminary`, `is_corrected` — Stage predicates.
    * `elements_type` — `"keplerian" | "equinoctial" | "cometary"`.
    * `keplerian`, `equinoctial`, `cometary` — Typed extraction helpers (return `None` if mismatched).
    * `to_dict` — Structured dict view for serialization or logging.
    """

    # --- Constructors (class methods) ---
    @classmethod
    def from_keplerian(cls, keplerian: KeplerianElements, corrected: Optional[bool] = ...) -> GaussResult:
        """
        Build a `GaussResult` from Keplerian elements.

        Parameters
        -----------------
        * `keplerian`: Keplerian element set.
        * `corrected`: If `True`, produce a corrected-stage result; otherwise preliminary.

        Returns
        ----------
        GaussResult
            A `GaussResult` embedding the provided elements.
        """
        ...

    @classmethod
    def from_equinoctial(cls, equinoctial: EquinoctialElements, corrected: Optional[bool] = ...) -> GaussResult:
        """
        Build a `GaussResult` from Equinoctial elements.

        Parameters
        -----------------
        * `equinoctial`: Equinoctial element set.
        * `corrected`: If `True`, produce a corrected-stage result; otherwise preliminary.

        Returns
        ----------
        GaussResult
            A `GaussResult` embedding the provided elements.
        """
        ...

    @classmethod
    def from_cometary(cls, cometary: CometaryElements, corrected: Optional[bool] = ...) -> GaussResult:
        """
        Build a `GaussResult` from Cometary elements.

        Parameters
        -----------------
        * `cometary`: Cometary element set.
        * `corrected`: If `True`, produce a corrected-stage result; otherwise preliminary.

        Returns
        ----------
        GaussResult
            A `GaussResult` embedding the provided elements.
        """
        ...

    # --- Stage predicates ---
    def is_corrected(self) -> bool:
        """
        Whether this result is the corrected stage.

        Returns
        ----------
        bool
            `True` for `CorrectedOrbit`, `False` for `PrelimOrbit`.
        """
        ...

    def is_preliminary(self) -> bool:
        """
        Whether this result is the preliminary Gauss solution.

        Returns
        ----------
        bool
            `True` for `PrelimOrbit`, `False` for `CorrectedOrbit`.
        """
        ...

    # --- Introspection ---
    def elements_type(self) -> Literal["keplerian", "equinoctial", "cometary"]:
        """
        Return the family of orbital elements stored inside.

        Returns
        ----------
        Literal["keplerian", "equinoctial", "cometary"]
            The family of orbital elements stored inside.
        """
        ...

    # --- Typed extraction (None if the stored family does not match) ---
    def keplerian(self) -> Optional[KeplerianElements]:
        """
        Extract Keplerian elements if present.

        Returns
        ----------
        KeplerianElements | None
            `KeplerianElements` if the underlying family is keplerian, else `None`.
        """
        ...

    def equinoctial(self) -> Optional[EquinoctialElements]:
        """
        Extract Equinoctial elements if present.

        Returns
        ----------
        EquinoctialElements | None
            `EquinoctialElements` if the underlying family is equinoctial, else `None`.
        """
        ...

    def cometary(self) -> Optional[CometaryElements]:
        """
        Extract Cometary elements if present.

        Returns
        ----------
        CometaryElements | None
            `CometaryElements` if the underlying family is cometary, else `None`.
        """
        ...

    # --- Structured representation ---
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result to a structured Python dict.

        Schema
        ----------
        * `"stage"`: `"preliminary"` | `"corrected"`
        * `"type"`: `"keplerian"` | `"equinoctial"` | `"cometary"`
        * `"elements"`: dict of concrete fields for the stored family:
          - Keplerian: `reference_epoch`, `semi_major_axis`, `eccentricity`,
            `inclination`, `ascending_node_longitude`, `periapsis_argument`, `mean_anomaly`
          - Equinoctial: `reference_epoch`, `semi_major_axis`,
            `eccentricity_sin_lon`, `eccentricity_cos_lon`,
            `tan_half_incl_sin_node`, `tan_half_incl_cos_node`, `mean_longitude`
          - Cometary: `reference_epoch`, `perihelion_distance`, `eccentricity`,
            `inclination`, `ascending_node_longitude`, `periapsis_argument`, `true_anomaly`

        Returns
        ----------
        dict[str, Any]
            A structured dict representation of the result.
        """
        ...

    # --- Representations ---
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
