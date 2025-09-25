// imports à compléter en haut de ton fichier trajectories.rs
use numpy::PyArray1;
use pyo3::{
    exceptions::PyIndexError,
    prelude::*,
    types::{PyIterator, PyList},
};

use outfit::observations::display::ObservationsDisplayExt;
use outfit::observations::observations_ext::ObservationIOD;
use rand::rngs::StdRng;
use rand::SeedableRng;

use crate::{
    iod_gauss::GaussResult as PyGaussResult, iod_params::IODParams, IntoPyResult, PyOutfit,
};

type ObsArrays<'py> = (
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
    Bound<'py, PyArray1<f64>>,
);

/// Read-only Python view over a single trajectory (owning clone of observations).
#[pyclass]
pub struct Observations {
    pub(crate) inner: outfit::Observations, // alias de Vec<Observation>
}

#[pymethods]
impl Observations {
    /// Human-friendly representation.
    fn __repr__(&self) -> String {
        format!("Trajectory(n_obs={})", self.inner.len())
    }

    /// Render a compact, fixed-width table as a Python string.
    ///
    /// Args:
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for sexagesimal/ISO seconds. Defaults to 3.
    ///
    /// Returns:
    ///     str: formatted table.
    ///
    /// Examples:
    ///     >>> print(obs.show())
    ///     >>> print(obs.show(sorted=True, sec_prec=4))
    #[pyo3(text_signature = "($self, sorted=False, sec_prec=3)")]
    pub fn show(&self, sorted: Option<bool>, sec_prec: Option<usize>) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);
        // ObservationsDisplay (Default mode) + options
        let disp = self.inner.show().with_seconds_precision(sec_prec);
        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Render a wide diagnostic table (uses comfy-table) as a Python string.
    ///
    /// Columns:
    ///   `# | Site | MJD (TT) | JD (TT) | RA±σ[arcsec] | RA [rad] | DEC±σ[arcsec] | DEC [rad] | |r_geo| AU | |r_hel| AU`
    ///
    /// Args:
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for sexagesimal seconds. Defaults to 3.
    ///     dist_prec (int, optional): Fixed-point digits for AU distances. Defaults to 6.
    ///
    /// Returns:
    ///     str: formatted table (Unicode box drawing via comfy-table).
    ///
    /// Examples:
    ///     >>> print(obs.table_wide())
    ///     >>> print(obs.table_wide(sorted=True, sec_prec=4, dist_prec=8))
    #[pyo3(text_signature = "($self, sorted=False, sec_prec=3, dist_prec=6)")]
    pub fn table_wide(
        &self,
        sorted: Option<bool>,
        sec_prec: Option<usize>,
        dist_prec: Option<usize>,
    ) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);
        let dist_prec = dist_prec.unwrap_or(6);

        let disp = self
            .inner
            .table_wide()
            .with_seconds_precision(sec_prec)
            .with_distance_precision(dist_prec);
        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Render an ISO-centric table (uses comfy-table) as a Python string.
    ///
    /// Columns:
    ///   `# | Site | ISO (TT) | ISO (UTC) | RA±σ[arcsec] | DEC±σ[arcsec]`
    ///
    /// Args:
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for seconds (applied to ISO and sexagesimal). Defaults to 3.
    ///
    /// Returns:
    ///     str: formatted table (Unicode box drawing via comfy-table).
    ///
    /// Examples:
    ///     >>> print(obs.table_iso())
    ///     >>> print(obs.table_iso(sorted=True, sec_prec=4))
    #[pyo3(text_signature = "($self, sorted=False, sec_prec=3)")]
    pub fn table_iso(&self, sorted: Option<bool>, sec_prec: Option<usize>) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);

        let disp = self.inner.table_iso().with_seconds_precision(sec_prec);
        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Python-friendly string representation (same as `show()` with defaults).
    fn __str__(&self) -> String {
        // compact, unsorted, 3 fractional digits on seconds
        self.show(None, None)
    }

    /// Render a compact table using the Outfit environment to resolve observer names.
    ///
    /// Columns:
    ///   `# | Site | MJD (TT) | RA[hms] ±σ["] | DEC[dms] ±σ["]`
    ///
    /// Args:
    ///     env (PyOutfit): Global environment (used to resolve site names).
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for sexagesimal seconds. Defaults to 3.
    ///
    /// Returns:
    ///     str: formatted table.
    ///
    /// Examples:
    ///     >>> print(obs.show_with_env(env))
    ///     >>> print(obs.show_with_env(env, sorted=True, sec_prec=4))
    #[pyo3(text_signature = "($self, env, sorted=False, sec_prec=3)")]
    pub fn show_with_env(
        &self,
        env: PyRef<'_, crate::PyOutfit>,
        sorted: Option<bool>,
        sec_prec: Option<usize>,
    ) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);

        let disp = self
            .inner
            .show()
            .with_seconds_precision(sec_prec)
            .with_env(&env.inner);

        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Render a wide diagnostic table (comfy-table) using the Outfit environment.
    ///
    /// Columns:
    ///   `# | Site | MJD (TT) | JD (TT) | RA±σ[arcsec] | RA [rad] | DEC±σ[arcsec] | DEC [rad] | |r_geo| AU | |r_hel| AU`
    ///
    /// Args:
    ///     env (PyOutfit): Global environment (used to resolve site names).
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for sexagesimal seconds. Defaults to 3.
    ///     dist_prec (int, optional): Fixed-point digits for AU distances. Defaults to 6.
    ///
    /// Returns:
    ///     str: Unicode table (comfy-table).
    ///
    /// Examples:
    ///     >>> print(obs.table_wide_with_env(env))
    ///     >>> print(obs.table_wide_with_env(env, sorted=True, sec_prec=4, dist_prec=8))
    #[pyo3(text_signature = "($self, env, sorted=False, sec_prec=3, dist_prec=6)")]
    pub fn table_wide_with_env(
        &self,
        env: PyRef<'_, crate::PyOutfit>,
        sorted: Option<bool>,
        sec_prec: Option<usize>,
        dist_prec: Option<usize>,
    ) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);
        let dist_prec = dist_prec.unwrap_or(6);

        let disp = self
            .inner
            .table_wide()
            .with_seconds_precision(sec_prec)
            .with_distance_precision(dist_prec)
            .with_env(&env.inner);

        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Render an ISO-centric table (comfy-table) using the Outfit environment.
    ///
    /// Columns:
    ///   `# | Site | ISO (TT) | ISO (UTC) | RA±σ[arcsec] | DEC±σ[arcsec]`
    ///
    /// Args:
    ///     env (PyOutfit): Global environment (used to resolve site names).
    ///     sorted (bool, optional): Sort rows by MJD(TT) ascending. Defaults to False.
    ///     sec_prec (int, optional): Fractional digits for seconds (ISO & sexagesimal). Defaults to 3.
    ///
    /// Returns:
    ///     str: Unicode table (comfy-table).
    ///
    /// Examples:
    ///     >>> print(obs.table_iso_with_env(env))
    ///     >>> print(obs.table_iso_with_env(env, sorted=True, sec_prec=4))
    #[pyo3(text_signature = "($self, env, sorted=False, sec_prec=3)")]
    pub fn table_iso_with_env(
        &self,
        env: PyRef<'_, crate::PyOutfit>,
        sorted: Option<bool>,
        sec_prec: Option<usize>,
    ) -> String {
        let sorted = sorted.unwrap_or(false);
        let sec_prec = sec_prec.unwrap_or(3);

        let disp = self
            .inner
            .table_iso()
            .with_seconds_precision(sec_prec)
            .with_env(&env.inner);

        if sorted {
            format!("{}", disp.sorted())
        } else {
            format!("{}", disp)
        }
    }

    /// Number of observations in this trajectory.
    fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// Random access: return `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)` for observation `idx`.
    fn __getitem__(&self, idx: isize) -> PyResult<(f64, f64, f64, f64, f64)> {
        let n = self.inner.len() as isize;
        let i = if idx < 0 { n + idx } else { idx };
        if i < 0 || i >= n {
            return Err(PyIndexError::new_err(format!("index out of range: {idx}")));
        }
        let obs = &self.inner[i as usize];
        Ok((
            obs.time,      // MJD (TT)
            obs.ra,        // rad
            obs.dec,       // rad
            obs.error_ra,  // rad
            obs.error_dec, // rad
        ))
    }

    /// Iterate over observations as `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.
    fn __iter__(slf: PyRef<'_, Self>) -> PyResult<Py<PyIterator>> {
        Python::attach(|py| {
            let out = PyList::empty(py);
            for o in &slf.inner {
                let tup = (o.time, o.ra, o.dec, o.error_ra, o.error_dec).into_pyobject(py)?;
                out.append(tup)?;
            }

            let it_bound = PyIterator::from_object(out.as_any())?;
            Ok(it_bound.unbind())
        })
    }

    /// Export arrays to NumPy (rad / days).
    fn to_numpy<'py>(&self, py: Python<'py>) -> PyResult<ObsArrays<'py>> {
        let n = self.inner.len();
        let mut mjd = Vec::with_capacity(n);
        let mut ra = Vec::with_capacity(n);
        let mut dec = Vec::with_capacity(n);
        let mut sra = Vec::with_capacity(n);
        let mut sdec = Vec::with_capacity(n);

        for o in &self.inner {
            mjd.push(o.time);
            ra.push(o.ra);
            dec.push(o.dec);
            sra.push(o.error_ra);
            sdec.push(o.error_dec);
        }

        let mjd_a = PyArray1::from_vec(py, mjd);
        let ra_a = PyArray1::from_vec(py, ra);
        let dec_a = PyArray1::from_vec(py, dec);
        let sra_a = PyArray1::from_vec(py, sra);
        let sdec_a = PyArray1::from_vec(py, sdec);

        Ok((mjd_a, ra_a, dec_a, sra_a, sdec_a))
    }

    /// Return a Python list of tuples `(mjd_tt, ra_rad, dec_rad, sigma_ra, sigma_dec)`.
    fn to_list<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        // Bound list
        let out = PyList::empty(py);
        for o in &self.inner {
            let tup = (o.time, o.ra, o.dec, o.error_ra, o.error_dec).into_pyobject(py)?;
            out.append(tup)?;
        }
        Ok(out)
    }

    /// Estimate the best orbit for this single set of observations.
    ///
    /// Arguments
    /// -----------------
    /// * `env` : Global environment providing ephemerides, observers, and the error model.
    /// * `params` : Configuration for Gauss IOD, including triplet constraints, noise realizations,
    ///     filters, and numerical tolerances.
    /// * `seed`: Optional RNG seed to make the Monte Carlo path deterministic. When not provided,
    ///     a random seed from the OS is used.
    ///
    /// Returns
    /// ----------
    /// (GaussResult, float)
    ///     The best preliminary or corrected orbit found by the engine and its RMS score
    ///     evaluated over the selected arc. The RMS is expressed in radians.
    ///
    /// Notes
    /// ----------
    /// The method mirrors the batch API used by `TrajectorySet.estimate_all_orbits` but operates
    /// on a single trajectory. Internally it applies batch RMS corrections, generates feasible
    /// triplets, samples noisy realizations, and returns the lowest-RMS candidate.
    #[pyo3(text_signature = "($self, env, params, seed=None)")]
    pub fn estimate_best_orbit(
        &mut self,
        py: Python<'_>,
        env: &PyOutfit,
        params: &IODParams,
        seed: Option<u64>,
    ) -> PyResult<(PyGaussResult, f64)> {
        // RNG setup (deterministic when seed is provided)
        let mut rng: StdRng = match seed {
            Some(s) => StdRng::seed_from_u64(s),
            None => StdRng::from_os_rng(),
        };

        // Heavy computation without the GIL
        let res = py.detach(|| {
            self.inner.estimate_best_orbit(
                &env.inner,
                &env.inner.error_model,
                &mut rng,
                &params.inner,
            )
        });

        // Map OutfitError -> PyErr and convert result to Python wrappers
        let (g, rms) = res.into_py()?;
        Ok((PyGaussResult::from(g), rms))
    }
}
