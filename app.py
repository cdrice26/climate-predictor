from flask import Flask, request, render_template

from api import geocode, get_parameter_name, get_weather_data, transform_data
from stats import regression_stats

app = Flask(__name__)


@app.route("/")
def index():
    """
    Render the main index page of the Climate Predictor application.

    This route serves the main HTML template for the web application,
    which allows users to interact with climate data visualization.

    :return: Rendered HTML template for the index page
    :rtype: flask.Response
    """
    return render_template("index.html")


@app.route("/data")
def get_data():
    """
    Process and retrieve climate data based on user-provided parameters.

    This route handles the data retrieval and processing workflow:
    1. Validates input parameters (location, parameter, years, moving average)
    2. Geocodes the location
    3. Retrieves historical weather data
    4. Transforms data for regression analysis
    5. Calculates regression statistics

    :return: A JSON response containing:
        - Regression statistics (slope, intercept, r-squared)
        - Data values and metadata
        - HTTP status code
    :rtype: tuple[dict, int]
    :raises: Various exceptions for invalid inputs or processing errors

    :example:
        GET /data?parameter=temperature_2m_max&location=New%20York&start_year=1950&end_year=2020&moving_average=5
        Returns: {
            'slope': 0.05,
            'intercept': 10.2,
            'r_squared': 0.75,
            ...
        }
    """
    try:
        parameter = request.args.get("parameter")
    except Exception:
        return {"error": "Missing or invalid parameter"}, 400
    try:
        location_string = request.args.get("location")
    except Exception:
        return {"error": "Missing or invalid location"}, 400
    try:
        location = geocode(location_string)
    except Exception as e:
        return {"error": "Error getting coordinates of the location: " + str(e)}, 400
    try:
        start_year = int(request.args.get("start_year"))
    except Exception:
        return {"error": "Missing or invalid start year"}, 400
    try:
        end_year = int(request.args.get("end_year"))
    except Exception:
        return {"error": "Missing or invalid end year"}, 400
    try:
        moving_average = int(request.args.get("moving_average"))
    except Exception:
        return {"error": "Missing or invalid moving average"}, 400
    data = get_weather_data(location, parameter, start_year, end_year)
    if type(data) == str:
        return {"error": data}, 400
    try:
        xvals, yvals = transform_data(data, start_year, end_year, moving_average)
    except Exception as e:
        return {"error": "Error transforming data: " + str(e)}, 400
    try:
        reg = regression_stats(xvals, yvals)
    except Exception as e:
        return {"error": "Error calculating regression: " + str(e)}, 400
    return {
        "slope": reg["slope"],
        "intercept": reg["intercept"],
        "xvals": xvals,
        "yvals": yvals,
        "r_squared": reg["r_squared"],
        "f_statistic": reg["f_statistic"],
        "p_value": reg["p_value"],
        "location": location["name"],
        "units": data["units"],
        "moving_average": moving_average,
        "parameter_name": get_parameter_name(parameter),
    }, 200


if __name__ == "__main__":
    """
    Entry point for running the Flask application.

    Starts the web server on port 5500 when the script is run directly.
    """
    app.run(port=5500)
