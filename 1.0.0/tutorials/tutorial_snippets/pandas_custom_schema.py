"""
Custom Schema: adapt to DataFrames with different column names.
"""

import numpy as np
import pandas as pd
from py_outfit import IODParams
from py_outfit.pandas_pyoutfit import Schema

import py_outfit.pandas_pyoutfit  # noqa: F401
from pandas_setup import env, observer  # type: ignore


df_weird = pd.DataFrame(
    {
        "object": [0, 0, 0, 0, 0, 0],
        "epoch": [
            58789.13709704,
            58790.20030304,
            58790.27413404,
            58790.29221274,
            58793.19047664,
            58801.28714334,
        ],
        "alpha": [
            20.9191548,
            20.6388309,
            20.6187259,
            20.6137886,
            19.8927380,
            18.2218784,
        ],
        "delta": [
            20.0550441,
            20.1218532,
            20.1264229,
            20.1275173,
            20.2977473,
            20.7096409,
        ],
    }
)

schema = Schema(tid="object", mjd="epoch", ra="alpha", dec="delta")
params = IODParams()

res = df_weird.outfit.estimate_orbits(
    env,
    params,
    observer,
    ra_error=0.3,
    dec_error=0.3,
    schema=schema,
    units="degrees",
)

print(res[["object_id", "variant", "element_set", "rms"]])
