# End-to-end usage: build params and run batch IOD
from py_outfit import PyOutfit, IODParams, TrajectorySet, Observer
import numpy as np

env = PyOutfit("horizon:DE440", "FCCT14")
obs = Observer(0.0, 0.0, 1.0, "DemoSite", np.deg2rad(0.3/3600.0), np.deg2rad(0.3/3600.0))
env.add_observer(obs)

# Minimal synthetic dataset
tid = np.array([1,1,1], dtype=np.uint32)
ra  = np.array([1.0,1.01,1.015])
dec = np.array([0.5,0.49,0.48])
t   = np.array([60000.0,60000.02,60000.05])

ts = TrajectorySet.from_numpy_radians(env, tid, ra, dec, 1e-4, 1e-4, t, obs)

params = (
    IODParams.builder()
    .max_triplets(200)
    .do_sequential()
    .build()
)

ok, err = ts.estimate_all_orbits(env, params, seed=123)
print(list(ok.keys()), list(err.keys()))
