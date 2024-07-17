from api import *
import numpy as np
import pyodide_http  # type: ignore
import matplotlib.pyplot as plt
from js import alert, dq  # type: ignore
from pyscript import when, display  # type: ignore
from stats import regression_stats

# Necessary to fix requests
pyodide_http.patch_all()


# Set up the graph
def set_up_graph(
    units: str, parameter: str, location: str, moving_average: int
) -> tuple[plt.Figure, str]:
    plt.clf()
    dq("#canvas").innerHTML = ""
    fig, ax = plt.subplots()
    parameter_name = get_parameter_name(parameter)
    plt.title(
        f"{parameter_name} in {location} ({units}){f' ({moving_average}-year moving average)' if moving_average > 1 else ''}"
    )
    return fig, units


# Graph the data
def graph_data(xvals: list[float], yvals: list[float]) -> None:
    x = np.array(xvals)
    y = np.array(yvals)
    plt.plot(x, y)


# Graph the regression line
def graph_reg(m: float, b: float, xmin: int, xmax: int) -> None:
    fn = lambda x: m * x + b
    f = np.vectorize(fn, excluded=["R", "cc"])
    x = np.arange(xmin - 20, xmax + 50)
    y = f(x)
    plt.plot(x, y)


# Update the text on the screen
def update_text_on_screen(
    reg: dict[str, float],
    slope: float,
    units: str,
    parameter_name: str,
    location: str,
    moving_average: int,
) -> None:
    dq("#results").style.display = "block"
    dq("#r-squared").textContent = str(round(reg["r_squared"] * 100))
    dq("#change").textContent = str(abs(round(slope, 4)))
    dq("#significance").textContent = (
        "statistically significant"
        if reg["p_value"] < 0.05
        else "not statistically significant"
    ) + f" (P = {round(reg['p_value'], 4)})"
    for el in dq(".direction"):
        if slope > 0:
            el.textContent = "increasing"
        elif slope < 0:
            el.textContent = "decreasing"
        else:
            el.textContent = "stable"

    for el in dq(".units"):
        el.textContent = units

    for el in dq(".parameter"):
        el.textContent = get_parameter_name(parameter_name).lower() + (
            f" ({moving_average}-year moving average)" if moving_average > 1 else ""
        )

    for el in dq(".location"):
        el.textContent = location


@when("click", "#go-button")
def run() -> None:
    parameter = dq("#parameter-select").value
    location_string = dq("#location-input").value
    location = geocode(location_string)
    start_year = int(dq("#start-year-input").value)
    end_year = int(dq("#end-year-input").value)
    moving_average = int(dq("#moving-average-input").value)
    data = get_weather_data(location, parameter, start_year, end_year)
    if type(data) == str:
        alert("Error fetching weather data: " + data)
        return
    xvals, yvals = transform_data(data, start_year, end_year, moving_average)
    reg = regression_stats(xvals, yvals)
    slope = reg["slope"]
    intercept = reg["intercept"]
    fig, units = set_up_graph(
        data["units"], parameter, location["name"], moving_average
    )
    graph_data(xvals, yvals)
    graph_reg(slope, intercept, start_year, end_year)
    update_text_on_screen(
        reg, slope, units, parameter, location["name"], moving_average
    )
    display(fig)
