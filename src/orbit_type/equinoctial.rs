use outfit::{EquinoctialElements as RsEquinoctial, KeplerianElements as RsKeplerian};

use pyo3::{pyclass, pymethods};

use crate::orbit_type::keplerian::KeplerianElements;

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
