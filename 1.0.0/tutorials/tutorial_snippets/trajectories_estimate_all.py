# Batch orbit estimation across all trajectories
from py_outfit import PyOutfit, TrajectorySet, IODParams, Observer
import numpy as np
from astropy.time import Time

# --8<-- [start:batch_env]
env = PyOutfit("horizon:DE440", "FCCT14")
obs = Observer(
    0.0, 0.0, 1.0, "DemoSite", np.deg2rad(0.3 / 3600.0), np.deg2rad(0.3 / 3600.0)
)
env.add_observer(obs)

# Minimal synthetic data (single trajectory)
trajectory_id = np.array(
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
# Convert times to MJD (TT) using astropy
t_utc = Time(jd_utc, format="jd", scale="utc")
mjd_tt = t_utc.tt.mjd.astype(np.float64)

# --8<-- [end:batch_env]

# --8<-- [start:batch_build_and_estimate]
ts = TrajectorySet.from_numpy_degrees(
    env,
    trajectory_id,
    ra_deg,
    dec_deg,
    error_ra_arcsec=0.3,
    error_dec_arcsec=0.3,
    mjd_tt=mjd_tt,
    observer=obs,
)

params = IODParams.builder().max_triplets(100).do_sequential().build()
ok, errors = ts.estimate_all_orbits(env, params, seed=42)

print("ok keys:", list(ok.keys()))
print("errors:", errors)
# --8<-- [end:batch_build_and_estimate]
