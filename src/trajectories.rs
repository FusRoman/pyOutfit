use std::sync::Arc;

use numpy::PyReadonlyArray1;
use outfit::{
    trajectories::{
        batch_reader::ObservationBatch, trajectory_file::TrajectoryFile,
        trajectory_fit::TrajectoryFit,
    },
    FullOrbitResult, ObjectNumber,
};
use pyo3::{exceptions::PyValueError, prelude::*, types::PyDict};

use rand::rngs::StdRng;
use rand::SeedableRng;

use crate::{
    iod_gauss::GaussResult, iod_params::IODParams, observer::Observer, IntoPyResult, PyOutfit,
};

use pyo3::types::{PyInt, PyString};
use pyo3::IntoPyObject;

/// Python wrapper for `TrajectorySet`.
///
/// See also
/// ------------
/// * [`TrajectorySet`] – Native Rust trajectory container built from observations.
/// * [`ObservationBatch`] – Intermediate batch container (radians-based).
#[pyclass]
pub struct TrajectorySet {
    pub(crate) inner: outfit::TrajectorySet,
}

#[pymethods]
impl TrajectorySet {
    /// Human-friendly representation.
    fn __repr__(&self) -> String {
        format!("TrajectorySet(num_trajectories={})", self.inner.len())
    }

    fn total_observations(&self) -> usize {
        self.inner.total_observations()
    }

    fn number_of_trajectories(&self) -> usize {
        self.inner.number_of_trajectories()
    }

    fn get_traj_stat(&self) -> String {
        if let Some(stat) = self.inner.obs_count_stats() {
            format!("{:#}", stat)
        } else {
            "No trajectories available.".to_string()
        }
    }

    /// Build a `TrajectorySet` from NumPy arrays already expressed in **radians** and **MJD (TT)**.
    ///
    /// Solve the ingestion path using a zero-copy `ObservationBatch::from_radians_borrowed`
    /// and then grouping observations into trajectories via `TrajectorySet::new_from_vec`.
    ///
    /// Arguments
    /// -----------------
    /// * `trajectory_id`: `np.ndarray[dtype=np.uint32]` — one ID per observation.
    /// * `ra`: `np.ndarray[dtype=np.float64]` — right ascension in **radians**.
    /// * `dec`: `np.ndarray[dtype=np.float64]` — declination in **radians**.
    /// * `error_ra_rad`: `float` — 1-σ RA uncertainty (**radians**) applied uniformly to the batch.
    /// * `error_dec_rad`: `float` — 1-σ DEC uncertainty (**radians**) applied uniformly to the batch.
    /// * `mjd_tt`: `np.ndarray[dtype=np.float64]` — epochs in **MJD (TT)** (days).
    /// * `observer`: `PyObserver` — single observer for the whole batch.
    ///
    /// Return
    /// ----------
    /// * A new `PyTrajectorySet` populated from the provided inputs.
    ///
    /// Panics
    /// ----------
    /// * Never panics; returns `ValueError` on length mismatches.
    ///
    /// See also
    /// ----------
    /// * [`Self::trajectory_set_from_numpy_degrees`] – Degrees/arcsec variant with conversions.
    #[allow(clippy::too_many_arguments)]
    #[staticmethod]
    pub fn trajectory_set_from_numpy_radians(
        py: Python<'_>,
        pyoutfit: &mut PyOutfit,
        trajectory_id: PyReadonlyArray1<u32>,
        ra: PyReadonlyArray1<f64>,
        dec: PyReadonlyArray1<f64>,
        error_ra_rad: f64,
        error_dec_rad: f64,
        mjd_tt: PyReadonlyArray1<f64>,
        observer: &Observer,
    ) -> PyResult<TrajectorySet> {
        // Borrow NumPy memory as Rust slices (lifetime bound to `py`/this function).
        let tid = trajectory_id.as_slice()?;
        let ra_rad = ra.as_slice()?;
        let dec_rad = dec.as_slice()?;
        let t_mjd = mjd_tt.as_slice()?;

        // Length checks (clear Python-side errors instead of debug-assert).
        let n = tid.len();
        if ra_rad.len() != n || dec_rad.len() != n || t_mjd.len() != n {
            return Err(PyValueError::new_err(format!(
                "Length mismatch: trajectory_id={}, ra={}, dec={}, mjd={}",
                n,
                ra_rad.len(),
                dec_rad.len(),
                t_mjd.len()
            )));
        }

        // Build zero-copy batch (Cow::Borrowed) and immediately consume it into a TrajectorySet.
        let batch = ObservationBatch::from_radians_borrowed(
            tid,
            ra_rad,
            dec_rad,
            error_ra_rad,
            error_dec_rad,
            t_mjd,
        );

        // Heavy work without the GIL (ephemerides, positions, etc.).
        let observer_arc: Arc<outfit::Observer> = observer.inner.clone();
        let ts_res = py.detach(|| {
            outfit::TrajectorySet::new_from_vec(&mut pyoutfit.inner, &batch, observer_arc)
        });

        ts_res.map(|ts| TrajectorySet { inner: ts }).into_py()
    }

