from flask import Flask, request, render_template

from api import geocode, get_parameter_name, get_weather_data, transform_data
from stats import regression_stats

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/data")
def get_data():
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
    app.run(port=5500)
