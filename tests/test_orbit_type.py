# -*- coding: utf-8 -*-
import math
import pytest

from py_outfit import (
    KeplerianElements,
    EquinoctialElements,
    CometaryElements,
    GaussResult,
)


def nearly_equal(a: float, b: float, *, rtol=1e-10, atol=1e-12) -> bool:
    return math.isclose(a, b, rel_tol=rtol, abs_tol=atol)


def assert_float_eq(a, b, *, rtol=1e-10, atol=1e-12, msg=""):
    assert nearly_equal(a, b, rtol=rtol, atol=atol), (
        msg or f"floats not close: {a} vs {b}"
    )


@pytest.fixture
def fake_kepler():
    return dict(
        reference_epoch=60000.0,
        semi_major_axis=1.234,
        eccentricity=0.1,
        inclination=0.3,
        ascending_node_longitude=1.1,
        periapsis_argument=0.7,
        mean_anomaly=2.3,
    )


@pytest.fixture
def fake_equino():
    return dict(
        reference_epoch=60000.0,
        semi_major_axis=2.5,
        eccentricity_sin_lon=0.05,
        eccentricity_cos_lon=-0.02,
        tan_half_incl_sin_node=0.1,
        tan_half_incl_cos_node=-0.03,
        mean_longitude=1.7,
    )


@pytest.fixture
def fake_comet_hyperb():
    return dict(
        reference_epoch=60000.0,
        perihelion_distance=0.9,  # q (AU)
        eccentricity=1.2,  # hyperbolic
        inclination=0.4,  # rad
        ascending_node_longitude=1.8,
        periapsis_argument=0.2,
        true_anomaly=0.1,  # rad
    )


@pytest.fixture
def fake_comet_parab():
    return dict(
        reference_epoch=60000.0,
        perihelion_distance=1.0,
        eccentricity=1.0,  # parabolic
        inclination=0.2,
        ascending_node_longitude=0.5,
        periapsis_argument=0.7,
        true_anomaly=0.0,
    )


# ------------------------- tests: constructors & getters -------------------------


def test_keplerian_ctor_and_getters(fake_kepler):
    k = KeplerianElements(
        reference_epoch=fake_kepler["reference_epoch"],
        semi_major_axis=fake_kepler["semi_major_axis"],
        eccentricity=fake_kepler["eccentricity"],
        inclination=fake_kepler["inclination"],
        ascending_node_longitude=fake_kepler["ascending_node_longitude"],
        periapsis_argument=fake_kepler["periapsis_argument"],
        mean_anomaly=fake_kepler["mean_anomaly"],
    )
    assert_float_eq(k.reference_epoch, fake_kepler["reference_epoch"])
    assert_float_eq(k.semi_major_axis, fake_kepler["semi_major_axis"])
    assert_float_eq(k.eccentricity, fake_kepler["eccentricity"])
    assert_float_eq(k.inclination, fake_kepler["inclination"])
    assert_float_eq(k.ascending_node_longitude, fake_kepler["ascending_node_longitude"])
    assert_float_eq(k.periapsis_argument, fake_kepler["periapsis_argument"])
    assert_float_eq(k.mean_anomaly, fake_kepler["mean_anomaly"])
    s = str(k)
    r = repr(k)
    assert isinstance(s, str) and len(s) > 0
    assert r.startswith("<EquinoctialElements ") or r.startswith("<KeplerianElements ")


def test_equinoctial_ctor_and_getters(fake_equino):
    q = EquinoctialElements(**fake_equino)
    assert_float_eq(q.reference_epoch, fake_equino["reference_epoch"])
    assert_float_eq(q.semi_major_axis, fake_equino["semi_major_axis"])
    assert_float_eq(q.eccentricity_sin_lon, fake_equino["eccentricity_sin_lon"])
    assert_float_eq(q.eccentricity_cos_lon, fake_equino["eccentricity_cos_lon"])
    assert_float_eq(q.tan_half_incl_sin_node, fake_equino["tan_half_incl_sin_node"])
    assert_float_eq(q.tan_half_incl_cos_node, fake_equino["tan_half_incl_cos_node"])
    assert_float_eq(q.mean_longitude, fake_equino["mean_longitude"])
    s = str(q)
    r = repr(q)
    assert isinstance(s, str) and len(s) > 0
    assert r.startswith("<EquinoctialElements ")


def test_cometary_ctor_and_getters(fake_comet_hyperb):
    c = CometaryElements(**fake_comet_hyperb)
    assert_float_eq(c.reference_epoch, fake_comet_hyperb["reference_epoch"])
    assert_float_eq(c.perihelion_distance, fake_comet_hyperb["perihelion_distance"])
    assert_float_eq(c.eccentricity, fake_comet_hyperb["eccentricity"])
    assert_float_eq(c.inclination, fake_comet_hyperb["inclination"])
    assert_float_eq(
        c.ascending_node_longitude, fake_comet_hyperb["ascending_node_longitude"]
    )
    assert_float_eq(c.periapsis_argument, fake_comet_hyperb["periapsis_argument"])
    assert_float_eq(c.true_anomaly, fake_comet_hyperb["true_anomaly"])
    s = str(c)
    r = repr(c)
    assert isinstance(s, str) and len(s) > 0
    assert r.startswith("<CometaryElements ")


