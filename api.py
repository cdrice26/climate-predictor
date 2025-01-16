import requests
from datetime import datetime
from os import getenv
import time
import threading
from functools import wraps

try:
    from dotenv import load_dotenv

    load_dotenv()
    api_key = getenv("API_KEY")
except ModuleNotFoundError:
    api_key = "fake_key"


# Gets the human-readable name of the open-meteo parameter
def get_parameter_name(parameter: str) -> str:
    """
    Convert Open-Meteo parameter names to human-readable names.

    This function maps technical parameter names used by the Open-Meteo API
    to more user-friendly, descriptive names.

    :param parameter: A string representing the Open-Meteo parameter name
    :type parameter: str
    :return: A human-readable name for the parameter
    :rtype: str
    :example:
        >>> get_parameter_name('temperature_2m_max')
        'High Temperature'
    """
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


class RateLimiter:
    """
    A decorator class to limit the rate of function calls.

    This class implements a simple rate limiting mechanism that ensures
    a minimum time interval between successive function calls.

    :param min_interval: Minimum time (in seconds) between method calls, defaults to 1.0
    :type min_interval: float, optional
    """

    def __init__(self, min_interval=1.0):
        """
        Initialize the RateLimiter with a specified minimum interval.

        :param min_interval: Minimum time between calls in seconds
        :type min_interval: float, optional
        """
        self._lock = threading.Lock()
        self._last_call_time = 0.0
        self._min_interval = min_interval

    def __call__(self, func):
        """
        Decorator method to rate limit a function.

        :param func: Function to be rate limited
        :type func: callable
        :return: Wrapped function with rate limiting
        :rtype: callable
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                current_time = time.time()
                time_since_last_call = current_time - self._last_call_time

                # Wait if not enough time has passed since the last call
                if time_since_last_call < self._min_interval:
                    time.sleep(self._min_interval - time_since_last_call)

                # Update the last call time and execute the function
                self._last_call_time = time.time()
                return func(*args, **kwargs)

        return wrapper


class GeocodeCache:
    """
    A class to manage geocoding with persistent caching.

    This class provides a geocoding method with built-in caching to reduce
    redundant API calls. It uses a singleton pattern to maintain a single
    cache across multiple uses.
    """

    _instance = None

    def __new__(cls):
        """
        Implement singleton pattern to ensure only one cache instance exists.

        :return: The single instance of the GeocodeCache
        :rtype: GeocodeCache
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    @RateLimiter(min_interval=1.0)
    def geocode(self, location_string: str) -> dict[str, float | str]:
        """
        Geocode a location with caching.

        Converts a location string to geographic coordinates using an external
        geocoding API. Results are cached to minimize repeated API calls.

        :param location_string: The location to geocode
        :type location_string: str
        :return: A dictionary containing latitude, longitude, and location name
        :rtype: dict
        :raises ValueError: If there are issues with the API request or response

        :example:
            >>> geocoder = GeocodeCache()
            >>> geocoder.geocode('New York, NY')
            {'lat': 40.7127281, 'lon': -74.0060152, 'name': 'New York'}
        """
        # Normalize location string to handle case and whitespace variations
        normalized_location = location_string.strip().lower()

        # Check if location is already in cache
        if normalized_location in self._cache:
            return self._cache[normalized_location]

        # Get the response from the geocoding api
        resp = requests.get(
            f"https://geocode.maps.co/search?q={location_string}&api_key={api_key}"
        )
        resp.raise_for_status()

        if not resp.text:
            raise ValueError("Empty response received from the API")

        # Convert the response to JSON
        json = resp.json()

        # Just store the coordinates in a dictionary
        location = {
            "lat": float(json[0]["lat"]),
            "lon": float(json[0]["lon"]),
            "name": json[0]["display_name"].split(",")[0],
        }

        # Cache the result using normalized location string
        self._cache[normalized_location] = location

        return location


geocode = GeocodeCache().geocode


# Create a rate limiter for weather data
weather_data_rate_limiter = RateLimiter(min_interval=0.25)


# Gets the relevant weather data for a specified location
@weather_data_rate_limiter
def get_weather_data(
    location: dict[str, float],
    parameter: str,
    start_year: int = 1940,
    end_year: int = datetime.now().year,
) -> dict[str, str | int | list[float]] | str:
    """
    Retrieve historical weather data for a specific location and parameter.

    Fetches daily weather data from the Open-Meteo Archive API for a given
    location, parameter, and year range.

    :param location: Dictionary containing latitude and longitude
    :type location: dict[str, float]
    :param parameter: Weather parameter to retrieve (e.g., 'temperature_2m_max')
    :type parameter: str
    :param start_year: First year of data to retrieve, defaults to 1940
    :type start_year: int, optional
    :param end_year: Last year of data to retrieve, defaults to current year
    :type end_year: int, optional
    :return: Dictionary containing weather data or error message
    :rtype: dict or str

    :example:
        >>> location = {'lat': 40.7128, 'lon': -74.0060}
        >>> get_weather_data(location, 'temperature_2m_max')
        {'start_year': 1940, 'end_year': 2024, 'values': [...], 'units': '°C'}
    """
    # Get the weather data from the api
    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={str(location["lat"])}&longitude={str(location["lon"])}&start_date={str(start_year - 5) if start_year - 5 >= 1940 else "1940"}-01-01&end_date={str(end_year - 1)}-12-31&daily={parameter}&timezone=auto'

    response = requests.get(url)
    response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx

    # Check if the response body is empty
    if not response.text:
        raise ValueError("Empty response received from the API")

    data = response.json()  # Now it's safe to decode as JSON

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


def transform_data(
    data: dict[str, str | int | list[float]],
    start_year: int,
    end_year: int,
    moving_average: int,
) -> tuple[list[float]]:
    """
    Transform weather data for statistical analysis.

    Prepares weather data for regression analysis by filtering years
    and applying a moving average.

    :param data: Dictionary containing weather data
    :type data: dict[str, str | int | list[float]]
    :param start_year: First year of data to include
    :type start_year: int
    :param end_year: Last year of data to include
    :type end_year: int
    :param moving_average: Number of years to use in moving average calculation
    :type moving_average: int
    :return: Tuple of x and y values for regression analysis
    :rtype: tuple[list[float]]

    :example:
        >>> data = {'start_year': 1950, 'end_year': 2020, 'values': [...]}
        >>> transform_data(data, 1970, 2010, 5)
        ([1970, 1975, 1980, ...], [22.5, 23.1, 23.7, ...])
    """
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
