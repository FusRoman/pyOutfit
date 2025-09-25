# IODParams defaults: obtain the standard configuration
from py_outfit import IODParams

# All fields are initialized to the documented defaults
params = IODParams()
print(params.max_triplets, params.dtmax, params.n_noise_realizations)
