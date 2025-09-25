# Convert between orbital element families
from common_tuto import run_iod

ok, _ = run_iod()

if ok:
    _, (g_res, _) = next(iter(ok.items()))
    k = g_res.keplerian()
    q = g_res.equinoctial()
    c = g_res.cometary()

    if k is not None:
        q2 = k.to_equinoctial()
        print("K→Q a,λ:", q2.semi_major_axis, q2.mean_longitude)
    if q is not None:
        k2 = q.to_keplerian()
        print("Q→K a,e:", k2.semi_major_axis, k2.eccentricity)
    if c is not None and c.eccentricity > 1.0:
        k_h = c.to_keplerian()
        print("C(hyperbolic)→K a,e:", k_h.semi_major_axis, k_h.eccentricity)
else:
    print("No successful results; cannot demonstrate conversions.")
