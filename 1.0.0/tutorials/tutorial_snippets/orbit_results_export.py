# Filter, convert, and build a plain export from successful results
from common_tuto import run_iod

ok, _ = run_iod()

export = []
for obj_id, (g_res, rms) in ok.items():
    k = g_res.keplerian()
    if k is None:
        q = g_res.equinoctial()
        if q is not None:
            k = q.to_keplerian()
        else:
            c = g_res.cometary()
            if c is not None and c.eccentricity > 1.0:
                k = c.to_keplerian()

    if k is None:
        d = g_res.to_dict()
        export.append({"id": obj_id, "rms": rms, **d})
    else:
        export.append({
            "id": obj_id,
            "rms": rms,
            "stage": "corrected" if g_res.is_corrected() else "preliminary",
            "type": "keplerian",
            "a_au": k.semi_major_axis,
            "e": k.eccentricity,
            "i_rad": k.inclination,
            "Omega_rad": k.ascending_node_longitude,
            "omega_rad": k.periapsis_argument,
            "M_rad": k.mean_anomaly,
            "epoch_mjd_tdb": k.reference_epoch,
        })

print(len(export))
