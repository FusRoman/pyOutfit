"""
Minimal degrees+arcseconds workflow using the Pandas accessor.
"""

import numpy as np
import pandas as pd
from py_outfit import IODParams

# Ensure the accessor is registered
import py_outfit.pandas_pyoutfit  # noqa: F401

from pandas_setup import env, observer  # type: ignore


# Build a tiny demo dataset: three objects, three observations each
df = pd.DataFrame(
    {
        "tid": [0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2],
        "mjd": [
            58789.13709704,
            58790.20030304,
            58790.27413404,
            58790.29221274,
            58793.19047664,
            58801.28714334,
            60000.0,
            60000.02,
            60000.05,
            60000.0,
            60000.02,
            60000.05,
        ],
        "ra": [
            20.9191548,
            20.6388309,
            20.6187259,
            20.6137886,
            19.8927380,
            18.2218784,
            33.42,
            33.44,
            33.47,
            32.14,
            32.17,
            32.20,
        ],
        "dec": [
            20.0550441,
            20.1218532,
            20.1264229,
            20.1275173,
            20.2977473,
            20.7096409,
            23.55,
            23.56,
            23.57,
            26.51,
            26.52,
            26.53,
        ],
    }
)

params = IODParams.builder().max_triplets(150).do_sequential().build()

res = df.outfit.estimate_orbits(
    env,
    params,
    observer,
    ra_error=0.3,  # arcsec
    dec_error=0.3,  # arcsec
    units="degrees",
    rng_seed=42,
)

# Show a compact preview, resilient to error-only outputs
wanted = ["object_id", "variant", "element_set", "rms", "status", "error"]
cols = [c for c in wanted if c in res.columns]
print(res.head(5)[cols])