    /// Build a `TrajectorySet` from NumPy arrays in **degrees** (RA/DEC), **arcseconds** (uncertainties),
    /// and **MJD (TT)** for epochs.
    ///
    /// Internally converts to radians once via `ObservationBatch::from_degrees_owned`,
    /// then groups observations with `TrajectorySet::new_from_vec`.
    ///
    /// Arguments
    /// -----------------
    /// * `trajectory_id`: `np.ndarray[dtype=np.uint32]` — one ID per observation.
    /// * `ra_deg`: `np.ndarray[dtype=np.float64]` — right ascension in **degrees**.
    /// * `dec_deg`: `np.ndarray[dtype=np.float64]` — declination in **degrees**.
    /// * `error_ra_arcsec`: `float` — 1-σ RA uncertainty (**arcseconds**).
    /// * `error_dec_arcsec`: `float` — 1-σ DEC uncertainty (**arcseconds**).
    /// * `mjd_tt`: `np.ndarray[dtype=np.float64]` — epochs in **MJD (TT)** (days).
    /// * `observer`: `PyObserver` — single observer for the whole batch.
    ///
    /// Return
    /// ----------
    /// * A new `PyTrajectorySet` populated from the provided inputs.
    ///
    /// Panics
    /// ----------
    /// * Never panics; returns `ValueError` on length mismatches.
    ///
    /// See also
    /// ------------
    /// * [`Self::trajectory_set_from_numpy_radians`] – Zero-copy variant for radian inputs.
    #[allow(clippy::too_many_arguments)]
    #[staticmethod]
    pub fn trajectory_set_from_numpy_degrees(
        py: Python<'_>,
        pyoutfit: &mut PyOutfit,
        trajectory_id: PyReadonlyArray1<u32>,
        ra_deg: PyReadonlyArray1<f64>,
        dec_deg: PyReadonlyArray1<f64>,
        error_ra_arcsec: f64,
        error_dec_arcsec: f64,
        mjd_tt: PyReadonlyArray1<f64>,
        observer: &Observer,
    ) -> PyResult<TrajectorySet> {
        let tid = trajectory_id.as_slice()?;
        let ra_d = ra_deg.as_slice()?;
        let dec_d = dec_deg.as_slice()?;
        let t_mjd = mjd_tt.as_slice()?;

        let n = tid.len();
        if ra_d.len() != n || dec_d.len() != n || t_mjd.len() != n {
            return Err(PyValueError::new_err(format!(
                "Length mismatch: trajectory_id={}, ra_deg={}, dec_deg={}, mjd={}",
                n,
                ra_d.len(),
                dec_d.len(),
                t_mjd.len()
            )));
        }

        // Build owned/converted batch once.
        let batch = ObservationBatch::from_degrees_owned(
            tid,
            ra_d,
            dec_d,
            error_ra_arcsec,
            error_dec_arcsec,
            t_mjd,
        );

        let observer_arc: Arc<outfit::Observer> = observer.inner.clone();
        let ts_res = py.detach(|| {
            outfit::TrajectorySet::new_from_vec(&mut pyoutfit.inner, &batch, observer_arc)
        });

        ts_res.map(|ts| TrajectorySet { inner: ts }).into_py()
    }

