# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import pytest

from py_outfit import TrajectorySet, PyOutfit

# ---------------------------------------------------------------------------
# File discovery helpers
# ---------------------------------------------------------------------------


def _data_dir() -> Path:
    """
    Return tests/data directory, or skip if it does not exist.
    """
    d = Path(__file__).resolve().parent / "data"
    if not d.exists():
        pytest.skip("tests/data/ not found; skipping file-ingestion tests.")
    return d


def _glob_80col(data_dir: Path) -> list[Path]:
    """
    Collect candidate MPC 80-column files.

    Notes
    -----
    We use broad patterns to be resilient to repository naming:
    - *.80col, *80col*.txt, *.mpc, *.mpc80, *.80c, *.txt

    If your repo contains unrelated .txt alongside, you may refine this list
    or filter by small content heuristics.
    """
    patterns = ["*.80col", "*80col*.txt", "*.mpc", "*.mpc80", "*.80c", "*.txt", "*.obs"]
    files: list[Path] = []
    for pat in patterns:
        files.extend(sorted(data_dir.glob(pat)))
    # Stable dedup (dict preserves order since Python 3.7)
    return list(dict.fromkeys(files))


def _glob_ades(data_dir: Path) -> list[Path]:
    """
    Collect candidate ADES files (.json/.xml), including *ades.json / *ades.xml
    and more generic *.json / *.xml.
    """
    files = (
        sorted(data_dir.glob("*.ades.json"))
        + sorted(data_dir.glob("*.ades.xml"))
        + sorted(data_dir.glob("*.json"))
        + sorted(data_dir.glob("*.xml"))
    )
    return list(dict.fromkeys(files))


def _assert_trajset_basic(ts: TrajectorySet):
    """
    Minimal structural assertions shared by all tests.
    """
    # Length ≥ 1
    ntraj = len(ts)
    assert ntraj >= 1, "TrajectorySet should contain at least one trajectory"

    # number_of_trajectories() must agree with __len__()
    assert ts.number_of_trajectories() == ntraj

    # At least one observation
    assert ts.total_observations() > 0, "Total observations should be positive"

    # Keys sanity and subscriptability
    keys = ts.keys()
    assert isinstance(keys, list) and len(keys) == ntraj
    k0 = keys[0]
    assert isinstance(k0, (int, str)), f"Unexpected key type: {type(k0)}"

    # __contains__ and __getitem__
    assert (k0 in ts) is True
    tr0 = ts[k0]
    _ = repr(tr0)  # Ensure it reprs without raising

    # values() and items() shapes
    vals = ts.values()
    items = ts.items()
    assert len(vals) == ntraj and len(items) == ntraj

    k, tr = items[0]
    assert k in keys
    _ = repr(tr)


# ---------------------------------------------------------------------------
# MPC 80-column ingestion
# ---------------------------------------------------------------------------


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_new_from_mpc_80col_smoke(pyoutfit_env: PyOutfit):
    """
    Build a TrajectorySet from each available MPC 80-column file
    and run basic structural checks.

    Exercises: TrajectorySet.new_from_mpc_80col
    """
    import py_outfit as pf

    data_dir = _data_dir()
    files = _glob_80col(data_dir)
    if not files:
        pytest.skip("No MPC 80-column files found in tests/data")

    for f in files:
        ts = pf.TrajectorySet.new_from_mpc_80col(pyoutfit_env, f)
        _assert_trajset_basic(ts)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_add_from_mpc_80col_monotonic(pyoutfit_env: PyOutfit):
    """
    Create from first 80-col file, then append a second file.
    The total observation count must be monotonic (non-decreasing).

    Exercises: TrajectorySet.new_from_mpc_80col + add_from_mpc_80col
    """
    import py_outfit as pf

    data_dir = _data_dir()
    files = _glob_80col(data_dir)
    if len(files) < 2:
        pytest.skip("Need at least two MPC 80-column files to test merging")

    ts = pf.TrajectorySet.new_from_mpc_80col(pyoutfit_env, files[0])
    before_obs = ts.total_observations()

    ts.add_from_mpc_80col(pyoutfit_env, files[1])
    after_obs = ts.total_observations()

    assert (
        after_obs >= before_obs
    ), "Total observations should not decrease after add_from_mpc_80col()"


# ---------------------------------------------------------------------------
# ADES ingestion
# ---------------------------------------------------------------------------


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_new_from_ades_smoke(pyoutfit_env: PyOutfit):
    """
    Build a TrajectorySet from each available ADES file (JSON/XML)
    and run basic structural checks.

    Exercises: TrajectorySet.new_from_ades
    """
    import py_outfit as pf

    data_dir = _data_dir()
    files = _glob_ades(data_dir)
    if not files:
        pytest.skip("No ADES files found in tests/data")

    # Provide small default uncertainties (arcsec) when needed
    for f in files:
        ts = pf.TrajectorySet.new_from_ades(pyoutfit_env, f, 0.5, 0.5)
        _assert_trajset_basic(ts)


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_add_from_ades_monotonic(pyoutfit_env):
    """
    Create from first ADES file, then append a second file.
    The total observation count must be monotonic (non-decreasing).

    Exercises: TrajectorySet.new_from_ades + add_from_ades
    """
    import py_outfit as pf

    data_dir = _data_dir()
    files = _glob_ades(data_dir)
    if len(files) < 2:
        pytest.skip("Need at least two ADES files to test merging")

    ts = pf.TrajectorySet.new_from_ades(pyoutfit_env, files[0], 0.5, 0.5)
    before_obs = ts.total_observations()

    # Passing None, None prefers per-row sigmas if present in the second file
    ts.add_from_ades(pyoutfit_env, files[1], None, None)
    after_obs = ts.total_observations()

    assert (
        after_obs >= before_obs
    ), "Total observations should not decrease after add_from_ades()"


# ---------------------------------------------------------------------------
# Mixed ingestion
# ---------------------------------------------------------------------------


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_mixed_ingestion_monotonic(pyoutfit_env):
    """
    Start from an 80-column file, then add an ADES file (or vice-versa if 80-col missing).
    Only require monotonicity on total observations.

    Exercises interplay of add_from_mpc_80col and add_from_ades.
    """
    import py_outfit as pf

    data_dir = _data_dir()
    f80 = _glob_80col(data_dir)
    fa = _glob_ades(data_dir)

    if f80 and fa:
        ts = pf.TrajectorySet.new_from_mpc_80col(pyoutfit_env, f80[0])
        before = ts.total_observations()
        ts.add_from_ades(pyoutfit_env, fa[0], 0.5, 0.5)
        after = ts.total_observations()
        assert after >= before
    elif f80:
        # Fallback: 80-col then 80-col (already covered above)
        ts = pf.TrajectorySet.new_from_mpc_80col(pyoutfit_env, f80[0])
        before = ts.total_observations()
        if len(f80) >= 2:
            ts.add_from_mpc_80col(pyoutfit_env, f80[1])
            after = ts.total_observations()
            assert after >= before
        else:
            pytest.skip("Only one 80-col file available")
    elif fa:
        # Fallback: ADES then ADES (already covered above)
        ts = pf.TrajectorySet.new_from_ades(pyoutfit_env, fa[0], 0.5, 0.5)
        before = ts.total_observations()
        if len(fa) >= 2:
            ts.add_from_ades(pyoutfit_env, fa[1], None, None)
            after = ts.total_observations()
            assert after >= before
        else:
            pytest.skip("Only one ADES file available")
    else:
        pytest.skip("No files found for mixed ingestion test")
