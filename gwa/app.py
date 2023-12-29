from flask import Flask
import os
import requests

import gwa.weather


def create_app():
    """
    Create a Flask Good Weather application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__)

    @app.route("/")
    def index():
        """
        :return: Flask response
        """
        weather_api_key = os.environ.get("WEATHER_API_TOKEN")
        html = gwa.weather.get_rendered_site_data(weather_api_key)
        return html

    return app
