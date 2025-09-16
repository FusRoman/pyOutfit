use pyo3::prelude::*;
use pyo3::types::PyDict;

use outfit::{
    CometaryElements as RsCometary, EquinoctialElements as RsEquinoctial,
    KeplerianElements as RsKeplerian,
};
use outfit::{GaussResult as RsGaussResult, OrbitalElements as RsOrbitalElements};

use crate::IntoPyResult;

/// Python wrapper for GaussResult.
#[pyclass]
pub struct GaussResult {
    pub(crate) inner: RsGaussResult,
}

impl From<RsGaussResult> for GaussResult {
    fn from(w: RsGaussResult) -> Self {
        Self { inner: w }
    }
}
impl AsRef<RsGaussResult> for GaussResult {
    fn as_ref(&self) -> &RsGaussResult {
        &self.inner
    }
}

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

/// Python wrapper for Equinoctial elements.
#[pyclass]
#[derive(Clone)]
pub struct EquinoctialElements {
    pub(crate) inner: RsEquinoctial,
}
impl From<RsEquinoctial> for EquinoctialElements {
    fn from(e: RsEquinoctial) -> Self {
        Self { inner: e }
    }
}

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
impl GaussResult {
    /// Whether the result includes the post-Gauss correction step.
    ///
    /// Return
    /// ----------
    /// * `True` if `CorrectedOrbit`, `False` if `PrelimOrbit`.
    ///
    /// See also
    /// ------------
    /// * [`is_preliminary`] – Companion boolean for the first stage result.
    /// * [`elements_type`] – Returns `"keplerian" | "equinoctial" | "cometary"`.
    #[pyo3(text_signature = "(self)")]
    fn is_corrected(&self) -> bool {
        matches!(self.inner, RsGaussResult::CorrectedOrbit(_))
    }

    /// Whether this is a preliminary Gauss solution (before corrections).
    ///
    /// Return
    /// ----------
    /// * `True` if `PrelimOrbit`, `False` otherwise.
    ///
    /// See also
    /// ------------
    /// * [`is_corrected`]
    #[pyo3(text_signature = "(self)")]
    fn is_preliminary(&self) -> bool {
        matches!(self.inner, RsGaussResult::PrelimOrbit(_))
    }

