// imports à compléter en haut de ton fichier trajectories.rs
use numpy::PyArray1;
use pyo3::{
    exceptions::PyIndexError,
    prelude::*,
    types::{PyIterator, PyList},
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
}
