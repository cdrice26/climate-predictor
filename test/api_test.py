import json
from api import *
import pytest
from unittest.mock import Mock


def test_get_parameter_name():
    assert get_parameter_name("temperature_2m_max") == "High Temperature"
    assert get_parameter_name("temperature_2m_min") == "Low Temperature"
    assert get_parameter_name("apparent_temperature_max") == "Max Heat Index"
    assert get_parameter_name("apparent_temperature_min") == "Min Heat Index"
    assert get_parameter_name("precipitation_sum") == "Precipitation"
    assert get_parameter_name("rain_sum") == "Rainfall"
    assert get_parameter_name("snowfall_sum") == "Snowfall"
    assert get_parameter_name("windspeed_10m_max") == "Wind Speed"


def test_geocode(mocker):
    mock_response = Mock()
    with open("test/sample_geocode_response.json") as f:
        mock_response.json.return_value = json.load(f)

    mocker.patch("requests.get", return_value=mock_response)

    result = geocode("18944")

    assert result == {
        "lat": pytest.approx(40.37057965917431),
        "lon": pytest.approx(-75.2811610921101),
        "name": "Perkasie",
    }


def test_get_weather_data(mocker):
    # Create a mock response object
    mock_response = Mock()
    # Set the json method to return the desired data
    with open("test/sample_weather_response.json") as f:
        mock_response.json.return_value = json.load(f)

    # Patch requests.get to return the mock response
    mocker.patch("requests.get", return_value=mock_response)

    result = get_weather_data(
        {"lat": 37.223198, "lon": 127.19205}, "temperature_2m_max", 2020, 2021
    )

    assert result == {
        "start_year": 2020,
        "end_year": 2021,
        "units": "°C",
        "values": [pytest.approx(16.712841530055)],
    }


def test_transform_data():
    # Test Case 1
    result1 = transform_data(
        {
            "start_year": 2015,
            "end_year": 2020,
            "values": [10, 12, 14, 16, 18, 20],
        },
        2017,
        2020,
        3,
    )
    assert result1 == ([2017, 2018, 2019, 2020], [12.0, 14.0, 16.0, 18.0])

    # Test Case 2
    result2 = transform_data(
        {
            "start_year": 2010,
            "end_year": 2016,
            "values": [5, 7, 9, 11, 13, 15, 17],
        },
        2013,
        2016,
        4,
    )
    assert result2 == ([2013, 2014, 2015, 2016], [8.0, 10.0, 12.0, 14.0])

    # Test Case 3
    result3 = transform_data(
        {
            "start_year": 2018,
            "end_year": 2021,
            "values": [20, 25, 30, 35],
        },
        2019,
        2021,
        2,
    )
    assert result3 == ([2019, 2020, 2021], [22.5, 27.5, 32.5])

    # Test Case 4
    result4 = transform_data(
        {
            "start_year": 2012,
            "end_year": 2015,
            "values": [15, 30, 45, 60],
        },
        2012,
        2015,
        5,
    )
    assert result4 == ([], [])  # Not enough data points for moving average
