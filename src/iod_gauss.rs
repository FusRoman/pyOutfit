use pyo3::prelude::*;
use pyo3::types::{PyDict, PyType};

use outfit::{GaussResult as RsGaussResult, OrbitalElements as RsOrbitalElements};

use crate::orbit_type::cometary::CometaryElements;
use crate::orbit_type::equinoctial::EquinoctialElements;
use crate::orbit_type::keplerian::KeplerianElements;

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
