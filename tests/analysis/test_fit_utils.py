import numpy as np
import pytest

from src.analysis.fit_utils import prepare_fit_xy


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
