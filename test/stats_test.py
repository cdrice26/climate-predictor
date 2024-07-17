from stats import regression_stats
import pytest


def test_regression_stats():
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    result = regression_stats(x, y)
    assert result["slope"] == pytest.approx(2.0)
    assert result["intercept"] == pytest.approx(0.0)
    assert result["r_squared"] == pytest.approx(1.0)
    assert result["f_statistic"] >= 1e15
    assert result["p_value"] == pytest.approx(0.0)
