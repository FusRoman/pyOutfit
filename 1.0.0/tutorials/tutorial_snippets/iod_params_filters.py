# Tune physical and numerical filters for the Gauss solver
from py_outfit import IODParams

params = (
    IODParams.builder()
    # Physical plausibility
    .max_ecc(3.0)
    .max_perihelion_au(100.0)
    .r2_min_au(0.1)
    .r2_max_au(100.0)
    .min_rho2_au(0.02)
    # Numerical tolerances
    .aberth_max_iter(100)
    .aberth_eps(1e-8)
    .newton_eps(1e-12)
    .newton_max_it(75)
    .kepler_eps(1e-12)
    .root_imag_eps(1e-8)
    .max_tested_solutions(5)
    .build()
)
print(
    params.max_ecc,
    params.aberth_max_iter,
    params.max_tested_solutions,
)
