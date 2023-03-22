import requests
import datetime
import json
import gwa.sample

USE_LIVE_DATA = False

def get_weather_json(weather_api_key, use_live_data = True):
    if use_live_data:
        weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/richmond%2C%20va?unitGroup=metric&include=days&key={weather_api_key}&contentType=json"
        return requests.get(weather_url).text
    return gwa.sample.sample_json

def get_rendered_site_data(weather_api_key):
    json_string = get_weather_json(weather_api_key, USE_LIVE_DATA)
    parsed = json.loads(json_string)
    pretty_json_string = json.dumps(parsed, indent=4, sort_keys=True)
    return render(weather_api_key, pretty_json_string)

def render(weather_api_key, json_string):
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
        <h1>It is now {datetime.datetime.now()}</h1>
        <p>And the weather is fine in Richmond</p>
        <p>And the api key is '{weather_api_key[0:5]}'</p>
        <p>The json string is {json_string}</p>
        </body>
        </html>
    """    
