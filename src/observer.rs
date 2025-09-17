use std::sync::Arc;

use outfit::{constants::Kilometer, Degree};
use pyo3::{pyclass, pymethods, PyResult};

use crate::IntoPyResult;

/// Python wrapper for `Observer`.
///
/// See also
/// ------------
/// * [`Observer`] – Native Rust observer type.
#[pyclass]
pub struct Observer {
    // Use Arc to align with your existing API that often returns Arc<Observer>.
    pub(crate) inner: Arc<outfit::Observer>,
}

#[pymethods]
impl Observer {
    /// Create a new PyObserver.
    #[new]
    pub fn new(
        longitude: Degree,
        latitude: Degree,
        elevation: Kilometer,
        name: Option<String>,
        ra_accuracy: Option<f64>,
        dec_accuracy: Option<f64>,
    ) -> PyResult<Self> {
        Ok(Self {
            inner: Arc::new(
                outfit::Observer::new(
                    longitude,
                    latitude,
                    elevation,
                    name,
                    ra_accuracy,
                    dec_accuracy,
                )
                .into_py()?,
            ),
        })
    }

    /// Return the string representation of the observer.
    fn __str__(&self) -> PyResult<String> {
        Ok(format!("<PyObserver {:#}>", self.inner))
    }

    /// Return the developer-oriented representation of the observer.
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("<PyObserver {}>", self.inner))
    }
}
