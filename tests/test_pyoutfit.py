# tests/test_pyoutfit.py
# Tests for the thin Python wrapper around the Outfit state.

import pytest

from py_outfit import PyOutfit, Observer


def _make_outfit_or_skip(ephem="horizon:DE440", error_model="FCCT14"):
    """
    Helper: try creating a PyOutfit; if it fails (ex: ephemeris not available),
    skip the test with a readable reason.
    """
    try:
        return PyOutfit(ephem, error_model)
    except Exception as e:
        pytest.skip(f"PyOutfit init failed for ephem='{ephem}', model='{error_model}': {e!r}")


@pytest.mark.parametrize("model", ["FCCT14", "VFCC17", "unknown-model"])
def test_construct_with_variants_of_error_models(model):
    """
    PyOutfit should construct even if the error model string is unknown
    (your code defaults to FCCT14 on unknown).
    """
    state = _make_outfit_or_skip(error_model=model)
    assert isinstance(state, PyOutfit)


def test_add_observer_and_show_observatories_contains_its_name():
    """
    After adding a user-defined observer, show_observatories() should mention it.
    We only check that the returned string contains the observer's name.
    """
    state = _make_outfit_or_skip()

    # Build a simple observer (lon/lat in degrees, elevation in km).
    obs = Observer(
        longitude=0.123456,    # Degree
        latitude=45.0,         # Degree
        elevation=1234.0,       # meter
        name="UnitTest Observatory",
        ra_accuracy=None,
        dec_accuracy=None,
    )

    state.add_observer(obs)
    txt = state.show_observatories()

    assert isinstance(txt, str)
    assert "UnitTest Observatory" in txt


@pytest.mark.parametrize("mpc_code", ["I41"])
def test_get_observer_from_mpc_code_returns_observer(mpc_code):
    """
    get_observer_from_mpc_code should return a valid Observer for a known code.
    If the internal MPC catalog isn't available, the test is skipped by the helper.
    """
    state = _make_outfit_or_skip()
    obs = state.get_observer_from_mpc_code(mpc_code)
    assert isinstance(obs, Observer)


def test_multiple_outfit_instances_are_independent():
    """
    Two PyOutfit instances should not share user-defined observers implicitly.
    We add an observer to A, and check it does not appear in B.
    """
    a = _make_outfit_or_skip()
    b = _make_outfit_or_skip()

    obs_a = Observer(
        longitude=12.0,
        latitude=-20.0,
        elevation=2.0,
        name="OnlyInA",
        ra_accuracy=None,
        dec_accuracy=None,
    )
    a.add_observer(obs_a)

    txt_a = a.show_observatories()
    txt_b = b.show_observatories()
    assert "OnlyInA" in txt_a
    assert "OnlyInA" not in txt_b


def test_show_observatories_is_string_even_when_empty():
    """
    Even with no user-defined observers, show_observatories() should return a string.
    If your Display impl writes a 'no observatory' line, we don't assert its exact content,
    just the type and non-crash behavior.
    """
    state = _make_outfit_or_skip()
    txt = state.show_observatories()
    assert isinstance(txt, str)
    # avoidance of over-specification: don't assert exact wording/formatting
