# --8<-- [start: env_init]
from py_outfit import PyOutfit

env = PyOutfit("horizon:DE440", "FCCT14")  # (ephemerides_id, error_model)
# --8<-- [end: env_init]

# --8<-- [start: observer_init]
from py_outfit import Observer

observer = Observer(
    longitude=12.345,  # degrees East
    latitude=-5.0,  # degrees North
    elevation=1.5,  # kilometers
    name="DemoSite",
    ra_accuracy=None,
    dec_accuracy=None,
)
env.add_observer(observer)

# Alternatively using MPC code:
# observer = env.get_observer_from_mpc_code("I41")
# --8<-- [end: observer_init]

# --8<-- [start: minimal_data]
import numpy as np

trajectory_id = np.array([0, 0, 0], dtype=np.uint32)  # single trajectory with ID 0
ra_deg = np.array(
    [
        20.9191548,
        19.8927380,
        18.2218784,
    ]
)  # Right Ascension in degrees
dec_deg = np.array(
    [
        20.0550441,
        20.2977473,
        20.7096409,
    ]
)  # Declination in degrees
mjd_tt = np.array(
    [
        58789.13709704,
        58793.19047664,
        58801.28714334,
    ]
)  # Observation epochs (TT)

err_ra_arcsec = 0.5  # uniform RA uncertainty
err_dec_arcsec = 0.5  # uniform Dec uncertainty
# --8<-- [end: minimal_data]

# --8<-- [start: build_trajectoryset]
from py_outfit import TrajectorySet

traj_set = TrajectorySet.from_numpy_degrees(
    env,
    trajectory_id,
    ra_deg.astype(float),
    dec_deg.astype(float),
    float(err_ra_arcsec),
    float(err_dec_arcsec),
    mjd_tt.astype(float),
    observer,
)

obs = traj_set[0]  # Observations wrapper for trajectory ID 0
print("Number of observations:", len(obs))
# --8<-- [end: build_trajectoryset]

# --8<-- [start: configure_iodparams]
from py_outfit import IODParams

params = (
    IODParams.builder()
    .n_noise_realizations(0)  # purely geometric Gauss solve
    .max_triplets(50)  # limit combinatorial expansion
    .build()
)
# --8<-- [end: configure_iodparams]

# --8<-- [start: estimate_orbit]
gauss_result, rms = obs.estimate_best_orbit(env, params, seed=42)
print("RMS:", rms)
print("Elements family:", gauss_result.elements_type())
# --8<-- [end: estimate_orbit]

# --8<-- [start: inspect_results]
kep = gauss_result.keplerian()
if kep is not None:
    print("Semi-major axis (AU):", kep.semi_major_axis)
    print("Eccentricity:", kep.eccentricity)
    print("Inclination (rad):", kep.inclination)
else:
    eq = gauss_result.equinoctial()
    if eq is not None:
        print("Equinoctial h,k:", eq.h, eq.k)
    else:
        com = gauss_result.cometary()
        print("Cometary perihelion distance (AU):", com.perihelion_distance)
# --8<-- [end: inspect_results]