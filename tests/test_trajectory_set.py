# tests/test_trajectory_set_from_numpy.py
import numpy as np
import pytest
import py_outfit
from astropy.time import Time


def _build_arrays_degrees():
    """
    Build small, deterministic arrays in degrees and MJD(TT).

    Two trajectories: IDs [0,0,0,1,1].
    """
    trajectory_id = np.array([0, 0, 0, 1, 1], dtype=np.uint32)

    # Simple, slightly varying values (degrees)
    ra_deg = np.array([10.0, 10.01, 10.02, 185.0, 185.02], dtype=np.float64)
    dec_deg = np.array([+5.0, +5.01, +5.02, -2.0, -2.02], dtype=np.float64)

    # Uniform 1-sigma uncertainties in arcseconds
    err_ra_arcsec = 0.5
    err_dec_arcsec = 0.5

    # MJD(TT) in days (monotonic)
    mjd_tt = np.array(
        [60000.0, 60000.01, 60000.02, 60000.03, 60000.04], dtype=np.float64
    )

    return trajectory_id, ra_deg, dec_deg, err_ra_arcsec, err_dec_arcsec, mjd_tt


def _build_arrays_radians():
    """
    Build arrays already in radians, with same pattern as degrees builder.
    """
    tid, ra_deg, dec_deg, _, _, mjd = _build_arrays_degrees()
    ra_rad = np.deg2rad(ra_deg)
    dec_rad = np.deg2rad(dec_deg)
    # Uniform uncertainties in radians for the radian path.
    err_ra_rad = np.deg2rad(0.5 / 3600.0)  # 0.5"
    err_dec_rad = np.deg2rad(0.5 / 3600.0)
    return tid, ra_rad, dec_rad, err_ra_rad, err_dec_rad, mjd


def test_build_from_numpy_radians(pyoutfit_env, observer):
    """
    Build a TrajectorySet using the zero-copy radians path.

    Validates:
      - No exception thrown
      - Total number of observations equals input length
      - A non-empty stat string is returned (if implemented)
    """
    # Inputs in radians
    tid, ra_rad, dec_rad, err_ra_rad, err_dec_rad, mjd = _build_arrays_radians()

    ts = py_outfit.TrajectorySet.trajectory_set_from_numpy_radians(
        pyoutfit_env,  # &mut PyOutfit
        tid,  # np.uint32[...]
        ra_rad.astype(np.float64),
        dec_rad.astype(np.float64),
        float(err_ra_rad),
        float(err_dec_rad),
        mjd.astype(np.float64),
        observer,
    )

    # Validate the returned object type
    assert ts is not None

    # Basic sanity checks
    assert hasattr(ts, "total_observations")
    assert ts.total_observations() == tid.size

    # Optional stats string if exposed
    if hasattr(ts, "get_traj_stat"):
        s = ts.get_traj_stat()
        assert isinstance(s, str)
        assert len(s) > 0


def test_build_from_numpy_degrees(pyoutfit_env, observer):
    """
    Build a TrajectorySet using the degrees+arcsec conversion path.

    Validates:
      - No exception thrown
      - Total number of observations equals input length
      - A non-empty stat string is returned (if implemented)
    """
    tid, ra_deg, dec_deg, err_ra_arcsec, err_dec_arcsec, mjd = _build_arrays_degrees()

    ts = py_outfit.TrajectorySet.trajectory_set_from_numpy_degrees(
        pyoutfit_env,  # &mut PyOutfit
        tid,  # np.uint32[...]
        ra_deg.astype(np.float64),
        dec_deg.astype(np.float64),
        float(err_ra_arcsec),
        float(err_dec_arcsec),
        mjd.astype(np.float64),
        observer,
    )

    assert ts is not None

    assert hasattr(ts, "total_observations")
    assert ts.total_observations() == tid.size

    if hasattr(ts, "get_traj_stat"):
        s = ts.get_traj_stat()
        assert isinstance(s, str)
        assert len(s) > 0


