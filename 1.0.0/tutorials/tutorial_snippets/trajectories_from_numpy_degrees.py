# Build a TrajectorySet from degrees/arcseconds and MJD(TT)
import numpy as np
from py_outfit import PyOutfit, TrajectorySet, Observer

env = PyOutfit("horizon:DE440", "FCCT14")
obs = Observer(0.0, 0.0, 1.0, "DemoSite", np.deg2rad(0.3/3600.0), np.deg2rad(0.3/3600.0))
env.add_observer(obs)

trajectory_id = np.array([10, 10, 10, 11, 11, 11], dtype=np.uint32)
ra_deg        = np.array([10.0, 10.01, 10.02, 180.0, 180.02, 180.05])
dec_deg       = np.array([ 5.0,  5.01,  5.015, -10.0, -10.02, -10.03])
mjd_tt        = np.array([60000.0, 60000.01, 60000.03, 60000.0, 60000.02, 60000.05])

# Performs one conversion to radians under the hood
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
