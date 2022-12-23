from flask import Flask


def create_app():
    """
    Create a Flask Good Weather application using the app factory pattern.

    :return: Flask app
    """
    app = Flask(__name__)

    @app.route('/')
    def index():
        """
        Render a Hello World response.

        :return: Flask response
        """
        return 'Hello World!'

    return app
