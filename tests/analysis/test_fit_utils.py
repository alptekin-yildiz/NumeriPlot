import numpy as np
import pytest

from src.analysis.fit_utils import evaluate_fit_model, fit_statistics, prepare_fit_xy


def test_prepare_fit_xy_uses_auto_x_when_x_missing():
    x, y = prepare_fit_xy([], [2.0, np.nan, 6.0])

    assert np.allclose(x, np.array([1.0, 2.0]))
    assert np.allclose(y, np.array([2.0, 6.0]))


def test_prepare_fit_xy_uses_auto_x_when_lengths_mismatch():
    x, y = prepare_fit_xy([10.0], [1.0, 2.0, 3.0])

    assert np.allclose(x, np.array([1.0, 2.0, 3.0]))
    assert np.allclose(y, np.array([1.0, 2.0, 3.0]))


def test_prepare_fit_xy_filters_invalid_numeric_pairs():
    x, y = prepare_fit_xy([1.0, "bad", 3.0, 4.0], [10.0, 20.0, "bad", 40.0])

    assert np.allclose(x, np.array([1.0, 4.0]))
    assert np.allclose(y, np.array([10.0, 40.0]))


def test_prepare_fit_xy_raises_for_insufficient_valid_points():
    with pytest.raises(ValueError, match="en az 2"):
        prepare_fit_xy([1.0, "bad"], [5.0, "bad"])


@pytest.mark.parametrize("x,y", [([1, 2, 3], [2, np.inf, 6]),
                                  ([1, -np.inf, 3], [2, 4, 6]),
                                  ([], [2, np.inf, 6])])
def test_prepare_fit_xy_rejects_infinity_without_changing_row_meaning(x, y):
    with pytest.raises(ValueError):
        prepare_fit_xy(x, y)


def test_statistics_match_independent_arithmetic():
    residuals, r2, stats = fit_statistics([1, 2, 3], [1, 2, 2])
    # residuals=[0,0,1], SSE=1, SST=2; sample variance=1/3.
    np.testing.assert_array_equal(residuals, [0, 0, 1])
    assert r2 == pytest.approx(0.5, abs=1e-12)
    assert stats["n"] == 3
    assert stats["mean"] == pytest.approx(1/3, abs=1e-12)
    assert stats["std"] == pytest.approx(np.sqrt(1/3), abs=1e-12)
    assert stats["rmse"] == pytest.approx(np.sqrt(1/3), abs=1e-12)


def test_poor_fit_retains_negative_r2():
    _, r2, _ = fit_statistics([1, 2, 3], [0, 0, 0])
    # SSE=14, SST=2, R²=1-14/2=-6 (must not be clipped).
    assert r2 == pytest.approx(-6., abs=1e-12)


@pytest.mark.parametrize("observed,predicted", [
    ([1., 2.], [np.nan, 2.]), ([1., 2.], [1.]),
    ([1e308, -1e308], [-1e308, 1e308]),
])
def test_statistics_reject_invalid_or_overflowing_results(observed, predicted):
    with pytest.raises(ValueError):
        fit_statistics(observed, predicted)


def test_model_domain_failure_is_rejected():
    from models.power_law import model
    with pytest.raises(ValueError):
        evaluate_fit_model(model, np.array([-1., 1.]), [1., 0.5])


def test_gaussian_underflow_is_valid_zero_tail():
    from models.gaussian import model
    result = evaluate_fit_model(model, np.array([0., 1e4]), [2., 0., 1.])
    np.testing.assert_array_equal(result, [2., 0.])
