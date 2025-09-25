# Determine element family and stage from one successful result
from common_tuto import run_iod

ok, errors = run_iod()

if ok:
    obj_id, (g_res, rms) = next(iter(ok.items()))
    fam = g_res.elements_type()
    stage = "corrected" if g_res.is_corrected() else "preliminary"
    print(obj_id, fam, stage)
else:
    print("No successful results; cannot show family/stage example.")
