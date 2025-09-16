use pyo3::prelude::*;
use pyo3::types::{PyDict, PyType};

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
    /// Build a GaussResult from Keplerian elements.
    ///
    /// Arguments
    /// -----------------
    /// * `keplerian`: A `KeplerianElements` instance.
    /// * `corrected`: If `True`, builds a corrected-stage result; otherwise preliminary (default: `False`).
    ///
    /// Return
    /// ----------
    /// * A `GaussResult` containing the provided element set.
    ///
    /// See also
    /// ------------
    /// * [`from_equinoctial`] – Build from equinoctial elements.
    /// * [`from_cometary`] – Build from cometary elements.
    /// * [`is_preliminary`], [`is_corrected`], [`elements_type`]
    #[classmethod]
    #[pyo3(text_signature = "(keplerian, corrected=False)")]
    fn from_keplerian(
        _cls: &Bound<'_, PyType>,
        keplerian: KeplerianElements,
        corrected: Option<bool>,
    ) -> Self {
        let elems = RsOrbitalElements::Keplerian(keplerian.inner);
        if corrected.unwrap_or(false) {
            Self {
                inner: RsGaussResult::CorrectedOrbit(elems),
            }
        } else {
            Self {
                inner: RsGaussResult::PrelimOrbit(elems),
            }
        }
    }

    /// Build a GaussResult from Equinoctial elements.
    ///
    /// Arguments
    /// -----------------
    /// * `equinoctial`: An `EquinoctialElements` instance.
    /// * `corrected`: If `True`, builds a corrected-stage result; otherwise preliminary (default: `False`).
    ///
    /// Return
    /// ----------
    /// * A `GaussResult` containing the provided element set.
    ///
    /// See also
    /// ------------
    /// * [`from_keplerian`] – Build from keplerian elements.
    /// * [`from_cometary`] – Build from cometary elements.
    /// * [`is_preliminary`], [`is_corrected`], [`elements_type`]
    #[classmethod]
    #[pyo3(text_signature = "(equinoctial, corrected=False)")]
    fn from_equinoctial(
        _cls: &Bound<'_, PyType>,
        equinoctial: EquinoctialElements,
        corrected: Option<bool>,
    ) -> Self {
        let elems = RsOrbitalElements::Equinoctial(equinoctial.inner);
        if corrected.unwrap_or(false) {
            Self {
                inner: RsGaussResult::CorrectedOrbit(elems),
            }
        } else {
            Self {
                inner: RsGaussResult::PrelimOrbit(elems),
            }
        }
    }

    /// Build a GaussResult from Cometary elements.
    ///
    /// Arguments
    /// -----------------
    /// * `cometary`: A `CometaryElements` instance.
    /// * `corrected`: If `True`, builds a corrected-stage result; otherwise preliminary (default: `False`).
    ///
    /// Return
    /// ----------
    /// * A `GaussResult` containing the provided element set.
    ///
    /// See also
    /// ------------
    /// * [`from_keplerian`] – Build from keplerian elements.
    /// * [`from_equinoctial`] – Build from equinoctial elements.
    /// * [`is_preliminary`], [`is_corrected`], [`elements_type`]
    #[classmethod]
    #[pyo3(text_signature = "(cometary, corrected=False)")]
    fn from_cometary(
        _cls: &Bound<'_, PyType>,
        cometary: CometaryElements,
        corrected: Option<bool>,
    ) -> Self {
        let elems = RsOrbitalElements::Cometary(cometary.inner);
        if corrected.unwrap_or(false) {
            Self {
                inner: RsGaussResult::CorrectedOrbit(elems),
            }
        } else {
            Self {
                inner: RsGaussResult::PrelimOrbit(elems),
            }
        }
    }

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

#[pymethods]
impl EquinoctialElements {
    /// Build a new Equinoctial element set.
    ///
    /// Arguments
    /// -----------------
    /// * `reference_epoch`: MJD (TDB).
    /// * `semi_major_axis`: Semi-major axis (AU).
    /// * `eccentricity_sin_lon`: h = e * sin(ϖ).
    /// * `eccentricity_cos_lon`: k = e * cos(ϖ).
    /// * `tan_half_incl_sin_node`: p = tan(i/2) * sin(Ω).
    /// * `tan_half_incl_cos_node`: q = tan(i/2) * cos(Ω).
    /// * `mean_longitude`: ℓ (rad).
    ///
    /// Return
    /// ----------
    /// * A new `EquinoctialElements`.
    ///
    /// See also
    /// ------------
    /// * [`to_keplerian`] – Convert to keplerian elements.
    #[new]
    #[pyo3(
        text_signature = "(reference_epoch, semi_major_axis, eccentricity_sin_lon, eccentricity_cos_lon, tan_half_incl_sin_node, tan_half_incl_cos_node, mean_longitude)"
    )]
    fn new(
        reference_epoch: f64,
        semi_major_axis: f64,
        eccentricity_sin_lon: f64,
        eccentricity_cos_lon: f64,
        tan_half_incl_sin_node: f64,
        tan_half_incl_cos_node: f64,
        mean_longitude: f64,
    ) -> Self {
        let inner = RsEquinoctial {
            reference_epoch,
            semi_major_axis,
            eccentricity_sin_lon,
            eccentricity_cos_lon,
            tan_half_incl_sin_node,
            tan_half_incl_cos_node,
            mean_longitude,
        };
        Self { inner }
    }

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
