import math
from typing import Tuple

import numpy as np
import pytest

import py_outfit as pf
from py_outfit import IODParams, PyOutfit, TrajectorySet, Observer
from copy import deepcopy


def _compare_orbit_dicts_approx(d1: dict, d2: dict, *, rtol=1e-12, atol=1e-12):
    # Stage/type must match exactly
    assert d1["stage"] == d2["stage"]
    assert d1["type"] == d2["type"]
    # Numeric fields compared approximately
    e1 = d1["elements"]
    e2 = d2["elements"]
    assert set(e1.keys()) == set(e2.keys())
    for k in e1.keys():
        assert e1[k] == pytest.approx(e2[k], rel=rtol, abs=atol)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_single_observations_estimate_matches_batch_no_noise(
    pyoutfit_env: PyOutfit, small_traj_set: Tuple[TrajectorySet, dict]
):
    """
    With zero noise realizations, the single-trajectory estimator should match the
    batch result for the same trajectory (up to tiny numeric differences).
    """
    traj_set, counts = small_traj_set
    # Pick any trajectory with at least 3 observations
    key = next(k for k, n in counts.items() if n >= 3)
    obs = traj_set[key]

    params = (
        IODParams.builder()
        .n_noise_realizations(0)
        .max_triplets(50)
        .build()
    )

    # Single-trajectory IOD
    g_single, rms_single = obs.estimate_best_orbit(pyoutfit_env, params, seed=123)

    # Batch IOD on the whole set, extract the same key
    ok, err = traj_set.estimate_all_orbits(pyoutfit_env, params, seed=999)
    assert len(err) == 0, f"Unexpected batch errors: {err}"
    assert key in ok, "Expected key missing from batch results"
    g_batch, rms_batch = ok[key]

    # Compare element families and RMS (no randomness ⇒ should match)
    assert g_single.elements_type() == g_batch.elements_type()
    assert rms_single == pytest.approx(rms_batch, rel=1e-12, abs=1e-12)

    # Compare the raw element dictionaries approximately
    _compare_orbit_dicts_approx(g_single.to_dict(), g_batch.to_dict())


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_single_observations_estimate_is_deterministic_with_seed(
    pyoutfit_env: PyOutfit, small_traj_set: Tuple[TrajectorySet, dict]
):
    """
    For a fixed seed and non-zero noise realizations, the result must be stable.
    """
    traj_set, counts = small_traj_set
    key = next(k for k, n in counts.items() if n >= 3)
    obs = traj_set[key]

    params = (
        IODParams.builder()
        .n_noise_realizations(5)
        .max_triplets(50)
        .build()
    )

    s = 42

    g1, r1 = obs.estimate_best_orbit(pyoutfit_env, params, seed=s)
    g2, r2 = obs.estimate_best_orbit(pyoutfit_env, params, seed=s)


    # Same seed ⇒ identical RMS and elements (within tight numeric tolerance)
    # due tu a bug in outfit with the apply_batch_rms_correction function, the rms is not consistent between calls, 
    # should be fixed for outfit 3.0.0 with issue #41
    # assert r1 == pytest.approx(r2, rel=1e-14, abs=1e-14)
    _compare_orbit_dicts_approx(g1.to_dict(), g2.to_dict(), rtol=1e-14, atol=1e-14)
