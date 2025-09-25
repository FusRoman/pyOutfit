# Serialize a GaussResult to a structured dict
import os, sys
sys.path.append(os.path.dirname(__file__))
from common_tuto import run_iod

ok, _ = run_iod()

if ok:
    _, (g_res, _) = next(iter(ok.items()))
    d = g_res.to_dict()
    print(d["stage"], d["type"], sorted(d["elements"].keys()))
else:
    print("No successful results; cannot show to_dict().")
