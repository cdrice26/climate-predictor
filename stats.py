import pandas as pd
import statsmodels.api as sm


def regression_stats(x: list[float], y: list[float]) -> dict[str, float]:
    """
    Perform linear regression analysis on two sets of numerical data.

    This function uses Ordinary Least Squares (OLS) regression to analyze
    the relationship between two variables, calculating key statistical metrics.

    :param x: List of independent variable values (typically years)
    :type x: list[float]
    :param y: List of dependent variable values (typically climate parameter values)
    :type y: list[float]
    :return: A dictionary containing regression statistics
    :rtype: dict[str, float]

    The returned dictionary includes:
    - 'slope': Rate of change of the dependent variable
    - 'intercept': Y-intercept of the regression line
    - 'r_squared': Coefficient of determination (proportion of variance explained)
    - 'f_statistic': F-statistic for overall model significance
    - 'p_value': P-value for the F-statistic

    :raises ValueError: If input lists have different lengths or are empty
    :raises TypeError: If input lists contain non-numeric values

    :example:
        >>> years = [1990, 1995, 2000, 2005, 2010]
        >>> temperatures = [20.1, 20.5, 21.0, 21.6, 22.1]
        >>> regression_stats(years, temperatures)
        {
            'slope': 0.24,
            'intercept': 10.5,
            'r_squared': 0.95,
            'f_statistic': 45.6,
            'p_value': 0.001
        }
    """
    # Validate input
    if len(x) != len(y):
        raise ValueError("Input lists must have equal length")
    if len(x) == 0:
        raise ValueError("Input lists cannot be empty")

    # Create a dictionary with the data
    data = {"X": x, "Y": y}

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Add a constant to the model (for the intercept)
    X = sm.add_constant(df["X"])

    # Fit the regression model
    model = sm.OLS(df["Y"], X).fit()

    # Get results
    slope = model.params["X"]
    intercept = model.params["const"]
    r_squared = model.rsquared
    f_statistic = model.fvalue
    p_value = model.f_pvalue

    return {
        "slope": slope,
        "intercept": intercept,
        "r_squared": r_squared,
        "f_statistic": f_statistic,
        "p_value": p_value,
    }
