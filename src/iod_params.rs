use pyo3::{pyclass, pymethods, PyRefMut, PyResult};

use crate::IntoPyResult;

#[pyclass]
pub struct IODParams {
    pub(crate) inner: outfit::IODParams,
    do_parallel: bool,
}

#[pyclass]
pub struct IODParamsBuilder {
    pub(crate) inner: outfit::initial_orbit_determination::IODParamsBuilder,
    do_parallel: bool,
}

impl Default for IODParams {
    fn default() -> Self {
        Self::new()
    }
}

#[pymethods]
impl IODParams {
    /// Create a new IODParams instance with default values.
    #[new]
    pub fn new() -> Self {
        Self {
            inner: outfit::IODParams::default(),
            do_parallel: false,
        }
    }

    /// Return the string representation of the IOD parameters.
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("<IODParams {:#}>", self.inner))
    }

    /// Return the developer-oriented representation of the IOD parameters.
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("<IODParams {}>", self.inner))
    }

    #[staticmethod]
    fn builder() -> PyResult<IODParamsBuilder> {
        Ok(IODParamsBuilder {
            inner: outfit::IODParams::builder(),
            do_parallel: false,
        })
    }

    // --- Read-only getters for testing & user introspection ---
    #[getter]
    pub fn n_noise_realizations(&self) -> usize {
        self.inner.n_noise_realizations
    }
    #[getter]
    pub fn noise_scale(&self) -> f64 {
        self.inner.noise_scale
    }
    #[getter]
    pub fn extf(&self) -> f64 {
        self.inner.extf
    }
    #[getter]
    pub fn dtmax(&self) -> f64 {
        self.inner.dtmax
    }
    #[getter]
    pub fn dt_min(&self) -> f64 {
        self.inner.dt_min
    }
    #[getter]
    pub fn dt_max_triplet(&self) -> f64 {
        self.inner.dt_max_triplet
    }
    #[getter]
    pub fn optimal_interval_time(&self) -> f64 {
        self.inner.optimal_interval_time
    }
    #[getter]
    pub fn max_obs_for_triplets(&self) -> usize {
        self.inner.max_obs_for_triplets
    }
    #[getter]
    pub fn max_triplets(&self) -> u32 {
        self.inner.max_triplets
    }
    #[getter]
    pub fn gap_max(&self) -> f64 {
        self.inner.gap_max
    }

    // Physical filters
    #[getter]
    pub fn max_ecc(&self) -> f64 {
        self.inner.max_ecc
    }
    #[getter]
    pub fn max_perihelion_au(&self) -> f64 {
        self.inner.max_perihelion_au
    }
    #[getter]
    pub fn min_rho2_au(&self) -> f64 {
        self.inner.min_rho2_au
    }
    #[getter]
    pub fn r2_min_au(&self) -> f64 {
        self.inner.r2_min_au
    }
    #[getter]
    pub fn r2_max_au(&self) -> f64 {
        self.inner.r2_max_au
    }

    // Gauss polynomial / solver
    #[getter]
    pub fn aberth_max_iter(&self) -> u32 {
        self.inner.aberth_max_iter
    }
    #[getter]
    pub fn aberth_eps(&self) -> f64 {
        self.inner.aberth_eps
    }
    #[getter]
    pub fn kepler_eps(&self) -> f64 {
        self.inner.kepler_eps
    }
    #[getter]
    pub fn max_tested_solutions(&self) -> usize {
        self.inner.max_tested_solutions
    }

    // Numerics
    #[getter]
    pub fn newton_eps(&self) -> f64 {
        self.inner.newton_eps
    }
    #[getter]
    pub fn newton_max_it(&self) -> usize {
        self.inner.newton_max_it
    }
    #[getter]
    pub fn root_imag_eps(&self) -> f64 {
        self.inner.root_imag_eps
    }

    // Multi-threading
    #[getter]
    pub fn batch_size(&self) -> usize {
        self.inner.batch_size
    }

    #[getter]
    pub fn do_parallel(&self) -> bool {
        self.do_parallel
    }
}

#[pymethods]
impl IODParamsBuilder {
    /// Create a new builder initialized with default values.
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(Self {
            inner: outfit::initial_orbit_determination::IODParamsBuilder::new(),
            do_parallel: false,
        })
    }

    #[pyo3(text_signature = "(v)")]
    pub fn n_noise_realizations(mut slf: PyRefMut<'_, Self>, v: usize) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).n_noise_realizations(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn noise_scale(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).noise_scale(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn extf(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).extf(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn dtmax(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).dtmax(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn dt_min(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).dt_min(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn dt_max_triplet(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).dt_max_triplet(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn optimal_interval_time(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).optimal_interval_time(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn max_obs_for_triplets(mut slf: PyRefMut<'_, Self>, v: usize) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).max_obs_for_triplets(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn max_triplets(mut slf: PyRefMut<'_, Self>, v: u32) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).max_triplets(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn gap_max(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).gap_max(v);
        slf.inner = inner;
        slf
    }

    // --- Physical filters ---
    #[pyo3(text_signature = "(v)")]
    pub fn max_ecc(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).max_ecc(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn max_perihelion_au(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).max_perihelion_au(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn min_rho2_au(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).min_rho2_au(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn r2_min_au(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).r2_min_au(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn r2_max_au(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).r2_max_au(v);
        slf.inner = inner;
        slf
    }

    // --- Gauss polynomial / solver ---
    #[pyo3(text_signature = "(v)")]
    pub fn aberth_max_iter(mut slf: PyRefMut<'_, Self>, v: u32) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).aberth_max_iter(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn aberth_eps(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).aberth_eps(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn kepler_eps(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).kepler_eps(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn max_tested_solutions(mut slf: PyRefMut<'_, Self>, v: usize) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).max_tested_solutions(v);
        slf.inner = inner;
        slf
    }

    // --- Numerics ---
    #[pyo3(text_signature = "(v)")]
    pub fn newton_eps(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).newton_eps(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn newton_max_it(mut slf: PyRefMut<'_, Self>, v: usize) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).newton_max_it(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "(v)")]
    pub fn root_imag_eps(mut slf: PyRefMut<'_, Self>, v: f64) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).root_imag_eps(v);
        slf.inner = inner;
        slf
    }

    // --- Multi-threading ---
    #[pyo3(text_signature = "(v)")]
    pub fn batch_size(mut slf: PyRefMut<'_, Self>, v: usize) -> PyRefMut<'_, Self> {
        let inner = std::mem::take(&mut slf.inner).batch_size(v);
        slf.inner = inner;
        slf
    }

    #[pyo3(text_signature = "($self)")]
    pub fn do_parallel(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.do_parallel = true;
        slf
    }

    #[pyo3(text_signature = "($self)")]
    pub fn do_sequential(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.do_parallel = false;
        slf
    }

    pub fn build(mut slf: PyRefMut<'_, Self>) -> PyResult<IODParams> {
        let inner = std::mem::take(&mut slf.inner).build().into_py()?;
        Ok(IODParams {
            inner,
            do_parallel: slf.do_parallel,
        })
    }
}
