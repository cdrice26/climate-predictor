import pandas as pd
import statsmodels.api as sm


def regression_stats(x: list[float], y: list[float]) -> dict[str, float]:

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
