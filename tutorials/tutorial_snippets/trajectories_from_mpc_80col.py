# Import trajectories from an MPC 80-column file and append another
from pathlib import Path
from py_outfit import PyOutfit, TrajectorySet

# Create environment (ephemerides + error model)
env = PyOutfit("horizon:DE440", "FCCT14")

# Build from a single MPC 80-column file
mpc_path = Path("tests/data/2015AB.obs")
ts = TrajectorySet.new_from_mpc_80col(env, mpc_path)
print("n_traj=", ts.number_of_trajectories(), "total_obs=", ts.total_observations())

# Append from a second file (no de-duplication)
mpc_path2 = Path("tests/data/33803.obs")
ts.add_from_mpc_80col(env, mpc_path2)
