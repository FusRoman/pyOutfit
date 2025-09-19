import math
from typing import Tuple
import numpy as np
import pytest
import py_outfit

from py_outfit import GaussResult, KeplerianElements, TrajectorySet, PyOutfit, Observer


def _build_arrays_degrees() -> (
    Tuple[np.ndarray, np.ndarray, np.ndarray, float, float, np.ndarray]
):
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


def _build_arrays_radians() -> (
    Tuple[np.ndarray, np.ndarray, np.ndarray, float, float, np.ndarray]
):
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


def test_build_from_numpy_radians(pyoutfit_env: PyOutfit, observer: Observer):
    """
    Build a TrajectorySet using the zero-copy radians path.

    Validates:
      - No exception thrown
      - Total number of observations equals input length
      - A non-empty stat string is returned (if implemented)
    """
    # Inputs in radians
    tid, ra_rad, dec_rad, err_ra_rad, err_dec_rad, mjd = _build_arrays_radians()

    ts = py_outfit.TrajectorySet.from_numpy_radians(
        pyoutfit_env,
        tid,
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


def test_build_from_numpy_degrees(pyoutfit_env: PyOutfit, observer: Observer):
    """
    Build a TrajectorySet using the degrees+arcsec conversion path.

    Validates:
      - No exception thrown
      - Total number of observations equals input length
      - A non-empty stat string is returned (if implemented)
    """
    tid, ra_deg, dec_deg, err_ra_arcsec, err_dec_arcsec, mjd = _build_arrays_degrees()

    ts = py_outfit.TrajectorySet.from_numpy_degrees(
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


def test_length_mismatch_raises(pyoutfit_env: PyOutfit, observer: Observer):
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
        _ = TrajectorySet.from_numpy_degrees(
            pyoutfit_env,
            tid,
            ra,
            dec,
            float(err_ra_rad),
            float(err_dec_rad),
            mjd,
            observer,
        )


def _assert_kepler_reasonable(
    k: KeplerianElements,
    *,
    a_range=(1.0, 5.0),
    e_range=(0.0, 0.9),
    i_max_rad=math.radians(60.0),
):
    """Basic sanity checks for a Keplerian orbit."""
    assert a_range[0] <= k.semi_major_axis <= a_range[1]
    assert e_range[0] <= k.eccentricity <= e_range[1]
    assert 0.0 <= k.inclination <= i_max_rad
    # Angles should be finite real numbers
    for ang in (
        k.inclination,
        k.ascending_node_longitude,
        k.periapsis_argument,
        k.mean_anomaly,
    ):
        assert math.isfinite(ang)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_iod_from_vec(
    pyoutfit_env: PyOutfit, small_traj_set: Tuple[TrajectorySet, dict]
):
    """
    End-to-end Gauss IOD on a small synthetic tracklet set.

    This test avoids ordering assumptions (parallel execution) by:
    - Addressing results by object ID keys (0, 1, 2).
    - Checking numerical ranges and structure rather than exact values.
    """
    # --- Reasonable IOD params for a tiny dataset
    params = (
        py_outfit.IODParams.builder()
        .n_noise_realizations(10)
        .noise_scale(1.0)
        .max_obs_for_triplets(12)
        .max_triplets(30)
        .build()
    )

    traj_set = small_traj_set[0]

    # Note: seed ordering is not stable under multithreading; we do not assert exact values.
    results, errors = traj_set.estimate_all_orbits(pyoutfit_env, params, seed=None)

    # --- No fatal errors expected
    assert isinstance(errors, dict)
    assert len(errors) == 0, f"Unexpected errors: {errors}"

    # --- We expect orbits for objects 0,1,2 (keys are unordered)
    assert isinstance(results, dict)
    assert set(results.keys()) == {0, 1, 2}

    # --- Check each object result
    for obj_id, (g_res, rms) in results.items():
        # Structure & types
        assert isinstance(g_res, py_outfit.GaussResult)
        assert isinstance(rms, float)
        assert math.isfinite(rms)
        # A loose, but meaningful upper bound on RMS (arcsec-like scale propagated)
        assert rms < 1.5

        # Elements family: this pipeline currently returns Keplerian
        elem_type = g_res.elements_type()
        assert elem_type in ("keplerian", "equinoctial", "cometary")

        # to_dict contains the expected shape
        d = g_res.to_dict()
        assert d["stage"] in ("preliminary", "corrected")
        assert d["type"] == elem_type
        assert isinstance(d["elements"], dict) and len(d["elements"]) > 0

        # Extract keplerian when available and sanity-check numbers
        k = g_res.keplerian()
        if k is not None:
            _assert_kepler_reasonable(
                k, a_range=(1.5, 4.5), e_range=(0.0, 0.6), i_max_rad=math.radians(60)
            )
            # Convert to equinoctial and back to ensure conversions are functional
            q = k.to_equinoctial()
            assert isinstance(q, py_outfit.EquinoctialElements)
            k2 = q.to_keplerian()
            assert isinstance(k2, py_outfit.KeplerianElements)
            # Semi-major axis & eccentricity should be close after round-trip
            assert k2.semi_major_axis == pytest.approx(
                k.semi_major_axis, rel=1e-9, abs=1e-12
            )
            assert k2.eccentricity == pytest.approx(k.eccentricity, rel=1e-9, abs=1e-12)
        else:
            # If not keplerian, ensure the corresponding accessor matches the reported type
            if elem_type == "equinoctial":
                assert g_res.equinoctial() is not None
            elif elem_type == "cometary":
                assert g_res.cometary() is not None

    # --- Optional: pick the best (lowest RMS) orbit and perform a few extra checks
    best_obj, (best_res, best_rms) = min(results.items(), key=lambda kv: kv[1][1])
    best_res: GaussResult = best_res
    assert math.isfinite(best_rms)
    assert best_rms <= min(v[1] for v in results.values()) + 1e-12
    # Ensure best one has a keplerian representation (expected in current pipeline)
    bk = best_res.keplerian()
    if bk is not None:
        _assert_kepler_reasonable(
            bk, a_range=(1.5, 4.5), e_range=(0.0, 0.6), i_max_rad=math.radians(60)
        )


# ----------------------------------------------------------------------
# Tests for dict-like behavior
# ----------------------------------------------------------------------


def test_len_and_contains_and_getitem_types(small_traj_set: Tuple[TrajectorySet, dict]):
    """Check __len__, __contains__ and that __getitem__ returns Observations."""
    (traj_set, counts) = small_traj_set
    import py_outfit as py_outfit

    # __len__
    assert len(traj_set) == len(counts)

    # __contains__
    for k in counts.keys():
        assert (k in traj_set) is True
    assert (9999 in traj_set) is False

    # __getitem__ type
    for k in counts.keys():
        obs = traj_set[k]
        # ensure it is the Observations wrapper
        assert isinstance(obs, py_outfit.Observations)


def test_keys_values_items_roundtrip(small_traj_set: Tuple[TrajectorySet, dict]):
    """Check keys/values/items consistency and lengths."""
    traj_set, counts = small_traj_set
    import py_outfit as py_outfit

    keys = traj_set.keys()
    values = traj_set.values()
    items = traj_set.items()

    # Basic types
    assert isinstance(keys, list)
    assert isinstance(values, list)
    assert isinstance(items, list)

    # Lengths are consistent
    assert len(keys) == len(values) == len(items) == len(counts)

    # items() pairs match keys() and values()
    keys_from_items = [k for (k, _) in items]
    assert set(keys_from_items) == set(keys)

    # Each value must be an Observations wrapper
    for v in values:
        assert isinstance(v, py_outfit.Observations)


def test_iter_over_keys_matches_keys_list(small_traj_set: Tuple[TrajectorySet, dict]):
    """__iter__ yields exactly the same set of keys as keys()."""
    traj_set, _ = small_traj_set
    keys_list = set(traj_set.keys())
    keys_iter = set(iter(traj_set))
    assert keys_iter == keys_list


def test_getitem_raises_keyerror_on_missing(small_traj_set: Tuple[TrajectorySet, dict]):
    """Indexing with a missing key must raise KeyError."""
    traj_set, _ = small_traj_set
    with pytest.raises(KeyError):
        _ = traj_set[424242]


# ----------------------------------------------------------------------
# Tests for Observations wrapper behavior
# ----------------------------------------------------------------------


def test_observations_len_and_indexing(small_traj_set: Tuple[TrajectorySet, dict]):
    """Check Observations.__len__ and __getitem__ (including negative index)."""
    traj_set, counts = small_traj_set

    for key, expected_n in counts.items():
        obs = traj_set[key]
        # length
        assert len(obs) == expected_n

        # positive index
        row0 = obs[0]
        assert isinstance(row0, tuple) and len(row0) == 5

        # negative index (last row)
        row_last = obs[-1]
        assert isinstance(row_last, tuple) and len(row_last) == 5

        # index bounds
        with pytest.raises(IndexError):
            _ = obs[expected_n]
        with pytest.raises(IndexError):
            _ = obs[-(expected_n + 1)]


def test_observations_iter_and_to_list(small_traj_set: Tuple[TrajectorySet, dict]):
    """Iterating Observations yields same number of rows as to_list()."""
    traj_set, counts = small_traj_set

    for key, expected_n in counts.items():
        obs = traj_set[key]
        rows = list(iter(obs))
        lst = obs.to_list()

        assert isinstance(lst, list)
        assert len(rows) == expected_n
        assert len(lst) == expected_n

        if expected_n > 0:
            # Each row is a 5-tuple of floats
            r0 = rows[0]
            assert isinstance(r0, tuple) and len(r0) == 5
            assert all(isinstance(x, float) for x in r0)


def test_observations_to_numpy_shapes_and_dtypes(
    small_traj_set: Tuple[TrajectorySet, dict],
):
    """to_numpy returns 5 float64 1D arrays with consistent lengths."""
    traj_set, counts = small_traj_set

    for key, expected_n in counts.items():
        obs = traj_set[key]
        (mjd, ra, dec, sra, sdec) = obs.to_numpy()

        # dtypes
        assert mjd.dtype == np.float64
        assert ra.dtype == np.float64
        assert dec.dtype == np.float64
        assert sra.dtype == np.float64
        assert sdec.dtype == np.float64

        # shapes/lengths
        assert mjd.shape == (expected_n,)
        assert ra.shape == (expected_n,)
        assert dec.shape == (expected_n,)
        assert sra.shape == (expected_n,)
        assert sdec.shape == (expected_n,)


def test_counts_match_grouping_by_tid(small_traj_set):
    """Cross-check: counts from Python match the original grouping by tid."""
    traj_set, counts = small_traj_set

    # Length per key from the mapping interface
    got = {k: len(traj_set[k]) for k in traj_set}
    assert got == dict(counts)