# ------------------------- tests: conversions -------------------------


def test_keplerian_to_equinoctial_and_back(fake_kepler):
    k = KeplerianElements(**fake_kepler)
    q = k.to_equinoctial()
    assert isinstance(q, EquinoctialElements)
    # Back to Keplerian
    k2 = q.to_keplerian()
    assert isinstance(k2, KeplerianElements)
    assert_float_eq(k2.semi_major_axis, k.semi_major_axis, rtol=1e-9)
    assert_float_eq(k2.eccentricity, k.eccentricity, rtol=1e-9)
    assert_float_eq(k2.inclination, k.inclination, rtol=1e-9)
    assert_float_eq(
        k2.ascending_node_longitude % (2 * math.pi),
        k.ascending_node_longitude % (2 * math.pi),
        rtol=1e-9,
    )
    assert_float_eq(
        k2.periapsis_argument % (2 * math.pi),
        k.periapsis_argument % (2 * math.pi),
        rtol=1e-8,
    )
    assert math.isfinite(k2.mean_anomaly)


def test_cometary_hyperbolic_conversions_ok(fake_comet_hyperb):
    c = CometaryElements(**fake_comet_hyperb)
    k = c.to_keplerian()
    assert isinstance(k, KeplerianElements)
    assert k.eccentricity > 1.0
    q = c.to_equinoctial()
    assert isinstance(q, EquinoctialElements)


def test_cometary_parabolic_conversions_raise(fake_comet_parab):
    c = CometaryElements(**fake_comet_parab)
    with pytest.raises(Exception):
        _ = c.to_keplerian()
    with pytest.raises(Exception):
        _ = c.to_equinoctial()


# ------------------------- tests: GaussResult constructors & accessors -------------------------


def test_gaussresult_from_keplerian_stages(fake_kepler):
    k = KeplerianElements(**fake_kepler)
    g_pre = GaussResult.from_keplerian(k, False)
    assert g_pre.is_preliminary() is True
    assert g_pre.is_corrected() is False
    assert g_pre.elements_type() == "keplerian"
    # extractors
    ke = g_pre.keplerian()
    eq = g_pre.equinoctial()
    co = g_pre.cometary()
    assert isinstance(ke, KeplerianElements)
    assert eq is None and co is None
    # to_dict
    d = g_pre.to_dict()
    assert d["stage"] == "preliminary"
    assert d["type"] == "keplerian"
    assert "elements" in d and isinstance(d["elements"], dict)
    assert_float_eq(d["elements"]["semi_major_axis"], fake_kepler["semi_major_axis"])

    # corrected
    k2 = KeplerianElements(**fake_kepler)
    g_cor = GaussResult.from_keplerian(k2, True)
    assert g_cor.is_preliminary() is False
    assert g_cor.is_corrected() is True
    assert g_cor.elements_type() == "keplerian"


def test_gaussresult_from_equinoctial_and_extract(fake_equino):
    q = EquinoctialElements(**fake_equino)
    g = GaussResult.from_equinoctial(q, False)
    assert g.is_preliminary() and not g.is_corrected()
    assert g.elements_type() == "equinoctial"
    assert g.keplerian() is None
    got_q = g.equinoctial()
    assert isinstance(got_q, EquinoctialElements)
    d = g.to_dict()
    assert d["type"] == "equinoctial"
    assert_float_eq(d["elements"]["mean_longitude"], fake_equino["mean_longitude"])


def test_gaussresult_from_cometary_and_extract(fake_comet_hyperb):
    c = CometaryElements(**fake_comet_hyperb)
    g = GaussResult.from_cometary(c, True)
    assert g.is_corrected() and not g.is_preliminary()
    assert g.elements_type() == "cometary"
    got_c = g.cometary()
    assert isinstance(got_c, CometaryElements)
    assert g.keplerian() is None and g.equinoctial() is None
    d = g.to_dict()
    assert d["stage"] == "corrected"
    assert d["type"] == "cometary"
    assert_float_eq(d["elements"]["eccentricity"], fake_comet_hyperb["eccentricity"])


# ------------------------- smoke tests: __str__/__repr__ on GaussResult -------------------------


def test_gaussresult_str_repr(fake_kepler):
    k = KeplerianElements(**fake_kepler)
    g = GaussResult.from_keplerian(k, False)
    s = str(g)
    r = repr(g)
    assert isinstance(s, str) and len(s) > 0
    assert r.startswith("<PyGaussResult ")
