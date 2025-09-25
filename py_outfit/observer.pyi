from typing import Optional


class Observer:
    """
    Observatory/site descriptor.

    Instances are typically obtained from `PyOutfit.get_observer_from_mpc_code(...)` 
    or built directly via the constructor below and then registered with `PyOutfit.add_observer(...)`

    Notes
    ----------
    The underlying Rust struct carries geodetic/ITRF position, codes, and
    precomputed parallax factors for astrometric use. In Python, this is an
    opaque handle; fields are not directly writable.

    See also
    ------------
    * `PyOutfit.add_observer` – Register this observer into an environment.
    """

    def __init__(
        self,
        longitude: float,
        latitude: float,
        elevation: float,
        name: Optional[str] = ...,
        ra_accuracy: Optional[float] = ...,
        dec_accuracy: Optional[float] = ...,
    ) -> None:
        """
        Create a new `Observer`.

        Parameters
        -----------------
        * `longitude`: Geodetic longitude **in degrees** (east-positive).
        * `latitude`: Geodetic latitude **in degrees**.
        * `elevation`: Site elevation **in kilometers** above mean sea level.
        * `name`: Optional human-readable site name.
        * `ra_accuracy`: Optional 1-sigma Right Ascension accuracy (radians).
        * `dec_accuracy`: Optional 1-sigma Declination accuracy (radians).

        Returns
        ----------
        Observer
            A new `Observer` instance.

        Notes
        ----------
        Internally, the Rust implementation converts geodetic coordinates to
        “parallax” form for precise topocentric astrometry. Accuracy fields
        can be used by error models during orbit determination.
        """
        ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
