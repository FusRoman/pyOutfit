//! # pyOutfit: Python bindings for the Outfit orbit-determination engine
//!
//! `pyOutfit` exposes the high-performance Rust crate **Outfit** to Python,
//! enabling **Gauss-based Initial Orbit Determination (IOD)**, observatory handling,
//! and multi-representation orbital elements from Python with near-native speed.
//!
//! Highlights
//! -----------------
//! * **Fast & safe**: heavy numerical work remains in Rust.
//! * **Pythonic surface**: thin, minimal bindings with clean classes.
//! * **Multiple element sets**: [`KeplerianElements`], [`EquinoctialElements`], [`CometaryElements`].
//! * **Observatories**: query by MPC code, list current sites, and register observers.
//!
//! Quick Start
//! -----------------
//! ```python
//! from py_outfit import PyOutfit, IODParams
//!
//! env = PyOutfit("horizon:DE440", "FCCT14")
//! print(env.show_observatories())
//! ```
//!
//! Error Handling
//! -----------------
//! Rust `OutfitError` values are mapped to Python `RuntimeError` via a small helper
//! so you can use idiomatic `try/except` in Python. See [`IntoPyResult`] below.
//!
//! See also
//! ------------
//! * [`Outfit`] – Core Rust engine.
//! * [`iod_params::IODParams`] – Tuning parameters for Gauss IOD.
//! * [`trajectories::TrajectorySet`] – Batched storage + IOD helpers.
//! * [`observer::Observer`] – Observatory definition and lookup.
pub mod iod_gauss;
pub mod iod_params;
pub mod observations;
pub mod observer;
pub mod orbit_type;
pub mod trajectories;

use outfit::Outfit;
use pyo3::{exceptions::PyRuntimeError, prelude::*};

use crate::{
    iod_gauss::GaussResult,
    observer::Observer,
    orbit_type::{
        cometary::CometaryElements, equinoctial::EquinoctialElements, keplerian::KeplerianElements,
    },
};

/// Map Rust `Result<T, OutfitError>` to `PyResult<T>`.
///
/// This small helper lets us write idiomatic Rust with `?` while producing
/// Python exceptions on failure.
///
/// Arguments
/// -----------------
/// * `self`: A `Result<T, outfit::outfit_errors::OutfitError>`.
///
/// Return
/// ----------
/// * A `PyResult<T>` where any `OutfitError` is converted to `PyRuntimeError`.
///
/// See also
/// ------------
/// * [`PyRuntimeError`] – Python exception type used for error forwarding.
/// * [`outfit::outfit_errors::OutfitError`] – Core error enum in Outfit.
trait IntoPyResult<T> {
    /// Map OutfitError to PyErr so `?` can be used.
    fn into_py(self) -> PyResult<T>;
}

impl<T> IntoPyResult<T> for Result<T, outfit::outfit_errors::OutfitError> {
    fn into_py(self) -> PyResult<T> {
        self.map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }
}

/// Thin Python wrapper around the global Outfit state.
///
/// `PyOutfit` owns the underlying [`Outfit`] engine and provides ergonomic
/// Python methods to configure ephemerides, register observatories, and
/// access IOD facilities exposed elsewhere in this module.
///
/// See also
/// ------------
/// * [`Outfit`] – Core Rust engine.
/// * [`iod_params::IODParams`] – Tuning parameters for Gauss IOD.
/// * [`trajectories::TrajectorySet`] – Helpers to load observations.
/// * [`observer::Observer`] – Observatory handle used by `PyOutfit`.
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
    /// * `ephem` - Ephemerides selector (e.g. `"horizon:DE440"`).
    /// * `error_model` - Astrometric error model (e.g. `"FCCT14"` or `"VFCC17"`).
    ///
    /// Return
    /// ----------
    /// * A new `PyOutfit` instance ready to accept observatories and run IOD.
    ///
    /// Notes
    /// ----------
    /// * Unknown `error_model` strings default to `FCCT14`.
    /// * All heavy computations remain in Rust; Python merely orchestrates flows.
    ///
    /// See also
    /// ------------
    /// * [`Outfit::new`] – Builder in the Rust core.
    /// * [`iod_params::IODParams`] – IOD tuning parameters.
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

    /// Add an `Observer` to the current environment.
    ///
    /// Arguments
    /// -----------------
    /// * `observer` - The observer to register (site location, codes, etc.).
    ///
    /// Return
    /// ----------
    /// * `Ok(())` on success.
    ///
    /// See also
    /// ------------
    /// * [`observer::Observer`] – Construction and fields.
    pub fn add_observer(&mut self, observer: &Observer) -> PyResult<()> {
        Ok(self.inner.add_observer(observer.inner.clone()))
    }

    /// Render a human-readable list of currently known observatories.
    ///
    /// Arguments
    /// -----------------
    /// * *(none)*
    ///
    /// Return
    /// ----------
    /// * A `String` with a formatted table or list of observatories.
    ///
    /// Example
    /// -----------------
    /// ```python
    /// env = PyOutfit("horizon:DE440", "FCCT14")
    /// print(env.show_observatories())
    /// ```
    pub fn show_observatories(&self) -> PyResult<String> {
        Ok(format!("{}", self.inner.show_observatories()))
    }

    /// Lookup an `Observer` from its MPC code.
    ///
    /// Arguments
    /// -----------------
    /// * `code` - MPC observatory code, e.g. `"807"`.
    ///
    /// Return
    /// ----------
    /// * An [`Observer`] handle usable with [`PyOutfit::add_observer`].
    ///
    /// See also
    /// ------------
    /// * [`observer::Observer`] – Python-visible wrapper for observatories.
    pub fn get_observer_from_mpc_code(&self, code: &str) -> PyResult<Observer> {
        Ok(Observer {
            inner: self.inner.get_observer_from_mpc_code(&code.to_string()),
        })
    }
}

/// Python module entry-point.
///
/// The function name must match `lib.name` in `Cargo.toml` so that Python
/// can import this module (e.g. `import py_outfit`).
///
/// Arguments
/// -----------------
/// * `m` - The Python module to populate with classes and functions.
///
/// Return
/// ----------
/// * `PyResult<()>` indicating success or a Python exception.
///
/// See also
/// ------------
/// * [`pyo3::prelude::pymodule`] – PyO3 macro for module initialization.
#[pymodule]
fn py_outfit(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Core environment + domain types.
    m.add_class::<PyOutfit>()?;
    m.add_class::<Observer>()?;

    // IOD configuration and trajectory handling.
    m.add_class::<iod_params::IODParams>()?;
    m.add_class::<trajectories::TrajectorySet>()?;
    m.add_class::<observations::Observations>()?;

    // Orbit results and element sets.
    m.add_class::<GaussResult>()?;
    m.add_class::<KeplerianElements>()?;
    m.add_class::<EquinoctialElements>()?;
    m.add_class::<CometaryElements>()?;

    Ok(())
}
