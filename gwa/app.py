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
        return f"""
            <!DOCTYPE html>
            <html>
            <body>

            <h1>It is now {datetime.datetime.now()}</h1>

            <p>And the weather is fine in Richmond</p>

            </body>
            </html>

        """


    return app
