use outfit::{EquinoctialElements as RsEquinoctial, KeplerianElements as RsKeplerian};
use pyo3::{pyclass, pymethods};

use crate::orbit_type::equinoctial::EquinoctialElements;

/// Python wrapper for Keplerian elements.
#[pyclass]
#[derive(Clone)]
pub struct KeplerianElements {
    pub(crate) inner: RsKeplerian,
}
impl From<RsKeplerian> for KeplerianElements {
    fn from(e: RsKeplerian) -> Self {
        Self { inner: e }
    }
}

#[pymethods]
impl KeplerianElements {
    /// Build a new Keplerian element set.
    ///
    /// Arguments
    /// -----------------
    /// * `reference_epoch`: MJD (TDB).
    /// * `semi_major_axis`: Semi-major axis (AU).
    /// * `eccentricity`: Eccentricity (unitless).
    /// * `inclination`: Inclination (rad).
    /// * `ascending_node_longitude`: Longitude of ascending node Ω (rad).
    /// * `periapsis_argument`: Argument of periapsis ω (rad).
    /// * `mean_anomaly`: Mean anomaly M (rad).
    ///
    /// Return
    /// ----------
    /// * A new `KeplerianElements`.
    ///
    /// See also
    /// ------------
    /// * [`to_equinoctial`] – Convert to equinoctial elements.
    #[new]
    #[pyo3(
        text_signature = "(reference_epoch, semi_major_axis, eccentricity, inclination, ascending_node_longitude, periapsis_argument, mean_anomaly)"
    )]
    fn new(
        reference_epoch: f64,
        semi_major_axis: f64,
        eccentricity: f64,
        inclination: f64,
        ascending_node_longitude: f64,
        periapsis_argument: f64,
        mean_anomaly: f64,
    ) -> Self {
        let inner = RsKeplerian {
            reference_epoch,
            semi_major_axis,
            eccentricity,
            inclination,
            ascending_node_longitude,
            periapsis_argument,
            mean_anomaly,
        };
        Self { inner }
    }

    /// Reference epoch (MJD).
    #[getter]
    fn reference_epoch(&self) -> f64 {
        self.inner.reference_epoch
    }
    /// Semi-major axis (AU).
    #[getter]
    fn semi_major_axis(&self) -> f64 {
        self.inner.semi_major_axis
    }
    /// Eccentricity.
    #[getter]
    fn eccentricity(&self) -> f64 {
        self.inner.eccentricity
    }
    /// Inclination (rad).
    #[getter]
    fn inclination(&self) -> f64 {
        self.inner.inclination
    }
    /// Longitude of ascending node Ω (rad).
    #[getter]
    fn ascending_node_longitude(&self) -> f64 {
        self.inner.ascending_node_longitude
    }
    /// Argument of periapsis ω (rad).
    #[getter]
    fn periapsis_argument(&self) -> f64 {
        self.inner.periapsis_argument
    }
    /// Mean anomaly M (rad).
    #[getter]
    fn mean_anomaly(&self) -> f64 {
        self.inner.mean_anomaly
    }

    /// Convert Keplerian elements to Equinoctial elements.
    ///
    /// Arguments
    /// -----------------
    /// * `self`: Borrowed keplerian elements.
    ///
    /// Return
    /// ----------
    /// * `EquinoctialElements`.
    ///
    /// See also
    /// ------------
    /// * [`to_cometary`] – Convert keplerian elements to cometary (if `e > 1`).
    /// * [`CometaryElements::to_cometary`] – Follow-up conversion to cometary.
    #[pyo3(text_signature = "(self)")]
    fn to_equinoctial(&self) -> EquinoctialElements {
        // Uses: impl From<&KeplerianElements> for EquinoctialElements
        RsEquinoctial::from(&self.inner).into()
    }

    /// Pretty string representation (`str(obj)` in Python).
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// Unambiguous representation (`repr(obj)` in Python).
    fn __repr__(&self) -> String {
        format!("<EquinoctialElements {}>", self.inner)
    }
}