def test_length_mismatch_raises(pyoutfit_env, observer):
    """
    Provide mismatched array lengths and expect a ValueError.
    """
    tid = np.array([0, 0, 1], dtype=np.uint32)
    ra = np.deg2rad(np.array([10.0, 10.01], dtype=np.float64))  # <- shorter on purpose
    dec = np.deg2rad(np.array([5.0, 5.01, 5.02], dtype=np.float64))
    mjd = np.array([60000.0, 60000.01, 60000.02], dtype=np.float64)

    err_ra_rad = np.deg2rad(0.5 / 3600.0)
    err_dec_rad = np.deg2rad(0.5 / 3600.0)

    with pytest.raises(ValueError):
        _ = py_outfit.TrajectorySet.trajectory_set_from_numpy_degrees(
            pyoutfit_env,
            tid,
            ra,
            dec,
            float(err_ra_rad),
            float(err_dec_rad),
            mjd,
            observer,
        )


def test_iod_from_vec(pyoutfit_env, ZTF_observatory):

    tid = np.array([0, 1, 2, 1, 2, 1, 0, 0, 0, 1, 2, 1, 1, 0, 2, 2, 0, 2, 2], np.uint32)
    ra_deg = np.array(
        [
            20.9191548,
            33.4247141,
            32.1435128,
            33.4159091,
            32.1347282,
            33.3829299,
            20.6388309,
            20.6187259,
            20.6137886,
            32.7525147,
            31.4874917,
            32.4518231,
            32.4495403,
            19.892738,
            30.6416348,
            30.0938936,
            18.2218784,
            28.3859403,
            28.3818327,
        ],
        dtype=np.float64,
    )
    dec_deg = np.array(
        [
            20.0550441,
            23.5516817,
            26.5139615,
            23.5525348,
            26.5160622,
            23.5555991,
            20.1218532,
            20.1264229,
            20.1275173,
            23.6064063,
            26.6622284,
            23.6270392,
            23.6272157,
            20.2977473,
            26.830301,
            26.9256271,
            20.7096409,
            27.1602652,
            27.160642,
        ],
        dtype=np.float64,
    )
    time = np.array(
        [
            2458789.6362963,
            2458789.638125,
            2458789.638125,
            2458789.6663773,
            2458789.6663773,
            2458789.7706481,
            2458790.6995023,
            2458790.7733333,
            2458790.791412,
            2458791.8445602,
            2458791.8445602,
            2458792.8514699,
            2458792.8590741,
            2458793.6896759,
            2458794.7996759,
            2458796.7965162,
            2458801.7863426,
            2458803.7699537,
            2458803.7875231,
        ],
        dtype=np.float64,
    )

    print("-----")
    print(time)
    print()
    t_utc = Time(time, format="jd", scale="utc")
    print(t_utc)
    mjd_tt = t_utc.tt.mjd
    print()

    print(mjd_tt)
    print("-----")

    traj_set = py_outfit.TrajectorySet.trajectory_set_from_numpy_degrees(
        pyoutfit_env,
        tid,
        ra_deg,
        dec_deg,
        float(0.5),
        float(0.5),
        mjd_tt,
        ZTF_observatory,
    )

    params = (
        py_outfit.IODParams.builder()
        .n_noise_realizations(10)
        .noise_scale(1.0)
        .max_obs_for_triplets(12)
        .max_triplets(30)
        .build()
    )

    print("--- start gauss iod ---")
    orb, err = traj_set.estimate_all_orbits(pyoutfit_env, params)
    print("--- done ---")

    print()
    print(orb)
    print("\n\n=======================\n")

    orbit, rms = orb[0]
    print("Orbit:\n", orbit.to_dict())
    print("Keplerian orbit:\n", orbit.keplerian())
    print("Equinoctial orbit:\n", orbit.equinoctial())

    kepler_orb = orbit.keplerian()
    print("Equinoctial orbit:\n", kepler_orb.to_equinoctial())
    print("RMS:", rms)
