pub mod iod_gauss;
pub mod iod_params;
pub mod observer;
pub mod trajectories;

use outfit::Outfit;
use pyo3::{exceptions::PyRuntimeError, prelude::*};

use crate::{
    iod_gauss::{CometaryElements, EquinoctialElements, GaussResult, KeplerianElements},
    observer::Observer,
};

trait IntoPyResult<T> {
    /// Map OutfitError to PyErr so `?` can be used.
    fn into_py(self) -> PyResult<T>;
}

impl<T> IntoPyResult<T> for Result<T, outfit::outfit_errors::OutfitError> {
    fn into_py(self) -> PyResult<T> {
        self.map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }
}

/// Thin Python wrapper around the Outfit state.
///
/// See also
/// ------------
/// * [`Outfit`] – Core Rust engine.
/// * [`IODParams`] – Tuning parameters for Gauss IOD.
/// * [`TrajectoryExt`] – Helpers to load observations.
#[pyclass]
pub struct PyOutfit {
    inner: Outfit,
}

#[pymethods]
impl PyOutfit {
    /// Create a new Outfit environment.
    ///
    /// Arguments
    /// -----------------
    /// * `ephem` - e.g. "horizon:DE440".
    /// * `error_model` - e.g. "FCCT14".
    ///
    /// Return
    /// ----------
    /// * A new `PyOutfit` instance.
    #[new]
    pub fn new(ephem: &str, error_model: &str) -> PyResult<Self> {
        let model = match error_model {
            "FCCT14" => outfit::error_models::ErrorModel::FCCT14,
            "VFCC17" => outfit::error_models::ErrorModel::VFCC17,
            _ => outfit::error_models::ErrorModel::FCCT14,
        };
        let inner = Outfit::new(ephem, model).into_py()?;
        Ok(Self { inner })
    }

    pub fn add_observer(&mut self, observer: &Observer) -> PyResult<()> {
        Ok(self.inner.add_observer(observer.inner.clone()))
    }

    pub fn show_observatories(&self) -> PyResult<String> {
        Ok(format!("{}", self.inner.show_observatories()))
    }

    pub fn get_observer_from_mpc_code(&self, code: &str) -> PyResult<Observer> {
        Ok(Observer {
            inner: self.inner.get_observer_from_mpc_code(&code.to_string()),
        })
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn py_outfit(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyOutfit>()?;
    m.add_class::<Observer>()?;
    m.add_class::<iod_params::IODParams>()?;
    m.add_class::<trajectories::TrajectorySet>()?;
    m.add_class::<GaussResult>()?;
    m.add_class::<KeplerianElements>()?;
    m.add_class::<EquinoctialElements>()?;
    m.add_class::<CometaryElements>()?;
    Ok(())
}
