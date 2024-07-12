from datetime import datetime

import numpy as np
import pyodide_http
import requests
import matplotlib.pyplot as plt
from js import document
from pyscript import when, display
from sklearn.linear_model import LinearRegression

# Necessary to fix requests
pyodide_http.patch_all()


# Converts the open-meteo name to a more human-readable format
def get_parameter_name(parameter):
    if parameter == "temperature_2m_max":
        return "High Temperature"
    elif parameter == "temperature_2m_min":
        return "Low Temperature"
    elif parameter == "apparent_temperature_max":
        return "Max Heat Index"
    elif parameter == "apparent_temperature_min":
        return "Min Heat Index"
    elif parameter == "precipitation_sum":
        return "Precipitation"
    elif parameter == "rain_sum":
        return "Rainfall"
    elif parameter == "snowfall_sum":
        return "Snowfall"
    else:
        return "Wind Speed"


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

    print(location)

    # Get the weather data from the api
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={str(location["lat"])}&longitude={str(location["lon"])}&start_date=1940-01-01&end_date={str(int(datetime.now().year) - 1)}-12-31&daily={parameter}&timezone=auto'

    try:
        data = requests.get(url).json()
    except:
        return "Error fetching weather data"

    print(data)

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


# Graph the data and run linear regression
def graph(data, parameter, location, **kwargs):
    start_year = kwargs.get("start_year", data["start_year"])
    if start_year < data["start_year"]:
        start_year = data["start_year"]
    if start_year > data["end_year"]:
        start_year = data["end_year"]
    end_year = kwargs.get("end_year", data["end_year"])
    if end_year < data["start_year"]:
        end_year = data["start_year"]
    if end_year > data["end_year"]:
        end_year = data["end_year"]
    print(start_year, end_year)
    moving_average = kwargs.get("moving_average", 1)
    plt.clf()
    document.getElementById("canvas").innerHTML = ""
    fig, ax = plt.subplots()
    units = data["units"]
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
    reg = lin_reg(xvals, yvals)
    parameter_name = get_parameter_name(parameter)
    plt.title(f"{parameter_name} in {location} ({units})")
    graph_data(xvals, yvals)
    graph_reg(reg["m"], reg["b"], start_year, end_year)
    return fig


# Graph the data
def graph_data(xvals, yvals):
    x = np.array(xvals)
    y = np.array(yvals)
    plt.plot(x, y)


# Run linear regression and return slope and y-intercept
def lin_reg(xvals, yvals):
    x = np.array(xvals).reshape(-1, 1)
    y = np.array(yvals)
    model = LinearRegression().fit(x, y)
    m = model.coef_
    b = model.intercept_
    return {"m": m, "b": b}


# Graph the regression line
def graph_reg(m, b, xmin, xmax):
    fn = lambda x: m * x + b
    f = np.vectorize(fn, excluded=["R", "cc"])
    x = np.arange(xmin - 20, xmax + 50)
    y = f(x)
    plt.plot(x, y)


@when("click", "#go-button")
def run():
    parameter = document.getElementById("parameter-select").value
    location_string = document.getElementById("location-input").value
    location = geocode(location_string)
    start_year = int(document.getElementById("start-year-input").value)
    end_year = int(document.getElementById("end-year-input").value)
    moving_average = int(document.getElementById("moving-average-input").value)
    data = get_weather_data(location, parameter)
    fig = graph(
        data,
        parameter,
        location_string,
        start_year=start_year,
        end_year=end_year,
        moving_average=moving_average,
    )
    display(fig)
