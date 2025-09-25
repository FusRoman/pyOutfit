//! # pyOutfit – High‑Performance Orbit Determination from Python
//!
//! `pyOutfit` is the Python binding layer for the Rust crate **Outfit**: a
//! modern, memory‑safe engine for **Orbit Determination (IOD)**,
//! astrometric observation ingestion, and orbital element conversions.
//! All numerically intensive routines (Gauss triplet solver, filtering,
//! residual evaluation) execute in Rust for performance; Python gets a
//! light, typed, ergonomic API for orchestration and analysis.
//!
//! ## 1. Key Capabilities
//! * **Gauss IOD** on observation triplets with iterative velocity refinement.
//! * **Batch processing**: run IOD across many trajectories and collect per‑object results.
//! * **Multiple orbital representations**: [`KeplerianElements`], [`EquinoctialElements`], [`CometaryElements`].
//! * **Observer management**: create custom observatories or look them up by MPC code.
//! * **Deterministic runs**: pass a seed when estimating all orbits for reproducibility.
//! * **Low overhead**: zero‑copy ingestion path when angles are already in radians; single conversion if in degrees.
//!
//! ## 2. Typical Workflow (Conceptual)
//! 1. Build a global environment (`PyOutfit`) selecting an ephemeris & error model.
//! 2. Register or fetch observers (MPC code, custom geodetic site, etc.).
//! 3. Ingest observations into a [`trajectories::TrajectorySet`].
//! 4. Configure an [`iod_params::IODParams`] object (triplet limits, gaps, noise, execution mode).
//! 5. Run Gauss IOD (single trajectory or all trajectories) to obtain [`GaussResult`] + RMS scores.
//! 6. Inspect, serialize, or transform orbital elements (e.g. Keplerian → Equinoctial).
//!
//! ## 3. Minimal Quick Start
//! ```python
//! from py_outfit import PyOutfit, IODParams, TrajectorySet
//!
//! # 1. Environment (ephemerides + error model)
//! env = PyOutfit("horizon:DE440", "FCCT14")
//!
//! # 2. Observer (fetch by MPC code or create manually)
//! ztf = env.get_observer_from_mpc_code("I41")
//!
//! # 3. (Synthetic) build a TrajectorySet from NumPy arrays (see README for full example)
//! # ts = TrajectorySet.from_numpy_degrees(...)
//!
//! # 4. IOD parameters (defaults + custom triplet cap)
//! params = (IODParams.builder()
//!           .max_triplets(200)
//!           .build())
//!
//! # 5. Batch orbit estimation (returns two dictionaries)
//! # ok, errors = ts.estimate_all_orbits(env, params, seed=42)
//! # print(ok.keys(), errors)
//! ```
//!
//! ## 4. Gauss IOD Internals (High Level)
//! For each candidate triplet (i, j, k):
//! 1. Solve topocentric distances via polynomial root finding.
//! 2. Construct heliocentric position & preliminary velocity at the middle epoch.
//! 3. Apply physical / geometric filters (eccentricity bounds, perihelion range, etc.).
//! 4. Iterate (Lagrange coefficients) to refine velocity if acceptable.
//! 5. Compute RMS of normalized residuals over an extended arc (if available).
//! 6. Keep best‑scoring solution per trajectory (ties resolved deterministically).
//!
//! ## 5. Orbital Elements API
//! A [`GaussResult`] may contain either a *preliminary* or *corrected* solution.
//! Access convenience methods:
//! * `gauss_res.elements_type()` – string tag of stored representation.
//! * `gauss_res.keplerian()` / `equinoctial()` / `cometary()` – return typed element objects (or `None`).
//! * Element objects expose read‑only numeric fields (semi‑major axis, eccentricity, inclination, etc.).
//!
//! ## 6. Error Handling Strategy
//! The Rust core defines `OutfitError` variants (I/O failures, invalid numeric states,
//! infeasible triplets, non‑finite scores). They are converted to Python `RuntimeError`
//! transparently; use idiomatic `try/except` in user code. This module provides a
//! small helper trait to map `Result<T, OutfitError>` into `PyResult<T>` so internal
//! code can still use the `?` operator.
//!
//! ## 7. Performance Notes
//! * Critical loops execute with the Python GIL released (PyO3 `#[pyo3(text_signature=...)]`
//!   not shown here but handled inside Rust functions).
//! * Radian input path avoids memory duplication; degree arrays are converted exactly once.
//! * Batch IOD derives per‑trajectory RNG seeds from a single base seed for reproducibility.
//! * Parallel execution (if exposed in future bindings) will mirror the Rust feature flag `parallel`.
//!
//! ## 8. Determinism & Reproducibility
//! Provide an explicit `seed` to `TrajectorySet.estimate_all_orbits` for deterministic
//! noise realizations / triplet ordering. Omit the seed to let the system RNG choose.
//!
//! ## 9. Limitations / Roadmap (Bindings Perspective)
//! * Only Gauss IOD is currently exposed (no full least‑squares refinement yet).
//! * Alternative IOD methods (e.g. Vaisala) and hyperbolic solutions are planned upstream.
//! * Advanced progress instrumentation & parallel knobs may expand as Rust features mature.
//!
//! ## 10. Design Principles
//! * "Do the heavy work in Rust; keep Python simple".
//! * Predictable, explicit APIs (no hidden global state beyond the environment object).
//! * Clear separation: environment (global), trajectories (container), observations (per object), elements (mathematical state).
//!
//! ## 11. Related Types (See Also)
//! * [`PyOutfit`] – Global ephemerides + observatory registry.
//! * [`observer::Observer`] – Geodetic / MPC site wrapper.
//! * [`iod_params::IODParams`] – Builder for solver & filtering configuration.
//! * [`trajectories::TrajectorySet`] – Mapping of object/trajectory IDs → observations.
//! * [`observations::Observations`] – Per‑trajectory readonly access & NumPy export.
//! * [`iod_gauss::GaussResult`] – Orbit solution (elements + metadata).
//! * [`orbit_type::keplerian::KeplerianElements`], [`orbit_type::equinoctial::EquinoctialElements`], [`orbit_type::cometary::CometaryElements`].
//!
//! ## 12. Minimal Error Handling Example
//! ```python
//! from py_outfit import PyOutfit
//! try:
//!     env = PyOutfit("horizon:DE440", "VFCC17")
//! except RuntimeError as exc:
//!     print("Failed to initialize environment:", exc)
//! ```
pub mod constants;
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
#[pyclass(module = "py_outfit")]
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
        self.inner.add_observer(observer.inner.clone());
        Ok(())
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

    // Constants (2π, AU, Gaussian k, etc.).
    constants::register_constants(m)?;

    Ok(())
}
