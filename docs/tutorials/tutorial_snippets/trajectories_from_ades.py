# Import trajectories from an ADES file (JSON or XML) and optionally append others
from pathlib import Path
from py_outfit import PyOutfit, TrajectorySet

env = PyOutfit("horizon:DE440", "FCCT14")

ades_path = Path("tests/data/example_ades.xml")
ts = TrajectorySet.new_from_ades(env, ades_path, error_ra_arcsec=0.3, error_dec_arcsec=0.3)

# Append another ADES file into the same set (avoid re-ingesting the same file)
ts.add_from_ades(env, Path("tests/data/flat_ades.xml"), 0.3, 0.3)
