import numpy as np
from scipy import stats


def regression_stats(x: list[float], y: list[float]) -> dict[str, float]:
    """
    Perform linear regression analysis on two sets of numerical data.

    This function uses scipy.stats for precise regression calculations.

    :param x: List of independent variable values (typically years)
    :type x: list[float]
    :param y: List of dependent variable values (typically climate parameter values)
    :type y: list[float]
    :return: A dictionary containing regression statistics
    :rtype: dict[str, float]
    """
    # Validate input
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) != len(y):
        raise ValueError("Input lists must have equal length")
    if len(x) == 0:
        raise ValueError("Input lists cannot be empty")

    # Perform linear regression using scipy.stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

    # Calculate F-statistic
    n = len(x)
    f_statistic = (r_value**2 / (1 - r_value**2)) * (n - 2)

    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_value**2,
        "f_statistic": f_statistic,
        "p_value": p_value,
    }
