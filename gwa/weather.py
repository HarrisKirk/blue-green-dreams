import requests
import datetime


def get_rendered_site_data(weather_api_key):
    weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/richmond%2C%20va?unitGroup=metric&include=days&key={weather_api_key}&contentType=json"
    json_string = requests.get(weather_url).text
    return render(weather_api_key, json_string)

def render(weather_api_key, json_string):
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