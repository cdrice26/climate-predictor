import requests
from datetime import datetime
from env import api_key


# Gets the human-readable name of the open-meteo parameter
def get_parameter_name(parameter):
    parameter_mapping = {
        "temperature_2m_max": "High Temperature",
        "temperature_2m_min": "Low Temperature",
        "apparent_temperature_max": "Max Heat Index",
        "apparent_temperature_min": "Min Heat Index",
        "precipitation_sum": "Precipitation",
        "rain_sum": "Rainfall",
        "snowfall_sum": "Snowfall",
    }
    return parameter_mapping.get(parameter, "Wind Speed")


# Gets the latitude and longitude from search query location_string
def geocode(location_string: str) -> dict[str, float | str]:

    # Get the response from the geocoding api
    try:
        resp = requests.get(
            f"https://geocode.maps.co/search?q={location_string}&api_key={api_key}"
        )
        resp.raise_for_status()

        if not resp.text:
            raise ValueError("Empty response received from the API")

    except requests.exceptions.RequestException as e:
        raise ValueError("Error fetching geocoding data: " + str(e))
    except ValueError as e:
        raise ValueError("Error parsing geocoding data: " + str(e))

    # Convert the response to JSON
    json = resp.json()

    # Just store the coordinates in a dictionary
    location = {
        "lat": float(json[0]["lat"]),
        "lon": float(json[0]["lon"]),
        "name": json[0]["display_name"].split(",")[0],
    }
    return location


# Gets the relevant weather data for a specified location
def get_weather_data(
    location: dict[str, float],
    parameter: str,
    start_year: int = 1940,
    end_year: int = datetime.now().year,
) -> dict[str, str | int | list[float]] | str:

    # Get the weather data from the api
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={str(location["lat"])}&longitude={str(location["lon"])}&start_date={str(start_year - 5) if start_year - 5 >= 1940 else "1940"}-01-01&end_date={str(end_year - 1)}-12-31&daily={parameter}&timezone=auto'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx

        # Check if the response body is empty
        if not response.text:
            raise ValueError("Empty response received from the API")

        data = response.json()  # Now it's safe to decode as JSON

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except ValueError as ve:
        return str(ve)
    except KeyError as ke:
        return f"Key error: {ke} in the response data"
    except Exception as ex:
        return f"An unexpected error occurred: {ex}"

    if data.get("error") is not None:
        return "Error fetching weather data"

    # Get the dates and values
    dates = data["daily"]["time"]
    values = data["daily"][parameter]

    # Replace None with 0
    for i in range(len(values)):
        if values[i] == None:
            values[i] = 0

    # Just keep the year
    years = [date[:4] for date in dates]

    # Get the indexes where the year changes
    change_indexes = []
    for i in range(len(dates)):
        if not dates[i] == dates[i - 1]:
            change_indexes.append(i)
    change_indexes.append(len(dates))

    # Calculate averages based on the available data
    if len(set(years)) == 1:  # Only one year
        average = sum(values) / len(values) if values else 0
        averages = [average]
    else:
        # Get indexes where the year changes
        change_indexes = (
            [0]
            + [i for i in range(1, len(years)) if years[i] != years[i - 1]]
            + [len(values)]
        )

        averages = []
        for i in range(len(change_indexes) - 1):
            yearly_values = values[change_indexes[i] : change_indexes[i + 1]]
            averages.append(sum(yearly_values) / len(yearly_values))

    # Set the units
    if "temperature" in parameter:
        units = "°C"
    elif "sum" in parameter:
        units = "mm/day"
    else:
        units = "km/hr"

    return {
        "start_year": int(years[0]),
        "end_year": int(years[-1]) + 1,
        "values": averages,
        "units": units,
    }


# Transform the data
def transform_data(
    data: dict[str, str | int | list[float]],
    start_year: int,
    end_year: int,
    moving_average: int,
) -> tuple[list[float]]:
    xvals = []
    yvals = []
    # Calculate the number of years we need to iterate over
    for year in range(start_year, end_year + 1):
        # Calculate the index in the data.values list
        index = year - data["start_year"]

        # Ensure we have enough data points for the moving average
        if index >= moving_average - 1 and index < len(data["values"]):
            xvals.append(year)
            # Calculate the moving average
            moving_sum = sum(data["values"][index - moving_average + 1 : index + 1])
            yvals.append(moving_sum / moving_average)

    return xvals, yvals