    /// Return the element family used inside (`"keplerian" | "equinoctial" | "cometary"`).
    ///
    /// Return
    /// ----------
    /// * A string describing the underlying element set.
    ///
    /// See also
    /// ------------
    /// * [`keplerian`], [`equinoctial`], [`cometary`]
    #[pyo3(text_signature = "(self)")]
    fn elements_type(&self) -> &'static str {
        let elems = match &self.inner {
            RsGaussResult::PrelimOrbit(e) | RsGaussResult::CorrectedOrbit(e) => e,
        };
        match elems {
            RsOrbitalElements::Keplerian(_) => "keplerian",
            RsOrbitalElements::Equinoctial(_) => "equinoctial",
            RsOrbitalElements::Cometary(_) => "cometary",
        }
    }

    /// Extract Keplerian elements if present, else `None`.
    ///
    /// Return
    /// ----------
    /// * `KeplerianElements | None`
    ///
    /// See also
    /// ------------
    /// * [`elements_type`]
    #[pyo3(text_signature = "(self)")]
    fn keplerian(&self) -> Option<KeplerianElements> {
        let elems = match &self.inner {
            RsGaussResult::PrelimOrbit(e) | RsGaussResult::CorrectedOrbit(e) => e,
        };
        match elems {
            RsOrbitalElements::Keplerian(k) => Some(KeplerianElements::from(k.clone())),
            _ => None,
        }
    }

    /// Extract Equinoctial elements if present, else `None`.
    ///
    /// Return
    /// ----------
    /// * `EquinoctialElements | None`
    ///
    /// See also
    /// ------------
    /// * [`elements_type`]
    #[pyo3(text_signature = "(self)")]
    fn equinoctial(&self) -> Option<EquinoctialElements> {
        let elems = match &self.inner {
            RsGaussResult::PrelimOrbit(e) | RsGaussResult::CorrectedOrbit(e) => e,
        };
        match elems {
            RsOrbitalElements::Equinoctial(q) => Some(EquinoctialElements::from(q.clone())),
            _ => None,
        }
    }

    /// Extract Cometary elements if present, else `None`.
    ///
    /// Return
    /// ----------
    /// * `CometaryElements | None`
    ///
    /// See also
    /// ------------
    /// * [`elements_type`]
    #[pyo3(text_signature = "(self)")]
    fn cometary(&self) -> Option<CometaryElements> {
        let elems = match &self.inner {
            RsGaussResult::PrelimOrbit(e) | RsGaussResult::CorrectedOrbit(e) => e,
        };
        match elems {
            RsOrbitalElements::Cometary(c) => Some(CometaryElements::from(c.clone())),
            _ => None,
        }
    }

    /// Convert the result to a Python dict.
    ///
    /// Return
    /// ----------
    /// * A dict with keys:
    ///   * `"stage"`: `"preliminary"` | `"corrected"`
    ///   * `"type"`: `"keplerian"` | `"equinoctial"` | `"cometary"`
    ///   * `"elements"`: a nested dict of the concrete fields.
    ///
    /// See also
    /// ------------
    /// * [`keplerian`], [`equinoctial`], [`cometary`]
    #[pyo3(text_signature = "(self)")]
    fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let d = PyDict::new(py);
        let (stage, elems) = match &self.inner {
            RsGaussResult::PrelimOrbit(e) => ("preliminary", e),
            RsGaussResult::CorrectedOrbit(e) => ("corrected", e),
        };
        d.set_item("stage", stage)?;

        match elems {
            RsOrbitalElements::Keplerian(k) => {
                d.set_item("type", "keplerian")?;
                let e = PyDict::new(py);
                e.set_item("reference_epoch", k.reference_epoch)?;
                e.set_item("semi_major_axis", k.semi_major_axis)?;
                e.set_item("eccentricity", k.eccentricity)?;
                e.set_item("inclination", k.inclination)?;
                e.set_item("ascending_node_longitude", k.ascending_node_longitude)?;
                e.set_item("periapsis_argument", k.periapsis_argument)?;
                e.set_item("mean_anomaly", k.mean_anomaly)?;
                d.set_item("elements", e)?;
            }
            RsOrbitalElements::Equinoctial(q) => {
                d.set_item("type", "equinoctial")?;
                let e = PyDict::new(py);
                e.set_item("reference_epoch", q.reference_epoch)?;
                e.set_item("semi_major_axis", q.semi_major_axis)?;
                e.set_item("eccentricity_sin_lon", q.eccentricity_sin_lon)?;
                e.set_item("eccentricity_cos_lon", q.eccentricity_cos_lon)?;
                e.set_item("tan_half_incl_sin_node", q.tan_half_incl_sin_node)?;
                e.set_item("tan_half_incl_cos_node", q.tan_half_incl_cos_node)?;
                e.set_item("mean_longitude", q.mean_longitude)?;
                d.set_item("elements", e)?;
            }
            RsOrbitalElements::Cometary(c) => {
                d.set_item("type", "cometary")?;
                let e = PyDict::new(py);
                e.set_item("reference_epoch", c.reference_epoch)?;
                e.set_item("perihelion_distance", c.perihelion_distance)?;
                e.set_item("eccentricity", c.eccentricity)?;
                e.set_item("inclination", c.inclination)?;
                e.set_item("ascending_node_longitude", c.ascending_node_longitude)?;
                e.set_item("periapsis_argument", c.periapsis_argument)?;
                e.set_item("true_anomaly", c.true_anomaly)?;
                d.set_item("elements", e)?;
            }
        }

        Ok(d)
    }

    /// Pretty string representation (`str(obj)` in Python).
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    /// Unambiguous representation (`repr(obj)` in Python).
    fn __repr__(&self) -> String {
        format!("<PyGaussResult {}>", self.inner)
    }
}

#[pymethods]
impl KeplerianElements {
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

#[pymethods]
impl EquinoctialElements {
    #[getter]
    fn reference_epoch(&self) -> f64 {
        self.inner.reference_epoch
    }
    #[getter]
    fn semi_major_axis(&self) -> f64 {
        self.inner.semi_major_axis
    }
    #[getter]
    fn eccentricity_sin_lon(&self) -> f64 {
        self.inner.eccentricity_sin_lon
    }
    #[getter]
    fn eccentricity_cos_lon(&self) -> f64 {
        self.inner.eccentricity_cos_lon
    }
    #[getter]
    fn tan_half_incl_sin_node(&self) -> f64 {
        self.inner.tan_half_incl_sin_node
    }
    #[getter]
    fn tan_half_incl_cos_node(&self) -> f64 {
        self.inner.tan_half_incl_cos_node
    }
    #[getter]
    fn mean_longitude(&self) -> f64 {
        self.inner.mean_longitude
    }

    /// Convert equinoctial elements to Keplerian elements.
    ///
    /// Arguments
    /// -----------------
    /// * `self`: Borrowed equinoctial elements.
    ///
    /// Return
    /// ----------
    /// * `KeplerianElements`.
    ///
    /// See also
    /// ------------
    /// * [`to_cometary`] – Convert equinoctial elements to cometary (if `e > 1`).
    /// * [`KeplerianElements::to_cometary`] – Follow-up conversion to cometary.
    #[pyo3(text_signature = "(self)")]
    fn to_keplerian(&self) -> KeplerianElements {
        // Uses: impl From<&EquinoctialElements> for KeplerianElements
        RsKeplerian::from(&self.inner).into()
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

#[pymethods]
impl CometaryElements {
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
