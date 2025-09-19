from typing import Iterable

import numpy as np
import pandas as pd
import pytest

from py_outfit import PyOutfit, IODParams, Observer, RADSEC
import py_outfit.pandas_pyoutfit  # noqa: F401 to register the accessor


# ---------- Helpers ----------


def _make_df_deg(
    tids: Iterable[object],
    ra_deg: Iterable[float],
    dec_deg: Iterable[float],
    mjd: Iterable[float],
) -> pd.DataFrame:
    """Build a minimal degree-based DataFrame with the standard schema."""
    return pd.DataFrame(
        {
            "tid": np.array(list(tids), dtype=np.uint32),
            "mjd": np.array(list(mjd), dtype=float),
            "ra": np.array(list(ra_deg), dtype=float),
            "dec": np.array(list(dec_deg), dtype=float),
        }
    )


def _required_cols_present(df: pd.DataFrame) -> bool:
    """Check the accessor's required columns are present."""
    return {"tid", "mjd", "ra", "dec"}.issubset(df.columns)


def _assert_result_basic_shape(df: pd.DataFrame) -> None:
    """Common minimal shape checks on the result frame."""
    assert isinstance(df, pd.DataFrame)
    # These columns should always exist on success rows.
    expected_subset = {"object_id", "variant", "element_set", "rms"}

    assert expected_subset.issubset(df.columns)


# ---------- Tests ----------


def test_pandas_estimate_orbit_smoke(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
    pandas_traj: pd.DataFrame,
):
    """
    Smoke test: ensure the accessor runs and returns a DataFrame with core columns.

    This uses the user's working fixture `pandas_traj` (degrees + arcsec).
    """
    assert _required_cols_present(pandas_traj)
    params = IODParams()
    orb_pdf = pandas_traj.outfit.estimate_orbits(
        pyoutfit_env, params, ZTF_observatory, ra_error=0.5, dec_error=0.5
    )
    _assert_result_basic_shape(orb_pdf)
    # At least one row should be produced in realistic scenarios.
    assert len(orb_pdf) >= 1


def test_units_radians_path(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
    pandas_traj: pd.DataFrame,
):
    """
    The 'radians' path should accept small radian uncertainties and succeed.
    We only verify that it does not raise and returns the core columns.
    """
    pandas_traj["ra"] = np.deg2rad(pandas_traj["ra"].values)
    pandas_traj["dec"] = np.deg2rad(pandas_traj["dec"].values)

    params = IODParams()
    # Tiny uncertainties in radians
    ra_sig = 1e-6
    dec_sig = 1e-6

    out = pandas_traj.outfit.estimate_orbits(
        pyoutfit_env,
        params,
        ZTF_observatory,
        ra_error=ra_sig,
        dec_error=dec_sig,
        units="radians",
    )
    _assert_result_basic_shape(out)
    assert set(out["element_set"].unique()) <= {"keplerian", "equinoctial", "cometary"}


def test_schema_remapping(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
    pandas_traj: pd.DataFrame,
):
    """
    Remapping columns via Schema should work when input uses non-default names.
    """

    pandas_traj.rename(
        columns={"tid": "object", "mjd": "epoch", "ra": "alpha", "dec": "delta"},
        inplace=True,
    )

    from py_outfit.pandas_pyoutfit import Schema

    schema = Schema(tid="object", mjd="epoch", ra="alpha", dec="delta")

    params = IODParams()
    out = pandas_traj.outfit.estimate_orbits(
        pyoutfit_env,
        params,
        ZTF_observatory,
        ra_error=0.4,
        dec_error=0.4,
        schema=schema,
        units="degrees",
    )
    _assert_result_basic_shape(out)
    assert "object_id" in out.columns
    assert set(out["element_set"].unique()) <= {"keplerian", "equinoctial", "cometary"}