    /// Estimate the best orbit for **all trajectories** in this set.
    ///
    /// Runs Gauss-based initial orbit determination for each trajectory, using
    /// the provided `Outfit` state and `IODParams`. A RNG is created locally:
    /// - when `seed` is provided, a deterministic `StdRng::seed_from_u64(seed)` is used;
    /// - otherwise, `StdRng::from_entropy()` is used.
    ///
    /// Arguments
    /// -----------------
    /// * `env`: Global Outfit state (ephemeris, EOP, error model).
    /// * `params`: IOD configuration parameters.
    /// * `seed`: Optional seed for deterministic RNG (u64). If `None`, a random seed is used.
    ///
    /// Return
    /// ----------
    /// * A `dict[int, PyGaussResult]` mapping each `trajectory_id` to its orbit-estimation result.
    ///
    /// See also
    /// ------------
    /// * [`TrajectorySet::trajectory_set_from_numpy_radians`] – Build set from radian inputs.
    /// * [`TrajectorySet::trajectory_set_from_numpy_degrees`] – Build set with degree→radian conversion.
    /// * [`PyIODParams`] – Initial orbit determination configuration.
    /// * [`PyGaussResult`] – Result wrapper for the Gauss IOD.
    pub fn estimate_all_orbits(
        &mut self,
        py: Python<'_>,
        env: &PyOutfit,
        params: &IODParams,
        seed: Option<u64>,
    ) -> PyResult<(Py<PyDict>, Py<PyDict>)> {
        // Build RNG (deterministic if a seed is provided).
        let mut rng: StdRng = match seed {
            Some(s) => StdRng::seed_from_u64(s),
            None => StdRng::from_os_rng(),
        };

        // Cancellation callback: returns true when a KeyboardInterrupt occurred.
        // We briefly acquire the GIL to check Python's signal state.
        let mut should_cancel = || Python::attach(|py| py.check_signals().is_err());

        // Run the heavy computation without the GIL.
        let results: FullOrbitResult = py.detach(|| {
            if params.do_parallel() {
                self.inner.estimate_all_orbits_in_batches_parallel(
                    &env.inner,
                    &mut rng,
                    &params.inner,
                )
            } else {
                self.inner.estimate_all_orbits_with_cancel(
                    &env.inner,
                    &mut rng,
                    &params.inner,
                    &mut should_cancel,
                )
            }
        });

        // Python dicts (bound to current GIL).
        let ok: Bound<'_, PyDict> = PyDict::new(py);
        let err: Bound<'_, PyDict> = PyDict::new(py);

        for (obj, res) in results {
            let py_key = object_number_to_py(py, &obj)?; // Bound<'py, PyAny>

            match res {
                Ok((g, rms)) => {
                    let py_g: GaussResult = g.into();
                    let py_rms = rms.into_pyobject(py)?;

                    let tuple = (py_g, py_rms).into_pyobject(py)?;

                    ok.set_item(py_key, tuple)?;
                }
                Err(e) => {
                    err.set_item(py_key, e.to_string())?;
                }
            }
        }

        Ok((ok.unbind(), err.unbind()))
    }
}

fn object_number_to_py<'py>(py: Python<'py>, key: &ObjectNumber) -> PyResult<Bound<'py, PyAny>> {
    match key {
        ObjectNumber::Int(n) => {
            let b: Bound<'py, PyInt> = (*n as u64).into_pyobject(py)?;
            Ok(b.into_any()) // upcast PyInt -> PyAny
        }
        ObjectNumber::String(s) => {
            let b: Bound<'py, PyString> = s.as_str().into_pyobject(py)?;
            Ok(b.into_any())
        }
    }
}
