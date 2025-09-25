"""
Handling status: split successes and errors, join back to metadata.
"""

import pandas as pd
from py_outfit import IODParams

import py_outfit.pandas_pyoutfit  # noqa: F401
from pandas_setup import env, observer  # type: ignore


# Small dataset with two objects, one might fail depending on config
data = {
    "tid": [0, 0, 0, 0, 0, 0, 101, 101, 101],
    "mjd": [
        58789.13709704,
        58790.20030304,
        58790.27413404,
        58790.29221274,
        58793.19047664,
        58801.28714334,
        60030.0,
        60030.01,
        60030.02,
    ],
    "ra": [
        20.9191548,
        20.6388309,
        20.6187259,
        20.6137886,
        19.8927380,
        18.2218784,
        220.0,
        220.01,
        219.99,
    ],
    "dec": [
        20.0550441,
        20.1218532,
        20.1264229,
        20.1275173,
        20.2977473,
        20.7096409,
        -2.0,
        -1.99,
        -2.02,
    ],
}
df = pd.DataFrame(data)

meta = pd.DataFrame({"tid": [0, 101], "mag": [20.1, 21.3]})

params = IODParams.builder().max_triplets(200).do_sequential().build()

out = df.outfit.estimate_orbits(
    env, params, observer, ra_error=0.3, dec_error=0.3, units="degrees", rng_seed=1
)

status = out["status"] if "status" in out.columns else pd.Series("ok", index=out.index)
ok = out[status == "ok"].copy()
err = out[status == "error"].copy()

ok_cols = [c for c in ["object_id", "rms", "element_set"] if c in ok.columns]
print("OK rows:\n", ok[ok_cols])
print("Errors:\n", err)

# Join successes to external metadata (left join by identifier)
ok = ok.merge(meta, left_on="object_id", right_on="tid", how="left")
print(ok[["object_id", "mag", "rms"]])
