"""
Radians workflow: supply RA/DEC and uncertainties in radians.
"""

import numpy as np
import pandas as pd
from py_outfit import IODParams

import py_outfit.pandas_pyoutfit  # noqa: F401
from pandas_setup import env, observer  # type: ignore


arcsec = np.deg2rad(1.0 / 3600.0)

df_rad = pd.DataFrame(
    {
        "tid": [
            0,
            0,
            0,
            0,
            0,
            0,
        ],
        "mjd": [
            58789.13709704,
            58790.20030304,
            58790.27413404,
            58790.29221274,
            58793.19047664,
            58801.28714334,
        ],
        "ra": np.deg2rad(
            [
                20.9191548,
                20.6388309,
                20.6187259,
                20.6137886,
                19.8927380,
                18.2218784,
            ]
        ),
        "dec": np.deg2rad(
            [
                20.0550441,
                20.1218532,
                20.1264229,
                20.1275173,
                20.2977473,
                20.7096409,
            ]
        ),
    }
)

params = IODParams()

res = df_rad.outfit.estimate_orbits(
    env,
    params,
    observer,
    ra_error=0.3 * arcsec,  # radians
    dec_error=0.3 * arcsec,  # radians
    units="radians",
    rng_seed=7,
)

print(res[["object_id", "variant", "element_set", "rms"]])
