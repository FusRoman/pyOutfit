# --8<-- [start: observer_simple_init]
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

# On the first use, you will see only the added custom site from below
print(env.show_observatories())
# --8<-- [end: observer_simple_init]

# --8<-- [start: from_mpc_code]
# Obtain the ZTF (Palomar) observatory by its MPC code
ztf = env.get_observer_from_mpc_code("I41")  # returns an Observer instance
print(ztf)  # human-readable summary (code, name, geodetic position)

# Listing available observatories (optional helper)
# Now that the MPC code lookup has been used, the internal registry
# has been populated with all MPC observatories, so the output is much longer.
print(env.show_observatories())  # table of currently known / registered sites
# --8<-- [end: from_mpc_code]