def test_invalid_units_raises_value_error(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
):
    """
    Passing an unsupported units string must raise ValueError.
    """
    df = _make_df_deg(
        tids=[0, 0, 0],
        ra_deg=[10.0, 10.1, 10.2],
        dec_deg=[-5.0, -4.9, -4.8],
        mjd=[60000.0, 60000.01, 60000.02],
    )
    params = IODParams()
    with pytest.raises(ValueError):
        df.outfit.estimate_orbits(
            pyoutfit_env,
            params,
            ZTF_observatory,
            ra_error=0.5,
            dec_error=0.5,
            units="gradians",  # invalid
        )


def test_missing_columns_raises_value_error(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
):
    """
    If required columns are missing, the accessor should raise ValueError.
    """
    df = pd.DataFrame({"tid": [0, 0, 0], "mjd": [60000, 60000.01, 60000.02]})
    params = IODParams()
    with pytest.raises(ValueError):
        df.outfit.estimate_orbits(
            pyoutfit_env, params, ZTF_observatory, ra_error=0.5, dec_error=0.5
        )


@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_mixed_success_and_error_status(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
    pandas_traj: pd.DataFrame,
):
    """
    Build a DataFrame where one object likely has enough observations (>=3)
    and another does not (e.g., 2 points), to exercise status='ok' and 'error'.

    We avoid asserting *which* object fails (engine-dependent), and instead
    verify that both statuses can appear and that columns are coherent.
    """

    # Add a second object with only two observations (should fail IOD)
    extra = pd.DataFrame(
        {
            "tid": np.array([3, 3], dtype=np.uint32),
            "mjd": np.array([60000.0, 60000.01], dtype=float),
            "ra": np.array([20.0, 20.1], dtype=float),
            "dec": np.array([10.0, 10.1], dtype=float),
            "sra": np.array([0.5, 0.5], dtype=float),
            "sdec": np.array([0.5, 0.5], dtype=float),
        }
    )
    pandas_traj = pd.concat([pandas_traj, extra], ignore_index=True)

    params = IODParams()
    out = pandas_traj.outfit.estimate_orbits(
        pyoutfit_env, params, ZTF_observatory, ra_error=0.4, dec_error=0.4
    )

    # Should have at least one status column entry
    assert "status" in out.columns
    assert set(out["status"].unique()).issubset({"ok", "error"})
    # Basic shape checks still hold
    _assert_result_basic_shape(out.loc[out["status"] == "ok"])
    # If there are error rows, they must carry an 'error' message.
    err_rows = out.loc[out["status"] == "error"]
    if len(err_rows):
        assert "error" in err_rows.columns
        assert err_rows["error"].map(lambda x: isinstance(x, str) and len(x) >= 1).all()


def test_reproducibility_with_rng_seed(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
):
    """
    If the algorithm uses randomized internals, a fixed seed should keep results stable.
    We compare two runs with the same seed and expect identical DataFrames (row-wise).
    """
    df = _make_df_deg(
        tids=[0, 0, 0, 1, 1, 1],
        ra_deg=[10.0, 10.1, 10.2, 33.4, 33.5, 33.6],
        dec_deg=[-5.0, -4.9, -4.8, 2.0, 2.1, 2.2],
        mjd=[60000.0, 60000.01, 60000.02, 60000.0, 60000.01, 60000.02],
    )
    params = IODParams()

    out1 = df.outfit.estimate_orbits(
        pyoutfit_env,
        params,
        ZTF_observatory,
        ra_error=0.5,
        dec_error=0.5,
        rng_seed=12345,
    )
    out2 = df.outfit.estimate_orbits(
        pyoutfit_env,
        params,
        ZTF_observatory,
        ra_error=0.5,
        dec_error=0.5,
        rng_seed=12345,
    )

    # Compare sorted by object_id and then by column names to avoid order issues.
    def _sort(df: pd.DataFrame) -> pd.DataFrame:
        cols = sorted(df.columns)
        key_cols = ["object_id"] if "object_id" in df.columns else []
        return df[cols].sort_values(key_cols).reset_index(drop=True)

    pd.testing.assert_frame_equal(_sort(out1), _sort(out2))
