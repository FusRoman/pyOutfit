# Observer registration example for documentation inclusion
from py_outfit import PyOutfit, Observer

env = PyOutfit("horizon:DE440", "FCCT14")

# Define a custom observing site; elevation is expressed in kilometers
obs = Observer(
    longitude=12.345,  # degrees east
    latitude=-5.0,     # degrees
    elevation=1.0,     # kilometers above MSL
    name="DemoSite",
    ra_accuracy=0.0,   # radians (optional, example value)
    dec_accuracy=0.0,  # radians (optional, example value)
)

# Register the observer in the environment
env.add_observer(obs)

# Alternatively, retrieve by MPC code and then register
# mpc_obs = env.get_observer_from_mpc_code("807")
# env.add_observer(mpc_obs)

print(env.show_observatories())
