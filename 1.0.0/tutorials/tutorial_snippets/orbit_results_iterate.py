# Iterate over successful Gauss results and print stage + RMS
from common_tuto import run_iod

ok, errors = run_iod()

if not ok:
    print("No successful results; errors:", errors)
else:
    for obj_id, (g_res, rms) in ok.items():
        stage = "corrected" if g_res.is_corrected() else "preliminary"
        print(f"Object {obj_id}: stage={stage}, RMS={rms:.6e} rad")
