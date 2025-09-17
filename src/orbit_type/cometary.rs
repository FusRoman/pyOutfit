use pyo3::{pyclass, pymethods, PyResult};

use outfit::{
    CometaryElements as RsCometary, EquinoctialElements as RsEquinoctial,
    KeplerianElements as RsKeplerian,
};

use crate::{
    orbit_type::{equinoctial::EquinoctialElements, keplerian::KeplerianElements},
    IntoPyResult,
};

/// Python wrapper for Cometary elements.
#[pyclass]
#[derive(Clone)]
pub struct CometaryElements {
    pub(crate) inner: RsCometary,
}
impl From<RsCometary> for CometaryElements {
    fn from(e: RsCometary) -> Self {
        Self { inner: e }
    }
}

#[pymethods]
impl CometaryElements {
    /// Build a new Cometary element set.
    ///
    /// Arguments
    /// -----------------
    /// * `reference_epoch`: MJD (TDB).
    /// * `perihelion_distance`: q (AU).
    /// * `eccentricity`: e (≥ 1 for cometary).
    /// * `inclination`: i (rad).
    /// * `ascending_node_longitude`: Ω (rad).
    /// * `periapsis_argument`: ω (rad).
    /// * `true_anomaly`: ν at epoch (rad).
    ///
    /// Return
    /// ----------
    /// * A new `CometaryElements`.
    ///
    /// See also
    /// ------------
    /// * [`to_keplerian`] – Convert to keplerian (hyperbolic).
    /// * [`to_equinoctial`] – Convert to equinoctial (hyperbolic).
    #[new]
    #[pyo3(
        text_signature = "(reference_epoch, perihelion_distance, eccentricity, inclination, ascending_node_longitude, periapsis_argument, true_anomaly)"
    )]
    fn new(
        reference_epoch: f64,
        perihelion_distance: f64,
        eccentricity: f64,
        inclination: f64,
        ascending_node_longitude: f64,
        periapsis_argument: f64,
        true_anomaly: f64,
    ) -> Self {
        let inner = RsCometary {
            reference_epoch,
            perihelion_distance,
            eccentricity,
            inclination,
            ascending_node_longitude,
            periapsis_argument,
            true_anomaly,
        };
        Self { inner }
    }

    #[getter]
    fn reference_epoch(&self) -> f64 {
        self.inner.reference_epoch
    }
    #[getter]
    fn perihelion_distance(&self) -> f64 {
        self.inner.perihelion_distance
    }
    #[getter]
    fn eccentricity(&self) -> f64 {
        self.inner.eccentricity
    }
    #[getter]
    fn inclination(&self) -> f64 {
        self.inner.inclination
    }
    #[getter]
    fn ascending_node_longitude(&self) -> f64 {
        self.inner.ascending_node_longitude
    }
    #[getter]
    fn periapsis_argument(&self) -> f64 {
        self.inner.periapsis_argument
    }
    #[getter]
    fn true_anomaly(&self) -> f64 {
        self.inner.true_anomaly
    }

    /// Convert cometary elements to Keplerian elements.
    ///
    /// Arguments
    /// -----------------
    /// * `self`: Borrowed cometary elements.
    ///
    /// Return
    /// ----------
    /// * `KeplerianElements` if `e > 1`; raises `ValueError` for the parabolic case.
    ///
    /// See also
    /// ------------
    /// * [`to_equinoctial`] – Convert cometary elements to equinoctial.
    /// * [`KeplerianElements::to_equinoctial`] – Follow-up conversion to equinoctial.
    #[pyo3(text_signature = "(self)")]
    fn to_keplerian(&self) -> PyResult<KeplerianElements> {
        // Uses: impl TryFrom<&CometaryElements> for KeplerianElements
        RsKeplerian::try_from(&self.inner)
            .map(KeplerianElements::from)
            .into_py()
    }

    /// Convert cometary elements to Equinoctial elements (via Keplerian).
    ///
    /// Arguments
    /// -----------------
    /// * `self`: Borrowed cometary elements.
    ///
    /// Return
    /// ----------
    /// * `EquinoctialElements` if `e > 1`; raises `ValueError` for the parabolic case.
    ///
    /// See also
    /// ------------
    /// * [`to_keplerian`] – Direct cometary → keplerian conversion.
    /// * [`EquinoctialElements::to_keplerian`] – Inverse mapping.
    #[pyo3(text_signature = "(self)")]
    fn to_equinoctial(&self) -> PyResult<EquinoctialElements> {
        // Uses: impl TryFrom<&CometaryElements> for EquinoctialElements
        RsEquinoctial::try_from(&self.inner)
            .map(EquinoctialElements::from)
            .into_py()
    }

    /// Pretty string representation (`str(obj)` in Python).
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// Unambiguous representation (`repr(obj)` in Python).
    fn __repr__(&self) -> String {
        format!("<CometaryElements {}>", self.inner)
    }
}
