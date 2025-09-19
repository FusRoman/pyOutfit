from collections import Counter
import numpy as np
from astropy.time import Time
import pandas as pd
import pytest
from typing import Iterator, Tuple

from py_outfit import PyOutfit
from py_outfit import Observer
from py_outfit import TrajectorySet


@pytest.fixture
def pyoutfit_env() -> Iterator[PyOutfit]:
    """
    Fixture that provides a fresh PyOutfit environment for each test.
    """
    from py_outfit import PyOutfit

    env = PyOutfit(ephem="horizon:DE440", error_model="FCCT14")
    yield env
    # No explicit teardown needed; env will be garbage-collected.


@pytest.fixture
def observer() -> Observer:
    """
    Fixture that provides a standard observer for tests.
    """
    from py_outfit import Observer

    obs = Observer(
        longitude=0.123456,  # Degree
        latitude=45.0,  # Degree
        elevation=1234.0,  # meter
        name="UnitTest Observatory",
        ra_accuracy=None,
        dec_accuracy=None,
    )
    return obs


@pytest.fixture
def ZTF_observatory() -> Observer:
    """
    Fixture that provides a standard observer for tests.
    """
    from py_outfit import Observer

    obs = Observer(
        longitude=243.140213,  # Degree
        latitude=33.357336,  # Degree
        elevation=1663.96,  # meter
        name="Palomar Mountain--ZTF",
        ra_accuracy=0.5,
        dec_accuracy=0.5,
    )
    return obs


@pytest.fixture
def pyoutfit_env_with_observer(pyoutfit_env: PyOutfit, observer: Observer):
    """
    Fixture that provides a PyOutfit environment with a standard observer added.
    """
    pyoutfit_env.add_observer(observer)
    return pyoutfit_env


# ----------------------------------------------------------------------
# Fixture: build a small TrajectorySet from the synthetic data you posted
# ----------------------------------------------------------------------


@pytest.fixture
def traj_data():
    """
    Provide synthetic trajectory data as numpy arrays.
    Returns:
        tid: np.ndarray of trajectory IDs (uint32)
        ra_deg: np.ndarray of RA in degrees (float64)
        dec_deg: np.ndarray of DEC in degrees (float64)
        mjd_tt: np.ndarray of epochs in MJD TT (float64)
    """

    tid = np.array(
        [0, 1, 2, 1, 2, 1, 0, 0, 0, 1, 2, 1, 1, 0, 2, 2, 0, 2, 2],
        dtype=np.uint32,
    )

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
            19.8927380,
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
            26.8303010,
            26.9256271,
            20.7096409,
            27.1602652,
            27.1606420,
        ],
        dtype=np.float64,
    )

    jd_utc = np.array(
        [
            2458789.6362963,
            2458789.6381250,
            2458789.6381250,
            2458789.6663773,
            2458789.6663773,
            2458789.7706481,
            2458790.6995023,
            2458790.7733333,
            2458790.7914120,
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

    # Convert times to MJD (TT)
    t_utc = Time(jd_utc, format="jd", scale="utc")
    mjd_tt = t_utc.tt.mjd.astype(np.float64)

    return tid, ra_deg, dec_deg, mjd_tt


@pytest.fixture
def small_traj_set(
    pyoutfit_env: PyOutfit,
    ZTF_observatory: Observer,
    traj_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> Tuple[TrajectorySet, Counter]:
    """
    Build a small TrajectorySet from synthetic observations (degrees + arcsec).
    """

    tid, ra_deg, dec_deg, mjd_tt = traj_data

    # Build TrajectorySet from numpy buffers (degrees input)
    import py_outfit as py_outfit

    traj_set = py_outfit.TrajectorySet.from_numpy_degrees(
        pyoutfit_env,
        tid,
        ra_deg,
        dec_deg,
        float(0.5),  # RA sigma [arcsec]
        float(0.5),  # DEC sigma [arcsec]
        mjd_tt,  # epoch TT (MJD)
        ZTF_observatory,
    )

    # Return both the set and the counts per key (for assertions below)
    return traj_set, Counter(tid.tolist())


@pytest.fixture
def pandas_traj(
    traj_data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray],
) -> pd.DataFrame:
    """
    Provide synthetic trajectory data as a pandas DataFrame.
    Returns:
        pd.DataFrame with columns: tid (uint32), ra (float64), dec (float64), mjd (float64)
    """
    import pandas as pd

    tid, ra_deg, dec_deg, mjd_tt = traj_data

    df = pd.DataFrame(
        {
            "tid": tid,
            "ra": ra_deg,
            "dec": dec_deg,
            "mjd": mjd_tt,
            "sra": np.full_like(ra_deg, 0.5),  # arcsec
            "sdec": np.full_like(dec_deg, 0.5),  # arcsec
        }
    )
    return df
