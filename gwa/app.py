from flask import Flask
import datetime


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
        return f"The Richmond weather is great on {datetime.datetime.now()}!"

    return app
