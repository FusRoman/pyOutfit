"""
Environment and observer setup for the Pandas tutorial.

This snippet creates a computation environment and registers a simple
observing site. Importing `py_outfit.pandas_pyoutfit` registers the
`DataFrame.outfit` accessor.
"""

from py_outfit import PyOutfit, Observer
import numpy as np

# Accessor registration (side‑effect import)
import py_outfit.pandas_pyoutfit  # noqa: F401


env = PyOutfit("horizon:DE440", "FCCT14")

observer = Observer(
    longitude=0.0,  # degrees east
    latitude=0.0,   # degrees
    elevation=1.0,  # kilometers
    name="DemoSite",
    ra_accuracy=np.deg2rad(0.3 / 3600.0),  # radians
    dec_accuracy=np.deg2rad(0.3 / 3600.0),  # radians
)
env.add_observer(observer)

print(env.show_observatories())
