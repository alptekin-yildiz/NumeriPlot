import numpy as np
import pytest

from models import gaussian, lineer, power_law, ustel, ustel_saturasyon


@pytest.mark.parametrize(
    ("func", "params"),
    [
        (gaussian.model, (2.0, 1.0, 0.5)),
        (lineer.model, (3.0, -1.0)),
        (power_law.model, (1.5, 2.0)),
        (ustel.model, (4.0, 3.0, 0.5)),
        (ustel_saturasyon.model, (10.0, 5.0, 1.2)),
    ],
)
def test_model_output_shape_matches_input(func, params):
    x = np.linspace(0.1, 5.0, 20)
    y = func(x, *params)
    assert y.shape == x.shape


def test_gaussian_center_reaches_amplitude():
    x = np.array([1.0])
    y = gaussian.model(x, A=7.0, mu=1.0, sigma=0.8)
    assert np.isclose(y[0], 7.0)


def test_lineer_computes_expected_values():
    x = np.array([0.0, 1.0, 2.0])
    y = lineer.model(x, a=2.0, b=1.0)
    assert np.allclose(y, np.array([1.0, 3.0, 5.0]))


def test_power_law_zero_input_with_positive_exponent_is_zero():
    x = np.array([0.0, 1.0, 2.0])
    y = power_law.model(x, K=3.0, n=2.0)
    assert np.allclose(y, np.array([0.0, 3.0, 12.0]))


def test_ustel_decays_toward_offset():
    x = np.array([0.0, 10.0, 100.0])
    y = ustel.model(x, A=5.0, tau=2.0, y0=1.0)
    assert y[0] > y[1] > y[2]
    assert y[2] > 0.99
    assert y[2] < 1.01


def test_ustel_saturasyon_increases_and_is_bounded_by_A():
    x = np.array([0.0, 1.0, 10.0, 100.0])
    y = ustel_saturasyon.model(x, A=8.0, B=4.0, k=1.0)
    assert np.all(np.diff(y) > 0)
    assert np.all(y < 8.0)

