# Extract concrete orbital elements from a GaussResult
from common_tuto import run_iod

ok, _ = run_iod()

if ok:
    _, (g_res, rms) = next(iter(ok.items()))
    k = g_res.keplerian()
    q = g_res.equinoctial()
    c = g_res.cometary()
    if k is not None:
        print("K a,e:", k.semi_major_axis, k.eccentricity)
    if q is not None:
        print("Q a,h,k:", q.semi_major_axis, q.eccentricity_sin_lon, q.eccentricity_cos_lon)
    if c is not None:
        print("C q,e:", c.perihelion_distance, c.eccentricity)
else:
    print("No successful results; cannot extract element examples.")
