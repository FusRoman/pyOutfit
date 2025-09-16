import pytest


@pytest.fixture
def pyoutfit_env():
    """
    Fixture that provides a fresh PyOutfit environment for each test.
    """
    from py_outfit import PyOutfit

    env = PyOutfit(ephem="horizon:DE440", error_model="FCCT14")
    yield env
    # No explicit teardown needed; env will be garbage-collected.


@pytest.fixture
def observer():
    """
    Fixture that provides a standard observer for tests.
    """
    from py_outfit import Observer

    obs = Observer(
        longitude=0.123456,  # Degree
        latitude=45.0,  # Degree
        elevation=1234.0,  # meter
        name="UnitTest Observatory",
        ra_accuracy=None,
        dec_accuracy=None,
    )
    return obs

@pytest.fixture
def ZTF_observatory():
    """
    Fixture that provides a standard observer for tests.
    """
    from py_outfit import Observer

    obs = Observer(
        longitude=243.140213,  # Degree
        latitude=33.357336,  # Degree
        elevation=1663.96,  # meter
        name="Palomar Mountain--ZTF",
        ra_accuracy=0.5,
        dec_accuracy=0.5,
    )
    return obs

@pytest.fixture
def pyoutfit_env_with_observer(pyoutfit_env, observer):
    """
    Fixture that provides a PyOutfit environment with a standard observer added.
    """
    pyoutfit_env.add_observer(observer)
    return pyoutfit_env
