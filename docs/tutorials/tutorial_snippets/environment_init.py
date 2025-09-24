# Environment initialization example for documentation inclusion
from py_outfit import PyOutfit

# Create a new environment with ephemerides and an error model
# The error model string controls observational uncertainty handling in the core engine
env = PyOutfit("horizon:DE440", "FCCT14") # (1) ephemerides selector, error model

# Human-readable listing of currently known observatories (initially empty or built-in)
print(env.show_observatories())
