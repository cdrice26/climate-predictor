from datetime import datetime

import numpy as np
import pyodide_http
import requests
import matplotlib.pyplot as plt
from js import document, alert, get_parameter_name
from pyscript import when, display
from stats import regression_stats

# Necessary to fix requests
pyodide_http.patch_all()


# Gets the latitude and longitude from search query location_string
def geocode(location_string):

    # Get the response from the geocoding api
    resp = requests.get(f"https://geocode.maps.co/search?q={location_string}")
    json = resp.json()

    # Just store the coordinates in a dictionary
    location = {"lat": float(json[0]["lat"]), "lon": float(json[0]["lon"])}
    return location


# Gets the relevant weather data for a specified location
def get_weather_data(location, parameter):

    # Get the weather data from the api
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={str(location["lat"])}&longitude={str(location["lon"])}&start_date=1940-01-01&end_date={str(int(datetime.now().year) - 1)}-12-31&daily={parameter}&timezone=auto'

    try:
        data = requests.get(url).json()
    except:
        alert("Error fetching weather data")
        return "Error fetching weather data"

    if data.get("error") is not None:
        alert("Error fetching weather data")
        return "Error fetching weather data"

    # Get the dates and values
    dates = data["daily"]["time"]
    values = data["daily"][parameter]

    # Replace None with 0
    for i in range(len(values)):
        if values[i] == None:
            values[i] = 0

    # Just keep the year
    for i in range(len(dates)):
        dates[i] = dates[i][0:4]

    # Get the indexes where the year changes
    change_indexes = []
    for i in range(len(dates)):
        if not dates[i] == dates[i - 1]:
            change_indexes.append(i)
    change_indexes.append(len(dates))

    # Calculate the average value for each year
    averages = []
    for i in range(len(change_indexes) - 1):
        values_for_year = values[change_indexes[i] : change_indexes[i + 1]]
        averages.append(sum(values_for_year) / len(values_for_year))

    # Set the units
    units = None
    if "temperature" in parameter:
        units = "°C"
    elif "sum" in parameter:
        units = "mm/day"
    else:
        units = "km/hr"

    return {
        "start_year": int(dates[0]),
        "end_year": int(dates[-1]) + 1,
        "values": averages,
        "units": units,
    }


# Transform the data
def transform_data(data, start_year, end_year, moving_average):
    xvals = []
    yvals = []
    for year in range(start_year - data["start_year"], end_year - data["start_year"]):
        if year - moving_average + 1 < 0 or year - moving_average + 1 >= len(
            data["values"]
        ):
            continue
        xvals.append(year + data["start_year"])
        yvals.append(
            sum(data["values"][year - moving_average + 1 : year + 1]) / moving_average
        )
    return xvals, yvals


# Set up the graph
def set_up_graph(units, parameter, location):
    plt.clf()
    document.getElementById("canvas").innerHTML = ""
    fig, ax = plt.subplots()
    parameter_name = get_parameter_name(parameter)
    plt.title(f"{parameter_name} in {location} ({units})")
    return fig, units


# Graph the data
def graph_data(xvals, yvals):
    x = np.array(xvals)
    y = np.array(yvals)
    plt.plot(x, y)


# Graph the regression line
def graph_reg(m, b, xmin, xmax):
    fn = lambda x: m * x + b
    f = np.vectorize(fn, excluded=["R", "cc"])
    x = np.arange(xmin - 20, xmax + 50)
    y = f(x)
    plt.plot(x, y)


# Update the text on the screen
def update_text_on_screen(reg, slope, units):
    document.getElementById("results").style.display = "block"
    document.getElementById("r-squared").textContent = str(
        round(reg["r_squared"] * 100)
    )
    document.getElementById("change").textContent = str(abs(round(slope, 4)))
    document.getElementById("significance").textContent = (
        "statistically significant"
        if reg["p_value"] < 0.05
        else "not statistically significant"
    ) + f" (P = {round(reg['p_value'], 4)})"
    for el in document.getElementsByClassName("direction"):
        if slope > 0:
            el.textContent = "increasing"
        elif slope < 0:
            el.textContent = "decreasing"
        else:
            el.textContent = "stable"

    for el in document.getElementsByClassName("units"):
        el.textContent = units


@when("click", "#go-button")
def run():
    parameter = document.getElementById("parameter-select").value
    location_string = document.getElementById("location-input").value
    location = geocode(location_string)
    start_year = int(document.getElementById("start-year-input").value)
    end_year = int(document.getElementById("end-year-input").value)
    moving_average = int(document.getElementById("moving-average-input").value)
    data = get_weather_data(location, parameter)
    xvals, yvals = transform_data(data, start_year, end_year, moving_average)
    reg = regression_stats(xvals, yvals)
    slope = reg["slope"]
    intercept = reg["intercept"]
    fig, units = set_up_graph(data["units"], parameter, location_string)
    graph_data(xvals, yvals)
    graph_reg(slope, intercept, start_year, end_year)
    update_text_on_screen(reg, slope, units)
    display(fig)
