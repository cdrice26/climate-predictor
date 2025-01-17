# Climate Predictor
This is a small webpage that allows the user to input a location and a weather statistic to monitor over a specified range of time and get a graph of the results. Usage is fairly self-explanatory.

# Disclaimer
This app is in development. Bugs and inaccuracies may occur. Please use with caution, and note that the software is provided as-is and without assumption of correctness.

# Installation and Usage
This is a Python Flask app. To use it, install the dependencies from ```requirements.txt``` and run ```python app.py``` (```python3``` on Mac/Linux). You'll also need to create a .env file and add an entry for `API_KEY` with your API key for [geocode.maps.co](https://geocode.maps.co).

# Data Sources
The data is provided by [Open-Meteo](https://open-meteo.com) and the [Copernicus Climate Change Service](https://climate.copernicus.eu/). 

# Licensing
Climate Predictor is licensed under the MIT License. However, it uses libraries that are licensed under the Apache 2.0 and BSD 3-Clause licenses, and so those licenses are included as well. You can also check LIBRARY_LICENSES.md for a list of libraries and links to their respective licenses.
