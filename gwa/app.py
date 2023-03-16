from flask import Flask
import datetime
import os
import requests


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
        weather_api_key = os.environ.get('WEATHER_API_TOKEN')
        weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/richmond%2C%20va?unitGroup=metric&include=days&key={weather_api_key}&contentType=json"
        json_string = requests.get(weather_url).text

        return f"""
            <!DOCTYPE html>
            <html>
            <body>

            <h1>It is now {datetime.datetime.now()}</h1>
            <p>And the weather is fine in Richmond</p>
            <p>And the api key is '{weather_api_key[0:5]}'</p>
            <p>The json string is {type(json_string)}</p>
            </body>
            </html>

        """


    return app
