import pytest

from py_outfit import IODParams


def test_builder_chaining_and_build_returns_instance():
    """Builder should allow fluent chaining and produce an IODParams instance."""
    params = (
        IODParams.builder()
        .n_noise_realizations(256)
        .noise_scale(0.05)
        .extf(1.2)
        .dtmax(5.0)
        .dt_min(0.1)
        .dt_max_triplet(2.0)
        .optimal_interval_time(0.5)
        .max_obs_for_triplets(128)
        .max_triplets(10_000)
        .gap_max(0.25)
        .max_ecc(0.95)
        .max_perihelion_au(5.0)
        .min_rho2_au(1e-6)
        .r2_min_au(0.5)
        .r2_max_au(50.0)
        .aberth_max_iter(200)
        .aberth_eps(1e-12)
        .kepler_eps(1e-13)
        .max_tested_solutions(32)
        .newton_eps(1e-10)
        .newton_max_it(64)
        .root_imag_eps(1e-9)
        .build()
    )

    assert isinstance(params, IODParams)

    # Verify a few representative fields
    assert params.n_noise_realizations == 256
    assert params.noise_scale == pytest.approx(0.05)
    assert params.extf == pytest.approx(1.2)
    assert params.dtmax == pytest.approx(5.0)
    assert params.dt_min == pytest.approx(0.1)
    assert params.dt_max_triplet == pytest.approx(2.0)
    assert params.optimal_interval_time == pytest.approx(0.5)
    assert params.max_obs_for_triplets == 128
    assert params.max_triplets == 10_000
    assert params.gap_max == pytest.approx(0.25)

    assert params.max_ecc == pytest.approx(0.95)
    assert params.max_perihelion_au == pytest.approx(5.0)
    assert params.min_rho2_au == pytest.approx(1e-6)
    assert params.r2_min_au == pytest.approx(0.5)
    assert params.r2_max_au == pytest.approx(50.0)

    assert params.aberth_max_iter == 200
    assert params.aberth_eps == pytest.approx(1e-12)
    assert params.kepler_eps == pytest.approx(1e-13)
    assert params.max_tested_solutions == 32

    assert params.newton_eps == pytest.approx(1e-10)
    assert params.newton_max_it == 64
    assert params.root_imag_eps == pytest.approx(1e-9)


def test_default_constructor_has_reasonable_defaults():
    """Plain IODParams() should be default-constructed."""
    p = IODParams()
    assert isinstance(p, IODParams)

    # We don't assert exact default values (they may evolve),
    # but we can check type/positivity/ranges for a few.
    assert p.n_noise_realizations >= 1
    assert p.max_triplets >= 0
    assert p.max_ecc >= 0.0
    assert p.kepler_eps > 0.0
    assert p.newton_max_it >= 1


def test_str_and_repr_exist_and_contain_class_name():
    """__str__ and __repr__ should not crash and should be informative."""
    p = (
        IODParams.builder()
        .n_noise_realizations(3)
        .max_triplets(42)
        .build()
    )
    s = str(p)
    r = repr(p)

    # Basic sanity checks
    assert isinstance(s, str)
    assert isinstance(r, str)
    assert len(s) > 0 and len(r) > 0

    # Heuristic: the repr or str should mention "IODParams"
    blob = s + " " + r
    assert "IODParams" in blob


@pytest.mark.parametrize("n", [0, 1, 10, 10_000])
def test_n_noise_realizations_is_settable(n):
    """n_noise_realizations should be applied as-is (no hidden coercion)."""
    params = IODParams.builder().n_noise_realizations(n).build()
    assert params.n_noise_realizations == n


def test_multiple_partial_chains_are_independent():
    """Independent chains shouldn't leak state into each other."""
    a = IODParams.builder().max_triplets(100).build()
    b = IODParams.builder().max_triplets(200).build()
    assert a.max_triplets == 100
    assert b.max_triplets == 200
